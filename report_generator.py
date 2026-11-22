import os
from datetime import datetime

import pandas as pd
from database import get_engine


# ==========================================
# REPORT GENERATOR MODULE
# ==========================================

REPORT_FOLDER = "reports"

os.makedirs(REPORT_FOLDER, exist_ok=True)


# ==========================================
# 1. GET INVENTORY DATA
# ==========================================

def get_inventory_data():

    query = """
        SELECT
            p.product_id,
            p.product_name,
            p.category,
            i.available_stock,
            i.reorder_level,
            w.warehouse_name,
            w.location
        FROM inventory i
        JOIN products p
            ON i.product_id = p.product_id
        JOIN warehouses w
            ON i.warehouse_id = w.warehouse_id
    """

    engine = get_engine()

    return pd.read_sql(query, engine)


# ==========================================
# 2. GENERATE INVENTORY SUMMARY REPORT
# ==========================================

def generate_inventory_report():

    df = get_inventory_data()

    if df.empty:
        return "No inventory records found."

    df["stock_status"] = df.apply(
        lambda row: (
            "Low Stock"
            if row["available_stock"] <= row["reorder_level"]
            else "Healthy"
        ),
        axis=1
    )

    filename = (
        f"inventory_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    filepath = os.path.join(REPORT_FOLDER, filename)

    df.to_csv(filepath, index=False)

    return filepath


# ==========================================
# 3. GENERATE LOW STOCK REPORT
# ==========================================

def generate_low_stock_report():

    df = get_inventory_data()

    if df.empty:
        return "No inventory records found."

    low_stock = df[
        df["available_stock"] <= df["reorder_level"]
    ]

    if low_stock.empty:
        return (
            "No low-stock products found. "
            "All products are currently above their reorder levels."
        )

    filename = (
        f"low_stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    filepath = os.path.join(REPORT_FOLDER, filename)

    low_stock.to_csv(filepath, index=False)

    return filepath


# ==========================================
# 4. GENERATE WAREHOUSE REPORT
# ==========================================

def generate_warehouse_report():

    df = get_inventory_data()

    if df.empty:
        return "No warehouse inventory records found."

    warehouse_report = (
        df.groupby(
            ["warehouse_name", "location"],
            as_index=False
        )
        .agg(
            total_products=("product_id", "nunique"),
            total_available_stock=("available_stock", "sum"),
            total_reorder_level=("reorder_level", "sum")
        )
    )

    filename = (
        f"warehouse_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )

    filepath = os.path.join(REPORT_FOLDER, filename)

    warehouse_report.to_csv(filepath, index=False)

    return filepath


# ==========================================
# 5. REPORT INTENT DETECTION
# ==========================================

def generate_report(question):

    question = question.lower().strip()

    try:

        if "low stock" in question:

            return generate_low_stock_report()

        elif "warehouse" in question:

            return generate_warehouse_report()

        elif any(word in question for word in [
            "inventory",
            "summary",
            "supply chain"
        ]):

            return generate_inventory_report()

        else:

            return (
                "Report type not identified. "
                "Please request an inventory, low stock, "
                "or warehouse report."
            )

    except Exception as error:

        return f"Report Generation Error: {error}"


# ==========================================
# 6. TEST REPORT GENERATOR
# ==========================================

if __name__ == "__main__":

    test_questions = [

        "Generate an inventory summary report",

        "Generate a low stock report",

        "Generate a warehouse report"

    ]

    for question in test_questions:

        print("\nQuestion:", question)

        result = generate_report(question)

        print("Report Result:", result)