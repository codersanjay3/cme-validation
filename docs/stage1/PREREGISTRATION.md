# Stage 1 pre-registration: horizon contagion, descriptive test

Committed before any peer coefficient was estimated. The git commit time of this file is the registration time. Any change after estimation is logged at the bottom with a reason, and the original text stays.

Context: idea 1 in `docs/novelty-audit/IDEAS.md` (branch `sumedh-agent/novelty-audit`). Data: the full-universe panel from `rebuild_13f/` (release `data-rebuild-v1`).

## Question

Does an institution's investment horizon move toward the horizons of the institutions whose portfolios overlap with its own?

Stage 1 is descriptive. A positive Stage 1b coefficient is a necessary condition for the paper, not evidence of contagion: Stage 2 (neighbour manager shocks) is what identifies it.

## Sample

- Institution-quarters in `panel_13f/tau.parquet` with `tau_split` defined, at least 20 positions in both t-1 and t, and AUM of at least 100 million dollars.
- Periods: transitions 2013Q3 to 2026Q2 (outcome quarters up to 2026Q2).

## Variables

- **Horizon**: log `tau_split` (share-based, split-rebased, common price per CUSIP-quarter, 2023 unit change handled; tau = 63 / quarterly turnover, clipped to [5, 2000]).
- **Network at t-1**: for each institution, its 10 nearest neighbours by cosine similarity of value weights (each institution's own weights, so units cancel) in the holdings at the end of quarter t-1. Ties broken by CIK.
- **Neighbour horizon from non-held stocks, NH_{i,t}**: for each neighbour j, the turnover of j between t-1 and t computed only over CUSIPs that i did not hold at t-1, with the same formula, prices and split rule as the panel; converted to log tau and averaged over i's neighbours with at least 5 such CUSIPs (weights equal). This removes mechanical overlap: shared positions hit by the same corporate events cannot drive it.
- **Outcome**: log tau_{i,t+1} (i's horizon from trades between t and t+1). The regressor uses trades up to t; the outcome uses trades after t.
- **Style cell**: quintile of i's lagged log tau (at t) crossed with tercile of log AUM (at t), within quarter: 15 cells per quarter.

## Stage 1a (no peer variables)

Share of the variance of log tau left after institution and quarter fixed effects, and after institution and style-by-quarter fixed effects.

**Gate 1a**: the share left after institution and quarter fixed effects must be at least 10%. Below that, stop: horizons are too close to a fixed trait for a peer study.

## Stage 1b specification

log tau_{i,t+1} = b * NH_{i,t} + a * log tau_{i,t} + c1 * log AUM_{i,t} + c2 * log n_positions_{i,t} + institution FE + style-by-quarter FE + e

- Standard errors clustered two ways, by institution and by quarter.
- **Primary coefficient**: b.

### Placebos (pre-specified)

1. **Future neighbours**: replace the t-1 neighbours with institutions that are among i's 10 nearest neighbours at t+4 but not at t-1; same NH construction at t. Expected b near 0 if the main effect reflects influence at t rather than sorting toward similar institutions.
2. **Shuffled neighbours**: within each style-by-quarter cell, randomly permute NH across institutions (seed 20261119). Expected b near 0.

### Gate 1b (pass or fail, decided by these rules only)

Pass if all three hold:
1. b > 0 with two-way clustered p < 0.05;
2. the future-neighbour placebo coefficient is not significant at 5% **or** is less than half of b;
3. the shuffled-neighbour placebo is not significant at 5%.

Pass: proceed to Stage 2 (shock design). Fail: per the decision rule in the audit, switch the headline to idea 2 (within-stock absorption), keeping Stage 0 and 1 work.

### Secondary (reported, not part of the gate)

- **Raw neighbour horizon**: NH computed over all of the neighbour's positions (shows how much the non-held restriction matters).
- **Quarter FE only** instead of style-by-quarter FE (shows how much style-level common shocks absorb).
- **Nonlinearity** (theory predicts possible tipping): add the share of i's neighbours with log tau below the quarter median, and its interaction with NH.
- **k = 5 and k = 20** neighbours.

## Software and reproducibility

`stage1/stage1a_variance.py` and `stage1/stage1b_peer_test.py` on branch `sumedh-agent/stage1-tests`, Python 3.12 with the versions in `requirements.txt`; the only randomness is the shuffle (seed above). Outputs go to `results/stage1a_*.json` and `results/stage1b_*.json`.

## Changes after registration

(none yet)
