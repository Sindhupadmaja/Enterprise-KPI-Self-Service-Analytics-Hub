"""Generate six months of sales operations data from two source systems, plus targets.

About 1% of rows are deliberately bad (missing dates, negative revenue, duplicates)
so the quality checks have real problems to catch. Seeded, so output is reproducible.
Usage: python scripts/generate_data.py
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(7)
DATA = Path(__file__).resolve().parents[1] / "data"
REGIONS = {"West": 1.3, "East": 1.0, "North": 0.9, "South": 0.8}
DEPARTMENTS = {"Retail": 1.0, "Commercial": 1.6, "Wealth": 0.7}
SOURCES = {"Retail": "POS", "Commercial": "ERP", "Wealth": "ERP"}
START, DAYS = date(2026, 1, 1), 181  # Jan 1 - Jun 30, 2026

rows = []
for d in range(DAYS):
    day = START + timedelta(days=d)
    season = 1 + 0.15 * (day.month - 1) / 5  # gentle growth over the half-year
    for region, rf in REGIONS.items():
        for dept, df in DEPARTMENTS.items():
            revenue = round(random.gauss(1000, 180) * rf * df * season, 2)
            margin = random.uniform(0.12, 0.32)
            orders = max(1, int(random.gauss(8, 2) * df))
            rows.append([day.isoformat(), region, dept, revenue,
                         round(revenue * margin, 2), orders, SOURCES[dept]])

# Inject realistic data problems.
bad = random.sample(range(len(rows)), 40)
for i in bad[:10]:
    rows[i][0] = ""                          # missing date
for i in bad[10:20]:
    rows[i][3] = -abs(rows[i][3])            # negative revenue
for i in bad[20:40]:
    rows.append(list(rows[i]))               # duplicate record at the same grain
random.shuffle(rows)

with open(DATA / "sales_ops.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["OrderDate", "Region", "Department", "Revenue", "Profit", "Orders", "DataSource"])
    w.writerows(rows)

with open(DATA / "kpi_targets.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Month", "Region", "Department", "RevenueTarget"])
    for m in range(1, 7):
        for region, rf in REGIONS.items():
            for dept, df in DEPARTMENTS.items():
                w.writerow([f"2026-{m:02d}", region, dept, round(29_000 * rf * df * (1 + 0.03 * m), -2)])

with open(DATA / "user_region.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["UserEmail", "Region"])
    w.writerows([["west.manager@example.com", "West"], ["east.manager@example.com", "East"],
                 ["north.manager@example.com", "North"], ["south.manager@example.com", "South"],
                 ["cfo@example.com", "West"], ["cfo@example.com", "East"],
                 ["cfo@example.com", "North"], ["cfo@example.com", "South"]])
print(f"Wrote {len(rows):,} sales rows, 72 targets, 8 access rules to data/")
