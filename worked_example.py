"""
worked_example.py — Show, for two real institutions in one quarter, exactly what
the data look like and how tau, horizon proximity, cosine similarity are built.
Used for the "what does the data look like" slide.
"""
import json, math, sys
from pathlib import Path

ROOT = Path("/Users/sanjaysubramania/cme_validation")
Q = sys.argv[1] if len(sys.argv) > 1 else "2019Q2"

db = json.load(open(ROOT / "edgar_cache" / "holdings_db.json"))

def weights(h):
    tot = sum(x["value_k"] for x in h)
    out = {}
    for x in h:
        out[x["cusip"]] = out.get(x["cusip"], 0) + x["value_k"] / tot
    return out

def prev_q(q):
    y, n = int(q[:4]), int(q[5])
    return f"{y-1}Q4" if n == 1 else f"{y}Q{n-1}"

def tau(cik):
    a, b = db[cik].get(Q), db[cik].get(prev_q(Q))
    if not a or not b:
        return None, None
    w2, w1 = weights(a), weights(b)
    to = sum(abs(w1.get(c, 0) - w2.get(c, 0)) for c in set(w1) | set(w2)) / 2
    return (63.0 / to, to) if to > 0.001 else (None, None)

cands = []
for cik in db:
    t, to = tau(cik)
    if t:
        cands.append((t, cik, to))
cands.sort()
fast, slow = cands[len(cands) // 10], cands[-len(cands) // 10]
trio = [fast, cands[len(cands) // 2], slow]

def show(label, t, cik, to):
    w = weights(db[cik][Q])
    top = sorted(w.items(), key=lambda kv: -kv[1])[:5]
    print(f"\n{label}: filer CIK {cik}   quarter {Q}")
    print(f"  positions held: {len(w)}")
    print(f"  portfolio turnover vs last quarter: {to:.1%}  ->  tau = 63 / {to:.3f} = {t:.0f} trading days")
    print("  five largest holdings (CUSIP, share of portfolio value):")
    for c, x in top:
        print(f"     {c}   {x:.2%}")

labels = ["Fast trader", "Middle trader", "Slow trader"]
for lab, (t, cik, to) in zip(labels, trio):
    show(lab, t, cik, to)

def cos(w1, w2):
    com = set(w1) & set(w2)
    d = sum(w1[c] * w2[c] for c in com)
    return d / (math.sqrt(sum(v * v for v in w1.values())) * math.sqrt(sum(v * v for v in w2.values()))), len(com)

print("\nPairs:")
for i in range(3):
    for j in range(i + 1, 3):
        (ti, ci, _), (tj, cj, _) = trio[i], trio[j]
        s, n = cos(weights(db[ci][Q]), weights(db[cj][Q]))
        prox = math.exp(-abs(math.log(ti + 1) - math.log(tj + 1)))
        print(f"  {labels[i]} vs {labels[j]}: shared holdings = {n}, "
              f"portfolio similarity (cosine) = {s:.3f}, horizon proximity = {prox:.3f}")
print("\nkappa-hat for the quarter = correlation of these two numbers across ALL institution pairs.")
