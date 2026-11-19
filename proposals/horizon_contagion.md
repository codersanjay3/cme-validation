# Proposal: Do investment horizons spread?

**Working title:** Horizon Contagion: How Trading Horizons Spread Through Institutional Portfolio Networks, and What It Does to Stock Fragility

**Status:** draft for discussion. Nothing in the paper changes because of this file.
**Author:** sumedh-agent (secondary agent), 2026-11-18. Name to be confirmed.
**Builds on:** the CME paper (`cme_frl_submission.tex`), `DECISIONS.md` baseline entry, `report/s7_tension.tex`.

---

## 1. The gap this study fills

The CME paper has two channels:

1. **Short-run channel (tested):** like-horizon investors cluster. The data confirm it: kappa-hat = 0.158, positive in all 50 quarters, Newey-West t = 19.
2. **Long-run channel (never tested):** investors *adapt* their horizon toward their neighbours' horizons, `tau_i <- (1 - eta) tau_i + eta * mean(tau of neighbours)`, which erodes horizon diversity over time ("temporal echo chambers").

The second channel is the paper's main story about fragility, but the adaptation rate `eta = 0.06` is assumed, not estimated, and nobody has checked whether real institutions adapt at all. The aggregate evidence that looked like support (TDI vs VIX) turned out to be price drift.

**The new study makes the long-run channel the object of study.** It asks whether trading horizons spread from institution to institution through portfolio-overlap networks, estimates how fast, and then tests whether that spread makes stocks more fragile.

### How this differs from the current paper
| | Current CME paper | This study |
|---|---|---|
| Main question | Does horizon clustering change volatility in a model? | Do horizons actually spread between real institutions, and does it matter? |
| Horizon adaptation | Assumed (`eta = 0.06`) | Estimated from 13F data |
| Unit of analysis | Simulated market; aggregate quarters; stock-quarters | Institution-quarter transitions in a network; stock-quarters in stress |
| Model's role | Main result | Disciplined by the empirical estimates, then tested out of sample |
| Fragility | Verbal (Fractal Market Hypothesis) | Tested through a named mechanism: who absorbs selling in a sell-off |

### How it differs from existing literature (to be verified by a literature search, step 0 below)
- Bushee (1998), Gaspar, Massa and Matos (2005), Cella, Ellul and Giannetti (2013) study the *level* of short-horizon ownership. They treat horizons as fixed traits.
- Hong, Kubik and Stein (2005) show fund managers in the same city trade alike (word of mouth). They study *what* is traded, not *how often*.
- Network peer-effects methods (Manski 1993; Bramoullé, Djebbari and Fortin 2009) are standard but, as far as we know, have not been applied to trading horizons.

The claim to novelty is: **horizon as a contagious behaviour**, measured with price-drift-free turnover, with a direct link back to a model parameter.

---

## 2. Research questions and pre-specified predictions

Signs are fixed now, before any outcome is looked at, following the practice in `stock_level_test.py`.

**RQ1. Horizon contagion.** Does an institution's horizon next quarter move toward the horizons of the institutions whose portfolios overlap with its own?
- Prediction: coefficient `b > 0` on neighbours' mean log tau, holding own log tau fixed.
- The implied quarterly adaptation rate is the empirical counterpart of `eta`.

**RQ2. Stress acceleration.** Is contagion faster in high-volatility quarters?
- Prediction: `b` is larger when VIX is high. This re-tests the paper's suggestive "volatility leads to horizon compression" result on the clean (share-based) measure.

**RQ3. Fragility through absorption.** In stress quarters (for example 2015Q3, 2018Q4, 2020Q1, 2022), do stocks with horizon-diverse holders have someone on the other side of the trade?
- Prediction A (absorption): within a stock, when short-horizon holders cut shares, long-horizon holders add shares, and more so when holder horizons are diverse.
- Prediction B (fragility): stocks whose holder horizons were clustered going into the stress quarter have larger drawdowns and slower recovery.
- This is a direct empirical test of Option B in `report/s7_tension.tex` (horizon-dependent liquidity) *before* any model change, which answers the "post-hoc model change" worry.

**RQ4. Disciplined model.** Replace `eta = 0.06` with the RQ1 estimate. If RQ3 supports absorption, add the Option B liquidity channel, calibrated on 2013 to 2019 only, and test whether the model's predictions hold on 2020 to 2026. This turns the model-data sign disagreement into a falsifiable out-of-sample test.

---

## 3. Design

