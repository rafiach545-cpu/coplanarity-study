#!/usr/bin/env python3
"""07 geometry, 3D cut-away views (matplotlib, 2026-11-17): the simulated detector in 3D, Ideal (Knapen et al.) and the full ATLAS Run 2 ID model.
Element positions from tables/X06_geometry_elements.csv (from sim/detsim07.build, the simulation geometry); beam pipe from geometry/atlas_run2_id_geometry.csv.
No number is typed here. Surfaces are drawn semi-transparent with one quadrant cut away so that the inner layers are visible; the beam (z) axis is horizontal.
The drawing code between the BEGIN/END markers is copied unchanged into the Colab notebook by build_colab_notebook.py.
Run with /home/rafia/venvs/f6fast/bin/python. Output: GEO4_3d_ideal/, GEO5_3d_atlas/ (pdf, png at 300 dpi, caption.md, provenance.json)."""
import os, csv, json, hashlib
import matplotlib; matplotlib.use("Agg")
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); X6 = f"{R}/tables/X06_geometry_elements.csv"; GC = f"{R}/geometry/atlas_run2_id_geometry.csv"
ELEMENTS = [dict(r) for r in csv.DictReader(open(X6))]
for e in ELEMENTS:
    for k in ("r_cm", "half_length_cm", "z_cm", "rmin_cm", "rmax_cm"): e[k] = float(e[k]) if e[k] not in ("", None) else None
GROWS = list(csv.DictReader(open(GC))); BEAM_PIPE_INNER_R_CM = float([r for r in GROWS if r["name"] == "BP"][0]["r_mm"]) / 10
SCT_DISK_Z_MM = sorted({float(r["z_mm"]) for r in GROWS if r["region"] == "endcap_ring"})   # disk |z| (R3 Table 4.6), before the +-15.25 mm ring displacement

# ===== BEGIN 3D DRAWING CODE =====
import math, numpy as np, matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import proj3d
from matplotlib.patches import Patch
PIX3, SCT3, BP3, INK3 = "#2a78d6", "#eb6834", "#7a7975", "#52514e"
NAMES3 = {"L1_IBL": "IBL", "L2_PixelB0": "Pixel L1", "L3_PixelB1": "Pixel L2", "L4_PixelB2": "Pixel L3",
          "L5_SCT_B3": "SCT L1", "L6_SCT_B4": "SCT L2", "L7_SCT_B5": "SCT L3", "L8_SCT_B6": "SCT L4"}
PHI = np.linspace(math.pi, 2.5 * math.pi, 91)          # 270 degrees: the quadrant facing the viewer (x < 0, y > 0) is cut away
def _cyl(ax, r, z1, z2, col, alpha, lw=0.7):
    zz, pp = np.meshgrid(np.array([z1, z2]), PHI)                  # plot axes: X = beam z, Y = x, Z = y
    ax.plot_surface(zz, r * np.cos(pp), r * np.sin(pp), color=col, alpha=alpha, linewidth=0, shade=False)
    for z in (z1, z2): ax.plot(np.full_like(PHI, z), r * np.cos(PHI), r * np.sin(PHI), color=col, lw=lw)
    for ph in (PHI[0], PHI[-1]): ax.plot([z1, z2], [r * math.cos(ph)] * 2, [r * math.sin(ph)] * 2, color=col, lw=lw)
def _disk(ax, z, r1, r2, col, alpha):
    rr, pp = np.meshgrid(np.array([r1, r2]), PHI)
    ax.plot_surface(np.full_like(rr, z), rr * np.cos(pp), rr * np.sin(pp), color=col, alpha=alpha, linewidth=0, shade=False)
    ax.plot(np.full_like(PHI, z), r2 * np.cos(PHI), r2 * np.sin(PHI), color=col, lw=0.5)
def _callout(ax, xyz, text, xy_text, color, ha="center", va="bottom"):
    x2, y2, _ = proj3d.proj_transform(*xyz, ax.get_proj())
    ax.annotate(text, xy=(x2, y2), xycoords="data", xytext=xy_text, textcoords="figure fraction", fontsize=9, color=color, ha=ha, va=va, linespacing=1.25,
                arrowprops=dict(arrowstyle="-", color=INK3, lw=0.6, shrinkA=2, shrinkB=0), annotation_clip=False)
    ax.scatter(*xyz, s=8, color="#0b0b0b", depthshade=False)
