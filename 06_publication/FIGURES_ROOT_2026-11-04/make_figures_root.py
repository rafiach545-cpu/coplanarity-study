#!/usr/bin/env python3
"""Paper figures (ROOT), step 2 of 2: every figure drawn with ROOT from the plot-ready CSVs in data/ (prepare_data.py). No numbers are computed here
beyond unit changes, ratios of two CSV columns and their error propagation.
Run with /home/rafia/miniconda3/envs/root-env/bin/python (ROOT 6.40). Output per figure: Fxx_<name>/Fxx_<name>.{pdf,png,root,C}, caption.md, provenance.json."""
import os, csv, json, hashlib, math, array, subprocess
import ROOT
ROOT.gROOT.SetBatch(True)
HERE = os.path.dirname(os.path.abspath(__file__)); D = f"{HERE}/data"; PDFTOPPM = "/home/rafia/miniconda3/envs/latex/bin/pdftoppm"

# ---------- style (paper: white, no titles or stat boxes, ticks on all sides, Helvetica)
st = ROOT.gStyle
for k, v in dict(OptStat=0, OptTitle=0, CanvasColor=0, PadColor=0, FrameFillColor=0, CanvasBorderMode=0, PadBorderMode=0, FrameBorderMode=0, PadTickX=1, PadTickY=1,
                 LegendBorderSize=0, LegendFillColor=0, EndErrorSize=0, LineScalePS=1.6).items():
    getattr(st, f"Set{k}")(v)
st.SetTextFont(42); st.SetLabelFont(42, "xyz"); st.SetTitleFont(42, "xyz"); st.SetLegendFont(42)
st.SetLabelSize(0.045, "xyz"); st.SetTitleSize(0.052, "xyz"); st.SetTitleOffset(1.05, "x"); st.SetTitleOffset(1.15, "y")
st.SetPadLeftMargin(0.14); st.SetPadRightMargin(0.04); st.SetPadTopMargin(0.07); st.SetPadBottomMargin(0.14)
C = lambda h: ROOT.TColor.GetColor(h)
INK, INK2, MUTED, GRID = C("#0b0b0b"), C("#52514e"), C("#898781"), C("#d9d8d4")
E13, E136 = C("#eb6834"), C("#2a78d6")                                   # identity: 13 TeV orange, 13.6 TeV blue (categorical slots 2, 1)
MU = {0: C("#86b6ef"), 20: C("#3987e5"), 50: C("#1c5cab"), 60: C("#0d366b")}  # magnitude: one blue ramp, light -> dark
SZ = {"Z1160": C("#1baf7a"), "Z0": C("#6250d6")}                          # identity: SCT setting (categorical slots 3, 7)
KEEP = []

def read(name):
    with open(f"{D}/{name}") as f: return list(csv.DictReader(f))
def fl(x):
    try: return float(x)
    except (TypeError, ValueError): return float("nan")
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def save(c, name, caption, inputs):
    d = f"{HERE}/{name}"; os.makedirs(d, exist_ok=True)
    st.SetPaperSize(c.GetWw() / 100.0, c.GetWh() / 100.0)                     # PDF CropBox = canvas aspect (width <= 21 cm, else TPDF rotates)
    c.Print(f"{d}/{name}.pdf", "pdf Portrait")
    for ext in ("root", "C"): c.SaveAs(f"{d}/{name}.{ext}")
    subprocess.run([PDFTOPPM, "-png", "-r", "250", "-cropbox", "-singlefile", f"{d}/{name}.pdf", f"{d}/{name}"], check=True)   # PNG from the PDF (ROOT's PNG drops dashes)
    open(f"{d}/caption.md", "w").write(caption.strip() + "\n")
    src = json.load(open(f"{D}/sources.json"))
    json.dump(dict(figure=name, script="make_figures_root.py (ROOT %s)" % ROOT.gROOT.GetVersion(), data={i: sha(f"{D}/{i}") for i in inputs},
                   data_prepared_by="prepare_data.py", upstream_sources=src), open(f"{d}/provenance.json", "w"), indent=1)
    KEEP.clear()
def text(x, y, s, size=0.045, align=11, color=INK, ndc=True):
    t = ROOT.TLatex(x, y, s); t.SetNDC(ndc); t.SetTextSize(size); t.SetTextAlign(align); t.SetTextColor(color); t.SetTextFont(42); t.Draw(); KEEP.append(t); return t
def graph(xs, ys, color, width=3, style=1):
    g = ROOT.TGraph(len(xs), array.array("d", xs), array.array("d", ys)); g.SetLineColor(color); g.SetLineWidth(width); g.SetLineStyle(style); KEEP.append(g); return g
def gerr(xs, ys, elo, ehi, color, marker, exl=None, exh=None, size=1.3):
    n = len(xs); z = [0.0] * n
    g = ROOT.TGraphAsymmErrors(n, array.array("d", xs), array.array("d", ys), array.array("d", exl or z), array.array("d", exh or z), array.array("d", elo), array.array("d", ehi))
    g.SetMarkerColor(color); g.SetLineColor(color); g.SetMarkerStyle(marker); g.SetMarkerSize(size); g.SetLineWidth(2); KEEP.append(g); return g
def legend(x1, y1, x2, y2, entries, ncol=1, size=0.04):
    l = ROOT.TLegend(x1, y1, x2, y2); l.SetNColumns(ncol); l.SetTextSize(size); l.SetFillStyle(0)
    for obj, lab, opt in entries: l.AddEntry(obj, lab, opt)
    l.Draw(); KEEP.append(l); return l
def frame(pad, x1, y1, x2, y2, xt, yt, logy=False, logx=False):
    pad.cd(); pad.SetLogy(logy); pad.SetLogx(logx); h = pad.DrawFrame(x1, y1, x2, y2); h.GetXaxis().SetTitle(xt); h.GetYaxis().SetTitle(yt)
    for a in (h.GetXaxis(), h.GetYaxis()): a.SetAxisColor(INK2); a.SetLabelColor(INK2); a.SetTitleColor(INK)
    KEEP.append(h); return h
