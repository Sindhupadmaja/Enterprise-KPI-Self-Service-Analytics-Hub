-- KPI quality checks
SELECT COUNT(*) AS MissingDates FROM sales_ops WHERE OrderDate IS NULL;
SELECT COUNT(*) AS InvalidRevenue FROM sales_ops WHERE Revenue < 0;
SELECT Region, COUNT(*) AS RowsPerRegion
FROM sales_ops
GROUP BY Region;

-- Duplicate grain check: one row per Date + Region + Department
SELECT OrderDate, Region, Department, COUNT(*) AS DuplicateRows
FROM sales_ops
GROUP BY OrderDate, Region, Department
HAVING COUNT(*) > 1;
