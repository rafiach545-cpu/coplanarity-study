#!/usr/bin/env python3
"""07 X02 figure (ROOT, 2026-11-17): N = 3 / N = 5 contours at 332 fb^-1, ideal (Stage 2 barrel geometry) vs ATLAS geometry on the same 10k-generated events,
with the Stage 2 (2k) contour for reference. Contour lines from tables/X02_contours_332fb.csv (compare/X02_ideal_vs_atlas.py, 06 contour method, T10);
grid nodes from tables/X02_N_grid_S2_Run3_ATLAS_300fb.csv. Style and helpers of 06_publication/FIGURES_ROOT_2026-11-04/make_figures_root.py, executed unchanged.
Run with /home/rafia/miniconda3/envs/root-env/bin/python. Output: compare/FIGURES_X02/X02_contours_ideal_vs_atlas_332fb/."""
import os
_src = open(os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/../../06_publication/FIGURES_ROOT_2026-11-04/make_figures_root.py")).read()
exec(_src[:_src.index("# ---------- contour figures")])
HERE = os.path.dirname(os.path.abspath(__file__)); TB = os.path.abspath(f"{HERE}/../tables"); OUT = f"{HERE}/FIGURES_X02"
exec(_src[_src.index("def segs("):_src.index("def grid4(")])                 # segs, draw_contours, draw_points of 06, unchanged
CON = [dict(r, scenario=r["setup"]) for r in csv.DictReader(open(f"{TB}/X02_contours_332fb.csv"))]
GP = [dict(scenario="S2_Run3_ATLAS", channel=r["channel"], sct=r["sct"], mass_gev=r["mass_gev"], lambda_eV=float(r["lambda_keV"]) * 1e3, k=int(float(r["k"])))
      for r in csv.DictReader(open(f"{TB}/X02_N_grid_S2_Run3_ATLAS_300fb.csv"))]
SCT = {"Z0": "#sigma_{long}^{SCT} = 0", "A580": "SCT 17 #mum / 580 #mum (ATLAS)", "Z1160": "SCT 34 #mum / 1.16 mm (Knapen)"}; SETS = ("Z0", "A580", "Z1160")
COL = {"S2_Run3_ATLAS": E136, "S1_Run3_Ideal": E13}
def save(c, name, caption, inputs):
    d = f"{OUT}/{name}"; os.makedirs(d, exist_ok=True)
    st.SetPaperSize(c.GetWw() / 100.0, c.GetWh() / 100.0); c.Print(f"{d}/{name}.pdf", "pdf Portrait")
    for ext in ("root", "C"): c.SaveAs(f"{d}/{name}.{ext}")
    subprocess.run([PDFTOPPM, "-png", "-r", "250", "-cropbox", "-singlefile", f"{d}/{name}.pdf", f"{d}/{name}"], check=True)
    open(f"{d}/caption.md", "w").write(caption.strip() + "\n")
    json.dump(dict(figure=name, script="compare/make_figures_X02.py (ROOT %s)" % ROOT.gROOT.GetVersion(), data={i: sha(f"{TB}/{i}") for i in inputs},
                   data_prepared_by="compare/X02_ideal_vs_atlas.py"), open(f"{d}/provenance.json", "w"), indent=1)
    KEEP.clear()
c = ROOT.TCanvas("X02", "", 1800, 1200); hd = ROOT.TPad("hd", "", 0, 0.95, 1, 1); top = ROOT.TPad("top", "", 0, 0.09, 1, 0.95); bot = ROOT.TPad("bot", "", 0, 0, 1, 0.09)
for q in (hd, top, bot): q.Draw()
KEEP.extend([c, hd, top, bot]); top.Divide(3, 2, 0.002, 0.002); header(hd, "Stage 2 #upoint Run 3 #upoint ATLAS vs Stage 1 #upoint Run 3 #upoint Ideal: 13.6 TeV, 332 fb^{-1}, zero background, same 10k events"); LE = {}
for i, (ch, sct) in enumerate([(a, b) for a in ("colored", "EW") for b in SETS]):
    p = top.cd(i + 1); p.SetLeftMargin(0.14); p.SetRightMargin(0.07); p.SetTopMargin(0.08)
    frame(p, XR[ch][0], 100, XR[ch][1], 25000, "m_{Q} [GeV]", "#Lambda [eV]", logy=True).GetXaxis().SetNdivisions(505)
    pts = draw_points("S2_Run3_ATLAS", ch, sct)
    if len(pts) > len(LE.get("pts", [])): LE["pts"] = pts
    if sct != "A580":
        s = draw_contours("S1_Run3_Ideal_2k", ch, sct, MUTED, 2, bands=False)
        for k_, v_ in s.items(): LE.setdefault("S1_Run3_Ideal_2k", {}).setdefault(k_, v_)
    for su in ("S1_Run3_Ideal", "S2_Run3_ATLAS"):
        n = draw_contours(su, ch, sct, COL[su], 3)
        for k_, v_ in n.items(): LE.setdefault(su, {}).setdefault(k_, v_)
    text(0.15, 0.94, f"#bf{{{CH[ch]}}}, {SCT[sct]}", 0.042); p.RedrawAxis()
E = []
for su, lab in (("S2_Run3_ATLAS", "S2#upointRun 3#upointATLAS (10k)"), ("S1_Run3_Ideal", "S1#upointRun 3#upointIdeal (10k)"), ("S1_Run3_Ideal_2k", "S1#upointRun 3#upointIdeal (2k, 06)")):
    E += [(LE.get(su, {}).get("exclusion"), f"{lab}: N = 3", "l"), (LE.get(su, {}).get("discovery"), f"{lab}: N = 5", "l")]
E += [(LE.get("S2_Run3_ATLAS", {}).get("band"), "N = 3, #pm 1#sigma Wilson band on k/n (dotted)", "l")] + [(g_, l_, "p") for g_, l_ in zip(LE.get("pts", []), ("grid point, k_{ATLAS} > 0", "grid point, k_{ATLAS} = 0"))]
bot.cd(); legend(0.03, 0.05, 0.99, 0.95, [e for e in E if e[0]], ncol=3, size=0.2)
save(c, "X02_contours_ideal_vs_atlas_332fb", """**X02.** Expected reach at √s = 13.6 TeV, 332 fb⁻¹, no pile-up, zero background: contours N = 3 (dashed) and N = 5 (solid),
N = L σ ε_trig f_ch k/n (σ, n_matched, n_trigger, both-charged from signal/inputs_large/counts.csv and the event files; k/n with Wilson 68% band, dotted for N = 3).
Orange: Stage 1 · Run 3 · Ideal (G01 stage2 geometry = the 8 barrel layers of Knapen et al.) and blue: Stage 2 · Run 3 · ATLAS (G01 atlas: barrel + end-caps, 8 ATLAS-like stations, D1),
both on the same 10 000-generated-event samples (server runs signal/runs/large_ideal, large_atlas, all bands Λ = 0.1–25 keV). Grey: Stage 1 · Run 3 · Ideal with 2000 generated events (06 S2,
barrel; no A580 setting there). Columns: SCT σ_long = 0, ATLAS 17 µm / 580 µm, Knapen 34 µm / 1.16 mm. Dots: grid points (filled: k_ATLAS > 0).
Contour method of 06 (log10 N on the grid, linear interpolation). Source: tables/X02_contours_332fb.csv, tables/X02_N_grid_S2_Run3_ATLAS_300fb.csv.""",
     ["X02_contours_332fb.csv", "X02_N_grid_S2_Run3_ATLAS_300fb.csv"])
print("make_figures_X02: done")
