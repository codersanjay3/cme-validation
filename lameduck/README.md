# lameduck/: retirement events for the lame-duck design

Planned portfolio-manager retirements announced in fund prospectus supplements
(SEC Forms 497 and 497K, 2019-10 to 2026-09), linked to N-PORT fund series through
filing-header SERIES-IDs. Outcomes have NOT been read by event time; everything here
is counts, so the design can still be pre-registered blind.

| Script | What it does | Output |
|---|---|---|
| `find_events.py` | EDGAR full-text search (11 retirement wordings with "portfolio manager", plus departure notices), PM-context filter, stated end date from the text, fallback end from a later departure filing | `results/lameduck_events.csv`, `results/lameduck_event_scope.json` |
| `test_find_events.py` | Fixture checks of the phrase, context and date rules (9/9) | stdout |
| `coverage.py` | Equity filter and pre / lame-duck / post report counts per event; power from whole-panel variance | `results/lameduck_coverage.json` |

Run from the repo root, `SEC_CONTACT_EMAIL` set: `python lameduck/find_events.py`
(about 3 hours cold; cached in `stage2_cache/`), then `python lameduck/coverage.py`
(needs `nport_panel_data/` from `nport_panel/build_fund_panel.py`).

## Numbers (2026-11-26)

- 4,082 retirement filings hit, 2,795 with PM context; 3,903 series events from
  1,015 announcements. All 462 Stage 2 retirement announcements are found again.
- End dates: 3,210 stated in the text, 71 from a later departure notice, 622 none.
- Equity funds: 484 announcements; 233 usable with a stated end (at least 2 pre,
  1 lame-duck and 2 post reports), 242 with stated or notice ends. Was 46.
- Filings naming at most 5 series (more precise; a header can list a whole trust):
  178 usable announcements, 2.45 lame-duck reports each on average.
- MDE (80% power, whole-panel sd 0.642, no serial correlation): 0.08 to 0.12 log
  points at N = 233, 0.10 to 0.14 at N = 178. Was 0.19 to 0.27 at N = 46.

## Known limits

- 90 announcements name 10 or more series (2,226 series events). The retiring
  manager may not run all of them. Pre-register the announcement as the unit and
  the at-most-5-series subset as a robustness check, or hand-check the wide filings.
- About 10% of stated ends fall before the filing date (completion notices);
  they drop out through the lame-duck count.
- Retirement can be endogenous to performance; the design compares the announced
  lame-duck window with the same fund's own pre period, and the stated date is set
  in advance.
