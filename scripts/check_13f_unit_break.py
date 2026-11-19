"""
check_13f_unit_break.py: does the SEC 13F unit change explain the 2022Q4 TDI minimum?

Background. From January 3, 2023 the SEC requires Form 13F information tables to
report market value in dollars instead of thousands of dollars. Filings for
2022Q4 onward were filed after that date. `edgar_cache/holdings_db.json` stores
the raw reported figure in a field called `value_k` for every quarter, so
quarters >= 2022Q4 are in dollars while earlier quarters are in thousands.

`empirical_tdi.compute_turnover` uses raw value differences between consecutive
quarters, so the 2022Q3 -> 2022Q4 transition sees every position grow about
1000x and reports turnover near 1 for almost every institution.

This script (1) shows the jump in reported values, (2) recomputes the original
TDI series with the original functions (extracted from empirical_tdi.py
unchanged), with and without dividing post-change values by 1000, and
(3) compares both with the stored series in empirical_tdi_results.csv.

Deterministic: no randomness. Run from the repo root:
    python scripts/check_13f_unit_break.py
Output: results/check_13f_unit_break.csv
"""
import ast, json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
UNIT_CHANGE_FIRST_Q = "2022Q4"   # first quarter whose filings were made after 2023-01-03

# Pull the original functions and constants out of empirical_tdi.py without
# importing it (its module-level code points at another user's cache folder).
src = (ROOT / "empirical_tdi.py").read_text()
tree = ast.parse(src)
keep = []
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in ("compute_turnover", "turnover_to_tau", "compute_tdi"):
        keep.append(node)
    if isinstance(node, ast.Assign) and any(getattr(t, "id", "") in ("TDI_K", "TAU_MIN", "TAU_MAX", "TAU_FLOOR", "TAU_CAP") for t in node.targets):
        keep.append(node)
ns = {"np": np}
exec(compile(ast.Module(body=keep, type_ignores=[]), "empirical_tdi_extract", "exec"), ns)
compute_turnover, turnover_to_tau, compute_tdi = ns["compute_turnover"], ns["turnover_to_tau"], ns["compute_tdi"]

db = json.load(open(ROOT / "edgar_cache" / "holdings_db.json"))
quarters = sorted({q for d in db.values() for q in d})

def prevq(q):
    y, n = int(q[:4]), int(q[5])
    return f"{y-1}Q4" if n == 1 else f"{y}Q{n-1}"

def scaled(hs, q, fix):
    if fix and q >= UNIT_CHANGE_FIRST_Q:
        return [{"cusip": h["cusip"], "value_k": (h.get("value_k") or 0) / 1000.0} for h in hs]
    return hs

rows = []
for q in quarters:
    p = prevq(q)
    med = np.median([np.median([h.get("value_k") or 0 for h in d[q]]) for d in db.values() if d.get(q)])
    out = {"quarter": q, "median_position_reported": float(med)}
    for fix in (False, True):
        taus = []
        for d in db.values():
            if d.get(q) and d.get(p):
                t = compute_turnover(scaled(d[p], p, fix), scaled(d[q], q, fix))
                if t is not None:
                    taus.append(turnover_to_tau(t))
        out["tdi_unit_fixed" if fix else "tdi_as_coded"] = compute_tdi(taus)
        out["n_inst_fixed" if fix else "n_inst"] = len(taus)
        if not fix:
            out["median_tau_as_coded"] = float(np.median(taus)) if taus else None
    rows.append(out)

res = pd.DataFrame(rows)
orig = pd.read_csv(ROOT / "empirical_tdi_results.csv")[["label", "TDI"]].rename(columns={"label": "quarter", "TDI": "tdi_stored_paper"})
res = res.merge(orig, on="quarter", how="left")
(ROOT / "results").mkdir(exist_ok=True)
res.to_csv(ROOT / "results" / "check_13f_unit_break.csv", index=False)
pd.set_option("display.width", 200)
print(res[(res.quarter >= "2021Q4") & (res.quarter <= "2023Q4")].round(3).to_string(index=False))
ok = res.dropna(subset=["tdi_stored_paper", "tdi_as_coded"])
print(f"\ncorr(stored paper TDI, recomputed as coded) = {ok.tdi_stored_paper.corr(ok.tdi_as_coded):.3f} over {len(ok)} quarters")

# Effect on the paper's headline TDI-VIX correlation (paper sample: 2013Q3-2024Q3, n = 45)
from scipy import stats
vix = pd.read_csv(ROOT / "empirical_tdi_results.csv")[["label", "VIX_avg"]].rename(columns={"label": "quarter"})
s = res.merge(vix, on="quarter")
s = s[(s.quarter >= "2013Q3") & (s.quarter <= "2024Q3")].dropna(subset=["VIX_avg"])
summary = {}
for col in ("tdi_stored_paper", "tdi_as_coded", "tdi_unit_fixed"):
    d = s.dropna(subset=[col])
    r, p = stats.pearsonr(d[col], d.VIX_avg)
    summary[col] = {"r": round(float(r), 3), "p": float(p), "n": int(len(d))}
    print(f"r(TDI, VIX) using {col:17s}: r = {r:+.3f}, p = {p:.2g}, n = {len(d)}")
json.dump(summary, open(ROOT / "results" / "check_13f_unit_break_vix.json", "w"), indent=1)

# Does the unit break explain the open bead cme-0ef (rebuilt series correlates 0.50 with the original)?
rb = pd.read_csv(ROOT / "price_adjusted_tdi_results.csv")[["quarter", "tdi_w", "tdi_s", "tdi_x"]]
m = res.merge(rb, on="quarter")
comp = {}
for c in ("tdi_w", "tdi_s", "tdi_x"):
    comp[c] = {"corr_with_stored": round(float(m.tdi_stored_paper.corr(m[c])), 3),
               "corr_with_unit_fixed": round(float(m.tdi_unit_fixed.corr(m[c])), 3), "n": int(m[c].notna().sum())}
    print(f"corr(original, rebuilt {c}): stored {comp[c]['corr_with_stored']:+.3f} -> unit-fixed {comp[c]['corr_with_unit_fixed']:+.3f}")
json.dump(comp, open(ROOT / "results" / "check_13f_unit_break_rebuilt.json", "w"), indent=1)
