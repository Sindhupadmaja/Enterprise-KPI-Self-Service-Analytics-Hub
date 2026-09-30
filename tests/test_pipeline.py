import csv
import shutil
from pathlib import Path

import pytest

from kpi_hub.pipeline import DATA, QualityGateError, connect, kpis_for_user, run, SQL


@pytest.fixture
def result(tmp_path):
    return run(output_dir=tmp_path)


def test_refresh_publishes_dashboard_and_log(result, tmp_path):
    assert (tmp_path / "kpi_dashboard.html").exists()
    assert (tmp_path / "fact_kpi_monthly.csv").exists()
    assert (tmp_path / "refresh_log.json").exists()
    assert result["kpi_rows"] == 72  # 6 months x 4 regions x 3 departments


def test_bad_rows_are_quarantined_and_duplicates_removed(result):
    assert result["rejected_rows"] == 20
    assert result["raw_rows"] - result["rejected_rows"] - result["staged_rows"] == 20


def test_all_blocking_checks_pass_after_staging(result):
    blocking = [c for c in result["quality_checks"] if c["severity"] == "BLOCKING"]
    assert blocking and all(c["passed"] for c in blocking)


def test_raw_problems_are_reported(result):
    flagged = {c["check"]: c["failed_rows"] for c in result["quality_checks"] if not c["passed"]}
    assert flagged == {"raw: missing OrderDate": 10, "raw: negative Revenue": 10, "raw: duplicate rows": 20}


def test_published_revenue_reconciles_to_source(result):
    assert result["reconciliation"]["passed"]


def test_gate_stops_refresh_on_blocking_failure(tmp_path):
    data = tmp_path / "data"
    shutil.copytree(DATA, data)
    with open(data / "sales_ops.csv", "a", newline="") as f:
        csv.writer(f).writerow(["2026-01-01", "West", "Retail", 100, 500, 1, "POS"])  # profit > revenue
    with pytest.raises(QualityGateError, match="profit exceeds revenue"):
        run(data_dir=data, output_dir=tmp_path / "out")
    assert not (tmp_path / "out" / "kpi_dashboard.html").exists()  # nothing published


def _semantic():
    con = connect()
    con.execute((SQL / "01_staging.sql").read_text())
    con.execute((SQL / "03_semantic_metrics.sql").read_text())
    return con


def test_row_level_security_limits_regions():
    con = _semantic()
    assert {r["Region"] for r in kpis_for_user(con, "west.manager@example.com")} == {"West"}
    assert {r["Region"] for r in kpis_for_user(con, "cfo@example.com")} == {"West", "East", "North", "South"}
    assert kpis_for_user(con, "stranger@example.com") == []


def test_kpi_formulas_match_catalog_definitions():
    con = _semantic()
    for r in kpis_for_user(con, "cfo@example.com"):
        assert r["ProfitMargin"] == pytest.approx(r["Profit"] / r["Revenue"], abs=1e-4)
        assert r["RevenueAttainment"] == pytest.approx(r["Revenue"] / r["RevenueTarget"], abs=1e-4)
