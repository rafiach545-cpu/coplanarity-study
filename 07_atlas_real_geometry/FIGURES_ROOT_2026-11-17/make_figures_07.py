#!/usr/bin/env python3
"""07 figures (ROOT), step 2 of 2: every figure drawn with ROOT from the plot-ready CSVs in data/ (prepare_data_07.py). No numbers are computed here beyond
unit changes and ratios of two CSV columns. Style and helpers: 06_publication/FIGURES_ROOT_2026-11-04/make_figures_root.py, its code before the first figure,
executed unchanged (as make_F14_expected_band.py), and its contour helpers segs, draw_contours, draw_points; save() is redefined only to name this script in provenance.json.
Run with /home/rafia/miniconda3/envs/root-env/bin/python (ROOT 6.40). Output per figure: Gxx_<name>/Gxx_<name>.{pdf,png,root,C}, caption.md, provenance.json."""
import os
_src = open(os.path.abspath(f"{os.path.dirname(os.path.abspath(__file__))}/../../06_publication/FIGURES_ROOT_2026-11-04/make_figures_root.py")).read()
exec(_src[:_src.index("# ---------- contour figures")])
SZ = {"Z0": C("#6250d6"), "A580": C("#2a78d6"), "Z1160": C("#1baf7a")}       # identity: SCT setting (06 slots 7, 1, 3); Stage 1 · Run 3 · Ideal (2k) = MUTED grey
SCT = {"Z0": "#sigma_{long}^{SCT} = 0", "A580": "SCT 17 #mum / 580 #mum (ATLAS)", "Z1160": "SCT 34 #mum / 1.16 mm (Knapen)"}
SETS = ("Z0", "A580", "Z1160"); MU3 = {0: MU[0], 20: MU[20], 50: MU[50], 60: MU[60]}
def save(c, name, caption, inputs):
    d = f"{HERE}/{name}"; os.makedirs(d, exist_ok=True)
    st.SetPaperSize(c.GetWw() / 100.0, c.GetWh() / 100.0); c.Print(f"{d}/{name}.pdf", "pdf Portrait")
    for ext in ("root", "C"): c.SaveAs(f"{d}/{name}.{ext}")
    subprocess.run([PDFTOPPM, "-png", "-r", "250", "-cropbox", "-singlefile", f"{d}/{name}.pdf", f"{d}/{name}"], check=True)
    open(f"{d}/caption.md", "w").write(caption.strip() + "\n")
    json.dump(dict(figure=name, script="make_figures_07.py (ROOT %s)" % ROOT.gROOT.GetVersion(), data={i: sha(f"{D}/{i}") for i in inputs},
                   data_prepared_by="prepare_data_07.py", upstream_sources=json.load(open(f"{D}/sources.json"))), open(f"{d}/provenance.json", "w"), indent=1)
    KEEP.clear()
_gerr = gerr
def gerr(xs, ys, *a, **k):                                                 # empty series (point not yet computed): an empty graph, not a crash
    if not len(xs): g = ROOT.TGraphAsymmErrors(); KEEP.append(g); return g
    return _gerr(xs, ys, *a, **k)
def mk(n, xs, ys): g = ROOT.TGraph(n, array.array("d", xs), array.array("d", ys)); KEEP.append(g); return g
HDR = "Stage 2 #upoint Run 3 #upoint ATLAS: #sqrt{s} = 13.6 TeV, ATLAS inner detector (barrel + end-caps)"

# ---------- G01: cross section, trigger efficiency, charge fraction (07 10k vs Stage 2 2k)
X = read("xsec_and_trigger.csv")
def ser(ch, s, key):
    rows = sorted([r for r in X if r["channel"] == ch and r["sample"] == s], key=lambda r: fl(r["mass_gev"])); return [fl(r["mass_gev"]) for r in rows], rows
