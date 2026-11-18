"""
holding_period_sim.py — Holding Period Model (HPM)
Subramanian & Seetharaman (2026) — exploratory extension

MOTIVATION
----------
In CME, τ is a lookback horizon: all agents use the same strategy
(fundamentalist + momentum) just computed over different windows.
Holding period is used only in the empirical calibration (τ_i = 63/θ_i).

In the Holding Period Model (HPM), τ_i is EXPLICITLY the holding duration,
and it determines WHICH STRATEGY the agent uses:

  α_i = ᾱ · (1 + φ · log(τ_i / τ_med))   ← long-τ → more fundamental
  β_i = β̄ · (1 − φ · log(τ_i / τ_med))   ← short-τ → more momentum

Empirical basis:
  - Momentum dominates at 1-12 month horizons (Jegadeesh & Titman 1993)
  - Value/mean-reversion at 3-5 year horizons (De Bondt & Thaler 1985)

This φ=0 limit exactly recovers CME. With φ > 0, homophily clusters
momentum traders together (and value traders together). The open question
is whether this AMPLIFIES or ATTENUATES the CME stability results.

PARAMETERS
----------
All shared parameters match CME canonical values.
New parameter: PHI (heterogeneity coupling, default 0.4)

OUTPUT
------
  holding_period_results.csv  — raw sweep data
  hpm_comparison.png          — 4-panel figure vs CME baseline
"""

import numpy as np
from scipy import stats as sp_stats
import warnings
import csv
import os
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

# ── Shared constants (match CME canonical) ────────────────────────────────────
N_AGENTS      = 80
T_STEPS       = 500
D_MAX         = 12
GAMMA         = 0.20
LAMBDA_PRICE  = 0.008
SIGMA_F       = 0.010
SIGMA_0       = 1.0
SIGMA_OBS     = 0.008
ALPHA_BAR     = 0.30
BETA_BAR      = 0.20
TDI_K         = 16
N_COMMUNITIES = 4

TYPE_COUNTS = [12, 20, 32, 16]
TYPE_MU     = [0.5, 2.8, 4.2, 6.0]
TYPE_SIGMA  = [0.6, 0.7, 0.6, 0.8]
TYPE_BOUNDS = [(1, 20), (15, 120), (60, 400), (400, 2000)]

# ── HPM-specific ──────────────────────────────────────────────────────────────
PHI = 0.4   # strategy-heterogeneity coupling
             # φ=0 → identical to CME; φ=0.4 → ±40% swing across log-τ range


# ── Agent sampling (identical to CME) ─────────────────────────────────────────
def sample_tau(n: int = N_AGENTS, seed: int = 42) -> np.ndarray:
    rng = np.random.default_rng(seed)
    tau: List[int] = []
    for count, mu, sig, (lo, hi) in zip(
            TYPE_COUNTS, TYPE_MU, TYPE_SIGMA, TYPE_BOUNDS):
        collected: List[float] = []
        while len(collected) < count:
            draws = np.exp(rng.normal(mu, sig, 5000))
            draws = draws[(draws >= lo) & (draws <= hi)]
            collected.extend(draws.tolist())
        tau.extend(max(1, int(round(x))) for x in collected[:count])
    return np.array(tau)


def compute_tdi(tau: np.ndarray, K: int = TDI_K) -> float:
    log_tau = np.log(np.maximum(tau, 1))
    counts, _ = np.histogram(log_tau, bins=K)
    freqs = counts / counts.sum()
    freqs = freqs[freqs > 0]
    return float(-np.sum(freqs * np.log(freqs)))


def build_network(tau: np.ndarray, kh: float,
                  rng: np.random.Generator) -> np.ndarray:
    n = len(tau)
    log_tau = np.log(tau + 1)
    diff = np.abs(log_tau[:, None] - log_tau[None, :])
    prob = np.exp(-kh * diff)
    np.fill_diagonal(prob, 0.0)
    adj = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        p = prob[i].copy()
        p /= p.sum()
        chosen = rng.choice(n, size=min(D_MAX, n - 1), replace=False, p=p)
        adj[i, chosen] = 1.0
    return adj


