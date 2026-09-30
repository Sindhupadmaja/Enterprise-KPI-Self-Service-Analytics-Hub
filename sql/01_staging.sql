-- Staging: standardize types, drop invalid rows, and remove duplicates at the model grain.
-- Rejected rows are kept in stg_rejected so nothing disappears silently.
CREATE OR REPLACE TABLE stg_rejected AS
SELECT *,
       CASE WHEN OrderDate IS NULL THEN 'missing OrderDate'
            WHEN Revenue < 0      THEN 'negative Revenue'
            ELSE 'negative Orders' END AS Reason
FROM raw_sales_ops
WHERE OrderDate IS NULL OR Revenue < 0 OR Orders < 0;

CREATE OR REPLACE TABLE stg_sales_ops AS
SELECT DISTINCT
    CAST(OrderDate AS DATE)      AS OrderDate,
    TRIM(Region)                 AS Region,
    TRIM(Department)             AS Department,
    CAST(Revenue AS DOUBLE)      AS Revenue,
    CAST(Profit AS DOUBLE)       AS Profit,
    CAST(Orders AS INTEGER)      AS Orders,
    DataSource
FROM raw_sales_ops
WHERE OrderDate IS NOT NULL
  AND Revenue >= 0
  AND Orders >= 0;
