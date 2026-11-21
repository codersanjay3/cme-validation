"""
Stage 2 scoping: how many 497 manager events land on N-PORT equity funds.

Joins results/stage2_events.csv (stage2/scope_events.py) to the equity-fund series
lists written by stage2/nport_coverage.py (nport_cache/equity_series_<q>.csv) on
SERIES_ID. A series counts as an equity fund if it meets the definition in any
coverage quarter available locally (scoping uses one quarter, so this is a lower
bound: funds that were equity funds only in other quarters are missed).

Run from the repo root:  python stage2/link_events.py
Output: results/stage2_event_link.json. No randomness.
"""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ev = pd.read_csv(ROOT / "results" / "stage2_events.csv", dtype=str)
eqs = [pd.read_csv(p, dtype={"SERIES_ID": str}) for p in sorted((ROOT / "nport_cache").glob("equity_series_*.csv"))]
eq = pd.concat(eqs).drop_duplicates("SERIES_ID")
ev["equity_fund"] = ev.series_id.isin(eq.SERIES_ID)
ev = ev.merge(eq[["SERIES_ID", "nav"]], left_on="series_id", right_on="SERIES_ID", how="left")
ev["nav_100m"] = ev.nav >= 1e8
ev["in_nport_window"] = (ev.month >= "2020-01") & (ev.month <= "2026-03")  # need >= 1 quarter before and 2 after
out = {"equity_series_quarters_used": [p.name for p in sorted((ROOT / "nport_cache").glob("equity_series_*.csv"))]}
for kind, g in ev.groupby("kind"):
    e = g[g.equity_fund]
    out[kind] = {
        "fund_series_events": int(len(g)),
        "on_equity_funds": int(len(e)),
        "on_equity_funds_nav_100m": int(e.nav_100m.sum()),
        "on_equity_funds_in_window": int(e.in_nport_window.sum()),
        "distinct_announcements_on_equity_funds": int(e.adsh.nunique()),
        "distinct_trusts_on_equity_funds": int(e.trust_cik.nunique()),
        "equity_events_by_year": {k: int(v) for k, v in e.month.str[:4].value_counts().sort_index().items()},
    }
json.dump(out, open(ROOT / "results" / "stage2_event_link.json", "w"), indent=1)
print(json.dumps(out, indent=1))
