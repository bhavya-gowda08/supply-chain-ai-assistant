
from docx import Document
import os

os.makedirs("documents", exist_ok=True)

doc = Document()

doc.add_heading("SUPPLY CHAIN MANAGEMENT POLICY", level=1)

doc.add_heading("Inventory Management", level=2)

doc.add_paragraph(
    "Inventory management monitors available stock "
    "in warehouses. Products include Soap, Shampoo, "
    "Detergent, Toothpaste and Cooking Oil."
)

doc.add_heading("Reorder Policy", level=2)

products = [
    ("Soap", 100),
    ("Shampoo", 80),
    ("Detergent", 150),
    ("Toothpaste", 100),
    ("Cooking Oil", 120)
]

for product, units in products:
    doc.add_paragraph(f"{product}: {units} units")

doc.add_paragraph(
    "When stock reaches or falls below the reorder "
    "level, a replenishment request should be initiated."
)

file_path = "documents/supply_chain_policy.docx"

doc.save(file_path)

print("DOCX file created successfully!")
print("Location:", file_path)
