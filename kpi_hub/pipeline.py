"""KPI refresh pipeline: load → stage → quality gate → semantic layer → reconcile → publish.

Usage: python -m kpi_hub.pipeline
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import duckdb

from kpi_hub.dashboard import write_dashboard

ROOT = Path(__file__).resolve().parents[1]
SQL = ROOT / "sql"
DATA = ROOT / "data"
OUTPUT = ROOT / "output"


class QualityGateError(RuntimeError):
    pass


def connect(data_dir: Path = DATA) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute(f"CREATE TABLE raw_sales_ops AS SELECT * FROM read_csv('{data_dir / 'sales_ops.csv'}', "
                "header=true, types={'OrderDate': 'DATE', 'Revenue': 'DOUBLE', 'Profit': 'DOUBLE', 'Orders': 'INTEGER'})")
    con.execute(f"CREATE TABLE kpi_targets AS SELECT * FROM read_csv('{data_dir / 'kpi_targets.csv'}', "
                "header=true, types={'Month': 'VARCHAR'})")
    con.execute(f"CREATE TABLE user_region AS SELECT * FROM read_csv('{data_dir / 'user_region.csv'}', header=true)")
    return con


def quality_checks(con) -> list[dict]:
    rows = con.execute((SQL / "02_quality_checks.sql").read_text()).fetchall()
    return [{"check": c, "severity": s, "failed_rows": int(n),
             "passed": n == 0} for c, s, n in rows]


def reconcile(con) -> dict:
    """The published KPI total must equal the staged source total, to the cent."""
    staged = con.execute("SELECT ROUND(SUM(Revenue), 2) FROM stg_sales_ops").fetchone()[0]
    published = con.execute("SELECT ROUND(SUM(Revenue), 2) FROM fact_kpi_monthly").fetchone()[0]
    return {"staged_revenue": staged, "published_revenue": published,
            "passed": abs(staged - published) < 0.05}


def kpis_for_user(con, email: str) -> list[dict]:
    cur = con.execute((SQL / "04_row_level_security.sql").read_text(), [email])
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def run(data_dir: Path = DATA, output_dir: Path = OUTPUT) -> dict:
    start = time.perf_counter()
    con = connect(data_dir)
    raw_rows = con.execute("SELECT COUNT(*) FROM raw_sales_ops").fetchone()[0]

    con.execute((SQL / "01_staging.sql").read_text())
    checks = quality_checks(con)
    blocking = [c for c in checks if c["severity"] == "BLOCKING" and not c["passed"]]
    if blocking:
        raise QualityGateError(f"refresh stopped, blocking checks failed: {blocking}")

    con.execute((SQL / "03_semantic_metrics.sql").read_text())
    rec = reconcile(con)
    if not rec["passed"]:
        raise QualityGateError(f"reconciliation failed: {rec}")

    output_dir.mkdir(parents=True, exist_ok=True)
    con.execute(f"COPY fact_kpi_monthly TO '{output_dir / 'fact_kpi_monthly.csv'}' (HEADER)")
    cur = con.execute("SELECT * FROM fact_kpi_monthly ORDER BY Month, Region, Department")
    cols = [d[0] for d in cur.description]
    facts = [dict(zip(cols, r)) for r in cur.fetchall()]

    log = {
        "refreshed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "raw_rows": raw_rows,
        "staged_rows": con.execute("SELECT COUNT(*) FROM stg_sales_ops").fetchone()[0],
        "rejected_rows": con.execute("SELECT COUNT(*) FROM stg_rejected").fetchone()[0],
        "kpi_rows": len(facts),
        "quality_checks": checks,
        "reconciliation": rec,
        "duration_s": round(time.perf_counter() - start, 3),
    }
    write_dashboard(facts, log, output_dir / "kpi_dashboard.html")
    (output_dir / "refresh_log.json").write_text(json.dumps(log, indent=2, default=str))
    return log


if __name__ == "__main__":
    try:
        result = run()
    except QualityGateError as e:
        sys.exit(f"FAILED: {e}")
    print(f"Refresh OK in {result['duration_s']}s: {result['raw_rows']:,} raw rows → "
          f"{result['staged_rows']:,} staged ({result['rejected_rows']} rejected, "
          f"{result['raw_rows'] - result['staged_rows'] - result['rejected_rows']} duplicates removed) → "
          f"{result['kpi_rows']} KPI rows")
    for c in result["quality_checks"]:
        print(f"  [{'PASS' if c['passed'] else c['severity']:>8}] {c['check']}: {c['failed_rows']}")
    print(f"  Reconciliation: published ${result['reconciliation']['published_revenue']:,.2f} "
          f"= staged ${result['reconciliation']['staged_revenue']:,.2f}")
    print("Dashboard: output/kpi_dashboard.html")
