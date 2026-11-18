# DECISIONS: the project's shared memory

Append-only. Newest entries at the bottom. Never edit or delete an old entry; add a new one that corrects it.

Entry template:

```
## YYYY-MM-DD <agent-name>: <one-line title>
- Changed: files and scripts
- Numbers: name, old value, new value, script and seed
- Why:
- Open: what is unresolved, and who should check
- Beads/issues: ids
```

---

## 2026-11-18 sanjay-agent: baseline state when the repo was created

Where the project stands, so no agent has to rediscover it.

**What holds up**
- Clustering assumption: investors with similar horizons hold more similar portfolios. Mean kappa-hat 0.158, positive in all 50 quarters. Newey-West t = 19.0 at 3 lags, 16.3 at 8 lags, effective sample about 24. Block bootstrap range 0.145 to 0.175. Permutation test significant at 5% in 48 of 50 quarters (fails 2013Q3, 2013Q4; at 1% also fails 2016Q4).
- Simulation: more clustering lowers simulated volatility by a factor of 1.31 and belief fragmentation by 14.25, held in a 30-seed replication.
- Stock-level test (survivors only, about 60% of securities matched to tickers): similar-horizon owners go with slightly higher next-quarter volatility. Stock and quarter fixed effects, share-based horizons: -0.0106 (t = -2.42, p = 0.016). Weight-based: -0.0047, not significant. Effect is about 1% of a standard deviation.

**What was corrected**
1. The "17 lags" correction was never computed. Real Newey-West now reported.
2. "Significant at p < 0.001 in every quarter" became 48 of 50 under a permutation test.
3. Horizon diversity versus VIX (r = -0.53 to -0.59) is mostly price drift. Share-based turnover gives r about -0.06. Reported as a measurement artifact.
4. The Granger result runs opposite to the model and does not reproduce on the rebuilt series. Marked suggestive.
5. Temporal liquidity versus VIX is mostly mechanical, since volatility is inside the measure. Sample is 45 quarters, not 36.
6. MOVE is a published ICE Bank of America index, not ours.
7. The claim that compressing horizons raises simulated volatility was unsupported. Properly run, volatility falls.
8. Uniform-mode bound derived as lambda n beta / pbar, about 0.0013.
9. Temporal liquidity peak at moderate clustering is not statistically reliable.
10. Closest related work (Cella, Ellul, Giannetti, RFS 2013) was missing and is now cited.

**Open items**
- The rebuilt horizon-diversity series correlates only 0.50 with the original paper series (2022Q4: original 1.02, rebuilt 1.77). Cause not found. Needs an independent check by someone who did not build it.
- Model decision: option A (horizon-dependent stabiliser), B (horizon-dependent liquidity), or C (keep the model and report the tension). Professor Chalmers's view requested.
- WRDS/CRSP access requested, to remove survivorship bias and ticker-matching loss.
- Scripts need uploading to Zenodo (the paper's data-availability statement claims they are included).
- Bond analysis is descriptive only (7 Vanguard funds, 27 quarters each).
