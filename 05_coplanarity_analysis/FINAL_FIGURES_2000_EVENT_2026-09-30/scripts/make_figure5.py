"""
Figure 5: Delta_s / Delta_w distributions, Colored (12 fid&plane) and EW
(75 fid&plane) signal, raw-count AND unit-normalized versions, with
Poisson (sqrt(N)) uncertainty bars per bin, bin edges/counts/uncertainty
saved to CSV.
"""
import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "/home/rafia/coplanarity_study/05_coplanarity_analysis/FINAL_FIGURES_2000_EVENT_2026-09-30"
COLORED = "#1f3d7a"
EW = "#0e8a7d"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "font.size": 13, "axes.titlesize": 13, "axes.labelsize": 13, "legend.fontsize": 10,
})

colored = pd.read_csv("/home/rafia/coplanarity_study/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/reconstruction/colored_1800GeV_L2keV/per_event_results.csv")
ew = pd.read_csv("/home/rafia/coplanarity_study/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1/reconstruction/EW_800GeV_L4keV/per_event_results.csv")

c_sel = colored[(colored["truth_fiducial"] == True) & (colored["sec3c_plane_found"] == True)]
e_sel = ew[(ew["truth_fiducial"] == True) & (ew["sec3c_plane_found"] == True)]
assert len(c_sel) == 12, f"expected 12 colored, got {len(c_sel)}"
assert len(e_sel) == 75, f"expected 75 EW, got {len(e_sel)}"

src_rows = []
for label, df in [("colored", c_sel), ("EW", e_sel)]:
    for _, r in df.iterrows():
        src_rows.append({"sample": label, "event_idx": r["event_idx"], "delta_s_cm": r["sec3c_ds_cm"],
                          "delta_w_cm": r["sec3c_dw_cm"]})
src = pd.DataFrame(src_rows)
src.to_csv(f"{OUT}/SOURCE_DATA/FIGURE_5_signal_source.csv", index=False)


def hist_with_err(data, bins):
    counts, edges = np.histogram(data, bins=bins)
    err = np.sqrt(counts)
    return counts, err, edges


bin_rows = []
for var, cut, xlabel in [("delta_s_cm", 0.01, "$\\Delta s$ (cm)"), ("delta_w_cm", 1.0, "$\\Delta w$ (cm)")]:
    fig, (axr, axn) = plt.subplots(1, 2, figsize=(11, 4.5))
    for label, color in [("colored", COLORED), ("EW", EW)]:
        d = src[src["sample"] == label][var]
        bins = np.linspace(d.min() * 0.9 if d.min() > 0 else 0, d.max() * 1.1, 12)
        counts, err, edges = hist_with_err(d, bins)
        centers = 0.5 * (edges[:-1] + edges[1:])
        widths = np.diff(edges)
        axr.bar(centers, counts, width=widths * 0.9, color=color, alpha=0.6, label=f"{label} (N={len(d)})")
        axr.errorbar(centers, counts, yerr=err, fmt="none", color="black", capsize=2, linewidth=1)
        norm_counts = counts / len(d) if len(d) else counts
        norm_err = err / len(d) if len(d) else err
        axn.bar(centers, norm_counts, width=widths * 0.9, color=color, alpha=0.6, label=f"{label} (N={len(d)})")
        axn.errorbar(centers, norm_counts, yerr=norm_err, fmt="none", color="black", capsize=2, linewidth=1)
        for c, e, lo, hi in zip(counts, err, edges[:-1], edges[1:]):
            bin_rows.append({"variable": var, "sample": label, "bin_lo": lo, "bin_hi": hi,
                              "raw_count": c, "raw_count_uncertainty": e,
                              "normalized_count": c / len(d) if len(d) else 0,
                              "normalized_uncertainty": e / len(d) if len(d) else 0})
    axr.axvline(cut, color="black", linestyle="--", linewidth=1, label=f"cut={cut}")
    axn.axvline(cut, color="black", linestyle="--", linewidth=1, label=f"cut={cut}")
    axr.set_xlabel(xlabel); axr.set_ylabel("Events (raw count)"); axr.set_title("Raw count")
    axn.set_xlabel(xlabel); axn.set_ylabel("Fraction of sample"); axn.set_title("Unit-normalized")
    axr.legend(loc="upper right", frameon=False, fontsize=9)
    axn.legend(loc="upper right", frameon=False, fontsize=9)
    fig.suptitle(f"{xlabel} distribution — Colored N=12, EW N=75 (fiducial$\\cap$plane-found only)", y=1.03)
    name = f"FIGURE_5_{var.replace('_cm','')}_raw_and_normalized"
    fig.savefig(f"{OUT}/PNG/{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(f"{OUT}/PDF/{name}.pdf", bbox_inches="tight")
    fig.savefig(f"{OUT}/SVG/{name}.svg", bbox_inches="tight")
    plt.close(fig)

pd.DataFrame(bin_rows).to_csv(f"{OUT}/SOURCE_DATA/FIGURE_5_bin_edges_counts_uncertainties.csv", index=False)

# combined comparison panel
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
for ax, var, cut, xlabel in [(axes[0], "delta_s_cm", 0.01, "$\\Delta s$ (cm)"), (axes[1], "delta_w_cm", 1.0, "$\\Delta w$ (cm)")]:
    for label, color in [("colored", COLORED), ("EW", EW)]:
        d = src[src["sample"] == label][var]
        ax.hist(d, bins=12, histtype="step", linewidth=2, color=color, density=True, label=f"{label} (N={len(d)})")
    ax.axvline(cut, color="black", linestyle="--", linewidth=1)
    ax.set_xlabel(xlabel); ax.set_ylabel("Density")
    ax.legend(loc="upper right", frameon=False, fontsize=9)
fig.suptitle("Combined comparison (density-normalized)", y=1.03)
fig.savefig(f"{OUT}/PNG/FIGURE_5_combined_comparison.png", dpi=200, bbox_inches="tight")
fig.savefig(f"{OUT}/PDF/FIGURE_5_combined_comparison.pdf", bbox_inches="tight")
fig.savefig(f"{OUT}/SVG/FIGURE_5_combined_comparison.svg", bbox_inches="tight")
plt.close(fig)

print("Figure 5 generated: raw+normalized for delta_s and delta_w, plus combined comparison.")
print(f"Colored N={len(c_sel)}, EW N={len(e_sel)} (verified counts)")
