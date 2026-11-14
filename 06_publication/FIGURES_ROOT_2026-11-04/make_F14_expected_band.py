#!/usr/bin/env python3
"""F14 (2026-11-05): expected exclusion band ("Brazil band") vs pile-up, 13.6 TeV, 332 fb^-1, sigma_z = 0. Separate from make_figures_root.py so that the final
figures F01-F13 are not redrawn; style and helpers are taken from it unchanged (its code before the first figure). Data: data/expected_bands.csv (S2_12),
data/unc_reach.csv (S2_11). Run with /home/rafia/miniconda3/envs/root-env/bin/python."""
import os
HERE = os.path.dirname(os.path.abspath(__file__)); src = open(f"{HERE}/make_figures_root.py").read(); exec(src[:src.index("# ---------- contour figures")])
CH = {"colored": "colored (3,1)_{2/3}", "EW": "EW (1,1)_{1}"}
BD = read("expected_bands.csv"); UR = read("unc_reach.csv")
GREEN, YELLOW = C("#00cc00"), C("#ffcc00")                                # HEP convention for expected +-1 / +-2 sigma bands
c = ROOT.TCanvas("F14", "", 1600, 760); tp = ROOT.TPad("tp", "", 0, 0.14, 1, 1); bp = ROOT.TPad("bp", "", 0, 0, 1, 0.14)
for q in (tp, bp): q.Draw()
KEEP.extend([c, tp, bp]); tp.Divide(2, 1, 0.002, 0.002); LE = {}
def band(xs, lo, hi, col):
    g = ROOT.TGraph(2 * len(xs), array.array("d", xs + xs[::-1]), array.array("d", lo + hi[::-1])); g.SetFillColor(col); g.SetLineWidth(0); g.Draw("F"); KEEP.append(g); return g
for j, (ch, yr) in enumerate((("colored", (1400, 1850)), ("EW", (550, 860)))):
    p = tp.cd(j + 1); p.SetLeftMargin(0.15); p.SetBottomMargin(0.14)
    frame(p, -3, yr[0], 63, yr[1], "pile-up #mu", "exclusion reach in m_{Q} [GeV]")
    R = sorted([r for r in BD if r["channel"] == ch and r["sct"] == "Z0"], key=lambda r: fl(r["mu"])); mu = [fl(r["mu"]) for r in R]
    g = lambda k: [fl(r[k]) for r in R]
    LE["y"] = band(mu, g("reach_p2"), g("reach_m2"), YELLOW); LE["g"] = band(mu, g("reach_p1"), g("reach_m1"), GREEN)
    LE["med"] = graph(mu, g("reach_med"), INK, 2, 2); LE["med"].Draw("L")
    U = {fl(r["mu"]): r for r in UR if r["sqrt_s_TeV"] == "13.6" and r["channel"] == ch and r["sct"] == "Z0" and r["contour"] == "exclusion" and r["mu"] != "-1"}
    v = g("nominal_reach"); e = gerr(mu, v, [x - fl(U[m]["all_16"]) for x, m in zip(v, mu)], [fl(U[m]["all_84"]) - x for x, m in zip(v, mu)], E136, 20, size=1.4); e.Draw("P"); LE["mc"] = e
    text(0.93, 0.87, f"#bf{{{CH[ch]}}}", 0.05, 31); text(0.93, 0.80, "13.6 TeV, 332 fb^{-1}, #sigma_{z}^{SCT} = 0", 0.042, 31, INK2); p.RedrawAxis()
bp.cd(); legend(0.03, 0.08, 0.97, 0.92, [(LE["med"], "expected (median n_{obs})", "l"), (LE["g"], "expected #pm1#sigma (n_{obs} ~ Poisson(b))", "f"),
       (LE["y"], "expected #pm2#sigma", "f"), (LE["mc"], "our result (n_{obs} = round(b)) #pm MC statistics (S2_11)", "pe")], ncol=2, size=0.27)
save(c, "F14_expected_band", """**Fig. 14.** Expected 95% CL_s exclusion reach versus pile-up at 13.6 TeV and 332 fb⁻¹, σ_z = 0. Dashed line: reach for the median n_obs of
background-only pseudo-experiments, n_obs ~ Poisson(b), b from the converted-photon background (S2_09). Green / yellow: n_obs at the ±1σ / ±2σ quantiles of
Poisson(b) (2.3–97.7%); more observed events give a weaker limit, so the upper edge belongs to the −σ side. Blue points: the result quoted in the report
(n_obs = round(b)) with its MC statistical uncertainty (16–84% of the S2_11 toys), a different quantity. For σ_z = 1.16 mm, b = 0 and the band has zero width
(n_obs = 0 always). Source: S2_expected_bands.csv, S2_unc_reach.csv via data/expected_bands.csv, data/unc_reach.csv.""", ["expected_bands.csv", "unc_reach.csv"])
print("F14_EXIT=0")
