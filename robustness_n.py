"""
robustness_n.py — Robustness checks at n=80, 160, 320.

For each n, scales type counts proportionally:
  HFT 15%, Hedge 25%, Mutual 40%, Pension 20%
Runs kh_sweep over kh_values=[0.0, 3.0, 6.0] with n_seeds=10.
Reports: mean λ₂ at κh=0, vol ratio (κh=0/κh=6), mean TDI, t-statistic.
"""

import sys
import numpy as np
from scipy import stats as sp_stats

# ── Import canonical building blocks ─────────────────────────────────────────
sys.path.insert(0, "/Users/sanjaysubramania/cme_validation")

from cme_canonical import (
    TYPE_MU, TYPE_SIGMA, TYPE_BOUNDS,
    T_STEPS, D_MAX, GAMMA, LAMBDA_PRICE, SIGMA_F, SIGMA_0, SIGMA_OBS,
    ALPHA_BAR, BETA_BAR, TDI_K, N_COMMUNITIES,
    build_network, row_normalise, fiedler_value, community_assignments,
    compute_tdi,
)


# ── Agent sampling with explicit type_counts ──────────────────────────────────

def sample_tau_n(n: int, seed: int = 42) -> np.ndarray:
    """Draw τ values for arbitrary n, preserving HFT/Hedge/Mutual/Pension ratios."""
    rng = np.random.default_rng(seed)
    # 15%, 25%, 40%, 20% rounded to integers that sum to n
    base = [int(round(n * p)) for p in [0.15, 0.25, 0.40, 0.20]]
    # Adjust rounding error so they sum to n
    diff = n - sum(base)
    base[2] += diff  # absorb residual into Mutual (largest bucket)
    type_counts = base

    tau = []
    for count, mu, sig, (lo, hi) in zip(
            type_counts, TYPE_MU, TYPE_SIGMA, TYPE_BOUNDS):
        collected = []
        while len(collected) < count:
            draws = np.exp(rng.normal(mu, sig, 5000))
            draws = draws[(draws >= lo) & (draws <= hi)]
            collected.extend(draws.tolist())
        tau.extend(max(1, int(round(x))) for x in collected[:count])
    return np.array(tau)


# ── Single run (adapted from cme_canonical.simulate_one_run, n-aware) ─────────

def simulate_one_run_n(kh: float, seed: int, n: int) -> dict:
    """Run one CME simulation for a given n and kh."""
    T = T_STEPS
    rng = np.random.default_rng(seed)

    tau  = sample_tau_n(n=n, seed=seed)
    adj  = build_network(tau, kh, rng)
    W    = row_normalise(adj)
    lam2 = fiedler_value(adj)
    comm = community_assignments(tau)

    c_lam = float(np.clip(np.log(1.0 + lam2) / np.log(2.0), 0.0, 1.0))

    log_tau_p1 = np.log(tau + 1)
    d_tau = np.zeros(n)
    for i in range(n):
        nbrs = np.where(adj[i] > 0)[0]
        if len(nbrs):
            d_tau[i] = np.mean(np.abs(log_tau_p1[i] - log_tau_p1[nbrs]))
    sigma_eff = SIGMA_0 * (1.0 + GAMMA * d_tau)

    max_tau = int(tau.max())
    buf_len = T + max_tau + 10
    p_hist  = np.full(buf_len, 100.0)

    F = 100.0
    p = 100.0
    returns   = []
    tmfi_vals = []

    for t in range(T):
        idx = max_tau + t
        F *= np.exp(rng.normal(0.0, SIGMA_F))

        p_bar = np.array([
            p_hist[max(0, idx - tau[i]) : idx].mean()
            if idx > 0 else 100.0
            for i in range(n)
        ])
        p_past  = np.array([p_hist[max(0, idx - tau[i])] for i in range(n)])
        momentum = np.where(
            p_past > 0,
            np.log(max(p, 1e-6) / np.maximum(p_past, 1e-6)),
            0.0,
        )

        eps    = rng.normal(0.0, sigma_eff)
        demand = (
            ALPHA_BAR * (F - p_bar) / max(p, 1e-3)
            + BETA_BAR * momentum
            + eps
        )

        p_new = p + LAMBDA_PRICE * demand.sum()
        if t > 0:
            returns.append((p_new - p) / p)
        p_hist[idx] = p_new
        p = p_new

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
    tdi      = compute_tdi(tau, K=TDI_K)

    return dict(
        volatility=vol,
        lambda2=lam2,
        tdi=tdi,
        kh=kh,
        seed=seed,
        n=n,
    )


