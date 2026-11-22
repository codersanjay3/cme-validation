"""
How often does the 13F split rule (rebuild_13f/build_panel.py::_split_rebase) fire
without a matching move in the stock's common price? (bead cme-d0m)

For each consecutive pair of periods and each position held in both, the 13F rule
fires when the filer's share ratio is within 2% of k or 1/k (k in SPLITS). A real
split also moves the CUSIP's common (median) price by about 1/k. Counts firings with
and without that price confirmation (price ratio within 10% of 1/k), by share of
positions and of traded value. Reads panel_13f/positions; read-only.
Run from the repo root: python scoping/split_rule_check.py
Output: results/scoping_split_rule_check.json. Deterministic.
"""
import glob, json, sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SPLITS = (2, 3, 4, 5, 6, 8, 10, 20)
files = sorted(glob.glob(str(ROOT / "panel_13f" / "positions" / "*.parquet")))
qn = lambda q: int(q[:4]) * 4 + int(q[5])
tot = {"pairs_both_held": 0, "fires": 0, "fires_price_confirmed": 0, "fires_unconfirmed": 0,
       "value_both_held": 0.0, "value_unconfirmed": 0.0}
by_k = {}
prev = None
for f in files:
    cur = pd.read_parquet(f, columns=["cik", "cusip", "shares", "value_usd"])
    cur["cik"] = cur.cik.astype(str)
    q = Path(f).stem
    pc = (cur.value_usd / cur.shares).groupby(cur.cusip).median()
    if prev is not None and qn(q) - qn(prev[0]) == 1:
        p0, pp = prev[1], prev[2]
        m = p0.merge(cur, on=["cik", "cusip"], suffixes=("_0", "_1"))
        m = m[(m.shares_0 > 0) & (m.shares_1 > 0)]
        r = (m.shares_1 / m.shares_0).to_numpy()
        pr = (m.cusip.map(pc) / m.cusip.map(pp)).to_numpy()
        fired = np.zeros(len(m), bool); conf = np.zeros(len(m), bool)
        for k in SPLITS:
            for fct in (k, 1 / k):
                h = (np.abs(r - fct) / fct < 0.02) & ~fired
                c = h & (np.abs(pr * fct - 1) < 0.10)
                key = f"{fct:g}"
                by_k.setdefault(key, [0, 0])
                by_k[key][0] += int(h.sum()); by_k[key][1] += int(c.sum())
                fired |= h; conf |= c
        v = m.value_usd_1.to_numpy()
        tot["pairs_both_held"] += len(m); tot["fires"] += int(fired.sum())
        tot["fires_price_confirmed"] += int(conf.sum()); tot["fires_unconfirmed"] += int((fired & ~conf).sum())
        tot["value_both_held"] += float(v.sum()); tot["value_unconfirmed"] += float(v[fired & ~conf].sum())
    prev = (q, cur, pc)
    print(q, flush=True, end=" ")
out = dict(tot)
out["share_positions_unconfirmed"] = round(tot["fires_unconfirmed"] / tot["pairs_both_held"], 5)
out["share_value_unconfirmed"] = round(tot["value_unconfirmed"] / tot["value_both_held"], 5)
out["share_of_firings_unconfirmed"] = round(tot["fires_unconfirmed"] / max(tot["fires"], 1), 3)
out["by_factor_fired_confirmed"] = by_k
json.dump(out, open(ROOT / "results" / "scoping_split_rule_check.json", "w"), indent=1)
print(); print(json.dumps(out, indent=1))
