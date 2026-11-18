"""
CME Paper Validation v3 — architecture-corrected model.

Key insight from v2 failure:
  The paper's friction mechanism (Eq. 5) enters as *demand noise* (ε), NOT
  through the price-history used for the moving average. Using noisy p_obs
  to compute p_bar feeds back through momentum → price runaway at kh=0.

Correct architecture:
  - DEMAND  uses global-price MA and global-price momentum (stable).
  - ε_i ~ N(0, σ_eff_i) carries the friction-amplified noise.
  - p_obs  (neighbourhood-blended, noisy) is used ONLY for TMFI computation.

This matches the paper's stated mechanism: "cross-τ friction amplifies
effective noise" feeds into volatility through ε, while the neighbourhood
price divergence feeds into TMFI through p_obs.
"""

import numpy as np
from scipy import stats as sp_stats
import networkx as nx
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# Helpers (same as v2)
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
                  rng=None) -> np.ndarray:
    if rng is None:
        rng = np.random.default_rng()
    n = len(tau)
    log_tau = np.log(tau + 1)
    diff = np.abs(log_tau[:, None] - log_tau[None, :])
    prob = np.exp(-kh * diff)
    np.fill_diagonal(prob, 0.0)
    adj = np.zeros((n, n), dtype=float)
    for i in range(n):
        p = prob[i].copy(); p /= p.sum()
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
# Core simulation — v3 (architecture-corrected)
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
    sigma0: float = 1.0,
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

    # Cross-τ friction (Eq. 5)
    log_tau = np.log(tau + 1)
    d_tau = np.zeros(n)
    for i in range(n):
        nbrs = np.where(adj[i] > 0)[0]
        if len(nbrs):
            d_tau[i] = np.mean(np.abs(log_tau[i] - log_tau[nbrs]))
    sigma_eff = sigma0 * (1.0 + gamma * d_tau)   # per-agent ε std

    max_tau = int(tau.max())
    buf_len = T + max_tau + 10
    p_global_hist = np.full(buf_len, 100.0)

    # Noisy-observation history for TMFI (per-agent, but cheaper: store community means)
    comm_p_obs_hist = {c: [] for c in range(4)}

    F        = 100.0
    p_global = 100.0
    returns: List[float] = []
    tmfi_vals: List[float] = []

    for t in range(T):
        idx = max_tau + t

        F *= np.exp(rng.normal(0.0, sigma_F))

        # ── DEMAND: uses global-price MA and global-price momentum  (stable) ──
        p_bar_global = np.array([
            p_global_hist[max(0, idx - tau[i]):idx].mean()
            if idx > 0 else 100.0
            for i in range(n)
        ])
        p_past_global = np.array([
            p_global_hist[max(0, idx - tau[i])]
            for i in range(n)
        ])
        momentum_global = np.where(
            p_past_global > 0,
            np.log(max(p_global, 1e-6) / np.maximum(p_past_global, 1e-6)), 0.0)

        # Friction-amplified demand noise (Eq. 5 — main mechanism)
        eps = rng.normal(0.0, sigma_eff)   # shape (n,)

        demand = (alpha_bar * (F - p_bar_global) / max(p_global, 1e-3)
                  + beta_bar * momentum_global
                  + eps)

        p_new = p_global + price_impact * demand.sum()

        if t > 0:
            returns.append((p_new - p_global) / p_global)

        p_global_hist[idx] = p_new
        p_global = p_new

        # ── p_obs for TMFI: neighbourhood-blended, noisy (Eq. 4 + 5) ──────
        # Only computed for TMFI (second half) to save time
        if t >= T // 2:
            noise_obs = rng.normal(0.0, sigma_eff)
            p_j      = p_global * (1.0 + noise_obs)
            p_nbr    = W @ p_j
            p_obs_i  = c_lam * p_nbr + (1.0 - c_lam) * p_global   # (n,)

            # Community mean of noisy observations → TMFI
            comm_means = []
            for c in range(4):
                mask = comm == c
                if mask.any():
                    comm_means.append(p_obs_i[mask].mean())
                else:
                    comm_means.append(p_global)
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
                lambda2=lam2, tdi=tdi, d_tau_mean=d_tau.mean())


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
            r['kh'] = float(kh); r['seed'] = seed
            all_results.append(r)
        vols  = [r['volatility'] for r in all_results if r['kh'] == float(kh)]
        dtaus = [r['d_tau_mean'] for r in all_results if r['kh'] == float(kh)]
        print(f"  kh={kh:.2f}  vol={np.mean(vols):.6f}  d_tau={np.mean(dtaus):.3f}",
              flush=True)
    return all_results


