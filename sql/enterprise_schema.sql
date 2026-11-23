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


USE supply_chain_db;

-- Manufacturing Plants
INSERT INTO manufacturing_plants
(plant_name, location, capacity)
VALUES
('Bangalore Manufacturing Plant', 'Bangalore', 10000),
('Mysore Manufacturing Plant', 'Mysore', 8000);

-- Distribution Centers
INSERT INTO distribution_centers
(dc_name, location)
VALUES
('Bangalore Distribution Center', 'Bangalore'),
('Chennai Distribution Center', 'Chennai');

-- Purchase Orders
INSERT INTO purchase_orders
(supplier_id, product_id, order_quantity, order_date,
 expected_delivery, actual_delivery, status)
VALUES
(1, 1, 1000, '2026-11-01', '2026-11-10', '2026-11-09', 'Delivered'),
(2, 2, 800, '2026-11-05', '2026-11-15', NULL, 'Pending'),
(3, 3, 1200, '2026-11-08', '2026-11-18', NULL, 'Delayed'),
(1, 4, 600, '2026-11-10', '2026-11-20', '2026-11-19', 'Delivered'),
(2, 5, 900, '2026-11-12', '2026-11-25', NULL, 'In Transit');

-- Production Orders
INSERT INTO production_orders
(product_id, plant_id, planned_quantity, produced_quantity,
 start_date, completion_date, status)
VALUES
(1, 1, 1000, 1000, '2026-11-01', '2026-11-05', 'Completed'),
(2, 2, 800, 600, '2026-11-05', NULL, 'In Progress'),
(3, 1, 1200, 900, '2026-11-08', NULL, 'In Progress'),
(4, 2, 600, 600, '2026-11-10', '2026-11-15', 'Completed'),
(5, 1, 900, 400, '2026-11-12', NULL, 'In Progress');

-- Demand Forecasts
INSERT INTO demand_forecasts
(product_id, forecast_date, predicted_demand, actual_demand)
VALUES
(1, '2026-11-22', 950, 900),
(2, '2026-11-22', 750, 800),
(3, '2026-11-22', 1100, 1200),
(4, '2026-11-22', 650, 600),
(5, '2026-11-22', 850, 900);

-- Logistics Shipments
INSERT INTO logistics_shipments
(po_id, source_location, destination_location, shipment_date,
 expected_arrival, actual_arrival, shipment_status)
VALUES
(1, 'Bangalore', 'Mysore', '2026-11-05', '2026-11-09', '2026-11-09', 'Delivered'),
(2, 'Chennai', 'Bangalore', '2026-11-10', '2026-11-15', NULL, 'In Transit'),
(3, 'Mysore', 'Chennai', '2026-11-12', '2026-11-18', NULL, 'Delayed'),
(4, 'Bangalore', 'Chennai', '2026-11-15', '2026-11-20', '2026-11-19', 'Delivered'),
(5, 'Chennai', 'Mysore', '2026-11-18', '2026-11-25', NULL, 'In Transit');

-- Quality Inspections
INSERT INTO quality_inspections
(product_id, inspection_date, inspected_quantity,
 defective_quantity, quality_status)
VALUES
(1, '2026-11-10', 1000, 10, 'Passed'),
(2, '2026-11-12', 800, 25, 'Passed'),
(3, '2026-11-15', 1200, 80, 'Failed'),
(4, '2026-11-17', 600, 5, 'Passed'),
(5, '2026-11-19', 900, 30, 'Under Review');

-- Retail Orders
INSERT INTO retail_orders
(retailer_name, product_id, quantity, order_date, delivery_status)
VALUES
('Big Basket', 1, 200, '2026-11-15', 'Delivered'),
('Reliance Retail', 2, 150, '2026-11-16', 'Pending'),
('DMart', 3, 300, '2026-11-17', 'In Transit'),
('More Supermarket', 4, 100, '2026-11-18', 'Delivered'),
('Big Basket', 5, 250, '2026-11-19', 'Pending');

-- Customer Orders
INSERT INTO customer_orders
(customer_name, product_id, quantity, order_date, order_status)
VALUES
('Customer A', 1, 2, '2026-11-18', 'Completed'),
('Customer B', 2, 3, '2026-11-19', 'Processing'),
('Customer C', 3, 1, '2026-11-20', 'Pending'),
('Customer D', 4, 4, '2026-11-21', 'Completed'),
('Customer E', 5, 2, '2026-11-22', 'Processing');

USE supply_chain_db;

SELECT 'customer_orders' AS table_name, COUNT(*) AS total_rows FROM customer_orders
UNION ALL
SELECT 'demand_forecasts', COUNT(*) FROM demand_forecasts
UNION ALL
SELECT 'purchase_orders', COUNT(*) FROM purchase_orders
UNION ALL
SELECT 'production_orders', COUNT(*) FROM production_orders
UNION ALL
SELECT 'logistics_shipments', COUNT(*) FROM logistics_shipments
UNION ALL
SELECT 'quality_inspections', COUNT(*) FROM quality_inspections
UNION ALL
SELECT 'retail_orders', COUNT(*) FROM retail_orders;

USE supply_chain_db;

DESCRIBE logistics_shipments;

SHOW COLUMNS FROM logistics_shipments;

USE supply_chain_db;

SELECT
    shipment_id,
    source_location,
    destination_location,
    shipment_date,
    expected_arrival,
    actual_arrival,
    shipment_status
FROM logistics_shipments;

USE supply_chain_db;

DESCRIBE purchase_orders;

DESCRIBE suppliers;

SELECT *
FROM purchase_orders
LIMIT 5;

SELECT
    supplier_id,
    COUNT(po_id) AS total_purchase_orders
FROM purchase_orders
GROUP BY supplier_id
ORDER BY total_purchase_orders DESC;

DESCRIBE suppliers;

USE supply_chain_db;

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
    total_purchase_orders DESC;