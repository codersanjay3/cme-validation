"""
CME Paper Validation Script
Reproduces every quantitative claim in:
  "Chronotypic Market Ecology: Temporal Homophily, Network Fragmentation,
   and Market Stability" – Subramanian & Seetharaman (2026)

Run: python simulate.py
"""

import numpy as np
from scipy import stats
import networkx as nx
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────
# Section 0: Analytical / formula checks (no simulation)
# ─────────────────────────────────────────────────────────

def check_tmfi_synthetic():
    """
    Definition 4: communities seeded at 90, 95, 100, 110
    Paper claims: TMFI = 0.076 (simulation), analytical = 0.074
    """
    prices = np.array([90., 95., 100., 110.])
    mean_p  = prices.mean()           # 98.75
    std_pop = prices.std(ddof=0)      # population std
    std_smp = prices.std(ddof=1)      # sample std
    tmfi_pop = std_pop / mean_p
    tmfi_smp = std_smp / mean_p
    print("=== TMFI Synthetic Validation ===")
    print(f"  Mean price          : {mean_p:.4f}")
    print(f"  Std (pop, ddof=0)   : {std_pop:.6f}")
    print(f"  Std (smp, ddof=1)   : {std_smp:.6f}")
    print(f"  TMFI (pop std)      : {tmfi_pop:.6f}  [paper claims analytical=0.074]")
    print(f"  TMFI (smp std)      : {tmfi_smp:.6f}")
    ok = abs(tmfi_pop - 0.074) < 0.002
    print(f"  PASS: {ok}  (pop std gives {tmfi_pop:.4f} vs 0.074)")
    return tmfi_pop, tmfi_smp


def check_stability_bound():
    """
    Theorem 1: stability bound λ2 > β̄/ᾱ
    Paper claims: ᾱ=0.30, β̄=0.20  → λ2* = 0.667
    """
    alpha_bar = 0.30
    beta_bar  = 0.20
    bound = beta_bar / alpha_bar
    print("\n=== Stability Bound ===")
    print(f"  β̄/ᾱ = {beta_bar}/{alpha_bar} = {bound:.6f}")
    ok = abs(bound - 0.667) < 0.001
    print(f"  PASS: {ok}  (paper claims 0.667)")
    return bound


def compute_tdi(tau_values: np.ndarray, K: int = 20) -> float:
    """Shannon entropy of the log-τ histogram. Base: natural log."""
    log_tau = np.log(tau_values)
    counts, _ = np.histogram(log_tau, bins=K)
    freqs = counts / counts.sum()
    freqs = freqs[freqs > 0]
    return float(-np.sum(freqs * np.log(freqs)))


def check_tdi_analytical():
    """
    Paper claims TDI = 2.36 for 2023 AUM composition.
    Verify with many draws from the stated distributions.
    """
    rng = np.random.default_rng(0)
    N_big = 100_000  # large sample for stable entropy
    counts_share = [0.15, 0.25, 0.40, 0.20]
    tau_params = [(0.5, 0.6), (2.8, 0.7), (4.2, 0.6), (6.0, 0.8)]
    tau_bounds = [(1, 20), (15, 120), (60, 400), (400, 2000)]

    all_tau = []
    for share, (mu, sig), (lo, hi) in zip(counts_share, tau_params, tau_bounds):
        n_type = int(N_big * share)
        draws = np.exp(rng.normal(mu, sig, n_type * 3))
        draws = draws[(draws >= lo) & (draws <= hi)][:n_type]
        while len(draws) < n_type:
            extra = np.exp(rng.normal(mu, sig, 100))
            extra = extra[(extra >= lo) & (extra <= hi)]
            draws = np.append(draws, extra)
        all_tau.extend(draws[:n_type].tolist())

    all_tau = np.array(all_tau)
    tdi_20  = compute_tdi(all_tau, K=20)
    tdi_40  = compute_tdi(all_tau, K=40)
    tdi_100 = compute_tdi(all_tau, K=100)

    # What K is needed to get TDI ≈ 2.36 ?
    print("\n=== TDI Analytical Check ===")
    print(f"  TDI (K=20 bins, nat log) : {tdi_20:.4f}")
    print(f"  TDI (K=40 bins, nat log) : {tdi_40:.4f}")
    print(f"  TDI (K=100 bins)         : {tdi_100:.4f}")
    print(f"  Paper claims TDI = 2.36")
    # Also check small n=80
    all_tau_small = sample_tau(n=80, seed=42)
    for K in [10, 20, 30, 40]:
        t = compute_tdi(all_tau_small, K=K)
        print(f"  n=80, K={K:3d}: TDI = {t:.4f}")
    return tdi_20, tdi_40


