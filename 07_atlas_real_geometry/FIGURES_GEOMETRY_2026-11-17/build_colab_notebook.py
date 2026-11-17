#!/usr/bin/env python3
"""Builds geometry_visualization_colab.ipynb (2026-11-17): a self-contained Google Colab notebook (numpy + matplotlib only, no upload needed) that draws
the simulated detector geometry (Stage 1 · Ideal vs Stage 2 · ATLAS). The element table inside the notebook is written here from
tables/X06_geometry_elements.csv (from sim/detsim07.build, the simulation geometry) and the beam pipe from geometry/atlas_run2_id_geometry.csv,
so no number is retyped by hand; a checksum of the source CSV is printed in the notebook. Run with /home/rafia/venvs/f6fast/bin/python."""
import os, csv, json, hashlib, nbformat as nbf
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/..")
X6 = f"{R}/tables/X06_geometry_elements.csv"; GC = f"{R}/geometry/atlas_run2_id_geometry.csv"
rows = list(csv.DictReader(open(X6))); bp = [r for r in csv.DictReader(open(GC)) if r["name"] == "BP"][0]
keep = ["geometry", "element", "kind", "detector", "r_cm", "half_length_cm", "z_cm", "rmin_cm", "rmax_cm"]
data = [{k: r[k] for k in keep} for r in rows]
sha = hashlib.sha256(open(X6, "rb").read()).hexdigest()
_s3 = open(f"{HERE}/make_geometry_3d.py").read(); SRC3D = _s3[_s3.index("# ===== BEGIN 3D DRAWING CODE ====="):_s3.index("# ===== END 3D DRAWING CODE =====")].strip()
DISKZ = sorted({float(r["z_mm"]) for r in csv.DictReader(open(GC)) if r["region"] == "endcap_ring"})
md = lambda s: nbf.v4.new_markdown_cell(s.strip()); code = lambda s: nbf.v4.new_code_cell(s.strip())
cells = [
md("""
# Inner-detector geometry used in the quirk simulation: Ideal (Knapen et al.) vs ATLAS Run 2 ID

This notebook draws the detector exactly as it is simulated in this study. It needs only `numpy` and `matplotlib` (available in Google Colab), so no file upload is needed.

- **Source of the numbers.** The element table in the next cell was written automatically from `07_atlas_real_geometry/tables/X06_geometry_elements.csv`. That file is produced by `compare/X06_geometry_comparison.py` from `sim/detsim07.build()`, i.e. the objects the simulation uses. The beam pipe comes from `geometry/atlas_run2_id_geometry.csv`. No number was typed by hand.
- **Ideal (Knapen et al.)**, used in Stages 0–1: 8 barrel layers, no end-caps. Knapen et al. define the 8-layer Pixel+SCT structure; the numerical radii and lengths are taken from ATLAS documentation.
- **ATLAS Run 2 ID**, used in Stage 2: the same 8 barrel layers, plus 3 pixel disks and 9 SCT end-cap disks per side. Each SCT disk is made of rings.

**Notes**
- Layers are infinitely thin surfaces. No material effects act on the quirk trajectories in either geometry; material enters only the background electrons and the photon-conversion probability.
- The TRT is not included in either geometry, as in Knapen et al.
- Lines of constant η are drawn from the nominal interaction point z0 = 0. The longitudinal beam spot (σ_z = 45 mm) smears the acceptance edges.
- Knapen et al. take the detector parameters from ATL-PHYS-PUB-2009-002 (their Ref. [27]), which was written before the IBL was installed in 2014. The IBL is included here as in the detector model of Knapen et al., arXiv:1612.00850, App. A (their Ref. [34]).

**References**
- [R1] ATLAS Collaboration, *Alignment of the ATLAS Inner Detector in Run-2*, Eur. Phys. J. C 80 (2020) 1194, arXiv:2007.07624. Table 1: barrel radii, pixel disk |z|, SCT disk |z| range.
- [R2] ATLAS IBL Collaboration, *Production and Integration of the ATLAS Insertable B-Layer*, JINST 13 (2018) T05008, arXiv:1803.00844. IBL |z| < 330.15 mm; *"The inner radius [of the beam pipe] was reduced from 29 mm to 23.5 mm"*.
- [R3] ATLAS Collaboration, *The ATLAS Experiment at the CERN LHC*, JINST 3 (2008) S08003, ch. 4. Pixel and SCT active lengths, pixel disk radii, SCT end-cap disks and rings (Tables 4.3, 4.5, 4.6).
- [R6] ATLAS Collaboration, *Study of the material of the ATLAS inner detector for Run 2 of the LHC*, JINST 12 (2017) P12009, arXiv:1707.02826. Beam pipe: 0.8 mm Be, inner radius 23.5 mm.
- [R10] S. Knapen, H. K. Lou, M. Papucci, J. Setford, *Tracking down quirks at the LHC*, Phys. Rev. D 96 (2017) 115015, arXiv:1708.02243. The 8-layer structure; barrel only.
"""),
code(f"""
# Element table of the simulated geometries (generated from tables/X06_geometry_elements.csv, sha256 {sha[:16]}...; units: cm).
# Disks are listed for the +z side only; the -z side is the mirror image.
ELEMENTS = {json.dumps(data, indent=0)}
BEAM_PIPE_INNER_R_CM = {float(bp["r_mm"]) / 10!r}   # R6 (0.8 mm Be, inner radius 23.5 mm); R2: reduced from 29 mm to 23.5 mm
for e in ELEMENTS:
    for k in ("r_cm", "half_length_cm", "z_cm", "rmin_cm", "rmax_cm"):
        e[k] = float(e[k]) if e[k] not in ("", None) else None
print(len([e for e in ELEMENTS if e["geometry"].endswith("Ideal")]), "elements in Stage 1 · Ideal;",
      len([e for e in ELEMENTS if e["geometry"].endswith("ATLAS")]), "elements in Stage 2 · ATLAS (+z side)")
"""),
code("""
import math, numpy as np, matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.linewidth": 0.8, "xtick.direction": "in", "ytick.direction": "in",
                     "xtick.top": True, "ytick.right": True})
PIX, SCT, BPC, ETA = "#2a78d6", "#eb6834", "#898781", "#bdbbb6"
def elements(geo): return [e for e in ELEMENTS if e["geometry"].endswith(geo)]
def draw_rz(ax, geo, zmax=285.0, rmax=62.0, etas=(0.5, 1.0, 1.5, 2.0, 2.5)):
    for eta in etas:                                    # straight lines of constant pseudorapidity from (z, r) = (0, 0)
        sh = math.sinh(eta); z_end, r_end = (zmax, zmax / sh) if zmax / sh <= rmax else (rmax * sh, rmax)
        ax.plot([0, z_end], [0, r_end], ls="--", lw=0.8, color=ETA, zorder=1)
        if r_end >= rmax - 1e-9: ax.text(z_end, rmax + 0.8, f"η = {eta:g}", ha="center", va="bottom", fontsize=9, color="#52514e")
        else: ax.text(232, 232 / sh - 3.0, f"η = {eta:g}", ha="center", va="top", fontsize=9, color="#52514e")
    ax.plot([0, zmax], [BEAM_PIPE_INNER_R_CM] * 2, color=BPC, lw=1.5, zorder=2)
    for e in elements(geo):
        c = PIX if e["detector"] == "pixel" else SCT
        if e["kind"] == "barrel": ax.plot([0, e["half_length_cm"]], [e["r_cm"]] * 2, color=c, lw=3, solid_capstyle="butt", zorder=3)
        else: ax.plot([e["z_cm"]] * 2, [e["rmin_cm"], e["rmax_cm"]], color=c, lw=3, solid_capstyle="butt", zorder=3)
    ax.set_xlim(0, zmax); ax.set_ylim(0, rmax); ax.set_xlabel("z [cm]"); ax.set_ylabel("r [cm]")
"""),
md("## 1. R–z quarter section (z ≥ 0, r ≥ 0)"),
code("""
fig, axs = plt.subplots(2, 1, figsize=(13, 9.5), constrained_layout=True)
draw_rz(axs[0], "Ideal"); axs[0].set_title("(a) Ideal (Knapen et al.): 8 barrel layers, radii and lengths from ATLAS", loc="left", pad=18)
draw_rz(axs[1], "ATLAS"); axs[1].set_title("(b) ATLAS Run 2 ID: same 8 barrel layers + 2×3 pixel disks + 2×9 SCT end-cap disks", loc="left", pad=18)
for e in elements("ATLAS"):
    if e["element"].startswith("SCTD") and e["element"].endswith("outer"): axs[1].text(e["z_cm"], 57.5, e["element"][4], ha="center", fontsize=9, color="#52514e")
axs[1].text(80, 57.5, "SCT disk", ha="right", fontsize=9, color="#52514e")
from matplotlib.lines import Line2D
fig.legend([Line2D([], [], color=PIX, lw=3), Line2D([], [], color=SCT, lw=3), Line2D([], [], color=BPC, lw=1.5)],
           ["pixel", "SCT", f"beam pipe (inner r = {BEAM_PIPE_INNER_R_CM * 10:g} mm)"], loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, -0.04))
fig.savefig("GEO1_rz_ideal_vs_atlas_colab.png", dpi=200, bbox_inches="tight"); plt.show()
"""),
md("## 2. Pixel region (barrel: Ideal and ATLAS; disks: ATLAS only)"),
code("""
fig, ax = plt.subplots(figsize=(13, 6.5), constrained_layout=True)
draw_rz(ax, "ATLAS", zmax=72.0, rmax=16.0, etas=(1.0, 1.5, 2.0, 2.5, 3.0))
names = {"L1_IBL": "IBL", "L2_PixelB0": "pixel layer 1", "L3_PixelB1": "pixel layer 2", "L4_PixelB2": "pixel layer 3"}
for e in elements("ATLAS"):
    if e["detector"] != "pixel": continue
    if e["kind"] == "barrel":
        ax.text(73, e["r_cm"], f'{names[e["element"]]}: r = {e["r_cm"] * 10:g} mm, |z| < {e["half_length_cm"] * 10:g} mm', va="center", fontsize=10, clip_on=False)
    else:
        ax.text(e["z_cm"] - 0.9, 0.5 * (e["rmin_cm"] + e["rmax_cm"]), f'disk {e["element"][-1]}: |z| = {e["z_cm"] * 10:g} mm', rotation=90, ha="center", va="center", fontsize=9)
ax.text(73, BEAM_PIPE_INNER_R_CM, f"beam pipe (inner): r = {BEAM_PIPE_INNER_R_CM * 10:g} mm", va="center", fontsize=10, color="#52514e", clip_on=False)
d = [e for e in elements("ATLAS") if e["element"] == "PIXD1"][0]
ax.text(57.5, 15.3, f'pixel disks: r = {d["rmin_cm"] * 10:g}–{d["rmax_cm"] * 10:g} mm', ha="center", fontsize=10, color="#52514e")
fig.savefig("GEO2_rz_pixel_zoom_colab.png", dpi=200, bbox_inches="tight"); plt.show()
"""),
md("## 3. Transverse view at z = 0 (same in Ideal and ATLAS)"),
code("""
fig, ax = plt.subplots(figsize=(8.5, 8.5), constrained_layout=True)
t = np.linspace(0, 2 * np.pi, 721)
ax.plot(BEAM_PIPE_INNER_R_CM * np.cos(t), BEAM_PIPE_INNER_R_CM * np.sin(t), color=BPC, lw=1.5, label=f"beam pipe (inner): {BEAM_PIPE_INNER_R_CM * 10:g} mm")
names.update({"L5_SCT_B3": "SCT 1", "L6_SCT_B4": "SCT 2", "L7_SCT_B5": "SCT 3", "L8_SCT_B6": "SCT 4"})
for e in [e for e in elements("ATLAS") if e["kind"] == "barrel"]:
    ax.plot(e["r_cm"] * np.cos(t), e["r_cm"] * np.sin(t), color=PIX if e["detector"] == "pixel" else SCT, lw=2, label=f'{names[e["element"]]}: {e["r_cm"] * 10:g} mm')
ax.set_aspect("equal"); ax.set_xlim(-60, 60); ax.set_ylim(-60, 60); ax.set_xlabel("x [cm]"); ax.set_ylabel("y [cm]")
ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1), frameon=False, title="radius (R1, R6)")
fig.savefig("GEO3_xy_barrel_colab.png", dpi=200, bbox_inches="tight"); plt.show()
"""),
md("## 4. 3D cut-away views (true scale; one quadrant removed to show the inner layers)"),
code(SRC3D),
code("""
SCT_DISK_Z_MM = """ + repr(DISKZ) + """   # SCT end-cap disk |z| (R3 Table 4.6), before the ±15.25 mm ring displacement
draw_3d(ELEMENTS, BEAM_PIPE_INNER_R_CM, "Ideal", "Ideal (Knapen et al.): 8 barrel layers, radii and lengths from ATLAS", 80.0, SCT_DISK_Z_MM, "GEO4_3d_ideal_colab"); plt.show()
draw_3d(ELEMENTS, BEAM_PIPE_INNER_R_CM, "ATLAS", "ATLAS Run 2 ID: same 8 barrel layers + 2×3 pixel disks + 2×9 SCT end-cap disks", 280.0, SCT_DISK_Z_MM, "GEO5_3d_atlas_colab"); plt.show()
"""),
md("## 5. Element table and straight-line η coverage (z0 = 0)"),
code("""
print(f"{'geometry':16s} {'element':18s} {'kind':6s} {'det':5s} {'r or |z| (cm)':>14s} {'extent (cm)':>16s} {'|eta| range':>14s}")
for e in ELEMENTS:
    if e["kind"] == "barrel":
        lo, hi = 0.0, math.asinh(e["half_length_cm"] / e["r_cm"]); pos, ext = f'r = {e["r_cm"]:g}', f'|z| < {e["half_length_cm"]:g}'
    else:
        lo, hi = math.asinh(e["z_cm"] / e["rmax_cm"]), math.asinh(e["z_cm"] / e["rmin_cm"]); pos, ext = f'|z| = {e["z_cm"]:g}', f'r {e["rmin_cm"]:g}-{e["rmax_cm"]:g}'
    print(f'{e["geometry"]:16s} {e["element"]:18s} {e["kind"]:6s} {e["detector"]:5s} {pos:>14s} {ext:>16s} {lo:6.2f} - {hi:5.2f}')
"""),
]
nb = nbf.v4.new_notebook(); nb["cells"] = cells; nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}}
nbf.write(nb, f"{HERE}/geometry_visualization_colab.ipynb"); print("wrote geometry_visualization_colab.ipynb, source sha256", sha)