### Data (all already produced by this project)
- `edgar_cache/holdings_db.json`: 13F holdings, 147 institutions, 2013Q2 to 2026Q1 (in the `data-v1` release).
- `tau_by_inst_quarter.json`: share-based horizons (`x`), split-rebased (`s`), value-weight (`w`).
- `stock_quarter_outcomes.csv`, `cusip_ticker.json`: stock outcomes for RQ3.

RQ1 and RQ2 use only holdings and horizons. **They need no price data, so the survivorship problem in the stock-level test does not affect them.**

### Feasibility (checked 2026-11-18 on `tau_by_inst_quarter.json`, share-based `x`)
| Quantity | Value |
|---|---|
| Institutions | 147 (median 133 per quarter) |
| Quarters | 50 |
| Institution-quarter transitions | 6,229 |
| SD of log tau, total | 0.92 |
| SD of log tau, within institution | 0.55 |
| Lag-1 autocorrelation of log tau | 0.75 |
| Share at the 2000-day cap | 10% |

Horizons are persistent but move a lot within institutions (60% of total spread), so there is variation to explain.

### RQ1 specification
```
log tau_{i,t+1} = a * log tau_{i,t} + b * NbrMean_{i,t} + controls + institution FE + quarter FE + e
```
- `NbrMean_{i,t}`: similarity-weighted mean log tau of i's neighbours, with neighbours and weights from **portfolio cosine similarity at t-1** (predetermined).
- Errors clustered two ways (institution, quarter); inference also by permutation (shuffle neighbour identities).

### Threats to identification and how we handle each
1. **Common shocks** (all institutions trade more in a crash): quarter fixed effects.
2. **Shared-stock shocks** (two neighbours both hold a stock that gets acquired or leaves an index, so both mechanically turn over): rebuild each neighbour's horizon from its trades **only in stocks i does not hold**. If contagion survives that, it is not a shared-stock artefact. This is the key design element.
3. **Reflection problem** (Manski): use neighbours-of-neighbours who are not i's neighbours as an instrument for `NbrMean` (Bramoullé, Djebbari and Fortin 2009).
4. **Regression to the mean**: own lagged log tau is in the regression; benchmark against randomly assigned neighbours drawn from the same horizon distribution.
5. **Nickell bias** (fixed effects with a lagged dependent variable): T = 50 keeps it small; check with a first-difference GMM estimator.
6. **Homophily vs influence** (similar institutions were already similar): placebo with *future* neighbours (institutions that become neighbours at t+4 but are not at t-1) should show no effect.
7. **Top-coding at 2000 days**: Tobit and drop-capped robustness.

### Kill criteria
We stop RQ1 and report a null if, on share-based horizons, `b` is not distinguishable from the random-neighbour benchmark, or if it disappears when neighbour horizons are built from non-overlapping stocks. A clean null is still informative: it would mean the paper's long-run channel has no empirical support, which the paper should say.

---

## 4. Work plan

| Step | What | Output |
|---|---|---|
| 0 | Literature search: horizon persistence, peer effects in fund trading, network peer-effects estimation | `proposals/lit_review.md` |
| 1 | Pre-registration: freeze specs, signs and kill criteria in this file before running | commit on this branch |
| 2 | Build institution network panel from holdings | `horizon_network_panel.py`, `.parquet` (not committed) |
| 3 | RQ1 baseline + threats 1 to 7 | `horizon_contagion.py`, `horizon_contagion_results.json` |
| 4 | RQ2 stress interaction | same script |
| 5 | RQ3 absorption and fragility | `stress_absorption.py`, results json |
| 6 | RQ4 recalibrated model, out-of-sample test | `cme_canonical.py` option, results json |
| 7 | Write-up as a separate paper | `paper2/` |

Every number goes through the project rules: script plus stored output, fixed seeds, `DECISIONS.md` entry.

---

## 5. Decisions needed from the team
1. Separate second paper (recommended, keeps the FRL submission clean) or a major revision of the current one.
2. Agent name for this collaborator (proposed: `sumedh-agent`).
3. OK to download the `data-v1` release (640 MB, expands to about 7.4 GB) on this machine.
4. Professor Chalmers's view on Option B is still pending; RQ3 gives an empirical answer either way.

## 6. Repository issues noticed while onboarding
- 21 of 31 scripts (including `cme_canonical.py` and `verify_numbers.py`) hard-code `/Users/sanjaysubramania/cme_validation`, so they only run on one machine. Should become a path relative to the script or an environment variable.
- `requirements.txt` needs numpy 2.1 or later, which needs Python 3.10 or later. macOS system Python is 3.9. Worth stating in `ONBOARDING.md`.
- `statsmodels` and `yfinance` are used but not listed in `requirements.txt`.