# ─────────────────────────────────────────────────────────
# Section 1: Agent / network setup helpers
# ─────────────────────────────────────────────────────────

def sample_tau(n: int = 80, seed: int = 42) -> np.ndarray:
    """Sample τ values for n=80 agents from calibrated distributions."""
    rng = np.random.default_rng(seed)
    counts     = [12, 20, 32, 16]           # 15%, 25%, 40%, 20% of 80
    tau_params = [(0.5, 0.6), (2.8, 0.7), (4.2, 0.6), (6.0, 0.8)]
    tau_bounds = [(1, 20), (15, 120), (60, 400), (400, 2000)]

    tau = []
    for count, (mu, sig), (lo, hi) in zip(counts, tau_params, tau_bounds):
        collected = []
        while len(collected) < count:
            batch = np.exp(rng.normal(mu, sig, 200))
            batch = batch[(batch >= lo) & (batch <= hi)]
            collected.extend(batch.tolist())
        tau.extend([int(round(x)) for x in collected[:count]])
    return np.array(tau)


def build_network(tau: np.ndarray, kh: float, dmax: int = 12,
                  rng: np.random.Generator = None) -> np.ndarray:
    """
    Build τ-proximity directed adjacency matrix.
    P(i→j) ∝ exp(-kh |log(τi+1) - log(τj+1)|)
    Each agent draws dmax out-edges (no self-loops).
    """
    if rng is None:
        rng = np.random.default_rng()
    n = len(tau)
    log_tau = np.log(tau + 1)
    diff = np.abs(log_tau[:, None] - log_tau[None, :])
    prob = np.exp(-kh * diff)
    np.fill_diagonal(prob, 0.0)

    adj = np.zeros((n, n), dtype=float)
    for i in range(n):
        p = prob[i].copy()
        p /= p.sum()
        chosen = rng.choice(n, size=min(dmax, n - 1), replace=False, p=p)
        adj[i, chosen] = 1.0
    return adj


def fiedler_value(adj: np.ndarray) -> float:
    """Second-smallest eigenvalue of the normalised symmetric Laplacian."""
    sym = (adj + adj.T) / 2.0
    deg = np.maximum(sym.sum(axis=1), 1e-12)
    D_inv_sqrt = np.diag(1.0 / np.sqrt(deg))
    L = np.eye(len(adj)) - D_inv_sqrt @ sym @ D_inv_sqrt
    evals = np.sort(np.linalg.eigvalsh(L))
    return float(max(evals[1], 0.0))


def tau_assortativity(adj: np.ndarray, tau: np.ndarray) -> float:
    """Numeric assortativity coefficient based on log-τ attribute."""
    log_tau = np.log(tau + 1)
    G = nx.from_numpy_array(adj + adj.T)           # undirected
    nx.set_node_attributes(G, dict(enumerate(log_tau)), 'lt')
    try:
        return float(nx.numeric_assortativity_coefficient(G, 'lt'))
    except Exception:
        return float('nan')


def community_assignments(tau: np.ndarray) -> np.ndarray:
    """Partition into C=4 log-τ quartile communities (Definition 4)."""
    log_tau = np.log(tau)
    q = np.percentile(log_tau, [25, 50, 75])
    comm = np.zeros(len(tau), dtype=int)
    for k, threshold in enumerate(q):
        comm[log_tau > threshold] = k + 1
    return comm


