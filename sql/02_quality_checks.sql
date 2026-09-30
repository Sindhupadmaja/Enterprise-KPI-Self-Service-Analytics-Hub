-- Data-quality gate. BLOCKING checks must return 0 failed rows or the refresh stops
-- before any KPI is published. WARNING checks are reported but do not stop the refresh.
SELECT 'raw: missing OrderDate' AS check_name, 'WARNING' AS severity,
       COUNT(*) AS failed_rows FROM raw_sales_ops WHERE OrderDate IS NULL
UNION ALL
SELECT 'raw: negative Revenue', 'WARNING', COUNT(*) FROM raw_sales_ops WHERE Revenue < 0
UNION ALL
SELECT 'raw: duplicate rows', 'WARNING', COUNT(*) - (SELECT COUNT(*) FROM (SELECT DISTINCT * FROM raw_sales_ops))
FROM raw_sales_ops
UNION ALL
SELECT 'staging: null keys', 'BLOCKING', COUNT(*) FROM stg_sales_ops
WHERE OrderDate IS NULL OR Region IS NULL OR Department IS NULL
UNION ALL
SELECT 'staging: negative Revenue', 'BLOCKING', COUNT(*) FROM stg_sales_ops WHERE Revenue < 0
UNION ALL
SELECT 'staging: duplicate grain (Date+Region+Department)', 'BLOCKING', COUNT(*) FROM (
    SELECT OrderDate, Region, Department FROM stg_sales_ops
    GROUP BY ALL HAVING COUNT(*) > 1)
UNION ALL
SELECT 'staging: profit exceeds revenue', 'BLOCKING', COUNT(*) FROM stg_sales_ops WHERE Profit > Revenue
UNION ALL
SELECT 'targets: region-month without a target', 'WARNING', COUNT(*) FROM (
    SELECT DISTINCT strftime(OrderDate, '%Y-%m') AS Month, Region, Department FROM stg_sales_ops) s
    ANTI JOIN kpi_targets t USING (Month, Region, Department);
