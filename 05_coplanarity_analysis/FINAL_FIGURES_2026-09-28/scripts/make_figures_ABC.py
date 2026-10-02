"""
Phase 5 figures A (Fig.2 repro), B (Fig.3 repro), C (Fig.4 repro).
Reuses already-verified, previously-committed source CSVs (no new
trajectory generation for A/B; C-EW uses one already-completed replay
of an existing corrected-selection event, event_idx=182, seed stored).
"""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FFP = "/home/rafia/coplanarity_study/05_coplanarity_analysis/FINAL_FIGURES_FOR_PPT/SOURCE_DATA"
OUT = "/home/rafia/coplanarity_study/05_coplanarity_analysis/FINAL_FIGURES_2026-09-28"
COLORED = "#1f3d7a"
EW = "#0e8a7d"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "font.size": 13, "axes.titlesize": 14, "axes.labelsize": 13,
    "legend.fontsize": 11, "xtick.labelsize": 11, "ytick.labelsize": 11,
})


def save_all(fig, name):
    fig.savefig(f"{OUT}/PNG/{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(f"{OUT}/PDF/{name}.pdf", bbox_inches="tight")
    fig.savefig(f"{OUT}/SVG/{name}.svg", bbox_inches="tight")
    plt.close(fig)


# ============================================================
# Figure A: Fig.2 reproduction (Colored, 1800GeV/2keV -- paper's own
# single benchmark for this figure; reused verified source, unchanged)
# ============================================================
fig2 = pd.read_csv(f"{FFP}/FIGURE_2_FINAL_source.csv")
fig2.to_csv(f"{OUT}/SOURCE_DATA/FIGURE_A_fig2_reproduction_source.csv", index=False)

fig, ax1 = plt.subplots(figsize=(7, 4.5))
ax2 = ax1.twinx()
ax1.plot(fig2["r_cm"], fig2["L_hbar"], color=COLORED, linewidth=1.5, label="Angular momentum $L$")
ax2.plot(fig2["r_cm"], fig2["d_cm"], color="darkorange", linewidth=1.5, linestyle="--", label="Separation $d$")
ax1.set_xlabel("$r$ (cm)")
ax1.set_ylabel("$L$ ($\\hbar$)", color=COLORED)
ax2.set_ylabel("$d$ (cm)", color="darkorange")
ax2.set_yscale("log")
ax1.set_title("Angular momentum & separation vs CM radial distance")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=False, fontsize=10)
save_all(fig, "FIGURE_A_fig2_reproduction")

# ============================================================
# Figure B: Fig.3 reproduction (Colored 2keV + EW 2keV, matching
# paper's own two benchmarks for this figure exactly -- reused verified
# source, unchanged; spike classification preserved, not all spikes
# claimed to be artifacts)
# ============================================================
c3 = pd.read_csv(f"{FFP}/FIGURE_3_FINAL_source_colored.csv")
e3 = pd.read_csv(f"{FFP}/FIGURE_3_FINAL_source_EW.csv")
c3.to_csv(f"{OUT}/SOURCE_DATA/FIGURE_B_fig3_colored_source.csv", index=False)
e3.to_csv(f"{OUT}/SOURCE_DATA/FIGURE_B_fig3_EW_source.csv", index=False)

fig, ax = plt.subplots(figsize=(7.5, 4.8))
c3v = c3[c3["valid"] == True]
e3v = e3[e3["valid"] == True]
ax.plot(c3v["r_cm"], c3v["dphi_rad"], color=COLORED, linewidth=1.2, label="Colored (1800 GeV, $\\Lambda$=2 keV)")
ax.plot(e3v["r_cm"], e3v["dphi_rad"], color=EW, linewidth=1.2, label="EW (800 GeV, $\\Lambda$=2 keV) [Fig.3 diagnostic benchmark]")
ax.set_xlabel("$r$ (cm)")
ax.set_ylabel("$\\Delta\\phi$ (rad)")
ax.set_title("Plane rotation vs CM radial distance")
ax.legend(loc="upper right", frameon=False, fontsize=9)
save_all(fig, "FIGURE_B_fig3_reproduction")

# ============================================================
# Figure C: Fig.4 reproduction, Colored (existing verified event) +
# EW (event_idx=182, from the corrected fiducial-AND-plane-found
# selection of 75 EW-2000 events -- replayed once this session from
# stored seed/momenta, not new generation)
# ============================================================
c4h = pd.read_csv(f"{FFP}/FIGURE_4_FINAL_hits.csv")
c4h.to_csv(f"{OUT}/SOURCE_DATA/FIGURE_C_colored_hits.csv", index=False)

import os
ew_hits_path = f"{OUT}/SOURCE_DATA/FIGURE_C_EW_hits.csv"

fig, axes = plt.subplots(1, 2, figsize=(11, 5))
axes[0].scatter(c4h["y_vtxrel"], c4h["x_vtxrel"], c=c4h["layer_idx"], cmap="viridis", s=25)
axes[0].set_title("Colored (1800 GeV, $\\Lambda$=2 keV) — representative hit plane")
axes[0].set_xlabel("y (cm, vertex-relative)"); axes[0].set_ylabel("x (cm, vertex-relative)")

if os.path.exists(ew_hits_path):
    e4h = pd.read_csv(ew_hits_path)
    sc = axes[1].scatter(e4h["y_vtxrel"], e4h["x_vtxrel"], c=e4h["layer_idx"], cmap="viridis", s=25)
    axes[1].set_title("EW (800 GeV, $\\Lambda$=4 keV) — representative hit plane")
    axes[1].set_xlabel("y (cm, vertex-relative)"); axes[1].set_ylabel("x (cm, vertex-relative)")
else:
    axes[1].text(0.5, 0.5, "EW replay pending\n(see scripts/replay182.log)", ha="center", va="center")
    axes[1].set_title("EW (800 GeV, $\\Lambda$=4 keV) — pending")

fig.suptitle("Representative reconstructed hit planes (fiducial$\\cap$plane-found selection)", y=1.02)
save_all(fig, "FIGURE_C_fig4_reproduction")
print("Figures A, B, C generated" + (" (EW panel pending replay)" if not os.path.exists(ew_hits_path) else " (complete)"))