# ─────────────────────────────────────────────────────────────────────────────
# Adaptation
# ─────────────────────────────────────────────────────────────────────────────

def simulate_adaptation(kh: float, n_steps: int = 10, n: int = 80,
                        seed: int = 0, adapt_rate: float = 0.15) -> List[float]:
    rng  = np.random.default_rng(seed)
    tau  = sample_tau(n=n, seed=seed).astype(float)
    tdi_series = [compute_tdi(tau.astype(int), K=20)]
    for _ in range(n_steps):
        adj     = build_network(tau.astype(int), kh=kh, dmax=12, rng=rng)
        log_tau = np.log(np.maximum(tau, 1) + 1)
        new_log = log_tau.copy()
        for i in range(n):
            nbrs = np.where(adj[i] > 0)[0]
            if len(nbrs):
                mean_nbr  = log_tau[nbrs].mean()
                new_log[i] = (1 - adapt_rate) * log_tau[i] + adapt_rate * mean_nbr
        tau = np.exp(new_log) - 1.0
        tau = np.maximum(tau, 1.0)
        tdi_series.append(compute_tdi(tau.astype(int), K=20))
    return tdi_series


# ─────────────────────────────────────────────────────────────────────────────
# Reports
# ─────────────────────────────────────────────────────────────────────────────

def report_kh_sweep(results):
    kh_vals = sorted(set(r['kh'] for r in results))
    def mean_kh(key, kh): return np.mean([r[key] for r in results if r['kh'] == kh])

    vol_0  = mean_kh('volatility', kh_vals[0])
    vol_6  = mean_kh('volatility', kh_vals[-1])
    tmfi_0 = mean_kh('tmfi', kh_vals[0])
    tmfi_6 = mean_kh('tmfi', kh_vals[-1])
    asr_0  = mean_kh('assortativity', kh_vals[0])
    asr_6  = mean_kh('assortativity', kh_vals[-1])
    lam_0  = mean_kh('lambda2', kh_vals[0])
    lam_6  = mean_kh('lambda2', kh_vals[-1])

    vols_low  = [r['volatility'] for r in results if r['kh'] < 0.5]
    vols_high = [r['volatility'] for r in results if r['kh'] > 5.5]
    t_stat, p_val = sp_stats.ttest_ind(vols_low, vols_high, equal_var=False)

    all_vols  = np.array([r['volatility'] for r in results])
    all_tmfis = np.array([r['tmfi'] for r in results])
    vr  = vol_0 / max(vol_6, 1e-30)
    nvd = (vol_0 - vol_6) / (all_vols.max() - all_vols.min() + 1e-30)
    ntd = (tmfi_0 - tmfi_6) / (all_tmfis.max() - all_tmfis.min() + 1e-30)

    print("\n=== κh Sweep Results (v3) ===")
    print(f"  Assortativity kh=0  : {asr_0:+.4f}   [paper: −0.02]")
    print(f"  Assortativity kh=6  : {asr_6:+.4f}   [paper: +0.994]")
    print(f"  λ2 at kh=0          : {lam_0:.4f}   [paper implies high λ2 → c≈1]")
    print(f"  λ2 at kh=6          : {lam_6:.4f}   [paper implies λ2≈0]")
    print(f"  Volatility kh=0     : {vol_0:.6f}   [paper: ~0.00080]")
    print(f"  Volatility kh=6     : {vol_6:.6f}   [paper: ~0.00064]")
    dir_v = '✓ correct' if vol_0 > vol_6 else '✗ WRONG DIRECTION'
    print(f"  Volatility ratio    : {vr:.4f}×   [paper: 1.26×]  {dir_v}")
    print(f"  t-stat (low vs hi)  : {t_stat:.2f}     [paper: 12.6]")
    print(f"  p-value             : {p_val:.2e}  [paper: <1e-20]")
    print(f"  TMFI kh=0           : {tmfi_0:.6f}   [paper: ~0.018]")
    print(f"  TMFI kh=6           : {tmfi_6:.6f}   [paper: ~0.009]")
    dir_t = '✓ correct' if tmfi_0 > tmfi_6 else '✗ WRONG DIRECTION'
    print(f"  TMFI ratio          : {tmfi_0/max(tmfi_6,1e-30):.4f}×   [paper: 1.30×]  {dir_t}")
    print(f"  Norm σ drop         : {nvd:.4f}    [paper: 0.948]")
    print(f"  Norm TMFI drop      : {ntd:.4f}    [paper: 0.558]")
    return dict(vol_ratio=vr, t_stat=t_stat, p_val=p_val,
                norm_vol_drop=nvd, norm_tmfi_drop=ntd)