def layout(name, w=1600, h=1450):
    """canvas with a header strip, a 2 x 2 block of panels and a legend strip"""
    c = ROOT.TCanvas(name, name, w, h); hd = ROOT.TPad("hd", "", 0, 0.95, 1, 1); top = ROOT.TPad("top", "", 0, 0.1, 1, 0.95); bot = ROOT.TPad("bot", "", 0, 0, 1, 0.1)
    for q in (hd, top, bot): q.Draw()
    KEEP.extend([c, hd, top, bot]); top.Divide(2, 2, 0.002, 0.002); return c, hd, top, bot
def header(hd, s): hd.cd(); text(0.5, 0.45, s, 0.55, 22)

CH = {"colored": "colored (3,1)_{2/3}", "EW": "EW (1,1)_{1}"}; SCT = {"Z1160": "#sigma_{z}^{SCT} = 1.16 mm (Knapen)", "Z0": "#sigma_{z}^{SCT} = 0"}
XR = {"colored": (600, 2400), "EW": (100, 1000)}

# ---------- contour figures
CON = read("contours.csv"); GP = read("grid_points.csv")
def segs(scen, ch, sct, cn, band="central"):
    out = {}
    for r in CON:
        if r["scenario"] == scen and r["channel"] == ch and r["sct"] == sct and r["contour"] == cn and r["band"] == band:
            out.setdefault(r["segment"], ([], []))[0].append(float(r["mass_gev"])); out[r["segment"]][1].append(float(r["lambda_eV"]))
    return list(out.values())
def draw_contours(scen, ch, sct, color, width=3, bands=True, cns=("exclusion", "discovery")):
    first = {}
    for cn in cns:
        for xs, ys in segs(scen, ch, sct, cn):
            g = graph(xs, ys, color, width, 2 if cn == "exclusion" else 1); g.Draw("L"); first.setdefault(cn, g)
        if bands and cn == "exclusion":
            for b in ("lo", "hi"):
                for xs, ys in segs(scen, ch, sct, cn, b):
                    g = graph(xs, ys, color, 1, 3); g.Draw("L"); first.setdefault("band", g)
    return first
def draw_points(scen, ch, sct):
    xp = [(float(r["mass_gev"]), float(r["lambda_eV"])) for r in GP if r["scenario"] == scen and r["channel"] == ch and r["sct"] == sct and int(r["k"]) > 0]
    x0 = [(float(r["mass_gev"]), float(r["lambda_eV"])) for r in GP if r["scenario"] == scen and r["channel"] == ch and r["sct"] == sct and int(r["k"]) == 0]
    out = []
    for pts, mk, col, sz in ((xp, 20, INK2, 0.55), (x0, 5, MUTED, 0.9)):
        if pts:
            g = ROOT.TGraph(len(pts), array.array("d", [p[0] for p in pts]), array.array("d", [p[1] for p in pts])); g.SetMarkerStyle(mk); g.SetMarkerColor(col); g.SetMarkerSize(sz); g.Draw("P"); KEEP.append(g); out.append(g)
    return out
def grid4(name, header_text, panels, legend_entries, caption, inputs):
    c, hd, top, bot = layout(name); header(hd, header_text); leg_objs = None
    for i, (ch, sct) in enumerate([(a, b) for a in ("colored", "EW") for b in ("Z1160", "Z0")]):
        p = top.cd(i + 1); p.SetLeftMargin(0.13); p.SetRightMargin(0.05); p.SetTopMargin(0.08)
        frame(p, XR[ch][0], 100, XR[ch][1], 25000, "m_{Q} [GeV]", "#Lambda [eV]", logy=True)
        objs = panels(ch, sct); leg_objs = leg_objs or objs
        text(0.14, 0.94, f"#bf{{{CH[ch]}}}, {SCT[sct]}", 0.045)
        p.RedrawAxis()
    bot.cd(); legend(0.04, 0.05, 0.98, 0.95, legend_entries(leg_objs), ncol=3, size=0.2)
    save(c, name, caption, inputs)

grid4("F03_reach_13TeV_139fb", "#sqrt{s} = 13 TeV, 139 fb^{-1}, Knapen geometry, no pile-up, zero background",
      lambda ch, sct: dict(**draw_contours("13TeV_139fb", ch, sct, E13), pts=draw_points("13TeV_139fb", ch, sct)),
      lambda o: [(o["exclusion"], "N = 3 (exclusion)", "l"), (o["discovery"], "N = 5 (discovery)", "l"), (o["band"], "N = 3, #pm 1#sigma (Wilson 68% on k/n)", "l"), (o["pts"][0], "grid point, k > 0", "p")] + ([(o["pts"][1], "grid point, k = 0", "p")] if len(o["pts"]) > 1 else []),
      """**Fig. 3.** Expected reach of the coplanarity search at √s = 13 TeV and 139 fb⁻¹ (stage 1: Knapen geometry, no pile-up on the signal, zero background).
Contours of N = 3 (exclusion, dashed) and N = 5 (discovery, solid) expected signal events in the (m_Q, Λ) plane, with N = L σ ε_trig f_ch k/n. Dotted lines: N = 3 for the
±1σ Wilson band on k/n. Rows: colored (3,1)_{2/3} and EW (1,1)_1 quirks; columns: SCT z resolution 1.16 mm (Knapen) and 0. Grid points with no passing event (×) are left out of
the interpolation. Source: S1_N_grid_139fb.csv via data/contours.csv, data/grid_points.csv.""", ["contours.csv", "grid_points.csv"])

def f4(ch, sct):
    o = draw_contours("13TeV_139fb", ch, sct, E13, 2, bands=False); n = draw_contours("13p6TeV_332fb", ch, sct, E136, 3); pts = draw_points("13p6TeV_332fb", ch, sct)
    return dict(e13=o["exclusion"], d13=o["discovery"], e136=n["exclusion"], d136=n["discovery"], band=n["band"], pts=pts)
