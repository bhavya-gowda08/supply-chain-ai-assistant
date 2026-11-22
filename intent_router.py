
import re


# =====================================================
# REPORT GENERATOR KEYWORDS
# =====================================================

REPORT_KEYWORDS = [
    "generate report",
    "create report",
    "prepare report",
    "download report",
    "export report",
    "inventory summary report",
    "inventory report",
    "warehouse report",
    "supplier report",
    "sales report",
    "logistics report",
    "quality report",
    "production report",
    "purchase order report",
    "shipment report",
    "stock report",
]


# =====================================================
# SQL ANALYTICS KEYWORDS
# =====================================================

SQL_KEYWORDS = [

    # Inventory
    "available stock",
    "current stock",
    "inventory details",
    "inventory status",
    "stock details",
    "stock level",
    "stock quantity",
    "low stock",
    "reorder level",
    "reorder quantity",
    "reorder point",
    "inventory quantity",
    "warehouse stock",
    "stock available",

    # Products
    "product details",
    "product information",
    "product price",
    "unit price",
    "price of",
    "product category",
    "product name",

    # Warehouse
    "warehouse details",
    "warehouse information",
    "warehouse location",
    "warehouse name",
    "warehouse name and location",
    "which warehouse",
    "list warehouses",
    "warehouse for",
    "where is the product stored",
    "where is detergent stored",
    "which warehouse stores",

    # Suppliers
    "supplier details",
    "supplier information",
    "supplier name",
    "contact number",
    "list suppliers",
    "who are the suppliers",
    "who are our suppliers",
    "who are the suppliers for",
    "who are the suppliers of",
    "show suppliers",

    # Sales
    "total sales revenue",
    "total revenue",
    "sales revenue",
    "total sales",
    "quantity sold",
    "total quantity sold",
    "how much quantity was sold",
    "quantity was sold",
    "how many units sold",
    "units sold",
    "sales history",
    "product wise sales",
    "product-wise sales",
    "sales of",
    "sales transactions",
    "sales summary",
    "sales data",

    # Purchase orders
    "purchase orders",
    "purchase order details",
    "purchase order status",
    "delayed purchase orders",

    # Production
    "production orders",
    "production order details",
    "production status",

    # Shipments
    "delayed shipments",
    "shipment details",
    "shipment status",
    "logistics details",

    # Quality
    "quality inspection",
    "inspection results",
    "quality results",
    "defective products",

    # General database questions
    "show records",
    "display records",
    "list products",
    "show products",
    "find product",
    "search product",
    "show warehouses",
]


# =====================================================
# RAG KEYWORDS
# =====================================================

RAG_KEYWORDS = [
    "policy",
    "policies",
    "sop",
    "standard operating procedure",
    "guidelines",
    "procedure",
    "procedures",
    "according to",
    "as per",
    "what does the document say",
    "what does the policy say",
    "explain the policy",
    "explain sop",
    "supplier evaluation",
    "supplier selection criteria",
    "safety stock policy",
    "inventory policy",
    "warehouse policy",
    "procurement guidelines",
    "production manual",
    "transportation policy",
    "quality policy",
    "how should",
    "why is",
    "explain how",
    "describe the process",
]


# =====================================================
# NORMALIZE QUESTION
# =====================================================

def normalize_question(question):

    question = question.lower().strip()

    question = re.sub(r"\s+", " ", question)

    return question


# =====================================================
# CHECK KEYWORDS
# =====================================================

def contains_keyword(question, keywords):

    for keyword in keywords:

        pattern = (
            r"(?<!\w)"
            + re.escape(keyword)
            + r"(?!\w)"
        )

        if re.search(pattern, question):
            return True

    return False


# =====================================================
# DETECT INTENT
# =====================================================

def detect_intent(question):

    question = normalize_question(question)

    if not question:
        return "supply_chain_rag"

    # Reports first
    if contains_keyword(question, REPORT_KEYWORDS):
        return "report_generator"

    # Explicit policy/document questions
    if contains_keyword(question, RAG_KEYWORDS):
        return "supply_chain_rag"

    # Database questions
    if contains_keyword(question, SQL_KEYWORDS):
        return "sql_analytics"

    # Default
    return "supply_chain_rag"


# =====================================================
# TEST CASES
# =====================================================

if __name__ == "__main__":

    test_questions = [

        # SQL
        "What is the available stock of detergent?",
        "Which warehouse stores the products?",
        "Who are the suppliers?",
        "What are the suppliers for detergent?",
        "What is the reorder level for detergent?",
        "Show low stock products",
        "What is the price of cooking oil?",
        "What is the warehouse name and location for detergent?",
        "Show delayed shipments",
        "Find production orders",
        "Show purchase orders",
        "Show quality inspection results",
        "What is the total sales revenue?",
        "What is the total revenue?",
        "How much quantity was sold?",
        "Show sales history",
        "Show product-wise sales",

        # RAG
        "What is the reorder policy?",
        "Why is stock monitoring important?",
        "How are suppliers evaluated?",
        "What does the warehouse SOP say?",
        "Explain safety stock policy",
        "According to policy, how should stock be monitored?",
        "Explain procurement guidelines",

        # Reports
        "Generate inventory summary report",
        "Prepare warehouse report",
        "Generate logistics report",
        "Create supplier report",
        "Generate quality report",
        "Generate sales report",
    ]

    print("\n========== INTENT ROUTER TESTING ==========\n")

    for question in test_questions:

        intent = detect_intent(question)

        print("Question :", question)
        print("Intent   :", intent)
        print("-" * 60)
