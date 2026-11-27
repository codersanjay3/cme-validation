---
title: Interim report — data-upgrade-and-abm-calibration
id: interim-report-data-upgrade-and-abm-calibration
tags:
- investor-horizon-novelty-audit-45a8e3
- locus-data-upgrade-and-abm-calibration
created: '2026-11-19T01:22:26.172908Z'
status: draft
type: interim
deprecated: false
summary: Free SEC 13F Data Sets (2013Q3+, shares, all filers; VALUE in dollars from
  3 Jan 2023) suffice for full-universe network; Pivot E novel-but-supporting after
  Oldham 2019 (full text unobtainable).
---

# Interim report: data-upgrade-and-abm-calibration

**Locus question:** (i) Can the free SEC Form 13F Data Sets give a full-universe overlap network (answering the sampled-network critique without WRDS), and what are the 13F data-quality issues incl. the Jan 3 2023 dollar-unit change? (ii) Precedent for calibrating an ABM adaptation rate to an estimated network peer-effect coefficient; Oldham 2019 as closest ABM near-duplicate.
**Flavor:** convergent

## What the corpus already said
[[econpapers-understanding-how-short-termism-and-a-dynamic-investor-network-affect]] (Oldham 2019, abstract only): heterogeneous time horizons, advice network that rewires toward outperforming "Oracles", short-termism raises volatility; not horizon-homophilous, not calibrated to 13F. [[how-homophily-a﻿ffects-the-speed-of]] (Golub-Jackson) supplies DeGroot theory: homophily slows convergence. [[econometrics-of-sampled-networks]] (Chandrasekhar-Lewis) is the sampled-network critique; [[empirical-challenges-with-peers-of-peers-instruments]] warns friends-of-friends instruments weaken with density. [[statistically-validated-network-of-portfolio-overlaps-and-systemic-risk-pmc]] builds a full 13F overlap network.

