"""
check_stock_level_split_rule.py: does the split-rule fix move the paper's
stock-level result? (bead cme-ekb)

stock_level_test.py takes holder horizons from tau_by_inst_quarter.json; its
primary series "x" (share-based, splits rebased) used a split rule that read
exact half-sales and doublings as splits. scripts/check_split_rule_paper.py
rebuilds "x" under a price-confirmed rule into
edgar_cache/tau_by_inst_quarter_pricesplit.json ("w" and "s" unchanged).

This script runs stock_level_test.py unchanged except for (1) its ROOT path,
(2) the horizon file, (3) optionally the per-filer unit normalisation from
scripts/check_stock_level_unit_fix.py (extracted unchanged, threshold 300x),
and (4) the output file. Four runs: {old, new split rule} x {as coded, unit-fixed}.
Seed 7 as in the original; the old-rule runs must reproduce the stored results.

Run from the repo root (after check_split_rule_paper.py):
    python scripts/check_stock_level_split_rule.py
Output: results/check_stock_level_split_rule.json
"""
import ast, json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NEW_TAU = ROOT / "edgar_cache" / "tau_by_inst_quarter_pricesplit.json"

# unit normalisation, extracted unchanged from check_stock_level_unit_fix.py
uf = (ROOT / "scripts" / "check_stock_level_unit_fix.py").read_text()
keep = [n for n in ast.parse(uf).body if isinstance(n, ast.FunctionDef) and n.name in ("qn", "unit_states")]
uns = {"np": np, "FLIP": 300.0}
exec(compile(ast.Module(body=keep, type_ignores=[]), "unit_fix_extract", "exec"), uns)


def normalise(db):
    states, _ = uns["unit_states"](db)
    for cik, qs in db.items():
        for q, hs in qs.items():
            if states[cik][q] == "thousands":
                for h in hs:
                    if h.get("value_k"):
                        h["value_k"] = h["value_k"] * 1000.0
    return db


src = (ROOT / "stock_level_test.py").read_text()
src = src.replace('ROOT = Path("/Users/sanjaysubramania/cme_validation")', f'ROOT = Path({str(ROOT)!r})')
assert "sanjaysubramania" not in src
TAU_LINE = 'taus = json.load(open(ROOT / "tau_by_inst_quarter.json"))'
DB_LINE = 'db = json.load(open(ROOT / "edgar_cache" / "holdings_db.json"))'
OUT_LINE = 'json.dump(results, open(ROOT / "stock_level_results.json", "w"), indent=1)'
assert TAU_LINE in src and DB_LINE in src and OUT_LINE in src


def run(new_rule, unit_fix):
    s = src
    if new_rule:
        s = s.replace(TAU_LINE, f'taus = json.load(open({str(NEW_TAU)!r}))')
    if unit_fix:
        s = s.replace(DB_LINE, DB_LINE + "\ndb = __normalise__(db)")
    s = s.replace(OUT_LINE, "RESULTS_OUT.update(results)")
    out = {}
    exec(compile(s, "stock_level_test_adapted", "exec"),
         {"__name__": "__check__", "RESULTS_OUT": out, "__normalise__": normalise})
    return out


res = {}
for new_rule in (False, True):
    for unit_fix in (False, True):
        key = f"{'new' if new_rule else 'old'}_split_rule|{'unit_fixed' if unit_fix else 'as_coded'}"
        print("===", key, flush=True)
        res[key] = run(new_rule, unit_fix)
stored = json.load(open(ROOT / "stock_level_results.json"))
prior_fix = json.load(open(ROOT / "results" / "check_stock_level_unit_fix.json"))["unit_fixed"]
def close(a, b, tol=1e-9):
    """Equal up to floating-point summation order (relative tolerance)."""
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(close(a[k], b[k], tol) for k in a)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= tol * max(1.0, abs(b))
    return a == b


out = {"reproduces_stored": close(res["old_split_rule|as_coded"], stored),
       "reproduces_unit_fix_check": close(res["old_split_rule|unit_fixed"], prior_fix),
       "runs": res}
json.dump(out, open(ROOT / "results" / "check_stock_level_split_rule.json", "w"), indent=1)
print("reproduces stored:", out["reproduces_stored"], "| reproduces unit-fix check:", out["reproduces_unit_fix_check"])
for k in ("x:twoway", "w:twoway", "x:lrv_next", "placebo"):
    for key, r in res.items():
        print(f"{k:12s} {key:32s} {r.get(k)}")
