#!/usr/bin/env python3
"""07 geometry figures (ROOT, 2026-11-17): the detector geometry exactly as simulated, Stage 1 · Ideal vs Stage 2 · ATLAS.
Every element position is read from tables/X06_geometry_elements.csv (written by compare/X06_geometry_comparison.py from sim/detsim07.build(),
i.e. the objects the simulation uses); the beam pipe from geometry/atlas_run2_id_geometry.csv (R6). No number is typed here.
Style and helpers: 06_publication/FIGURES_ROOT_2026-11-04/make_figures_root.py (code before the first figure, executed unchanged).
Run with /home/rafia/miniconda3/envs/root-env/bin/python. Output per figure: <name>/<name>.{pdf,png,root,C}, caption.md, provenance.json.
  GEO1_rz_ideal_vs_atlas : R-z quarter section (z >= 0, r >= 0), top Stage 1 · Ideal, bottom Stage 2 · ATLAS, with lines of constant eta
  GEO2_rz_pixel_zoom     : the pixel region (both stages have the same barrel; the disks exist only in Stage 2), every radius and |z| labelled
  GEO3_xy_barrel         : transverse view at z = 0 (identical in both stages), every radius labelled"""
import os, math
_src = open(os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/../../06_publication/FIGURES_ROOT_2026-11-04/make_figures_root.py")).read()
exec(_src[:_src.index("# ---------- contour figures")])
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); TB = f"{R}/tables"
X6 = f"{TB}/X06_geometry_elements.csv"; GC = f"{R}/geometry/atlas_run2_id_geometry.csv"
E = list(csv.DictReader(open(X6))); BP = [r for r in csv.DictReader(open(GC)) if r["name"] == "BP"][0]; RBP = float(BP["r_mm"]) / 10   # 2.35 cm (R6)
PIX, SCTC = E136, E13                                                      # identity: pixel blue, SCT orange (06 categorical slots 1, 2)
def els(geo): return [r for r in E if r["geometry"].endswith(geo)]
def save(c, name, caption, inputs):
    d = f"{HERE}/{name}"; os.makedirs(d, exist_ok=True)
    st.SetPaperSize(c.GetWw() / 100.0, c.GetWh() / 100.0); c.Print(f"{d}/{name}.pdf", "pdf Portrait")
    for ext in ("root", "C"): c.SaveAs(f"{d}/{name}.{ext}")
    subprocess.run([PDFTOPPM, "-png", "-r", "250", "-cropbox", "-singlefile", f"{d}/{name}.pdf", f"{d}/{name}"], check=True)
    open(f"{d}/caption.md", "w").write(caption.strip() + "\n")
    json.dump(dict(figure=name, script="FIGURES_GEOMETRY_2026-11-17/make_geometry_figures.py (ROOT %s)" % ROOT.gROOT.GetVersion(),
                   data={os.path.relpath(i, R): sha(i) for i in inputs}, data_prepared_by="compare/X06_geometry_comparison.py (from sim/detsim07.build)"),
              open(f"{d}/provenance.json", "w"), indent=1)
    KEEP.clear()
def seg(x1, y1, x2, y2, col, w, s=1): g = graph([x1, x2], [y1, y2], col, w, s); g.Draw("L"); return g
def draw_elements(geo, zmax, rmax, w=4):
    out = {}
    for r in els(geo):
        col = PIX if r["detector"] == "pixel" else SCTC
        if r["kind"] == "barrel":
            rr, h = fl(r["r_cm"]), fl(r["half_length_cm"]); g = seg(0, rr, min(h, zmax), rr, col, w)
        else:
            z = fl(r["z_cm"]); g = seg(z, fl(r["rmin_cm"]), z, min(fl(r["rmax_cm"]), rmax), col, w)
        out.setdefault((r["detector"], r["kind"]), g)
    return out