grid4("F04_reach_13p6TeV_332fb", "#sqrt{s} = 13.6 TeV, 332 fb^{-1}  vs  #sqrt{s} = 13 TeV, 139 fb^{-1}  (Knapen geometry, no pile-up, zero background)", f4,
      lambda o: [(o["e136"], "13.6 TeV, 332 fb^{-1}: N = 3", "l"), (o["d136"], "13.6 TeV, 332 fb^{-1}: N = 5", "l"), (o["band"], "13.6 TeV: N = 3, #pm 1#sigma", "l"), (o["pts"][0], "13.6 TeV grid point, k > 0", "p"),
                 (o["e13"], "13 TeV, 139 fb^{-1}: N = 3", "l"), (o["d13"], "13 TeV, 139 fb^{-1}: N = 5", "l")],
      """**Fig. 4.** Expected reach at √s = 13.6 TeV with the ATLAS Run 3 recorded luminosity, 332 fb⁻¹ (blue), compared with 13 TeV at 139 fb⁻¹ (Run 2, orange). Knapen
geometry, no pile-up, zero background; N = 3 dashed, N = 5 solid, ±1σ (Wilson) of the 13.6 TeV N = 3 contour dotted. Same selection, propagation and seeds at both energies;
only the beam energy differs. Source: S1_N_grid_139fb.csv, S2_N_grid_300fb.csv (× 332/300) via data/contours.csv.""", ["contours.csv", "grid_points.csv"])

# F05: pile-up, sigma_z = 0 (the sigma_z = 1.16 mm reach does not change with mu)
c, hd, top, bot = layout("F05"); header(hd, "#sqrt{s} = 13.6 TeV, 332 fb^{-1}: converted-photon background with pile-up")
TH = {r["sct"] + r["mu"]: r for r in read("background_13p6TeV_thresholds.csv")}; LE = []
for i, (cn, ch) in enumerate([(a, b) for a in ("exclusion", "discovery") for b in ("colored", "EW")]):
    p = top.cd(i + 1); p.SetLeftMargin(0.13); p.SetRightMargin(0.05); p.SetTopMargin(0.08)
    frame(p, XR[ch][0], 100, XR[ch][1], 25000, "m_{Q} [GeV]", "#Lambda [eV]", logy=True)
    ref = [graph(xs, ys, SZ["Z1160"], 2, 2 if cn == "exclusion" else 1) for xs, ys in segs("13p6TeV_332fb_mu0", ch, "Z1160", cn)]
    for g in ref: g.Draw("L")
    gs = {}
    for mu in (0, 20, 50, 60):
        for xs, ys in segs(f"13p6TeV_332fb_mu{mu}", ch, "Z0", cn):
            g = graph(xs, ys, MU[mu], 3, 2 if cn == "exclusion" else 1); g.Draw("L"); gs.setdefault(mu, g)
    if i == 0: LE = [(gs[mu], f"#sigma_{{z}} = 0, #mu = {mu}" + (" (no pile-up)" if mu == 0 else ""), "l") for mu in (0, 20, 50, 60)] + [(ref[0], "#sigma_{z} = 1.16 mm, every #mu (0#minus60)", "l")]
    s = "s_excl_332fb" if cn == "exclusion" else "s_disc_332fb"
    text(0.14, 0.94, f"#bf{{{CH[ch]}}}, {'exclusion (95% CL_{s})' if cn == 'exclusion' else 'discovery'}", 0.045)
    text(0.93, 0.20, "s_{req}(#sigma_{z}=0): " + " / ".join(f"{fl(TH['Z0' + m][s]):.1f}" for m in ('0', '20', '50', '60')) + "  (#mu = 0/20/50/60)", 0.034, 31, INK2)
    p.RedrawAxis()
bot.cd(); legend(0.04, 0.05, 0.98, 0.95, LE, ncol=3, size=0.2)
save(c, "F05_reach_13p6TeV_pileup", """**Fig. 5.** Effect of pile-up on the 13.6 TeV reach at 332 fb⁻¹. Blue ramp: SCT σ_z = 0 with the converted-photon background at μ = 0, 20, 50, 60
(light to dark); the contour is the signal count s_req needed for 95% CL_s exclusion (top, dashed; n_obs = round(b)) or for discovery (bottom, solid; max(5, Asimov Z = 5)),
printed in each panel. Green: σ_z = 1.16 mm (Knapen), whose background is < 0.27 events at every μ, so its contour is the same for μ = 0–60. Signal efficiencies without pile-up.
Source: S2_N_grid_300fb.csv, S2_background_13p6TeV.csv via data/contours.csv, data/background_13p6TeV_thresholds.csv.""", ["contours.csv", "background_13p6TeV_thresholds.csv"])

# ---------- F01: cross sections and ratio
X = read("xsec_and_trigger.csv")
def series(ch, E, key, err=None):
    rows = sorted([r for r in X if r["channel"] == ch and r["sqrt_s_TeV"] == E], key=lambda r: fl(r["mass_gev"]))
    return [fl(r["mass_gev"]) for r in rows], [fl(r[key]) for r in rows], rows
c = ROOT.TCanvas("F01", "", 1600, 900); KEEP.append(c)
for j, ch in enumerate(("colored", "EW")):
    c.cd(); up = ROOT.TPad(f"u{j}", "", j * 0.5, 0.32, (j + 1) * 0.5, 1); dn = ROOT.TPad(f"d{j}", "", j * 0.5, 0, (j + 1) * 0.5, 0.32); up.Draw(); dn.Draw(); KEEP.extend([up, dn])
    up.SetBottomMargin(0.02); up.SetTopMargin(0.06); dn.SetTopMargin(0.03); dn.SetBottomMargin(0.33)
    for q in (up, dn): q.SetLeftMargin(0.15); q.SetRightMargin(0.04)
    m, s13, r13 = series(ch, "13", "sigma_fb"); _, s136, r136 = series(ch, "13.6", "sigma_fb")
    e13 = [fl(r["sigma_err_fb"]) for r in r13]; e136 = [fl(r["sigma_err_fb"]) for r in r136]
    h = frame(up, XR[ch][0] - 60, min(s13) / 3, XR[ch][1] + 60, max(s136) * 4, "", "#sigma [fb]", logy=True); h.GetXaxis().SetLabelSize(0)
    g13 = gerr(m, s13, e13, e13, E13, 21); g136 = gerr(m, s136, e136, e136, E136, 20); g13.Draw("PL"); g136.Draw("PL")
    text(0.17, 0.85, f"#bf{{{CH[ch]}}}", 0.055); text(0.17, 0.78, "MG5 3.7.3 + Pythia8, MLM, nn23lo1", 0.042, 11, INK2)
    if j == 0: legend(0.55, 0.74, 0.94, 0.9, [(g136, "#sqrt{s} = 13.6 TeV", "pl"), (g13, "#sqrt{s} = 13 TeV", "pl")], size=0.05)
    ratio = [b / a for a, b in zip(s13, s136)]; er = [q * math.hypot(ea / a, eb / b) for q, a, b, ea, eb in zip(ratio, s13, s136, e13, e136)]
    h2 = frame(dn, XR[ch][0] - 60, 0.9, XR[ch][1] + 60, 1.7, "m_{Q} [GeV]", "13.6 / 13 TeV")
    for a in (h2.GetXaxis(), h2.GetYaxis()): a.SetLabelSize(0.1); a.SetTitleSize(0.11)
    h2.GetYaxis().SetTitleOffset(0.62); h2.GetYaxis().SetNdivisions(505); h2.GetXaxis().SetTitleOffset(1.1)
    one = ROOT.TLine(XR[ch][0] - 60, 1, XR[ch][1] + 60, 1); one.SetLineColor(MUTED); one.SetLineStyle(2); one.Draw(); KEEP.append(one)
    gr = gerr(m, ratio, er, er, INK, 20, size=1.1); gr.Draw("PL")
