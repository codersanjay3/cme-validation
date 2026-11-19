# Cross-locus comparisons

## Tension 1: Novel question, fragile identification

- **Near-duplicate audit** ([[interim-report-pivot-a-near-duplicate-audit]]) commits: horizon contagion among institutions is novel as an estimand (no hit in about 18 framings); ingredients exist. About 65%.
- **Identification** ([[interim-report-correlated-turnover-vs-horizon-contagion-identification]]) commits: a 13F-only, top-150, friends-of-friends design is not credible at top-field standard; only a shock/event design on the full 13F universe survives. About 70%.
- **The cross-locus dynamic:** novelty and identifiability decouple. The question is open precisely because the obvious design does not identify it. Both investigators independently name the same alternative explanation (the Pastor-Stambaugh-Taylor common turnover component) and the same disconfirming test (the peer coefficient must survive time/category commonality controls), so this is a genuine open question, not a disagreement.
- **How the draft should engage this:** the recommendation must say that Pivot A is publishable only if built on exogenous shocks to neighbours' horizons (filer mergers/closures, manager departures) with style x quarter fixed effects and future-neighbour placebos, and must present the friends-of-friends IV as robustness only.
- **Calibration:** both medium confidence; both would change on (a) a found paper regressing fund turnover on peers' turnover with an exclusion restriction (Liang-Wu-Yin unread), (b) the event count being too small (fewer than about 30 usable shocks).

## Tension 2: How much of the horizon moves, and why

- **Trait vs time-varying** ([[interim-report-horizon-trait-or-time-varying]]) commits: within-institution variation exists but is mostly common/flow-driven; quarter FE mandatory; kill Pivot A if the residual after institution FE + quarter FE + flows is below about 10% of total variance. About 60%.
- **Identification** commits: style-level commonality survives the non-held-stock construction.
- **Orchestrator check (project data, outcome-free):** after institution and quarter FE, 33% of var(log tau) remains (34% excluding capped observations); quarter FE alone explain only about 2%.
- **The cross-locus dynamic:** the data partially resolve the dispute. The market-wide common component that PST document for mutual funds is small in this panel, so the trait investigator's kill condition is not met; but the remaining 33% can still be style-level commonality, which is exactly the identification investigator's worry. The two positions converge on style x quarter FE as the binding control.
- **How the draft should engage this:** report the variance decomposition as the first empirical fact of the pivot and state that flows and style-quarter effects must be partialled out before any peer claim.

## Tension 3: The old paper's empirical findings do not carry the new one

- **Dispersion/absorption** ([[interim-report-dispersion-and-absorption-beyond-chan-cheng-hameed]]) commits: Chan-Cheng-Hameed (JFQA 2022) already show dispersion -> liquidity and (IA1) dispersion -> lower volatility; the CME stock-level slope is a weaker replication. B is a section, not a paper. About 65%.
- **Homophily** ([[interim-report-horizon-homophily-fact-or-mechanical]]) commits: the kappa-hat = 0.158 fact is mostly mechanical (index geometry, drift-contaminated tau, type demand) and partly pre-empted (Crane-Koch-Michaely; CCH). About 65%.
- **Width corpus (Pivot C):** Gaspar-Massa-Matos churn and Yan-Zhang already net out price drift; C is pre-empted.
- **The cross-locus dynamic:** three independent investigations converge: every empirical result the CME paper currently headlines (C, D, the stock-level part of B) is pre-empted, mechanical, or a replication. Convergence from independent evidence paths is itself the finding: the pivot cannot be an incremental rewrite of CME; it must be a new estimand.
- **How the draft should engage this:** the recommendation section must say plainly that CME's current empirical results become supporting or robustness material, and name which ones (D as a conditional motivating fact after controls; B as a section; C as a footnote plus the 2022Q4 unit-break correction).

## Tension 4: The model's friction channel against two empirical signs

- **Dispersion/absorption** commits: the CME simulated friction channel (more horizon diversity, more volatility) is the outlier against two independent empirical signs (CCH IA1; CME's own stock-level slope).
- **Data/ABM** ([[interim-report-data-upgrade-and-abm-calibration]]) commits: Pivot E remains novel only in a specific form (horizon-homophilous links + adaptation rate estimated from 13F peer effects + out-of-sample test) and only as a supporting section; nearest ABM is Oldham 2019 (abstract-level read). About 55%.
- **The cross-locus dynamic:** the model cannot simply be calibrated and kept; its sign is contradicted by data. A calibrated model must add a liquidity/absorption channel (the repo's Option B) whose strength is disciplined by the B-section estimates, or drop the friction-volatility claim. This links Pivot B (the estimate) to Pivot E (the model) and gives E its only defensible role.
- **How the draft should engage this:** recommend E as the paper's final section: estimated adaptation rate from A, absorption strength from B, then an out-of-sample check; state that the uncalibrated friction result should be withdrawn.

## Tension 5: Sample and data integrity versus credibility

- **Identification** and **Data/ABM** both commit that the top-150 filer sample makes friends-of-friends instruments invalid (Chandrasekhar-Lewis sampled networks) and that the free SEC 13F Data Sets (2013Q3 onward, all filers, share counts) answer this without WRDS (high confidence on data facts).
- **Orchestrator finding:** the January 3, 2023 SEC change to dollar values produced a 1000x unit break in the project cache at 2022Q4; the paper's TDI minimum (1.021) is an artefact (1.918 after rescaling) and r(TDI, VIX) moves from -0.526 to -0.641.
- **The cross-locus dynamic:** credibility of every pivot depends on rebuilding the panel from full-universe, share-based, unit-consistent data. This is a precondition, not a contribution.
- **How the draft should engage this:** the data-upgrade section must list the rebuild as step zero and record the unit-break correction as a result change for the current paper.

## Step 8 corpus-critic updates
- Tension 1: adversarial searches (Liang-Wu-Yin abstract, Chinese literature, 2023-2026 WPs, manager-mover designs) returned no paper with institutional turnover/horizon as the peer outcome; novelty confidence up to ~70%. Chinese co-holding-network peer designs exist for other outcomes (bubble-riding), so A must be framed as a known design applied to a new estimand. One unread lead: MacDonald SSRN 5692342 (2025), to be read manually.
- Tension 1 (identification): merger/closure shocks WEAKENED (Lewellen-Lowry JFE 2021: BGI-dominated; Massa-Schumacher-Wang RFS 2021: mergers shift neighbours' holdings directly, violating exclusion). Manager-shock arm STRENGTHENED (Liu et al. RoF 2023: managers' parental deaths shift style toward indexing). Theory added (Froot-Scharfstein-Stein 1992; Chamley 2007; Cespa-Vives): strategic complementarity predicts a positive, possibly nonlinear, horizon peer effect.
- Tension 3: Pivot B tail-risk increment partly pre-empted in China (Chen-Lu-Qin 2026); US/stress/absorption version open. B stays a section.
- Tension 4: Oldham 2019 read in full; E's specific mechanism not pre-empted (~70%).