c = ROOT.TCanvas("G01", "", 1800, 650); c.Divide(3, 1, 0.002, 0.002); KEEP.append(c); LE = []
for j, (key, yt, lo, hi, logy) in enumerate((("sigma_fb", "#sigma(pp #rightarrow Q#bar{Q}) [fb]", 0.01, 1e6, True), ("eps_trig", "#varepsilon_{trig} (p_{T}(Q#bar{Q}) > 200 GeV)", 0, 0.35, False),
                                             ("f_ch", "f_{ch} (both quirk-hadrons charged)", 0, 1.1, False))):
    p = c.cd(j + 1); p.SetLeftMargin(0.21); p.SetRightMargin(0.03); h_ = frame(p, 0, lo, 2600, hi, "m_{Q} [GeV]", yt, logy=logy); h_.GetYaxis().SetTitleOffset(1.75); h_.GetXaxis().SetNdivisions(505)
    for ch, mk_ in (("colored", 20), ("EW", 21)):
        if key == "f_ch" and ch == "EW": continue
        for s, col, off in (("S2_Run3_ATLAS_10k", E136, 0), ("S1_Run3_Ideal_2k", MUTED, 25)):
            xs, rows = ser(ch, s, key); xs = [x + off for x in xs]; ys = [fl(r[key]) for r in rows]
            if key == "sigma_fb": el = eh = [fl(r["sigma_err_fb"]) for r in rows]
            else: el = [y - fl(r[f"{key}_lo"]) for y, r in zip(ys, rows)]; eh = [fl(r[f"{key}_hi"]) - y for y, r in zip(ys, rows)]
            g = gerr(xs, ys, el, eh, col, mk_ if s == "S2_Run3_ATLAS_10k" else mk_ + 4, size=1.2); g.Draw("P"); LE.append((g, f"{ch}, {'10k generated' if s == 'S2_Run3_ATLAS_10k' else '2k (S1#upointRun 3#upointIdeal)'}", "p")) if j == 0 else None
    if j == 0: legend(0.36, 0.68, 0.97, 0.93, LE, size=0.036)
    p.RedrawAxis()
save(c, "G01_cross_sections_trigger", """**G01.** Signal samples at √s = 13.6 TeV: matched cross section (left), trigger efficiency ε_trig = n(p_T(QQ̄) > 200 GeV)/n_matched (middle) and the
fraction f_ch of triggered colored events with both quirk-hadrons charged (right). Blue: Stage 2 · Run 3 · ATLAS large samples (10 000 generated events per mass point, five MG5 runs
of 2000 with new seeds); grey (shifted by +25 GeV): Stage 1 · Run 3 · Ideal (2000 generated, 06 S2). Errors: MC error of σ, Wilson 68% for the fractions. Same cards as Stage 1 · Run 3 · Ideal. EW 1200 GeV (added 2026-11-17 to close the EW reach) is generated but not yet propagated.
Source: signal/inputs_large/counts.csv, 06 S2 inputs/counts.csv via data/xsec_and_trigger.csv.""", ["xsec_and_trigger.csv"])

# ---------- G02: quirk velocity beta
BS = read("beta_summary.csv"); BH = read("beta_hist.csv")
c = ROOT.TCanvas("G02", "", 1700, 700); c.Divide(2, 1, 0.002, 0.002); KEEP.append(c)
p = c.cd(1); p.SetLeftMargin(0.14); frame(p, 0, 0, 2600, 1.05, "m_{Q} [GeV]", "#beta = |p| / E of the quirks"); LE = []
for ch, col, m_ in (("EW", E136, 21), ("colored", E13, 20)):
    rows = sorted([r for r in BS if r["channel"] == ch], key=lambda r: fl(r["mass_gev"])); xs = [fl(r["mass_gev"]) for r in rows]; ys = [fl(r["beta_median"]) for r in rows]
    g = gerr(xs, ys, [y - fl(r["beta_p16"]) for y, r in zip(ys, rows)], [fl(r["beta_p84"]) - y for y, r in zip(ys, rows)], col, m_); g.Draw("P"); LE.append((g, f"{ch}: median, 16#minus84%", "p"))
    gt = gerr(xs, [fl(r["betaT_median"]) for r in rows], [0] * len(xs), [0] * len(xs), col, m_ + 4); gt.Draw("P"); LE.append((gt, f"{ch}: median #beta_{{T}} = p_{{T}} / E", "p"))
legend(0.45, 0.15, 0.95, 0.40, LE, size=0.038); p.RedrawAxis()
p = c.cd(2); p.SetLeftMargin(0.14); frame(p, 0, 0, 1, 0.42, "#beta", "fraction of quirks / 0.02"); LE = []
for (ch, m), col, ls in ((("EW", 100), E136, 1), (("EW", 1000), E136, 2), (("colored", 600), E13, 1), (("colored", 2400), E13, 2)):
    rows = [r for r in BH if r["channel"] == ch and fl(r["mass_gev"]) == m]; xs, ys = [], []
    for r in rows: xs += [fl(r["lo"]), fl(r["hi"])]; ys += [fl(r["frac"])] * 2
    g = graph(xs, ys, col, 3, ls); g.Draw("L"); LE.append((g, f"{ch} {m} GeV", "l"))
