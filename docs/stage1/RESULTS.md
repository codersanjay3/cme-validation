# Stage 1 results (2026-11-19)

Pre-registration: `docs/stage1/PREREGISTRATION.md`, commit `c14dba7` (12:34 PT). Code committed before the Stage 1b run: commit `d23862d` (12:36 PT). Nothing in the specification was changed after seeing results. Data: full-universe 13F panel (release `data-rebuild-v1`).

## Correction (2026-11-22): split rule fixed, Stage 1 rerun

The panel's split-rebased horizon (`tau_split`, the Stage 1 measure) used a split rule that looked only at the share ratio. It treated a position whose share count halved or doubled as a split, even when the price did not move, so those trades vanished from turnover. That rule fired on 1,385,494 of 63,618,289 continuing positions, and 96.8% of the firings had no confirming price move (`results/scoping_split_rule_check.json`, bead cme-d0m). The fix rebases only when the common price also moves by about 1/k. The specification is otherwise unchanged; same code, same seed (20261119). All tables below show the rerun. Original values:

| Quantity | Original | Rerun |
|---|---|---|
| Median tau_split (days) | 674.6 | 649.0 |
| 1a: share of var(log tau) left after institution + quarter FE | 30.4% | 30.9% |
| 1a: AR(1) of log tau | 0.753 | 0.750 |
| 1b primary b (t) | +0.0324 (5.33) | +0.0310 (5.28) |
| 1b future-neighbour placebo b (t) | -0.0080 (-2.48) | -0.0087 (-2.80) |
| 1b shuffled placebo b (t) | +0.0035 (1.62) | -0.0026 (-1.16) |
| 1b all-positions neighbour horizon b (t) | +0.0463 (7.22) | +0.0421 (6.58) |
| 1b share of short-horizon neighbours b (t) | -0.0717 (-5.16) | -0.0667 (-4.48) |
| Gates 1a and 1b | pass | pass |

Old and new log tau_split correlate at 0.994; raw (not split-rebased) turnover is unchanged. Before the fix, the shuffled placebo was positive; after it, negative; it is not significant either way. The shuffle seed is unchanged, but the sample changed slightly (199,310 rather than 199,225 observations), so the shuffle draws differ.

## Stage 1a: horizons move enough to study (gate passed)

214,188 institution-quarters, 9,278 institutions, 52 quarters (`results/stage1a_variance.json`).

| Fixed effects removed | Share of var(log tau) left |
|---|---|
| Institution | 32.9% |
| Quarter | 97.6% |
| **Institution + quarter (gate: at least 10%)** | **30.9%** |
| Institution + style-by-quarter | 4.2% (mechanical in 1a: style cells are built from the same quarter's horizon) |

Quarter-to-quarter persistence of log tau: 0.75. The same numbers as on the old top-150 panel (33%, 2%, 0.75).

## Stage 1b: horizons move toward overlap neighbours' horizons (gate passed)

199,310 institution-quarters, 8,867 institutions, 51 quarters; institution and style-by-quarter fixed effects; two-way clustered standard errors (`results/stage1b_results.json`).

| Pre-registered test | b | t | p | Gate criterion |
|---|---|---|---|---|
| **Primary**: neighbours' horizon from stocks i did not hold, k = 10 | **+0.0310** | **5.28** | < 0.0001 | b > 0, p < 0.05: met |
| Placebo 1: future neighbours (top 10 at t+4, not at t-1) | -0.0087 | -2.80 | 0.007 | n.s. or below b/2: met (negative) |
| Placebo 2: neighbour horizon shuffled within style-by-quarter cells | -0.0026 | -1.16 | 0.252 | n.s.: met |

**Gate 1b: pass.** Per the decision rule, the programme proceeds to Stage 2 (neighbour manager shocks).

### Secondary results (pre-specified, not part of the gate)

| Variant | b on neighbour horizon | t |
|---|---|---|
| Neighbours' horizon over all their positions (includes shared stocks) | +0.0421 | 6.58 |
| Quarter fixed effects only (no style cells) | +0.0330 | 5.05 |
| k = 5 neighbours | +0.0243 | 6.45 |
| k = 20 neighbours | +0.0384 | 5.31 |
| Nonlinearity: add share of neighbours below median horizon and its interaction | +0.0037 (n.s.); share short: -0.0667 (t = -4.48); interaction +0.0189 (t = 1.60) | |

## Reading

1. **Direction**: an institution's horizon next quarter moves toward the horizons its portfolio-overlap neighbours showed in stocks it did not hold. The future-neighbour placebo is negative, so the result is not explained by institutions drifting toward the horizon of institutions they will later resemble; the shuffled placebo is zero.
2. **Restricting to non-held stocks matters but does not remove the effect**: +0.042 with all positions, +0.031 with non-held stocks only. About a third of the raw association is mechanical overlap.
3. **Style-level common shocks absorb little**: +0.033 with quarter effects only, +0.031 with style-by-quarter effects.
4. **Magnitude is small.** One within-institution standard deviation of the neighbour horizon (0.29 log points) moves the next-quarter horizon by about 0.009 log points, about 2% of a within standard deviation of the outcome (0.47). With own persistence 0.27 inside institution fixed effects, the implied long-run response is 0.0310 / (1 - 0.272) = 0.043 per unit of neighbour horizon. For comparison, the CME model assumes an adaptation rate of 0.06 per cycle: the estimate is of the same order, which is what idea 4 (calibrated model) needs.
5. **Caution from the nonlinearity check**: once the share of short-horizon neighbours (measured over all positions) is added, the non-held-stock coefficient falls to zero and the share of short-horizon neighbours carries the association (-0.067, t = -4.48). The two measures are strongly related and the share uses all positions, so this does not settle anything, but it means the effect may run mainly through having short-horizon neighbours rather than through the average. Stage 2 should test both forms.

## What Stage 1 does not show

- It is not causal. Common information shocks at a finer level than the style cells, and institutions choosing neighbours, can still produce the pattern. Stage 2 (exogenous shocks to neighbours' managers) is the identification step.
- With institution fixed effects and a lagged outcome, the coefficient on own lagged horizon carries Nickell bias (about 22 quarters per institution on average); the neighbour coefficient is less exposed but not immune.
- 13F is filer-level, not fund-level; the shock design needs fund-level manager data (N-PORT or CRSP mutual funds).
