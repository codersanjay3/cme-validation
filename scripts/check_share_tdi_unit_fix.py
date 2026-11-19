"""
check_share_tdi_unit_fix.py: share-based TDI with the 13F dollar-unit change handled.

Open item from issue #1. `price_adjusted_tdi.turnover_shares` values every
position at a per-share price v/s. Since 2023-01-03 the SEC requires 13F values
in dollars (before: thousands). For an institution's first quarter after the
change, positions it exited keep a price from the older filing (thousands),
while continuing positions take the newer price (dollars), so exits are
undervalued about 1000x and turnover is understated.

Fix: divide reported values by 1000 for every filing whose FILING DATE is on or
after 2023-01-03 (amendments for earlier quarters filed later are in dollars
too). Everything else is the original code: `parse`, `rebase_splits`,
`turnover_shares`, `turnover_weights` and `tdi` are extracted unchanged from
price_adjusted_tdi.py, and the same quarter, amendment and >= 50-institution
rules are applied. VIX is taken from the stored price_adjusted_tdi_results.csv
so the comparison uses the identical VIX series.

Deterministic, no seed. Run from the repo root:
    python scripts/check_share_tdi_unit_fix.py
Outputs: results/check_share_tdi_unit_fix.csv, results/check_share_tdi_unit_fix.json
"""
import ast, glob, json, re, math
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "edgar_cache"
CUTOFF = "2023-01-03"

src = (ROOT / "price_adjusted_tdi.py").read_text()
keep = [n for n in ast.parse(src).body
        if (isinstance(n, ast.FunctionDef) and n.name in ("tag", "parse", "rebase_splits", "turnover_shares", "turnover_weights", "tdi"))
        or (isinstance(n, ast.Assign) and any(getattr(t, "id", "") in ("ROW", "SPLITS") for t in n.targets))
        or (isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple)
            and any(getattr(e, "id", "") == "TAU_HI" for e in n.targets[0].elts))]   # K, TAU_LO, TAU_HI
ns = {"np": np, "re": re, "math": math, "Path": Path, "defaultdict": defaultdict}
exec(compile(ast.Module(body=keep, type_ignores=[]), "price_adjusted_tdi_extract", "exec"), ns)
parse, turnover_shares, turnover_weights, tdi = ns["parse"], ns["turnover_shares"], ns["turnover_weights"], ns["tdi"]

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

stores = {k: defaultdict(dict) for k in ("s_orig", "x_orig", "s_fix", "x_fix", "w")}
n_dollar_filings = 0
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
                dollars = (acc_date.get(acc) or "") >= CUTOFF
                n_dollar_filings += dollars
                series[q] = (pos, dollars)          # later amendments overwrite, as in the original
    qs = sorted(series)
    for i in range(1, len(qs)):
        a, b = qs[i - 1], qs[i]
        if (int(b[:4]) * 4 + int(b[5])) - (int(a[:4]) * 4 + int(a[5])) != 1:
            continue
        (pa, da), (pb, db) = series[a], series[b]
        inst = Path(d).name
        for key, fn, p_, c_ in (("w", turnover_weights, pa, pb),
                                ("s_orig", turnover_shares, pa, pb),
                                ("x_orig", lambda p, c: turnover_shares(p, c, True), pa, pb),
                                ("s_fix", turnover_shares, scale(pa, da), scale(pb, db)),
                                ("x_fix", lambda p, c: turnover_shares(p, c, True), scale(pa, da), scale(pb, db))):
            t = fn(p_, c_)
            if t and t > 0.001:
                stores[key][b][inst] = 63.0 / t

rows = []
for q in sorted(set.intersection(*[set(s) for s in stores.values()])):
    common = set.intersection(*[set(s[q]) for s in stores.values()])
    if len(common) < 50:
        continue
    row = {"quarter": q, "n": len(common)}
    for k, s in stores.items():
        row[f"tdi_{k}"] = tdi(np.array([s[q][c] for c in common]))
    rows.append(row)
df = pd.DataFrame(rows)
stored = pd.read_csv(ROOT / "price_adjusted_tdi_results.csv")[["quarter", "tdi_s", "tdi_x", "vix"]]
df = df.merge(stored, on="quarter", how="left")
(ROOT / "results").mkdir(exist_ok=True)
df.to_csv(ROOT / "results" / "check_share_tdi_unit_fix.csv", index=False)

out = {"n_filings_in_dollars": int(n_dollar_filings),
       "reproduces_stored_s": round(float(df.tdi_s_orig.corr(df.tdi_s)), 4),
       "reproduces_stored_x": round(float(df.tdi_x_orig.corr(df.tdi_x)), 4)}
paper = df[(df.quarter >= "2013Q3") & (df.quarter <= "2024Q3")].dropna(subset=["vix"])
for col in ("tdi_w", "tdi_s_orig", "tdi_x_orig", "tdi_s_fix", "tdi_x_fix"):
    r, p = stats.pearsonr(paper[col], paper.vix)
    out[f"r_vix_{col}"] = {"r": round(float(r), 3), "p": float(p), "n": int(len(paper))}
json.dump(out, open(ROOT / "results" / "check_share_tdi_unit_fix.json", "w"), indent=1)
pd.set_option("display.width", 200)
print(df[(df.quarter >= "2022Q2") & (df.quarter <= "2023Q2")].round(3).to_string(index=False))
print(json.dumps(out, indent=1))
