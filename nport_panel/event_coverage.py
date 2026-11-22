"""
event_coverage.py: how many retirement events have enough N-PORT reports around them
for the lame-duck design. COUNTS ONLY: no outcome (turnover, risk, returns) is read
or summarised by event time, so the pre-registration stays blind to results.

Events: retirement announcements linked to fund series (results/stage2_events.csv),
stated retirement dates (results/scoping_retirement_dates.csv). Panel: reports with
a turnover value (nport_panel_data/tau.parquet; only the existence of a row is used).
Equity fund: at least 20 stocks and equity value at least 80% of net assets in the
last report before the announcement.

Windows (report dates): pre = before the announcement month; lame duck = from the
announcement month to the stated retirement date; post = after the retirement date.
Run from the repo root: python nport_panel/event_coverage.py
Also a power check from whole-panel variance (not event-aligned).
Output: results/nport_event_coverage.json. Deterministic.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "nport_panel_data"
ev = pd.read_csv(ROOT / "results" / "stage2_events.csv", dtype=str)
ev = ev[ev.kind == "retirement"]
dates = pd.read_csv(ROOT / "results" / "scoping_retirement_dates.csv", dtype=str)
ev = ev.merge(dates[["adsh", "stated", "precision"]], on="adsh", how="left")
ev["ann"] = pd.to_datetime(ev.month + "-01")
ev["stated"] = pd.to_datetime(ev.stated, errors="coerce")
rows = pd.read_parquet(D / "tau.parquet", columns=["series_id", "report_date", "n_stocks"])
rep = pd.read_parquet(D / "reports.parquet", columns=["series_id", "report_date", "net_assets", "eq_value_usd", "n_stocks"])

out_rows = []
for e in ev.itertuples():
    r = rows[rows.series_id == e.series_id]
    pre = r[r.report_date < e.ann]
    last = rep[(rep.series_id == e.series_id) & (rep.report_date < e.ann)].sort_values("report_date").tail(1)
    equity = bool(len(last) and last.n_stocks.iloc[0] >= 20 and last.eq_value_usd.iloc[0] >= 0.8 * last.net_assets.iloc[0])
    if pd.notna(e.stated):
        lame = r[(r.report_date >= e.ann) & (r.report_date <= e.stated)]
        post = r[r.report_date > e.stated]
    else:
        lame = r.iloc[0:0]
        post = r[r.report_date >= e.ann]
    out_rows.append({"adsh": e.adsh, "series_id": e.series_id, "equity": equity, "has_date": pd.notna(e.stated),
                     "pre": len(pre), "lame": len(lame), "post": len(post)})
c = pd.DataFrame(out_rows)
eqc = c[c.equity]


def summary(d):
    return {"series_events": int(len(d)), "announcements": int(d.adsh.nunique()),
            "with_2pre": int((d.pre >= 2).sum()),
            "with_2pre_and_2post": int(((d.pre >= 2) & (d.post >= 2)).sum()),
            "with_date_2pre_1lame_2post": int((d.has_date & (d.pre >= 2) & (d.lame >= 1) & (d.post >= 2)).sum()),
            "announcements_with_date_2pre_1lame_2post": int(d[d.has_date & (d.pre >= 2) & (d.lame >= 1) & (d.post >= 2)].adsh.nunique())}


# Power, from the whole panel only (not aligned to any event, so the design stays blind):
# within-fund sd of log share-based turnover on equity funds, after fund and quarter means.
# MDE (80% power, 5% two-sided) for the mean lame-duck shift across N independent events,
# each averaging L lame-duck reports: 2.8 * sd / sqrt(N * L), ignoring serial correlation.
t = pd.read_parquet(D / "tau.parquet", columns=["series_id", "period", "turnover_split", "n_stocks"])
t = t[(t.n_stocks >= 20) & (t.turnover_split > 1e-3)].copy()
t["y"] = np.log(t.turnover_split)
t["y"] = t.y - t.groupby("series_id").y.transform("mean")
t["y"] = t.y - t.groupby("period").y.transform("mean")
sd = float(t.y.std())
n_ann = summary(eqc)["announcements_with_date_2pre_1lame_2post"]
power = {"sd_log_turnover_within": round(sd, 3),
         "mde_log_points": {f"N={n},L={L}": round(2.8 * sd / np.sqrt(n * L), 3)
                            for n in (n_ann, 100, 200) for L in (1, 2)}}
out = {"all_series": summary(c), "equity_funds": summary(eqc), "power": power,
       "note": "counts only; no outcomes read by event time"}
json.dump(out, open(ROOT / "results" / "nport_event_coverage.json", "w"), indent=1)
print(json.dumps(out, indent=1))
