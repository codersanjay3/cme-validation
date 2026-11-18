"""
price_adjusted_tdi.py — Does VIX -> TDI survive removing price-drift from turnover?

Chalmers' mechanism question: when volatility is high, people trade more, so
tau = 63/turnover falls. But value-weight turnover (used in empirical_tdi.py)
also rises mechanically when prices move, even with zero trading. Here turnover
is built from SHARE changes only (valued at one common price per CUSIP), so
price moves cannot create turnover.

Outputs: quarterly TDI (weight-based vs share-based), correlation with VIX,
Granger tests in both directions for each TDI version.
"""
import json, re, math, glob
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy import stats
import yfinance as yf
from statsmodels.tsa.api import VAR

ROOT = Path("/Users/sanjaysubramania/cme_validation")
CACHE = ROOT / "edgar_cache"
K, TAU_LO, TAU_HI = 16, 5.0, 2000.0

# accession -> report quarter, from cached submissions files
acc_q = {}
for f in glob.glob(str(CACHE / "submissions" / "*.json")):
    r = json.load(open(f)).get("filings", {}).get("recent", {})
    for a, rd, form in zip(r.get("accessionNumber", []), r.get("reportDate", []), r.get("form", [])):
        if form.startswith("13F-HR") and rd:
            acc_q[a.replace("-", "")] = f"{rd[:4]}Q{(int(rd[5:7]) - 1) // 3 + 1}"

ROW = re.compile(r"<(?:\w+:)?infoTable>(.*?)</(?:\w+:)?infoTable>", re.S | re.I)
def tag(s, t):
    m = re.search(rf"<(?:\w+:)?{t}>\s*([^<]+?)\s*</(?:\w+:)?{t}>", s, re.I)
    return m.group(1) if m else None

def parse(path):
    txt = Path(path).read_text(errors="replace")
    pos = defaultdict(lambda: [0.0, 0.0])   # cusip -> [shares, value]
    for row in ROW.findall(txt):
        if (tag(row, "sshPrnamtType") or "SH").upper() != "SH":
            continue
        if tag(row, "putCall"):
            continue
        c, v, s = tag(row, "cusip"), tag(row, "value"), tag(row, "sshPrnamt")
        if not (c and v and s):
            continue
        try:
            pos[c][0] += float(s.replace(",", ""))
            pos[c][1] += float(v.replace(",", ""))
        except ValueError:
            continue
    return {c: tuple(x) for c, x in pos.items() if x[0] > 0 and x[1] > 0}

SPLITS = (2, 3, 4, 5, 6, 8, 10, 20)

def rebase_splits(prev, cur):
    out = {}
    for c, (s, v) in prev.items():
        if c in cur:
            r = cur[c][0] / s
            for k in SPLITS:
                if abs(r - k) / k < 0.02 or abs(r - 1 / k) * k < 0.02:
                    s = s * r
                    break
        out[c] = (s, v)
    return out

def turnover_shares(prev, cur, split_fix=False):
    if split_fix:
        prev = rebase_splits(prev, cur)
    price = {c: v / s for c, (s, v) in prev.items()}
    price.update({c: v / s for c, (s, v) in cur.items()})
    cs = set(prev) | set(cur)
    trade = sum(abs(cur.get(c, (0, 0))[0] - prev.get(c, (0, 0))[0]) * price[c] for c in cs)
    v_prev = sum(prev.get(c, (0, 0))[0] * price[c] for c in cs)
    v_cur = sum(cur.get(c, (0, 0))[0] * price[c] for c in cs)
    denom = 0.5 * (v_prev + v_cur)
    return 0.5 * trade / denom if denom > 0 else None

def turnover_weights(prev, cur):
    tp, tc = sum(v for _, v in prev.values()), sum(v for _, v in cur.values())
    cs = set(prev) | set(cur)
    return 0.5 * sum(abs(cur.get(c, (0, 0))[1] / tc - prev.get(c, (0, 0))[1] / tp) for c in cs)

