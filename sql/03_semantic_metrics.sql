-- Canonical KPI source
SELECT
    OrderDate,
    Region,
    Department,
    SUM(Revenue) AS Revenue,
    SUM(Profit) AS Profit,
    SUM(Orders) AS Orders,
    SUM(Profit) / NULLIF(SUM(Revenue),0) AS ProfitMargin
FROM sales_ops
GROUP BY OrderDate, Region, Department;
