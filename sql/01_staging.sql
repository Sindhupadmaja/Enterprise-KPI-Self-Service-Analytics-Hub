-- Standardize fields before the semantic layer.
CREATE VIEW stg_sales_ops AS
SELECT
    CAST(OrderDate AS DATE) AS OrderDate,
    Region,
    Department,
    Revenue,
    Profit,
    Orders,
    DataSource
FROM sales_ops
WHERE Revenue >= 0
  AND Orders >= 0;
