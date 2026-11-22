
import chromadb

client = chromadb.PersistentClient(
    path="data/chroma_db"
)

collection = client.get_or_create_collection(
    name="supply_chain_documents"
)

print("ChromaDB connected successfully!")

print("Total stored chunks:",
      collection.count())

results = collection.query(
    query_texts=["What is the reorder level for detergent?"],
    n_results=1
)

print("\nRetrieved information:")

for document in results["documents"][0]:
    print(document)
