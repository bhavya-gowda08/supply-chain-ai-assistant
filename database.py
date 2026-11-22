
import pymysql
import pandas as pd
from sqlalchemy import create_engine


# ==========================================
# 1. MYSQL DATABASE CONNECTION
# ==========================================

def get_connection():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="supply_chain_db",
        port=3306
    )
    return connection


# ==========================================
# 2. SQLALCHEMY ENGINE
# ==========================================

def get_engine():
    engine = create_engine(
        "mysql+pymysql://root:root@localhost:3306/supply_chain_db"
    )
    return engine


# ==========================================
# 3. GENERIC TABLE RETRIEVAL
# ==========================================

def get_table_data(table_name):
    allowed_tables = [
        "products",
        "inventory",
        "warehouses",
        "suppliers",
        "sales",
        "manufacturing_plants",
        "distribution_centers",
        "purchase_orders",
        "production_orders",
        "demand_forecasts",
        "logistics_shipments",
        "quality_inspections",
        "retail_orders",
        "customer_orders"
    ]

    if table_name not in allowed_tables:
        raise ValueError("Invalid table name")

    engine = get_engine()

    try:
        query = f"SELECT * FROM `{table_name}`"
        return pd.read_sql(query, engine)
    finally:
        engine.dispose()


# ==========================================
# 4. EXISTING INVENTORY RETRIEVAL
# ==========================================

def get_inventory():
    engine = get_engine()

    query = """
    SELECT
        p.product_name,
        i.available_stock,
        i.reorder_level,
        w.location
    FROM inventory i
    JOIN products p
        ON i.product_id = p.product_id
    JOIN warehouses w
        ON i.warehouse_id = w.warehouse_id
    """

    try:
        return pd.read_sql(query, engine)
    finally:
        engine.dispose()


# ==========================================
# 5. EXISTING DASHBOARD METRICS
# ==========================================

def get_dashboard_metrics():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM warehouses")
        total_warehouses = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM suppliers")
        total_suppliers = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(available_stock) FROM inventory")
        total_inventory = cursor.fetchone()[0] or 0

        cursor.close()

        return (
            total_products,
            total_warehouses,
            total_suppliers,
            total_inventory
        )
    finally:
        connection.close()


# ==========================================
# 6. ENTERPRISE TABLE RETRIEVAL FUNCTIONS
# ==========================================

def get_demand_forecasts():
    return get_table_data("demand_forecasts")


def get_purchase_orders():
    return get_table_data("purchase_orders")


def get_production_orders():
    return get_table_data("production_orders")


def get_logistics_shipments():
    return get_table_data("logistics_shipments")


def get_quality_inspections():
    return get_table_data("quality_inspections")


def get_retail_orders():
    return get_table_data("retail_orders")


def get_customer_orders():
    return get_table_data("customer_orders")


def get_manufacturing_plants():
    return get_table_data("manufacturing_plants")


def get_distribution_centers():
    return get_table_data("distribution_centers")


# ==========================================
# 7. EXISTING BUSINESS DATA FUNCTIONS
# ==========================================

def get_products():
    return get_table_data("products")


def get_warehouses():
    return get_table_data("warehouses")


def get_suppliers():
    return get_table_data("suppliers")


def get_sales():
    return get_table_data("sales")


# ==========================================
# 8. ENTERPRISE DASHBOARD METRICS
# ==========================================

def get_enterprise_metrics():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        metrics = {}

        tables = [
            "products",
            "inventory",
            "warehouses",
            "suppliers",
            "sales",
            "purchase_orders",
            "production_orders",
            "demand_forecasts",
            "logistics_shipments",
            "quality_inspections",
            "retail_orders",
            "customer_orders",
            "manufacturing_plants",
            "distribution_centers"
        ]

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            metrics[table] = cursor.fetchone()[0]

        return metrics

    finally:
        connection.close()
