# Stage 2 feasibility: neighbour manager shocks with free SEC data (2026-11-19)

Question: can the identification step of idea 1 (horizon contagion, `docs/novelty-audit/IDEAS.md`) be built from free SEC data, and does it clear the decision rule ("switch to idea 2 if fewer than about 30 usable neighbour manager shocks exist")?

Short answer: **the data exist and link. Manager deaths fail the count gate (6 announcements on equity funds); retirements pass it (231), but a single-neighbour shock design is badly underpowered either way.** The count gate was the wrong test. At the Stage 1 effect size, a design built on single-neighbour manager shocks cannot detect anything unless the causal effect is many times larger than the Stage 1 association. Details and options below. No Stage 2 coefficient has been estimated; nothing here is pre-registered yet.

Scripts (branch `sumedh-agent/stage2-nport`), all deterministic:

| Script | Output |
|---|---|
| `stage2/download_nport.py` | `nport_cache/` (gitignored) with sha256 manifest |
| `stage2/nport_coverage.py` | `results/stage2_nport_coverage.json` |
| `stage2/scope_events.py` | `results/stage2_event_scope.json`, `results/stage2_events.csv` |
| `stage2/link_events.py` | `results/stage2_event_link.json` |
| `stage2/power.py` | `results/stage2_power.json` |

## 1. Fund holdings: N-PORT data sets (usable)

- 28 quarterly zips, 2019Q4 to 2026Q3, 240 to 480 MB each (about 11 GB in all).
- One quarter (2023Q1) inspected: 12,519 filings (120 amendments), 11,717 fund series, 1,931 registrants.
- `FUND_REPORTED_HOLDING` has CUSIP, `BALANCE` with unit (`NS` = number of shares), dollar value, and asset category; `FUND_REPORTED_INFO` has `SERIES_ID`, net assets and monthly flows. Share counts allow the same share-based turnover as the 13F rebuild.
- 1.79 million common-stock rows in shares, of which 1.15 million (64%) carry a valid CUSIP. Most of the rest appear to be foreign listings identified by ISIN, which can be handled through the `IDENTIFIERS` table.
- Equity funds (at least 80% of reported value in common stock, at least 20 stocks): 6,478; 4,447 with net assets of at least 100 million dollars; median 75 stocks.
- Report dates are staggered by fiscal quarter (in this file: 2,482 November, 6,556 December, 3,377 January period ends). Each fund still has one report per quarter, so fund turnover between consecutive reports is well defined; neighbour networks need a calendar-quarter alignment rule.
- Limits: holdings start at 2019Q4 (no free structured fund holdings before that), so the Stage 2 window is about 26 quarterly transitions, against 52 in the 13F panel.

## 2. Manager shocks: Form 497 supplements via EDGAR full-text search (usable, counts below)

N-PORT and N-CEN do not name portfolio managers. Funds announce manager deaths, retirements and departures in prospectus supplements (Form 497). The EDGAR full-text search covers them; each filing's header lists the affected `SERIES-ID`s, which are the same IDs as `SERIES_ID` in N-PORT, so events link to funds without any name matching.

Rules (in `stage2/scope_events.py`): queries pair the event phrase with "portfolio manager"; the document is fetched and kept only if a 600-character window around the phrase mentions portfolio-manager language and does not mention trustees, directors, insured persons or annuitants (life-insurance and board wording are the main false positives; "has died" alone is almost all insurance wording). Repeated supplements for the same series within 12 months count as one event.

Window 2019-10-01 to 2026-09-30, Form 497 (`results/stage2_event_scope.json`, `results/stage2_event_link.json`; equity status from the 2023Q1 N-PORT file only, so the equity counts are lower bounds):

| | Deaths | Retirements | Departures, any reason |
|---|---|---|---|
| Search hits (filings) | 1,773 | 748 | 1,808 (counted only) |
| Kept: phrase next to portfolio-manager language | 14 filings, 10 trusts | 670 filings, 222 trusts | |
| Fund-series events | 30 | 1,896 | |
| On N-PORT equity funds | 17 series, **6 announcements**, 6 trusts | 938 series, **231 announcements**, 129 trusts | |
| On equity funds with net assets of at least 100 million dollars | 11 | 821 | |