def row_normalise(adj: np.ndarray) -> np.ndarray:
    row_s = adj.sum(axis=1, keepdims=True)
    return np.where(row_s > 0, adj / row_s, 0.0)


def fiedler_value(adj: np.ndarray) -> float:
    sym = (adj + adj.T) / 2.0
    deg = np.maximum(sym.sum(axis=1), 1e-12)
    D_inv_sqrt = np.diag(1.0 / np.sqrt(deg))
    L = np.eye(len(adj)) - D_inv_sqrt @ sym @ D_inv_sqrt
    evals = np.sort(np.linalg.eigvalsh(L))
    return float(max(evals[1], 0.0))


def community_assignments(tau: np.ndarray) -> np.ndarray:
    log_tau = np.log(tau)
    q25, q50, q75 = np.percentile(log_tau, [25, 50, 75])
    comm = np.zeros(len(tau), dtype=int)
    comm[log_tau > q25] = 1
    comm[log_tau > q50] = 2
    comm[log_tau > q75] = 3
    return comm


# ── HPM-specific: holding-period-stratified α_i, β_i ─────────────────────────
def compute_alpha_beta(tau: np.ndarray, phi: float = PHI
                       ) -> Tuple[np.ndarray, np.ndarray]:
    """
    α_i = ᾱ · (1 + φ · z_i)    long-τ agents: more fundamentalist
    β_i = β̄ · (1 − φ · z_i)    short-τ agents: more momentum-driven

    z_i = log(τ_i / τ_med) / max(|log(τ / τ_med)|)  ∈ [-1, 1]

    Clamped so α_i ≥ 0.05 and β_i ≥ 0.05 to avoid degenerate agents.
    """
    tau_med = np.median(tau)
    log_rel = np.log(np.maximum(tau, 1) / max(tau_med, 1))
    max_abs  = max(np.abs(log_rel).max(), 1e-6)
    z = log_rel / max_abs  # ∈ [-1, 1]

    alpha = ALPHA_BAR * (1.0 + phi * z)
    beta  = BETA_BAR  * (1.0 - phi * z)

    alpha = np.clip(alpha, 0.05, None)
    beta  = np.clip(beta,  0.05, None)
    return alpha, beta