save(c, "F01_cross_sections", """**Fig. 1.** Matched cross sections of quirk-pair production (0 + 1 jet, MLM merging) at √s = 13 TeV (orange) and 13.6 TeV (blue) for the colored
(3,1)_{2/3} (left) and EW (1,1)_1 (right) benchmarks; lower panels: ratio 13.6/13 TeV. Error bars: MadGraph integration error. Same process directories, cards and
seeds; only the beam energy differs. Source: fig6/inputs/counts.csv and S2 inputs/counts.csv via data/xsec_and_trigger.csv.""", ["xsec_and_trigger.csv"])

# ---------- F02: trigger efficiency and charged fraction
c = ROOT.TCanvas("F02", "", 1800, 650); c.Divide(3, 1, 0.002, 0.002)
for j, (ch, key, yt, yr) in enumerate((("colored", "eps_trig", "#varepsilon_{trig}", (0, 0.45)), ("EW", "eps_trig", "#varepsilon_{trig}", (0, 0.3)), ("colored", "f_ch", "f_{ch}", (0, 0.6)))):
    p = c.cd(j + 1); p.SetLeftMargin(0.19); p.SetRightMargin(0.06); h = frame(p, XR[ch][0] - 100, yr[0], XR[ch][1] + 100, yr[1], "m_{Q} [GeV]", yt); h.GetXaxis().SetNdivisions(505); h.GetYaxis().SetTitleOffset(1.6); gs = []
    for E, col, mk, dx in (("13", E13, 21, -12), ("13.6", E136, 20, 12)):
        m, v, rows = series(ch, E, key); lo = [a - fl(r[key + "_lo"]) for a, r in zip(v, rows)]; hi = [fl(r[key + "_hi"]) - a for a, r in zip(v, rows)]
        g = gerr([x + dx for x in m], v, lo, hi, col, mk); g.Draw("P"); gs.append(g)
    text(0.23, 0.86, f"#bf{{{CH[ch]}}}", 0.05)
    if j == 0: legend(0.55, 0.16, 0.94, 0.3, [(gs[1], "13.6 TeV", "pe"), (gs[0], "13 TeV", "pe")], size=0.045)
save(c, "F02_trigger_and_charge", """**Fig. 2.** Trigger efficiency ε_trig (pT of the quirk pair > 200 GeV) for colored (left) and EW (centre) quirks, and the fraction f_ch of triggered
colored events with both quirk-hadrons charged (right), at 13 TeV (orange squares) and 13.6 TeV (blue circles). Error bars: Wilson 68%. Points are offset by ±12 GeV for
legibility. Source: data/xsec_and_trigger.csv.""", ["xsec_and_trigger.csv"])

# ---------- F06: background vs mu
B = read("background_vs_mu.csv"); TB = read("background_13p6TeV_thresholds.csv")
c = ROOT.TCanvas("F06", "", 1600, 700); c.Divide(2, 1, 0.002, 0.002)
p = c.cd(1); p.SetLeftMargin(0.15); frame(p, -4, 0.005, 64, 40, "pile-up #mu", "fraction in the signal region [%]", logy=True); gl = []
for E, col, mk, dx in (("13", E13, 21, -0.8), ("13.6", E136, 20, 0.8)):
    rows = sorted([r for r in B if r["sqrt_s_TeV"] == E and r["sct"] == "Z0" and not r["note"]], key=lambda r: fl(r["mu"]))
    v = [100 * fl(r["frac"]) for r in rows]; g = gerr([fl(r["mu"]) + dx for r in rows], v, [a - 100 * fl(r["frac_lo"]) for a, r in zip(v, rows)], [100 * fl(r["frac_hi"]) - a for a, r in zip(v, rows)], col, mk)
    g.Draw("P"); gl.append((g, f"{E} TeV, #sigma_{{z}} = 0", "pe"))
    rz = sorted([r for r in B if r["sqrt_s_TeV"] == E and r["sct"] == "Z1160"], key=lambda r: fl(r["mu"]))
    xs = [fl(r["mu"]) + dx for r in rz]; ys = [100 * (fl(r["frac_UL95"]) if r["sr"] == "0" else fl(r["frac"])) for r in rz]
    gz = ROOT.TGraph(len(xs), array.array("d", xs), array.array("d", ys)); gz.SetMarkerStyle(23 if E == "13.6" else 32); gz.SetMarkerColor(col); gz.SetMarkerSize(1.3); gz.Draw("P"); KEEP.append(gz)
    gl.append((gz, f"{E} TeV, #sigma_{{z}} = 1.16 mm (95% UL if k = 0)", "p"))
rs = [r for r in B if r["note"]][0]; v = 100 * fl(rs["frac"])
g = gerr([fl(rs["mu"]) - 2.4], [v], [v - 100 * fl(rs["frac_lo"])], [100 * fl(rs["frac_hi"]) - v], E13, 25); g.Draw("P"); gl.insert(1, (g, "13 TeV, #sigma_{z} = 0, other pile-up seed", "pe"))
legend(0.33, 0.37, 0.95, 0.59, gl, size=0.033)                                  # empty band between 0.07% and 0.9%
p = c.cd(2); p.SetLeftMargin(0.13); frame(p, -4, 0, 64, 28, "pile-up #mu", "events at 13.6 TeV, 332 fb^{-1}  (#sigma_{z} = 0)")
rows = sorted([r for r in TB if r["sct"] == "Z0"], key=lambda r: fl(r["mu"])); mus = [fl(r["mu"]) for r in rows]; gs = []
for key, lab, col, mk in (("N_bkg_332fb", "expected background b", INK, 20), ("s_excl_332fb", "signal for 95% CL_{s} exclusion", E136, 22), ("s_disc_332fb", "signal for discovery", C("#0d366b"), 33)):
    g = gerr(mus, [fl(r[key]) for r in rows], [0] * len(rows), [0] * len(rows), col, mk, size=1.6); g.SetLineWidth(2); g.Draw("PL"); gs.append((g, lab, "pl"))
