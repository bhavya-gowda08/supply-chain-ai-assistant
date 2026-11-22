
from vector_store import extract_pdf_pages, split_text

pdf_path = "documents/supply_chain_policy.pdf"

print("Reading PDF...")

pages = extract_pdf_pages(pdf_path)
text = "\n".join(page["content"] for page in pages)

print("PDF extraction successful!")

print("Total characters:", len(text))

chunks = split_text(text)

print("Total chunks:", len(chunks))

print("\nFirst chunk:")

if chunks:
    print(chunks[0])
else:
    print("No text found in PDF.")
