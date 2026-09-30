# KPI Catalog

| KPI | Definition | Owner | Grain |
|---|---|---|---|
| Revenue | Sum of recognized sales revenue | Finance | Date/Region/Department |
| Profit | Revenue minus recognized cost | Finance | Date/Region/Department |
| Profit Margin | Profit divided by Revenue | Finance | Date/Region/Department |
| Orders | Sum of valid orders | Sales Ops | Date/Region/Department |
| Revenue per Order | Revenue divided by Orders | Business Analytics | Month/Region/Department |
| Revenue Attainment | Actual revenue / target revenue | Business Analytics | Month/Region/Department |

## Governance rule
A KPI should have one approved definition, a named owner, source lineage, refresh expectation, and validation rule.

Implemented in `sql/03_semantic_metrics.sql`; `tests/test_pipeline.py` checks the formulas match these definitions.