legend(0.17, 0.72, 0.7, 0.91, gs, size=0.04)
z3 = ROOT.TLine(-4, 3, 64, 3); z3.SetLineColor(MUTED); z3.SetLineStyle(2); z3.Draw(); KEEP.append(z3); text(63, 3.5, "N = 3 (zero background)", 0.034, 31, INK2, ndc=False)
save(c, "F06_background_vs_pileup", """**Fig. 6.** Converted-photon background versus pile-up. Left: fraction of converted photons (Z(νν̄)γj, MET > 200 GeV) that pass the full
selection, with Wilson 68% errors, at 13 TeV (orange; μ = 0, 20, 33.7, 50; open square: μ = 50 with another pile-up seed) and 13.6 TeV (blue; μ = 0, 20, 50, 60). Triangles:
σ_z = 1.16 mm, 95% upper limit when no event passes (one event at 13.6 TeV, μ = 60). Right: 13.6 TeV, σ_z = 0, at 332 fb⁻¹ (σ_γ × 1% = 2.30 fb): expected background and the
signal counts required for exclusion and discovery. Source: S1_background_139fb.csv, S1_background_run2.csv, S2_background_13p6TeV.csv via data/background_vs_mu.csv,
data/background_13p6TeV_thresholds.csv.""", ["background_vs_mu.csv", "background_13p6TeV_thresholds.csv"])

# ---------- F07: mixed test
M = read("mix_test_mu50.csv"); c = ROOT.TCanvas("F07", "", 1300, 750); c.SetLeftMargin(0.36); c.SetRightMargin(0.04)
n = len(M); h = ROOT.TH2F("h7", "", 10, 1.3, 2.5, n, 0, n); h.GetXaxis().SetTitle("signal-region fraction of converted photons [%]  (#sigma_{z} = 0, #mu = 50)")
labs = [f"photons {r['photons_TeV']} TeV, pile-up {r['pileup_TeV'].split(' ')[0]} TeV" + (" (2nd seed)" if "seed" in r["pileup_TeV"] else "") for r in M]
for i, l in enumerate(labs): h.GetYaxis().SetBinLabel(i + 1, l)
h.GetYaxis().SetLabelSize(0.045); h.Draw("AXIS"); KEEP.append(h)
vals = [100 * fl(r["frac"]) for r in M]; mean = sum(fl(r["sr"]) for r in M) / sum(fl(r["n"]) for r in M) * 100
NT = sum(fl(r["n"]) for r in M); sm = 100 * math.sqrt(mean / 100 * (1 - mean / 100) / NT)
band = ROOT.TBox(mean - sm, 0, mean + sm, n); band.SetFillColorAlpha(GRID, 0.7); band.Draw(); KEEP.append(band)
ln = ROOT.TLine(mean, 0, mean, n); ln.SetLineColor(MUTED); ln.SetLineStyle(2); ln.Draw(); KEEP.append(ln)
for i, r in enumerate(M):
    col = E13 if r["photons_TeV"] == "13" else E136; mk = 21 if r["photons_TeV"] == "13" else 20
    g = gerr([vals[i]], [i + 0.5], [0], [0], col, mk, exl=[vals[i] - 100 * fl(r["frac_lo"])], exh=[100 * fl(r["frac_hi"]) - vals[i]], size=1.6); g.Draw("P")
    text(100 * fl(r["frac_hi"]) + 0.02, i + 0.5, f"{r['sr']}/{r['n']}", 0.036, 12, INK2, ndc=False)
h.Draw("AXIS SAME")
text(0.37, 0.94, f"dashed: mean of the five runs, {mean:.2f}%; band: its #pm 1#sigma (binomial)", 0.032, 11, INK2)
save(c, "F07_mix_test_mu50", """**Fig. 7.** Mixed test of the σ_z = 0 background at μ = 50: every combination of 13 or 13.6 TeV photons with the 13 or 13.6 TeV minimum-bias pool,
and the 13 TeV inputs with a second pile-up seed. Points: fraction of converted photons in the signal region with Wilson 68% errors; counts at the right. The original
13 TeV run (146/9139) is the low one; with another seed the same inputs give 181/9139. Neither the photons nor the pool shift the rate consistently.
Source: background chunk files via data/mix_test_mu50.csv.""", ["mix_test_mu50.csv"])

# ---------- F08: maximum reach summary
R = read("reach_summary.csv"); SC = [("13TeV_139fb", "13 TeV, 139 fb^{-1}"), ("13TeV_300fb", "13 TeV, 300 fb^{-1}"), ("13p6TeV_300fb", "13.6 TeV, 300 fb^{-1}"),
                                    ("13p6TeV_332fb", "13.6 TeV, 332 fb^{-1}"), ("13p6TeV_332fb_mu50", "13.6 TeV, 332 fb^{-1}, #mu = 50"), ("13p6TeV_332fb_pooled_eff", "13.6 TeV, 332 fb^{-1}, pooled #varepsilon")]
