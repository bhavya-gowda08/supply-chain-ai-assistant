
import chromadb
import time

from sentence_transformers import SentenceTransformer


# ==========================================
# 1. CONNECT TO CHROMADB
# ==========================================

client = chromadb.PersistentClient(
    path="data/embedding_comparison"
)

minilm_collection = client.get_collection(
    name="supply_chain_minilm"
)

mpnet_collection = client.get_collection(
    name="supply_chain_mpnet"
)


# ==========================================
# 2. LOAD EMBEDDING MODELS
# ==========================================

print("Loading MiniLM model...")

minilm_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Loading MPNet model...")

mpnet_model = SentenceTransformer(
    "all-mpnet-base-v2"
)


# ==========================================
# 3. TEST QUESTIONS AND RELEVANT DOCUMENTS
# ==========================================

test_cases = [
    {
        "question": "What should happen when stock reaches reorder level?",
        "relevant_ids": ["doc1", "doc4"]
    },
    {
        "question": "How should warehouse inventory be monitored?",
        "relevant_ids": ["doc2", "doc5"]
    },
    {
        "question": "What are the supplier delivery requirements?",
        "relevant_ids": ["doc3"]
    }
]

TOP_K = 3


# ==========================================
# 4. EVALUATION FUNCTION
# ==========================================

def evaluate_model(model, collection, model_name):

    precision_scores = []
    recall_scores = []
    reciprocal_ranks = []
    response_times = []

    print("\n======================================")
    print("MODEL:", model_name)
    print("======================================")

    for test in test_cases:

        question = test["question"]
        relevant_ids = set(test["relevant_ids"])

        # Generate query embedding
        query_embedding = model.encode(
            [question]
        ).tolist()

        # Measure retrieval time
        start_time = time.perf_counter()

        results = collection.query(
            query_embeddings=query_embedding,
            n_results=TOP_K
        )

        end_time = time.perf_counter()

        elapsed_time = end_time - start_time
        response_times.append(elapsed_time)

        retrieved_ids = results["ids"][0]

        # Calculate relevant retrieved documents
        relevant_retrieved = [
            doc_id for doc_id in retrieved_ids
            if doc_id in relevant_ids
        ]

        # Precision@K
        precision = (
            len(relevant_retrieved) / TOP_K
        )

        # Recall@K
        recall = (
            len(relevant_retrieved) / len(relevant_ids)
        )

        # Reciprocal Rank
        reciprocal_rank = 0

        for rank, doc_id in enumerate(
            retrieved_ids,
            start=1
        ):

            if doc_id in relevant_ids:
                reciprocal_rank = 1 / rank
                break

        precision_scores.append(precision)
        recall_scores.append(recall)
        reciprocal_ranks.append(reciprocal_rank)

        print("\nQuestion:", question)

        print("Retrieved documents:", retrieved_ids)

        print("Relevant documents:", list(relevant_ids))

        print("Precision@3:", round(precision, 3))

        print("Recall@3:", round(recall, 3))

        print("Reciprocal Rank:", round(reciprocal_rank, 3))

        print("Retrieval Time:", round(elapsed_time, 5), "seconds")

    # Calculate average metrics
    average_precision = sum(precision_scores) / len(precision_scores)

    average_recall = sum(recall_scores) / len(recall_scores)

    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)

    average_time = sum(response_times) / len(response_times)

    return {
        "Model": model_name,
        "Precision@3": round(average_precision, 3),
        "Recall@3": round(average_recall, 3),
        "MRR": round(mrr, 3),
        "Average Retrieval Time (seconds)": round(average_time, 5)
    }


# ==========================================
# 5. COMPARE BOTH MODELS
# ==========================================

minilm_results = evaluate_model(
    minilm_model,
    minilm_collection,
    "all-MiniLM-L6-v2"
)

mpnet_results = evaluate_model(
    mpnet_model,
    mpnet_collection,
    "all-mpnet-base-v2"
)


# ==========================================
# 6. DISPLAY COMPARISON
# ==========================================

import pandas as pd

comparison = pd.DataFrame([
    minilm_results,
    mpnet_results
])

print("\n======================================")
print("       FINAL MODEL COMPARISON")
print("======================================")

print(comparison.to_string(index=False))

comparison.to_csv(
    "embedding_comparison_results.csv",
    index=False
)

print("\nResults saved to embedding_comparison_results.csv")
