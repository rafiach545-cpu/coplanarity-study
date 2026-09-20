"""
Figure 1 schematic reproduction (v1) -- project-native, not a copy of the
paper bitmap. Conceptual illustration only; no simulated data plotted.

Paper Fig.1 caption (verified via direct visual inspection of the rendered
PDF page 2): "Schematic event display of a pair of quirks (green) with an
ISR jet (blue). The cylinders represent the three innermost layers of the
ATLAS/CMS tracker. The hits (black dots) all lie on a single plane (shaded
red)."
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

OUT = "/home/rafia/coplanarity_study/05_coplanarity_analysis/figure1_schematic_v1"
import os
os.makedirs(OUT, exist_ok=True)

fig = plt.figure(figsize=(9, 6.5))
ax = fig.add_subplot(111, projection="3d")

# Cylinder axis runs along X (matching the paper's own horizontal-tracker
# view). Quirks travel outward along +X; ISR jet recoils along -X.
x_cyl = np.linspace(-2, 10, 2)
theta = np.linspace(0, 2 * np.pi, 60)
Xc, Theta = np.meshgrid(x_cyl, theta)
for r in [2.0, 3.2, 4.5]:
    Yc = r * np.cos(Theta)
    Zc = r * np.sin(Theta)
    ax.plot_surface(Xc, Yc, Zc, color="gray", alpha=0.10, linewidth=0)
    circ_theta = np.linspace(0, 2 * np.pi, 100)
    ax.plot(np.full_like(circ_theta, -2), r * np.cos(circ_theta), r * np.sin(circ_theta), color="gray", lw=0.8, alpha=0.5)
    ax.plot(np.full_like(circ_theta, 10), r * np.cos(circ_theta), r * np.sin(circ_theta), color="gray", lw=0.8, alpha=0.5)

# --- coplanar shaded plane: contains the X axis, tilted in Y-Z ---
pp = np.array([1.0, 0.0, 0.0])  # along cylinder axis
qq = np.array([0.0, 1.0, 0.4]); qq = qq / np.linalg.norm(qq)  # tilted transverse direction
uu, vv = np.meshgrid(np.linspace(-1, 9, 2), np.linspace(-4.5, 4.5, 2))
plane_pts = uu[..., None] * pp + vv[..., None] * qq
Xp, Yp, Zp = plane_pts[..., 0], plane_pts[..., 1], plane_pts[..., 2]
ax.plot_surface(Xp, Yp, Zp, color="firebrick", alpha=0.22, linewidth=0)

# --- two oscillatory quirk trajectories (green), confined to the shaded plane, traveling along +X ---
tvals = np.linspace(0, 9, 400)
for sign in [1, -1]:
    u_coord = tvals
    v_coord = sign * 1.4 * np.exp(-tvals / 9) * np.sin(tvals * 2.2)
    pts = u_coord[:, None] * pp + v_coord[:, None] * qq
    ax.plot(pts[:, 0], pts[:, 1], pts[:, 2], color="green", lw=2.2)

# --- hits (black dots) exactly ON the shaded plane, near the 3 layer radii ---
hit_u_layers = [2.0, 3.2, 4.5]
rng = np.random.default_rng(42)
hit_u, hit_v = [], []
for ubase in hit_u_layers:
    for sign in [1, -1]:
        hit_u.append(ubase)
        hit_v.append(sign * 1.4 * np.exp(-ubase / 9) * np.sin(ubase * 2.2))
hit_pts = np.array(hit_u)[:, None] * pp + np.array(hit_v)[:, None] * qq
ax.scatter(hit_pts[:, 0], hit_pts[:, 1], hit_pts[:, 2], color="black", s=45, depthshade=False, zorder=5)

# --- ISR jet (blue lines fanning from origin, recoiling along -X) ---
rng2 = np.random.default_rng(7)
for _ in range(6):
    d = np.array([-1.0, rng2.normal(0, 0.35), rng2.normal(0, 0.35)])
    d = d / np.linalg.norm(d) * 4.5
    ax.plot([0, d[0]], [0, d[1]], [0, d[2]], color="steelblue", lw=1.8)

# --- interaction point ---
ax.scatter([0], [0], [0], color="black", s=30, marker="*", zorder=6)

ax.set_xlim(-2, 10); ax.set_ylim(-5, 5); ax.set_zlim(-5, 5)
ax.set_box_aspect((12, 10, 10))
ax.set_axis_off()
ax.view_init(elev=18, azim=-50)

from matplotlib.lines import Line2D
legend_elems = [
    Line2D([0], [0], color="green", lw=2, label="Quirk pair trajectories"),
    Line2D([0], [0], color="steelblue", lw=2, label="ISR jet"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="black", markersize=7, label="Detector hits"),
    Line2D([0], [0], color="firebrick", lw=6, alpha=0.3, label="Common coplanar plane"),
]
ax.legend(handles=legend_elems, loc="upper left", fontsize=8, framealpha=0.9)
ax.set_title("Project schematic inspired by Paper Figure 1\nconceptual, not simulated data", fontsize=10)

plt.tight_layout()
plt.savefig(f"{OUT}/Figure_1_reproduced_v1.png", dpi=150, bbox_inches="tight")
plt.savefig(f"{OUT}/Figure_1_reproduced_v1.pdf", bbox_inches="tight")
plt.close()

with open(f"{OUT}/figure1_metadata_v1.json", "w") as f:
    import json
    json.dump({
        "label": "Project schematic inspired by Paper Figure 1 -- conceptual, not simulated data.",
        "source_caption": "FIG. 1: Schematic event display of a pair of quirks (green) with an ISR jet (blue). The cylinders represent the three innermost layers of the ATLAS/CMS tracker. The hits (black dots) all lie on a single plane (shaded red).",
        "verified_against": "direct visual inspection of rendered PDF page 2 (400dpi)",
        "elements": ["3 cylindrical tracker layers", "2 oscillatory quirk trajectories (green)",
                     "6 hits (black dots) exactly on the shaded plane", "ISR jet (blue, 6 lines)",
                     "shaded coplanar plane (red)", "interaction point (star marker)"],
        "no_invented_numerical_result": True,
        "visual_verification": "all 6 plotted hits lie exactly on the shaded plane by construction (computed as pp/qq in-plane coordinates, zero out-of-plane component)",
    }, f, indent=2)
print("saved Figure 1 schematic")
