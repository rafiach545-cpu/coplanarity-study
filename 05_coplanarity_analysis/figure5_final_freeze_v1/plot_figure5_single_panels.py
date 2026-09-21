"""
Figure 5A/5B single-panel split (v1) -- reads the ALREADY-COMPUTED frozen
bin-level source CSV (Figure_5_four_component_source_v2.csv) and replots
each panel standalone. No new simulation, no new binning -- purely a
re-rendering of already-verified, already-frozen numbers, for PPT slides
that need one panel per slide instead of the combined 2-panel figure.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = "/home/rafia/coplanarity_study/05_coplanarity_analysis/figure5_final_freeze_v1/Figure_5_four_component_source_v2.csv"
OUT = "/home/rafia/coplanarity_study/05_coplanarity_analysis/figure5_final_freeze_v1"

c = pd.read_csv(SRC)

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

def plot_panel(panel, xlabel, cut_line, outfile_stub):
    fig, ax = plt.subplots(figsize=(8, 6))
    for curve in ORDER:
        sub = c[(c["curve"] == curve) & (c["panel"] == panel)].sort_values("bin_lo")
        edges = list(sub["bin_lo"]) + [sub["bin_hi"].iloc[-1]]
        ax.stairs(sub["density"], edges, label=CURVE_LABELS[curve], color=COLORS[curve], linewidth=1.5)
    if cut_line is not None:
        ax.axvline(cut_line, color="black", linestyle="--", linewidth=1.2, label=f"cut at {cut_line} cm")
    ax.set_xscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("unit-normalized density")
    ax.set_title(f"Figure 5 ({panel.replace('delta_', 'Delta_')}) -- 4-component (authoritative populations)\n{LABEL}",
                 fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"{OUT}/{outfile_stub}.png", dpi=150)
    fig.savefig(f"{OUT}/{outfile_stub}.pdf")
    plt.close(fig)
    print(f"Saved {outfile_stub}.png/.pdf")

plot_panel("delta_s", "Delta_s (cm)", 0.01, "Figure_5A_DeltaS_four_component_v1")
plot_panel("delta_w", "Delta_w (cm)", None, "Figure_5B_DeltaW_four_component_v1")
