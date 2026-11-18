"""
bond_by_type.py — Bond funds split by credit quality (Chalmers suggestion).

Funds: Vanguard Treasury (short/intermediate/long), investment-grade corporate
(short/intermediate/long), and high-yield corporate, from N-PORT filings.

For each fund and quarter we compute two horizon proxies:
  * WAM tau          = weighted average maturity * 252          (structural)
  * behavioural tau  = 63 / turnover, turnover from changes in PAR holdings
                       valued at one common price per bond (price moves cannot
                       create turnover); bonds that matured between the two
                       dates are excluded from the trade count.
Then correlate each with the MOVE index, by fund and by credit type.
"""
import json, re, ssl, time, math, urllib.request
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats
import yfinance as yf

ROOT = Path("/Users/sanjaysubramania/cme_validation")
CACHE = ROOT / "bond_cache"
ctx = ssl._create_unverified_context()
H = {"User-Agent": "research jaysubbu@gmail.com"}
CIK = 106444
TYPES = {
    "VANGUARD SHORT-TERM TREASURY FUND": "Treasury",
    "VANGUARD INTERMEDIATE-TERM TREASURY FUND": "Treasury",
    "VANGUARD LONG-TERM TREASURY FUND": "Treasury",
    "VANGUARD SHORT-TERM INVESTMENT-GRADE FUND": "Investment-grade corporate",
    "VANGUARD INTERMEDIATE-TERM INVESTMENT-GRADE FUND": "Investment-grade corporate",
    "VANGUARD LONG-TERM INVESTMENT-GRADE FUND": "Investment-grade corporate",
    "VANGUARD HIGH-YIELD CORPORATE FUND": "High-yield corporate",
}

def get(url):
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=90, context=ctx) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            time.sleep(2 + 3 * k)
    return None

def tag(s, t):
    m = re.search(rf"<{t}>\s*([^<]+?)\s*</{t}>", s)
    return m.group(1) if m else None

def parse(xml):
    rep = tag(xml, "repPdDate")
    pos = {}
    for blk in re.findall(r"<invstOrSec>(.*?)</invstOrSec>", xml, re.S):
        cus = re.search(r"<cusip>([^<]+)</cusip>", blk) or re.search(r'<isin value="([^"]+)"', blk)
        bal, val, mat = tag(blk, "balance"), tag(blk, "valUSD"), tag(blk, "maturityDt")
        units, pct = tag(blk, "units"), tag(blk, "pctVal")
        if not (cus and bal and val and units == "PA"):
            continue
        try:
            b, v = float(bal), float(val)
        except ValueError:
            continue
        if b > 0 and v > 0:
            key = cus.group(1)
            ob, ov, om, op = pos.get(key, (0, 0, mat, 0))
            pos[key] = (ob + b, ov + v, mat, op + float(pct or 0))
    return rep, pos

index = json.load(open(CACHE / "series_index.json"))["Vanguard"]
funds = {}
for name, typ in TYPES.items():
    rows = []
    for dt, acc, rp in index[name]:
        f = CACHE / f"{acc}.json"
        if f.exists():
            d = json.load(open(f))
        else:
            xml = get(f"https://www.sec.gov/Archives/edgar/data/{CIK}/{acc.replace('-', '')}/primary_doc.xml")
            if not xml:
                continue
            rep, pos = parse(xml)
            d = {"rep": rep, "pos": pos}
            json.dump(d, open(f, "w"))
            time.sleep(0.15)
        if d["rep"] and d["pos"]:
            rows.append((d["rep"], d["pos"]))
    rows = sorted({r[0]: r for r in rows}.values())
    funds[name] = rows
    print(f"{name}: {len(rows)} reports", flush=True)

def wam(pos, rep):
    r = datetime.strptime(rep, "%Y-%m-%d").date()
    num = den = 0.0
    for b, v, mat, pct in pos.values():
        try:
            days = (datetime.strptime(mat, "%Y-%m-%d").date() - r).days
        except (TypeError, ValueError):
            continue
        if 0 < days < 365 * 60:
            num += v * days; den += v
    return num / den / 365.25 if den else None

