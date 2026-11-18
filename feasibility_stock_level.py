"""Feasibility check for the stock-level horizon-concentration test."""
import json, random, time, ssl, urllib.request
from pathlib import Path
from collections import defaultdict
import yfinance as yf

ROOT = Path("/Users/sanjaysubramania/cme_validation")
db = json.load(open(ROOT / "edgar_cache" / "holdings_db.json"))

holders = defaultdict(lambda: defaultdict(int))   # cusip -> quarter -> n holders
value = defaultdict(lambda: defaultdict(float))
for cik, qs in db.items():
    for q, hs in qs.items():
        seen = set()
        for h in hs:
            c = h["cusip"]
            if c in seen:
                continue
            seen.add(c)
            holders[c][q] += 1
            value[c][q] += h["value_k"]

quarters = sorted({q for c in holders for q in holders[c]})
print("distinct CUSIPs ever held:", len(holders))
for q in ("2014Q2", "2019Q2", "2023Q2"):
    n = [holders[c].get(q, 0) for c in holders]
    print(q, "CUSIPs with >=1 holder:", sum(x >= 1 for x in n), " >=10:", sum(x >= 10 for x in n),
          " >=20:", sum(x >= 20 for x in n), " >=40:", sum(x >= 40 for x in n))

def n_quarters_with(c, k):
    return sum(v >= k for v in holders[c].values())
stable = [c for c in holders if n_quarters_with(c, 10) >= 30]
print("CUSIPs with >=10 holders in >=30 quarters:", len(stable))
print("CUSIP formats (9 chars):", sum(len(c) == 9 for c in stable), "of", len(stable))
json.dump(sorted(stable), open(ROOT / "stock_level_cusips.json", "w"))

# --- CUSIP -> ticker via OpenFIGI ---
random.seed(1)
sample = random.sample(stable, min(20, len(stable)))
ctx = ssl._create_unverified_context()
body = json.dumps([{"idType": "ID_CUSIP", "idValue": c} for c in sample]).encode()
req = urllib.request.Request("https://api.openfigi.com/v3/mapping", data=body,
                             headers={"Content-Type": "application/json"})
try:
    res = json.loads(urllib.request.urlopen(req, timeout=60, context=ctx).read())
    tick = {}
    for c, r in zip(sample, res):
        if "data" in r:
            us = [d for d in r["data"] if d.get("exchCode") == "US"] or r["data"]
            tick[c] = us[0].get("ticker")
    print("OpenFIGI mapped", len(tick), "of", len(sample), ":", list(tick.items())[:8])
except Exception as e:
    tick = {}
    print("OpenFIGI FAILED:", repr(e)[:200])

# --- returns via yfinance ---
ts = [t for t in tick.values() if t][:15]
if ts:
    t0 = time.time()
    px = yf.download(ts, start="2013-01-01", end="2025-01-01", interval="1d", progress=False, auto_adjust=True)["Close"]
    print("yfinance:", px.shape, "rows x tickers; non-empty tickers:", int(px.notna().any().sum()),
          f"in {time.time() - t0:.1f}s")