def report_adaptation():
    print("\n=== Echo Chamber Adaptation ===")
    for label, kh_val, rate in [
        ("0.5 (low)", 0.5,  0.15),
        ("3.0 (mid)", 3.0,  0.15),
        ("6.0 (high)", 6.0, 0.15),
    ]:
        s = simulate_adaptation(kh=kh_val, n_steps=10, adapt_rate=rate)
        delta = s[-1] - s[0]
        print(f"  κh={label}: start={s[0]:.4f} end={s[-1]:.4f} ∆TDI={delta:+.4f}")
    print("  Paper: κh=0.5→+0.061; κh=3.0→−0.114; κh=6.0→−0.102")
    print("  Abstract: −0.10 (silent average of Fig 6 values)")


def analytical_checks():
    prices = np.array([90., 95., 100., 110.])
    tmfi_analytical = prices.std(ddof=0) / prices.mean()
    stab = 0.20 / 0.30

    print("=== Analytical / Formula Checks ===")
    print(f"  TMFI synthetic (pop std): {tmfi_analytical:.6f}  [paper: 0.074]  "
          f"PASS={abs(tmfi_analytical-0.074)<0.002}")
    print(f"  Stability bound β̄/ᾱ    : {stab:.6f}  [paper: 0.667]  "
          f"PASS={abs(stab-0.667)<0.001}")

    # TDI vs K
    tau = sample_tau(n=80, seed=42)
    print(f"\n  TDI vs K (n=80, seed=42):")
    for K in [8, 10, 12, 14, 16, 20]:
        print(f"    K={K:3d} → TDI = {compute_tdi(tau, K):.4f}  "
              f"{'← ≈2.36?' if abs(compute_tdi(tau,K)-2.36)<0.06 else ''}")
    print(f"  Paper claims TDI=2.36 but NEVER states K → not reproducible!")

    # d_tau at kh=0
    rng = np.random.default_rng(0)
    tau2 = sample_tau(n=80, seed=0)
    adj0 = build_network(tau2, kh=0.0, dmax=12, rng=rng)
    adj6 = build_network(tau2, kh=6.0, dmax=12, rng=rng)
    log_tau2 = np.log(tau2 + 1)
    d0 = np.mean([np.mean(np.abs(log_tau2[i] - log_tau2[np.where(adj0[i]>0)[0]]))
                  for i in range(80) if adj0[i].sum()>0])
    d6 = np.mean([np.mean(np.abs(log_tau2[i] - log_tau2[np.where(adj6[i]>0)[0]]))
                  for i in range(80) if adj6[i].sum()>0])
    print(f"\n  Mean d_tau at kh=0 : {d0:.4f}")
    print(f"  Mean d_tau at kh=6 : {d6:.4f}")
    print(f"  σ_eff ratio (eq 5) : {(1+0.20*d0)/(1+0.20*d6):.4f}  "
          f"[should ≈1.26× if friction dominates]")


