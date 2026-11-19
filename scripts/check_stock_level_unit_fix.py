"""
check_stock_level_unit_fix.py: does the 13F unit problem move the stock-level result?

stock_level_test.py weights each stock's holders by reported 13F value
(`value_k` in holdings_db.json). The SEC moved 13F values from thousands to
dollars for filings from 2023-01-03, but not every filer switched on time: in
our top-150 panel 66 filers jump about 1000x exactly at 2022Q4, while 25 show
no jump there and several switch later (2023Q1, 2023Q2, 2024Q3, 2025Q3), and a
few have one-quarter 1000x spikes. Mixing units inside a stock-quarter gives
holders still in thousands almost no weight.

Fix used here (per filer, over time): walk each filer's quarters in order,
start in thousands, and flip the unit state whenever the filer's median
position value jumps by more than 300x (to dollars) or falls by more than 300x
(back to thousands) between consecutive quarters. Values are then put in
dollars. The cross-section cannot do this, because typical position sizes
differ by up to 100x across filers.

The script then runs stock_level_test.py unchanged except for (1) its ROOT
path, (2) the unit normalisation applied to holdings_db before weights are
built, and (3) the output file. It runs it twice: as coded (to confirm it
reproduces the stored results) and unit-fixed. Seed 7 as in the original.

Run from the repo root: python scripts/check_stock_level_unit_fix.py
Outputs: results/check_stock_level_unit_fix.json, results/unit_flips_by_filer.json
(optional threshold argument, e.g. 100 or 1000, writes *_flip<N>.json for the sensitivity check)
"""
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FLIP = float(sys.argv[1]) if len(sys.argv) > 1 else 300.0

def qn(q):
    return int(q[:4]) * 4 + int(q[5])

def unit_states(db):
    states, flips = {}, {}
    for cik, qs in db.items():
        order = sorted(qs, key=qn)
        med = {q: float(np.median([h.get("value_k") or 0 for h in qs[q] if (h.get("value_k") or 0) > 0] or [0])) for q in order}
        state, prev, out, fl = "thousands", None, {}, []
        for q in order:
            if prev is not None and med[prev] > 0 and med[q] > 0 and qn(q) - qn(prev) == 1:
                r = med[q] / med[prev]
                if r > FLIP and state == "thousands":
                    state = "dollars"; fl.append((q, "to dollars", round(r)))
                elif r < 1 / FLIP and state == "dollars":
                    state = "thousands"; fl.append((q, "to thousands", round(1 / r)))
            out[q] = state
            prev = q
        states[cik], flips[cik] = out, fl
    return states, flips

src = (ROOT / "stock_level_test.py").read_text()
src = src.replace('ROOT = Path("/Users/sanjaysubramania/cme_validation")', f'ROOT = Path({str(ROOT)!r})')
assert "ROOT = Path(" in src and "sanjaysubramania" not in src

def run(fix):
    s = src
    if fix:
        s = s.replace('db = json.load(open(ROOT / "edgar_cache" / "holdings_db.json"))',
                      'db = json.load(open(ROOT / "edgar_cache" / "holdings_db.json"))\n'
                      'db = __normalise__(db)')
    s = s.replace('json.dump(results, open(ROOT / "stock_level_results.json", "w"), indent=1)',
                  'RESULTS_OUT.update(results)')
    out = {}
    ns = {"__name__": "__check__", "RESULTS_OUT": out, "__normalise__": normalise}
    exec(compile(s, "stock_level_test_adapted", "exec"), ns)
    return out

STATE = {}
def normalise(db):
    states, flips = unit_states(db)
    STATE["flips"] = {c: f for c, f in flips.items() if f}
    for cik, qs in db.items():
        for q, hs in qs.items():
            if states[cik][q] == "thousands":
                for h in hs:
                    if h.get("value_k"):
                        h["value_k"] = h["value_k"] * 1000.0
    return db

print("=== as coded ===", flush=True)
as_coded = run(False)
print("=== unit-fixed ===", flush=True)
fixed = run(True)
stored = json.load(open(ROOT / "stock_level_results.json"))
summary = {"stored": stored, "as_coded": as_coded, "unit_fixed": fixed,
           "n_filers_with_flips": len(STATE.get("flips", {}))}
(ROOT / "results").mkdir(exist_ok=True)
json.dump(summary, open(ROOT / "results" / ("check_stock_level_unit_fix.json" if FLIP == 300.0 else f"check_stock_level_unit_fix_flip{int(FLIP)}.json"), "w"), indent=1)
json.dump(STATE.get("flips", {}), open(ROOT / "results" / ("unit_flips_by_filer.json" if FLIP == 300.0 else f"unit_flips_by_filer_flip{int(FLIP)}.json"), "w"), indent=1)
for k in ("x:twoway", "w:twoway"):
    print(k, "stored", stored.get(k), "| as coded", as_coded.get(k), "| unit-fixed", fixed.get(k))
for k in ("x:lrv_next", "w:lrv_next", "placebo"):
    print(k, "as coded", as_coded.get(k), "| unit-fixed", fixed.get(k))
