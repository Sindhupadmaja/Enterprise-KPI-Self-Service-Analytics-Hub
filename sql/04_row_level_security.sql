-- Row-level security: a user sees only the regions mapped to them in user_region.
-- The pipeline passes the user's email as the ? parameter. Unknown users see nothing.
SELECT k.*
FROM fact_kpi_monthly k
JOIN user_region u ON u.Region = k.Region
WHERE u.UserEmail = ?
ORDER BY k.Month, k.Region, k.Department;
