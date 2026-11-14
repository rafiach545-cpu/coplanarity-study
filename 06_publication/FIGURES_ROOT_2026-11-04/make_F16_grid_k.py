#!/usr/bin/env python3
"""F16 (2026-11-09, test figure): one panel of Fig. 4 (colored, 13.6 TeV, 332 fb^-1) redrawn with the number of passing events k written at every grid point
(x for k = 0), Lambda on a linear axis in keV, for sigma_z = 1.16 mm and sigma_z = 0 side by side. Contours N = 3 and N = 5 are the Fig. 4 contours (data/contours.csv,
scenario 13p6TeV_332fb). Lambda = 0.1-0.7 keV would overlap on the 0-25 keV axis, so each column has a second, also linear, strip for 0-0.8 keV. F01-F15 are not
redrawn; style and helpers from make_figures_root.py. Data: data/grid_k_13p6TeV.csv (k, n from S2_N_grid_300fb.csv), data/contours.csv. Run with root-env python."""
import os
HERE = os.path.dirname(os.path.abspath(__file__)); src = open(f"{HERE}/make_figures_root.py").read(); exec(src[:src.index("# ---------- contour figures")])
CON = [r for r in read("contours.csv") if r["scenario"] == "13p6TeV_332fb" and r["channel"] == "colored" and r["band"] == "central"]
GK = [r for r in read("grid_k_13p6TeV.csv") if r["channel"] == "colored"]
def segs(sct, cn):
    out = {}
    for r in CON:
        if r["sct"] == sct and r["contour"] == cn: out.setdefault(r["segment"], ([], []))[0].append(fl(r["mass_gev"])); out[r["segment"]][1].append(fl(r["lambda_eV"]) / 1000)
    return list(out.values())
c = ROOT.TCanvas("F16", "", 1700, 1500); hd = ROOT.TPad("hd", "", 0, 0.955, 1, 1); bot = ROOT.TPad("bot", "", 0, 0, 1, 0.06)
for q in (hd, bot): q.Draw()
KEEP.extend([c, hd, bot]); hd.cd(); text(0.5, 0.45, "colored (3,1)_{2/3},  #sqrt{s} = 13.6 TeV, 332 fb^{-1}:  passing events k at every grid point", 0.5, 22); LE = {}
for j, sct in enumerate(("Z1160", "Z0")):
    x0, x1 = 0.5 * j, 0.5 * j + 0.5; c.cd()
    up = ROOT.TPad(f"up{j}", "", x0, 0.30, x1, 0.955); lo = ROOT.TPad(f"lo{j}", "", x0, 0.06, x1, 0.30)
    for q in (up, lo): q.SetLeftMargin(0.13); q.SetRightMargin(0.04); q.Draw()
    KEEP.extend([up, lo]); up.SetTopMargin(0.13); up.SetBottomMargin(0.07); lo.SetTopMargin(0.03); lo.SetBottomMargin(0.25)
    for pad, (y0, y1), lamsel, tsz in ((up, (0, 26), lambda l: l >= 1, 0.03), (lo, (0, 0.8), lambda l: l < 1, 0.075)):
        h = frame(pad, 480, y0, 2520, y1, "m_{Q} [GeV]", "#Lambda [keV]")
        if pad is lo:
            for a in (h.GetXaxis(), h.GetYaxis()): a.SetLabelSize(0.085); a.SetTitleSize(0.095)
            h.GetYaxis().SetTitleOffset(0.6); h.GetYaxis().SetNdivisions(504); h.GetXaxis().SetTitleOffset(1.05)
        else:
            h.GetXaxis().SetLabelSize(0); h.GetXaxis().SetTitle(""); h.GetYaxis().SetTitleOffset(1.15)
            bx = ROOT.TBox(480, 0, 2520, 0.8); bx.SetFillColor(GRID); bx.Draw(); KEEP.append(bx)
        for cn, sty in (("exclusion", 2), ("discovery", 1)):
            for xs, ys in segs(sct, cn):
                g = graph(xs, ys, E136, 3, sty); g.Draw("L"); LE.setdefault(cn, g)
        for r in GK:
            l = fl(r["lambda_keV"])
            if r["sct"] != sct or not lamsel(l): continue
            k = int(fl(r["k"])); text(fl(r["mass_gev"]), l, str(k) if k else "#times", tsz, 22, INK if k else MUTED, ndc=False)
        pad.cd(); pad.RedrawAxis()
    up.cd(); text(0.13, 0.95, f"#bf{{{SCT[sct]}}}", 0.034, 12)
    for m in sorted({int(fl(r["mass_gev"])) for r in GK}):
        n = [r for r in GK if int(fl(r["mass_gev"])) == m][0]["n_prop"]; text(m, 26.6, f"n = {int(fl(n))}", 0.026, 21, INK2, ndc=False)
    up.cd(); text(2480, 0.4, "0.1#minus0.7 keV: zoom below", 0.022, 32, INK2, ndc=False)
bot.cd(); legend(0.02, 0.08, 0.58, 0.92, [(LE["exclusion"], "N = 3 (exclusion), as Fig. 4", "l"), (LE["discovery"], "N = 5 (discovery), as Fig. 4", "l")], ncol=2, size=0.36)
text(0.97, 0.5, "numbers: k;   #times: k = 0;   n: propagated events", 0.36, 32, INK2)
save(c, "F16_grid_k_colored_13p6TeV", """**Fig. 16 (test).** Colored quirks at √s = 13.6 TeV and 332 fb⁻¹, as one panel of Fig. 4, with the number of passing events k written at every grid
point (× for k = 0) and Λ on a linear axis in keV. Left: SCT σ_z = 1.16 mm (Knapen); right: σ_z = 0, the same propagated events. n above each mass column: propagated events
(triggered, both quirk-hadrons charged); N = L σ ε_trig f_ch k/n. Lines: N = 3 (dashed) and N = 5 (solid), the Fig. 4 contours. The lower strip of each column repeats
Λ = 0.1–0.7 keV on its own linear scale (on the 0–25 keV axis these rows would overlap; shaded band). Source: S2_N_grid_300fb.csv via data/grid_k_13p6TeV.csv; data/contours.csv.""",
     ["grid_k_13p6TeV.csv", "contours.csv"])
print("F16_EXIT=0")
