
from sentence_transformers import SentenceTransformer

print("\n====================================")
print("   EMBEDDING MODEL COMPARISON")
print("====================================")

# =====================================
# MODEL 1: MiniLM
# =====================================

print("\nLoading Model 1: all-MiniLM-L6-v2")

model1 = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Model 1 loaded successfully!")


# =====================================
# MODEL 2: MPNet
# =====================================

print("\nLoading Model 2: all-mpnet-base-v2")

model2 = SentenceTransformer(
    "all-mpnet-base-v2"
)

print("Model 2 loaded successfully!")


# =====================================
# TEST SENTENCES
# =====================================

sentences = [
    "When inventory reaches the reorder level, "
    "a replenishment request should be initiated.",

    "Warehouse managers should monitor available stock.",

    "Suppliers are responsible for delivering products "
    "according to purchase orders."
]


# =====================================
# GENERATE EMBEDDINGS
# =====================================

print("\nGenerating Model 1 embeddings...")

embeddings1 = model1.encode(sentences)

print("Model 1 embedding shape:", embeddings1.shape)


print("\nGenerating Model 2 embeddings...")

embeddings2 = model2.encode(sentences)

print("Model 2 embedding shape:", embeddings2.shape)


# =====================================
# DISPLAY RESULTS
# =====================================

print("\n====================================")
print("       COMPARISON RESULTS")
print("====================================")

print("Model 1: all-MiniLM-L6-v2")
print("Embedding dimension:", embeddings1.shape[1])

print("\nModel 2: all-mpnet-base-v2")
print("Embedding dimension:", embeddings2.shape[1])

print("\nBoth embedding models loaded and tested successfully!")