c = ROOT.TCanvas("F08", "", 1700, 1250); top = ROOT.TPad("t8", "", 0, 0.06, 1, 1); bot = ROOT.TPad("b8", "", 0, 0, 1, 0.06); top.Draw(); bot.Draw(); KEEP.extend([top, bot]); top.Divide(2, 2, 0.002, 0.002); LE = None
for i, (cn, ch) in enumerate([(a, b) for a in ("exclusion", "discovery") for b in ("colored", "EW")]):
    p = top.cd(i + 1); p.SetLeftMargin(0.33); p.SetRightMargin(0.03); p.SetTopMargin(0.09)
    xr = (1150, 1900) if ch == "colored" else (330, 900); h = ROOT.TH2F(f"h8{i}", "", 10, xr[0], xr[1], len(SC), 0, len(SC)); KEEP.append(h)
    for k, (s, lab) in enumerate(SC): h.GetYaxis().SetBinLabel(len(SC) - k, lab)
    h.GetXaxis().SetTitle(f"maximum m_{{Q}} reach [GeV]"); h.GetYaxis().SetLabelSize(0.05); h.Draw("AXIS"); gs = {}
    for sct, dy, mk in (("Z1160", 0.62, 20), ("Z0", 0.38, 21)):
        for k, (s, lab) in enumerate(SC):
            r = [x for x in R if x["scenario"] == s and x["channel"] == ch and x["sct"] == sct and x["contour"] == cn]
            if not r: continue
            r = r[0]; v = fl(r["m_max"]); lo, hi = fl(r["lo"]), fl(r["hi"]); y = len(SC) - 1 - k + dy
            g = gerr([v], [y], [0], [0], SZ[sct], mk, exl=[v - lo if lo == lo else 0], exh=[hi - v if hi == hi else 0], size=1.5); g.Draw("P"); gs.setdefault(sct, g)
    text(0.34, 0.935, f"#bf{{{CH[ch]}}}, {'exclusion (N = 3 / 95% CL_{s})' if cn == 'exclusion' else 'discovery (N = 5 / Z_{A} = 5)'}", 0.045)
    LE = LE or gs; h.Draw("AXIS SAME")
bot.cd(); legend(0.25, 0.05, 0.85, 0.95, [(LE["Z1160"], "#sigma_{z}^{SCT} = 1.16 mm (Knapen)", "pe"), (LE["Z0"], "#sigma_{z}^{SCT} = 0", "pe")], ncol=2, size=0.4)
save(c, "F08_reach_summary", """**Fig. 8.** Maximum quirk-mass reach (over Λ) for every scenario, with the ±1σ Wilson range on k/n where available. Green circles: SCT σ_z = 1.16 mm
(Knapen); violet squares: σ_z = 0. "μ = 50": with the 13.6 TeV converted-photon background at μ = 50 (95% CL_s / Asimov Z = 5 thresholds). "pooled ε": the 13.6 TeV
σ ε_trig f_ch with the selection efficiencies of the 13 and 13.6 TeV samples combined (cross-check, no band). Source: S1_reach_139fb.csv, F6_reach.csv, S2_reach.csv,
S2_reach_with_background.csv, S2_compare_reach.csv via data/reach_summary.csv.""", ["reach_summary.csv"])

# ---------- F09: bootstrap of the 13 -> 13.6 TeV reach change
BT = read("bootstrap.csv"); c = ROOT.TCanvas("F09", "", 1300, 800); c.SetLeftMargin(0.33); c.SetRightMargin(0.04)
n = len(BT); h = ROOT.TH2F("h9", "", 10, -260, 160, n, 0, n); h.GetXaxis().SetTitle("#Delta = reach(13.6 TeV) #minus expected reach  [GeV]   (332 fb^{-1})"); KEEP.append(h)
for i, r in enumerate(BT): h.GetYaxis().SetBinLabel(n - i, f"{r['channel']}, {'#sigma_{z} = 1.16 mm' if r['sct'] == 'Z1160' else '#sigma_{z} = 0'}, {r['contour']}")
h.GetYaxis().SetLabelSize(0.042); h.Draw("AXIS")
z = ROOT.TLine(0, 0, 0, n); z.SetLineColor(MUTED); z.SetLineStyle(2); z.Draw(); KEEP.append(z)
for i, r in enumerate(BT):
    v = fl(r["delta_observed"]); y = n - 1 - i + 0.5; s = fl(r["sigma_boot"])
    g = gerr([v], [y], [0], [0], SZ[r["sct"]], 20 if r["sct"] == "Z1160" else 21, exl=[s], exh=[s], size=1.5); g.Draw("P")
    text(150, y, f"{v / s:+.1f}#sigma", 0.036, 32, INK2, ndc=False)
h.Draw("AXIS SAME")
save(c, "F09_bootstrap_13_vs_13p6", """**Fig. 9.** Change of the reach from 13 to 13.6 TeV against the expectation from the cross-section and trigger gain alone. Δ = (13.6 TeV reach) −
(13 TeV selection efficiencies × 13.6 TeV σ ε_trig f_ch), at 332 fb⁻¹; error bars: ±1σ from 500 bootstrap replicas (events resampled per mass point, all Λ of an event
together, both samples). Δ/σ at the right. The colored σ_z = 1.16 mm deficit is −1.1σ (exclusion) and −1.7σ (discovery). Source: S2_compare_bootstrap.csv via data/bootstrap.csv.""", ["bootstrap.csv"])

# ---------- F10: k/n of the colored channel, 13 vs 13.6 TeV
KN = read("kn_13_vs_13p6.csv"); c = ROOT.TCanvas("F10", "", 1800, 1050); c.Divide(3, 2, 0.002, 0.002); LE = []
for i, (sct, lam) in enumerate([(a, b) for a in ("Z1160", "Z0") for b in ("2.0", "4.0", "5.0")]):
    p = c.cd(i + 1); p.SetLeftMargin(0.17); p.SetTopMargin(0.09)
    rows = sorted([r for r in KN if r["channel"] == "colored" and r["sct"] == sct and r["lambda_keV"] == lam], key=lambda r: fl(r["mass_gev"]))
    frame(p, 500, 0, 2200, 0.2 if sct == "Z1160" else 0.5, "m_{Q} [GeV]", "k / n  (signal region / propagated)"); gs = []
    for E, col, mk, dx in (("13", E13, 21, -15), ("13p6", E136, 20, 15)):
        v = [fl(r[f"k_{E}"]) / fl(r[f"n_{E}"]) for r in rows]
        g = gerr([fl(r["mass_gev"]) + dx for r in rows], v, [a - fl(r[f"lo_{E}"]) for a, r in zip(v, rows)], [fl(r[f"hi_{E}"]) - a for a, r in zip(v, rows)], col, mk); g.Draw("P"); gs.append(g)
    text(0.2, 0.935, f"#bf{{colored}}, {SCT[sct]}, #Lambda = {float(lam):g} keV", 0.042)
    if i == 0: LE = gs
