---
title: Interim report — pivot-a-near-duplicate-audit
id: interim-report-pivot-a-near-duplicate-audit
tags:
- investor-horizon-novelty-audit-45a8e3
- locus-pivot-a-near-duplicate-audit
created: '2026-11-19T01:24:31.394704Z'
status: draft
type: interim
deprecated: false
summary: No direct near-duplicate found for institutional horizon peer effects across
  ~18 framings; PST turnover commonality is the key alternative; Liang-Wu-Yin unread
---

# Interim report: pivot-a-near-duplicate-audit

**Locus question:** Has anyone estimated peer effects, contagion or convergence in INSTITUTIONAL turnover, trading frequency, holding period or horizon under any name?
**Flavor:** convergent

## What the corpus already said
Corpus peer-effect papers on institutions study holdings, trades or flows, not turnover/horizon: Hong-Kubik-Stein [[nber-working-paper-series]], Pool-Stoffman-Yonker [[the-people-in-your-neighborhood-social-interactions-and-mutual-fund-portfolios]], Blocher [[network-externalities-in-mutual-funds]], Gerritzen-Jackwerth-Plazzi (MS 2024; returns/holdings similarity via shared-employer ties) [[birds-of-a-feather-do-hedge-fund-managers-flock-together]], Kooli-Zhang [[interplay-between-competition-networks-strategy-uniqueness-and-hedge-fund-perfor]], Jiang-Verardo (turnover only as control) [[does-herding-behavior-reveal-skill]], Ben-David et al. within-family correlated flows/trades [[nber-working-paper-series-8]]. Papers where trading activity IS the peer outcome are all retail: Heimer [[w-o-r-k-i-n-g]], Heimer-Simon [[facebook-finance-how-social-interaction-propagates-active-investing]], Escobar-Pedraza [[active-trading-and-poor-performance-the-social-transmission-channel]], Gelman et al. [[social-interaction-intensity]], Jin-Yu [[does-communication-increase-investors-trading-frequency-evidence-from-a-chinese]], Balakina-Stockler [[balakina-and-stockler-2025-peer-effects-in-multi-layer-networks-bse-netsci]]. I did not re-read these bodies in full; I relied on the vault summaries.

## What the new sources say (search audit)
Provenance caveat: most of the below were read as search-engine snippets or abstract-level WebFetch summaries. Vault `fetch` of SSRN (bot-blocked) and the CFR/NUS PDFs (compressed, unreadable or timed out) failed. Reliability is therefore medium. The absence verdict rests on search coverage, not full-text reads. No new vault notes were created from fetches.

Searches run (about 16 distinct queries; all returned no paper with institutional turnover/horizon/holding-period as a network-peer outcome):
1. peer effects mutual fund portfolio turnover network spillover institutional
2. investment horizon contagion institutional investors network short-termism spillover SSRN
3. fund family spillover turnover trading style co-managed funds manager moves
4. China mutual fund turnover peer effect common holdings network herding holding period
5. investor/investment horizon peer effects portfolio overlap IV friends-of-friends
6. hedge fund strategy contagion trading frequency holding-period herding
7. investment consultants / pension plan manager turnover short-termism spillover
8. arXiv 2025 heterogeneous horizons network adaptation ABM 13F horizon homophily
9. "Follow the Leader" peer effects (Pomorski)
10. turnover peer effects fund managers 2024-2026 (extended)
11. Bushee transient/dedicated persistence peer/co-holding network
12. Europe/Nordic/German fund managers peer effects turnover
13. Liang-Wu-Yin Chinese fund turnover
14. Rossi et al. pension consultants network
15. financial-centre fund turnover
16. short-term institutions peer imitation turnover (extended)
17. commonality in fund turnover (Pastor-Stambaugh-Taylor)
18. portfolio-overlap/common-ownership network x horizon assortativity