def turnover(prev, cur, rep_cur):
    price = {c: v / b for c, (b, v, _, _) in prev.items()}
    price.update({c: v / b for c, (b, v, _, _) in cur.items()})
    rc = datetime.strptime(rep_cur, "%Y-%m-%d").date()
    trade = v0 = v1 = 0.0
    for c in set(prev) | set(cur):
        b0 = prev.get(c, (0, 0, None, 0))[0]
        b1 = cur.get(c, (0, 0, None, 0))[0]
        mat = (prev.get(c) or cur.get(c))[2]
        try:
            if c not in cur and datetime.strptime(mat, "%Y-%m-%d").date() <= rc:
                continue   # matured, not traded
        except (TypeError, ValueError):
            pass
        trade += abs(b1 - b0) * price[c]
        v0 += b0 * price[c]; v1 += b1 * price[c]
    den = 0.5 * (v0 + v1)
    return 0.5 * trade / den if den else None

move = yf.download("^MOVE", start="2017-01-01", end="2027-01-01", interval="1mo",
                   progress=False, auto_adjust=True)["Close"]
move = move.iloc[:, 0] if hasattr(move, "columns") else move
mq = defaultdict(list)
for i, v in move.dropna().items():
    mq[f"{i.year}Q{(i.month - 1) // 3 + 1}"].append(float(v))
mq = {q: float(np.mean(v)) for q, v in mq.items()}

def q_of(rep):
    return f"{rep[:4]}Q{(int(rep[5:7]) - 1) // 3 + 1}"

table = defaultdict(list)   # type -> list of (quarter, wam_tau, beh_tau, move)
print(f"\n{'fund':52s} {'n':>3s} {'mean WAM(yr)':>12s} {'median tau_beh(d)':>18s} "
      f"{'r(WAM,MOVE)':>12s} {'r(tau_beh,MOVE)':>16s}")
for name, rows in funds.items():
    W, T, M = [], [], []
    for i in range(1, len(rows)):
        (r0, p0), (r1, p1) = rows[i - 1], rows[i]
        gap = (datetime.strptime(r1, "%Y-%m-%d") - datetime.strptime(r0, "%Y-%m-%d")).days
        if not 60 <= gap <= 125:
            continue
        to, w, mv = turnover(p0, p1, r1), wam(p1, r1), mq.get(q_of(r1))
        if to and to > 0.001 and w and mv:
            W.append(w); T.append(63.0 / to); M.append(mv)
            table[TYPES[name]].append((q_of(r1), w, 63.0 / to, mv, name))
    if len(M) >= 6:
        rw = stats.pearsonr(W, M); rt = stats.pearsonr(np.log(T), M)
        print(f"{name:52s} {len(M):3d} {np.mean(W):12.2f} {np.median(T):18.0f} "
              f"{rw[0]:+7.2f} (p={rw[1]:.2f}) {rt[0]:+7.2f} (p={rt[1]:.2f})")

print("\nBy credit type (fund-quarters pooled, quarter-demeaned within fund):")
for typ, rows in table.items():
    byfund = defaultdict(list)
    for q, w, t, m, n in rows:
        byfund[n].append((math.log(t), m, w))
    lt, mm, ww = [], [], []
    for n, v in byfund.items():
        a = np.array(v)
        lt += list(a[:, 0] - a[:, 0].mean()); mm += list(a[:, 1] - a[:, 1].mean()); ww += list(a[:, 2] - a[:, 2].mean())
    rt = stats.pearsonr(lt, mm); rw = stats.pearsonr(ww, mm)
    print(f"  {typ:28s} fund-quarters={len(mm):3d}  median tau_beh={np.median([r[2] for r in rows]):6.0f}d  "
          f"r(log tau_beh, MOVE)={rt[0]:+.2f} (p={rt[1]:.3f})  r(WAM, MOVE)={rw[0]:+.2f} (p={rw[1]:.3f})")
json.dump({t: [list(r) for r in v] for t, v in table.items()}, open(ROOT / "bond_by_type_results.json", "w"))