def tdi(taus):
    lt = np.log(np.clip(taus, TAU_LO, TAU_HI))
    h, _ = np.histogram(lt, bins=np.linspace(0, math.log(TAU_HI), K + 1))
    p = h[h > 0] / h.sum()
    return float(-(p * np.log(p)).sum())

# per institution: quarter -> positions
tau_w, tau_s, tau_x = defaultdict(dict), defaultdict(dict), defaultdict(dict)
for d in sorted(glob.glob(str(CACHE / "filings" / "*"))):
    series = {}
    for fp in glob.glob(d + "/*"):
        name = Path(fp).name
        if "index" in name.lower():
            continue
        q = acc_q.get(name[:18])
        if q:
            pos = parse(fp)
            if pos:
                series[q] = pos          # later amendments overwrite
    qs = sorted(series)
    for i in range(1, len(qs)):
        a, b = qs[i - 1], qs[i]
        if (int(b[:4]) * 4 + int(b[5])) - (int(a[:4]) * 4 + int(a[5])) != 1:
            continue
        for store, fn in ((tau_w, turnover_weights), (tau_s, turnover_shares),
                          (tau_x, lambda p_, c_: turnover_shares(p_, c_, True))):
            t = fn(series[a], series[b])
            if t and t > 0.001:
                store[b][Path(d).name] = 63.0 / t

json.dump({'w': tau_w, 's': tau_s, 'x': tau_x}, open(ROOT / 'tau_by_inst_quarter.json', 'w'))
rows = []
for q in sorted(set(tau_w) & set(tau_s) & set(tau_x)):
    common = set(tau_w[q]) & set(tau_s[q]) & set(tau_x[q])
    if len(common) < 50:
        continue
    tw = np.array([tau_w[q][c] for c in common]); ts = np.array([tau_s[q][c] for c in common])
    tx = np.array([tau_x[q][c] for c in common])
    rows.append({"quarter": q, "n": len(common), "tdi_w": tdi(tw), "tdi_s": tdi(ts), "tdi_x": tdi(tx),
                 "med_tau_w": float(np.median(tw)), "med_tau_s": float(np.median(ts))})
df = pd.DataFrame(rows)

vix = yf.download("^VIX", start="2012-01-01", end="2027-01-01", interval="1mo",
                  progress=False, auto_adjust=True)["Close"]
vix = vix.iloc[:, 0] if hasattr(vix, "columns") else vix
vq = vix.dropna().groupby([f"{i.year}Q{(i.month - 1) // 3 + 1}" for i in vix.dropna().index]).mean()
df["vix"] = df["quarter"].map(vq)
df = df.dropna()
df.to_csv(ROOT / "price_adjusted_tdi_results.csv", index=False)
print(df.round(3).to_string(index=False))
print(f"\nn quarters = {len(df)}")
print(f"median tau: weight-based {df.med_tau_w.median():.1f}d, share-based {df.med_tau_s.median():.1f}d")

def vix_slope(col):
    lt = df.groupby("quarter")[col].mean()
    return stats.pearsonr(df[col], df["vix"])

for col, lab in (("tdi_w", "weight-based"), ("tdi_s", "share-based"), ("tdi_x", "share-based, splits rebased")):
    r, p = stats.pearsonr(df[col], df["vix"])
    print(f"\n[{lab}] r(TDI, VIX) = {r:+.3f}  p = {p:.4f}")
    m = VAR(df[[col, "vix"]].to_numpy()).fit(1)
    g1 = m.test_causality(0, [1], kind="f")   # VIX -> TDI
    g2 = m.test_causality(1, [0], kind="f")   # TDI -> VIX
    print(f"   VIX -> TDI: F={g1.test_statistic:.2f} p={g1.pvalue:.3f}   "
          f"TDI -> VIX: F={g2.test_statistic:.2f} p={g2.pvalue:.3f}")

# does VIX raise turnover itself, or only the weight-drift part?
df["drift_gap"] = np.log(df.med_tau_s) - np.log(df.med_tau_w)
r, p = stats.pearsonr(df["drift_gap"], df["vix"])
print(f"\nlog(median tau_share / tau_weight) vs VIX: r = {r:+.3f}, p = {p:.4f}")