legend(0.18, 0.66, 0.55, 0.92, LE, size=0.04); p.RedrawAxis()
save(c, "G02_quirk_velocity_beta", """**G02.** Velocity of the quirks in the propagated events (triggered; colored: both quirk-hadrons charged), Stage 2 · Run 3 · ATLAS large samples, 13.6 TeV, both quirks of every event.
Left: median of β = |p|/E with the 16–84% interval (filled markers) and median β_T = p_T/E (open markers) vs m_Q. Right: β distributions for the lightest and heaviest
point of each channel. Heavier quirks are slower; slow quirks reach the outer layers and the end-caps late (25 ns cut). Source: signal/inputs_large/<tag>_events.csv via
data/beta_summary.csv, data/beta_hist.csv.""", ["beta_summary.csv", "beta_hist.csv"])

# ---------- G03 / G04: efficiencies vs Lambda for four mass points
EF = read("efficiency_vs_lambda.csv"); PTS = (("EW", 400), ("EW", 1000), ("colored", 900), ("colored", 1800))
def eser(s, ch, m, sct, key):
    rows = sorted([r for r in EF if r["sample"] == s and r["channel"] == ch and fl(r["mass_gev"]) == m and r["sct"] == sct], key=lambda r: fl(r["lambda_keV"]))
    xs = [fl(r["lambda_keV"]) * 1e3 for r in rows]; ys = [fl(r[key]) for r in rows]
    return xs, ys, [y - fl(r[f"{key}_lo"]) for y, r in zip(ys, rows)], [fl(r[f"{key}_hi"]) - y for y, r in zip(ys, rows)]
def eff4(name, hdr, draw, legf, caption):
    c, hd, top, bot = layout(name); header(hd, hdr); LE = None
    for i, (ch, m) in enumerate(PTS):
        p = top.cd(i + 1); p.SetLeftMargin(0.13); p.SetRightMargin(0.05); p.SetTopMargin(0.08)
        frame(p, 70, 0, 35000, 1.05, "#Lambda [eV]", draw.__doc__, logx=True); o = draw(ch, m); LE = LE or o
        text(0.14, 0.94, f"#bf{{{CH[ch]}}}, m_{{Q}} = {m} GeV", 0.045); p.RedrawAxis()
    bot.cd(); legend(0.04, 0.05, 0.98, 0.95, legf(LE), ncol=3, size=0.2); save(c, name, caption, ["efficiency_vs_lambda.csv"])
def d3(ch, m):
    """#varepsilon_{fid} = n_{fid} / n"""
    o = {}
    for key, s, col, mk_, sh in (("eps_fid", "S2_Run3_ATLAS_10k", E136, 20, 1.0), ("eps_fid_barrel_rule", "S2_Run3_ATLAS_10k", E13, 25, 1.03), ("eps_fid", "S1_Run3_Ideal_2k", MUTED, 24, 0.97)):
        xs, ys, el, eh = eser(s, ch, m, "Z0", key); g = gerr([x * sh for x in xs], ys, el, eh, col, mk_, size=1.1); g.Draw("P"); o[(key, s)] = g
    return o