# ── Core HPM simulation ───────────────────────────────────────────────────────
def simulate_hpm(kh: float, seed: int,
                 phi: float = PHI,
                 n: int = N_AGENTS,
                 T: int = T_STEPS) -> Dict:
    """
    HPM variant of CME.

    KEY DIFFERENCE from CME:
      Each agent's fundamentalist weight α_i and momentum weight β_i are
      determined by their holding period τ_i (via compute_alpha_beta).
      Short-τ agents are primarily momentum traders;
      long-τ agents are primarily fundamentalist/value investors.

    Everything else (network, noise, TMFI path, τ-adaptation) is identical.
    """
    rng = np.random.default_rng(seed)

    tau  = sample_tau(n=n, seed=seed)
    adj  = build_network(tau, kh, rng)
    W    = row_normalise(adj)
    lam2 = fiedler_value(adj)
    comm = community_assignments(tau)

    c_lam = float(np.clip(np.log(1.0 + lam2) / np.log(2.0), 0.0, 1.0))

    # Per-agent cross-τ distances → effective noise
    log_tau_p1 = np.log(tau + 1)
    d_tau = np.zeros(n)
    for i in range(n):
        nbrs = np.where(adj[i] > 0)[0]
        if len(nbrs):
            d_tau[i] = np.mean(np.abs(log_tau_p1[i] - log_tau_p1[nbrs]))
    sigma_eff = SIGMA_0 * (1.0 + GAMMA * d_tau)

    # HPM: per-agent α and β derived from holding period
    alpha_i, beta_i = compute_alpha_beta(tau, phi=phi)

    max_tau = int(tau.max())
    buf_len = T + max_tau + 10
    p_hist  = np.full(buf_len, 100.0)

    F = 100.0
    p = 100.0
    returns:    List[float] = []
    tmfi_vals:  List[float] = []

    for t in range(T):
        idx = max_tau + t

        F *= np.exp(rng.normal(0.0, SIGMA_F))

        # τ_i-period moving average (fundamentalist reference — each agent's own window)
        p_bar = np.array([
            p_hist[max(0, idx - tau[i]):idx].mean()
            if idx > 0 else 100.0
            for i in range(n)
        ])

        # Momentum signal over each agent's own τ_i window
        p_past = np.array([p_hist[max(0, idx - tau[i])] for i in range(n)])
        momentum = np.where(
            p_past > 0,
            np.log(max(p, 1e-6) / np.maximum(p_past, 1e-6)),
            0.0,
        )

        # HPM demand: α_i and β_i are holding-period-specific
        eps    = rng.normal(0.0, sigma_eff)
        demand = (
            alpha_i * (F - p_bar) / max(p, 1e-3)
            + beta_i * momentum
            + eps
        )

        p_new = p + LAMBDA_PRICE * demand.sum()

        if t > 0:
            returns.append((p_new - p) / p)

        p_hist[idx] = p_new
        p = p_new

        # TMFI: same observation-noise path as CME
        if t >= T // 2:
            xi      = rng.normal(0.0, sigma_eff / SIGMA_0)
            p_obs_j = p * (1.0 + SIGMA_OBS * xi)
            p_nbr   = W @ p_obs_j
            p_obs_i = c_lam * p_nbr + (1.0 - c_lam) * p

            comm_means = np.array([
                p_obs_i[comm == c].mean() if (comm == c).any() else p
                for c in range(N_COMMUNITIES)
            ])
            m = comm_means.mean()
            if m > 1e-6:
                tmfi_vals.append(comm_means.std(ddof=0) / m)

    ret_arr  = np.array(returns)
    vol      = ret_arr.std()
    tmfi     = float(np.mean(tmfi_vals)) if tmfi_vals else 0.0
    tdi      = compute_tdi(tau)

    if len(ret_arr) > 2:
        acf_lag1 = float(np.corrcoef(ret_arr[:-1], ret_arr[1:])[0, 1])
    else:
        acf_lag1 = 0.0

    tl_denom = vol * abs(acf_lag1)
    tl = 1.0 / tl_denom if tl_denom > 1e-15 else float("inf")

    return dict(
        volatility=vol,
        tmfi=tmfi,
        tdi=tdi,
        acf_lag1=acf_lag1,
        temporal_liquidity=tl,
        d_tau_mean=float(d_tau.mean()),
        alpha_mean=float(alpha_i.mean()),
        beta_mean=float(beta_i.mean()),
    )


# ── CME baseline (φ=0) for direct comparison ─────────────────────────────────
def simulate_cme_baseline(kh: float, seed: int,
                          n: int = N_AGENTS,
                          T: int = T_STEPS) -> Dict:
    """CME with uniform α=ᾱ, β=β̄ (φ=0 limit). Isolated for clean comparison."""
    return simulate_hpm(kh=kh, seed=seed, phi=0.0, n=n, T=T)


# ── Sweep ─────────────────────────────────────────────────────────────────────
def run_sweep(kh_values: np.ndarray, n_seeds: int, phi: float) -> List[Dict]:
    results = []
    for kh in kh_values:
        seed_results = []
        for seed in range(n_seeds):
            r = simulate_hpm(kh=float(kh), seed=seed, phi=phi)
            r["kh"]  = float(kh)
            r["seed"] = seed
            r["phi"]  = phi
            results.append(r)
            seed_results.append(r)
        vols = [s["volatility"] for s in seed_results]
        tls  = [s["temporal_liquidity"] for s in seed_results
                if np.isfinite(s["temporal_liquidity"])]
        print(
            f"  φ={phi:.1f}  κ_h={kh:.2f}  "
            f"vol={np.mean(vols):.6f}  "
            f"TL={np.mean(tls) if tls else float('inf'):.2e}",
            flush=True,
        )
    return results


