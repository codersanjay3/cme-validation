"""
Stage 1a: how much of an institution's horizon moves over time? (no peer variables)

Pre-registered in docs/stage1/PREREGISTRATION.md. Gate 1a: the share of
var(log tau) left after institution and quarter fixed effects must be >= 10%.

Run from the repo root: python stage1/stage1a_variance.py
Output: results/stage1a_variance.json. Deterministic.
"""
import json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, load_tau, demean

t = load_tau()
t = t[t.groupby("cik").cik.transform("size") >= 2]          # institution FE needs >= 2 quarters
tot = float(t.ltau.var())
res = {}
for name, fes in (("institution", ["cik"]), ("quarter", ["period"]),
                  ("institution+quarter", ["cik", "period"]),
                  ("institution+style_by_quarter", ["cik", "style_q"])):
    r = demean(t, ["ltau"], fes)["ltau"]
    res[name] = round(float(r.var() / tot), 4)
ar = t.sort_values(["cik", "qn"])
lag = ar.groupby("cik").ltau.shift(1)
ok = (ar.qn - ar.groupby("cik").qn.shift(1)) == 1
out = {
    "n_institution_quarters": int(len(t)), "n_institutions": int(t.cik.nunique()),
    "n_quarters": int(t.period.nunique()), "var_log_tau": round(tot, 4),
    "share_of_variance_left_after": res,
    "ar1_log_tau": round(float(np.corrcoef(ar.ltau[ok], lag[ok])[0, 1]), 3),
    "gate_1a_threshold": 0.10,
    "gate_1a_pass": bool(res["institution+quarter"] >= 0.10),
}
(ROOT / "results").mkdir(exist_ok=True)
json.dump(out, open(ROOT / "results" / "stage1a_variance.json", "w"), indent=1)
print(json.dumps(out, indent=1))
