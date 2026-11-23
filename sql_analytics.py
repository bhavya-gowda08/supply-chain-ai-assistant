
import pandas as pd
from sqlalchemy import text
from database import get_engine


# ==========================================
# SQL ANALYTICS MODULE
# ==========================================

def execute_analytics(question):

    question = question.lower().strip()
    engine = get_engine()

    try:

        query = None
        query_params = {}

        # ======================================
        # 1. PRODUCTION COMPLETION DETAILS
        # ======================================

        if any(word in question for word in [
            "production",
            "produced quantity",
            "production completion",
            "production orders",
            "production status"
        ]):

            query = """
            SELECT
                po.production_id,
                p.product_name,
                po.planned_quantity,
                po.produced_quantity,
                (po.planned_quantity - po.produced_quantity)
                    AS remaining_quantity,
                po.start_date,
                po.completion_date,
                po.status
            FROM production_orders po
            JOIN products p
                ON po.product_id = p.product_id
            ORDER BY p.product_name
            """

        # ======================================
        # 2. SUPPLIERS WITH HIGHEST PURCHASE ORDERS
        # ======================================

        elif (
            "supplier" in question
            and any(word in question for word in [
                "highest",
                "most",
                "maximum",
                "number of purchase orders",
                "purchase order count",
                "highest number"
            ])
        ):

            query = """
            SELECT
                s.supplier_id,
                s.supplier_name,
                COUNT(po.po_id) AS total_purchase_orders
            FROM suppliers s
            INNER JOIN purchase_orders po
                ON s.supplier_id = po.supplier_id
            GROUP BY
                s.supplier_id,
                s.supplier_name
            ORDER BY
                total_purchase_orders DESC
            """

        # ======================================
        # 3. PURCHASE ORDER INFORMATION
        # ======================================

        elif any(word in question for word in [
            "purchase order",
            "purchase orders",
            "delayed purchase",
            "pending purchase"
        ]):

            query = """
            SELECT
                po.po_id,
                p.product_name,
                s.supplier_name,
                po.order_quantity,
                po.order_date,
                po.expected_delivery,
                po.actual_delivery,
                po.status
            FROM purchase_orders po
            JOIN products p
                ON po.product_id = p.product_id
            JOIN suppliers s
                ON po.supplier_id = s.supplier_id
            ORDER BY po.order_date DESC
            """

        # ======================================
        # 4. SUPPLIER INFORMATION
        # ======================================

        elif "supplier" in question:

            query = """
            SELECT
                supplier_id,
                supplier_name,
                contact_number
            FROM suppliers
            ORDER BY supplier_name
            """

        # ======================================
        # 5. WAREHOUSE INFORMATION
        # ======================================

        elif "warehouse" in question:

            product_names = pd.read_sql(
                "SELECT product_name FROM products",
                engine
            )["product_name"].dropna().tolist()

            matched_product = next(
                (
                    name for name in product_names
                    if name.lower() in question
                ),
                None
            )

            if matched_product:

                query = """
                SELECT
                    p.product_name,
                    w.warehouse_name,
                    w.location,
                    i.available_stock,
                    i.reorder_level
                FROM inventory i
                JOIN products p
                    ON i.product_id = p.product_id
                JOIN warehouses w
                    ON i.warehouse_id = w.warehouse_id
                WHERE LOWER(p.product_name) = LOWER(:product_name)
                """

                query_params = {
                    "product_name": matched_product
                }

            else:

                query = """
                SELECT
                    warehouse_id,
                    warehouse_name,
                    location
                FROM warehouses
                """

        # ======================================
        # 6. LOW STOCK PRODUCTS
        # ======================================

        elif any(phrase in question for phrase in [
            "low stock",
            "below reorder",
            "reorder required",
            "replenishment required"
        ]):

            query = """
            SELECT
                p.product_name,
                i.available_stock,
                i.reorder_level,
                w.warehouse_name,
                w.location
            FROM inventory i
            JOIN products p
                ON i.product_id = p.product_id
            JOIN warehouses w
                ON i.warehouse_id = w.warehouse_id
            WHERE i.available_stock <= i.reorder_level
            ORDER BY i.available_stock ASC
            """

        # ======================================
        # 7. QUALITY INSPECTION
        # ======================================

        elif any(word in question for word in [
            "quality",
            "inspection",
            "defective",
            "defect",
            "failed inspection"
        ]):

            query = """
            SELECT
                qi.inspection_id,
                p.product_name,
                qi.inspected_quantity,
                qi.defective_quantity,
                qi.quality_status,
                qi.inspection_date
            FROM quality_inspections qi
            JOIN products p
                ON qi.product_id = p.product_id
            WHERE LOWER(TRIM(COALESCE(qi.quality_status, '')))
                IN ('failed', 'fail')
            ORDER BY qi.inspection_date DESC
            """

        # ======================================
        # 8. LOGISTICS AND SHIPMENT INFORMATION
        # ======================================

        elif any(word in question for word in [
            "shipment",
            "logistics",
            "transport",
            "delivery status",
            "delayed delivery"
        ]):

            query = """
            SELECT
                ls.shipment_id,
                ls.origin,
                ls.destination,
                ls.expected_delivery_date,
                ls.actual_delivery_date,
                ls.status
            FROM logistics_shipments ls
            ORDER BY ls.expected_delivery_date
            """

        # ======================================
        # 9. DEMAND FORECAST ANALYTICS
        # ======================================

        elif any(word in question for word in [
            "demand forecast",
            "predicted demand",
            "forecast",
            "actual demand"
        ]):

            query = """
            SELECT
                p.product_name,
                df.predicted_demand,
                df.actual_demand,
                (df.actual_demand - df.predicted_demand)
                    AS demand_difference
            FROM demand_forecasts df
            JOIN products p
                ON df.product_id = p.product_id
            ORDER BY p.product_name
            """

        # ======================================
        # 10. SALES ANALYTICS
        # ======================================

        elif any(word in question for word in [
            "sales",
            "revenue",
            "quantity sold",
            "sold products",
            "total amount"
        ]):

            if "total quantity sold" in question:

                query = """
                SELECT
                    SUM(quantity_sold) AS total_quantity_sold
                FROM sales
                """

            elif any(word in question for word in [
                "total sales",
                "total revenue",
                "sales revenue",
                "total amount"
            ]):

                query = """
                SELECT
                    COUNT(*) AS total_transactions,
                    SUM(quantity_sold) AS total_quantity_sold,
                    SUM(total_amount) AS total_revenue
                FROM sales
                """

            elif any(phrase in question for phrase in [
                "product wise",
                "product-wise",
                "each product",
                "by product"
            ]):

                query = """
                SELECT
                    p.product_name,
                    SUM(s.quantity_sold) AS total_quantity_sold,
                    SUM(s.total_amount) AS total_revenue
                FROM sales s
                JOIN products p
                    ON s.product_id = p.product_id
                GROUP BY
                    p.product_id,
                    p.product_name
                ORDER BY total_revenue DESC
                """

            else:

                query = """
                SELECT
                    s.sale_id,
                    p.product_name,
                    s.quantity_sold,
                    s.sale_date,
                    s.total_amount
                FROM sales s
                JOIN products p
                    ON s.product_id = p.product_id
                ORDER BY s.sale_date DESC
                """

        # ======================================
        # 11. INVENTORY AND REORDER INFORMATION
        # ======================================

        elif any(word in question for word in [
            "inventory",
            "stock",
            "quantity",
            "available",
            "reorder level"
        ]):

            query = """
            SELECT
                p.product_name,
                i.available_stock,
                i.reorder_level,
                w.warehouse_name,
                w.location
            FROM inventory i
            JOIN products p
                ON i.product_id = p.product_id
            JOIN warehouses w
                ON i.warehouse_id = w.warehouse_id
            ORDER BY i.available_stock ASC
            """

        # ======================================
        # 12. PRODUCT INFORMATION AND PRICE
        # ======================================

        elif "product" in question or "price" in question:

            query = """
            SELECT
                product_id,
                product_name,
                category,
                unit_price
            FROM products
            """

        else:

            return "I could not identify the required SQL operation."

        # ======================================
        # 13. EXECUTE SQL QUERY
        # ======================================

        df = pd.read_sql(
            text(query),
            engine,
            params=query_params
        )

        if df.empty:

            return "No matching records found in the database."

        # ======================================
        # 14. PRODUCT NAME FILTERING
        # ======================================

        if "product_name" in df.columns:

            product_names = pd.read_sql(
                "SELECT product_name FROM products",
                engine
            )["product_name"].dropna().tolist()

            matched_product = next(
                (
                    name for name in product_names
                    if name.lower() in question
                ),
                None
            )

            if matched_product:

                df = df[
                    df["product_name"].str.lower()
                    == matched_product.lower()
                ]

        if df.empty:

            return "No matching records found for that product."

        # ======================================
        # 15. RETURN RESULTS
        # ======================================

        return df.to_string(index=False)

    except Exception as error:

        return f"SQL Analytics Error: {error}"


# ==========================================
# TEST SQL ANALYTICS MODULE
# ==========================================

if __name__ == "__main__":

    test_questions = [

        "Who are the suppliers?",

        "Which suppliers have the highest number of purchase orders?",

        "Show all warehouses",

        "What is the warehouse for detergent?",

        "Show inventory details",

        "Show low stock products",

        "What is the price of cooking oil?",

        "Show sales history",

        "What is the total sales revenue?",

        "Show product wise sales",

        "Show production completion details for all products",

        "Show all purchase orders",

        "Which products have quality inspection failures?",

        "Which shipments are delayed?",

        "Compare predicted demand and actual demand for all products"

    ]

    print("\n")
    print("=" * 55)
    print("          SQL ANALYTICS MODULE TESTING")
    print("=" * 55)

    for question in test_questions:

        print("\n" + "=" * 55)
        print("Question:", question)

        result = execute_analytics(question)

        print("\nSQL Result:")
        print(result)

    print("\n")
    print("=" * 55)
    print("             TESTING COMPLETED")
    print("=" * 55)
