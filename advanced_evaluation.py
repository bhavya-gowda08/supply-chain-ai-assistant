
import os
import time
import pandas as pd
import chromadb

from sentence_transformers import SentenceTransformer

# --------------------------------------------------
# 1. Load embedding models
# --------------------------------------------------

models = {
    "all-MiniLM-L6-v2": SentenceTransformer("all-MiniLM-L6-v2"),
    "all-mpnet-base-v2": SentenceTransformer("all-mpnet-base-v2")
}

# --------------------------------------------------
# 2. Evaluation questions
# --------------------------------------------------

evaluation_data = [
    {
        "question": "What should happen when stock reaches the reorder level?",
        "relevant_keywords": ["reorder", "replenishment"]
    },
    {
        "question": "What is the purpose of monitoring warehouse inventory?",
        "relevant_keywords": ["inventory", "warehouse", "stock"]
    },
    {
        "question": "What information is available about inventory products?",
        "relevant_keywords": ["product", "stock", "quantity"]
    },
    {
        "question": "What details are recorded in the inventory spreadsheet?",
        "relevant_keywords": ["inventory", "product", "warehouse"]
    },
    {
        "question": "What information is available in the sales data?",
        "relevant_keywords": ["sales", "quantity", "amount"]
    }
]

# --------------------------------------------------
# 3. Read actual documents
# --------------------------------------------------

documents = []
document_ids = []

document_folder = "documents"

for root, dirs, files in os.walk(document_folder):

    # Avoid processing ChromaDB or other generated folders
    dirs[:] = [d for d in dirs if d not in ["uploaded_docs"]]

    for filename in files:

        file_path = os.path.join(root, filename)

        try:
            if filename.endswith(".txt"):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

            elif filename.endswith(".csv"):
                content = pd.read_csv(file_path).to_string(index=False)

            elif filename.endswith(".xlsx"):
                sheets = pd.read_excel(file_path, sheet_name=None)
                content = "\n".join(
                    f"Sheet: {name}\n{df.to_string(index=False)}"
                    for name, df in sheets.items()
                )

            elif filename.endswith(".pdf"):
                from vector_store import extract_pdf_pages
                pages = extract_pdf_pages(file_path)
                content = "\n".join(str(page) for page in pages)

            else:
                continue

            if content.strip():
                documents.append(content)
                document_ids.append(filename)

                print("Loaded:", filename)

        except Exception as e:
            print("Could not load", filename, ":", e)

print("\nTotal documents loaded:", len(documents))

if not documents:
    raise ValueError("No documents were loaded. Check the documents folder.")

# --------------------------------------------------
# 4. Create separate ChromaDB collections
# --------------------------------------------------

client = chromadb.PersistentClient(
    path="data/advanced_evaluation"
)

results = []

for model_name, model in models.items():

    collection_name = (
        "evaluation_minilm"
        if model_name == "all-MiniLM-L6-v2"
        else "evaluation_mpnet"
    )

    # Create a fresh collection for this evaluation run
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    collection = client.create_collection(
        name=collection_name
    )

    embeddings = model.encode(documents).tolist()

    collection.add(
        ids=[f"doc_{i}" for i in range(len(documents))],
        documents=documents,
        embeddings=embeddings,
        metadatas=[
            {"filename": name}
            for name in document_ids
        ]
    )

    print("\nEvaluating:", model_name)

    precision_scores = []
    retrieval_times = []

    for item in evaluation_data:

        query = item["question"]

        query_embedding = model.encode(query).tolist()

        start_time = time.time()

        search_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(3, len(documents))
        )

        elapsed = time.time() - start_time
        retrieval_times.append(elapsed)

        retrieved_docs = search_results["documents"][0]

        relevant_count = 0

        for doc in retrieved_docs:
            if any(
                keyword.lower() in doc.lower()
                for keyword in item["relevant_keywords"]
            ):
                relevant_count += 1

        precision = relevant_count / len(retrieved_docs)
        precision_scores.append(precision)

        print("\nQuestion:", query)
        print("Retrieved documents:", len(retrieved_docs))
        print("Precision:", round(precision, 3))
        print("Time:", round(elapsed, 4), "seconds")

    results.append({
        "Model": model_name,
        "Average Precision": sum(precision_scores) / len(precision_scores),
        "Average Retrieval Time": sum(retrieval_times) / len(retrieval_times)
    })

# --------------------------------------------------
# 5. Display and save results
# --------------------------------------------------

results_df = pd.DataFrame(results)

print("\n========== MODEL COMPARISON ==========")
print(results_df.to_string(index=False))

results_df.to_csv(
    "advanced_evaluation_results.csv",
    index=False
)

print("\nResults saved to advanced_evaluation_results.csv")
