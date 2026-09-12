# Enterprise semantic measures

```DAX
Revenue = SUM(FactKPI[Revenue])

Profit = SUM(FactKPI[Profit])

Profit Margin = DIVIDE([Profit], [Revenue])

Orders = SUM(FactKPI[Orders])

Revenue per Order = DIVIDE([Revenue], [Orders])

Target Revenue = SUM(KPITargets[RevenueTarget])

Revenue Attainment = DIVIDE([Revenue], [Target Revenue])
```

Keep KPI calculations centralized and documented rather than rebuilding them independently in every report.
