-- Semantic layer: the single approved definition of every KPI (see governance/kpi_catalog.md).
CREATE OR REPLACE TABLE fact_kpi_monthly AS
SELECT
    strftime(s.OrderDate, '%Y-%m')                        AS Month,
    s.Region,
    s.Department,
    ROUND(SUM(s.Revenue), 2)                              AS Revenue,
    ROUND(SUM(s.Profit), 2)                               AS Profit,
    SUM(s.Orders)                                         AS Orders,
    ROUND(SUM(s.Profit) / NULLIF(SUM(s.Revenue), 0), 4)   AS ProfitMargin,
    ROUND(SUM(s.Revenue) / NULLIF(SUM(s.Orders), 0), 2)   AS RevenuePerOrder,
    MAX(t.RevenueTarget)                                  AS RevenueTarget,
    ROUND(SUM(s.Revenue) / NULLIF(MAX(t.RevenueTarget), 0), 4) AS RevenueAttainment
FROM stg_sales_ops s
LEFT JOIN kpi_targets t
       ON t.Month = strftime(s.OrderDate, '%Y-%m')
      AND t.Region = s.Region AND t.Department = s.Department
GROUP BY ALL;
