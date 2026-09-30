# Refresh and deployment

## Automated refresh
`.github/workflows/kpi-refresh.yml` runs every weekday at 11:00 UTC, on every push, and on demand (Actions tab → KPI refresh → Run workflow). Each run publishes the dashboard, the KPI extract and the refresh log as a downloadable artifact.

## Refresh steps (`kpi_hub/pipeline.py`)
1. Load source files (sales operations, targets, access mapping)
2. Stage: standardize types, quarantine invalid rows, remove duplicates
3. Quality gate: any failed BLOCKING check stops the refresh before anything is published
4. Build the semantic KPI layer
5. Reconcile: published revenue must equal staged revenue
6. Publish dashboard, `fact_kpi_monthly.csv` and `refresh_log.json`

## Deployment thinking
Use separate Development, Test and Production environments where the platform supports them. Maintain versioned KPI definitions and a change log; a definition change should go through a pull request so the tests run before it is merged.
