"""Map stable CUSIPs to tickers with OpenFIGI (keyless: 10 per request). Resumable."""
import json, ssl, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path("/Users/sanjaysubramania/cme_validation")
OUT = ROOT / "cusip_ticker.json"
ctx = ssl._create_unverified_context()
cusips = json.load(open(ROOT / "stock_level_cusips.json"))
done = json.load(open(OUT)) if OUT.exists() else {}
todo = [c for c in cusips if c not in done]
print(len(todo), "to map", flush=True)

for i in range(0, len(todo), 10):
    batch = todo[i:i + 10]
    body = json.dumps([{"idType": "ID_CUSIP", "idValue": c} for c in batch]).encode()
    req = urllib.request.Request("https://api.openfigi.com/v3/mapping", data=body,
                                 headers={"Content-Type": "application/json"})
    for attempt in range(6):
        try:
            res = json.loads(urllib.request.urlopen(req, timeout=60, context=ctx).read())
            break
        except urllib.error.HTTPError as e:
            time.sleep(30 if e.code == 429 else 5)
        except Exception:
            time.sleep(5)
    else:
        continue
    for c, r in zip(batch, res):
        d = [x for x in r.get("data", []) if x.get("exchCode") == "US" and x.get("securityType") in ("Common Stock", "ADR", "REIT")]
        done[c] = d[0]["ticker"] if d else None
    if (i // 10) % 20 == 0:
        json.dump(done, open(OUT, "w"))
        print(i, "mapped", sum(v is not None for v in done.values()), flush=True)
    time.sleep(2.6)
json.dump(done, open(OUT, "w"))
print("done:", sum(v is not None for v in done.values()), "of", len(done))
