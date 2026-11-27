"""
coverage.py: how many lame-duck events (results/lameduck_events.csv) have enough
N-PORT reports around them. COUNTS ONLY: no outcome (turnover, risk, returns) is
read by event time, so the pre-registration stays blind.

Same rules as nport_panel/event_coverage.py, with the event's actual filing date:
  equity fund = at least 20 stocks and equity value at least 80% of net assets in
  the last report before the announcement;
  pre = reports dated before the announcement; lame duck = reports from the
  announcement date to the end date; post = reports after the end date.
Usable event = an end date, at least 2 pre, at least 1 lame-duck and 2 post reports.
Reported for end dates stated in the text, and for stated or later-notice ends,
and again for filings whose header names at most 5 series (a header can list a
whole trust, so wide filings may tag funds the retiring manager does not run).

Power from whole-panel variance only (not event-aligned): within-fund sd of log
share-based turnover on equity funds after fund and quarter means; MDE (80% power,
5% two-sided) = 2.8 * sd / sqrt(N * L), N independent announcements, L lame-duck
reports each, ignoring serial correlation.

Run from the repo root: python lameduck/coverage.py
Output: results/lameduck_coverage.json. Deterministic.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "nport_panel_data"
ev = pd.read_csv(ROOT / "results" / "lameduck_events.csv", dtype=str, keep_default_na=False)
ev["ann"] = pd.to_datetime(ev.filed)
ev["end"] = pd.to_datetime(ev.end.replace("", None), errors="coerce")
rows = pd.read_parquet(D / "tau.parquet", columns=["series_id", "report_date"])
rep = pd.read_parquet(D / "reports.parquet", columns=["series_id", "report_date", "net_assets", "eq_value_usd", "n_stocks"])
rows_by = {k: g.report_date.sort_values().to_numpy() for k, g in rows.groupby("series_id")}
rep_by = {k: g.sort_values("report_date") for k, g in rep.groupby("series_id")}

out_rows = []
for e in ev.itertuples():
    r = rows_by.get(e.series_id, np.array([], dtype="datetime64[ns]"))
    rp = rep_by.get(e.series_id)
    last = rp[rp.report_date < e.ann].tail(1) if rp is not None else pd.DataFrame()
    equity = bool(len(last) and last.n_stocks.iloc[0] >= 20 and last.eq_value_usd.iloc[0] >= 0.8 * last.net_assets.iloc[0])
    ann = np.datetime64(e.ann)
    if pd.notna(e.end):
        end = np.datetime64(e.end)
        lame, post = int(((r >= ann) & (r <= end)).sum()), int((r > end).sum())
    else:
        lame, post = 0, int((r >= ann).sum())
    out_rows.append({"adsh": e.adsh, "series_id": e.series_id, "equity": equity, "end_source": e.end_source,
                     "lag_months": (e.end - e.ann).days / 30.44 if pd.notna(e.end) else np.nan,
                     "in_panel": bool(len(r)), "pre": int((r < ann).sum()), "lame": lame, "post": post})
c = pd.DataFrame(out_rows)
# header SERIES-IDs can list a whole trust; announcements naming few series are more precise
c["n_series_in_filing"] = c.groupby("adsh").series_id.transform("nunique")


def summary(d):
    usable = (d.pre >= 2) & (d.lame >= 1) & (d.post >= 2)
    st, ln = d.end_source == "stated", d.end_source.isin(["stated", "later_notice"])
    return {"series_events": int(len(d)), "announcements": int(d.adsh.nunique()),
            "in_panel": int(d.in_panel.sum()),
            "with_end": {"stated": int(st.sum()), "later_notice": int((d.end_source == "later_notice").sum())},
            "lag_months_stated_quantiles": {str(q): round(float(d[st].lag_months.quantile(q)), 1)
                                            for q in (0.1, 0.25, 0.5, 0.75, 0.9)} if st.any() else {},
            "usable_stated": {"series_events": int((usable & st).sum()), "announcements": int(d[usable & st].adsh.nunique())},
            "usable_stated_or_notice": {"series_events": int((usable & ln).sum()), "announcements": int(d[usable & ln].adsh.nunique())},
            "mean_lame_reports_usable_stated": round(float(d[usable & st].lame.mean()), 2) if (usable & st).any() else None}


t = pd.read_parquet(D / "tau.parquet", columns=["series_id", "period", "turnover_split", "n_stocks"])
t = t[(t.n_stocks >= 20) & (t.turnover_split > 1e-3)].copy()
t["y"] = np.log(t.turnover_split)
t["y"] = t.y - t.groupby("series_id").y.transform("mean")
t["y"] = t.y - t.groupby("period").y.transform("mean")
sd = float(t.y.std())
eq = summary(c[c.equity])
eq_narrow = summary(c[c.equity & (c.n_series_in_filing <= 5)])
n1, n2 = eq["usable_stated"]["announcements"], eq["usable_stated_or_notice"]["announcements"]
power = {"sd_log_turnover_within": round(sd, 3),
         "mde_log_points": {f"N={n},L={L}": round(2.8 * sd / np.sqrt(n * L), 3) for n in sorted({n1, n2}) if n for L in (1, 2)}}
n3 = eq_narrow["usable_stated"]["announcements"]
power["mde_log_points"].update({f"narrow N={n3},L={L}": round(2.8 * sd / np.sqrt(n3 * L), 3) for L in (1, 2)} if n3 else {})
out = {"all_series": summary(c), "equity_funds": eq,
       "equity_funds_filing_names_at_most_5_series": eq_narrow, "power": power,
       "note": "counts only; no outcomes read by event time"}
json.dump(out, open(ROOT / "results" / "lameduck_coverage.json", "w"), indent=1)
print(json.dumps(out, indent=1))
