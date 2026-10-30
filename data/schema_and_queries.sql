-- LogiPulse relational schema reference (SQLite-compatible)
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id TEXT PRIMARY KEY, order_id TEXT, warehouse_id TEXT, customer_id TEXT,
    carrier_id TEXT, vehicle_id TEXT, route_id TEXT, origin TEXT, destination TEXT,
    distance_km REAL, shipping_date TEXT, expected_delivery TEXT, actual_delivery TEXT,
    shipping_mode TEXT, weight_kg REAL, weather TEXT, traffic_level TEXT,
    shipping_cost REAL, delivery_status TEXT
);

-- Example analytical queries
-- 1. Monthly shipment count
SELECT substr(shipping_date, 1, 7) AS month, COUNT(*) AS shipments
FROM shipments GROUP BY month ORDER BY month;

-- 2. Cost by transport mode
SELECT shipping_mode, SUM(shipping_cost) AS total_cost,
       AVG(shipping_cost) AS avg_cost
FROM shipments GROUP BY shipping_mode ORDER BY total_cost DESC;

-- 3. Late-delivery rate by origin-destination lane
SELECT origin, destination,
       COUNT(*) AS shipment_count,
       100.0 * SUM(CASE WHEN delivery_status = 'Delivered Late' THEN 1 ELSE 0 END)
       / COUNT(*) AS late_rate_pct
FROM shipments GROUP BY origin, destination
HAVING COUNT(*) >= 10 ORDER BY late_rate_pct DESC;
