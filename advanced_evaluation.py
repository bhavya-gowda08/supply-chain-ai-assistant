
import os
import time

import pandas as pd
import chromadb

from sentence_transformers import SentenceTransformer
from vector_store import extract_pdf_pages


# --------------------------------------------------
# 1. Project directory
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOCUMENT_FOLDER = os.path.join(BASE_DIR, "documents")


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
# 3. Load documents
# --------------------------------------------------

documents = []
document_names = []

if not os.path.exists(DOCUMENT_FOLDER):
    raise FileNotFoundError(
        f"Documents folder not found: {DOCUMENT_FOLDER}"
    )

for root, dirs, files in os.walk(DOCUMENT_FOLDER):

    dirs[:] = [
        directory
        for directory in dirs
        if directory not in ["uploaded_docs"]
    ]

    for filename in files:

        file_path = os.path.join(root, filename)
        extension = os.path.splitext(filename)[1].lower()

        content = ""

        try:

            if extension == ".txt":

                with open(
                    file_path,
                    "r",
                    encoding="utf-8"
                ) as file:
                    content = file.read()

            elif extension == ".csv":

                content = pd.read_csv(
                    file_path
                ).to_string(index=False)

            elif extension in [".xlsx", ".xls"]:

                sheets = pd.read_excel(
                    file_path,
                    sheet_name=None
                )

                content = "\n".join(
                    f"Sheet: {name}\n{df.to_string(index=False)}"
                    for name, df in sheets.items()
                )

            elif extension == ".pdf":

                pages = extract_pdf_pages(file_path)

                content = "\n".join(
                    page["content"] for page in pages
                )

            else:
                continue

            if content.strip():

                documents.append(content)
                document_names.append(filename)

                print("Loaded:", filename)

        except Exception as error:

            print(
                f"Could not load {filename}: {error}"
            )


print("\nTotal documents loaded:", len(documents))

if not documents:
    raise ValueError(
        "No documents were loaded. Check the documents folder."
    )


# --------------------------------------------------
# 4. Load embedding models
# --------------------------------------------------

models = {
    "all-MiniLM-L6-v2": SentenceTransformer(
        "all-MiniLM-L6-v2"
    ),
    "all-mpnet-base-v2": SentenceTransformer(
        "all-mpnet-base-v2"
    )
}


# --------------------------------------------------
# 5. Prepare ChromaDB
# --------------------------------------------------

chroma_path = os.path.join(
    BASE_DIR,
    "data",
    "advanced_evaluation"
)

os.makedirs(chroma_path, exist_ok=True)

client = chromadb.PersistentClient(
    path=chroma_path
)

results = []


# --------------------------------------------------
# 6. Evaluate each embedding model
# --------------------------------------------------

for model_name, model in models.items():

    collection_name = (
        "evaluation_minilm"
        if model_name == "all-MiniLM-L6-v2"
        else "evaluation_mpnet"
    )

    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    embeddings = model.encode(
        documents,
        normalize_embeddings=True
    ).tolist()

    collection.add(
        ids=[
            f"doc_{index}"
            for index in range(len(documents))
        ],
        documents=documents,
        embeddings=embeddings,
        metadatas=[
            {"filename": name}
            for name in document_names
        ]
    )

    print("\nEvaluating:", model_name)

    precision_scores = []
    retrieval_times = []

    # --------------------------------------------------
    # 7. Evaluate each question
    # --------------------------------------------------

    for item in evaluation_data:

        query = item["question"]

        query_embedding = model.encode(
            query,
            normalize_embeddings=True
        ).tolist()

        start_time = time.perf_counter()

        search_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(3, len(documents))
        )

        elapsed = time.perf_counter() - start_time

        retrieval_times.append(elapsed)

        # Safely handle missing or None documents
        retrieved_batches = search_results.get("documents")

        retrieved_docs = (
            retrieved_batches[0]
            if retrieved_batches and retrieved_batches[0]
            else []
        )

        relevant_count = 0

        for doc in retrieved_docs:

            if any(
                keyword.lower() in doc.lower()
                for keyword in item["relevant_keywords"]
            ):
                relevant_count += 1

        precision = (
            relevant_count / len(retrieved_docs)
            if retrieved_docs else 0
        )

        precision_scores.append(precision)

        print("\nQuestion:", query)
        print("Retrieved documents:", len(retrieved_docs))
        print("Precision:", round(precision, 3))
        print("Retrieval time:", round(elapsed, 4), "seconds")

    # --------------------------------------------------
    # 8. Calculate model metrics
    # --------------------------------------------------

    average_precision = (
        sum(precision_scores) / len(precision_scores)
        if precision_scores else 0
    )

    average_time = (
        sum(retrieval_times) / len(retrieval_times)
        if retrieval_times else 0
    )

    results.append({
        "Model": model_name,
        "Average Precision": average_precision,
        "Average Retrieval Time": average_time
    })


# --------------------------------------------------
# 9. Display and save results
# --------------------------------------------------

results_df = pd.DataFrame(results)

print("\n========== MODEL COMPARISON ==========")

print(
    results_df.to_string(index=False)
)

output_file = os.path.join(
    BASE_DIR,
    "advanced_evaluation_results.csv"
)

results_df.to_csv(
    output_file,
    index=False
)

print("\nResults saved successfully!")
print(output_file)
