"""
check_split_rule_paper.py: does the split rule in price_adjusted_tdi.py bias the
paper's split-rebased horizon series (tau_by_inst_quarter.json, series "x")?
(bead cme-ekb; same bug as cme-d0m in the 13F rebuild)

`rebase_splits` treats any continuing position whose share ratio is within 2% of
k or 1/k (k in 2, 3, 4, 5, 6, 8, 10, 20) as a split and sets the earlier share
count equal to the later one, so the trade disappears. Selling exactly half or
doubling a position is then read as a split.

New rule (as in the rebuilt 13F and N-PORT panels): rebase by k only if the
filer's own price for that CUSIP (value / shares) also moved by about 1/k: the
CUSIP's price ratio between the two filings, divided by the median price ratio
over all positions the filer held in both, is within 10% of 1/k. Dividing by the
filer's median makes the check immune to the 2023 thousands-to-dollars change
and to market moves.

Everything else is the original code: `parse`, `rebase_splits`,
`turnover_shares`, `turnover_weights` and `tdi` are extracted unchanged from
price_adjusted_tdi.py, with the same quarter, amendment and >= 50-institution
rules. VIX comes from the stored price_adjusted_tdi_results.csv. The series
rebuilt with the old rule must equal the stored series "x" exactly. The TDI
check is also run with the 2023 unit fix of scripts/check_share_tdi_unit_fix.py
(values filed on or after 2023-01-03 divided by 1000), old and new rule.

Deterministic, no seed. Run from the repo root:
    python scripts/check_split_rule_paper.py
Outputs: results/check_split_rule_paper.json, results/check_split_rule_paper_tdi.csv,
edgar_cache/tau_by_inst_quarter_pricesplit.json (same layout as
tau_by_inst_quarter.json with "x" rebuilt under the new rule; gitignored data).
"""
import ast, glob, json, re, math
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "edgar_cache"

src = (ROOT / "price_adjusted_tdi.py").read_text()
keep = [n for n in ast.parse(src).body
        if (isinstance(n, ast.FunctionDef) and n.name in ("tag", "parse", "rebase_splits", "turnover_shares", "turnover_weights", "tdi"))
        or (isinstance(n, ast.Assign) and any(getattr(t, "id", "") in ("ROW", "SPLITS") for t in n.targets))
        or (isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple)
            and any(getattr(e, "id", "") == "TAU_HI" for e in n.targets[0].elts))]   # K, TAU_LO, TAU_HI
ns = {"np": np, "re": re, "math": math, "Path": Path, "defaultdict": defaultdict}
exec(compile(ast.Module(body=keep, type_ignores=[]), "price_adjusted_tdi_extract", "exec"), ns)
parse, turnover_shares, turnover_weights, tdi = ns["parse"], ns["turnover_shares"], ns["turnover_weights"], ns["tdi"]
SPLITS = ns["SPLITS"]

# counts only: summing values would mix thousands and dollars across the 2023 change
COUNT = {"continuing_positions": 0, "old_rule_fires": 0, "fires_price_confirmed": 0}


def rebase_splits_price(prev, cur, count=False):
    both = [c for c in prev if c in cur]
    rel = {c: (cur[c][1] / cur[c][0]) / (prev[c][1] / prev[c][0]) for c in both}
    med = float(np.median(list(rel.values()))) if rel else 1.0
    out = {}
    for c, (s, v) in prev.items():
        if c in cur:
            r, pr = cur[c][0] / s, rel[c] / med
            old = next((k for k in SPLITS if abs(r - k) / k < 0.02 or abs(r - 1 / k) * k < 0.02), None)
            new = next((f for k in SPLITS for f in (k, 1 / k)
                        if abs(r / f - 1) < 0.02 and abs(pr * f - 1) < 0.10), None)
            if count:
                COUNT["continuing_positions"] += 1
                if old is not None:
                    COUNT["old_rule_fires"] += 1
                    COUNT["fires_price_confirmed"] += new is not None
            if new is not None:
                s = s * new
        out[c] = (s, v)
    return out


def turnover_shares_price(prev, cur, count=False):
    return turnover_shares(rebase_splits_price(prev, cur, count), cur, False)


CUTOFF = "2023-01-03"   # unit fix as in scripts/check_share_tdi_unit_fix.py (filing date on or after: dollars)
acc_q, acc_date = {}, {}
for f in glob.glob(str(CACHE / "submissions" / "*.json")):
    r = json.load(open(f)).get("filings", {}).get("recent", {})
    for a, rd, fd, form in zip(r.get("accessionNumber", []), r.get("reportDate", []), r.get("filingDate", []), r.get("form", [])):
        if form.startswith("13F-HR") and rd:
            k = a.replace("-", "")
            acc_q[k] = f"{rd[:4]}Q{(int(rd[5:7]) - 1) // 3 + 1}"
            acc_date[k] = fd


def scale(pos, dollars):
    return {c: (s, v / 1000.0) for c, (s, v) in pos.items()} if dollars else pos