c.cd(1); legend(0.55, 0.72, 0.94, 0.88, [(LE[1], "13.6 TeV", "pe"), (LE[0], "13 TeV", "pe")], size=0.045)
save(c, "F10_selection_efficiency_colored", """**Fig. 10.** Fraction k/n of propagated colored-quirk events that pass the full selection, at 13 TeV (orange) and 13.6 TeV (blue), for Λ = 2, 4 and
5 keV. Top: SCT σ_z = 1.16 mm, where k = 0–9 per point; bottom: σ_z = 0 on the same events. Error bars: Wilson 68%; points offset by ±15 GeV. The 13.6 TeV deficit at
1200–2100 GeV appears only at σ_z = 1.16 mm. Source: S2_compare_factors.csv via data/kn_13_vs_13p6.csv.""", ["kn_13_vs_13p6.csv"])

# ---------- F11: expected signal events per mass point (best Lambda), 13 TeV 139 fb^-1 vs 13.6 TeV 332 fb^-1
EV = read("expected_events.csv"); s50 = {r["sct"] + r["mu"]: r for r in read("background_13p6TeV_thresholds.csv")}
c, hd, top, bot = layout("F11"); header(hd, "Expected signal events at the best #Lambda of each mass point (no pile-up on the signal)"); LE = {}
for i, (ch, sct) in enumerate([(a, b) for a in ("colored", "EW") for b in ("Z1160", "Z0")]):
    p = top.cd(i + 1); p.SetLeftMargin(0.13); p.SetRightMargin(0.05); p.SetTopMargin(0.08)
    x1, x2 = XR[ch][0] - 100 if ch == "colored" else 40, XR[ch][1] + 100 if ch == "colored" else 1060
    frame(p, x1, 0.008, x2, 3e4, "m_{Q} [GeV]", "expected signal events N", logy=True)
    lines_ = [(3.0, 2, MUTED, "N = 3"), (5.0, 1, MUTED, "N = 5")] + ([(fl(s50[sct + "50"]["s_excl_332fb"]), 3, C("#1c5cab"), "s_{req}, #mu = 50")] if sct == "Z0" else [])
    for yv, ls, col, lab in lines_:
        l = ROOT.TLine(x1, yv, x2, yv); l.SetLineStyle(ls); l.SetLineColor(col); l.SetLineWidth(2); l.Draw(); KEEP.append(l); LE.setdefault(lab, l)
    for E, col, mk, dx in (("13TeV_139fb", E13, 21, -12), ("13p6TeV_332fb", E136, 20, 12)):
        rows = sorted([r for r in EV if r["scenario"] == E and r["channel"] == ch and r["sct"] == sct], key=lambda r: fl(r["mass_gev"]))
        cp = [r for r in rows if r["status"] == "computed"]; bd = [r for r in rows if r["status"] == "bound"]
        g = gerr([fl(r["mass_gev"]) + dx for r in cp], [fl(r["best_N"]) for r in cp], [fl(r["best_N"]) - fl(r["best_lo"]) for r in cp], [fl(r["best_hi"]) - fl(r["best_N"]) for r in cp], col, mk)
        g.Draw("P"); LE.setdefault(E, g)
        if bd:
            gb = gerr([fl(r["mass_gev"]) + dx for r in bd], [fl(r["best_N"]) for r in bd], [0] * len(bd), [0] * len(bd), col, 25); gb.Draw("P"); LE.setdefault("bound", gb)
    text(0.14, 0.94, f"#bf{{{CH[ch]}}}, {SCT[sct]}", 0.045); p.RedrawAxis()
bot.cd(); legend(0.04, 0.05, 0.98, 0.95, [(LE["13TeV_139fb"], "13 TeV, 139 fb^{-1}", "pe"), (LE["13p6TeV_332fb"], "13.6 TeV, 332 fb^{-1}", "pe"),
                                          (LE["bound"], "13 TeV, not propagated (upper bound)", "p"), (LE["N = 3"], "N = 3: exclusion, no background", "l"),
                                          (LE["N = 5"], "N = 5: discovery, no background", "l"), (LE["s_{req}, #mu = 50"], "#sigma_{z} = 0: needed at #mu = 50", "l")], ncol=3, size=0.17)
save(c, "F11_expected_events", """**Fig. 11.** Expected number of signal events N = L σ ε_trig f_ch k/n at every simulated mass point, taken at the Λ with the largest N, for 13 TeV and 139 fb⁻¹
(orange squares) and 13.6 TeV and 332 fb⁻¹ (blue circles); error bars: Wilson 68% on k/n; points offset by ±12 GeV. Open square: 13 TeV colored 2400 GeV, not propagated
(upper bound, already below 3). Grey lines: N = 3 (dashed, exclusion) and N = 5 (solid, discovery) without background; blue dotted (σ_z = 0 only): signal needed for
exclusion with the μ = 50 background at 13.6 TeV. A mass is reachable where its point lies above the line. Signal without pile-up. Source: S1_N_grid_139fb.csv,
S2_N_grid_300fb.csv (× 332/300) via data/expected_events.csv.""", ["expected_events.csv", "background_13p6TeV_thresholds.csv"])
# ---------- F12: pulls of the selection efficiency, 13.6 vs 13 TeV
UM = read("unc_consistency_mass.csv"); US = read("unc_consistency.csv")
c, hd, top, bot = layout("F12", 1600, 1250); header(hd, "Selection efficiency 13.6 TeV vs 13 TeV: pull z per mass point (permutation test)"); LE = {}
for i, (ch, sct) in enumerate([(a, b) for a in ("colored", "EW") for b in ("Z1160", "Z0")]):
    p = top.cd(i + 1); p.SetLeftMargin(0.13); p.SetRightMargin(0.05); p.SetTopMargin(0.08)
    x1, x2 = (450, 2250) if ch == "colored" else (40, 1060)
    frame(p, x1, -4.6, x2, 3.6, "m_{Q} [GeV]", "z = (13.6 TeV #minus 13 TeV) / #sigma")
    for lo, hi, col in ((-2, 2, C("#ecebe8")), (-1, 1, C("#d9d8d4"))):
        bx = ROOT.TBox(x1, lo, x2, hi); bx.SetFillColor(col); bx.Draw(); KEEP.append(bx); LE.setdefault(hi, bx)
    l0 = ROOT.TLine(x1, 0, x2, 0); l0.SetLineColor(MUTED); l0.SetLineStyle(2); l0.Draw(); KEEP.append(l0)
    rows = sorted([r for r in UM if r["channel"] == ch and r["sct"] == sct], key=lambda r: fl(r["mass_gev"]))
    g = gerr([fl(r["mass_gev"]) for r in rows], [fl(r["z"]) for r in rows], [1.0] * len(rows), [1.0] * len(rows), SZ[sct], 20 if sct == "Z1160" else 21, size=1.5); g.Draw("P"); LE.setdefault(sct, g)
    t = [r for r in US if r["channel"] == ch and r["sct"] == sct][0]
    text(0.17, 0.255, f"#chi^{{2}}/ndf = {fl(t['chi2']):.1f}/{t['n_points']}, p = {fl(t['p_chi2']):.2f}", 0.042, 11, INK2)
    text(0.17, 0.19, f"mean pull #Sigmaz/#sqrt{{M}} = {fl(t['signed_z']):+.2f}, p = {fl(t['p_signed_two']):.2f}", 0.042, 11, INK2)
    text(0.14, 0.94, f"#bf{{{CH[ch]}}}, {SCT[sct]}", 0.045); p.RedrawAxis()
