
import chromadb
from sentence_transformers import SentenceTransformer

# =====================================
# INITIALIZE CHROMADB
# =====================================

client = chromadb.PersistentClient(
    path="data/embedding_comparison"
)

# =====================================
# LOAD BOTH MODELS
# =====================================

print("Loading MiniLM model...")

model1 = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Loading MPNet model...")

model2 = SentenceTransformer(
    "all-mpnet-base-v2"
)

# =====================================
# SAMPLE SUPPLY CHAIN DOCUMENTS
# =====================================

documents = [
    "When available stock reaches the reorder level, "
    "a replenishment request should be initiated.",

    "Warehouse managers should monitor inventory levels regularly.",

    "Suppliers must deliver products according to purchase orders.",

    "Low stock products require immediate replenishment planning.",

    "Inventory reports should be reviewed regularly by managers."
]

ids = [
    "doc1",
    "doc2",
    "doc3",
    "doc4",
    "doc5"
]

# =====================================
# CREATE SEPARATE COLLECTIONS
# =====================================

collection1 = client.get_or_create_collection(
    name="supply_chain_minilm"
)

collection2 = client.get_or_create_collection(
    name="supply_chain_mpnet"
)

# =====================================
# GENERATE EMBEDDINGS
# =====================================

print("\nGenerating MiniLM embeddings...")

embeddings1 = model1.encode(
    documents
).tolist()

print("Generating MPNet embeddings...")

embeddings2 = model2.encode(
    documents
).tolist()

# =====================================
# STORE IN CHROMADB
# =====================================

collection1.upsert(
    ids=ids,
    documents=documents,
    embeddings=embeddings1
)

collection2.upsert(
    ids=ids,
    documents=documents,
    embeddings=embeddings2
)

# =====================================
# VERIFY COLLECTIONS
# =====================================

print("\n========== RESULTS ==========")

print(
    "MiniLM documents:",
    collection1.count()
)

print(
    "MPNet documents:",
    collection2.count()
)

print("\nBoth ChromaDB collections created successfully!")