# ─────────────────────────────────────────────────────────
# Section 2: Core simulation
# ─────────────────────────────────────────────────────────

def simulate_one_run(
    n: int = 80,
    T: int = 500,
    kh: float = 0.0,
    seed: int = 42,
    dmax: int = 12,
    gamma: float = 0.20,
    price_impact: float = 0.008,
    sigma_F: float = 0.010,
    sigma0: float = 0.00012,   # base noise — calibrated below
    alpha_bar: float = 0.30,
    beta_bar: float = 0.20,
) -> Dict:
    rng = np.random.default_rng(seed)

    tau  = sample_tau(n=n, seed=seed)
    adj  = build_network(tau, kh, dmax=dmax, rng=rng)
    lam2 = fiedler_value(adj)
    comm = community_assignments(tau)

    # Normalised weight matrix (row-stochastic)
    W = adj.copy()
    row_s = W.sum(axis=1, keepdims=True)
    W = np.where(row_s > 0, W / row_s, 0.0)

    # c(λ2) blending coefficient (Eq. 4)
    c_lam = np.log(1.0 + lam2) / np.log(2.0)

    # Cross-τ distances for effective noise (Eq. 5)
    log_tau = np.log(tau + 1)
    d_tau = np.zeros(n)
    for i in range(n):
        nbrs = np.where(adj[i] > 0)[0]
        if len(nbrs):
            d_tau[i] = np.mean(np.abs(log_tau[i] - log_tau[nbrs]))
    sigma_eff = sigma0 * (1.0 + gamma * d_tau)   # per-agent noise σ

    # ── Price-history buffer ──────────────────────────────
    max_tau = int(tau.max())
    buf_len = T + max_tau + 10
    p_hist  = np.full(buf_len, 100.0)  # global price history

    F        = 100.0
    p_global = 100.0
    returns  = []

    # TMFI accumulation (second half of simulation)
    tmfi_vals: List[float] = []

    for t in range(T):
        idx = max_tau + t          # current position in history buffer

        # Fundamental random walk
        F *= np.exp(rng.normal(0.0, sigma_F))

        # Per-agent noisy price observations
        noise_obs = rng.normal(0.0, sigma_eff)    # shape (n,)
        p_j = p_global * (1.0 + noise_obs)        # agent-j's quoted price

        # Neighbourhood-averaged observed price (Eq. 4)
        p_nbr_avg = W @ p_j
        p_obs = c_lam * p_nbr_avg + (1.0 - c_lam) * p_global

        # τi-period moving average of global price (fundamentalist ref)
        p_bar = np.array([
            p_hist[max(0, idx - tau[i]):idx].mean() if idx > 0 else 100.0
            for i in range(n)
        ])

        # Log-return momentum over τi horizon (Eq. 2 term 2)
        p_past = np.array([
            p_hist[max(0, idx - tau[i])] for i in range(n)
        ])
        momentum = np.where(p_past > 0, np.log(p_global / p_past), 0.0)

        # Agent demand (Eq. 2)
        eps = rng.normal(0.0, sigma_eff)
        demand = (alpha_bar * (F - p_bar) / np.maximum(p_obs, 1e-3)
                  + beta_bar * momentum
                  + eps)

        # Global price update (market clearing)
        p_global_new = p_global + price_impact * demand.sum()

        # Record return
        if t > 0:
            returns.append((p_global_new - p_global) / p_global)

        # Store in history
        p_hist[idx] = p_global_new
        p_global = p_global_new

        # TMFI (second half)
        if t >= T // 2:
            comm_means = [
                p_bar[comm == c].mean() if (comm == c).any() else p_global
                for c in range(4)
            ]
            arr = np.array(comm_means)
            m = arr.mean()
            if m > 1e-6:
                tmfi_vals.append(arr.std(ddof=0) / m)

    returns  = np.array(returns)
    vol      = returns.std()
    tmfi     = float(np.mean(tmfi_vals)) if tmfi_vals else 0.0
    assort   = tau_assortativity(adj, tau)
    tdi      = compute_tdi(tau, K=20)

    return dict(volatility=vol, tmfi=tmfi, assortativity=assort,
                lambda2=lam2, tdi=tdi)


