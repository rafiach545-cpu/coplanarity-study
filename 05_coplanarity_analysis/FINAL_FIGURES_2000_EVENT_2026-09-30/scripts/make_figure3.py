"""
Figure 3: the fresh 2000-event EW sample is at Lambda=4 keV (per
CONFIGURATION_FROZEN.json), NOT the 2 keV used by the paper's own Fig.3
EW diagnostic curve. Per instruction, retain the existing verified
diagnostic (Colored 2keV + EW 2keV, both already correctly labeled and
NOT derived from the Table-I 4keV sample) rather than silently
substituting the 4keV Table-I benchmark. Spike classification (4
near-degeneracy artifacts + 4 physical trajectory features) is
preserved unchanged.
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FFP = "/home/rafia/coplanarity_study/05_coplanarity_analysis/FINAL_FIGURES_FOR_PPT/SOURCE_DATA"
OUT = "/home/rafia/coplanarity_study/05_coplanarity_analysis/FINAL_FIGURES_2000_EVENT_2026-09-30"
COLORED = "#1f3d7a"
EW = "#0e8a7d"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "font.size": 13, "axes.titlesize": 13, "axes.labelsize": 13, "legend.fontsize": 10,
})

c3 = pd.read_csv(f"{FFP}/FIGURE_3_FINAL_source_colored.csv")
e3 = pd.read_csv(f"{FFP}/FIGURE_3_FINAL_source_EW.csv")
c3.to_csv(f"{OUT}/SOURCE_DATA/FIGURE_3_colored_2keV_source.csv", index=False)
e3.to_csv(f"{OUT}/SOURCE_DATA/FIGURE_3_EW_2keV_source.csv", index=False)

spikes = pd.read_csv(f"{FFP}/FIGURE_3_SPIKE_DIAGNOSTICS.csv")
spikes.to_csv(f"{OUT}/SOURCE_DATA/FIGURE_3_spike_classification_PRESERVED.csv", index=False)

fig, ax = plt.subplots(figsize=(7.5, 4.8))
c3v = c3[c3["valid"] == True]
e3v = e3[e3["valid"] == True]
ax.plot(c3v["r_cm"], c3v["dphi_rad"], color=COLORED, linewidth=1.2, label="Colored (1800 GeV, $\\Lambda$=2 keV)")
ax.plot(e3v["r_cm"], e3v["dphi_rad"], color=EW, linewidth=1.2,
        label="EW (800 GeV, $\\Lambda$=2 keV) [paper's own Fig.3 diagnostic benchmark —\nNOT derived from the fresh 2000-event Table-I 4 keV sample]")
ax.set_xlabel("$r$ (cm)"); ax.set_ylabel("$\\Delta\\phi$ (rad)")
ax.set_title("Plane rotation vs CM radial distance")
ax.legend(loc="upper right", frameon=False, fontsize=8)
fig.savefig(f"{OUT}/PNG/FIGURE_3_reproduction.png", dpi=200, bbox_inches="tight")
fig.savefig(f"{OUT}/PDF/FIGURE_3_reproduction.pdf", bbox_inches="tight")
fig.savefig(f"{OUT}/SVG/FIGURE_3_reproduction.svg", bbox_inches="tight")
plt.close(fig)
print("Figure 3 generated (reused verified 2keV/2keV data; fresh 2000-event EW sample is 4keV, not substituted).")
print("Spike classification preserved:", len(spikes), "rows -- not all spikes are artifacts.")
