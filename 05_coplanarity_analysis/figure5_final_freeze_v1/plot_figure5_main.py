"""
Figure 5 main plots (combined 2-panel four-component shape figure, and the
corrected absolute three-component figure) -- reconstructed from the
ALREADY-FROZEN bin-level source CSVs (Figure_5_four_component_source_v2.csv,
Figure_5_absolute_three_component_source_v2.csv). This codifies what was
originally run via inline Bash/Python heredocs in an earlier session turn
into a standalone, reproducible script, per the requirement that every
final figure be regeneratable from a committed script + source data. No
new simulation, no new binning, no new numbers -- purely a re-rendering of
already-verified, already-frozen values.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "/home/rafia/coplanarity_study/05_coplanarity_analysis/figure5_final_freeze_v1"

CURVE_LABELS = {
    "colored": "Colored Quirk (N=5)",
    "EW": "EW Quirk (N=32)",
    "pileup_mu50": "Pileup mu=50 (N=172)",
    "converted_gamma_plus_pileup_mu50": "Converted gamma + Pileup mu=50 (N=3276)",
}
COLORS = {"colored": "tab:blue", "EW": "tab:orange", "pileup_mu50": "tab:green",
          "converted_gamma_plus_pileup_mu50": "tab:red"}
ORDER = ["colored", "EW", "pileup_mu50", "converted_gamma_plus_pileup_mu50"]

LABEL = "Approximate unit-area Figure 5 shape reproduction; absolute paper normalization unavailable."


def plot_four_component_combined():
    c = pd.read_csv(f"{OUT}/Figure_5_four_component_source_v2.csv")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, panel, xlabel, cut_line, title in [
        (axes[0], "delta_s", "Delta_s (cm)", 0.01, "Left panel: Delta_s -- 4-component (authoritative populations)"),
        (axes[1], "delta_w", "Delta_w (cm)", None, "Right panel: Delta_w -- 4-component (authoritative populations)"),
    ]:
        for curve in ORDER:
            sub = c[(c["curve"] == curve) & (c["panel"] == panel)].sort_values("bin_lo")
            edges = list(sub["bin_lo"]) + [sub["bin_hi"].iloc[-1]]
            ax.stairs(sub["density"], edges, label=CURVE_LABELS[curve], color=COLORS[curve], linewidth=1.5)
        if cut_line is not None:
            ax.axvline(cut_line, color="black", linestyle="--", linewidth=1.2, label="Delta_s<0.01cm cut")
        ax.set_xscale("log")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("unit-normalized density")
        ax.set_title(title)
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
    fig.suptitle(f"{LABEL}\nPileup=full mu=50 population (N=172); Converted-gamma=REAL mu=50 overlay (N=3276, not conversion-only N=2982)",
                 fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(f"{OUT}/Figure_5_four_component_v2_AUTHORITATIVE.png", dpi=150)
    fig.savefig(f"{OUT}/Figure_5_four_component_v2_AUTHORITATIVE.pdf")
    plt.close(fig)
    print("Saved Figure_5_four_component_v2_AUTHORITATIVE.png/.pdf")


def plot_absolute_three_component():
    c = pd.read_csv(f"{OUT}/Figure_5_absolute_three_component_source_v2.csv")
    WEIGHTS = {"colored": "N=5, w=7.5036e-04 fb/evt, N_matched_full=419",
               "EW": "N=32, w=4.5738e-04 fb/evt, N_matched_full=511",
               "converted_gamma_plus_pileup_mu50": "N=3276"}
    LABELS = {"colored": f"Colored Quirk ({WEIGHTS['colored']})",
              "EW": f"EW Quirk ({WEIGHTS['EW']})",
              "converted_gamma_plus_pileup_mu50": f"Converted gamma + Pileup mu=50 ({WEIGHTS['converted_gamma_plus_pileup_mu50']})"}
    fig, ax = plt.subplots(figsize=(9, 7))
    for curve in ["colored", "EW", "converted_gamma_plus_pileup_mu50"]:
        sub = c[c["curve"] == curve].sort_values("bin_lo")
        sub = sub[sub["dsigma_dlogDs_fb_per_bin"] > 0]  # log-y axis: drop zero bins
        edges_lo = sub["bin_lo"].values
        edges = list(edges_lo) + [sub["bin_hi"].iloc[-1]]
        ax.stairs(sub["dsigma_dlogDs_fb_per_bin"], edges,
                  label=LABELS[curve], color=COLORS[curve], linewidth=1.5)
    ax.axvline(0.01, color="black", linestyle="--", linewidth=1.2, label="Delta_s<0.01cm cut")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Delta_s (cm)")
    ax.set_ylabel(r"d$\sigma$/dlog(Delta_s) (fb/bin)")
    ax.set_title("Fig.5 left panel -- CORRECTED ABSOLUTE (3 components)\n"
                 "Pileup EXCLUDED: no cross-section concept available")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(f"{OUT}/Figure_5_absolute_three_component_v2_CORRECTED.png", dpi=150)
    fig.savefig(f"{OUT}/Figure_5_absolute_three_component_v2_CORRECTED.pdf")
    plt.close(fig)
    print("Saved Figure_5_absolute_three_component_v2_CORRECTED.png/.pdf")


if __name__ == "__main__":
    plot_four_component_combined()
    plot_absolute_three_component()