stores = {k: defaultdict(dict) for k in ("w", "s", "x_old", "x_price", "x_old_unitfix", "x_price_unitfix")}
for d in sorted(glob.glob(str(CACHE / "filings" / "*"))):
    series = {}
    for fp in glob.glob(d + "/*"):
        name = Path(fp).name
        if "index" in name.lower():
            continue
        acc = name[:18]
        q = acc_q.get(acc)
        if q:
            pos = parse(fp)
            if pos:
                series[q] = (pos, (acc_date.get(acc) or "") >= CUTOFF)   # later amendments overwrite
    qs = sorted(series)
    for i in range(1, len(qs)):
        a, b = qs[i - 1], qs[i]
        if (int(b[:4]) * 4 + int(b[5])) - (int(a[:4]) * 4 + int(a[5])) != 1:
            continue
        inst = Path(d).name
        (pa, da), (pb, db) = series[a], series[b]
        ua, ub = scale(pa, da), scale(pb, db)
        for key, fn, p_, c_ in (("w", turnover_weights, pa, pb), ("s", turnover_shares, pa, pb),
                                ("x_old", lambda p, c: turnover_shares(p, c, True), pa, pb),
                                ("x_price", lambda p, c: turnover_shares_price(p, c, True), pa, pb),
                                ("x_old_unitfix", lambda p, c: turnover_shares(p, c, True), ua, ub),
                                ("x_price_unitfix", lambda p, c: turnover_shares_price(p, c, False), ua, ub)):
            t = fn(p_, c_)
            if t and t > 0.001:
                stores[key][b][inst] = 63.0 / t

stored = json.load(open(ROOT / "tau_by_inst_quarter.json"))
def same(a, b):
    keys = {(q, c) for q in a for c in a[q]} | {(q, c) for q in b for c in b[q]}
    return all(q in a and q in b and c in a[q] and c in b[q] and abs(a[q][c] - b[q][c]) < 1e-9 * max(1, abs(b[q][c]))
               for q, c in keys)
repro = {k: same(stores[m], stored[k]) for k, m in (("w", "w"), ("s", "s"), ("x", "x_old"))}
json.dump({"w": stores["w"], "s": stores["s"], "x": stores["x_price"]},
          open(CACHE / "tau_by_inst_quarter_pricesplit.json", "w"))

# per institution-quarter change in log tau, old vs new rule
pairs = [(math.log(stores["x_old"][q][c]), math.log(stores["x_price"][q][c]))
         for q in stores["x_old"] for c in stores["x_old"][q] if c in stores["x_price"].get(q, {})]
lo, ln_ = np.array(pairs).T
lo_c, ln_c = np.log(np.clip(np.exp(lo), 5, 2000)), np.log(np.clip(np.exp(ln_), 5, 2000))

rows = []
for q in sorted(set.intersection(*[set(s) for s in stores.values()])):
    common = set.intersection(*[set(s[q]) for s in stores.values()])
    if len(common) < 50:
        continue
    row = {"quarter": q, "n": len(common)}
    for k, s in stores.items():
        row[f"tdi_{k}"] = tdi(np.array([s[q][c] for c in common]))
        row[f"med_tau_{k}"] = float(np.median([s[q][c] for c in common]))
    rows.append(row)
df = pd.DataFrame(rows).merge(pd.read_csv(ROOT / "price_adjusted_tdi_results.csv")[["quarter", "tdi_x", "vix"]],
                              on="quarter", how="left")
(ROOT / "results").mkdir(exist_ok=True)
df.to_csv(ROOT / "results" / "check_split_rule_paper_tdi.csv", index=False)

out = {"reproduces_stored_series_exactly": repro,
       "split_rule_firings": {**{k: int(v) for k, v in COUNT.items()},
                              "share_of_fires_unconfirmed": round(1 - COUNT["fires_price_confirmed"] / max(COUNT["old_rule_fires"], 1), 4),
                              "unconfirmed_share_of_positions": round((COUNT["old_rule_fires"] - COUNT["fires_price_confirmed"]) / COUNT["continuing_positions"], 4)},
       "institution_quarters": int(len(lo)),
       "log_tau_x_change_new_minus_old": {"mean": round(float((ln_c - lo_c).mean()), 4),
                                          "median": round(float(np.median(ln_c - lo_c)), 4),
                                          "share_changed": round(float((np.abs(ln_c - lo_c) > 1e-9).mean()), 4),
                                          "corr_old_new": round(float(np.corrcoef(lo_c, ln_c)[0, 1]), 4)},
       "median_tau_x": {"old": round(float(np.median(np.exp(lo))), 1), "new": round(float(np.median(np.exp(ln_))), 1)}}
paper = df[(df.quarter >= "2013Q3") & (df.quarter <= "2024Q3")].dropna(subset=["vix"])
for col in ("tdi_w", "tdi_s", "tdi_x_old", "tdi_x_price", "tdi_x_old_unitfix", "tdi_x_price_unitfix"):
    r, p = stats.pearsonr(paper[col], paper.vix)
    out[f"r_vix_{col}"] = {"r": round(float(r), 3), "p": float(p), "n": int(len(paper))}
json.dump(out, open(ROOT / "results" / "check_split_rule_paper.json", "w"), indent=1)
print(json.dumps(out, indent=1))