- **Deaths do not pass even the count gate.** Most "passed away" hits concern trustees or directors (30 of 46 have no portfolio-manager language near the phrase; the exclusion list removed only 2 more), and "following the death" or "due to the death" is almost always redemption or insurance wording. Six announcements on equity funds is far below 30.
- **Retirements pass the count gate easily** (231 announcements, 938 equity-fund series, rising over time: 27 in late 2019 to 243 in 2025). They are planned and age-driven, so plausibly unrelated to the quarter's market conditions, but they are announced months ahead and often come with a hand-over period, so the shock is anticipated and gradual.
- Departures for any reason are more numerous but follow poor performance, which overlapping neighbours share; they fail the exclusion argument.
- Several series in one announcement share a manager, so the 938 retirement series are about 231 independent shocks for inference.

## 3. Power: the binding constraint

In the Stage 1 design an institution's peer variable is the equal-weighted mean horizon of its k = 10 neighbours. A manager shock to one neighbour j that changes j's log horizon by delta moves the focal fund's peer variable by delta / 10. At the Stage 1 coefficient (b = 0.032) the expected response of an exposed fund is 0.032 x delta / 10, about 0.0016 log points for delta = 0.5, against a within standard deviation of the outcome of 0.46.

Minimum detectable peer coefficient (5% two-sided, 80% power, 10 exposed funds per shock, independent observations, which is optimistic):

| Shocks | First-stage delta | MDE of b | MDE / Stage 1 b |
|---|---|---|---|
| 30 | 0.5 | 1.49 | 46x |
| 100 | 0.5 | 0.82 | 25x |
| 300 | 0.5 | 0.47 | 15x |
| 1,000 | 0.5 | 0.26 | 8x |
| 1,000 | 1.0 | 0.13 | 4x |
| 3,000 | 1.0 | 0.075 | 2.3x |

(`results/stage2_power.json` has the full grid.)

So a single-neighbour shock design can only find an effect if the causal coefficient is several times the Stage 1 association. That is possible in principle (Stage 1 is attenuated by measurement error in the neighbour horizon, which an instrument removes), but no design should rest on it.

## 4. What this means for the decision rule

The rule asked for at least about 30 usable shocks. That threshold came from the count, not from power, and it is far too low: even 3,000 shocks with a large first stage only reach 2.3x the Stage 1 slope. Options, in order of preference:

1. **Switch the headline to idea 2 (within-stock absorption of short-horizon selling in stress), as the decision rule already allows, and keep Stage 1 as a descriptive section.** Stage 0 and Stage 1 carry over; the rebuilt stock-level slope (issue #5) is the starting point. Recommended.
2. **Keep idea 1 but change the shock so it moves many neighbours at once.** The peer variable moves by delta / k only because one of k neighbours is hit. Shocks that change the horizons of a large share of a fund's neighbours (for example fund-family mergers or adviser replacements that re-staff many funds together, from N-CEN adviser fields) would move it by close to delta. These run into the merger critiques already noted (Lewellen-Lowry 2021; Massa-Schumacher-Wang 2021) and need their own scoping.
3. **Use retirements only as a first-stage result.** Showing that a fund's horizon moves after its manager retires (231 announcements, enough for a first stage) supports the premise that horizons are set by people rather than fixed fund traits, and feeds the calibrated model (idea 4). It does not identify peer effects.
4. **Run the retirement reduced form anyway as a bound.** With about 231 independent shocks it can rule out only very large peer coefficients (roughly 15x to 25x the Stage 1 slope at a first stage of 0.5). Worth reporting only as an upper bound.

Not recommended: claiming identification from deaths (6 events) or from all departures (performance-driven).

## 5. What was not checked

- The first stage (how much a fund's own horizon moves after its manager dies or retires) needs the multi-quarter N-PORT fund panel; only one quarter was downloaded. Earlier work on fund manager replacement reports higher portfolio turnover after a change (for example Khorana, JFQA 2001), which would give a predictable sign, but its size here is unknown.
- Event classification is by keyword window, not by reading each filing; a manual pass over the death events is needed before any estimate.
- Announcement dates are used; retirements are often announced months before the effective date.

**Update 2026-11-22 (split-rule fix, bead cme-d0m):** after the 13F split rule was fixed and Stage 1 rerun, the Stage 1 slope is 0.031 (was 0.032) and the within SD of the outcome is 0.47 (was 0.46). `results/stage2_power.json` was regenerated: 300 shocks at a first stage of 0.5 now need 15.4x the Stage 1 slope (was 14.5x); 3,000 shocks at 1.0 need 2.4x (was 2.3x). The conclusion is unchanged.