eff4("G03_fiducial_efficiency", "Stage 2 #upoint Run 3 #upoint ATLAS (13.6 TeV): fiducial efficiency, 10k samples", d3,
     lambda o: [(o[("eps_fid", "S2_Run3_ATLAS_10k")], "ATLAS geometry: 8 stations, |#eta| < 2.5 (D1)", "p"), (o[("eps_fid_barrel_rule", "S2_Run3_ATLAS_10k")], "same trajectories, ideal barrel rule", "p"),
                (o[("eps_fid", "S1_Run3_Ideal_2k")], "S1#upointRun 3#upointIdeal (2k)", "p")],
     """**G03.** Fiducial efficiency vs Λ for four mass points, 13.6 TeV. Blue: the Stage 2 · Run 3 · ATLAS rule (each quirk's true hits within 25 ns cover the 8 ATLAS-like stations of D1, barrel or
end-cap, and the line PV → station-8 hit has |η| < 2.5). Orange: the ideal-geometry barrel rule (all 8 barrel layers crossed inside their length, t < 25 ns) on the same 07
trajectories. Grey: Stage 1 · Run 3 · Ideal (2000 generated events). Wilson 68% errors; markers shifted by ±3% in Λ for visibility. Source: tables/R01_N_grid_300fb.csv, Stage 2
S2_N_grid_300fb.csv via data/efficiency_vs_lambda.csv.""")
def d4(ch, m):
    """k / n (selected / propagated)"""
    o = {}
    for sct, sh in (("Z0", 0.97), ("A580", 1.0), ("Z1160", 1.03)):
        xs, ys, el, eh = eser("S2_Run3_ATLAS_10k", ch, m, sct, "kn"); g = gerr([x * sh for x in xs], ys, el, eh, SZ[sct], 20, size=1.1); g.Draw("P"); o[sct] = g
    for sct, mk_ in (("Z0", 24), ("Z1160", 26)):
        xs, ys, el, eh = eser("S1_Run3_Ideal_2k", ch, m, sct, "kn"); g = gerr(xs, ys, el, eh, MUTED, mk_, size=1.1); g.Draw("P"); o["s2" + sct] = g
    return o
eff4("G04_selection_efficiency", "Stage 2 #upoint Run 3 #upoint ATLAS (13.6 TeV): selection efficiency k/n, 10k samples", d4,
     lambda o: [(o["Z0"], SCT["Z0"], "p"), (o["A580"], SCT["A580"], "p"), (o["Z1160"], SCT["Z1160"], "p"),
                (o["s2Z0"], "S1#upointRun 3#upointIdeal (2k): #sigma_{z} = 0", "p"), (o["s2Z1160"], "S1#upointRun 3#upointIdeal (2k): #sigma_{z} = 1.16 mm", "p")],
     """**G04.** Fraction k/n of propagated events that pass the full coplanarity selection (fiducial, plane, multiplicity, Δs < 0.01 cm, Δw < 1 cm) vs Λ, for the three SCT
settings of D4 (Stage 2 · Run 3 · ATLAS, 10k samples) and for Stage 1 · Run 3 · Ideal (grey, open; 2000 generated). Wilson 68% errors; ATLAS markers shifted by ±3% in Λ.
Source: data/efficiency_vs_lambda.csv.""")

# ---------- G05: reach contours, zero background, 332 fb^-1 (07, three settings) vs Stage 2
CON = read("contours.csv"); GP = read("grid_points.csv")
exec(_src[_src.index("def segs("):_src.index("def grid4(")])                 # segs, draw_contours, draw_points of 06, unchanged
c = ROOT.TCanvas("G05", "", 1800, 1200); hd = ROOT.TPad("hd", "", 0, 0.95, 1, 1); top = ROOT.TPad("top", "", 0, 0.09, 1, 0.95); bot = ROOT.TPad("bot", "", 0, 0, 1, 0.09)
for q in (hd, top, bot): q.Draw()
KEEP.extend([c, hd, top, bot]); top.Divide(3, 2, 0.002, 0.002); header(hd, "S2 #upoint Run 3 #upoint ATLAS vs S1 #upoint Run 3 #upoint Ideal (2k): #sqrt{s} = 13.6 TeV, 332 fb^{-1}, no pile-up, zero background"); LE = {}
for i, (ch, sct) in enumerate([(a, b) for a in ("colored", "EW") for b in SETS]):
    p = top.cd(i + 1); p.SetLeftMargin(0.14); p.SetRightMargin(0.07); p.SetTopMargin(0.08)
    frame(p, XR[ch][0], 100, XR[ch][1], 25000, "m_{Q} [GeV]", "#Lambda [eV]", logy=True).GetXaxis().SetNdivisions(505)
    if sct != "A580":
        s = draw_contours("S1_Run3_Ideal_2k_332fb", ch, sct, MUTED, 2, bands=False)
        if s.get("exclusion"): LE.setdefault("s2e", s["exclusion"])
        if s.get("discovery"): LE.setdefault("s2d", s["discovery"])
    n = draw_contours("S2_Run3_ATLAS_332fb", ch, sct, SZ[sct], 3); pts = draw_points("S2_Run3_ATLAS_332fb", ch, sct)
    for k_, v_ in n.items(): LE.setdefault(sct, {}).setdefault(k_, v_)
    if len(pts) > len(LE.get("pts", [])): LE["pts"] = pts
    text(0.15, 0.94, f"#bf{{{CH[ch]}}}, {SCT[sct]}", 0.042); p.RedrawAxis()
