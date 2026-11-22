USE supply_chain_db;

-- Manufacturing Plants
CREATE TABLE IF NOT EXISTS manufacturing_plants (
    plant_id INT AUTO_INCREMENT PRIMARY KEY,
    plant_name VARCHAR(150) NOT NULL,
    location VARCHAR(150),
    capacity INT
);

-- Distribution Centers
CREATE TABLE IF NOT EXISTS distribution_centers (
    dc_id INT AUTO_INCREMENT PRIMARY KEY,
    dc_name VARCHAR(150) NOT NULL,
    location VARCHAR(150)
);

-- Purchase Orders
CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT,
    product_id INT,
    order_quantity INT,
    order_date DATE,
    expected_delivery DATE,
    actual_delivery DATE,
    status VARCHAR(50)
);

-- Production Orders
CREATE TABLE IF NOT EXISTS production_orders (
    production_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    plant_id INT,
    planned_quantity INT,
    produced_quantity INT,
    start_date DATE,
    completion_date DATE,
    status VARCHAR(50)
);

-- Demand Forecasts
CREATE TABLE IF NOT EXISTS demand_forecasts (
    forecast_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    forecast_date DATE,
    predicted_demand INT,
    actual_demand INT
);

-- Logistics Shipments
CREATE TABLE IF NOT EXISTS logistics_shipments (
    shipment_id INT AUTO_INCREMENT PRIMARY KEY,
    po_id INT,
    source_location VARCHAR(150),
    destination_location VARCHAR(150),
    shipment_date DATE,
    expected_arrival DATE,
    actual_arrival DATE,
    shipment_status VARCHAR(50)
);

-- Quality Inspections
CREATE TABLE IF NOT EXISTS quality_inspections (
    inspection_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    inspection_date DATE,
    inspected_quantity INT,
    defective_quantity INT,
    quality_status VARCHAR(50)
);

-- Retail Orders
CREATE TABLE IF NOT EXISTS retail_orders (
    retail_order_id INT AUTO_INCREMENT PRIMARY KEY,
    retailer_name VARCHAR(150),
    product_id INT,
    quantity INT,
    order_date DATE,
    delivery_status VARCHAR(50)
);

-- Customer Orders
CREATE TABLE IF NOT EXISTS customer_orders (
    customer_order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(150),
    product_id INT,
    quantity INT,
    order_date DATE,
    order_status VARCHAR(50)
);

USE supply_chain_db;

SHOW TABLES;


USE supply_chain_db;

SELECT product_id, product_name FROM products;

SELECT supplier_id, supplier_name FROM suppliers;