Closest hits, ranked:
- **Pastor-Stambaugh-Taylor, "Do Funds Make More When They Trade More?" (NBER w20700; JF 2017).** Abstract: "Turnover has a common component that is positively correlated with proxies for stock mispricing." Commonality is higher among funds with similar characteristics. This is a time-series factor structure, not a peer effect. It does not use a network, a neighbour exclusion rule or an instrument. It is the strongest reason to expect a referee to ask whether horizon convergence is just common shocks (sentiment/mispricing), so Pivot A must control for the common factor. It does not pre-empt A.
- **Liang-Wu-Yin, "High Turnover in Chinese Mutual Funds: Drivers and Effects" (SSRN 5048159).** Snippet only: drivers include herding, and high turnover predicts lower after-fee alpha. I could not read the abstract (SSRN returned 403). This is the one genuine unverified risk. Herding here is the LSV-type trade-direction measure and is probably not a peer effect in turnover itself, but it needs an abstract-level check.
- **Sialm-Tham, "Spillover Effects in Mutual Fund Companies" (NBER w17292).** Spillovers in flows and attrition across funds in a family, not turnover.
- **Christoffersen-Sarkissian, "The demographics of fund turnover" (JFI 2011).** Turnover varies with manager location (financial centres) and experience. Their abstract says they do not compare overall turnover levels across cities. This is a cross-sectional location effect and is not peer-effect identification. It supports the claim that the local environment shifts turnover.
- **Pomorski, "Follow the Leader: Peer Effects in Mutual Fund Portfolio Decisions" (AQR/working paper, 1980-2003).** Followers amplify leaders' buys by about 15-30%, per a secondary CXO summary. The outcome is the direction of trades in stocks, not turnover or horizon.
- **Rossi-Blake-Timmermann-Tonks-Wermers, "Network Centrality and Delegated Investment Performance" (CFR 15-16).** A consultant/shared-client network, linked to performance, risk-taking and flows. The outcomes are not turnover. The PDF was unreadable.
- **Zhu (manager social ties) and Liang-Liao-Ling (CFRI 2022, Chinese alumni networks).** Outcomes are portfolio similarity, return correlation and herding, not turnover.
- **Frontiers in Physics 2023 (Chinese co-holding network and net flows).** Outcome is flows. Network-science herding studies (2003-2019 China) concern herding coherence.
- **Chinco-Ye, "Investment-Horizon Spillovers" (NBER w23650).** A name collision only. It uses wavelets on stock volume at different frequencies and has no investor-level network.
- **Short-termism trap (JFE 2024) and Bhattacharya, "Institutional Investor Horizon and CSR Peer Imitation" (CSREM).** Peer interdependence among FIRMS (project horizon, CSR). The investor horizon is the moderator, not the outcome. These are possible "horizon contagion" keyword collisions but do not pre-empt A.
- **NUS/CUHK working paper (Chan, Cheng, Allaudeen; PDF unreadable).** The search snippet says fund flows are more correlated among funds with similar investment horizon. This is horizon-homophily-adjacent for D, with the outcome being flows.
- **Oldham (Complexity 2019), "short-termism and dynamic investor network" ABM, and arXiv 2604.23975 (heterogeneous horizons MARL).** Theory/ABM only, with no empirical estimation of an institutional adaptation rate. These bear on E. They are not 13F-calibrated.
- **Andonov-Bonetti-Stefanescu (consultants, pensions).** Consultant changes alter asset allocation and benchmarks, with no portfolio-turnover outcome.
- **Wharton working paper (snippet only).** Notes that fund turnover may depend on other funds' styles in the same family. A model, not a test.

## Evidence synthesis
Across about 18 query framings (fund family, manager moves, consultants, China/Europe, hedge-fund strategy contagion, holding-period herding, arXiv/SSRN 2023-2026, overlap-network x horizon), I found no paper that uses the portfolio-overlap or social network to estimate a peer effect where the OUTCOME is an institution's own turnover, holding period or horizon. Institutional peer-effect work consistently targets holdings, trade direction, flows or performance. Turnover-as-outcome peer work is retail (Heimer, Escobar-Pedraza, Jin-Yu, Gelman et al.). Three adjacent literatures give partial cover and should be cited as boundary markers: commonality in turnover (PST), fund-level turnover determinants (location, family, experience), and horizon-moderated peer imitation at the firm level.

The residual risks are (i) Liang-Wu-Yin (unread), (ii) fund-family/team turnover transmission buried in theses or niche journals (the snippet found a thesis on turnover after manager departures, which hints that manager-level portable turnover is studied and could be framed as an "effect of the manager", not a peer effect), (iii) Chinese-language journal papers invisible to this search engine, and (iv) post-June-2026 SSRN uploads. The search tool is US-centric web search, not SSRN/Google Scholar full-text, so recall for SSRN titles is limited.