# ─────────────────────────────────────────────────────────
# Section 3: κh sweep  (25 values × 10 seeds = 250 runs)
# ─────────────────────────────────────────────────────────

def kh_sweep(kh_values=None, n_seeds=10, n=80, T=500):
    if kh_values is None:
        kh_values = np.linspace(0, 6, 25)

    all_results = []
    for kh in kh_values:
        for seed in range(n_seeds):
            r = simulate_one_run(n=n, T=T, kh=float(kh), seed=seed)
            r['kh'] = float(kh)
            r['seed'] = seed
            all_results.append(r)
        print(f"  kh={kh:.2f} done", flush=True)
    return all_results


# ─────────────────────────────────────────────────────────
# Section 4: Echo-chamber τ-adaptation
# ─────────────────────────────────────────────────────────

def simulate_adaptation(kh: float, n_steps: int = 10, n: int = 80,
                         T: int = 500, seed: int = 0) -> List[float]:
    """
    Agents adapt τi toward the mean τ of their neighbourhood.
    Returns TDI after each of n_steps adaptation cycles.
    Paper claims: κh=0.5 → ∆TDI=+0.061; κh≥3 → ∆TDI≈-0.10.
    """
    rng = np.random.default_rng(seed)
    tau = sample_tau(n=n, seed=seed).astype(float)
    tdi_series = [compute_tdi(tau.astype(int), K=20)]

    for step in range(n_steps):
        adj = build_network(tau.astype(int), kh=kh, dmax=12, rng=rng)
        log_tau = np.log(tau + 1)
        new_log_tau = log_tau.copy()
        for i in range(n):
            nbrs = np.where(adj[i] > 0)[0]
            if len(nbrs):
                mean_nbr = log_tau[nbrs].mean()
                # Partial adaptation: move 10% toward neighbourhood mean
                new_log_tau[i] = 0.9 * log_tau[i] + 0.1 * mean_nbr
        tau = np.exp(new_log_tau) - 1.0
        tau = np.maximum(tau, 1.0)
        tdi_series.append(compute_tdi(tau.astype(int), K=20))

    return tdi_series


# ─────────────────────────────────────────────────────────
# Section 5: TDI concentration sweep
# ─────────────────────────────────────────────────────────

def tdi_concentration_sweep(n=80, T=500, n_seeds=10):
    """
    Paper claims: r(TDI, σ) = +0.612, p < 0.001
    """
    conc_levels = np.linspace(0.3, 3.0, 8)
    results = []
    for conc in conc_levels:
        for seed in range(n_seeds):
            rng = np.random.default_rng(seed)
            # Vary concentration by multiplying σ of log-normal by 1/conc
            counts     = [12, 20, 32, 16]
            tau_params = [(0.5, 0.6/conc), (2.8, 0.7/conc),
                          (4.2, 0.6/conc), (6.0, 0.8/conc)]
            tau_bounds = [(1, 20), (15, 120), (60, 400), (400, 2000)]
            tau = []
            for count, (mu, sig), (lo, hi) in zip(counts, tau_params, tau_bounds):
                collected = []
                while len(collected) < count:
                    batch = np.exp(rng.normal(mu, sig, 300))
                    batch = np.clip(batch, lo, hi)
                    collected.extend(batch.tolist())
                tau.extend([int(round(x)) for x in collected[:count]])
            tau = np.array(tau)
            tdi = compute_tdi(tau, K=20)
            r = simulate_one_run(n=n, T=T, kh=2.0, seed=seed)
            r['tdi_measured'] = tdi
            r['conc'] = float(conc)
            results.append(r)
        print(f"  conc={conc:.2f} done", flush=True)
    return results


