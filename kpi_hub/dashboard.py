"""Builds a self-contained HTML executive KPI dashboard (no server or BI licence needed)."""
from collections import defaultdict
from html import escape
from pathlib import Path


def _money(v: float) -> str:
    return f"${v / 1e6:.2f}M" if v >= 1e6 else f"${v / 1e3:.0f}K"


def _bar_chart(months: list[str], actual: dict, target: dict) -> str:
    w, h, pad = 640, 240, 40
    top = max(max(actual.values()), max(target.values())) * 1.1
    bw = (w - 2 * pad) / len(months)
    parts = []
    for i, m in enumerate(months):
        x = pad + i * bw
        ah = (h - 2 * pad) * actual[m] / top
        ty = h - pad - (h - 2 * pad) * target[m] / top
        color = "#1a7f4b" if actual[m] >= target[m] else "#c0392b"
        parts.append(f'<rect x="{x + bw * 0.2:.0f}" y="{h - pad - ah:.0f}" width="{bw * 0.6:.0f}" '
                     f'height="{ah:.0f}" fill="{color}" rx="3"><title>{m}: {_money(actual[m])} '
                     f'vs target {_money(target[m])}</title></rect>')
        parts.append(f'<line x1="{x + bw * 0.1:.0f}" x2="{x + bw * 0.9:.0f}" y1="{ty:.0f}" y2="{ty:.0f}" '
                     'stroke="#222" stroke-width="2" stroke-dasharray="4 3"/>')
        parts.append(f'<text x="{x + bw / 2:.0f}" y="{h - pad + 18}" text-anchor="middle">{m}</text>')
        parts.append(f'<text x="{x + bw / 2:.0f}" y="{min(h - pad - ah, ty) - 8:.0f}" text-anchor="middle">'
                     f'{_money(actual[m])}</text>')
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Monthly revenue vs target">'
            + "".join(parts) + "</svg>")


def write_dashboard(facts: list[dict], log: dict, path: Path) -> None:
    rev = sum(f["Revenue"] for f in facts)
    profit = sum(f["Profit"] for f in facts)
    target = sum(f["RevenueTarget"] or 0 for f in facts)
    months = sorted({f["Month"] for f in facts})
    m_act, m_tgt = defaultdict(float), defaultdict(float)
    reg = defaultdict(lambda: [0.0, 0.0, 0.0])
    for f in facts:
        m_act[f["Month"]] += f["Revenue"]
        m_tgt[f["Month"]] += f["RevenueTarget"] or 0
        r = reg[f["Region"]]
        r[0] += f["Revenue"]; r[1] += f["Profit"]; r[2] += f["RevenueTarget"] or 0

    region_rows = "".join(
        f"<tr><td>{escape(k)}</td><td>{_money(v[0])}</td><td>{v[1] / v[0]:.1%}</td>"
        f"<td class='{'good' if v[0] >= v[2] else 'bad'}'>{v[0] / v[2]:.1%}</td></tr>"
        for k, v in sorted(reg.items(), key=lambda kv: -kv[1][0]))
    check_rows = "".join(
        f"<tr><td>{escape(c['check'])}</td><td>{c['severity']}</td><td>{c['failed_rows']}</td>"
        f"<td class='{'good' if c['passed'] else ('bad' if c['severity'] == 'BLOCKING' else 'warn')}'>"
        f"{'PASS' if c['passed'] else 'FLAGGED'}</td></tr>" for c in log["quality_checks"])

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Executive KPI Dashboard</title>
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f4f6f8;color:#1d2733}}
main{{max-width:980px;margin:auto;padding:24px}} h1{{margin:0 0 4px}} .sub{{color:#5b6b7b;margin:0 0 20px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-bottom:20px}}
.card,.panel{{background:#fff;border-radius:10px;padding:16px;box-shadow:0 1px 3px #0001}}
.card b{{display:block;font-size:1.6rem;margin-top:4px}} .card span{{color:#5b6b7b;font-size:.85rem}}
.panel{{margin-bottom:20px;overflow-x:auto}} svg{{width:100%;height:auto;font-size:11px;fill:#1d2733}}
table{{border-collapse:collapse;width:100%}} td,th{{text-align:left;padding:6px 8px;border-bottom:1px solid #e3e8ee}}
.good{{color:#1a7f4b;font-weight:600}} .bad{{color:#c0392b;font-weight:600}} .warn{{color:#b9770e;font-weight:600}}
</style></head><body><main>
<h1>Executive KPI Dashboard</h1>
<p class="sub">H1 2026 · refreshed {log['refreshed_at']} · {log['staged_rows']:,} validated records ·
all figures from the governed semantic layer</p>
<div class="cards">
<div class="card"><span>Revenue</span><b>{_money(rev)}</b></div>
<div class="card"><span>Profit</span><b>{_money(profit)}</b></div>
<div class="card"><span>Profit margin</span><b>{profit / rev:.1%}</b></div>
<div class="card"><span>Revenue attainment</span><b class="{'good' if rev >= target else 'bad'}">{rev / target:.1%}</b></div>
</div>
<div class="panel"><h2>Monthly revenue vs target</h2>{_bar_chart(months, m_act, m_tgt)}
<p class="sub">Bars: actual revenue (green = at or above target) · dashed line: target</p></div>
<div class="panel"><h2>By region</h2><table><tr><th>Region</th><th>Revenue</th><th>Margin</th><th>Attainment</th></tr>
{region_rows}</table></div>
<div class="panel"><h2>Data quality for this refresh</h2><table>
<tr><th>Check</th><th>Severity</th><th>Rows</th><th>Result</th></tr>{check_rows}</table>
<p class="sub">{log['rejected_rows']} invalid rows quarantined · reconciliation: published revenue matches staged source
{'✓' if log['reconciliation']['passed'] else '✗'}</p></div>
</main></body></html>"""
    path.write_text(html, encoding="utf-8")
