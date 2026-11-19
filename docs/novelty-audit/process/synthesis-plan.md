# Synthesis plan

## Core thesis (1-2 sentences)
The most defensible novel pivot is "horizon contagion": the first identified peer effect in institutional investment horizon through portfolio-overlap networks, run as a staged, pre-registered programme on the full SEC 13F universe with manager-level shocks to neighbours; every empirical result the current CME paper headlines is pre-empted, mechanical or a replication, so those results become supporting modules (B dispersion/absorption, E calibrated model, D motivating fact, C footnote plus data correction), and B's US stress-absorption paper is the named fallback if A fails its shock gate.

## The strongest argumentative beats
1. **Open because unidentified** (Draft C, comparisons Tension 1): novelty and identifiability decouple; the obvious design fails, which is why nobody has done it.
2. **Asymmetry: identification problems are fixable, novelty problems are not** (Draft A 4.2): nothing un-publishes Chan-Cheng-Hameed; each threat to A has a known remedy.
3. **The steelman numbers** (Draft B 3.1): eta = 0.06 implies a tiny share of residual variance; Nickell bias about 0.036 is of similar size; top-k thresholding manufactures friends-of-friends. These set the bar the shock design must clear, and justify the event-study design over a dynamic linear-in-means regression.
4. **The current paper's empirics do not carry** (Tension 3): C pre-empted since 2005; CCH IA1 already reports dispersion -> lower volatility (CME slope is a weaker replication); D mechanical; the CME friction channel's sign is contradicted by data, so the friction claim should be withdrawn (Tension 4).
5. **The 2022Q4 unit break** (project data): the paper's TDI minimum 1.021 is an artefact of the SEC dollar change (1.918 fixed); it must be corrected regardless of pivot.
6. **Theory gives a signed, falsifiable prediction** (Draft A): strategic complementarity (Froot-Scharfstein-Stein; Chamley; Cespa-Vives) predicts positive and possibly tipping horizon spillovers.
7. **The impact-factor bar was never binding** (Draft C 5.1): FRL already sits at 7.1; quality ranking differs from IF (JFQA 4.1 vs IRFA 10.2); the constraint is having a non-replication contribution.

## Section structure
Use the 7 required H2 headings in order (from prompt-decomposition.json), preceded by a bold executive summary paragraph with the verdict table, then ## Sources.

## Per-section commitments
### 1. Where the Current CME Paper Stands
- Evidence: Drafts A 1.1-1.3, C 1.1-1.3, B 1.1. Beat 4 and 5. Keep the question, drop the results.
### 2. Literature Map
- Seven strands (a)-(g), compact, each ending with what it means for the pivots. Use Draft C's strand text as the base (most concise), add Draft A's Chinese co-holding peer design and Draft B's absorption evidence.
### 3. Novelty Audit of the Five Candidate Pivots
- Verdict table first, then A-E subsections with closest papers and the novel increment. Tension 1, 3 and the B-relevant source tension (who absorbs). Name the unread MacDonald (SSRN 5692342) and Liang-Wu-Yin full text as residual risks.
### 4. Recommended Pivot
- Beat 1, 2, 3 and 6. The paper in one paragraph, why A leads not B (engage Draft B fully), staged decision tree with kill criteria (Draft C 4.3), pre-registration.
### 5. Target Journals and Fit
- Beat 7. Table of journals with IF (latest release; note year volatility) and fit; submission ladder (RoF -> MS/JFQA -> JFS/JBF; JIFMIM for US-vs-China B; FRL for a short correction/replication letter).
### 6. Identification Strategy and Data Upgrades
- Step zero rebuild (SEC 13F Data Sets, share-based, unit fix, full universe), Stage 1 variance + descriptive test (33% residual already passes 10% gate; quarter FE ~2% so style x quarter FE is the binding control), Stage 2 manager-shock event design (Liu et al. template; mergers only robustness ex-BGI per Lewellen-Lowry and Massa-Schumacher-Wang), FoF IV with precise Prop 3.4 statement and Anderson-Rubin sets, B module and E module, CRSP/WRDS role.
### 7. Referee Objections the Pivot Must Survive
- 8-10 numbered objections with answers (common shocks/PST; reflection/Angrist; exclusion bias; sampled network; merger critique; trait persistence/Cohen-Lu-Nguyen; homophily vs influence; small effect/Nickell; fund vs filer level; survivorship/CRSP).

## Where drafts disagreed
- **Which pivot leads:** commit to A as a staged programme; B-plus is the fallback; Draft B's objections become explicit gates.
- **Prop 3.4:** state both parts precisely (see conflicts file).
- **JBF/JFQA IF:** give latest release and the 2024 figure.
- **Cliques authors:** Crane, Koch and Michenaud.

## Length target
- response_format: argumentative
- Pass 1 target: about 8,500 words
- Pass 2 final target: about 7,500 words (hard ceiling 10,000)