def eta_lines(zmax, rmax, etas, lab_size=0.032, side_z=None):
    """dashed lines of constant eta from (0, 0); label above the frame where the line leaves through the top, else (side_z given) below the line at z = side_z"""
    for eta in etas:
        sh = math.sinh(eta); z_end, r_end = (zmax, zmax / sh) if zmax / sh <= rmax else (rmax * sh, rmax)
        seg(0, 0, z_end, r_end, GRID if eta not in (2.5,) else MUTED, 1, 2)
        if r_end >= rmax - 1e-9: text(z_end, r_end + 0.012 * rmax, f"#eta = {eta:g}", lab_size, 21, INK2, ndc=False)
        elif side_z: text(side_z, side_z / sh - 0.05 * rmax, f"#eta = {eta:g}", lab_size, 23, INK2, ndc=False)
        else: text(z_end - 0.01 * zmax, r_end, f"#eta = {eta:g}", lab_size, 32, INK2, ndc=False)

# ---------- GEO1: R-z quarter section, Stage 1 · Ideal (top) and Stage 2 · ATLAS (bottom)
ZM, RM = 285.0, 62.0
c = ROOT.TCanvas("GEO1", "", 1800, 1450); KEEP.append(c)
pads = [ROOT.TPad("pt", "", 0, 0.55, 1, 1), ROOT.TPad("pb", "", 0, 0.09, 1, 0.55), ROOT.TPad("pl", "", 0, 0, 1, 0.09)]
for q in pads: q.Draw(); KEEP.append(q)
LE = []
for p, geo, title in ((pads[0], "Ideal", "(a) Ideal (Knapen et al.): 8 barrel layers, radii and lengths from ATLAS"),
                      (pads[1], "ATLAS", "(b) ATLAS Run 2 ID: same 8 barrel layers + 2 #times 3 pixel disks + 2 #times 9 SCT end-cap disks")):
    p.SetLeftMargin(0.07); p.SetRightMargin(0.03); p.SetTopMargin(0.19); p.SetBottomMargin(0.15)
    h = frame(p, 0, 0, ZM, RM, "z [cm]", "r [cm]"); h.GetYaxis().SetTitleOffset(0.55); h.GetXaxis().SetTitleOffset(1.0)
    for a in (h.GetXaxis(), h.GetYaxis()): a.SetLabelSize(0.06); a.SetTitleSize(0.065)
    eta_lines(ZM, RM, (0.5, 1.0, 1.5, 2.0, 2.5), 0.05, side_z=232.0)
    g = seg(0, RBP, ZM, RBP, MUTED, 2); LE = LE or [(g, f"beam pipe (inner r = {RBP * 10:g} mm)", "l")]
    o = draw_elements(geo, ZM, RM)
    if geo == "ATLAS":
        LE = [(o[("pixel", "barrel")], "pixel", "l"), (o[("SCT", "barrel")], "SCT", "l")] + LE
        for r in els("ATLAS"):
            if r["element"].startswith("SCTD") and r["element"].endswith("outer"):
                text(fl(r["z_cm"]), 57.3, r["element"][4], 0.045, 21, INK2, ndc=False)
        text(80.0, 57.3, "SCT disk", 0.045, 31, INK2, ndc=False)
    text(0.07, 0.915, title, 0.06, 11)
    p.RedrawAxis()
