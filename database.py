
import os
import pandas as pd
import pymysql

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# ==========================================
# 1. ENVIRONMENT CONFIGURATION
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "supply_chain_db")
DB_PORT = int(os.getenv("DB_PORT", "3306"))


# ==========================================
# 2. MYSQL DATABASE CONNECTION
# ==========================================

def get_connection():

    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )

    return connection


# ==========================================
# 3. SQLALCHEMY ENGINE
# ==========================================

def get_engine():

    database_url = URL.create(
        drivername="mysql+pymysql",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )

    engine = create_engine(database_url)

    return engine


# ==========================================
# 4. GENERIC TABLE RETRIEVAL
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
# 5. INVENTORY RETRIEVAL
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
# 6. DASHBOARD METRICS
# ==========================================

def get_dashboard_metrics():

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = (cursor.fetchone() or (0,))[0]

        cursor.execute("SELECT COUNT(*) FROM warehouses")
        total_warehouses = (cursor.fetchone() or (0,))[0]

        cursor.execute("SELECT COUNT(*) FROM suppliers")
        total_suppliers = (cursor.fetchone() or (0,))[0]

        cursor.execute(
            "SELECT SUM(available_stock) FROM inventory"
        )

        total_inventory = (cursor.fetchone() or (0,))[0]

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
# 7. ENTERPRISE TABLE RETRIEVAL FUNCTIONS
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
# 8. BUSINESS DATA FUNCTIONS
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
# 9. ENTERPRISE DASHBOARD METRICS
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

            cursor.execute(
                f"SELECT COUNT(*) FROM `{table}`"
            )

            metrics[table] = (cursor.fetchone() or (0,))[0]

        cursor.close()

        return metrics

    finally:
        connection.close()
