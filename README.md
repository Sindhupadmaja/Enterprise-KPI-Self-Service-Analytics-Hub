# Project 4 — Enterprise KPI & Self-Service Analytics Hub

## Business problem
Different teams often report the same KPI using different definitions. Leaders need trusted metrics, secure access, data-quality controls, and self-service analytics.

## Objective
Design a production-minded analytics hub that standardizes KPI definitions and enables governed self-service reporting.

## Architecture
Sources → ingestion → staging → data-quality checks → dimensional model → semantic/KPI layer → security → dashboards

## Governance goals
- One definition per enterprise KPI
- Reusable semantic measures
- Documented data owners
- Row-level security
- Data-quality monitoring
- Refresh and deployment readiness
- Self-service datasets with guardrails

## KPI catalog
See `governance/kpi_catalog.md`.

## Security
See `governance/row_level_security.md`.