pads[2].cd(); legend(0.2, 0.15, 0.85, 0.85, [e for e in LE if e[0]], ncol=3, size=0.3)
save(c, "GEO1_rz_ideal_vs_atlas", """**GEO1.** Inner-detector geometry as simulated, R–z quarter section (z ≥ 0, r ≥ 0; the −z side is the mirror image); axes not to scale.
(a) Ideal (Knapen et al., arXiv:1708.02243; used in Stages 0–1): 8 barrel layers only — IBL, 3 pixel and 4 SCT layers.
(b) ATLAS Run 2 inner detector (used in Stage 2): the same 8 barrel layers plus 3 pixel disks and 9 SCT end-cap disks per side; each SCT disk is drawn as its rings (outer, middle,
inner; ring centres displaced by ±15.25 mm, R3 Table 4.6). Blue: pixel, orange: SCT; grey: beam pipe (inner radius 23.5 mm, R6, R2). Dashed: lines of constant
pseudorapidity η from the nominal interaction point (z0 = 0). Numbers above the SCT end-cap: disk index. Radii: R1 Table 1 (IBL 33.25 mm; pixel 50.5, 88.5, 122.5 mm;
SCT 299, 371, 443, 514 mm); lengths: R2 (IBL |z| < 330.15 mm) and R3 (pixel 801 mm, SCT 1498 mm active length); disks: R1 Table 1, R3 Tables 4.3 and 4.6.
Source: tables/X06_geometry_elements.csv (from sim/detsim07.build, the simulation geometry) and geometry/atlas_run2_id_geometry.csv.
Layers are infinitely thin surfaces; no material effects act on the quirk trajectories in either geometry (material enters only the background electrons and the photon-conversion probability). The TRT is not included in either geometry (as in Knapen et al.). Lines of constant η are drawn from the nominal interaction point z0 = 0; the longitudinal beam spot (σ_z = 45 mm) smears the acceptance edges.
Knapen et al. (arXiv:1708.02243) take the detector parameters from ATL-PHYS-PUB-2009-002 (their Ref. [27], written before the IBL was installed in 2014); the IBL is included here as in the detector model of Knapen et al., arXiv:1612.00850, App. A (their Ref. [34]), which lists the IBL as one barrel layer.""", [X6, GC])

# ---------- GEO2: pixel region zoom with every radius and |z| labelled
ZP, RP = 72.0, 16.0
c = ROOT.TCanvas("GEO2", "", 1900, 950); c.SetLeftMargin(0.07); c.SetRightMargin(0.26); c.SetTopMargin(0.12); c.SetBottomMargin(0.12); KEEP.append(c)
h = frame(c, 0, 0, ZP, RP, "z [cm]", "r [cm]"); h.GetYaxis().SetTitleOffset(0.6)
eta_lines(ZP, RP, (1.0, 1.5, 2.0, 2.5, 3.0), 0.03, side_z=46.0)
seg(0, RBP, ZP, RBP, MUTED, 2); text(ZP + 1.0, RBP, f"beam pipe (inner): r = {RBP * 10:g} mm", 0.028, 12, INK2, ndc=False)
for r in els("ATLAS"):
    if r["detector"] != "pixel": continue
    if r["kind"] == "barrel":
        rr, hz = fl(r["r_cm"]), fl(r["half_length_cm"]); seg(0, rr, hz, rr, PIX, 5); seg(hz, rr, ZP, rr, GRID, 1, 3)
        nm = {"L1_IBL": "IBL", "L2_PixelB0": "pixel layer 1", "L3_PixelB1": "pixel layer 2", "L4_PixelB2": "pixel layer 3"}[r["element"]]
        text(ZP + 1.0, rr, f"{nm}: r = {rr * 10:g} mm, |z| < {hz * 10:g} mm", 0.028, 12, INK, ndc=False)
    else:
        z = fl(r["z_cm"]); r1, r2 = fl(r["rmin_cm"]), fl(r["rmax_cm"]); seg(z, r1, z, r2, PIX, 5)
        t = text(z - 0.9, 0.5 * (r1 + r2), f"disk {r['element'][-1]}: |z| = {z * 10:g} mm", 0.026, 22, INK, ndc=False); t.SetTextAngle(90)
