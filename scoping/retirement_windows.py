"""
Idea scoping ("lame-duck managers"): how long is the window between a retirement
announcement (Form 497 filing date) and the stated retirement date?

Reads the 497 documents cached by stage2/scope_events.py (stage2_cache/docs, gitignored)
for every retirement announcement (results/stage2_events.csv) and extracts the first date within 250 characters
after a retirement phrase ("will retire ... effective/on/as of <Month day, year>",
"retire at the end of <Month year>", "retire ... <year>").

Run from the repo root:  python scoping/retirement_windows.py
Outputs: results/scoping_retirement_windows.json (summary on announcements touching a
fund in nport_cache/equity_series_2023q1.csv, as in round 2, plus counts for all),
results/scoping_retirement_dates.csv (every announcement). No randomness.
"""
import html, json, re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "stage2_cache" / "docs"
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
PHRASE = re.compile(r"will retire|announced (?:his|her) retirement|intends to retire|plans to retire", re.I)
FULL = re.compile(rf"({MONTHS})\s+(\d{{1,2}}),?\s+(20\d\d)")
MONTH_YEAR = re.compile(rf"(?:end of|in|by)\s+(?:the\s+)?({MONTHS})\s+(20\d\d)")
QUARTER = re.compile(r"(?:end of|in|by)\s+(?:the\s+)?(first|second|third|fourth)\s+quarter\s+of\s+(20\d\d)", re.I)
YEAR_END = re.compile(r"(?:end of|by)\s+(20\d\d)")

ev = pd.read_csv(ROOT / "results" / "stage2_events.csv", dtype=str)
eq = pd.concat([pd.read_csv(p, dtype=str) for p in [ROOT / "nport_cache" / "equity_series_2023q1.csv"]])
ev = ev[ev.kind == "retirement"]
eq_adsh = set(ev[ev.series_id.isin(eq.SERIES_ID)].adsh)   # summary subset (unchanged since round 2)
ann = ev.drop_duplicates("adsh")[["adsh", "month", "trust"]]   # dates extracted for every announcement


def stated_date(text):
    for m in PHRASE.finditer(text):
        win = text[m.end(): m.end() + 250]
        if (d := FULL.search(win)):
            return pd.Timestamp(f"{d.group(1)} {d.group(2)} {d.group(3)}"), "day"
        if (d := MONTH_YEAR.search(win)):
            return pd.Timestamp(f"{d.group(1)} 1 {d.group(2)}") + pd.offsets.MonthEnd(0), "month"
        if (d := QUARTER.search(win)):
            q = ["first", "second", "third", "fourth"].index(d.group(1).lower()) + 1
            return pd.Timestamp(f"{d.group(2)}-{3 * q:02d}-01") + pd.offsets.MonthEnd(0), "quarter"
        if (d := YEAR_END.search(win)):
            return pd.Timestamp(f"{d.group(1)}-12-31"), "year"
    return None, None


rows = []
for a in ann.itertuples():
    d = DOCS / a.adsh
    best = (None, None)
    for f in sorted(d.glob("*")) if d.exists() else []:
        t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", f.read_bytes().decode("latin-1"))))
        best = stated_date(t)
        if best[0] is not None:
            break
    filed = pd.Timestamp(a.month + "-15")
    lag = (best[0] - filed).days / 30.44 if best[0] is not None else None
    rows.append({"adsh": a.adsh, "filed_month": a.month, "stated": best[0], "precision": best[1], "lag_months": lag})
r_all = pd.DataFrame(rows)
r = r_all[r_all.adsh.isin(eq_adsh)]
ok = r[r.lag_months.between(-1, 36)]
out = {
    "announcements_on_equity_funds": int(len(r)),
    "stated_date_found": int(r.stated.notna().sum()),
    "precision": r.precision.value_counts().to_dict(),
    "lag_months_quantiles": {str(q): round(float(ok.lag_months.quantile(q)), 1) for q in (0.1, 0.25, 0.5, 0.75, 0.9)},
    "share_lag_at_least_3_months": round(float((ok.lag_months >= 3).mean()), 3),
    "share_lag_at_least_6_months": round(float((ok.lag_months >= 6).mean()), 3),
    "lag_outside_minus1_to_36_months": int(r.lag_months.notna().sum() - len(ok)),
    "all_retirement_announcements": int(len(r_all)),
    "all_stated_date_found": int(r_all.stated.notna().sum()),
}
json.dump(out, open(ROOT / "results" / "scoping_retirement_windows.json", "w"), indent=1)
r_all.to_csv(ROOT / "results" / "scoping_retirement_dates.csv", index=False)  # per announcement, no text
print(json.dumps(out, indent=1))