E = [(LE[s]["exclusion"], f"S2 #upoint Run 3 #upoint ATLAS {SCT[s]}: N = 3", "l") for s in SETS if LE.get(s, {}).get("exclusion")] + [(LE.get("Z0", {}).get("discovery"), "S2 #upoint Run 3 #upoint ATLAS: N = 5 (solid)", "l"), (LE.get("Z0", {}).get("band"), "S2 #upoint Run 3 #upoint ATLAS: N = 3, #pm 1#sigma (Wilson)", "l")]
E += [(LE.get("s2e"), "S1 #upoint Run 3 #upoint Ideal (2k): N = 3", "l"), (LE.get("s2d"), "S1 #upoint Run 3 #upoint Ideal (2k): N = 5", "l")] + [(g_, l_, "p") for g_, l_ in zip(LE.get("pts", []), ("grid point, k > 0", "grid point, k = 0"))]
bot.cd(); legend(0.03, 0.05, 0.99, 0.95, [e for e in E if e[0]], ncol=3, size=0.2)
save(c, "G05_reach_zero_background_332fb", """**G05.** Expected reach of the coplanarity search, Stage 2 · Run 3 · ATLAS (ATLAS inner detector: barrel and end-caps, 8 ATLAS-like stations), √s = 13.6 TeV,
332 fb⁻¹, no pile-up, zero background. Contours N = 3 (exclusion, dashed) and N = 5 (discovery, solid), N = L σ ε_trig f_ch k/n; dotted: N = 3 for the ±1σ Wilson band on
k/n. Columns: SCT σ_long = 0, the ATLAS intrinsic 17 µm / 580 µm (D4, A580), Knapen 34 µm / 1.16 mm. Grey: Stage 1 · Run 3 · Ideal (Knapen barrel geometry, 2000 generated events,
same method). Source: tables/R01_N_grid_300fb.csv (× 332/300), 06 S2_N_grid_300fb.csv via data/contours.csv, data/grid_points.csv.""", ["contours.csv", "grid_points.csv"])

# ---------- G06: reach with the converted-photon background vs pile-up (A580 and Z0)
TH = {r["sct"] + r["mu"]: r for r in read("background_thresholds.csv")}
for name, sct, mus in (("G06_reach_pileup_A580", "A580", (0, 20, 50)), ("G07_reach_pileup_Z0", "Z0", (0, 20, 50, 60))):
    c, hd, top, bot = layout(name); header(hd, f"S2 #upoint Run 3 #upoint ATLAS, 332 fb^{{-1}}, #gamma-conversion background vs #mu: {SCT[sct]}"); LE = []
    for i, (cn, ch) in enumerate([(a, b) for a in ("exclusion", "discovery") for b in ("colored", "EW")]):
        p = top.cd(i + 1); p.SetLeftMargin(0.13); p.SetRightMargin(0.05); p.SetTopMargin(0.08)
        frame(p, XR[ch][0], 100, XR[ch][1], 25000, "m_{Q} [GeV]", "#Lambda [eV]", logy=True)
        ref = [graph(xs, ys, MUTED, 2, 2 if cn == "exclusion" else 1) for xs, ys in segs("S2_Run3_ATLAS_332fb", ch, sct, cn)]
        for g in ref: g.Draw("L")
        gs = {}
        for mu in mus:
            for xs, ys in segs(f"S2_Run3_ATLAS_332fb_mu{mu}", ch, sct, cn):
                g = graph(xs, ys, MU3[mu], 3, 2 if cn == "exclusion" else 1); g.Draw("L"); gs.setdefault(mu, g)
        if not LE: LE = [(gs[mu], f"#mu = {mu}" + (" (no pile-up)" if mu == 0 else ""), "l") for mu in mus if mu in gs] + ([(ref[0], "zero background (G05)", "l")] if ref else [])
        s = "s_excl_332fb" if cn == "exclusion" else "s_disc_332fb"
        text(0.14, 0.94, f"#bf{{{CH[ch]}}}, {'exclusion (95% CL_{s})' if cn == 'exclusion' else 'discovery'}", 0.045)
        text(0.93, 0.20, "s_{req}: " + " / ".join(f"{fl(TH[sct + str(m)][s]):.1f}" for m in mus) + "  (#mu = " + "/".join(str(m) for m in mus) + ")", 0.034, 31, INK2)
        p.RedrawAxis()
    bot.cd(); legend(0.04, 0.05, 0.98, 0.95, LE, ncol=3, size=0.2)
    save(c, name, f"""**{name[:3]}.** Reach with the converted-photon background (C01: Z(νν̄)γ+j photons, conversion probability from the ATLAS material M01, full simulation
through the Stage 2 · Run 3 · ATLAS geometry with pile-up), {SCT[sct].replace('#mu', 'µ').replace('#sigma_{long}^{SCT}', 'σ_long')}, √s = 13.6 TeV, 332 fb⁻¹. Blue ramp: μ = {", ".join(str(m) for m in mus)} (light to dark); the contour is the
signal count s_req for 95% CL_s exclusion (top, dashed; n_obs = round(b_used)) or discovery (bottom, solid; max(5, Asimov Z = 5)), printed in each panel.
b_used = central background if any photon passed, else the 95% upper limit (largest per-region limit). Grey: zero background. Signal efficiencies without pile-up.
Settings with the same s_req give identical contours, drawn on top of each other (the last drawn, darker one is visible); s_req is not monotonic in μ because
μ = 0 with no passing photon uses the upper limit b = 1.29 events (n_obs = 1), while small central values (b < 0.5) round to n_obs = 0.
Source: tables/R01_N_grid_300fb.csv, tables/R01_background.csv via data/contours.csv, data/background_thresholds.csv.""", ["contours.csv", "background_thresholds.csv"])