text(57.5, 15.3, f"pixel disks: r = {fl(els('ATLAS')[8]['rmin_cm']) * 10:g} #minus {fl(els('ATLAS')[8]['rmax_cm']) * 10:g} mm", 0.028, 21, INK2, ndc=False)
text(0.07, 0.955, "Pixel detector as simulated (barrel: Ideal and ATLAS; disks: ATLAS only)", 0.036, 11)
c.RedrawAxis()
save(c, "GEO2_rz_pixel_zoom", """**GEO2.** Pixel region of the simulated geometry, R–z view (z ≥ 0). The IBL and the 3 pixel barrel layers are identical in the Ideal and the
ATLAS geometry; the 3 pixel disks per side exist only in the ATLAS geometry. Radii: R1 Table 1 (IBL 33.25 mm, conflict with R2 33.5 mm noted in the geometry CSV;
pixel 50.5, 88.5, 122.5 mm); IBL length R2 Table 1 (|z| < 330.15 mm); pixel barrel active length 801 mm (R3 Table 4.3 caption); disks |z| = 495, 580, 650 mm,
r = 88.8–149.6 mm (R1 Table 1, R3 Table 4.3). Beam pipe inner radius 23.5 mm (R6; R2: reduced from 29 mm to 23.5 mm for the IBL). Dashed: constant η from z0 = 0.
Source: tables/X06_geometry_elements.csv, geometry/atlas_run2_id_geometry.csv.
Layers are infinitely thin surfaces; no material effects act on the quirk trajectories in either geometry (material enters only the background electrons and the photon-conversion probability). The TRT is not included in either geometry (as in Knapen et al.). Lines of constant η are drawn from the nominal interaction point z0 = 0; the longitudinal beam spot (σ_z = 45 mm) smears the acceptance edges.""", [X6, GC])

# ---------- GEO3: transverse view at z = 0
c = ROOT.TCanvas("GEO3", "", 1800, 1200); c.SetLeftMargin(0.11); c.SetRightMargin(0.33); c.SetTopMargin(0.06); c.SetBottomMargin(0.10); KEEP.append(c)
h = frame(c, -60, -60, 60, 60, "x [cm]", "y [cm]"); h.GetYaxis().SetTitleOffset(0.9)
def circ(rr, col, w):
    xs = [rr * math.cos(2 * math.pi * k / 720) for k in range(721)]; ys = [rr * math.sin(2 * math.pi * k / 720) for k in range(721)]; g = graph(xs, ys, col, w); g.Draw("L"); return g
circ(RBP, MUTED, 2)
names = {"L1_IBL": "IBL", "L2_PixelB0": "pixel 1", "L3_PixelB1": "pixel 2", "L4_PixelB2": "pixel 3", "L5_SCT_B3": "SCT 1", "L6_SCT_B4": "SCT 2", "L7_SCT_B5": "SCT 3", "L8_SCT_B6": "SCT 4"}
for k, r in enumerate([r for r in els("ATLAS") if r["kind"] == "barrel"]):
    rr = fl(r["r_cm"]); circ(rr, PIX if r["detector"] == "pixel" else SCTC, 3)
text(0.70, 0.86, "radius (R1, R6)", 0.03, 11, INK)
order = ["beam pipe"] + [r["element"] for r in els("ATLAS") if r["kind"] == "barrel"]
for k, nm in enumerate(order):
    rr = RBP if nm == "beam pipe" else fl([r for r in els("ATLAS") if r["element"] == nm][0]["r_cm"])
    det = "beam" if nm == "beam pipe" else [r for r in els("ATLAS") if r["element"] == nm][0]["detector"]
    lab = f"beam pipe (inner): {rr * 10:g} mm" if nm == "beam pipe" else f"{names[nm]}: {rr * 10:g} mm"
    text(0.70, 0.80 - 0.055 * k, lab, 0.03, 12, MUTED if det == "beam" else (PIX if det == "pixel" else SCTC))
text(0.09, 0.955, "Barrel layers at z = 0 (same in Ideal and ATLAS)", 0.032, 11)
c.RedrawAxis()
save(c, "GEO3_xy_barrel", """**GEO3.** Transverse (x–y) view at z = 0 of the 8 barrel layers as simulated (cylinders), identical in the Ideal and the ATLAS geometry.
Blue: IBL and pixel layers; orange: SCT layers; grey: beam pipe inner radius. Radii from R1 Table 1 (arXiv:2007.07624); beam pipe from R6 (arXiv:1707.02826) and R2
(arXiv:1803.00844). In the real detector the layers are made of tilted staves/modules (IBL 14°, pixel 20°, SCT 11–11.25°, R2, R3); the simulation uses cylinders at the
quoted radii. Source: tables/X06_geometry_elements.csv, geometry/atlas_run2_id_geometry.csv.
Layers are infinitely thin surfaces; no material effects act on the quirk trajectories in either geometry.""", [X6, GC])
print("make_geometry_figures: done")
