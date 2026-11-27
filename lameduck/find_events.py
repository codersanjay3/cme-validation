"""
find_events.py: portfolio-manager retirement events for the lame-duck design,
grown from the Stage 2 search (stage2/scope_events.py, left unchanged).

What is added over Stage 2:
1. Forms 497 AND 497K (summary-prospectus supplements; most trusts file both).
2. More retirement wordings: "will retire", "intends to retire", "plans to retire",
   "expected to retire", "expects to retire", "will be retiring", "intention to
   retire", "announced his/her retirement", "retirement from", "has retired".
3. Stated end dates read from the text: a date in the 300 characters after the
   phrase (full date, "on or about", month and year, quarter, year end), else
   "Effective <date>" in the 200 characters before it.
4. A fallback end for undated announcements: the first later filing for the same
   fund series that says a manager "has retired" or "no longer serves as a
   portfolio manager" (filing date = upper bound on the retirement date).

Same filters as Stage 2: the phrase must sit within 300 characters of
portfolio-manager wording and not of trustee/director/insurance wording.
Events: one per fund series per 12 months (first filing = announcement).
Whether an event leaves a lame-duck window is decided later from its dates
(lameduck/coverage.py), so completion notices drop out there.

Run from the repo root (needs SEC_CONTACT_EMAIL): python lameduck/find_events.py
Cache (gitignored, shared with Stage 2): stage2_cache/. Outputs:
results/lameduck_events.csv (no text), results/lameduck_event_scope.json. No randomness.
"""
import csv, html, json, os, re, sys, time, urllib.parse
from collections import defaultdict
from pathlib import Path
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "stage2_cache"
START, END = "2019-10-01", "2026-09-30"
FORMS = "497,497K"
PAUSE = 0.25

RETIRE_Q = ['"will retire" "portfolio manager"', '"intends to retire" "portfolio manager"',
            '"plans to retire" "portfolio manager"', '"expected to retire" "portfolio manager"',
            '"expects to retire" "portfolio manager"', '"will be retiring" "portfolio manager"',
            '"intention to retire" "portfolio manager"', '"announced his retirement" "portfolio manager"',
            '"announced her retirement" "portfolio manager"', '"retirement from" "portfolio manager"',
            '"has retired" "portfolio manager"']
DEPART_Q = ['"no longer serve as a portfolio manager"', '"no longer serves as a portfolio manager"']
PHRASE = re.compile(r"will retire|intends to retire|plans to retire|expected to retire|expects to retire|"
                    r"will be retiring|intention to retire|announced (?:his|her|their) retirement|"
                    r"retirement from|has retired", re.I)
PM = re.compile(r"portfolio manager|co-portfolio|lead manager|manager of the fund", re.I)
NOT_PM = re.compile(r"\b(trustee|director of the (?:fund|trust)|board of (?:trustees|directors)|insured|annuitant|owner)\b", re.I)

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
FULL = re.compile(rf"({MONTHS})\s+(\d{{1,2}}),?\s+(20\d\d)")
MONTH_YEAR = re.compile(rf"\b({MONTHS})\s+(?:of\s+)?(20\d\d)\b")
QUARTER = re.compile(r"(first|second|third|fourth)\s+quarter\s+of\s+(20\d\d)", re.I)
YEAR_END = re.compile(r"(?:end of|by|year[- ]end|close of)\s+(?:calendar\s+)?(?:year\s+)?(20\d\d)|(20\d\d)\s+year[- ]end", re.I)
EFFECTIVE_BEFORE = re.compile(rf"effective\s+(?:as of\s+)?(?:the close of business on\s+)?({MONTHS})\s+(\d{{1,2}}),?\s+(20\d\d)", re.I)


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
    hits, total = {}, 0
    key = "ld_" + re.sub(r"\W+", "_", q).strip("_")
    for a, b in years():
        frm = 0
        while True:
            url = ("https://efts.sec.gov/LATEST/search-index?q=" + urllib.parse.quote(q)
                   + f"&forms={urllib.parse.quote(FORMS)}&dateRange=custom&startdt={a}&enddt={b}&from={frm}")
            raw = cached_get(s, url, CACHE / "efts" / f"{key}_{a}_{frm}.json")
            if raw is None:
                print("  search failed:", q, a, frm, flush=True); break
            d = json.loads(raw)["hits"]
            if frm == 0:
                total += d["total"]["value"]
            for h in d["hits"]:
                hits[h["_id"]] = h["_source"]
            frm += len(d["hits"])
            if len(d["hits"]) < 100 or frm >= d["total"]["value"]:
                break
    return hits, total


def text_of(raw):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw.decode("latin-1"))))


def stated_end(txt):
    """First stated retirement date next to a PM-context retirement phrase: (date, precision) or (None, None)."""
    for m in PHRASE.finditer(txt):
        ctx = txt[max(0, m.start() - 300): m.end() + 300]
        if not PM.search(ctx) or NOT_PM.search(ctx):
            continue
        post = txt[m.end(): m.end() + 300]
        if (d := FULL.search(post)):
            return pd.Timestamp(f"{d.group(1)} {d.group(2)} {d.group(3)}"), "day"
        if (d := MONTH_YEAR.search(post)):
            return pd.Timestamp(f"{d.group(1)} 1 {d.group(2)}") + pd.offsets.MonthEnd(0), "month"
        if (d := QUARTER.search(post)):
            q = ["first", "second", "third", "fourth"].index(d.group(1).lower()) + 1
            return pd.Timestamp(f"{d.group(2)}-{3 * q:02d}-01") + pd.offsets.MonthEnd(0), "quarter"
        if (d := YEAR_END.search(post)):
            return pd.Timestamp(f"{d.group(1) or d.group(2)}-12-31"), "year"
        pre = txt[max(0, m.start() - 200): m.start()]
        if (d := list(EFFECTIVE_BEFORE.finditer(pre))):
            d = d[-1]
            return pd.Timestamp(f"{d.group(1)} {d.group(2)} {d.group(3)}"), "day_effective_before"
    return None, None