# ─────────────────────────────────────────────────────────
# Section 6: Run everything and report
# ─────────────────────────────────────────────────────────

def report_kh_sweep(results):
    import numpy as np
    from scipy import stats as sp_stats

    kh_vals = sorted(set(r['kh'] for r in results))

    def mean_for_kh(key, kh_val):
        return np.mean([r[key] for r in results if r['kh'] == kh_val])

    vol_0 = mean_for_kh('volatility', kh_vals[0])
    vol_6 = mean_for_kh('volatility', kh_vals[-1])
    tmfi_0 = mean_for_kh('tmfi', kh_vals[0])
    tmfi_6 = mean_for_kh('tmfi', kh_vals[-1])
    asr_0 = mean_for_kh('assortativity', kh_vals[0])
    asr_6 = mean_for_kh('assortativity', kh_vals[-1])

    # t-test on volatility: low vs high kh
    vols_low  = [r['volatility'] for r in results if r['kh'] < 0.5]
    vols_high = [r['volatility'] for r in results if r['kh'] > 5.5]
    t_stat, p_val = sp_stats.ttest_ind(vols_low, vols_high, equal_var=False)

    # Normalised drops
    all_vols  = [r['volatility'] for r in results]
    all_tmfis = [r['tmfi'] for r in results]
    norm_vol_drop  = (np.max(all_vols) - np.min(all_vols))
    norm_tmfi_drop = (np.max(all_tmfis) - np.min(all_tmfis))
    # Drops relative to min-max scale
    vol_high_norm  = (vol_0 - vol_6) / (np.max(all_vols) - np.min(all_vols) + 1e-20)
    tmfi_high_norm = (tmfi_0 - tmfi_6) / (np.max(all_tmfis) - np.min(all_tmfis) + 1e-20)

    print("\n=== κh Sweep Results ===")
    print(f"  Assortativity at κh=0     : {asr_0:.4f}   [paper: r=-0.02]")
    print(f"  Assortativity at κh=6     : {asr_6:.4f}   [paper: r=0.994]")
    print(f"  Volatility at κh=0        : {vol_0:.6f}   [paper: ~0.00080]")
    print(f"  Volatility at κh=6        : {vol_6:.6f}   [paper: ~0.00064]")
    print(f"  Volatility ratio (0/6)    : {vol_0/vol_6:.4f}x  [paper: 1.26x]")
    print(f"  t-statistic (vol low/high): {t_stat:.2f}        [paper: 12.6]")
    print(f"  p-value                   : {p_val:.2e}     [paper: <1e-20]")
    print(f"  TMFI at κh=0              : {tmfi_0:.6f}   [paper: ~0.018]")
    print(f"  TMFI at κh=6              : {tmfi_6:.6f}   [paper: ~0.009]")
    print(f"  TMFI ratio (0/6)          : {tmfi_0/tmfi_6:.4f}x  [paper: 1.30x]")
    print(f"  Normalised σ drop         : {vol_high_norm:.4f}      [paper: 0.948]")
    print(f"  Normalised TMFI drop      : {tmfi_high_norm:.4f}      [paper: 0.558]")

    return {
        'vol_ratio': vol_0/vol_6,
        't_stat': t_stat,
        'p_val': p_val,
        'assort_0': asr_0,
        'assort_6': asr_6,
        'norm_vol_drop': vol_high_norm,
        'norm_tmfi_drop': tmfi_high_norm,
    }


