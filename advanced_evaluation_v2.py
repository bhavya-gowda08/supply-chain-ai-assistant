
import json
import os
import time

import pandas as pd
import chromadb

from sentence_transformers import SentenceTransformer
from vector_store import extract_pdf_pages


# --------------------------------------------------
# 1. Load evaluation questions
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

evaluation_file = os.path.join(
    BASE_DIR,
    "evaluation_dataset.json"
)

with open(evaluation_file, "r", encoding="utf-8") as file:
    evaluation_data = json.load(file)


# --------------------------------------------------
# 2. Load actual documents in fixed order
# --------------------------------------------------

document_paths = [
    "documents/supply_chain_policy.pdf",
    "documents/test_document.txt",
    "documents/test_inventory.csv",
    "documents/test_inventory.xlsx"
]

documents = []
document_ids = []

for index, relative_path in enumerate(document_paths):

    path = os.path.join(BASE_DIR, relative_path)

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing document: {path}"
        )

    extension = os.path.splitext(path)[1].lower()

    # Always initialize content
    content = ""

    if extension == ".pdf":

        pages = extract_pdf_pages(path)

        content = "\n".join(
            page["content"] for page in pages
        )

    elif extension == ".txt":

        with open(path, "r", encoding="utf-8") as file:
            content = file.read()

    elif extension == ".csv":

        content = pd.read_csv(path).to_string(index=False)

    elif extension in [".xlsx", ".xls"]:

        sheets = pd.read_excel(
            path,
            sheet_name=None
        )

        content = "\n".join(
            f"Sheet: {name}\n{df.to_string(index=False)}"
            for name, df in sheets.items()
        )

    if content.strip():

        documents.append(content)
        document_ids.append(f"doc_{index}")

print("Documents loaded:", len(documents))
print("Evaluation questions:", len(evaluation_data))

if not documents:
    raise ValueError("No documents were loaded.")


# --------------------------------------------------
# 3. Load embedding models
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
# 4. Prepare ChromaDB
# --------------------------------------------------

chroma_path = os.path.join(
    BASE_DIR,
    "data",
    "advanced_evaluation_v2"
)

os.makedirs(chroma_path, exist_ok=True)

client = chromadb.PersistentClient(
    path=chroma_path
)

all_results = []


# --------------------------------------------------
# 5. Evaluate each model
# --------------------------------------------------

for model_name, model in models.items():

    print("\nEvaluating:", model_name)

    collection_name = (
        "eval_minilm_v2"
        if model_name == "all-MiniLM-L6-v2"
        else "eval_mpnet_v2"
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
        ids=document_ids,
        documents=documents,
        embeddings=embeddings
    )

    precision_scores = []
    recall_scores = []
    reciprocal_ranks = []
    retrieval_times = []

    # --------------------------------------------------
    # 6. Evaluate all questions
    # --------------------------------------------------

    for item in evaluation_data:

        query = item["question"]
        relevant_docs = set(item["relevant_docs"])

        query_embedding = model.encode(
            query,
            normalize_embeddings=True
        ).tolist()

        start_time = time.perf_counter()

        result = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(3, len(documents))
        )

        elapsed = time.perf_counter() - start_time
        retrieval_times.append(elapsed)

        retrieved_ids = result["ids"][0]

        retrieved_relevant = [
            doc_id
            for doc_id in retrieved_ids
            if doc_id in relevant_docs
        ]

        precision = (
            len(retrieved_relevant) / len(retrieved_ids)
            if retrieved_ids else 0
        )

        recall = (
            len(retrieved_relevant) / len(relevant_docs)
            if relevant_docs else 0
        )

        reciprocal_rank = 0

        for rank, doc_id in enumerate(retrieved_ids, start=1):

            if doc_id in relevant_docs:
                reciprocal_rank = 1 / rank
                break

        precision_scores.append(precision)
        recall_scores.append(recall)
        reciprocal_ranks.append(reciprocal_rank)

    # --------------------------------------------------
    # 7. Calculate average metrics
    # --------------------------------------------------

    average_precision = (
        sum(precision_scores) / len(precision_scores)
        if precision_scores else 0
    )

    average_recall = (
        sum(recall_scores) / len(recall_scores)
        if recall_scores else 0
    )

    mrr = (
        sum(reciprocal_ranks) / len(reciprocal_ranks)
        if reciprocal_ranks else 0
    )

    average_time = (
        sum(retrieval_times) / len(retrieval_times)
        if retrieval_times else 0
    )

    model_result = {
        "Model": model_name,
        "Precision@3": average_precision,
        "Recall@3": average_recall,
        "MRR": mrr,
        "Average Retrieval Time (seconds)": average_time
    }

    all_results.append(model_result)

    print("Precision@3:", round(average_precision, 4))
    print("Recall@3:", round(average_recall, 4))
    print("MRR:", round(mrr, 4))
    print("Average Retrieval Time:", round(average_time, 6))


# --------------------------------------------------
# 8. Save final comparison
# --------------------------------------------------

results_df = pd.DataFrame(all_results)

print("\n========== FINAL MODEL COMPARISON ==========")
print(results_df.to_string(index=False))

output_file = os.path.join(
    BASE_DIR,
    "advanced_evaluation_v2_results.csv"
)

results_df.to_csv(
    output_file,
    index=False
)

print("\nResults saved successfully!")
print(output_file)