def aggregate(results: List[Dict], key: str) -> Tuple[np.ndarray, np.ndarray]:
    kh_vals = sorted(set(r["kh"] for r in results))
    means, stds = [], []
    for kh in kh_vals:
        vals = [r[key] for r in results
                if r["kh"] == kh and np.isfinite(r[key])]
        means.append(np.mean(vals) if vals else np.nan)
        stds.append(np.std(vals)   if vals else np.nan)
    return np.array(means), np.array(stds)


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    OUT_DIR = os.path.dirname(os.path.abspath(__file__))
    KH_VALUES = np.linspace(0, 6, 25)
    N_SEEDS   = 10

    print("=" * 60)
    print("HOLDING PERIOD MODEL (HPM)  —  κ_h sweep")
    print("=" * 60)

    # Run CME baseline (φ=0)
    print("\n── CME baseline (φ=0, uniform α=0.30, β=0.20) ──")
    cme_results = run_sweep(KH_VALUES, N_SEEDS, phi=0.0)

    # Run HPM (φ=0.4)
    print("\n── HPM (φ=0.4, heterogeneous α/β by holding period) ──")
    hpm_results = run_sweep(KH_VALUES, N_SEEDS, phi=PHI)

    # Save CSV
    csv_path = os.path.join(OUT_DIR, "holding_period_results.csv")
    all_results = cme_results + hpm_results
    if all_results:
        fieldnames = list(all_results[0].keys())
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
    print(f"\nResults saved → {csv_path}")

    # Aggregate for plotting
    kh_arr = np.linspace(0, 6, 25)

    cme_vol,  cme_vol_s  = aggregate(cme_results, "volatility")
    hpm_vol,  hpm_vol_s  = aggregate(hpm_results, "volatility")

    cme_tmfi, cme_tmfi_s = aggregate(cme_results, "tmfi")
    hpm_tmfi, hpm_tmfi_s = aggregate(hpm_results, "tmfi")

    cme_tl,   _          = aggregate(cme_results, "temporal_liquidity")
    hpm_tl,   _          = aggregate(hpm_results, "temporal_liquidity")

    cme_acf,  _          = aggregate(cme_results, "acf_lag1")
    hpm_acf,  _          = aggregate(hpm_results, "acf_lag1")

    # Normalise to κ_h=0 baseline
    def norm(arr):
        b = arr[0] if np.isfinite(arr[0]) and arr[0] != 0 else 1.0
        return arr / b

    # ── 4-panel comparison figure ─────────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    fig.suptitle(
        "HPM vs CME: Holding-Period-Stratified Agent Strategies\n"
        r"($\phi=0.4$: short-$\tau$ momentum, long-$\tau$ value;  $\phi=0$: CME uniform)",
        fontsize=11,
    )

    kh_fine = kh_arr

    # Panel 1: Volatility
    ax = axes[0, 0]
    ax.plot(kh_fine, norm(cme_vol), "b-o",  ms=4, lw=1.8, label="CME (φ=0)")
    ax.plot(kh_fine, norm(hpm_vol), "r-s",  ms=4, lw=1.8, label="HPM (φ=0.4)")
    ax.fill_between(kh_fine,
                    norm(cme_vol) - cme_vol_s / (cme_vol[0] or 1),
                    norm(cme_vol) + cme_vol_s / (cme_vol[0] or 1),
                    alpha=0.12, color="blue")
    ax.fill_between(kh_fine,
                    norm(hpm_vol) - hpm_vol_s / (hpm_vol[0] or 1),
                    norm(hpm_vol) + hpm_vol_s / (hpm_vol[0] or 1),
                    alpha=0.12, color="red")
    ax.axhline(1.0, color="gray", lw=0.8, ls="--")
    ax.set_xlabel(r"$\kappa_h$ (temporal homophily)")
    ax.set_ylabel("Normalised Volatility")
    ax.set_title("Volatility Channel")
    ax.legend(fontsize=9)

    # Panel 2: TMFI
    ax = axes[0, 1]
    ax.plot(kh_fine, norm(cme_tmfi), "b-o", ms=4, lw=1.8, label="CME (φ=0)")
    ax.plot(kh_fine, norm(hpm_tmfi), "r-s", ms=4, lw=1.8, label="HPM (φ=0.4)")
    ax.axhline(1.0, color="gray", lw=0.8, ls="--")
    ax.set_xlabel(r"$\kappa_h$ (temporal homophily)")
    ax.set_ylabel("Normalised TMFI")
    ax.set_title("Temporal Fragmentation (TMFI)")
    ax.legend(fontsize=9)

    # Panel 3: Temporal Liquidity
    ax = axes[1, 0]
    cme_tl_fin = np.where(np.isfinite(cme_tl), cme_tl, np.nan)
    hpm_tl_fin = np.where(np.isfinite(hpm_tl), hpm_tl, np.nan)
    ax.plot(kh_fine, cme_tl_fin, "b-o", ms=4, lw=1.8, label="CME (φ=0)")
    ax.plot(kh_fine, hpm_tl_fin, "r-s", ms=4, lw=1.8, label="HPM (φ=0.4)")
    ax.set_xlabel(r"$\kappa_h$ (temporal homophily)")
    ax.set_ylabel("Temporal Liquidity (TL)")
    ax.set_title("Liquidity Hump")
    ax.legend(fontsize=9)

    # Panel 4: ACF lag-1 (autocorrelation, proxy for momentum persistence)
    ax = axes[1, 1]
    ax.plot(kh_fine, cme_acf, "b-o", ms=4, lw=1.8, label="CME (φ=0)")
    ax.plot(kh_fine, hpm_acf, "r-s", ms=4, lw=1.8, label="HPM (φ=0.4)")
    ax.axhline(0.0, color="gray", lw=0.8, ls="--")
    ax.set_xlabel(r"$\kappa_h$ (temporal homophily)")
    ax.set_ylabel("ACF Lag-1")
    ax.set_title("Return Autocorrelation\n(momentum persistence proxy)")
    ax.legend(fontsize=9)

    plt.tight_layout()
    fig_path = os.path.join(OUT_DIR, "hpm_comparison.png")
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Figure saved → {fig_path}")

    # ── Summary statistics ────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SUMMARY: KEY RATIOS (κ_h=6 vs κ_h=0)")
    print("=" * 60)

    kh_hi = -1  # last index = κ_h=6

    def ratio(arr):
        return f"{arr[kh_hi] / arr[0]:.3f}×" if arr[0] != 0 else "N/A"

    print(f"\n  VOLATILITY ratio (κ_h=6 / κ_h=0):")
    print(f"    CME (φ=0):    {ratio(cme_vol)}")
    print(f"    HPM (φ=0.4):  {ratio(hpm_vol)}")

    print(f"\n  TMFI ratio (κ_h=6 / κ_h=0):")
    print(f"    CME (φ=0):    {ratio(cme_tmfi)}")
    print(f"    HPM (φ=0.4):  {ratio(hpm_tmfi)}")

    print(f"\n  ACF lag-1 at κ_h=6:")
    print(f"    CME (φ=0):    {cme_acf[kh_hi]:.4f}")
    print(f"    HPM (φ=0.4):  {hpm_acf[kh_hi]:.4f}")

    print(f"\n  TL peak location:")
    fin_cme = np.where(np.isfinite(cme_tl_fin), cme_tl_fin, -np.inf)
    fin_hpm = np.where(np.isfinite(hpm_tl_fin), hpm_tl_fin, -np.inf)
    peak_cme = kh_arr[np.argmax(fin_cme)]
    peak_hpm = kh_arr[np.argmax(fin_hpm)]
    print(f"    CME (φ=0):    κ_h = {peak_cme:.2f}")
    print(f"    HPM (φ=0.4):  κ_h = {peak_hpm:.2f}")

    print(f"\n  Per-agent α/β means at φ=0.4 (κ_h=0 run, seed=0):")
    tau_sample = sample_tau(seed=0)
    a, b = compute_alpha_beta(tau_sample, phi=PHI)
    tau_med = np.median(tau_sample)
    short_mask = tau_sample < tau_med
    long_mask  = tau_sample >= tau_med
    print(f"    Short-τ agents (τ < {tau_med:.0f}d): "
          f"α={a[short_mask].mean():.3f}  β={b[short_mask].mean():.3f}")
    print(f"    Long-τ  agents (τ ≥ {tau_med:.0f}d): "
          f"α={a[long_mask].mean():.3f}  β={b[long_mask].mean():.3f}")

    print(f"\nDone. See hpm_comparison.png and holding_period_results.csv")
