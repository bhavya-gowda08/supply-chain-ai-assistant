
from vector_store import extract_pdf_pages

pdf_path = "documents/supply_chain_policy.pdf"

pages = extract_pdf_pages(pdf_path)

print("\nTotal pages extracted:", len(pages))

for i, page in enumerate(pages, start=1):
    print(f"\n--- Page {i} ---")
    print(page)