def pm_context(txt):
    for m in PHRASE.finditer(txt):
        ctx = txt[max(0, m.start() - 300): m.end() + 300]
        if PM.search(ctx) and not NOT_PM.search(ctx):
            return True
    return False


def series_ids(s, adsh, cik):
    a = adsh.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{a}/{adsh}.hdr.sgml"
    raw = cached_get(s, url, CACHE / "hdr" / f"{adsh}.sgml")
    return sorted(set(re.findall(r"<SERIES-ID>(S\d{9})", raw.decode("latin-1")))) if raw else None


def main():
    s = session()
    scope = {"window": [START, END], "forms": FORMS, "queries": {}}
    rhits = {}
    for q in RETIRE_Q:
        h, tot = search(s, q); rhits.update(h); scope["queries"][q] = tot
        print(f"{tot:6d}  {q}", flush=True)
    dhits = {}
    for q in DEPART_Q:
        h, tot = search(s, q); dhits.update(h); scope["queries"][q] = tot
        print(f"{tot:6d}  {q}", flush=True)

    # retirement filings: read each document, keep PM context, take the first stated date
    fil = {}
    for n, (hid, src) in enumerate(sorted(rhits.items())):
        adsh, fn = hid.split(":", 1)
        cik = src["ciks"][0]
        raw = cached_get(s, f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{adsh.replace('-', '')}/{fn}",
                         CACHE / "docs" / adsh / fn)
        f = fil.setdefault(adsh, {"adsh": adsh, "filed": src["file_date"], "form": src.get("form", ""), "cik": cik,
                                  "pm": False, "end": None, "precision": None})
        if raw is not None:
            txt = text_of(raw)
            if pm_context(txt):
                f["pm"] = True
                if f["end"] is None:
                    f["end"], f["precision"] = stated_end(txt)
        if n % 500 == 0:
            print(f"  docs {n}/{len(rhits)}", flush=True)
    kept = [f for f in fil.values() if f["pm"]]
    for n, f in enumerate(kept):
        f["series"] = series_ids(s, f["adsh"], f["cik"]) or []
        if n % 500 == 0:
            print(f"  headers {n}/{len(kept)}", flush=True)

    # departure / completion notices: headers only (series and filing date)
    dep = defaultdict(list)
    dfil = {h.split(":")[0]: src for h, src in dhits.items()}
    for n, (adsh, src) in enumerate(sorted(dfil.items())):
        for sid in series_ids(s, adsh, src["ciks"][0]) or []:
            dep[sid].append(pd.Timestamp(src["file_date"]))
        if n % 500 == 0:
            print(f"  departure headers {n}/{len(dfil)}", flush=True)

    # events: one per series per 12 months; end = first stated date in the cluster,
    # else the first later departure/retirement filing for that series (within 24 months)
    by_series = defaultdict(list)
    for f in sorted(kept, key=lambda f: (f["filed"], f["adsh"])):
        for sid in f["series"]:
            by_series[sid].append(f)
    ev = []
    for sid, fs in by_series.items():
        clusters, cur = [], []
        for f in fs:
            if cur and (pd.Timestamp(f["filed"]) - pd.Timestamp(cur[0]["filed"])).days > 365:
                clusters.append(cur); cur = []
            cur.append(f)
        clusters.append(cur)
        for c in clusters:
            ann = pd.Timestamp(c[0]["filed"])
            end, prec, src_ = None, None, None
            for f in c:
                if f["end"] is not None and f["end"] >= ann - pd.Timedelta(days=31):
                    end, prec, src_ = f["end"], f["precision"], "stated"
                    break
            if end is None:
                later = sorted(d for d in dep[sid] if ann + pd.Timedelta(days=45) <= d <= ann + pd.Timedelta(days=730))
                if later:
                    end, prec, src_ = later[0], "filing", "later_notice"
            ev.append({"series_id": sid, "adsh": c[0]["adsh"], "filed": ann.date().isoformat(),
                       "form": c[0]["form"], "trust_cik": c[0]["cik"], "n_filings": len(c),
                       "end": end.date().isoformat() if end is not None else "", "precision": prec or "",
                       "end_source": src_ or ""})
    ev.sort(key=lambda e: (e["filed"], e["series_id"]))
    with open(ROOT / "results" / "lameduck_events.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ev[0]))
        w.writeheader(); w.writerows(ev)
    e = pd.DataFrame(ev)
    scope.update({
        "retirement_filings_hit": len(fil), "retirement_filings_pm_context": len(kept),
        "departure_filings_hit": len(dfil),
        "series_events": int(len(e)), "announcements": int(e.adsh.nunique()),
        "series_events_by_end_source": e.end_source.replace("", "none").value_counts().to_dict(),
        "stated_precision": e[e.end_source == "stated"].precision.value_counts().to_dict(),
        "stage2_announcements_covered": None,
    })
    s2 = ROOT / "results" / "stage2_events.csv"
    if s2.exists():
        old = pd.read_csv(s2, dtype=str)
        old = old[old.kind == "retirement"]
        scope["stage2_announcements_covered"] = {"stage2_retirement_announcements": int(old.adsh.nunique()),
                                                 "found_again": int(old.adsh.isin(set(f["adsh"] for f in kept)).groupby(old.adsh).first().sum())}
    json.dump(scope, open(ROOT / "results" / "lameduck_event_scope.json", "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in scope.items() if k != "queries"}, indent=1, default=str))


if __name__ == "__main__":
    main()