# ---------- G08: background vs pile-up
BV = read("background_vs_mu.csv")
c = ROOT.TCanvas("G08", "", 1500, 900); c.SetLeftMargin(0.12); c.SetRightMargin(0.03); c.SetBottomMargin(0.13); KEEP.append(c)
frame(c, -3, 0.01, 63, 1e5, "pile-up #mu", "N_{bkg} (332 fb^{-1})", logy=True); LE = []
def bser(sample, sct, part, col, mk_, sh, lab):
    rows = sorted([r for r in BV if r["sample"] == sample and r["sct"] == sct and r["part"] == part and fl(r["N_332fb"]) > 0], key=lambda r: fl(r["mu"]))
    if not rows: return
    xs = [fl(r["mu"]) + sh for r in rows]; ys = [fl(r["N_332fb"]) for r in rows]; e = [fl(r["N_stat"]) if math.isfinite(fl(r["N_stat"])) else 0 for r in rows]
    e = [min(a, y * 0.999) for a, y in zip(e, ys)]
    g = gerr(xs, ys, e, e, col, mk_); g.Draw("P"); LE.append((g, lab, "p"))
bser("S2_Run3_ATLAS", "Z0", "all", SZ["Z0"], 20, 0, "S2#upointRun 3#upointATLAS, #sigma_{long} = 0: all"); bser("S2_Run3_ATLAS", "Z0", "barrel-like", SZ["Z0"], 24, 0.6, "S2#upointRun 3#upointATLAS, #sigma_{long} = 0: barrel-like planes")
bser("S2_Run3_ATLAS", "Z0", "with end-cap", SZ["Z0"], 26, -0.6, "S2#upointRun 3#upointATLAS, #sigma_{long} = 0: planes with an end-cap element"); bser("S2_Run3_ATLAS", "A580", "all", SZ["A580"], 21, 1.2, "S2#upointRun 3#upointATLAS, A580 (17 / 580 #mum): all")
bser("S2_Run3_ATLAS", "A580", "UL95 if 0 passed", SZ["A580"], 23, 1.2, "S2#upointRun 3#upointATLAS, A580: 95% UL, 0 passed"); bser("S2_Run3_ATLAS", "Z1160", "UL95 if 0 passed", SZ["Z1160"], 23, -1.2, "S2#upointRun 3#upointATLAS, Z1160: 95% UL, 0 passed (every #mu)")
bser("S1_Run3_Ideal_2k", "Z0", "all", MUTED, 25, 0.3, "S1#upointRun 3#upointIdeal (2k), #sigma_{z} = 0 (flat 1% conversion)")
legend(0.15, 0.62, 0.72, 0.93, LE, size=0.03); c.RedrawAxis()
save(c, "G08_background_vs_pileup", """**G08.** Expected converted-photon background in the signal region at 332 fb⁻¹ vs pile-up μ, 13.6 TeV (C01, Z(νν̄)γ+j, 9130 photons after MET > 200 GeV,
conversion probability from the ATLAS material M01). Violet: SCT σ_long = 0, split into planes on barrel layers only and planes with at least one end-cap element. Blue:
the ATLAS intrinsic SCT resolution (A580, D4; μ = 0, 20, 50). Triangles: 95% upper limit where no photon passed (largest per-region limit); Z1160 has no passing photon at any μ.
Grey: Stage 1 · Run 3 · Ideal (barrel, flat 1% conversion). Errors: MC statistics. Source: tables/S02_conversion_breakdown.csv, tables/R01_background.csv, Stage 2
S2_background_13p6TeV.csv via data/background_vs_mu.csv.""", ["background_vs_mu.csv"])

