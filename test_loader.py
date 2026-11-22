from vector_store import load_document

result = load_document("documents/test_inventory.xlsx")

print("\nExtracted Excel Document:")
print(result)