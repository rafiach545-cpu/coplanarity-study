"""
Figure 2 audit -- independent, cache-only plotting script.

Imports NO trajectory/detector/simulation module from this project. Reads
ONLY the already-exported EVENT65_ROOT_RECOMPUTED_VALUES.csv (produced once,
read-mostly, by the audit's Phase 8 regeneration script) and redraws the
same graph shape as the project's existing Figure 2
(FINAL_FIGURES_2000_EVENT_2026-09-30/scripts/make_figure2.py), using the
same colors, for independent visual cross-check.

This script is part of a read-mostly forensic audit
(FIGURE2_ROOT_AUDIT_2026-09-30) and does NOT modify, overwrite, or replace
any existing Figure 2 file elsewhere in the repository.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = "/home/rafia/coplanarity_study/05_coplanarity_analysis/FIGURE2_ROOT_AUDIT_2026-09-30"

# Same colors as the project's original make_figure2.py:
#   angular-momentum curve: "#1f3d7a" (dark blue)
#   separation curve:       "darkorange"
COLOR_L = "#1f3d7a"
COLOR_D = "darkorange"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "font.size": 13, "axes.titlesize": 13, "axes.labelsize": 13,
})

df = pd.read_csv(f"{HERE}/EVENT65_ROOT_RECOMPUTED_VALUES.csv")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
ax1.plot(df["r_cm"], df["L_hbar"] / 1e12, color=COLOR_L, linewidth=1.2)
ax1.set_ylabel(r"$L$ ($\hbar \times 10^{12}$)")
ax1.set_title("Angular momentum & quirk separation vs CM radial distance\n"
              "(audit-independent cache-only replot, event_idx=65, "
              "Colored 1800 GeV / 2 keV benchmark)")

ax2.plot(df["r_cm"], df["d_cm"], color=COLOR_D, linewidth=1.2)
ax2.set_yscale("log")
ax2.set_xlabel("$r$ (cm, CM to interaction point)")
ax2.set_ylabel("$d$ (cm)")

fig.text(0.5, -0.03,
          "AUDIT REPLOT -- from EVENT65_ROOT_RECOMPUTED_VALUES.csv only, no simulation code imported.\n"
          "Representative project event (Colored, event_idx=65, seed=2123515583) -- "
          "NOT a claimed exact reproduction of the paper's own (unpublished) representative event.",
          ha="center", fontsize=8, style="italic")

fig.savefig(f"{HERE}/FIGURE2_EVENT65_ROOT_VERIFIED.png", dpi=200, bbox_inches="tight")
fig.savefig(f"{HERE}/FIGURE2_EVENT65_ROOT_VERIFIED.pdf", bbox_inches="tight")
fig.savefig(f"{HERE}/FIGURE2_EVENT65_ROOT_VERIFIED.svg", bbox_inches="tight")
print("Wrote FIGURE2_EVENT65_ROOT_VERIFIED.{png,pdf,svg}")