# ---------- G09: maximum reach summary
RS = read("reach_summary.csv")
c = ROOT.TCanvas("G09", "", 1800, 1700); c.Divide(1, 2, 0.002, 0.002); KEEP.append(c)
ROWS = [("S1_Run3_Ideal_2k_332fb", "Z1160", "zero background", "S1 #upoint Run 3 #upoint Ideal (2k), #sigma_{z} = 1.16 mm"), ("S1_Run3_Ideal_2k_332fb", "Z0", "zero background", "S1 #upoint Run 3 #upoint Ideal (2k), #sigma_{z} = 0"),
        ("S2_Run3_ATLAS_332fb", "Z1160", "zero background", "S2 #upoint Run 3 #upoint ATLAS, Knapen 34 #mum / 1.16 mm"), ("S2_Run3_ATLAS_332fb", "A580", "zero background", "S2 #upoint Run 3 #upoint ATLAS, ATLAS 17 #mum / 580 #mum"),
        ("S2_Run3_ATLAS_332fb", "Z0", "zero background", "S2 #upoint Run 3 #upoint ATLAS, #sigma_{long} = 0"), ("S2_Run3_ATLAS_332fb_mu50", "A580", "b_used = UL if 0 passed", "S2 #upoint Run 3 #upoint ATLAS, A580, #mu = 50"),
        ("S2_Run3_ATLAS_332fb_mu50", "Z0", "b_used = UL if 0 passed", "S2 #upoint Run 3 #upoint ATLAS, #sigma_{long} = 0, #mu = 50"), ("S1_Run3_Ideal_2k_332fb_mu50", "Z0", "b_used = UL if 0 passed", "S1 #upoint Run 3 #upoint Ideal (2k), #sigma_{z} = 0, #mu = 50")]
for j, ch in enumerate(("colored", "EW")):
    p = c.cd(j + 1); p.SetLeftMargin(0.36); p.SetRightMargin(0.04); p.SetTopMargin(0.09); p.SetBottomMargin(0.13); n = len(ROWS)
    h = frame(p, XR[ch][0] if ch == "EW" else 900, 0, 1050 if ch == "EW" else 2400, n, "maximum reach m_{Q} [GeV] (332 fb^{-1})", ""); h.GetYaxis().SetLabelSize(0); h.GetYaxis().SetNdivisions(0); h.GetXaxis().SetNdivisions(505); h.GetXaxis().SetTitleSize(0.042); h.GetXaxis().SetLabelSize(0.04)
    for i, (sc, sct, var, lab) in enumerate(ROWS):
        y = n - i - 0.5; text(0.35, 0, lab, 0.034, 32, INK); KEEP[-1].SetNDC(False); KEEP[-1].SetX(h.GetXaxis().GetXmin() - 0.02 * (h.GetXaxis().GetXmax() - h.GetXaxis().GetXmin())); KEEP[-1].SetY(y)
        for cn, mk_, dy in (("exclusion", 20, 0.15), ("discovery", 24, -0.15)):
            r = [x for x in RS if x["scenario"] == sc and x["channel"] == ch and x["sct"] == sct and x["contour"] == cn and x["variant"] == var]
            if not r or not math.isfinite(fl(r[0]["m_max"])): continue
            m, lo, hi = fl(r[0]["m_max"]), fl(r[0]["lo"]), fl(r[0]["hi"]); col = MUTED if sc.startswith("S1_") else SZ[sct]
            g = gerr([m], [y + dy], [0], [0], col, mk_, [m - lo] if math.isfinite(lo) else [0], [hi - m] if math.isfinite(hi) else [0]); g.Draw("P")
    text(0.37, 0.945, f"#bf{{{CH[ch]}}}", 0.05); text(0.96, 0.945, "#bullet excl.   #circ disc.", 0.036, 31, INK2); p.RedrawAxis()