# ── Sweep for one n ────────────────────────────────────────────────────────────

def sweep_n(n: int, kh_values: list, n_seeds: int = 10) -> list:
    results = []
    for kh in kh_values:
        for seed in range(n_seeds):
            r = simulate_one_run_n(kh=float(kh), seed=seed, n=n)
            results.append(r)
    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    KH_VALUES = [0.0, 3.0, 6.0]
    N_SEEDS   = 10
    N_LIST    = [80, 160, 320]

    print(f"\n{'='*72}")
    print(f"  Robustness checks: n ∈ {N_LIST},  κh ∈ {KH_VALUES},  seeds={N_SEEDS}")
    print(f"{'='*72}\n")

    # Header
    hdr = (
        f"{'n':>5}  {'λ₂ (κh=0)':>11}  {'vol(κh=0)':>11}  "
        f"{'vol(κh=6)':>11}  {'vol ratio':>10}  "
        f"{'t-stat':>8}  {'mean TDI':>9}"
    )
    print(hdr)
    print("-" * len(hdr))

    all_stats = {}

    for n in N_LIST:
        print(f"\n  Running n={n} ...", flush=True)
        results = sweep_n(n=n, kh_values=KH_VALUES, n_seeds=N_SEEDS)

        def mean_kh(key, kh):
            return float(np.mean([r[key] for r in results if r["kh"] == kh]))

        lam2_0   = mean_kh("lambda2", 0.0)
        vol_0    = mean_kh("volatility", 0.0)
        vol_6    = mean_kh("volatility", 6.0)
        vol_ratio = vol_0 / max(vol_6, 1e-30)
        tdi_mean = float(np.mean([r["tdi"] for r in results]))

        vols_lo = [r["volatility"] for r in results if r["kh"] == 0.0]
        vols_hi = [r["volatility"] for r in results if r["kh"] == 6.0]
        t_stat, p_val = sp_stats.ttest_ind(vols_lo, vols_hi, equal_var=False)

        all_stats[n] = dict(
            lam2_0=lam2_0, vol_0=vol_0, vol_6=vol_6,
            vol_ratio=vol_ratio, t_stat=t_stat, p_val=p_val,
            tdi_mean=tdi_mean,
        )

        print(
            f"  {n:>5}  {lam2_0:>11.4f}  {vol_0:>11.6f}  "
            f"{vol_6:>11.6f}  {vol_ratio:>10.3f}×  "
            f"{t_stat:>8.2f}  {tdi_mean:>9.4f}"
        )

    print(f"\n{'='*72}")
    print("SUMMARY TABLE")
    print(f"{'='*72}")
    print(hdr)
    print("-" * len(hdr))
    for n in N_LIST:
        s = all_stats[n]
        print(
            f"  {n:>5}  {s['lam2_0']:>11.4f}  {s['vol_0']:>11.6f}  "
            f"{s['vol_6']:>11.6f}  {s['vol_ratio']:>10.3f}×  "
            f"{s['t_stat']:>8.2f}  {s['tdi_mean']:>9.4f}"
        )
    print(f"{'='*72}\n")

    # Machine-readable for patch generation
    print("\n--- RAW STATS FOR PAPER PATCH ---")
    for n, s in all_stats.items():
        print(
            f"n={n}: lam2_0={s['lam2_0']:.4f}  vol_ratio={s['vol_ratio']:.3f}x  "
            f"t={s['t_stat']:.2f}  p={s['p_val']:.2e}  tdi={s['tdi_mean']:.4f}"
        )

    return all_stats


if __name__ == "__main__":
    main()
