"""
Figure 4 plot generation (v1) -- projects event 386's vertex-relative hits
onto the Sec IIIC reconstructed plane (n3=flight direction, n2=width axis),
in the paper's own Fig.4 style (2D scatter, hits colored by quirk origin).
Reads only the already-computed replay outputs; no new simulation.
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "/home/rafia/coplanarity_study/05_coplanarity_analysis/figure4_vertex_fixed_v1"

with open(f"{OUT}/Figure_4_metadata_v1.json") as f:
    meta = json.load(f)

hits = pd.read_csv(f"{OUT}/Figure_4_source_hits_v1.csv")
plane_hits = pd.read_csv(f"{OUT}/Figure_4_source_plane_v1.csv")

n1 = np.array(meta["sec3c_normal_n1"])  # smallest-eigenvalue axis (thickness, Delta_s)
n2 = np.array(meta["sec3c_normal_n2"])  # second axis (width, Delta_w)
n3 = np.array(meta["sec3c_normal_n3"])  # flight direction

plane_hit_ids = set(plane_hits["hit_id"])

pts = hits[["x_vtxrel", "y_vtxrel", "z_vtxrel"]].values
u = pts @ n3   # flight-direction coordinate (paper's Fig.4 x-axis analogue)
v = pts @ n2   # width coordinate (paper's Fig.4 y-axis analogue)
w = pts @ n1   # thickness coordinate (out-of-plane, Delta_s direction)

fig, ax = plt.subplots(figsize=(7, 6))
colors = {1: "tab:green", 2: "tab:purple"}
markers = {1: "o", 2: "^"}
for qi in (1, 2):
    m = hits["quirk_index"] == qi
    in_plane = hits.loc[m, "hit_id"].isin(plane_hit_ids)
    ax.scatter(u[m][in_plane], v[m][in_plane], c=colors[qi], marker=markers[qi],
               s=70, edgecolor="k", linewidth=0.5, label=f"Quirk {qi} hit (selected plane)", zorder=3)
    ax.scatter(u[m][~in_plane], v[m][~in_plane], c="lightgray", marker=markers[qi],
               s=50, edgecolor="k", linewidth=0.3, label=f"Quirk {qi} hit (unused)" if (~in_plane).any() else None, zorder=2)

for layer_idx in sorted(hits["layer_idx"].unique()):
    lm = hits["layer_idx"] == layer_idx
    ax.annotate(f"L{layer_idx}", (u[lm].mean(), v[lm].mean()), textcoords="offset points",
                xytext=(6, 6), fontsize=7, color="gray")

ds = meta["sec3c_ds_cm"]
dw = meta["sec3c_dw_cm"]
ax.set_xlabel(r"$n_3$ (flight direction) [cm]")
ax.set_ylabel(r"$n_2$ (width axis) [cm]")
ax.set_title(f"Figure 4 reproduced (vertex-fixed pipeline) -- APPROXIMATE\n"
             f"Event 386, colored benchmark (mQ=1.8TeV, $\\Lambda$=2keV)")
ax.text(0.02, 0.98, f"$\\Delta s$ = {ds:.5f} cm\n$\\Delta w$ = {dw:.5f} cm\n"
                     f"(paper reference: $\\Delta s$=0.0083cm, $\\Delta w$=0.074cm)",
        transform=ax.transAxes, va="top", ha="left", fontsize=9,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.85))
ax.legend(fontsize=8, loc="lower right")
ax.grid(alpha=0.3)
ax.set_aspect("equal", adjustable="datalim")
fig.tight_layout()
fig.savefig(f"{OUT}/Figure_4_reproduced_vertex_fixed_v1.png", dpi=150)
fig.savefig(f"{OUT}/Figure_4_reproduced_vertex_fixed_v1.pdf")
plt.close(fig)
print("Saved Figure_4_reproduced_vertex_fixed_v1.png/.pdf")
print(f"Delta_s={ds:.6f} cm  Delta_w={dw:.6f} cm")
print(f"u(n3) range: [{u.min():.3f}, {u.max():.3f}]  v(n2) range: [{v.min():.3f}, {v.max():.3f}]  w(n1,out-of-plane) std: {w.std():.6f}")
