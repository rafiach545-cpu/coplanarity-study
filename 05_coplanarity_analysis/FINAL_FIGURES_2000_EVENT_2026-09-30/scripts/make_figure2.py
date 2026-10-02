import pandas as pd, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "/home/rafia/coplanarity_study/05_coplanarity_analysis/FINAL_FIGURES_2000_EVENT_2026-09-30"
COLORED = "#1f3d7a"

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    "font.size": 13, "axes.titlesize": 13, "axes.labelsize": 13,
})

df = pd.read_csv(f"{OUT}/SOURCE_DATA/FIGURE_2_2000event_colored_event65_source.csv")
meta = json.load(open(f"{OUT}/SOURCE_DATA/FIGURE_2_2000event_metadata.json"))

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
ax1.plot(df["r_cm"], df["L_hbar"] / 1e12, color=COLORED, linewidth=1.2)
ax1.set_ylabel("$L$ ($\\hbar \\times 10^{12}$)")
ax1.set_title("Angular momentum & quirk separation vs CM radial distance")
ax2.plot(df["r_cm"], df["d_cm"], color="darkorange", linewidth=1.2)
ax2.set_yscale("log")
ax2.set_xlabel("$r$ (cm, CM to interaction point)")
ax2.set_ylabel("$d$ (cm)")
fig.text(0.5, -0.02, "Representative project event (Colored, event_idx=65) — not an exact reproduction of the paper's own event",
          ha="center", fontsize=9, style="italic")
fig.savefig(f"{OUT}/PNG/FIGURE_2_2000event_representative.png", dpi=200, bbox_inches="tight")
fig.savefig(f"{OUT}/PDF/FIGURE_2_2000event_representative.pdf", bbox_inches="tight")
fig.savefig(f"{OUT}/SVG/FIGURE_2_2000event_representative.svg", bbox_inches="tight")
plt.close(fig)
print("Figure 2 (2000-event) generated. Event:", meta["event_idx"], "seed:", meta["seed"])