bot.cd(); legend(0.04, 0.05, 0.98, 0.95, [(LE["Z1160"], "#sigma_{z} = 1.16 mm", "p"), (LE["Z0"], "#sigma_{z} = 0", "p"), (LE[1], "#pm 1#sigma", "f"), (LE[2], "#pm 2#sigma", "f")], ncol=4, size=0.24)
save(c, "F12_pulls_13_vs_13p6", """**Fig. 12.** Is the selection efficiency the same at 13 and 13.6 TeV? For every mass point, z = (mean pass fraction over the 15 Λ values at 13.6 TeV −
the same at 13 TeV) divided by its standard deviation under 5000 random relabellings of the pooled events (permutation test; error bar ±1 by construction). Grey bands:
±1σ and ±2σ. In each panel: χ² = Σz² and the mean pull Σz/√M with permutation p-values. All 24 points lie within ±2σ except colored σ_z = 0 at 900 GeV (+2.0σ, p = 0.05),
as expected for 24 points; the four channel tests give p = 0.13–0.73 (global p = 0.43). Source: S2_unc_consistency_mass.csv, S2_unc_consistency.csv via data/unc_*.csv.""",
     ["unc_consistency_mass.csv", "unc_consistency.csv"])

# ---------- F13: reach with the total statistical uncertainty, 13 vs 13.6 TeV
UR = read("unc_reach.csv"); c = ROOT.TCanvas("F13", "", 1700, 900); tp = ROOT.TPad("tp", "", 0, 0.12, 1, 1); bp = ROOT.TPad("bp", "", 0, 0, 1, 0.12)
for q in (tp, bp): q.Draw()
KEEP.extend([c, tp, bp]); tp.Divide(2, 1, 0.002, 0.002)
RW = [("Z1160", "-1", "exclusion", "#sigma_{z} = 1.16 mm, exclusion"), ("Z1160", "-1", "discovery", "#sigma_{z} = 1.16 mm, discovery"), ("Z0", "-1", "exclusion", "#sigma_{z} = 0, exclusion"),
      ("Z0", "-1", "discovery", "#sigma_{z} = 0, discovery"), ("Z0", "50", "exclusion", "#sigma_{z} = 0, #mu = 50, excl."), ("Z0", "50", "discovery", "#sigma_{z} = 0, #mu = 50, disc.")]
LE = {}
for j, (ch, xr) in enumerate((("colored", (1150, 1900)), ("EW", (350, 880)))):
    p = tp.cd(j + 1); p.SetLeftMargin(0.36); p.SetRightMargin(0.05); p.SetBottomMargin(0.14); p.SetTopMargin(0.08)
    n = len(RW); h = ROOT.TH2F(f"h13{j}", "", 10, xr[0], xr[1], n, 0, n); h.GetXaxis().SetTitle("maximum m_{Q} reach [GeV]"); KEEP.append(h)
    for i, (_, _, _, lab) in enumerate(RW): h.GetYaxis().SetBinLabel(n - i, lab)
    h.GetYaxis().SetLabelSize(0.048); h.GetXaxis().SetLabelSize(0.042); h.GetXaxis().SetTitleSize(0.05); h.GetXaxis().SetNdivisions(505); h.Draw("AXIS")
    for i, (sct, mu, cn, _) in enumerate(RW):
        for E, col, mk, dy in (("13.0", E13, 21, 0.18), ("13.6", E136, 20, -0.18)):
            r = [x for x in UR if x["sqrt_s_TeV"] == E and x["channel"] == ch and x["sct"] == sct and x["mu"] == mu and x["contour"] == cn]
            if not r: continue
            r = r[0]; v = fl(r["central"]); y = n - 1 - i + 0.5 + dy
            g = gerr([v], [y], [0], [0], col, mk, exl=[v - fl(r["all_16"])], exh=[fl(r["all_84"]) - v], size=1.4); g.Draw("P"); LE.setdefault(E, g)
            gk = gerr([v], [y], [0], [0], col, mk, exl=[v - fl(r["kn_16"])], exh=[fl(r["kn_84"]) - v], size=1.4); gk.SetLineWidth(6); gk.Draw("P")
    text(0.37, 0.95, f"#bf{{{CH[ch]}}}", 0.05); h.Draw("AXIS SAME")
bp.cd(); legend(0.04, 0.1, 0.6, 0.9, [(LE["13.0"], "13 TeV, 139 fb^{-1}", "pe"), (LE["13.6"], "13.6 TeV, 332 fb^{-1}", "pe")], ncol=2, size=0.32)
text(0.62, 0.5, "thick bar: k/n only;   thin bar: total statistical (16#minus84%)", 0.28, 12, INK2)
save(c, "F13_reach_uncertainty", """**Fig. 13.** Maximum reach with its statistical uncertainty, 13 TeV and 139 fb⁻¹ (orange) and 13.6 TeV and 332 fb⁻¹ (blue). Marker: central value.
Thick bar: 16–84% of 1000 toys resampling only the propagated events (k/n). Thin bar: all statistical sources together (k/n; σ from the MG5 integration error;
ε_trig and f_ch binomial; at μ = 50 also the background count). Rows: SCT setting and contour; μ = 50 only at 13.6 TeV. Source: S2_unc_reach.csv via data/unc_reach.csv.""",
     ["unc_reach.csv"])
print("FIGURES_EXIT=0")