save(c, "G09_reach_summary", """**G09.** Maximum mass reach at 332 fb⁻¹, 13.6 TeV (filled: exclusion, N = 3 or 95% CL_s with background; open: discovery). Horizontal bars: reach of the ±1σ Wilson
band on k/n. Stage 2 · Run 3 · ATLAS (10k samples) for the three SCT settings, zero background and with the μ = 50 converted-photon background; grey: Stage 1 · Run 3 · Ideal (2k).
Source: tables/R01_reach.csv, tables/R01_reach_with_background.csv, 06 S2_reach*.csv via data/reach_summary.csv.""", ["reach_summary.csv"])

# ---------- G10: conversion probability from the material
MC = read("material_conversion_vs_eta.csv")
c = ROOT.TCanvas("G10", "", 1500, 900); c.SetLeftMargin(0.12); c.SetRightMargin(0.03); c.SetBottomMargin(0.13); KEEP.append(c)
frame(c, 0, 0.00003, 2.5, 1, "|#eta| of the photon", "conversion probability (mean per photon)", logy=True); LE = []
for key, col, lab in (("P_before_IBL", C("#86b6ef"), "before the IBL (beam pipe)"), ("P_IBL", C("#3987e5"), "IBL"), ("P_pixel", C("#1c5cab"), "pixel layers + disks"),
                      ("P_SCT", C("#0d366b"), "SCT"), ("P_total", INK, "total (inner detector)")):
    rows = [r for r in MC if r["variant"] == "nominal"]; xs, ys = [], []
    for r in rows: xs += [fl(r["eta_lo"]), fl(r["eta_hi"])]; ys += [fl(r[key])] * 2
    g = graph(xs, ys, col, 3); g.Draw("L"); LE.append((g, lab, "l"))
for v, key, col, ls, lab in (("BP_run1_0p45", "P_before_IBL", C("#86b6ef"), 2, "before the IBL, Run 1 pipe 0.45% X_{0}"), ("BP_x2", "P_before_IBL", C("#86b6ef"), 3, "before the IBL, Be wall #times 2"),
                             ("IBL_1p5", "P_IBL", C("#3987e5"), 2, "IBL, 1.5% X_{0} (R6)")):
    rows = [r for r in MC if r["variant"] == v]; xs, ys = [], []
    for r in rows: xs += [fl(r["eta_lo"]), fl(r["eta_hi"])]; ys += [fl(r[key])] * 2
    g = graph(xs, ys, col, 2, ls); g.Draw("L"); LE.append((g, lab, "l"))
legend(0.15, 0.15, 0.97, 0.36, LE, ncol=2, size=0.032); c.RedrawAxis()
save(c, "G10_material_conversion_probability", """**G10.** Photon conversion probability from the ATLAS Run 2 inner-detector material (M01, decision D2; x/X0 of each component from the references in
geometry/atlas_run2_id_material.csv), straight photon path from (0, 0, z0), every surface thin with t = (x/X0)/|cos α|, P_i = Π_{j<i} exp(−7t_j/9) · (1 − exp(−7t_i/9))
(R7 Eq. 34.32); mean per photon of the Z(νν̄)γ+j sample (9130 photons after MET > 200 GeV) in bins of |η|, split by the region where the conversion happens. Nominal:
beam-pipe Be wall 0.227% (derived), IBL 1.88% (R2). Dashed / dotted: variants (beam pipe 0.45%, Run 1 value of R3; beam pipe ×2; IBL 1.5%, R6). Stage 1 · Run 3 · Ideal used a flat 1%. Source: tables/M01_conversion_per_photon.csv via data/material_conversion_vs_eta.csv.""", ["material_conversion_vs_eta.csv"])
print("make_figures_07: done")