## Committed position
The evidence adds up to "partially pre-empted at the level of ingredients, novel at the level of the exact estimand." Each ingredient exists: network peer effects among institutions (Pool et al., HKS, Pomorski, Gerritzen et al.), peer effects in trading activity (retail), and commonality in turnover (PST). The combination (institutional turnover/horizon as the outcome, neighbours defined through portfolio overlap, neighbour horizon computed only from stocks the focal institution does not hold, and friends-of-friends instruments) was not found in about 18 framings. The load-bearing reason is that every institutional peer-effect paper I found targets what is held, bought or flowed, and every turnover peer-effect paper targets retail. The novelty claim must be worded narrowly. It should not read "first peer effects among institutions". It should read "first identified peer effect in institutional horizon/turnover", and it must confront PST commonality as the main alternative, because a common mispricing/sentiment component would mimic convergence.

- **Position:** Pivot A is novel as an estimand but only as strong as its non-held-stock neighbour design. It is not pre-empted by anything I could read.
- **Confidence:** medium (about 65% that no killer paper exists; the main uncertainty is search-tool recall and the unread Liang-Wu-Yin and NUS papers).
- **Boundary conditions:** Applies to the 13F-style, US, holdings-derived horizon outcome and the overlap-network definition of peers. For Chinese or European fund data and for managers who move between funds, the audit is thinner (Chinese-language literature unsearched).
- **What would change this position:** Liang-Wu-Yin or any paper reporting a regression of a fund's turnover on peers' turnover (network, family or geographic) with an exclusion restriction would drop this to "partially pre-empted". A published manager-mover design showing that turnover follows managers would pre-empt a manager-move variant of A. A paper with PST-style commonality controlled that still finds peer convergence would also be a direct competitor.
- **Evidence weight:** 0 direct hits; about 6 adjacent institutional peer-effect papers (holdings/flows); about 5 retail turnover-peer papers; 1 commonality paper (PST) as the key alternative explanation; 3 unread or unreadable items (Liang-Wu-Yin, NUS/CUHK, CFR 15-16).

Recommended wording and checks for the draft: cite PST and demonstrate that the peer coefficient survives time fixed effects plus the PST common factor. Frame the contribution as an identification increment (neighbour horizon from non-held stocks; friends-of-friends instrument; reflection-problem handling per Manski), as the corpus supports.

## Open questions
- Full text of Liang-Wu-Yin (SSRN 5048159) and the NUS/CUHK horizon-flow paper.
- Chinese-language journal literature (CNKI) on fund turnover peer effects.
- Whether any SSRN 2025-2026 paper on "portable turnover" of moving managers exists.
- Whether the Wharton horizon/turnover paper (fund-family style) has an empirical peer test.

## Sources
(Vault-tagged corpus notes cited above by [[id]]. New items were read via search snippets or WebFetch summaries only; no new vault notes were created.)
1. Pastor-Stambaugh-Taylor, NBER w20700: https://www.nber.org/papers/w20700
2. Chinco-Ye, NBER w23650: https://ideas.repec.org/p/nbr/nberwo/23650.html
3. Liang-Wu-Yin, SSRN 5048159: https://ssrn.com/abstract=5048159 (unread)
4. Pomorski, Follow the Leader: https://www.aqr.com/Insights/Research/Working-Paper/Follow-the-Leader-Peer-Effects-in-Mutual-Fund-Portfolio-Decisions
5. Christoffersen-Sarkissian: https://mpra.ub.uni-muenchen.de/28651/
6. Rossi et al., CFR 15-16: https://www.cfr-cologne.de/download/workingpaper/cfr-15-16.pdf (unread)
7. Sialm-Tham, NBER w17292: https://www.nber.org/system/files/working_papers/w17292/w17292.pdf
8. Liang-Liao-Ling, CFRI: https://econpapers.repec.org/RePEc:eme:cfripp:cfri-04-2021-0073
9. Bhattacharya, CSR peer imitation: https://onlinelibrary.wiley.com/doi/10.1002/csr.70766
10. Andonov-Bonetti-Stefanescu (AEA 2024): https://aeaweb.org/conference/2024/program/paper/H4y3DEGF
