"""
Stage 2 scoping: count candidate portfolio-manager shocks in SEC Form 497 supplements.

Free data only. Uses the EDGAR full-text search (efts.sec.gov, 2001+ filings, here
2019-10-01 to 2026-09-30 to match the N-PORT data sets), then fetches each hit's
document and filing header:
  - the document text gives a short window around the phrase, used to keep only
    supplements where the phrase sits next to "portfolio manager" language;
  - the header (.hdr.sgml) gives the SERIES-IDs, which are the same IDs as
    SERIES_ID in the N-PORT data sets, so each event links to the affected funds.

Run from the repo root (needs SEC_CONTACT_EMAIL):  python stage2/scope_events.py
Cache (gitignored): stage2_cache/. Outputs: results/stage2_event_scope.json and
results/stage2_events.csv (event list: type, month, trust, series; no text).
No randomness.
"""
import csv, html, json, os, re, sys, time, urllib.parse
from collections import defaultdict
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "stage2_cache"
START, END = "2019-10-01", "2026-09-30"
PAUSE = 0.25  # under the SEC limit of 10 requests per second

QUERIES = {
    "death": ['"passed away" "portfolio manager"', '"untimely death" "portfolio manager"',
              '"recent death" "portfolio manager"', '"untimely passing" "portfolio manager"',
              '"following the death" "portfolio manager"', '"due to the death" "portfolio manager"'],
    "retirement": ['"will retire" "portfolio manager"', '"announced his retirement" "portfolio manager"',
                   '"announced her retirement" "portfolio manager"', '"has retired" "portfolio manager"'],
    # counted only (not fetched): departures for any reason, the least exogenous kind
    "departure_any": ['"no longer serve as a portfolio manager"', '"no longer serves as a portfolio manager"'],
}
PHRASE = {"death": re.compile(r"passed away|untimely death|recent death|untimely passing|following the death|due to the death", re.I),
          "retirement": re.compile(r"will retire|announced (?:his|her) retirement|has retired", re.I)}
PM = re.compile(r"portfolio manager|co-portfolio|lead manager|manager of the fund", re.I)
NOT_PM = re.compile(r"\b(trustee|director of the (?:fund|trust)|board of (?:trustees|directors)|insured|annuitant|owner)\b", re.I)


def session():
    ua = os.environ.get("SEC_CONTACT_EMAIL")
    if not ua:
        sys.exit("Set SEC_CONTACT_EMAIL (see APIS.md).")
    s = requests.Session()
    s.headers["User-Agent"] = "CME-Validation " + ua
    return s


def cached_get(s, url, path, tries=4):
    if path.exists():
        return path.read_bytes()
    for t in range(tries):
        time.sleep(PAUSE * (1 + 3 * t))
        try:
            r = s.get(url, timeout=60)
        except requests.RequestException:
            continue
        if r.status_code == 200:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(r.content)
            return r.content
    return None


def years():
    for y in range(int(START[:4]), int(END[:4]) + 1):
        yield max(START, f"{y}-01-01"), min(END, f"{y}-12-31")


def search(s, q):
    """All hits for one query, sliced by year (large single queries return HTTP 500)."""
    hits, totals = {}, 0
    key = re.sub(r"\W+", "_", q).strip("_")
    for a, b in years():
        frm = 0
        while True:
            url = ("https://efts.sec.gov/LATEST/search-index?q=" + urllib.parse.quote(q)
                   + f"&forms=497&dateRange=custom&startdt={a}&enddt={b}&from={frm}")
            raw = cached_get(s, url, CACHE / "efts" / f"{key}_{a}_{frm}.json")
            if raw is None:
                print("  search failed:", q, a, frm); break
            d = json.loads(raw)["hits"]
            if frm == 0:
                totals += d["total"]["value"]
            for h in d["hits"]:
                hits[h["_id"]] = h["_source"]
            frm += len(d["hits"])
            if len(d["hits"]) < 100 or frm >= d["total"]["value"]:
                break
    return hits, totals


