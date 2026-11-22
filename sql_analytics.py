
import pandas as pd

from sqlalchemy import text

from database import get_engine


# =====================================================
# 1. SQL ANALYTICS MODULE
# =====================================================

def execute_analytics(question):

    if not question or not question.strip():

        return "Please enter a valid question."

    question = question.lower().strip()

    engine = get_engine()

    query = None
    query_params = {}

    try:

        # =================================================
        # 2. PRODUCTION COMPLETION DETAILS
        # =================================================

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
                    (
                        po.planned_quantity - po.produced_quantity
                    ) AS remaining_quantity,
                    po.start_date,
                    po.completion_date,
                    po.status
                FROM production_orders po
                JOIN products p
                    ON po.product_id = p.product_id
                ORDER BY p.product_name
            """

        # =================================================
        # 3. PURCHASE ORDER INFORMATION
        # =================================================

        elif any(word in question for word in [
            "purchase order",
            "purchase orders",
            "delayed purchase",
            "pending purchase"
        ]):

            query = """
                SELECT
                    po.purchase_order_id,
                    p.product_name,
                    s.supplier_name,
                    po.quantity,
                    po.order_date,
                    po.expected_delivery_date,
                    po.status
                FROM purchase_orders po
                JOIN products p
                    ON po.product_id = p.product_id
                JOIN suppliers s
                    ON po.supplier_id = s.supplier_id
                ORDER BY po.order_date DESC
            """

        # =================================================
        # 4. SUPPLIER INFORMATION
        # =================================================

        elif "supplier" in question:

            query = """
                SELECT
                    supplier_id,
                    supplier_name,
                    contact_number
                FROM suppliers
                ORDER BY supplier_name
            """

        # =================================================
        # 5. WAREHOUSE INFORMATION
        # =================================================

        elif "warehouse" in question:

            product_names = get_product_names(engine)

            matched_product = find_product(
                question,
                product_names
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
                    WHERE LOWER(p.product_name)
                        = LOWER(:product_name)
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
                    ORDER BY warehouse_name
                """

        # =================================================
        # 6. LOW STOCK PRODUCTS
        # =================================================

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

        # =================================================
        # 7. QUALITY INSPECTION
        # =================================================

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
                WHERE
                    LOWER(
                        TRIM(
                            COALESCE(qi.quality_status, '')
                        )
                    ) IN ('failed', 'fail')
                ORDER BY qi.inspection_date DESC
            """

        # =================================================
        # 8. LOGISTICS AND SHIPMENT INFORMATION
        # =================================================

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

        # =================================================
        # 9. DEMAND FORECAST ANALYTICS
        # =================================================

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
                    (
                        df.actual_demand - df.predicted_demand
                    ) AS demand_difference
                FROM demand_forecasts df
                JOIN products p
                    ON df.product_id = p.product_id
                ORDER BY p.product_name
            """

        # =================================================
        # 10. SALES ANALYTICS
        # =================================================

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
                        SUM(s.quantity_sold)
                            AS total_quantity_sold,
                        SUM(s.total_amount)
                            AS total_revenue
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

        # =================================================
        # 11. INVENTORY AND REORDER INFORMATION
        # =================================================

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
                ORDER BY p.product_name
            """

        # =================================================
        # 12. PRODUCT INFORMATION AND PRICE
        # =================================================

        elif "product" in question or "price" in question:

            query = """
                SELECT
                    product_id,
                    product_name,
                    category,
                    unit_price
                FROM products
                ORDER BY product_name
            """

        else:

            return (
                "I could not identify the required SQL operation. "
                "Please ask about inventory, products, suppliers, "
                "warehouses, sales, production, purchase orders, "
                "quality, shipments or demand forecasts."
            )

        # =================================================
        # 13. EXECUTE SQL QUERY
        # =================================================

        with engine.connect() as connection:

            dataframe = pd.read_sql_query(
                text(query),
                connection,
                params=query_params
            )

            # Load product names for product filtering.
            product_names = get_product_names(
                engine,
                connection=connection
            )

        if dataframe.empty:

            return (
                "No matching records found in the database."
            )

        # =================================================
        # 14. FILTER BY PRODUCT NAME
        # =================================================

        if "product_name" in dataframe.columns:

            matched_product = find_product(
                question,
                product_names
            )

            if matched_product:

                dataframe = dataframe[
                    dataframe["product_name"]
                    .fillna("")
                    .astype(str)
                    .str.casefold()
                    == matched_product.casefold()
                ]

        if dataframe.empty:

            return (
                "No matching records found for that product."
            )

        # =================================================
        # 15. FORMAT RESULTS
        # =================================================

        return dataframe.to_string(
            index=False
        )

    except Exception as error:

        print(
            "SQL Analytics Error:",
            error
        )

        return f"SQL Analytics Error: {error}"


# =====================================================
# 16. GET PRODUCT NAMES
# =====================================================

def get_product_names(engine, connection=None):

    try:

        if connection is not None:

            dataframe = pd.read_sql_query(
                text(
                    "SELECT product_name FROM products"
                ),
                connection
            )

        else:

            with engine.connect() as conn:

                dataframe = pd.read_sql_query(
                    text(
                        "SELECT product_name FROM products"
                    ),
                    conn
                )

        return (
            dataframe["product_name"]
            .dropna()
            .astype(str)
            .tolist()
        )

    except Exception as error:

        print(
            "Product lookup error:",
            error
        )

        return []


# =====================================================
# 17. FIND PRODUCT IN QUESTION
# =====================================================

def find_product(question, product_names):

    question = question.casefold()

    # Longest match first avoids matching a shorter
    # product name when a longer one is present.

    sorted_names = sorted(
        product_names,
        key=len,
        reverse=True
    )

    for product_name in sorted_names:

        product_name = product_name.strip()

        if not product_name:
            continue

        pattern = (
            r"(?<!\w)"
            + __import__("re").escape(
                product_name.casefold()
            )
            + r"(?!\w)"
        )

        if __import__("re").search(
            pattern,
            question
        ):

            return product_name

    return None


# =====================================================
# 18. TEST SQL ANALYTICS MODULE
# =====================================================

if __name__ == "__main__":

    test_questions = [

        "Who are the suppliers?",

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

    print("=" * 60)

    print("          SQL ANALYTICS MODULE TESTING")

    print("=" * 60)

    for question in test_questions:

        print("\n" + "=" * 60)

        print("Question:", question)

        result = execute_analytics(question)

        print("\nSQL Result:")

        print(result)

    print("\n")

    print("=" * 60)

    print("             TESTING COMPLETED")

    print("=" * 60)
