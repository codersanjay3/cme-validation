"""
CME Paper Validation v2 — calibration-corrected simulation.

Key fix from v1:
  sigma0 must be ~1.0 (not 0.00012). The friction mechanism (Eq. 5)
  must dominate so that cross-τ noise drives the volatility ratio.
  With σ0=1.0, λ=0.008, n=80:  vol ≈ λ*√n*σ0/p ≈ 0.00071 ✓
"""

import numpy as np
from scipy import stats as sp_stats
import networkx as nx
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def compute_tdi(tau_values: np.ndarray, K: int = 20) -> float:
    log_tau = np.log(np.maximum(tau_values, 1))
    counts, _ = np.histogram(log_tau, bins=K)
    freqs = counts / counts.sum()
    freqs = freqs[freqs > 0]
    return float(-np.sum(freqs * np.log(freqs)))


def sample_tau(n: int = 80, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    counts     = [12, 20, 32, 16]
    tau_params = [(0.5, 0.6), (2.8, 0.7), (4.2, 0.6), (6.0, 0.8)]
    tau_bounds = [(1, 20), (15, 120), (60, 400), (400, 2000)]
    tau = []
    for count, (mu, sig), (lo, hi) in zip(counts, tau_params, tau_bounds):
        collected: List[float] = []
        while len(collected) < count:
            batch = np.exp(rng.normal(mu, sig, 400))
            batch = batch[(batch >= lo) & (batch <= hi)]
            collected.extend(batch.tolist())
        tau.extend([max(1, int(round(x))) for x in collected[:count]])
    return np.array(tau)


def build_network(tau: np.ndarray, kh: float, dmax: int = 12,
                  rng: np.random.Generator = None) -> np.ndarray:
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
    sym = (adj + adj.T) / 2.0
    deg = np.maximum(sym.sum(axis=1), 1e-12)
    D_inv_sqrt = np.diag(1.0 / np.sqrt(deg))
    L = np.eye(len(adj)) - D_inv_sqrt @ sym @ D_inv_sqrt
    evals = np.sort(np.linalg.eigvalsh(L))
    return float(max(evals[1], 0.0))


def tau_assortativity(adj: np.ndarray, tau: np.ndarray) -> float:
    log_tau = np.log(tau + 1)
    G = nx.from_numpy_array(adj + adj.T)
    nx.set_node_attributes(G, dict(enumerate(log_tau)), 'lt')
    try:
        return float(nx.numeric_assortativity_coefficient(G, 'lt'))
    except Exception:
        return float('nan')


def community_assignments(tau: np.ndarray) -> np.ndarray:
    log_tau = np.log(tau)
    q = np.percentile(log_tau, [25, 50, 75])
    comm = np.zeros(len(tau), dtype=int)
    for k, threshold in enumerate(q):
        comm[log_tau > threshold] = k + 1
    return comm


# ─────────────────────────────────────────────────────────────────────────────
# Core simulation  (sigma0 = 1.0 — calibrated to match paper's vol scale)
# ─────────────────────────────────────────────────────────────────────────────

def simulate_one_run(
    n: int = 80,
    T: int = 500,
    kh: float = 0.0,
    seed: int = 42,
    dmax: int = 12,
    gamma: float = 0.20,
    price_impact: float = 0.008,
    sigma_F: float = 0.010,
    sigma0: float = 1.0,       # <── calibrated so noise dominates; vol~0.0007
    alpha_bar: float = 0.30,
    beta_bar: float = 0.20,
) -> Dict:
    rng = np.random.default_rng(seed)

    tau  = sample_tau(n=n, seed=seed)
    adj  = build_network(tau, kh, dmax=dmax, rng=rng)
    lam2 = fiedler_value(adj)
    comm = community_assignments(tau)

    W = adj.copy()
    row_s = W.sum(axis=1, keepdims=True)
    W = np.where(row_s > 0, W / row_s, 0.0)

    c_lam = np.log(1.0 + lam2) / np.log(2.0)

    # Cross-τ distances → effective noise (Eq. 5)
    log_tau = np.log(tau + 1)
    d_tau = np.zeros(n)
    for i in range(n):
        nbrs = np.where(adj[i] > 0)[0]
        if len(nbrs):
            d_tau[i] = np.mean(np.abs(log_tau[i] - log_tau[nbrs]))
    sigma_eff = sigma0 * (1.0 + gamma * d_tau)   # per-agent demand noise std

    max_tau = int(tau.max())
    # Per-agent noisy observation history buffers
    p_obs_hist = np.zeros((n, T + max_tau + 10))  # each agent's noisy observations
    p_global_hist = np.zeros(T + max_tau + 10)
    p_global_hist[:max_tau + 1] = 100.0
    p_obs_hist[:, :max_tau + 1] = 100.0

    F        = 100.0
    p_global = 100.0
    returns: List[float] = []
    tmfi_vals: List[float] = []

    for t in range(T):
        idx = max_tau + t

        F *= np.exp(rng.normal(0.0, sigma_F))

        # Noisy price observed by each agent (Eq. 4 + 5)
        noise_j = rng.normal(0.0, sigma_eff)           # shape (n,)
        p_j     = p_global * (1.0 + noise_j)
        p_nbr   = W @ p_j
        p_obs   = c_lam * p_nbr + (1.0 - c_lam) * p_global  # per-agent (n,)

        # Moving average of each agent's own noisy observations
        p_bar = np.array([
            p_obs_hist[i, max(0, idx - tau[i]):idx].mean()
            if idx > 0 else 100.0
            for i in range(n)
        ])

        # Log-return momentum from agent's own observation history
        p_past = np.array([
            p_obs_hist[i, max(0, idx - tau[i])]
            for i in range(n)
        ])
        momentum = np.where(p_past > 0, np.log(np.maximum(p_obs, 1e-6) /
                                                np.maximum(p_past, 1e-6)), 0.0)

        # Demand (Eq. 2)
        eps    = rng.normal(0.0, sigma_eff)
        demand = (alpha_bar * (F - p_bar) / np.maximum(p_obs, 1e-3)
                  + beta_bar * momentum
                  + eps)

        p_new = p_global + price_impact * demand.sum()

        if t > 0:
            returns.append((p_new - p_global) / p_global)

        p_global_hist[idx]      = p_new
        p_obs_hist[:, idx]      = p_obs   # store each agent's observation
        p_global = p_new

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


# ─────────────────────────────────────────────────────────────────────────────
# κh sweep
# ─────────────────────────────────────────────────────────────────────────────

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
        # progress
        vols = [r['volatility'] for r in all_results if r['kh'] == float(kh)]
        print(f"  kh={kh:.2f}  mean vol={np.mean(vols):.6f}", flush=True)
    return all_results


# ─────────────────────────────────────────────────────────────────────────────
# Adaptation dynamics
# ─────────────────────────────────────────────────────────────────────────────

def simulate_adaptation(kh: float, n_steps: int = 10, n: int = 80,
                        seed: int = 0, adapt_rate: float = 0.05) -> List[float]:
    """
    Agents partially adapt τ toward neighbourhood mean each cycle.
    adapt_rate=5% matches paper's ∆TDI magnitudes better than 10%.
    """
    rng = np.random.default_rng(seed)
    tau = sample_tau(n=n, seed=seed).astype(float)
    tdi_series = [compute_tdi(tau.astype(int), K=20)]

    for _ in range(n_steps):
        adj = build_network(tau.astype(int), kh=kh, dmax=12, rng=rng)
        log_tau = np.log(np.maximum(tau, 1) + 1)
        new_log_tau = log_tau.copy()
        for i in range(n):
            nbrs = np.where(adj[i] > 0)[0]
            if len(nbrs):
                mean_nbr = log_tau[nbrs].mean()
                new_log_tau[i] = (1 - adapt_rate) * log_tau[i] + adapt_rate * mean_nbr
        tau = np.exp(new_log_tau) - 1.0
        tau = np.maximum(tau, 1.0)
        tdi_series.append(compute_tdi(tau.astype(int), K=20))

    return tdi_series


# ─────────────────────────────────────────────────────────────────────────────
# Report
# ─────────────────────────────────────────────────────────────────────────────

def report_kh_sweep(results):
    kh_vals = sorted(set(r['kh'] for r in results))

    def mean_for_kh(key, kh_val):
        return np.mean([r[key] for r in results if r['kh'] == kh_val])

    vol_0  = mean_for_kh('volatility', kh_vals[0])
    vol_6  = mean_for_kh('volatility', kh_vals[-1])
    tmfi_0 = mean_for_kh('tmfi', kh_vals[0])
    tmfi_6 = mean_for_kh('tmfi', kh_vals[-1])
    asr_0  = mean_for_kh('assortativity', kh_vals[0])
    asr_6  = mean_for_kh('assortativity', kh_vals[-1])

    vols_low  = [r['volatility'] for r in results if r['kh'] < 0.5]
    vols_high = [r['volatility'] for r in results if r['kh'] > 5.5]
    t_stat, p_val = sp_stats.ttest_ind(vols_low, vols_high, equal_var=False)

    all_vols  = np.array([r['volatility'] for r in results])
    all_tmfis = np.array([r['tmfi'] for r in results])
    vol_range  = all_vols.max()  - all_vols.min()
    tmfi_range = all_tmfis.max() - all_tmfis.min()
    norm_vol_drop  = (vol_0 - vol_6)  / (vol_range  + 1e-30)
    norm_tmfi_drop = (tmfi_0 - tmfi_6) / (tmfi_range + 1e-30)

    print("\n=== κh Sweep — v2 Results ===")
    print(f"  Assortativity kh=0  : {asr_0:+.4f}  [paper: −0.02]")
    print(f"  Assortativity kh=6  : {asr_6:+.4f}  [paper: +0.994]")
    print(f"  Volatility kh=0     : {vol_0:.6f}  [paper: ~0.00080]")
    print(f"  Volatility kh=6     : {vol_6:.6f}  [paper: ~0.00064]")
    direction = "↓ correct" if vol_0 > vol_6 else "↑ WRONG DIRECTION"
    print(f"  Volatility ratio    : {vol_0/max(vol_6,1e-30):.4f}×  [paper: 1.26×]  {direction}")
    print(f"  t-stat (low vs high): {t_stat:.2f}  [paper: 12.6]")
    print(f"  p-value             : {p_val:.2e}  [paper: <1e-20]")
    print(f"  TMFI kh=0           : {tmfi_0:.6f}  [paper: ~0.018]")
    print(f"  TMFI kh=6           : {tmfi_6:.6f}  [paper: ~0.009]")
    direction2 = "↓ correct" if tmfi_0 > tmfi_6 else "↑ WRONG DIRECTION"
    print(f"  TMFI ratio          : {tmfi_0/max(tmfi_6,1e-30):.4f}×  [paper: 1.30×]  {direction2}")
    print(f"  Norm σ drop         : {norm_vol_drop:.4f}   [paper: 0.948]")
    print(f"  Norm TMFI drop      : {norm_tmfi_drop:.4f}   [paper: 0.558]")
    return dict(vol_ratio=vol_0/max(vol_6,1e-30), t_stat=t_stat, p_val=p_val,
                norm_vol_drop=norm_vol_drop, norm_tmfi_drop=norm_tmfi_drop)


def report_adaptation():
    print("\n=== Echo Chamber Adaptation (adapt_rate=5%) ===")
    for label, kh_val in [("0.5 (low)", 0.5), ("3.0 (mid)", 3.0), ("6.0 (high)", 6.0)]:
        tdi_series = simulate_adaptation(kh=kh_val, n_steps=10, adapt_rate=0.05)
        delta = tdi_series[-1] - tdi_series[0]
        print(f"  κh={label}: start={tdi_series[0]:.4f} end={tdi_series[-1]:.4f} "
              f"∆TDI={delta:+.4f}")
    print("  Paper: κh=0.5→+0.061; κh=3.0→−0.114; κh=6.0→−0.102")
    print("  Abstract: ∆TDI = −0.10 (rounding of Fig 6 values)")


def check_tmfi_synthetic():
    prices = np.array([90., 95., 100., 110.])
    mean_p = prices.mean()
    std_p  = prices.std(ddof=0)
    tmfi   = std_p / mean_p
    print("=== TMFI Synthetic Validation ===")
    print(f"  TMFI (pop std) = {tmfi:.6f}  [paper: analytical=0.074]  "
          f"PASS: {abs(tmfi-0.074)<0.002}")


def check_stability_bound():
    bound = 0.20 / 0.30
    print(f"\n=== Stability Bound ===")
    print(f"  β̄/ᾱ = 0.20/0.30 = {bound:.6f}  [paper: 0.667]  PASS: {abs(bound-0.667)<0.001}")


def check_tdi_vs_K():
    tau = sample_tau(n=80, seed=42)
    print("\n=== TDI vs K (n=80 agents) ===")
    for K in [8, 10, 12, 14, 16, 20, 25]:
        print(f"  K={K:3d}: TDI = {compute_tdi(tau, K):.4f}")
    print("  Paper claims TDI = 2.36 (K not stated in paper)")


def report_internal_inconsistencies():
    print("\n=== Internal Inconsistencies (close reading) ===")
    issues = [
        ("MAJOR",    "Temporal Liquidity peak contradiction: Sec 4.5 and Fig 6 caption "
                     "say 'TL peaks at κh≈0.75' but the star in Fig 6b is explicitly "
                     "labelled 'Peak κh=0.50'. Caption and figure annotation disagree."),
        ("MAJOR",    "TDI formula (Eq. 1) does not specify the log base. The value "
                     "TDI=2.36 can only be reproduced knowing K (number of histogram "
                     "bins), which is never stated. K≈12 gives TDI≈2.36 for n=80; "
                     "K=20 gives TDI≈2.52. This makes the claim non-reproducible."),
        ("MODERATE", "Abstract says ∆TDI=−0.10, but Fig 6 shows −0.114 (κh=3.0) and "
                     "−0.102 (κh=6.0). The abstract silently averages/rounds these."),
        ("MODERATE", "Fig 4 caption says 'low TDI=1.88' but Fig 4a legend shows "
                     "'TDI=1.85'. The stated correction for inverted labels introduced "
                     "a new 3-unit numeric inconsistency."),
        ("MODERATE", "Theorem 1 proof: the stability condition λ2>β̄/ᾱ is derived only "
                     "for k≥2. The k=1 (uniform) eigenmode is not handled. If the "
                     "uniform mode is unstable the whole claim fails. Needs a complete "
                     "proof covering all modes."),
        ("MINOR",    "t-statistic: abstract/body say t=12.6; Fig 2b annotation says "
                     "t=13. Rounding inconsistency — should be consistent throughout."),
        ("MINOR",    "c(λ2)=log(1+λ2)/log2: at λ2>1 this exceeds 1, making the "
                     "global-price weight (1−c) negative. This edge case is not "
                     "discussed and could produce unstable prices."),
        ("INFO",     "Temporal Liquidity TL=1/(σ·ACF·crash_excess) has no derivation "
                     "and is described as 'custom and exploratory'. Its use in the "
                     "'Goldilocks zone' figure should be clearly labelled exploratory "
                     "throughout, not just in Sec 3.3."),
        ("INFO",     "All five historical compositions give λ2≈0 (well below 0.667) "
                     "but the paper doesn't explain why a connected market should have "
                     "Fiedler values this low. This may be a model artefact of fixing "
                     "homophily rather than varying the network structure."),
    ]
    for sev, desc in issues:
        print(f"\n  [{sev}]")
        # word-wrap
        words = desc.split()
        line = "    "
        for w in words:
            if len(line)+len(w)+1 > 78:
                print(line)
                line = "    " + w + " "
            else:
                line += w + " "
        if line.strip():
            print(line)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 65)
    print("CME PAPER VALIDATION  v2")
    print("=" * 65)

    check_tmfi_synthetic()
    check_stability_bound()
    check_tdi_vs_K()
    report_internal_inconsistencies()

    print("\n=== Running κh sweep (250 runs, v2) … ===")
    kh_results = kh_sweep(kh_values=np.linspace(0, 6, 25), n_seeds=10)
    sweep_summary = report_kh_sweep(kh_results)

    report_adaptation()

    print("\n" + "=" * 65)
    print("DONE")
    print("=" * 65)
