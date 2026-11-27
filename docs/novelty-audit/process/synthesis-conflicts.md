# Synthesis conflicts (orchestrator source checks)

## Conflict 1: author of the cliques paper
- Drafts A/B (and interim notes, evidence digest) say: Crane, Koch and Michaely.
- Draft C says: Crane, Koch and Michenaud.
- Source check: the fetched PDF (institutional-investor-cliques-and-governance) lists "Sébastien Michenaud" (DePaul) as third author; the note summary's "Michaely" is an error.
- **Verdict:** Crane, Koch and Michenaud. Use this everywhere.

## Conflict 2: what Chandrasekhar-Lewis Proposition 3.4 permits
- Drafts A/B: friends-of-friends instruments from a sampled network are generically invalid.
- Draft C: instruments built from the full graph stay valid when the second stage is restricted to sampled nodes.
- Source check (econometrics-of-sampled-networks, Proposition 3.4): parts (1)-(2) show invalidity when the instrument uses the sampled graph; part (3) shows E[Zu] = 0 when the graph records sampled nodes' links to all nodes, outcomes and covariates are observed for all nodes, and the second stage is restricted to sampled nodes.
- **Verdict:** both correct within scope. State precisely: instruments built from a sampled graph are generically invalid (parts 1-2); validity is restored when the network and covariates are observed for all nodes and only the estimation sample is restricted (part 3). The full SEC 13F universe gives the whole network, so the team can estimate on its top filers while building neighbours and instruments on the full graph.

## Conflict 3: Journal of Banking & Finance impact factor
- Draft A/C: 4.0. Draft B: 3.8.
- Source check: journal page shows 4.0 (latest release); Review of Finance 2025 report gives 3.8 for 2024.
- **Verdict:** report "4.0 (latest release; 3.8 for 2024)". Same pattern for JFQA: 4.1 (2025 release; 2.8 for 2024).

## Conflict 4: which pivot leads
- Draft A: horizon contagion (A) leads; B as consequence section.
- Draft B: a US stress-episode absorption paper (B-plus) leads; A is a trap.
- Draft C: A leads as a staged programme with kill criteria; B and E as modules publishable alone.
- **Verdict:** commit to C's structure with A's thesis: A leads, run as a staged, pre-registered programme; B's absorption paper is the named fallback if A fails the shock gate. Engage Draft B's quantitative objections explicitly (small implied variance share of eta = 0.06; Nickell bias of similar size; top-k threshold artefact in FoF counts) as the conditions the shock design must meet, not as reasons to abandon A.
