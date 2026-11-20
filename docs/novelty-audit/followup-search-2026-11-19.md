# Follow-up search, 2026-11-19

Targeted searches after the audit report was finalised, aimed at the residual risks it named. Web searches (extended mode) plus fetches into the research vault where sites allowed it.

## Verdicts

| Target | Result | Effect on IDEAS.md |
|---|---|---|
| Liang, Wu and Yin (SSRN 5048159), the one unread paper flagged as a risk to idea 1 | Still abstract only (SSRN blocks automated access). Abstract: determinants of high turnover include herding (Wermers/LSV-style trade direction), not peers' turnover. Earlier version: Liang and Yin (2025). | Idea 1 unchanged. Read the full PDF manually before submission. |
| Chinese literature on peer effects in fund turnover or holding period | Co-holding networks and trade correlation (Liu Yangshu et al. 2018, Southern Finance: fund trades positively correlated within co-holding networks); fund "herding together" (Luo Danglun et al.); alumni networks and portfolio similarity (Qi et al. 2020); manager social networks and performance (Wang Wenlan et al. 2022). None uses turnover or holding period as the peer outcome. | Idea 1 unchanged; adds Chinese network-trading papers to cite as adjacent. CNKI still not searched directly. |
| Manager-change designs where turnover follows the manager | New managers overhaul inherited portfolios (Journal of Business Research 2016); no paper found showing turnover is a portable manager trait. | Stage 2 manager-shock design still open; cite the overhaul paper as a known confound (a new manager trades a lot regardless of peers). |
| Institutional contagion designs with exogenous shocks | **Luo (SSRN 5983719)**: after natural disasters, institutions in socially connected but unaffected areas adopt similar sustainability tilts; small and low-skill institutions are more susceptible. Not about horizon. | Best design template so far for idea 1's shock arm: exogenous shocks to peers, then spillover. Add as closest design precedent. |
| Within-stock absorption by horizon (idea 2) | Cella, Ellul and Giannetti's text says only that short-horizon investors do not provide liquidity in turmoil; no within-stock test of long-horizon absorption. **Aragon and Strahan (JFE 2012)**: stocks with more ownership by other institutions and non-Lehman hedge funds lost less liquidity after Lehman (ownership level, not horizon). | Idea 2 still open at the within-stock, by-horizon level; Aragon-Strahan becomes a closest neighbour and a design template (Lehman prime-broker shock). |
| Novelty of the 13F unit-break note (idea 7) | Known to practitioners: a 2026 analysis reports a few percent of 2026Q2 holdings reports still in thousands; StoneX disclosed misreporting from 2022Q4 to 2025Q1; Barclays amended a 2024 filing; open-source parsers normalise by date. | Idea 7 downgraded: not novel as a stand-alone note. Kept as a data-integrity appendix. |
| Short-termism as a social norm | A sovereign-fund forum review describes short-termism as an accepted norm that creates peer pressure to conform (conceptual, not empirical). | Conceptual support for idea 1's mechanism. |

## Consequence found in our own data

The search showed that a filing-date unit rule is not enough. In our top-150 panel, 66 filers jump about 1000x exactly at 2022Q4, but 25 show no jump there and several switch later (2023Q1, 2023Q2, 2024Q3, 2025Q3); a few have one-quarter 1000x spikes before 2023. This matters for any analysis that compares or weights raw values across filers in the same quarter, notably the stock-level test's ownership weights. A rerun with a per-filer unit fix (`scripts/check_stock_level_unit_fix.py`, PR #2) roughly doubles the paper's within-stock slope: -0.0106 (t = -2.42) to -0.0200 (t = -4.96); the value-weight version becomes significant (-0.0182, t = -4.63); the placebo stays at zero. Result-change issue #5. The direction is unchanged and it is still a sign replication of Chan-Cheng-Hameed, so the pivot recommendation does not change. The rebuild (PR #4) now has a per-filing implied-price check.

## Sources added to the vault

Aragon and Strahan (NBER w15336); FocusAlpha 13F filing analysis; an open-source 13F parser fix for the 2023 rule. Blocked (abstract only): Luo SSRN 5983719, the JBR 2016 new-managers paper, the IFSWF review.
