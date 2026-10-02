import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json

OUT = "/home/rafia/coplanarity_study/05_coplanarity_analysis/FINAL_FIGURES_2000_EVENT_2026-09-30"
OLD = "/home/rafia/coplanarity_study/05_coplanarity_analysis/FINAL_FIGURES_2026-09-28/SOURCE_DATA/FIGURE_C_EW_hits.csv"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "font.size": 13, "axes.titlesize": 13, "axes.labelsize": 13,
})

c_hits = pd.read_csv(f"{OUT}/SOURCE_DATA/FIGURE_4_colored_hits.csv")
e_hits = pd.read_csv(OLD)
e_hits.to_csv(f"{OUT}/SOURCE_DATA/FIGURE_4_EW_hits.csv", index=False)  # copy into this directory, source unchanged

fig, axes = plt.subplots(1, 2, figsize=(11, 5))
sc1 = axes[0].scatter(c_hits["y_vtxrel"], c_hits["x_vtxrel"], c=c_hits["layer_idx"], cmap="viridis", s=30)
axes[0].set_title("Colored (1800 GeV, $\\Lambda$=2 keV)")
axes[0].set_xlabel("y (cm, vertex-rel)"); axes[0].set_ylabel("x (cm, vertex-rel)")
sc2 = axes[1].scatter(e_hits["y_vtxrel"], e_hits["x_vtxrel"], c=e_hits["layer_idx"], cmap="viridis", s=30)
axes[1].set_title("EW (800 GeV, $\\Lambda$=4 keV)")
axes[1].set_xlabel("y (cm, vertex-rel)"); axes[1].set_ylabel("x (cm, vertex-rel)")
fig.suptitle("Representative reconstructed hit planes (fresh 2000-event, fiducial$\\cap$plane-found)", y=1.03)
fig.savefig(f"{OUT}/PNG/FIGURE_4_reproduction.png", dpi=200, bbox_inches="tight")
fig.savefig(f"{OUT}/PDF/FIGURE_4_reproduction.pdf", bbox_inches="tight")
fig.savefig(f"{OUT}/SVG/FIGURE_4_reproduction.svg", bbox_inches="tight")
plt.close(fig)

meta = {
    "colored": {
        "event_idx": 65, "seed": 2123515583,
        "selection_criterion": "fastest-converging (smallest wall_time_s) among the 12 corrected fiducial-AND-plane-found colored events",
        "delta_s_cm": 0.026692586327045693, "delta_w_cm": 0.6391264177537167,
        "hit_multiplicity_pass": True, "final_secIV_pass": False,
        "n_hits": int(len(c_hits)),
    },
    "EW": {
        "event_idx": 182, "seed": 2626882725,
        "selection_criterion": "fastest-converging (smallest wall_time_s) among the 75 corrected fiducial-AND-plane-found EW events",
        "delta_s_cm": 0.0077850299200439, "delta_w_cm": 0.0808772669419935,
        "hit_multiplicity_pass": True, "final_secIV_pass": True,
        "n_hits": int(len(e_hits)),
    },
    "disclosure": "Selection criterion (fastest wall_time_s, for computational tractability) is declared explicitly, not chosen because the event 'looks most like the paper'.",
}
with open(f"{OUT}/METADATA/FIGURE_4_event_metadata.json", "w") as f:
    json.dump(meta, f, indent=2)
print("Figure 4 generated. Colored event_idx=65, EW event_idx=182.")
