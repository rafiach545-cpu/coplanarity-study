"""
Figure 3 cache-only reproduction -- reads ONLY the exported source-values
CSV (FIGURE_3_FINAL_Plane_Rotation_VALUES.csv). Does not import
quirk_trajectory, does not propagate any trajectory, does not change or
smooth any value. Reproduces the current final figure from stored numbers
alone, for provenance verification.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "/home/rafia/coplanarity_study"
SRC = f"{BASE}/05_coplanarity_analysis/FINAL_FIGURES_FOR_PPT/SOURCE_DATA/FIGURE_3_FINAL_Plane_Rotation_VALUES.csv"
OUT_PNG = f"{BASE}/05_coplanarity_analysis/FINAL_FIGURES_FOR_PPT/PNG/FIGURE_3_FINAL_Plane_Rotation_FROM_CSV.png"
OUT_PDF = f"{BASE}/05_coplanarity_analysis/FINAL_FIGURES_FOR_PPT/PDF/FIGURE_3_FINAL_Plane_Rotation_FROM_CSV.pdf"

PLOT_MAP = {
    "colored": ("mQ = 1.8 TeV, Lambda = 2 keV (colored benchmark)", "tab:blue"),
    "EW": ("mQ = 800 GeV, Lambda = 2 keV (EW-mass benchmark)", "tab:orange"),
}


def main():
    df = pd.read_csv(SRC)

    fig, ax = plt.subplots(figsize=(7, 5))
    for benchmark, (leglabel, color) in PLOT_MAP.items():
        sub = df[(df["benchmark"] == benchmark) & (df["plotted_in_final_figure"])]
        sub = sub.sort_values("point_index")
        ax.plot(sub["r_cm"], sub["delta_phi_times_1e3"], label=leglabel, color=color, lw=1.2)

    ax.set_xlabel("r (cm)")
    ax.set_ylabel(r"$\Delta\phi$  ($\times 10^{-3}$)")
    ax.set_title("Figure 3 diagnostic reproduction (v2) -- FINAL APPROXIMATE / diagnostic\n"
                  "plane-normal rotation of quirk velocity vectors vs CM radial distance\n"
                  "(reproduced cache-only, from exported CSV values, not re-simulated)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    ax.text(0.02, -0.18,
             "Needle-like spikes arise from residual angle-unwrapping near plane-normal\n"
             "degeneracies; the overall trend and scale are interpreted qualitatively.",
             transform=ax.transAxes, fontsize=7, style="italic", va="top")
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=150)
    fig.savefig(OUT_PDF)
    plt.close(fig)
    print(f"Wrote {OUT_PNG}")
    print(f"Wrote {OUT_PDF}")
    print(f"Points plotted: colored={len(df[(df.benchmark=='colored') & (df.plotted_in_final_figure)])}, "
          f"EW={len(df[(df.benchmark=='EW') & (df.plotted_in_final_figure)])}")


if __name__ == "__main__":
    main()