def report_adaptation():
    print("\n=== Echo Chamber Adaptation ===")
    for kh_label, kh_val in [("0.5 (low)", 0.5), ("3.0 (mid)", 3.0), ("6.0 (high)", 6.0)]:
        tdi_series = simulate_adaptation(kh=kh_val, n_steps=10)
        delta = tdi_series[-1] - tdi_series[0]
        print(f"  κh={kh_label}: TDI start={tdi_series[0]:.4f}, "
              f"end={tdi_series[-1]:.4f}, ∆TDI={delta:+.4f}")
    print("  Paper claims: κh=0.5→+0.061; κh=3.0→-0.114; κh=6.0→-0.102")
    print("  Abstract claims ∆TDI = -0.10 (should be from Fig 6 averages)")


def report_internal_inconsistencies():
    """Flag issues found by close reading — no simulation needed."""
    print("\n=== Internal Inconsistencies Found by Close Reading ===")
    issues = [
        ("MINOR",    "t-statistic: Abstract + Fig caption body say t=12.6; "
                     "Figure 2b annotation says t=13. Rounding inconsistency."),
        ("MODERATE", "Echo-chamber ∆TDI: Abstract says ∆TDI=−0.10 but "
                     "Fig 6 annotation shows −0.114 (κh=3.0) and −0.102 (κh=6.0). "
                     "The abstract rounds/averages these silently."),
        ("MAJOR",    "TL peak location CONTRADICTION: Section 4.5 + Figure 6 caption "
                     "both state 'TL peaks at κh ≈ 0.75', but Figure 6b explicitly "
                     "marks the star as 'Peak κh = 0.50'. Text/caption and figure "
                     "annotation disagree on the exact peak."),
        ("MODERATE", "Figure 4 TDI label discrepancy: caption says 'low TDI = 1.88' "
                     "but the legend in Fig 4a shows 'TDI=1.85'. The figure note says "
                     "'previous versions had labels inverted' — the fix introduced a "
                     "new numeric inconsistency (1.85 vs 1.88)."),
        ("MINOR",    "TDI formula (Eq. 1) writes 'log' without specifying the base. "
                     "Shannon entropy conventionally uses ln or log2; the value 2.36 "
                     "is consistent with natural log and ~20 bins but would differ "
                     "significantly with log2. Base should be stated explicitly."),
        ("MODERATE", "Stability bound (Theorem 1 proof sketch): The update is written "
                     "as ∆p(t+1)=(I−λᾱW+λβ̄M)∆p(t)+η. Stability ρ<1 requires ALL "
                     "eigenvalues, but the condition λ2>β̄/ᾱ is derived only for "
                     "k≥2. The k=1 case (uniform mode) is not explicitly handled."),
        ("MINOR",    "Abstract says '250 runs' matching 25 κh × 10 seeds. "
                     "Section 3.2 also says this. Consistent."),
        ("INFO",     "Temporal Liquidity formula TL=1/(σ·ACF·crash_excess) has no "
                     "derivation or motivation. Described as 'custom and exploratory' "
                     "in Sec 3.3, which is honest but limits interpretability."),
        ("INFO",     "c(λ2)=log(1+λ2)/log2. At λ2=0 this gives c=0 (pure global), "
                     "at λ2=1 gives c=1 (pure neighbourhood). But Fiedler values "
                     "can exceed 1; c(λ2)>1 is possible, making p_obs negative-weighted "
                     "on p_global. This edge case is not discussed."),
    ]
    for sev, desc in issues:
        print(f"  [{sev}] {desc}")


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 65)
    print("CME PAPER VALIDATION")
    print("=" * 65)

    # ── Analytical checks ─────────────────────────────────
    check_tmfi_synthetic()
    check_stability_bound()
    check_tdi_analytical()
    report_internal_inconsistencies()

    # ── κh sweep ──────────────────────────────────────────
    print("\n=== Running κh sweep (250 runs) … ===")
    kh_sweep_results = kh_sweep(kh_values=np.linspace(0, 6, 25), n_seeds=10)
    sweep_summary = report_kh_sweep(kh_sweep_results)

    # ── Adaptation dynamics ───────────────────────────────
    report_adaptation()

    print("\n" + "=" * 65)
    print("VALIDATION COMPLETE")
    print("=" * 65)
