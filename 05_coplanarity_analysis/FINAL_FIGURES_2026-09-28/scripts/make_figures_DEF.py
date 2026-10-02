"""
Phase 5 figures D (Delta-s/Delta-w), E (efficiency comparison), F (cutflow).
Uses ONLY verified, already-computed data from this session's audits.
No new simulation. Colors: Colored=dark blue (#1f3d7a), EW=teal (#0e8a7d),
paper=dark gray (#4d4d4d). White background, linear axes for efficiency %.
"""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "/home/rafia/coplanarity_study/05_coplanarity_analysis/FINAL_FIGURES_2026-09-28"
COLORED = "#1f3d7a"
EW = "#0e8a7d"
PAPER = "#4d4d4d"

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


def wilson95(k, n):
    z = 1.96
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = (z / d) * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    return max(0, c - h), min(1, c + h)


# ============================================================
# Figure D: Delta-s and Delta-w distributions (corrected 12/75)
# ============================================================
src = pd.read_csv(f"{OUT}/../EW_TRIGGER_FIDUCIAL_AUDIT_2026-09-28/PHASE4_MASTER_TABLE/figure5_corrected_source_data.csv")
src.to_csv(f"{OUT}/SOURCE_DATA/FIGURE_D_delta_s_delta_w_corrected_source.csv", index=False)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
for label, color in [("colored", COLORED), ("EW", EW)]:
    d = src[src["sample"] == label]
    axes[0].hist(d["delta_s_cm"], bins=15, histtype="step", linewidth=2, color=color,
                 label=f"{label.capitalize()} (N={len(d)})")
    axes[1].hist(d["delta_w_cm"], bins=15, histtype="step", linewidth=2, color=color,
                 label=f"{label.capitalize()} (N={len(d)})")
axes[0].axvline(0.01, color="black", linestyle="--", linewidth=1, label="$\\Delta s$<0.01cm cut")
axes[1].axvline(1.0, color="black", linestyle="--", linewidth=1, label="$\\Delta w$<1cm cut")
axes[0].set_xlabel("$\\Delta s$ (cm)"); axes[0].set_ylabel("Events")
axes[1].set_xlabel("$\\Delta w$ (cm)"); axes[1].set_ylabel("Events")
axes[0].set_title("Plane thickness ($\\Delta s$)")
axes[1].set_title("Plane width ($\\Delta w$)")
axes[0].legend(loc="upper right", frameon=False)
axes[1].legend(loc="upper right", frameon=False)
fig.suptitle("Fiducial$\\cap$plane-found events: $\\Delta s$/$\\Delta w$ (corrected intersections)", y=1.03)
save_all(fig, "FIGURE_D_delta_s_delta_w_corrected")

# ============================================================
# Figure E: efficiency comparison, paper vs project, Wilson 95%
# ============================================================
master = pd.read_csv("/home/rafia/coplanarity_study/05_coplanarity_analysis/EW_TRIGGER_FIDUCIAL_AUDIT_2026-09-28/PHASE4_MASTER_TABLE/MASTER_TABLE_CONSOLIDATED.csv")

def eff_panel(ax, prefix, title, color):
    quantities = [
        (f"{prefix}2000: trigger" + ("_only" if "Colored" in prefix else ""), "eps_trig"),
        (f"{prefix}2000: fiducial", "eps_fid"),
        (f"{prefix}2000: eps_plane_conditional (CORRECTED, not stale 20/25)" if "Colored" in prefix
         else f"{prefix}2000: eps_plane_conditional (CORRECTED, not stale 84/94)", "eps_plane"),
        (f"{prefix}2000: eps_secIV_conditional", "eps_secIV"),
    ]
    labels = ["$\\epsilon_{trig}$", "$\\epsilon_{fid}$", "$\\epsilon_{reco}$\n(plane)", "$\\epsilon_{reco}$\n(Sec IV)"]
    x = np.arange(len(quantities))
    proj_vals, proj_lo, proj_hi, paper_vals = [], [], [], []
    for qname, _ in quantities:
        row = master[master["quantity"] == qname].iloc[0]
        proj_vals.append(row["efficiency"] * 100)
        lo, hi = wilson95(int(row["numerator"]), int(row["denominator"]))
        proj_lo.append(row["efficiency"] * 100 - lo * 100)
        proj_hi.append(hi * 100 - row["efficiency"] * 100)
        paper_vals.append(row["paper_value"] * 100)
    ax.bar(x, proj_vals, yerr=[proj_lo, proj_hi], capsize=4, color=color, alpha=0.85,
           width=0.5, label="Project (this audit)")
    ax.scatter(x, paper_vals, color=PAPER, marker="D", s=70, zorder=5, label="Paper Table I")
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Efficiency (%)")
    ax.set_title(title)
    ax.legend(loc="upper left", frameon=False, fontsize=10)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
eff_panel(axes[0], "Colored", "Colored (1800 GeV, $\\Lambda$=2 keV)", COLORED)
eff_panel(axes[1], "EW", "EW (800 GeV, $\\Lambda$=4 keV)", EW)
fig.suptitle("Efficiency comparison: project (2000-event) vs paper Table I", y=1.03)
save_all(fig, "FIGURE_E_efficiency_comparison")

eff_source = master[master["quantity"].str.contains("2000")].copy()
eff_source.to_csv(f"{OUT}/SOURCE_DATA/FIGURE_E_efficiency_comparison_source.csv", index=False)

# ============================================================
# Figure F: cutflow figures
# ============================================================
def cutflow_panel(ax, stages, counts, color, title):
    x = np.arange(len(stages))
    ax.bar(x, counts, color=color, alpha=0.85, width=0.6)
    for i, c in enumerate(counts):
        ax.text(i, c + max(counts) * 0.02, str(c), ha="center", fontsize=10)
    ax.set_xticks(x); ax.set_xticklabels(stages, rotation=30, ha="right", fontsize=10)
    ax.set_ylabel("Events")
    ax.set_title(title)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
cutflow_panel(axes[0],
              ["Generated", "Matched", "Trigger-only", "Trig&Charged", "Fiducial", "Fid&Plane", "Fid&Plane&Mult", "Final SecIV"],
              [2000, 873, 207, 68, 25, 12, 7, 3], COLORED, "Colored 2000 cutflow")
cutflow_panel(axes[1],
              ["Generated", "Matched", "Trigger", "Fiducial", "Fid&Plane", "Hit-mult", "Final SecIV"],
              [2000, 1045, 186, 94, 75, 48, 21], EW, "EW 2000 cutflow")
fig.suptitle("Fresh 2000-event cutflows (corrected intersections)", y=1.03)
save_all(fig, "FIGURE_F_cutflow_colored_EW")

cutflow_source = pd.DataFrame([
    {"sample": "Colored2000", "stage": s, "count": c} for s, c in zip(
        ["Generated", "Matched", "Trigger-only", "Trig&Charged", "Fiducial", "Fid&Plane", "Fid&Plane&Mult", "Final SecIV"],
        [2000, 873, 207, 68, 25, 12, 7, 3])
] + [
    {"sample": "EW2000", "stage": s, "count": c} for s, c in zip(
        ["Generated", "Matched", "Trigger", "Fiducial", "Fid&Plane", "Hit-mult", "Final SecIV"],
        [2000, 1045, 186, 94, 75, 48, 21])
])
cutflow_source.to_csv(f"{OUT}/SOURCE_DATA/FIGURE_F_cutflow_source.csv", index=False)

print("Figures D, E, F generated successfully.")