## What the new sources say
1. [[secgov-form-13f-data-sets]] (fetched into vault). SEC page: data sets cover "July 2013 - August 2026", extracted from the XML portion of 13F submissions, "presented without change from the as-filed submissions", free ZIPs of roughly 45-96 MB per period. Disclaimer: "we cannot guarantee the accuracy of the data sets." Notes: all sets refreshed 12 Mar 2024 to a common format (EDGAR Release 22.4.1), with fixes for some missing information-table records.
2. SEC 13F Data Sets readme (https://www.sec.gov/files/form_13f_readme.pdf; read directly, not vault-stored). INFOTABLE field VALUE: "Market value. Starting on January 3, 2023, market value is reported rounded to the nearest dollar. Previously, market value was reported in thousands." Also: SSHPRNAMT (shares or principal amount) plus SSHPRNAMTTYPE (SH/PRN); CUSIP; optional FIGI (new); PUTCALL; INVESTMENTDISCRETION; submission types 13F-HR, 13F-HR/A, 13F-NT. Confirms the rule date and wording. Web search additionally attributes this to EDGAR Release 22.4.1 (sec.gov/oit/announcement/edgar-release-2241) and the June 2022 amendments; I did not open that page (search-snippet level).
3. Thomson s34 issues (search snippets only; WRDS slide "WRDS Ownership Data", 2020): Thomson 13F files omit some institutions (BlackRock named for 2018); WRDS research note shows how to append WRDS's own 13F history; WRDS's own 13F product starts June 2013. Vendor blogs on CUSIP errors and amendments are low-reliability context. I did not retrieve the research note itself.
4. Oldham full text: NOT obtained. Hindawi PDF returned HTTP 403, Wiley/Hindawi landing pages and the Wiley pdfdirect link (Semantic Scholar's OA link) returned Cloudflare bot pages. Audited absence: I could not verify from the text whether horizon itself adapts or whether links depend on horizon similarity. Metadata only: Crossref lists 60 references (including Alfarano 2008 "Should network structure matter in agent-based finance?" and Markose et al. guru effects); Semantic Scholar counts ~4 citations (2024 Mathematics, 2026 JEIC, 2020 Complexity paper on modular networks); code at comses.net (an agent-based artificial stock with a dynamic investor network). The abstract says short-/long-term "behavior" and trust updating, with rewiring on performance.

## Evidence synthesis
Data. The SEC flat files cover 2013Q3 onward (the paper's sample starts 2013Q2; the first quarter is lost or must be taken from raw EDGAR), give every filer rather than the top 150, and include share counts, so the full-universe network and the share-based horizon (immune to price drift) can be built free of WRDS. Holdings per CUSIP are as-filed, so the cleaning burden (amendments 13F-HR/A, CUSIP typos, 13F-NT, shared discretion, SH vs PRN, puts/calls) falls on the user; CUSIP-to-permno mapping still needs a crosswalk (FIGI field is optional and new; OpenFIGI or CRSP/Compustat for returns). Full universe (~5,000+ filers per quarter) cuts the sampling problem but sharpens the Canen-Chadha density issue for friends-of-friends instruments; restrict to a sparse thresholded overlap graph.

ORCHESTRATOR-VERIFIED FACT (project cache, not a vault source): the reported value field jumps about 1000x at 2022Q4; the paper's TDI minimum of 1.021 in 2022Q4 is an artefact (1.918 after rescaling) and r(TDI,VIX) moves from -0.525 to -0.641. The SEC readme explains the mechanism (the readme says "starting on January 3, 2023"; filings for 2022Q4 reports filed after that date are in dollars, which is consistent with the jump at 2022Q4). Any value-weighted measure must rescale by filing date, and share-based measures avoid the issue entirely, reinforcing pivot C.

ABM calibration. From the vault and my own background knowledge (NOT verified in this session; treat as leads): estimating ABMs by simulated method of moments / indirect inference is established (Franke-Westerhoff; Kukacka-Barunik; Grazzini-Richiardi), but typically to aggregate return moments, and the PLOS ONE 2018 and Scholl et al. 2025 notes calibrate to market or holdings data. I found no instance tying a reduced-form peer coefficient to a structural adaptation parameter. The mapping is mathematically simple: in DeGroot updating x_t+1 = (1-a)x_t + a W x_t, the linear-in-means coefficient beta on neighbour-average horizon equals a (the weight on neighbours), conditional on W being row-normalised and adaptation per quarter; the model's 0.06 would be directly comparable to a quarterly beta, with the caveat that linear-in-means identifies a reduced-form of social interaction plus correlated effects. Search coverage for the bridge was thin (no dedicated search of arXiv/SSRN beyond the vault) so the absence is only suggestive.

## Committed position
Data: the pivot should rebuild everything from the free SEC 13F Data Sets (2013Q3-2026Q2 vintages), using share-based horizons only, a full-filer sample (or at least top 1,000 by AUM plus a random-sample robustness check showing coefficients stable as sampling fraction rises), and treat the Jan 3 2023 dollar change as a hard rescale (VALUE/1000 for filings before that date) in any residual value-based series; WRDS/CRSP is only needed for returns and permno mapping, not for the network. The sampled-network critique is therefore answerable for free. On Pivot E: after Oldham 2019 it remains novel in its specific form (horizon-homophilous link formation, horizon imitation among neighbours, adaptation rate estimated from 13F peer effects and tested out of sample), because Oldham as far as abstract and metadata show rewires on performance and is uncalibrated, but this rests on abstract-level reading, so the claim must be phrased as "to our knowledge" and Oldham must be cited as the nearest ABM. Position E as a supporting section that disciplines the 0.06 parameter with the estimated peer coefficient from Pivot A, not as a standalone paper (JEDC/JEBO/Complexity-tier outlets).
- **Position:** Free SEC data suffice for a full-universe, share-based network, and E is a novel but supporting calibration step layered on an empirical peer-effect paper, with Oldham 2019 as the nearest ABM.
- **Confidence:** high on data and the SEC rule (read directly); medium-low (about 55%) on E's novelty because Oldham's full text was unreadable and the bridge search was thin.
- **Boundary conditions:** Holds for 2013Q3 onward; pre-2013 needs text parsing. Holds if beta is estimated per quarter on a comparable timescale to the model step. Full-universe IV validity depends on graph sparsity.
- **What would change this position:** Oldham's body showing that horizon is an adapting state variable with similarity-based links; any paper estimating a DeGroot weight from holdings peer effects and feeding an ABM; evidence that SEC-data cleaning (CUSIP/amendments) changes the horizon ranking materially versus Thomson-based results.
- **Evidence weight:** 2 primary SEC documents read; Thomson issues and EDGAR release at search-snippet level; Oldham abstract and metadata only; ABM-calibration precedents from memory.

## Open questions
- Oldham full text (try library access or the comses.net code and docs).
- The WRDS research note and Backus-Conlon-Sinkinson data appendix for concrete s34 error rates.
- Dedicated search for any ABM paper calibrating imitation to a measured peer coefficient.
- Whether 13F filings for 2022Q4 filed before Jan 3 2023 are in thousands (the jump suggests mixed vintage; check filing dates).

## Sources
1. [[secgov-form-13f-data-sets]] SEC Form 13F Data Sets page
2. SEC 13F Data Sets readme PDF (not vault-stored)
3. [[econpapers-understanding-how-short-termism-and-a-dynamic-investor-network-affect]] Oldham 2019
4. [[how-homophily-a﻿ffects-the-speed-of]] Golub-Jackson
5. [[econometrics-of-sampled-networks]]; [[empirical-challenges-with-peers-of-peers-instruments]]