def draw_3d(elements, beam_pipe_r_cm, geo, title, zlim, sct_disk_z_mm=None, fname=None):
    """geo 'Ideal': one callout per barrel layer; geo 'ATLAS': grouped callouts (barrel per detector, pixel disks, SCT end-cap). True scale on all axes."""
    els = [e for e in elements if e["geometry"].endswith(geo)]; full = geo.endswith("ATLAS")
    fig = plt.figure(figsize=(15, 7.2) if full else (12, 8.2))
    ax = fig.add_axes([-0.06, -0.10, 1.12, 1.02] if full else [0.02, -0.04, 0.96, 0.86], projection="3d")
    _cyl(ax, beam_pipe_r_cm, -zlim, zlim, BP3, 0.6, 0.5)
    for e in els:
        col = PIX3 if e["detector"] == "pixel" else SCT3
        if e["kind"] == "barrel": _cyl(ax, e["r_cm"], -e["half_length_cm"], e["half_length_cm"], col, 0.32 if e["detector"] == "pixel" else 0.10)
        else:
            for s_ in (1, -1): _disk(ax, s_ * e["z_cm"], e["rmin_cm"], e["rmax_cm"], col, 0.30 if e["detector"] == "pixel" else 0.14)
    ax.set_xlim(-zlim, zlim); ax.set_ylim(-60, 60); ax.set_zlim(-60, 60); ax.set_box_aspect((2 * zlim, 120, 120), zoom=1.0)
    ax.view_init(elev=20, azim=-60); ax.set_yticks([-50, 0, 50]); ax.set_zticks([-50, 0, 50])
    ax.set_xlabel("z [cm] (beam axis)", labelpad=14 if full else 10); ax.set_ylabel("x [cm]", labelpad=4); ax.set_zlabel("y [cm]", labelpad=2)
    ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False
    for a in (ax.xaxis, ax.yaxis, ax.zaxis): a._axinfo["grid"].update(linewidth=0.3, color="#d9d8d4")
    fig.canvas.draw()
    barrel = [e for e in els if e["kind"] == "barrel"]
    if not full:
        for k, e in enumerate(barrel):        # label row above the detector; anchor = top edge of the layer at z = +0.9 half length
            lab = f'{NAMES3[e["element"]]}\nr = {e["r_cm"] * 10:g} mm\n|z| < {e["half_length_cm"] * 10:g} mm'
            _callout(ax, (e["half_length_cm"] * 0.9, 0.0, e["r_cm"]), lab, (0.07 + 0.122 * k, 0.80), PIX3 if e["detector"] == "pixel" else SCT3)
    else:
        pb = [e for e in barrel if e["detector"] == "pixel"]; sb = [e for e in barrel if e["detector"] == "SCT"]
        _callout(ax, (pb[-1]["half_length_cm"] * 0.9, 0.0, pb[-1]["r_cm"]), "Pixel barrel: IBL + 3 layers\nr = " + ", ".join(f'{e["r_cm"] * 10:g}' for e in pb)
                 + " mm\n" + f'|z| < {pb[0]["half_length_cm"] * 10:g} (IBL), {pb[1]["half_length_cm"] * 10:g} mm', (0.30, 0.80), PIX3)
        _callout(ax, (sb[-1]["half_length_cm"] * 0.9, 0.0, sb[-1]["r_cm"]), "SCT barrel: 4 layers\nr = " + ", ".join(f'{e["r_cm"] * 10:g}' for e in sb)
                 + " mm\n" + f'|z| < {sb[0]["half_length_cm"] * 10:g} mm', (0.52, 0.80), SCT3)
        pd_ = [e for e in els if e["element"].startswith("PIXD")]; sd = [e for e in els if e["element"].startswith("SCTD")]
        _callout(ax, (pd_[-1]["z_cm"], 0.0, pd_[-1]["rmax_cm"]), "Pixel disks: 3 per side\n|z| = " + ", ".join(f'{e["z_cm"] * 10:g}' for e in pd_)
                 + " mm\n" + f'r = {pd_[0]["rmin_cm"] * 10:g}–{pd_[0]["rmax_cm"] * 10:g} mm', (0.74, 0.80), PIX3)
        last = [e for e in sd if e["element"].startswith("SCTD9")][0]
        zr = (f"{min(sct_disk_z_mm):g}–{max(sct_disk_z_mm):g} mm" if sct_disk_z_mm else "")
        _callout(ax, (last["z_cm"], 0.0, last["rmax_cm"]), "SCT end-cap: 9 disks per side\n(outer / middle / inner rings)\n"
                 + f"disk |z| = {zr}\n" + f'r = {min(e["rmin_cm"] for e in sd) * 10:g}–{max(e["rmax_cm"] for e in sd) * 10:g} mm', (0.93, 0.62), SCT3)
    _callout(ax, (-zlim * 0.85, 0.0, -beam_pipe_r_cm), f"beam pipe\ninner r = {beam_pipe_r_cm * 10:g} mm", (0.10, 0.12 if full else 0.10), BP3)
    fig.text(0.5, 0.975, title, ha="center", va="top", fontsize=14, weight="bold")
    fig.legend([Patch(color=PIX3, alpha=0.7), Patch(color=SCT3, alpha=0.7), Patch(color=BP3, alpha=0.8)], ["pixel", "SCT", "beam pipe"],
               loc="lower right", bbox_to_anchor=(0.99, 0.02), frameon=False, fontsize=10)
    if fname:
        fig.savefig(fname + ".png", dpi=300); fig.savefig(fname + ".pdf")
    return fig
