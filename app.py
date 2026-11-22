import os
import json
import hashlib
import hmac

import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv

load_dotenv()

from database import (
    get_connection,
    get_inventory,
    get_dashboard_metrics,
    get_enterprise_metrics
)

from rag import ask_question, clear_memory
from vector_store import process_document


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Enterprise Supply Chain AI Assistant",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# 2. CONSTANTS
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "documents",
    "uploaded_docs"
)

os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TABLES = [
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


# =====================================================
# 3. SESSION STATE
# =====================================================

def initialize_session_state():

    defaults = {
        "messages": [],
        "processed_documents": []
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


initialize_session_state()


# =====================================================
# 3A. BASIC LOGIN AND ROLE IDENTIFICATION
# =====================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "user_role" not in st.session_state:
    st.session_state.user_role = ""


def authenticate_user(username, password):
    """Authenticate demo users using credentials stored in .env."""

    users = {
        os.getenv("ADMIN_USERNAME"): {
            "password": os.getenv("ADMIN_PASSWORD"),
            "role": "Administrator"
        },
        os.getenv("PLANNER_USERNAME"): {
            "password": os.getenv("PLANNER_PASSWORD"),
            "role": "Demand Planner"
        },
        os.getenv("WAREHOUSE_USERNAME"): {
            "password": os.getenv("WAREHOUSE_PASSWORD"),
            "role": "Warehouse Manager"
        }
    }

    user = users.get(username)

    if (
        user
        and user.get("password")
        and hmac.compare_digest(password, user["password"])
    ):
        return user["role"]

    return None


if not st.session_state.logged_in:

    st.title("📦 Supply Chain AI Assistant")
    st.subheader("User Login")
    st.write("Sign in to access the supply chain dashboard.")

    with st.form("login_form"):

        login_username = st.text_input("Username")
        login_password = st.text_input(
            "Password",
            type="password"
        )

        login_submitted = st.form_submit_button(
            "Login",
            type="primary",
            use_container_width=True
        )

    if login_submitted:

        authenticated_role = authenticate_user(
            login_username.strip(),
            login_password
        )

        if authenticated_role:

            st.session_state.logged_in = True
            st.session_state.username = login_username.strip()
            st.session_state.user_role = authenticated_role

            st.rerun()

        else:
            st.error("Invalid username or password.")

    st.stop()


# =====================================================
# 4. SAFE NUMBER CONVERSION
# =====================================================

def safe_number(value):

    try:

        if value is None or pd.isna(value):
            return 0

        return int(value)

    except (ValueError, TypeError, OverflowError):

        return 0


# =====================================================
# 5. DATABASE TABLE HELPER
# =====================================================

def load_table(table_name):

    if table_name not in ALLOWED_TABLES:

        raise ValueError(
            f"Invalid table name: {table_name}"
        )

    connection = get_connection()

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute(
            f"SELECT * FROM `{table_name}`"
        )

        rows = cursor.fetchall()

        columns = [
            column[0]
            for column in cursor.description
        ]

        dataframe = pd.DataFrame(
            rows,
            columns=columns
        )

        return dataframe

    finally:

        if cursor is not None:
            cursor.close()

        connection.close()


# =====================================================
# 6. DATAFRAME DISPLAY HELPER
# =====================================================

def show_dataframe(dataframe, message):

    if dataframe is not None and not dataframe.empty:

        st.dataframe(
            dataframe,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(message)


# =====================================================
# 7. DOWNLOAD HELPER
# =====================================================

def add_download_button(
    dataframe,
    label,
    filename,
    key
):

    if dataframe is None or dataframe.empty:

        st.info("No data available to download.")

        return

    csv_data = dataframe.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label=label,
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        key=key
    )


# =====================================================
# 8. CUSTOM STYLING
# =====================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 36px;
        font-weight: bold;
        color: #263859;
    }

    .subtitle {
        font-size: 17px;
        color: #64748b;
    }

    div[data-testid="stMetric"] {
        background-color: #f8fafc;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =====================================================
# 9. HEADER
# =====================================================

st.markdown(
    '<p class="main-title">📦 Supply Chain AI Assistant</p>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <p class="subtitle">
    Enterprise AI Demand Planning and Supply Chain Intelligence
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()


# =====================================================
# 10. SIDEBAR
# =====================================================

with st.sidebar:

    st.title("📦 Navigation")

    st.write(f"Signed in: **{st.session_state.username}**")
    st.write(f"Role: **{st.session_state.user_role}**")

    if st.button(
        "Logout",
        key="logout_button",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_role = ""
        st.session_state.messages = []

        clear_memory()

        st.rerun()

    st.divider()

    st.markdown(
        """
        - Supply Chain Dashboard
        - Enterprise Analytics
        - Reports and Downloads
        - Document Management
        - AI Chatbot
        """
    )

    st.divider()

    st.subheader("Application Information")

    st.write("Database: MySQL")
    st.write("AI Model: Gemini")
    st.write("Vector Database: ChromaDB")
    st.write("Framework: Streamlit")


# =====================================================
# 11. MAIN SUPPLY CHAIN DASHBOARD
# =====================================================

st.header("📊 Supply Chain Dashboard")

try:

    products, warehouses, suppliers, inventory = (
        get_dashboard_metrics()
    )

    inventory_df = get_inventory()

    enterprise_metrics = get_enterprise_metrics()

    if inventory_df is None or inventory_df.empty:

        st.warning(
            "No inventory records available."
        )

    else:

        inventory_df = inventory_df.copy()

        required_columns = [
            "product_name",
            "available_stock",
            "reorder_level",
            "location"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in inventory_df.columns
        ]

        if missing_columns:

            st.error(
                "Missing inventory columns: "
                + ", ".join(missing_columns)
            )

        else:

            inventory_df["available_stock"] = pd.to_numeric(
                inventory_df["available_stock"],
                errors="coerce"
            ).fillna(0)

            inventory_df["reorder_level"] = pd.to_numeric(
                inventory_df["reorder_level"],
                errors="coerce"
            ).fillna(0)

            inventory_df["stock_status"] = inventory_df.apply(
                lambda row: (
                    "Low Stock"
                    if row["available_stock"] <= row["reorder_level"]
                    else "Healthy"
                ),
                axis=1
            )

            low_stock = inventory_df[
                inventory_df["stock_status"] == "Low Stock"
            ]

            st.subheader("Main Business Metrics")

            c1, c2, c3, c4, c5 = st.columns(5)

            c1.metric(
                "📦 Total Products",
                safe_number(products)
            )

            c2.metric(
                "🏭 Warehouses",
                safe_number(warehouses)
            )

            c3.metric(
                "🚚 Suppliers",
                safe_number(suppliers)
            )

            c4.metric(
                "📊 Total Inventory",
                f"{safe_number(inventory):,}"
            )

            c5.metric(
                "⚠️ Low Stock Items",
                len(low_stock)
            )

            st.divider()

            st.subheader(
                "🏢 Enterprise Supply Chain Metrics"
            )

            metric_groups = [
                ("Purchase Orders", "purchase_orders"),
                ("Production Orders", "production_orders"),
                ("Demand Forecasts", "demand_forecasts"),
                ("Logistics Shipments", "logistics_shipments"),
                ("Quality Inspections", "quality_inspections"),
                ("Retail Orders", "retail_orders"),
                ("Customer Orders", "customer_orders"),
                ("Manufacturing Plants", "manufacturing_plants"),
                ("Distribution Centers", "distribution_centers")
            ]

            for start in range(0, len(metric_groups), 3):

                columns = st.columns(3)

                for column, (label, key) in zip(
                    columns,
                    metric_groups[start:start + 3]
                ):

                    column.metric(
                        label,
                        enterprise_metrics.get(key, 0)
                    )

            with st.expander(
                "View all database table counts"
            ):

                metrics_df = pd.DataFrame(
                    list(enterprise_metrics.items()),
                    columns=[
                        "Table Name",
                        "Total Records"
                    ]
                )

                show_dataframe(
                    metrics_df,
                    "No database metrics available."
                )

            st.divider()

            st.subheader("📦 Inventory Overview")

            f1, f2, f3 = st.columns(3)

            with f1:

                warehouse_options = (
                    ["All Warehouses"]
                    + sorted(
                        inventory_df["location"]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                    )
                )

                selected_warehouse = st.selectbox(
                    "Filter by Warehouse",
                    warehouse_options
                )

            with f2:

                search_product = st.text_input(
                    "🔍 Search Product",
                    placeholder="Enter product name..."
                )

            with f3:

                selected_status = st.selectbox(
                    "Filter by Stock Status",
                    [
                        "All",
                        "Low Stock",
                        "Healthy"
                    ]
                )

            filtered_df = inventory_df.copy()

            if selected_warehouse != "All Warehouses":

                filtered_df = filtered_df[
                    filtered_df["location"].astype(str)
                    == selected_warehouse
                ]

            if search_product:

                filtered_df = filtered_df[
                    filtered_df["product_name"]
                    .astype(str)
                    .str.contains(
                        search_product,
                        case=False,
                        na=False
                    )
                ]

            if selected_status != "All":

                filtered_df = filtered_df[
                    filtered_df["stock_status"]
                    == selected_status
                ]

            st.caption(
                f"Showing {len(filtered_df)} inventory records"
            )

            display_columns = [
                "product_name",
                "available_stock",
                "reorder_level",
                "location",
                "stock_status"
            ]

            show_dataframe(
                filtered_df[display_columns],
                "No inventory records match your filters."
            )

            st.divider()

            st.subheader(
                "📈 Product-wise Inventory Analytics"
            )

            if not filtered_df.empty:

                fig = px.bar(
                    filtered_df,
                    x="product_name",
                    y="available_stock",
                    color="location",
                    barmode="group",
                    title="Available Stock by Product and Warehouse"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                col1, col2 = st.columns(2)

                with col1:

                    stock_fig = px.pie(
                        filtered_df,
                        names="stock_status",
                        title="Inventory Health Distribution",
                        hole=0.4
                    )

                    st.plotly_chart(
                        stock_fig,
                        use_container_width=True
                    )

                with col2:

                    warehouse_fig = px.bar(
                        filtered_df.groupby(
                            "location",
                            as_index=False
                        )["available_stock"].sum(),
                        x="location",
                        y="available_stock",
                        title="Warehouse-wise Stock"
                    )

                    st.plotly_chart(
                        warehouse_fig,
                        use_container_width=True
                    )

            else:

                st.info(
                    "No records match your inventory filters."
                )

            st.subheader("⚠️ Low Stock Alerts")

            if not low_stock.empty:

                st.warning(
                    f"{len(low_stock)} products require restocking."
                )

                st.dataframe(
                    low_stock[display_columns],
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.success(
                    "All products have sufficient stock!"
                )

except Exception as error:

    st.error(
        f"Dashboard database error: {error}"
    )


# =====================================================
# 12. ENTERPRISE ANALYTICS
# =====================================================

st.divider()

st.header("📊 Enterprise Supply Chain Analytics")

try:

    purchase_df = load_table("purchase_orders")
    production_df = load_table("production_orders")
    forecast_df = load_table("demand_forecasts")
    shipment_df = load_table("logistics_shipments")
    quality_df = load_table("quality_inspections")

    # PURCHASE ORDER ANALYSIS

    st.subheader("🛒 Purchase Order Analysis")

    if not purchase_df.empty:

        if "status" in purchase_df.columns:

            order_status = (
                purchase_df["status"]
                .fillna("Unknown")
                .value_counts()
                .reset_index()
            )

            order_status.columns = [
                "Order Status",
                "Total Orders"
            ]

            fig = px.pie(
                order_status,
                names="Order Status",
                values="Total Orders",
                title="Purchase Orders by Status",
                hole=0.4
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        show_dataframe(
            purchase_df,
            "No purchase order records found."
        )

        add_download_button(
            purchase_df,
            "⬇️ Download Purchase Orders",
            "purchase_orders.csv",
            "download_purchase_orders"
        )

    else:

        st.info("No purchase order records available.")

    st.divider()

    # DEMAND FORECAST ANALYSIS

    st.subheader("📈 Demand Forecast vs Actual Demand")

    if not forecast_df.empty:

        required_columns = [
            "product_id",
            "predicted_demand",
            "actual_demand"
        ]

        if all(
            column in forecast_df.columns
            for column in required_columns
        ):

            forecast_df["predicted_demand"] = pd.to_numeric(
                forecast_df["predicted_demand"],
                errors="coerce"
            )

            forecast_df["actual_demand"] = pd.to_numeric(
                forecast_df["actual_demand"],
                errors="coerce"
            )

            fig = px.bar(
                forecast_df,
                x="product_id",
                y=[
                    "predicted_demand",
                    "actual_demand"
                ],
                barmode="group",
                title="Predicted Demand vs Actual Demand"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            forecast_df["forecast_difference"] = (
                forecast_df["actual_demand"]
                - forecast_df["predicted_demand"]
            )

        show_dataframe(
            forecast_df,
            "No demand forecast records found."
        )

        add_download_button(
            forecast_df,
            "⬇️ Download Demand Forecast",
            "demand_forecast.csv",
            "download_forecast"
        )

    else:

        st.info("No demand forecast records available.")

    st.divider()

    # PRODUCTION ANALYSIS

    st.subheader("🏭 Production Performance Analysis")

    if not production_df.empty:

        required_columns = [
            "product_id",
            "produced_quantity",
            "planned_quantity",
            "status"
        ]

        if all(
            column in production_df.columns
            for column in required_columns
        ):

            production_df["produced_quantity"] = pd.to_numeric(
                production_df["produced_quantity"],
                errors="coerce"
            )

            production_df["planned_quantity"] = pd.to_numeric(
                production_df["planned_quantity"],
                errors="coerce"
            )

            denominator = production_df[
                "planned_quantity"
            ].replace(0, pd.NA)

            production_df["completion_percentage"] = (
                production_df["produced_quantity"]
                / denominator
                * 100
            )

            fig = px.bar(
                production_df,
                x="product_id",
                y="completion_percentage",
                color="status",
                title="Production Completion Percentage"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        show_dataframe(
            production_df,
            "No production records found."
        )

        add_download_button(
            production_df,
            "⬇️ Download Production Report",
            "production_report.csv",
            "download_production"
        )

    else:

        st.info("No production records available.")

    st.divider()

    # LOGISTICS ANALYSIS

    st.subheader("🚚 Logistics and Shipment Tracking")

    if not shipment_df.empty:

        required_columns = [
            "expected_arrival",
            "actual_arrival",
            "shipment_status"
        ]

        missing_columns = [
            column
            for column in required_columns
            if column not in shipment_df.columns
        ]

        if missing_columns:

            st.warning(
                "Logistics columns missing: "
                + ", ".join(missing_columns)
            )

        else:

            shipment_df["expected_arrival"] = pd.to_datetime(
                shipment_df["expected_arrival"],
                errors="coerce"
            )

            shipment_df["actual_arrival"] = pd.to_datetime(
                shipment_df["actual_arrival"],
                errors="coerce"
            )

            shipment_df["shipment_status"] = (
                shipment_df["shipment_status"]
                .fillna("Unknown")
                .astype(str)
            )

            status_delayed = (
                shipment_df["shipment_status"]
                .str.contains(
                    "delayed",
                    case=False,
                    na=False
                )
            )

            date_delayed = (
                shipment_df["actual_arrival"].notna()
                & shipment_df["expected_arrival"].notna()
                & (
                    shipment_df["actual_arrival"]
                    > shipment_df["expected_arrival"]
                )
            )

            overdue_not_arrived = (
                shipment_df["actual_arrival"].isna()
                & shipment_df["expected_arrival"].notna()
                & (
                    shipment_df["expected_arrival"]
                    < pd.Timestamp.today().normalize()
                )
                & ~shipment_df["shipment_status"].str.contains(
                    "delivered|completed",
                    case=False,
                    na=False
                )
            )

            shipment_df["delivery_result"] = "On Time"

            shipment_df.loc[
                status_delayed | date_delayed | overdue_not_arrived,
                "delivery_result"
            ] = "Delayed"

            shipment_status = (
                shipment_df["shipment_status"]
                .value_counts()
                .reset_index()
            )

            shipment_status.columns = [
                "Shipment Status",
                "Total Shipments"
            ]

            fig = px.bar(
                shipment_status,
                x="Shipment Status",
                y="Total Shipments",
                color="Shipment Status",
                title="Shipment Status Overview"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            delivery_summary = (
                shipment_df["delivery_result"]
                .value_counts()
                .reset_index()
            )

            delivery_summary.columns = [
                "Delivery Result",
                "Total Shipments"
            ]

            delivery_fig = px.pie(
                delivery_summary,
                names="Delivery Result",
                values="Total Shipments",
                title="On-Time vs Delayed Shipments",
                hole=0.4
            )

            st.plotly_chart(
                delivery_fig,
                use_container_width=True
            )

            delayed_shipments = shipment_df[
                shipment_df["delivery_result"] == "Delayed"
            ]

            st.subheader("⚠️ Delayed Shipments")

            if not delayed_shipments.empty:

                st.warning(
                    f"{len(delayed_shipments)} delayed shipments found."
                )

                st.dataframe(
                    delayed_shipments,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.success("No delayed shipments found.")

            add_download_button(
                shipment_df,
                "⬇️ Download Shipment Report",
                "shipment_report.csv",
                "download_shipments"
            )

    else:

        st.info("No shipment records available.")

    st.divider()

    # QUALITY ANALYSIS

    st.subheader("🔍 Quality Inspection Analysis")

    if not quality_df.empty:

        required_columns = [
            "product_id",
            "defective_quantity",
            "inspected_quantity",
            "quality_status"
        ]

        if all(
            column in quality_df.columns
            for column in required_columns
        ):

            quality_df["defective_quantity"] = pd.to_numeric(
                quality_df["defective_quantity"],
                errors="coerce"
            )

            quality_df["inspected_quantity"] = pd.to_numeric(
                quality_df["inspected_quantity"],
                errors="coerce"
            )

            denominator = quality_df[
                "inspected_quantity"
            ].replace(0, pd.NA)

            quality_df["defect_percentage"] = (
                quality_df["defective_quantity"]
                / denominator
                * 100
            )

            fig = px.bar(
                quality_df,
                x="product_id",
                y="defect_percentage",
                color="quality_status",
                title="Product-wise Defect Percentage"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        show_dataframe(
            quality_df,
            "No quality inspection records found."
        )

        add_download_button(
            quality_df,
            "⬇️ Download Quality Report",
            "quality_report.csv",
            "download_quality"
        )

    else:

        st.info("No quality inspection records available.")

except Exception as error:

    st.error(
        f"Enterprise analytics error: {error}"
    )
# =====================================================
# 13. REPORTS AND DOWNLOADS
# =====================================================

st.divider()

st.header("📄 Reports and Downloads")

try:

    report_df = get_inventory()

    if report_df is None:
        report_df = pd.DataFrame()

    report1, report2, report3 = st.columns(3)

    with report1:

        st.subheader("📦 Inventory Summary")

        add_download_button(
            report_df,
            "Download Inventory Report",
            "inventory_summary.csv",
            "download_inventory"
        )

    with report2:

        st.subheader("⚠️ Low Stock Report")

        if (
            not report_df.empty
            and {
                "available_stock",
                "reorder_level"
            }.issubset(report_df.columns)
        ):

            low_stock_df = report_df[
                report_df["available_stock"]
                <= report_df["reorder_level"]
            ]

            add_download_button(
                low_stock_df,
                "Download Low Stock Report",
                "low_stock_report.csv",
                "download_low_stock"
            )

        else:

            st.info("Low stock information is unavailable.")

    with report3:

        st.subheader("🏭 Warehouse Report")

        required_columns = [
            "location",
            "product_name",
            "available_stock"
        ]

        if (
            not report_df.empty
            and all(
                column in report_df.columns
                for column in required_columns
            )
        ):

            warehouse_report = (
                report_df.groupby(
                    "location",
                    as_index=False
                )
                .agg(
                    total_products=(
                        "product_name",
                        "count"
                    ),
                    total_stock=(
                        "available_stock",
                        "sum"
                    )
                )
            )

            add_download_button(
                warehouse_report,
                "Download Warehouse Report",
                "warehouse_report.csv",
                "download_warehouse"
            )

        else:

            st.info("Warehouse report information is unavailable.")

except Exception as error:

    st.error(
        f"Report generation error: {error}"
    )


# =====================================================
# 14. DOCUMENT MANAGEMENT AND METADATA
# =====================================================

st.divider()
st.header("📂 Document Management")

st.write(
    "Upload supply chain documents and attach metadata "
    "to improve document retrieval."
)

st.subheader("📋 Document Metadata")

meta_col1, meta_col2, meta_col3 = st.columns(3)

with meta_col1:

    metadata_product = st.text_input(
        "Product",
        placeholder="Example: Shampoo",
        key="metadata_product"
    )

    metadata_sku = st.text_input(
        "SKU",
        placeholder="Example: SKU001",
        key="metadata_sku"
    )

    metadata_factory = st.text_input(
        "Factory",
        placeholder="Example: Factory001",
        key="metadata_factory"
    )

with meta_col2:

    metadata_warehouse = st.text_input(
        "Warehouse",
        placeholder="Example: WH001",
        key="metadata_warehouse"
    )

    metadata_supplier = st.text_input(
        "Supplier",
        placeholder="Example: Supplier001",
        key="metadata_supplier"
    )

    metadata_region = st.text_input(
        "Region",
        placeholder="Example: South India",
        key="metadata_region"
    )

with meta_col3:

    metadata_department = st.selectbox(
        "Department",
        [
            "General",
            "Inventory",
            "Procurement",
            "Manufacturing",
            "Logistics",
            "Quality",
            "Sales"
        ],
        key="metadata_department"
    )

    metadata_sop_version = st.text_input(
        "SOP Version",
        placeholder="Example: V1.0",
        key="metadata_sop_version"
    )

    metadata_effective_date = st.date_input(
        "Effective Date",
        key="metadata_effective_date"
    )


# =====================================================
# 15. DOCUMENT UPLOAD
# =====================================================

uploaded_files = st.file_uploader(
    "Upload Supply Chain Documents",
    type=["pdf", "docx", "txt", "csv", "xlsx", "xls"],
    accept_multiple_files=True,
    key="supply_chain_document_uploader"
)


# =====================================================
# 16. PROCESS DOCUMENTS WITH METADATA
# =====================================================

if st.button(
    "🚀 Process Documents",
    type="primary",
    key="process_supply_chain_documents"
):

    if not uploaded_files:

        st.warning("Please upload at least one document.")

    else:

        document_metadata = {

            "product": str(
                st.session_state.get("metadata_product", "")
            ).strip(),

            "sku": str(
                st.session_state.get("metadata_sku", "")
            ).strip(),

            "factory": str(
                st.session_state.get("metadata_factory", "")
            ).strip(),

            "warehouse": str(
                st.session_state.get("metadata_warehouse", "")
            ).strip().upper(),

            "supplier": str(
                st.session_state.get("metadata_supplier", "")
            ).strip(),

            "region": str(
                st.session_state.get("metadata_region", "")
            ).strip(),

            "department": str(
                st.session_state.get(
                    "metadata_department",
                    "General"
                )
            ).strip(),

            "sop_version": str(
                st.session_state.get("metadata_sop_version", "")
            ).strip(),

            "effective_date": st.session_state[
                "metadata_effective_date"
            ].isoformat()
        }

        if not document_metadata["warehouse"]:

            st.error(
                "Please enter the Warehouse ID, for example WH001."
            )

        elif not document_metadata["region"]:

            st.error(
                "Please enter the Region, for example South India."
            )

        else:

            st.subheader("Metadata Verification")

            st.json(document_metadata)

            successful = 0
            failed = 0

            progress = st.progress(0)

            for index, uploaded_file in enumerate(uploaded_files):

                try:

                    file_bytes = uploaded_file.getvalue()

                    hash_payload = (
                        file_bytes
                        + json.dumps(
                            document_metadata,
                            sort_keys=True
                        ).encode("utf-8")
                    )

                    file_hash = hashlib.sha256(
                        hash_payload
                    ).hexdigest()

                    if file_hash in st.session_state.processed_documents:

                        st.info(
                            f"{uploaded_file.name} with these "
                            "metadata values is already processed."
                        )

                        progress.progress(
                            (index + 1) / len(uploaded_files)
                        )

                        continue

                    safe_filename = os.path.basename(
                        uploaded_file.name
                    )

                    filename, extension = os.path.splitext(
                        safe_filename
                    )

                    stored_filename = (
                        f"{filename}_{file_hash[:10]}{extension}"
                    )

                    file_path = os.path.join(
                        UPLOAD_DIR,
                        stored_filename
                    )

                    with open(file_path, "wb") as file:

                        file.write(file_bytes)

                    with st.spinner(
                        f"Processing {uploaded_file.name}..."
                    ):

                        result = process_document(
                            file_path,
                            metadata=document_metadata.copy()
                        )

                    if result is False:

                        st.error(
                            f"Could not index {uploaded_file.name}. "
                            "Check the terminal for details."
                        )

                        failed += 1

                    else:

                        st.session_state.processed_documents.append(
                            file_hash
                        )

                        st.success(
                            f"Successfully processed: {uploaded_file.name}"
                        )

                        successful += 1

                except Exception as error:

                    st.error(
                        f"Document processing error for "
                        f"{uploaded_file.name}: {error}"
                    )

                    failed += 1

                progress.progress(
                    (index + 1) / len(uploaded_files)
                )

            st.write(
                f"Successful: {successful} | Failed: {failed}"
            )

            if successful > 0:

                st.success(
                    "Document processing completed. "
                    "Your metadata has been passed to the indexing function."
                )
# =====================================================
# 17. ADVANCED RAG CHATBOT
# =====================================================

st.divider()

st.header("🤖 Supply Chain AI Chatbot")

st.write(
    """
    Ask questions about inventory, suppliers, warehouses,
    demand forecasts, purchase orders, production and policies.
    """
)

st.caption(
    "Powered by Gemini, MySQL, ChromaDB and Advanced RAG."
)


# =====================================================
# 18. CLEAR CHAT
# =====================================================

chat_col1, chat_col2 = st.columns([5, 1])

with chat_col1:

    st.write("Your conversation")

with chat_col2:

    if st.button(
        "🗑️ Clear Chat",
        key="clear_chat_button"
    ):

        st.session_state.messages = []

        clear_memory()

        st.rerun()


# =====================================================
# 19. DISPLAY CHAT HISTORY
# =====================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            with st.expander("View Sources"):

                for source in message["sources"]:

                    st.write(
                        f"**Document:** "
                        f"{source.get('source', 'Unknown')}"
                    )

                    st.write(
                        f"**Page:** "
                        f"{source.get('page', 'Unknown')}"
                    )

                    st.write(
                        f"**Section:** "
                        f"{source.get('section', 'Unknown')}"
                    )


# =====================================================
# 20. CHAT INPUT
# =====================================================

question = st.chat_input(
    "Ask your supply chain question..."
)


# =====================================================
# 21. GENERATE CHATBOT RESPONSE
# =====================================================

if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):

        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching and generating answer..."
        ):

            try:

                answer = ask_question(question)

                if not answer:

                    answer = "No answer was generated."

                try:

                    from rag import last_sources

                    sources = list(last_sources)

                except Exception:

                    sources = []

            except Exception as error:

                answer = (
                    "Unable to generate an answer: "
                    f"{error}"
                )

                sources = []

        st.markdown(answer)

        if sources:

            with st.expander("View Sources"):

                for source in sources:

                    st.write(
                        f"**Document:** "
                        f"{source.get('source', 'Unknown')}"
                    )

                    st.write(
                        f"**Page:** "
                        f"{source.get('page', 'Unknown')}"
                    )

                    st.write(
                        f"**Section:** "
                        f"{source.get('section', 'Unknown')}"
                    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })


# =====================================================
# 22. FOOTER
# =====================================================

st.divider()

st.caption(
    "Enterprise AI Demand Planning & "
    "Supply Chain Intelligence Assistant"
)    