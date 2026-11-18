"""Download daily adjusted closes for mapped tickers; build quarterly outcomes per ticker."""
import json, time
from pathlib import Path
import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path("/Users/sanjaysubramania/cme_validation")
m = json.load(open(ROOT / "cusip_ticker.json"))
tickers = sorted({t for t in m.values() if t})
print(len(tickers), "tickers", flush=True)

frames = []
for i in range(0, len(tickers), 100):
    b = tickers[i:i + 100]
    for attempt in range(3):
        try:
            px = yf.download(b, start="2012-10-01", end="2026-04-30", interval="1d",
                             progress=False, auto_adjust=True, threads=True)["Close"]
            break
        except Exception:
            time.sleep(10)
    else:
        continue
    if isinstance(px, pd.Series):
        px = px.to_frame(b[0])
    frames.append(px)
    print(i, px.shape, flush=True)
px = pd.concat(frames, axis=1)
px = px.loc[:, ~px.columns.duplicated()]
px.to_pickle(ROOT / "stock_prices.pkl")

ret = np.log(px).diff()
rows = []
q = ret.index.to_period("Q")
for per, g in ret.groupby(q):
    n = g.notna().sum()
    ok = n[n >= 50].index
    g = g[ok]
    for t in ok:
        r = g[t].dropna()
        rows.append({"quarter": f"{per.year}Q{per.quarter}", "ticker": t, "rv": float(r.std() * np.sqrt(252)),
                     "minret": float(r.min()), "skew": float(r.skew()), "ndays": len(r)})
pd.DataFrame(rows).to_csv(ROOT / "stock_quarter_outcomes.csv", index=False)
print("saved", len(rows), "ticker-quarters")
