
from vector_store import (
    collection,
    load_parent_store,
    search_documents_with_metadata
)

print("\n========== DOCUMENT INDEX CHECK ==========")

# Check ChromaDB
total_chunks = collection.count()

print("Total ChromaDB chunks:", total_chunks)

# Check parent document storage
parent_store = load_parent_store() or {}

print("Total parent documents:", len(parent_store))

# Get indexed documents
stored = collection.get(
    include=["metadatas", "documents"]
)

metadatas = stored.get("metadatas") or []
documents = stored.get("documents") or []

# Display indexed document names
print("\nIndexed document names:")

sources = set()

for metadata in metadatas:

    metadata = metadata or {}

    source = metadata.get("source", "Unknown")

    sources.add(source)

for source in sorted(sources):
    print("-", source)

# Display sample metadata
print("\nSample metadata:")

for metadata in metadatas[:3]:
    print(metadata or {})

# Display sample extracted text
print("\nSample extracted document text:")

for document in documents[:2]:

    print(
        (document or "")[:500]
    )

# Test document retrieval
print("\n========== RAG RETRIEVAL TEST ==========")

results = search_documents_with_metadata(
    "What is the inventory reorder policy?",
    top_k=3
) or []

print("\nRetrieved documents:", len(results))

for index, result in enumerate(results, start=1):

    print(f"\nDocument {index}")

    print("Metadata:", result.get("metadata") or {})

    print("Content:")
    print((result.get("content") or "")[:500])

print("\n========== TEST COMPLETED ==========")