def inconsistency_summary():
    print("\n" + "="*65)
    print("SUMMARY OF ERRORS AND INCONSISTENCIES")
    print("="*65)

    issues = [
        ("MAJOR",    "E1",
         "Temporal Liquidity peak: Sec 4.5 and Fig 6 caption say 'TL peaks at "
         "κh≈0.75'. Fig 6b star annotation says 'Peak κh=0.50'. "
         "Caption and figure disagree. ONE of these is wrong; fix both to match."),
        ("MAJOR",    "E2",
         "TDI formula (Eq. 1) omits the histogram bin count K and the log base. "
         "TDI=2.36 requires K≈16 (nat log, n=80) but K is not stated. "
         "Without K the claim is NOT reproducible. State K explicitly."),
        ("MAJOR",    "E3",
         "σ_eff enters demand noise but the paper's model description is "
         "ambiguous: Eq. 5 amplifies 'effective noise' but it's unclear whether "
         "this affects ε_i directly or only through p_obs. The two "
         "interpretations give opposite stability behaviour at kh=0."),
        ("MODERATE", "E4",
         "Abstract ∆TDI=−0.10 is a silent round/average of Fig 6 values "
         "−0.114 (κh=3.0) and −0.102 (κh=6.0). Should quote the actual values "
         "or state explicitly this is an average."),
        ("MODERATE", "E5",
         "Fig 4 legend: 'TDI=1.85' (Low TDI); Fig 4 caption: 'low TDI=1.88'. "
         "3-unit discrepancy introduced when correcting the inverted-label bug. "
         "Pick one number and use it consistently."),
        ("MODERATE", "E6",
         "Theorem 1 proof: stability condition λ2>β̄/ᾱ is derived for k≥2 modes "
         "only. The k=1 uniform eigenmode is not addressed. A complete proof "
         "must show the uniform mode is also stable (or explain why it's excluded)."),
        ("MODERATE", "E7",
         "c(λ2)=log(1+λ2)/log2 exceeds 1 when λ2>1 (possible in dense graphs). "
         "This makes the global-price weight (1−c) negative, producing unstable "
         "price observations. The paper does not mention or bound this."),
        ("MINOR",    "E8",
         "t-statistic inconsistency: abstract and body text say t=12.6; "
         "Fig 2b annotation says t=13. Use one value throughout."),
        ("INFO",     "E9",
         "Temporal Liquidity TL=1/(σ·ACF·crash_excess) has no theoretical "
         "motivation. Described as exploratory only in Sec 3.3. The Goldilocks "
         "zone figure (Fig 5a) uses TL prominently; flag it as exploratory there "
         "too, or remove from the main results."),
        ("INFO",     "E10",
         "All historical compositions show λ2≈0 regardless of HFT share. "
         "The paper doesn't explain this. It likely reflects the network being "
         "fixed at kh=2.0 in those runs (Fig 5b), making the Fiedler analysis "
         "circular: you get λ2≈0 because you chose a moderately homophilic network."),
    ]
    for sev, code, desc in issues:
        print(f"\n  [{sev}] {code}")
        words = desc.split()
        line = "    "
        for w in words:
            if len(line)+len(w)+1 > 76:
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
    print("CME PAPER VALIDATION  v3")
    print("=" * 65)

    analytical_checks()

    print("\n=== Running κh sweep (250 runs) … ===")
    kh_results = kh_sweep(kh_values=np.linspace(0, 6, 25), n_seeds=10)
    sweep = report_kh_sweep(kh_results)

    report_adaptation()
    inconsistency_summary()

    print("\n" + "=" * 65)
    print("DONE")
    print("=" * 65)