def doc_context(s, hid, src, kind):
    adsh, fn = hid.split(":", 1)
    cik = src["ciks"][0].lstrip("0")
    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{fn}"
    raw = cached_get(s, url, CACHE / "docs" / adsh / fn)
    if raw is None:
        return None
    txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw.decode("latin-1"))))
    wins = [txt[max(0, m.start() - 300): m.end() + 300] for m in PHRASE[kind].finditer(txt)]
    pm = [w for w in wins if PM.search(w) and not NOT_PM.search(w)]
    return {"n_windows": len(wins), "pm_windows": len(pm)}


def series_ids(s, adsh, cik):
    a = adsh.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{a}/{adsh}.hdr.sgml"
    raw = cached_get(s, url, CACHE / "hdr" / f"{adsh}.sgml")
    if raw is None:
        return None
    return sorted(set(re.findall(r"<SERIES-ID>(S\d{9})", raw.decode("latin-1"))))


def main():
    s = session()
    out = {"window": [START, END], "forms": "497", "queries": {}}
    filings = {}
    for kind, qs in QUERIES.items():
        allhits = {}
        for q in qs:
            h, tot = search(s, q)
            out["queries"][q] = {"kind": kind, "hits": tot}
            allhits.update(h)
            print(f"{kind:14s} {tot:6d}  {q}")
        out["queries"][kind + "_unique_filings"] = len({k.split(":")[0] for k in allhits})
        if kind == "departure_any":
            continue
        for hid, src in sorted(allhits.items()):
            adsh = hid.split(":")[0]
            ctx = doc_context(s, hid, src, kind)
            f = filings.setdefault((kind, adsh), {"kind": kind, "adsh": adsh, "date": src["file_date"],
                                                  "cik": src["ciks"][0], "trust": src["display_names"][0],
                                                  "pm_windows": 0, "fetched": False})
            if ctx:
                f["fetched"] = True
                f["pm_windows"] += ctx["pm_windows"]
    kept = [f for f in filings.values() if f["pm_windows"] > 0]
    for f in kept:
        f["series"] = series_ids(s, f["adsh"], f["cik"]) or []
    # events: one per (kind, series); repeated supplements within 365 days are the same event
    ev = []
    by_series = defaultdict(list)
    for f in sorted(kept, key=lambda f: f["date"]):
        for sid in f["series"] or [f"trust:{f['cik']}"]:
            by_series[(f["kind"], sid)].append(f)
    for (kind, sid), fs in by_series.items():
        last = None
        for f in fs:
            if last is None or (int(f["date"][:4]) * 12 + int(f["date"][5:7])) - last > 12:
                ev.append({"kind": kind, "month": f["date"][:7], "series_id": sid, "trust_cik": f["cik"],
                           "trust": re.sub(r"\s*\(CIK \d+\)", "", f["trust"]), "adsh": f["adsh"]})
                last = int(f["date"][:4]) * 12 + int(f["date"][5:7])
    for kind in ("death", "retirement"):
        fk = [f for f in filings.values() if f["kind"] == kind]
        ek = [e for e in ev if e["kind"] == kind]
        out[kind] = {"filings_hit": len(fk), "filings_fetched": sum(f["fetched"] for f in fk),
                     "filings_pm_context": sum(f["pm_windows"] > 0 for f in fk),
                     "trusts_pm_context": len({f["cik"] for f in fk if f["pm_windows"] > 0}),
                     "fund_series_events": len(ek),
                     "events_by_year": dict(sorted(defaultdict(int, {}).items()))}
        yrs = defaultdict(int)
        for e in ek:
            yrs[e["month"][:4]] += 1
        out[kind]["events_by_year"] = dict(sorted(yrs.items()))
    (ROOT / "results").mkdir(exist_ok=True)
    json.dump(out, open(ROOT / "results" / "stage2_event_scope.json", "w"), indent=1)
    with open(ROOT / "results" / "stage2_events.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["kind", "month", "series_id", "trust_cik", "trust", "adsh"])
        w.writeheader(); w.writerows(sorted(ev, key=lambda e: (e["kind"], e["month"], e["series_id"])))
    print(json.dumps({k: v for k, v in out.items() if k != "queries"}, indent=1))


if __name__ == "__main__":
    main()
