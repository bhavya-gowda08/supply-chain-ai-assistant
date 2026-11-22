import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

os.makedirs("documents", exist_ok=True)

pdf_path = "documents/supply_chain_policy.pdf"

doc = SimpleDocTemplate(pdf_path, pagesize=A4)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "CustomTitle",
    parent=styles["Title"],
    textColor=colors.darkblue,
    fontSize=18,
    spaceAfter=20
)

heading_style = ParagraphStyle(
    "CustomHeading",
    parent=styles["Heading2"],
    textColor=colors.darkblue,
    spaceBefore=12
)

content = []

content.append(Paragraph(
    "SUPPLY CHAIN MANAGEMENT POLICY",
    title_style
))

sections = [
    ("1. Introduction",
     "Supply Chain Management involves planning, sourcing, purchasing, storing and distributing products efficiently."),

    ("2. Inventory Management",
     "Inventory management monitors available stock in warehouses. Products include Soap, Shampoo, Detergent, Toothpaste and Cooking Oil."),

    ("3. Reorder Policy",
     "Soap: 100 units<br/>Shampoo: 80 units<br/>Detergent: 150 units<br/>Toothpaste: 100 units<br/>Cooking Oil: 120 units.<br/><br/>When stock reaches or falls below the reorder level, a replenishment request should be initiated."),

    ("4. Warehouse Management",
     "The company operates warehouses in Bangalore, Mysore and Chennai. Warehouses receive, store and dispatch products."),

    ("5. Supplier Management",
     "Suppliers provide products and raw materials. They are evaluated based on quality, delivery time, pricing and reliability."),

    ("6. Demand Planning",
     "Demand planning estimates future product requirements using historical sales, market trends and customer demand."),

    ("7. Stock Monitoring",
     "Inventory should be monitored regularly. Low-stock products must be reported to the inventory management team."),

    ("8. Conclusion",
     "Effective supply chain management improves inventory control, reduces operational costs and ensures timely product delivery.")
]

for heading, text in sections:
    content.append(Paragraph(heading, heading_style))
    content.append(Paragraph(text, styles["BodyText"]))
    content.append(Spacer(1, 10))

doc.build(content)

print("PDF created successfully!")
print("Location:", pdf_path)
