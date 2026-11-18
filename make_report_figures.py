"""Figures for the long-form report: clustering score series and concentration check."""
import json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = "/Users/sanjaysubramania/cme_validation/"
k = pd.read_csv(R + "kappa_empirical_results.csv")
h = json.load(open(R + "kappa_hac_results.json"))
fig, ax = plt.subplots(figsize=(8.2, 3.6))
x = np.arange(len(k))
ax.plot(x, k.kappa_hat, color="#4b3f9e", lw=1.8, marker="o", ms=3.5)
ax.axhline(0, color="k", lw=0.8)
ax.axhline(k.kappa_hat.mean(), color="#2a8f5a", ls="--", lw=1.2, label=f"average = {k.kappa_hat.mean():.3f}")
lo, hi = h["block_boot_ci"]
ax.axhspan(lo, hi, color="#2a8f5a", alpha=0.15, label=f"95% bootstrap range for the average ({lo:.3f} to {hi:.3f})")
ticks = [i for i, q in enumerate(k.quarter) if q.endswith("Q1") and int(q[:4]) % 2 == 0]
ax.set_xticks(ticks); ax.set_xticklabels([k.quarter[i][:4] for i in ticks])
ax.set_ylabel("horizon clustering score"); ax.set_xlabel("quarter")
ax.legend(frameon=False, fontsize=8, loc="upper left"); ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(R + "figures/kappa_series.png", dpi=200); plt.close()

d = pd.DataFrame(json.load(open(R + "sim_concentration_results.json")))
fig, axs = plt.subplots(1, 2, figsize=(9, 3.5))
for kh, c in ((0.5, "#4b3f9e"), (2.0, "#c0792b")):
    g = d[d.kh == kh].groupby("conc").vol.agg(["mean", "std", "count"])
    axs[0].errorbar(g.index, g["mean"] * 1e3, yerr=g["std"] / np.sqrt(g["count"]) * 1e3 * 1.96,
                    color=c, marker="o", capsize=3, label=f"clustering setting {kh}")
axs[0].set_xlabel("horizon compression (higher = narrower horizons)")
axs[0].set_ylabel("simulated volatility (x 0.001)"); axs[0].legend(frameon=False, fontsize=8)
axs[0].set_title("(a) Volatility falls as horizons compress", fontsize=10)
g = d[d.kh == 0.5]
axs[1].scatter(g.tdi, g.vol * 1e3, s=10, color="#4b3f9e", alpha=0.6)
b = np.polyfit(g.tdi, g.vol * 1e3, 1); xs = np.linspace(g.tdi.min(), g.tdi.max(), 20)
axs[1].plot(xs, np.polyval(b, xs), "k", lw=1)
r = np.corrcoef(g.tdi, g.vol)[0, 1]
axs[1].set_xlabel("horizon diversity"); axs[1].set_ylabel("simulated volatility (x 0.001)")
axs[1].set_title(f"(b) Each run, clustering setting 0.5 (r = {r:+.2f})", fontsize=10)
for a in axs: a.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig(R + "figures/conc_check.png", dpi=200); plt.close()
print("ok")