# ===== END 3D DRAWING CODE =====

if __name__ == "__main__":
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    NOTE = ("Layers are infinitely thin surfaces; no material effects act on the quirk trajectories in either geometry. The TRT is not included (as in Knapen et al.). "
            "True scale on all three axes. Semi-transparent surfaces; one quadrant (x < 0, y > 0) is cut away to show the inner layers; the beam axis z is horizontal. Element positions from "
            "tables/X06_geometry_elements.csv (from sim/detsim07.build, the simulation geometry); beam pipe from geometry/atlas_run2_id_geometry.csv (R6). "
            "Radii: R1 Table 1 (arXiv:2007.07624); lengths: R2 (arXiv:1803.00844), R3 (JINST 3 S08003 ch. 4); disks: R1 Table 1, R3 Tables 4.3, 4.6.")
    for name, geo, title, zlim, cap in (
            ("GEO4_3d_ideal", "Ideal", "Ideal (Knapen et al.): 8 barrel layers, radii and lengths from ATLAS", 80.0,
             "**GEO4.** 3D view of the Ideal geometry (Knapen et al., arXiv:1708.02243; used in Stages 0–1): IBL, 3 pixel and 4 SCT barrel layers, no end-caps. "
             "Knapen et al. take the detector parameters from ATL-PHYS-PUB-2009-002 (written before the IBL was installed in 2014); the IBL is included as in the "
             "detector model of arXiv:1612.00850, App. A (their Ref. [34]). "),
            ("GEO5_3d_atlas", "ATLAS", "ATLAS Run 2 ID: same 8 barrel layers + 2×3 pixel disks + 2×9 SCT end-cap disks", 280.0,
             "**GEO5.** 3D view of the full ATLAS Run 2 inner-detector model (used in Stage 2): the same 8 barrel layers, 3 pixel disks and 9 SCT end-cap disks "
             "per side (each SCT disk drawn as its outer, middle and inner rings, R3 Table 4.6). ")):
        d = f"{HERE}/{name}"; os.makedirs(d, exist_ok=True)
        draw_3d(ELEMENTS, BEAM_PIPE_INNER_R_CM, geo, title, zlim, SCT_DISK_Z_MM, f"{d}/{name}")
        open(f"{d}/caption.md", "w").write(cap + NOTE + "\n")
        json.dump(dict(figure=name, script="FIGURES_GEOMETRY_2026-11-17/make_geometry_3d.py (matplotlib %s)" % matplotlib.__version__,
                       data={os.path.relpath(X6, R): sha(X6), os.path.relpath(GC, R): sha(GC)}), open(f"{d}/provenance.json", "w"), indent=1)
    print("make_geometry_3d: done")
