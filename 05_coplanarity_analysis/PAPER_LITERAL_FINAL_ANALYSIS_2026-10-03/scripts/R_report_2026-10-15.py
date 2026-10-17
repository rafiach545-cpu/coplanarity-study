#!/usr/bin/env python3
"""Builds TABLE_I_REPRODUCTION_REPORT_2026-10-15.pdf (A4): update of the 2026-10-09 report with the work of 2026-10-10 ... 2026-10-15 (D17-D41).
All numbers come from scripts/R_data_2026_10_15.py (read from the analysis outputs, with assertions). Uncertainties: simple approximate binomial
sigma = sqrt(e (1 - e) / n) with the denominator of each efficiency; no Wilson intervals, no p-values (request of 2026-10-15).
The 2026-10-09 report is not modified. Run with a Python that has reportlab (4.2.5 used)."""
import os, sys, re, json
import numpy as np, pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import R_data_2026_10_15 as R

L_ = R.L_; T = R.T; FIG = R.FIG; OUT = f"{L_}/TABLE_I_REPRODUCTION_REPORT_2026-10-15.pdf"
F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", F + "DejaVuSans.ttf")); pdfmetrics.registerFont(TTFont("DVB", F + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVO", F + "DejaVuSans.ttf")); registerFontFamily("DV", normal="DV", bold="DVB", italic="DVO", boldItalic="DVB")
INK, MUTED, RULE = colors.HexColor("#1b2328"), colors.HexColor("#5b6770"), colors.HexColor("#d5dbde")
NOTE, HEAD, PROV = colors.HexColor("#edf3f6"), colors.HexColor("#eef1f2"), colors.HexColor("#fbf0d6")
st = {"h1": ParagraphStyle("h1", fontName="DVB", fontSize=16, leading=20, textColor=INK, spaceAfter=3),
      "h2": ParagraphStyle("h2", fontName="DVB", fontSize=12, leading=15, textColor=INK, spaceBefore=7, spaceAfter=4),
      "h3": ParagraphStyle("h3", fontName="DVB", fontSize=9.6, leading=12.5, textColor=INK, spaceBefore=5, spaceAfter=2),
      "b": ParagraphStyle("b", fontName="DV", fontSize=8.8, leading=12.2, textColor=INK),
      "m": ParagraphStyle("m", fontName="DV", fontSize=7.8, leading=10.4, textColor=MUTED),
      "c": ParagraphStyle("c", fontName="DV", fontSize=7.5, leading=9.6, textColor=INK),
      "ch": ParagraphStyle("ch", fontName="DVB", fontSize=7.1, leading=8.8, textColor=MUTED),
      "eq": ParagraphStyle("eq", fontName="DV", fontSize=8.4, leading=12, textColor=INK, leftIndent=14, spaceBefore=1, spaceAfter=1),
      "q": ParagraphStyle("q", fontName="DVO", fontSize=8.2, leading=10.8, textColor=INK, leftIndent=8),
      "bl": ParagraphStyle("bl", fontName="DV", fontSize=8.6, leading=11.6, textColor=INK, leftIndent=9, bulletIndent=0),
      "exp": ParagraphStyle("exp", fontName="DV", fontSize=8.0, leading=10.8, textColor=INK, leftIndent=6, spaceBefore=1, spaceAfter=4)}
P = lambda t, s="b": Paragraph(t, st[s])
B = lambda xs: [Paragraph(x, st["bl"], bulletText="•") for x in xs]
EQ = lambda t: P(t, "eq")
def grid(data, widths, extra=(), head=1):
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=head)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, head - 1), HEAD), ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE), ("BOX", (0, 0), (-1, -1), 0.6, RULE),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
                           ("LEFTPADDING", (0, 0), (-1, -1), 3.5), ("RIGHTPADDING", (0, 0), (-1, -1), 3.5)] + list(extra))); return t
H = lambda *xs: [P(x, "ch") for x in xs]
C = lambda *xs: [x if not isinstance(x, str) else P(x, "c") for x in xs]
def img(name, w):
    from reportlab.lib.utils import ImageReader
    p = f"{FIG}/{name}/{name}.png"; iw, ih = ImageReader(p).getSize(); return Image(p, width=w * mm, height=w * mm * ih / iw)
def explain(items):
    """substantive explanation directly under a figure: list of (label, text)"""
    return [P(f"<b>{a}.</b> {b}", "exp") for a, b in items]
def box(title, items, bg=NOTE):
    t = Table([[[P(f"<b>{title}</b>")] + items]], colWidths=[174 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)])); return t
def es(k, n, d=3):
    if n == 0: return "—"
    if k == 0: return f"0 (95% UL {R.ul95(n):.{d}f})"
    e, s = R.sig(k, n); return f"{e:.{d}f} ± {s:.{d}f}"
sci = lambda x: (lambda m, e: f"{m}×10<super>{int(e)}</super>")(*f"{x:.1e}".split("e"))

# ---------------- data ----------------
import subprocess
if not os.environ.get("D41_NMAX"):                                   # freeze the D41 snapshot, then rebuild the F38 figures with the same events
    os.environ["D41_NMAX"] = str(R.d41()["n"])
subprocess.run([sys.executable, f"{HERE}/F38_report_2026_10_15_figs.py"], check=True, env=os.environ, capture_output=True)
CNT = R.production(); BG = R.backgrounds(); LT = R.lo_trigger(); D41 = R.d41(); D41s = R.d41("mg5_373_lo_showered")
S2, pl2, pd2, ours2 = R.fig2(); CH = R.checks(); LS = R.lambda_scan()
c, e = CNT["COL2000"], CNT["EW2000"]; N41 = D41["n"] if D41 else 0; FINAL41 = N41 >= 3000
V5 = json.load(open(f"{T}/paper_fig5_vector.json")); V23 = json.load(open(f"{T}/paper_fig23_vector.json"))
def pmed(b):
    lo = np.array([x["lo"] for x in b]); hi = np.array([x["hi"] for x in b]); h = np.array([x["height"] for x in b]); cc = np.cumsum(h) / h.sum(); i = int(np.searchsorted(cc, 0.5))
    f = (0.5 - (cc[i - 1] if i else 0)) / (cc[i] - (cc[i - 1] if i else 0)); return 10 ** (np.log10(lo[i]) + f * np.log10(hi[i] / lo[i]))
PM = {lab: (pmed(V5["delta_s_cm"]["histograms"][lab]), pmed(V5["delta_w_cm"]["histograms"][lab])) for lab in V5["delta_s_cm"]["histograms"]}
PAPER_BELOW = {lab: sum(b["height"] for b in V5["delta_s_cm"]["histograms"][lab] if b["hi"] <= 0.0101) / sum(b["height"] for b in V5["delta_s_cm"]["histograms"][lab]) for lab in V5["delta_s_cm"]["histograms"]}
c3 = pd.read_csv(f"{T}/fig3_velocity_plane_curves.csv"); e3 = c3[c3.r_cm > 14.5].groupby(["sample", "key"]).dphi_rad.median()
P3 = {"COL2000": V23["fig3"]["curves"]["colored_1800GeV_2keV"], "EW2000": V23["fig3"]["curves"]["EW_800GeV_2keV"]}
p3end = {s: float(np.interp(15.0, np.array(cv["x"]), np.array(cv["y"]))) * 1e-3 for s, cv in P3.items()}
f4 = {sct: pd.read_csv(f"{FIG}/F29_fig4_{sct}/F29_fig4_{sct}_source.csv") for sct in ("Z1160", "Z0")}
F5 = {sct: pd.read_csv(f"{FIG}/F30_fig5_{sct}/F30_fig5_{sct}_source.csv").dropna(subset=["ds"]) for sct in ("Z1160", "Z0")}
for s, sct in (("colored", "Z0"), ("EW", "Z0"), ("colored", "Z1160"), ("EW", "Z1160")):   # Fig. 5 signal population = plane + hit cut of the production samples
    smp = "COL2000" if s == "colored" else "EW2000"; assert (F5[sct].population == s).sum() == CNT[smp][("FIRST", sct)]["mult"]
FL = pd.read_csv(f"{T}/fig2_L_check.csv")
A_ = CH["annih_A"]; D29 = CH["D29"]; D32 = CH["D32"]; D14 = CH["D14"]; D26 = CH["D26"]; P24 = CH["P24"]

# ---------------- document ----------------
S = []
S += [P("Reproduction of Table I of arXiv:1708.02243 — update", "h1"),
      P("S. Knapen, H. K. Lou, M. Papucci, J. Setford, “Tracking down quirks at the Large Hadron Collider”, Phys. Rev. D 96, 115015 (2017) · Table I, backgrounds, "
        "Figures 2–5 · 2000-event production samples and an EW LO sample · 15 October 2026 (replaces the summary of the 9 October report; that report is kept unchanged)", "m"), Spacer(1, 5)]
lt = LT[("3.7.3", "EW")]; d4 = D41[4] if D41 else None
S += [box("Executive summary", B([
    f"<b>Trigger.</b> Colored: {c['trig']}/{c['matched']} = {es(c['trig'], c['matched'])} (paper 0.24). EW, matched + showered production sample: {es(e['trig'], e['matched'])} (paper 0.10). "
    f"EW, LO cross-section ratio σ(QQ̄j, p<sub>T</sub>(j) &gt; 200 GeV)/σ(QQ̄) = {lt['r']:.3f} ± {lt['dr']:.3f} (MG5 3.7.3; 2.3.3: {LT[('2.3.3','EW')]['r']:.3f}), equal to the paper's 0.10. "
    f"The same LO ratio for colored is {LT[('3.7.3','COL')]['r']:.3f}, not 0.24. The two benchmarks therefore behave as if they had been produced differently; this is an inference, not a demonstration.",
    f"<b>Fiducial.</b> Colored {es(c['fid'], c['charged'])}, EW production {es(e['fid'], e['charged'])}; EW LO sample (first {N41} of 3000 events{'' if FINAL41 else ', run in progress'}) "
    f"{es(d4['fid'], N41)}; paper 0.28 for both.",
    f"<b>Reconstruction.</b> Without SCT z smearing: colored {es(c[('FIRST','Z0')]['sr'], c['fid'])}, EW {es(e[('FIRST','Z0')]['sr'], e['fid'])} (paper 0.35, 0.72). "
    f"With the SCT z resolution the authors confirm (580 µm, Ref. [27]): {es(c[('FIRST','Z580')]['sr'], c['fid'])} and {es(e[('FIRST','Z580')]['sr'], e['fid'])}; with 1.16 mm: "
    f"{es(c[('FIRST','Z1160')]['sr'], c['fid'])} and {es(e[('FIRST','Z1160')]['sr'], e['fid'])}. Only the setting without SCT z smearing reproduces the paper's numbers.",
    "<b>Figure 2.</b> With the paper's equation of motion (Eq. 3 + Lorentz force) |L| returns to zero at every second closest approach and all |L| peaks are equal. "
    "This is the analytic result of Li, Li, Pei and Zhang (arXiv:2002.07503, Appendix A) and is reproduced by three independent codes. The paper's Fig. 2 instead shows "
    "unequal half-oscillations (|L| = 0.19 and 0.29×10¹² ħ at the 2nd and 4th approach); no tested definition, charge set, axis or equation-of-motion variant gives that.",
    "<b>Annihilation.</b> The paper argues that |L| = 0 only at large separation. In the classical model |L| ≈ 0 at every second closest approach, so this argument is not supported. "
    "Whether annihilation then matters needs a quantum estimate of the per-meeting probability; a worst-case estimate is small at the Table I benchmarks (≤ 3% loss for colored at 2 keV) "
    "and grows with Λ.",
    f"<b>Backgrounds.</b> 0 of 9139 converted photons and 0 of 5000 pile-up events in the signal region (SCT z 580 µm), as in the paper; the 95% upper limit "
    f"{sci(R.ul95(9139))} per conversion depends only on the 9139 events, not on the cross section. Without SCT z smearing on the background, {BG['conv0']['sr']}/9139 conversions pass.",
    "<b>Open:</b> EW ε<sub>reco</sub> at Λ = 1–2 keV above the paper; signal strip width Δw 2× (EW) and 5× (colored) the paper's; the SCT z resolution; the unequal half-oscillations of the paper's Fig. 2."]))]
S += [Spacer(1, 3), P("Uncertainties in this report are approximate statistical uncertainties of binomial efficiencies, σ = √(ε(1−ε)/n), with n the denominator of each efficiency "
                      "(Section 1.4). No systematic uncertainty is included. Wilson intervals and p-values of the 9 October report are not repeated.", "m")]

# 1 setup
S += [P("1. Samples, detector model and definitions", "h2"), P("1.1 Signal samples", "h3")]
g = [H("Sample", "Generation", "Events", "Trigger definition")]
g.append(C("Production (colored, EW)", "MG5 3.7.3 + Pythia 8.317, MLM (ickkw 1, xqcut 30 GeV, qCut 45 GeV, nJetMax 1, nQmatch 4, doShowerKt off), nn23lo1, "
           "default dynamical scale, 13 TeV; colored p p → t1 t1~ (+j), EW p p → qe+ qe− (+j); seeds 8001 / 8002", "2000 each", "p<sub>T</sub>(QQ̄) &gt; 200 GeV of the final-state pair"))
g.append(C("EW LO sample A", "p p → qe+ qe−, LO, no shower; MG5 3.7.3 and 2.3.3", "2000", "— (σ only)"))
g.append(C("EW LO sample B (D41)", "p p → qe+ qe− j, p<sub>T</sub>(j) &gt; 200 GeV, |η(j)| &lt; 5, ickkw 0, xqcut 0, LO, no shower; MG5 3.7.3 (seed 41002) and 2.3.3",
           f"3000 ({N41} analysed{'' if FINAL41 else ', run in progress'})", "all events (p<sub>T</sub>(QQ̄) = p<sub>T</sub>(j) &gt; 200 GeV at LO)"))
g.append(C("EW sample B showered (D41 sensitivity)", "sample B + Pythia 8.317, no matching", "3000", "p<sub>T</sub>(QQ̄) &gt; 200 GeV after the shower" +
           ("" if D41s else " — <i>not yet run</i>")))
g.append(C("Colored LO A / B", "p p → t1 t1~ (j), p<sub>T</sub>(j) &gt; 200 GeV, m = 1800 GeV", "2000 each", "— (σ only)"))
S += [grid(g, [36, 82, 22, 34]), P("No generation cut other than those listed. The colored quirk is a Dirac fermion, colour triplet, charge 2/3 (param_card QNUMBERS: 2 spin states; FFV vertices); "
                                     "only its PDG number (1000006) is borrowed from the stop.", "m")]
S += [P("1.2 Detector model and the smearing formulas used", "h3")]
g = [H("Element", "Formula / value", "Source")]
for r in [("Layers", "IBL 3.325, pixel 5.05 / 8.85 / 12.25, SCT 29.9 / 37.1 / 44.3 / 51.4 cm; |z| &lt; 33.0 / 40.05 / 74.9 cm; B = 2 T along z", "paper Sec. III; Ref. [27] lengths; IBL not in [27] (2008), Run-2 values"),
          ("Pixel hit", "pixel centre: x<sub>meas</sub> = p·round(x/p), p<sub>rφ</sub> = 50 µm, p<sub>z</sub> = 250 µm (IBL) / 400 µm; RMS error p/√12 = 14 / 72 / 115 µm; neighbouring pixels merged", "paper: “pixel size rather than the resolution”"),
          ("SCT rφ", "(rφ)<sub>meas</sub> = rφ + σ<sub>rφ</sub>·g, g ~ N(0, 1), σ<sub>rφ</sub> = 34 µm = 2 × 17 µm", "paper: twice the intrinsic accuracy of [27]"),
          ("SCT z", "z<sub>meas</sub> = z + σ<sub>z</sub>·g, σ<sub>z</sub> = 0 (none), 0.58 mm (Ref. [27]; authors' reply), 1.16 mm (2 × 0.58, paper text)", "all three reported"),
          ("Beam spot", "one z<sub>0</sub> ~ N(0, 45 mm) per event shifts all hits; the plane is fitted about the true vertex", "paper Sec. III A; per-event shift: our choice"),
          ("Hits", "first outward crossing of each layer by each quirk, t &lt; 25 ns (every crossing as a sensitivity)", "paper silent; our choice"),
          ("Plane", "T<sub>ij</sub> = Σ<sub>a</sub> x<sub>a,i</sub> x<sub>a,j</sub> / (N − 1); Δs = √λ<sub>1</sub>, Δw = √λ<sub>2</sub>; seeds Δs &lt; 0.05 cm, Δw &lt; 1 cm, factor 3", "paper Sec. III C, Eq. 11"),
          ("Signal region", "2 hits in 7 layers and ≥ 1 in the 8th, Δw &lt; 1 cm, Δs &lt; 0.01 cm", "paper Sec. IV"),
          ("Backgrounds", "[34] detector model (bremsstrahlung, ionisation), SCT z 580 µm; μ = 50 pile-up, Pythia 8 minimum bias", "Ref. [34] App. A; values not stated for SCT z")]:
    g.append(C(*r))
S += [grid(g, [22, 98, 54])]
S += [P("1.3 Efficiencies (paper Eq. 12, ε = ε<sub>trig</sub> × ε<sub>fid</sub> × ε<sub>reco</sub>); each is conditional on the previous stage", "h3")]
g = [H("Efficiency", "Numerator", "Denominator")]
g += [C("ε<sub>trig</sub>", "events with p<sub>T</sub>(QQ̄) &gt; 200 GeV", "events after MLM matching (production); LO: σ(B)/σ(A), a cross-section ratio"),
      C("ε<sub>fid</sub>", "events whose two quirks cross all 8 layers inside the lengths, first crossings at t &lt; 25 ns", "triggered events (colored: both quirk-hadrons charged); LO sample B: all events"),
      C("ε<sub>reco</sub>", "events in the signal region", "fiducial events"),
      C("ε (Eq. 12)", "product of the three", "relative σ added in quadrature (three disjoint binomial stages)")]
S += [grid(g, [22, 82, 70])]
S += [P("1.4 Approximate uncertainty", "h3"), EQ("ε̂ = k / N,    σ<sub>ε̂</sub> ≈ √( ε̂ (1 − ε̂) / N ),    N = number of events entering that selection"),
      P("For 0 passing events the formula gives 0; the 95% upper limit 1 − 0.05<super>1/N</super> ≈ 3/N is quoted instead. The LO trigger ratio is a ratio of integrated cross sections; "
        "its uncertainty comes from the MadGraph integration errors, σ<sub>r</sub>/r = √((δσ<sub>A</sub>/σ<sub>A</sub>)² + (δσ<sub>B</sub>/σ<sub>B</sub>)²). The events are unweighted and independent; "
        "the same events enter all Λ points (correlated between Λ, not between samples).", "m")]

# 2 Table I
S += [P("2. Table I", "h2"), P("2.1 Event counts of the production samples (first crossing)", "h3")]
g = [H("Step", "Colored: none", "580 µm", "1.16 mm", "EW: none", "580 µm", "1.16 mm")]
g.append(C("after matching", *[str(c["matched"])] * 3, *[str(e["matched"])] * 3)); g.append(C("triggered", *[str(c["trig"])] * 3, *[str(e["trig"])] * 3))
g.append(C("both charged (colored)", *[str(c["charged"])] * 3, "—", "—", "—")); g.append(C("fiducial", *[str(c["fid"])] * 3, *[str(e["fid"])] * 3))
for lab, k in [("plane found (Δw &lt; 1 cm)", "plane"), ("+ hit multiplicity", "mult"), ("+ Δs &lt; 0.01 cm = signal region", "sr")]:
    g.append(C(lab, *[str(CNT[s][("FIRST", z)][k]) for s in R.SAM for z in ("Z0", "Z580", "Z1160")]))
S += [grid(g, [44, 22, 22, 22, 22, 21, 21]), P(f"{c['tech']} colored and {e['tech']} EW triggered events stopped with a numerical integration error and are counted as not fiducial.", "m")]
S += [P("2.2 Efficiencies against the paper", "h3")]
g = [H("Benchmark", "Efficiency", "Sample / setting", "k / N", "ε ± σ", "Paper")]
for s, v in R.SAM.items():
    C_ = CNT[s]; nm = f"{v['name']} {v['mq']} GeV, {v['lam']} keV"; rows = [("ε<sub>trig</sub>", "production (MLM + shower)", C_["trig"], C_["matched"])]
    lr = LT[("3.7.3", "EW" if s == "EW2000" else "COL")]; lr2 = LT[("2.3.3", "EW" if s == "EW2000" else "COL")]
    rows.append(("ε<sub>trig</sub>", "LO ratio σ(QQ̄j)/σ(QQ̄), MG5 3.7.3 / 2.3.3", None, f"{lr['r']:.3f} ± {lr['dr']:.3f} / {lr2['r']:.3f} ± {lr2['dr']:.3f}"))
    rows.append(("ε<sub>fid</sub>", "production", C_["fid"], C_["charged"]))
    if s == "EW2000" and D41: rows.append(("ε<sub>fid</sub>", f"LO sample B, Λ = 4 keV ({N41} events)", D41[4]["fid"], N41))
    for z, zl in (("Z0", "SCT z none"), ("Z580", "SCT z 580 µm"), ("Z1160", "SCT z 1.16 mm")): rows.append(("ε<sub>reco</sub>", f"production, {zl}", C_[("FIRST", z)]["sr"], C_["fid"]))
    if s == "EW2000" and D41: rows.append(("ε<sub>reco</sub>", "LO sample B, SCT z none", D41[4]["sr"], D41[4]["fid"]))
    for j, (q, lab, k, n) in enumerate(rows):
        pv = v["paper"]["trig" if "trig" in q else "fid" if "fid" in q else "reco"]
        g.append(C(nm if j == 0 else "", q, lab, "—" if k is None else f"{k} / {n}", n if k is None else es(k, n), f"{pv:.2f}"))
    for z, zl in (("Z0", "none"), ("Z580", "580 µm")):
        fr = [(C_["trig"], C_["matched"]), (C_["fid"], C_["charged"]), (C_[("FIRST", z)]["sr"], C_["fid"])]; tot = np.prod([k / n for k, n in fr])
        rel = np.sqrt(sum((1 - k / n) / k for k, n in fr if k > 0)); g.append(C("", "ε (Eq. 12)", f"production, SCT z {zl}", "", f"{tot:.4f} ± {tot * rel:.4f}", f"{v['paper']['trig'] * v['paper']['fid'] * v['paper']['reco']:.4f}*"))
S += [grid(g, [32, 18, 56, 18, 34, 16]), P("* product of the paper's Table I entries (the paper does not quote ε). The relative σ of a product uses σ<sub>rel</sub>² = Σ (1 − ε<sub>i</sub>)/k<sub>i</sub>.", "m"),
      Spacer(1, 2), img("F38_table_I", 174)]
S += explain([("What it shows", "Every efficiency of Table I at the two benchmarks: circles are the production samples, squares the EW LO sample B and the LO cross-section ratios; dashes are the paper."),
              ("Mechanism", "ε<sub>trig</sub> is the fraction of pairs recoiling against initial-state radiation with p<sub>T</sub>(QQ̄) &gt; 200 GeV; the matched + showered sample has a larger fraction "
               "than the LO cross-section ratio (0.178 vs 0.096 for EW). "
               "ε<sub>fid</sub> is geometry and the 25 ns cut (heavy, slow pairs). ε<sub>reco</sub> is set by Δs relative to the 0.01 cm cut, which the SCT z smearing dominates."),
              ("Comparison", f"Colored ε<sub>trig</sub> and both ε<sub>fid</sub> agree with the paper. EW ε<sub>trig</sub>: production {e['trig']/e['matched']:.3f}, LO ratio {lt['r']:.3f}, paper 0.10. "
               f"The EW LO sample also gives ε<sub>fid</sub> = {d4['fid']/N41:.3f}, closer to 0.28 than the production {e['fid']/e['charged']:.3f}. "
               "ε<sub>reco</sub> agrees only without SCT z smearing; 580 µm and 1.16 mm give values far below the paper."),
              ("Limitation", f"22 colored fiducial events (σ ≈ 0.10 on ε<sub>reco</sub>). The LO sample is still running ({N41}/3000 events); its showered version is pending.")])
EW2 = LS[(LS["sample"] == "EW2000") & (LS.lambda_keV == 2) & (LS.sct == "Z0") & (LS["mode"] == "FIRST")].iloc[0]
S += [PageBreak(), P("2.3 The Λ column of Table I (ε<sub>reco</sub>, first crossing)", "h3")]
g = [H("Benchmark", "Λ (keV)", "Paper", "Production, none: k / N", "ε ± σ", "Production, 1.16 mm", "EW LO sample B, none: k / N", "ε ± σ")]
for s, v in R.SAM.items():
    x = LS[(LS["sample"] == s) & (LS["mode"] == "FIRST")]
    for i, lk in enumerate(sorted(x.lambda_keV.unique())):
        r0 = x[(x.lambda_keV == lk) & (x.sct == "Z0")].iloc[0]; r1 = x[(x.lambda_keV == lk) & (x.sct == "Z1160")].iloc[0]
        lo = (f"{D41[lk]['sr']} / {D41[lk]['fid']}", es(D41[lk]["sr"], D41[lk]["fid"])) if (s == "EW2000" and D41) else ("—", "—")
        g.append(C(v["name"] if i == 0 else "", str(lk), f"{r0.paper_reco:.3g}", f"{int(r0.k_ge2)} / {int(r0.n_fid)}", es(int(r0.k_ge2), int(r0.n_fid), 2),
                   es(int(r1.k_ge2), int(r1.n_fid), 2), *lo))
S += [grid(g, [20, 13, 13, 30, 26, 26, 28, 26]), Spacer(1, 2), img("F38_lambda", 172)]
S += explain([("What it shows", "ε<sub>reco</sub> versus the string tension Λ. The oscillation amplitude scales as 1/Λ² (Eq. 1), so low Λ means wide strips and many hits off the plane; high Λ means hits merging."),
              ("Mechanism", "At low Λ the plane finder loses events through the Δw seed and hit-multiplicity cuts (Section 2.4); the rise with Λ follows the amplitude. With SCT z 1.16 mm, Δs ≈ 100–200 µm "
               "exceeds the 0.01 cm cut at every Λ, so the efficiency stays low."),
              ("Comparison", "Colored without SCT z smearing follows the paper within about 2σ except at 3 and 5 keV (higher than the paper). EW is above the paper at 1–2 keV in both the production and the LO sample "
               f"(2 keV: {EW2['k_ge2'] / EW2['n_fid']:.2f} production, "
               f"{D41[2]['sr']/D41[2]['fid']:.2f} LO, paper 0.41). The LO sample changes the trigger and fiducial efficiencies but not this excess."),
              ("Limitation", "The same events enter every Λ point, so the points of one curve are correlated.")])
S += [P("2.4 Where events are lost (step-by-step cut-flow, D26)", "h3")]
g = [H("Step", "Colored none", "Colored 580 µm", "EW none", "EW 580 µm")]
for k_ in range(9):
    rr = [D26[(D26["sample"] == s) & (D26.sct == z) & (D26.step == k_)].iloc[0] for s in ("COL2000", "EW2000") for z in ("Z0", "Z580")]
    g.append(C(rr[0].stage.replace("<", "&lt;"), *[f"{int(r.events)}" + (f" (−{int(r.lost_here)})" if r.lost_here else "") for r in rr]))
S += [grid(g, [62, 28, 28, 28, 28]), P("The last row is the ε<sub>reco</sub> numerator; the denominator is the first row (fiducial). Without SCT z smearing most losses are in the hit-multiplicity step; "
                                         "with 580 µm the Δs cut removes most events.", "m")]

# 3 Figure 2
S += [PageBreak(), P("3. Figure 2: angular momentum and quirk separation", "h2")]
S += [P("3.1 Equations used (the paper's model, solved numerically)", "h3"),
      EQ("Eq. 3 (straight string, Nambu–Goto with massive ends):  d(mγ<b>v</b>)/dt = −Λ² [ √(1−v<sub>⊥</sub>²) ŝ + (v<sub>∥</sub>/√(1−v<sub>⊥</sub>²)) <b>v</b><sub>⊥</sub> ] + q <b>v</b> × <b>B</b>"),
      P("with v<sub>∥</sub> = <b>v</b>·ŝ (signed), <b>v</b><sub>⊥</sub> = <b>v</b> − v<sub>∥</sub>ŝ, ŝ the unit vector from the partner to the quirk, T = Λ² the string tension, B = 2 T along z. "
        "Material effects are neglected, as in the paper (“We therefore neglect this effect in our simulations”). Integration: RK4, 3000 steps per period for Fig. 2.", "m"),
      EQ("Eq. 4 (B = 0, one quirk's distance from the CM):  d<sub>cm</sub>(t) = (m/Λ²) [ γ − √(1 + (Λ²t/m − vγ)²) ],  maximum (γ − 1) m/Λ²;  the plotted d = |<b>x</b>₁* − <b>x</b>₂*| = 2 d<sub>cm</sub>"),
      EQ("L = (<b>x</b>₁* − <b>x</b>₂*) × (<b>p</b>₁* − <b>p</b>₂*) / 2  in the initial CM frame at equal CM time;  r = transverse radius of the CM"),
      EQ("Eq. 5 (CM frame):  <b>E</b>* = γ<sub>cm</sub> <b>v</b><sub>cm</sub> × <b>B</b>,  torque  <b>τ</b> = q <b>d</b> × <b>E</b>*  (for charges ±q)")]
S += [P("3.2 Appendix A of arXiv:2002.07503 and what it predicts", "h3"),
      P("Li, Li, Pei and Zhang solve Eq. 3 with a uniform magnetic field analytically in the CM frame. In the time variable g = Λ²t<sub>c</sub>/(2mρ) (ρ = p*/m) the quirks meet "
        "(d = 0) at every integer g, and the motion between meetings is the B = 0 solution r(g) = (m/Λ²)[√(1+ρ²) − √(1+ρ²(1−2g)²)] plus small out-of-plane terms z<sup>±</sup>(g). Appendix A states:", "b")]
S += [P("“the average torque on the system of two quirks is zero when g is increased from 2n to 2n + 2 such that the total angular momentum of the quirk pair is also invariant at g = 2n … "
        "two quirks meet each other and have opposite velocity at g = 2n in the CoM frame.”", "q"), Spacer(1, 2)]
S += [P("Reason: between g = 2n and 2n + 1 quirk 1 is on one side (<b>d</b> along +ŝ), between 2n + 1 and 2n + 2 on the other (<b>d</b> along −ŝ). The electric field <b>E</b>* is constant, "
        "so <b>τ</b> = q<b>d</b>×<b>E</b>* has the same size and opposite sign in the two half-oscillations, and ΔL over a full oscillation vanishes. With L = 0 at production, "
        "|L| is therefore zero at every second meeting (g = 2, 4, …) and equal at every odd meeting. A crossing here means a closest approach, a minimum of d (d → 0 up to "
        "the classical impact parameter).", "b")]
tq = CH["torque_constructed"]
g = [H("Half-oscillation (constructed event, 10¹² ħ)", "1", "2", "3", "4")]
g += [C("change of L along its axis (trajectory)", *[f"{r_[0]:+.3f}" for r_ in tq]), C("EM torque ∫ q<b>d</b>×<b>E</b>* dt (Eq. 5 form)", *[f"{r_[1]:+.3f}" for r_ in tq]),
      C("string term (v<sub>∥</sub>v<sub>⊥</sub> of Eq. 3)", *[f"{r_[2]:+.3f}" for r_ in tq]), C("paper's Fig. 2 (signed, from its curves)", *[f"{x:+.3f}" for x in S2["paper"]["dL_half"]])]
S += [grid(g, [74, 25, 25, 25, 25]), P(f"The string term is part of Eq. 3: at B = 0 the quirks' |L| drops to {CH['B0_turning'][0]:.4f} = 1/γ* at the turning points and returns at the meetings, "
                                         "independently of v<sub>cm</sub> (0, 0.0975, 0.3), and the same 0.643 is obtained when the event is integrated directly in the CM frame (D26, D21).", "m")]
g = [H("Fig. 2 quantity", "Paper", "This work: paper's kinematics (±2/3)", "This work: COL2000 key 8 (±1)")]
pp, cc_, kk = S2["paper"], S2["constructed"], S2["key8"]; f2 = lambda xs: " / ".join(f"{x:.2f}" for x in xs[:4])
g += [C("d max (cm)", f"{pp['dmax']:.2f}", f"{cc_['dmax']:.2f}", f"{kk['dmax']:.2f}"), C("spacing of closest approaches in r (cm)", f"{pp['spacing']:.3f}", f"{cc_['spacing']:.3f}", f"{kk['spacing']:.3f}"),
      C("|L| at closest approaches 1–4 (10¹² ħ)", f2(pp["Lapp"]), f2(cc_["Lapp"]), f2(kk["Lapp"])), C("r where |L| = 0 (cm)", f2(pp["lz"]), f2(cc_["lz"]), f2(kk["lz"]))]
S += [Spacer(1, 3), grid(g, [52, 40, 42, 40]), Spacer(1, 2), img("F38_fig2", 174)]
S += explain([("What it shows", "|L| (top) and the quirk separation d (bottom) versus the radius r of the centre of mass for the paper's event (left), an event built with the paper's kinematics "
               "(middle: v* = 0.556 and β<sub>cm</sub> = 0.0975 read from its d curve) and a simulated event (right). Grey lines mark the closest approaches."),
              ("Mechanism", "d follows Eq. 4: each arch is one half-oscillation, d<sub>max</sub> = 2(γ*−1)m/Λ² = 3.61 cm, and arches repeat every β<sub>cm</sub> × period = 1.16 cm in r. "
               "|L| is the integral of the torque q<b>d</b>×<b>E</b>* (plus the string term): it rises during one arch and is removed during the next, because <b>d</b> reverses. "
               "Hence |L| = 0 at every second closest approach and all peaks are equal — the Appendix A result."),
              ("Comparison", f"The paper's d (d<sub>max</sub> {pp['dmax']:.2f} cm, spacing {pp['spacing']:.3f} cm) and its first |L| maximum ({pp['Lapp'][0]:.3f}) are matched "
               f"({cc_['dmax']:.2f} cm, {cc_['spacing']:.3f} cm, {cc_['Lapp'][0]:.3f}). After that the paper's |L| does not return to zero: its half-oscillations are unequal "
               f"({' / '.join(f'{x:+.2f}' for x in pp['dL_half'])}), and its zeros of |L| lie near the maxima of d."),
              ("Agreement", "Good for d and for the first |L| peak; poor for the later |L| values. The difference is not reproduced by: four definitions of L (CM frame, lab midpoint, lab centre of energy, "
               "production point), 7 charge sets × 5 axes and 60 random configurations, 8 equation-of-motion variants (only a non-energy-conserving forward-Euler integration gives a non-zero "
               "second approach), string direction at equal CM time, an independent code (PreFASERQuirkSim) or the user-supplied simulator after correcting its units."),
              ("Unresolved", "The paper does not state its L definition, the event's charges and momenta or its integrator; these are the questions for the authors.")])
S += [P("3.3 Checks of the Fig. 2 machinery", "h3")]
g = [H("Check", "Result", "Record")]
g += [C("Eq. 3 written literally vs the integrator, 2000 random states", "max difference 7×10⁻¹⁶ Λ²", "D27 (T0 tests)"),
      C("Eq. 4 at B = 0 / energy E₁ + E₂ + Λ²d", "4×10⁻¹¹ of the amplitude / 7×10⁻¹² (median)", "D27"),
      C("Lorentz force and units (gyroradius, p<sub>T</sub> = 50 GeV, 2 T)", "83.391 m expected, within 1.4×10⁻⁵", "D27"),
      C("step size 3000 vs 6000 per period (Fig. 2 event)", "|L| at approaches unchanged to 3×10⁻⁴", "D27"),
      C("closest approaches with |L| &lt; 1% of the event's |L|max, all 22 COL2000 fiducial events", f"{int(FL.n_low_L.sum())} of {int(FL.n_approach.sum())}; every event", "D17"),
      C("independent codes: improved user simulator, PreFASERQuirkSim (CM-time string)", "same pattern; peaks within 0.7%", "D31, D32")]
S += [grid(g, [86, 62, 26])]

# 4 Annihilation
S += [P("4. Annihilation at the |L| ≈ 0 meetings", "h2")]
S += [P("The paper: “whenever |L| = 0, the separation between the quirks is large, and annihilation is suppressed by a small wave-function overlap.” In the classical model "
        "(this work; arXiv:2002.07503, App. A) |L| returns to its production value at every second meeting, where d ≈ 0. This argument is therefore not supported. "
        "This does not show that annihilation occurs; the reasons are separated below by type.", "b")]
lr_ = CH["L_residual"]
g = [H("Type", "Statement", "Basis")]
g += [C("Simulation evidence", f"At the even meetings the classical |L| is below 10⁻⁵ of its peak but not converged: {', '.join(f'{abs(a):.0e}' for _, a, _ in lr_)} ħ at "
        f"{', '.join(str(n) for n, _, _ in lr_)} steps per period (2nd meeting). The classical impact parameter b = |L|/p* stays ≫ 1/m<sub>Q</sub> = 1.1×10⁻¹⁷ cm at every resolution reached, "
        "but whether |L| would reach a few ħ cannot be decided classically.", "D29 (D22 script)"),
      C("Physical argument", "Annihilation needs an S-wave overlap at distances ≈ 1/m<sub>Q</sub>; the per-meeting probability is ≈ (σv)|ψ(0)|² × time. For an S state of V = Λ²r, "
        "|ψ(0)|² = μΛ²/2π (μ = m/2), and one full oscillation lasts 4mγ*v*/Λ², so P per oscillation ≈ c<sub>σ</sub>α²γ*v*, independent of m and Λ: 10⁻⁴–10⁻³ for α = 0.02–0.05.", "D37"),
      C("Physical argument", "The symmetry that returns L to zero is not exact in reality: material (2108.06748 finds that material changes L), radiation of glueballs and photons, "
        "non-uniform field. These are not in the paper's model or ours.", "literature"),
      C("Inherited assumption", "Neither the paper nor this work simulates annihilation; Table I assumes none. arXiv:2404.13814 models annihilation only from the quirkonium ground state "
        "after radiative de-excitation.", "paper; 2404.13814 Sec. 4"),
      C("Quantum test (toy)", "2D Schrödinger evolution of the relative coordinate with V = r − f x: the overlap at the origin returns to the field-free value at the even meetings "
        "(0.98, 0.93 for L<sub>peak</sub> = 10 ħ); the incomplete return at L<sub>peak</sub> = 30 ħ (0.57) is reproduced by a classical ensemble (0.52) and by a finer grid (0.565).", "D37, D38")]
S += [grid(g, [28, 124, 22])]
g = [H("Worst case: S-wave at every second meeting, mean survival", "Λ (keV)", "full oscillations (median)", "σv = πα²/m², α 0.02 / 0.05", "dark gluons (2404.13814), α 0.02 / 0.05")]
for smp, lam in (("COL2000", 2), ("COL2000", 10), ("EW2000", 4), ("EW2000", 5)):
    x = A_[(A_["sample"] == smp) & (A_.lambda_ev == lam * 1000)]; q = lambda sv, al: x[(x.sigma_v == sv) & (x.alpha == al)].survival.mean()
    g.append(C(("colored 1.8 TeV" if smp == "COL2000" else "EW 800 GeV"), str(lam), f"{x.N_osc.median():.0f}", f"{q('c_sigma=1', .02):.3f} / {q('c_sigma=1', .05):.3f}",
               f"{q('dark gluons N_IC=2', .02):.3f} / {q('dark gluons N_IC=2', .05):.3f}"))
S += [Spacer(1, 3), grid(g, [56, 14, 30, 36, 38]), P("Order of magnitude (non-relativistic formula, v* ≈ 0.6); α<sub>dark</sub> is not given by the paper. A worst case, not a prediction: "
                                                       "the loss is small at the benchmarks and grows with Λ (number of oscillations ∝ Λ²).", "m"),
      box("Statement for the record", [P("In the classical straight-string model, |L| returns to its production value at every second meeting (this work; arXiv:2002.07503, App. A), "
          "so the paper's argument that |L| = 0 only at large separation is not supported. Whether this leads to non-negligible annihilation requires a quantum estimate of the "
          "per-meeting annihilation probability, which neither the paper nor this study provides; the worst case above bounds it from above at the Table I benchmarks.", "b")])]

# 5 Figures 3-5
S += [PageBreak(), P("5. Figures 3–5", "h2"), P("Figure 3: rotation of the quirk plane", "h3")]
g = [H("Δφ at r = 15 cm (Λ = 2 keV)", "Events", "median [16–84%]", "Paper's event", "fraction of our events below the paper")]
for s, lab in (("COL2000", "colored 1.8 TeV"), ("EW2000", "EW 800 GeV")):
    v_ = e3.loc[s].values; k = int((v_ < p3end[s]).sum())
    g.append(C(lab, str(len(v_)), f"{np.median(v_)*1e3:.2f} [{np.quantile(v_,.16)*1e3:.2f}, {np.quantile(v_,.84)*1e3:.2f}]×10⁻³", f"{p3end[s]*1e3:.2f}×10⁻³", f"{k}/{len(v_)} = {es(k, len(v_), 2)}"))
S += [grid(g, [40, 14, 52, 26, 42]), Spacer(1, 2), img("F30_fig3", 172)]
S += explain([("What it shows", "The angle Δφ by which the plane of the two quirks' velocity vectors turns, versus r: median of all fiducial events with the 16–84% band; dotted: the paper's event."),
              ("Mechanism", "The torque of Eq. 5 turns the plane, but the moment of inertia I ≈ 2d²m is large, so Δφ ≈ |τ|Δt²/I ≈ 10⁻⁵ v<sub>cm</sub>/v² (paper Eq. 9). Δφ oscillates with "
               "the half-oscillations and accumulates slowly."),
              ("Comparison", "The paper's single event lies inside our distribution (at its low edge for colored)."),
              ("Agreement / limitation", "Good: the paper's event lies within our spread. Δφ describes the plane of the velocity vectors; whether the hits stay coplanar is measured directly by the "
                 "truth plane thickness of the hits (a few µm, Section 6.2). One paper event only; its kinematics are unknown.")])
g = [H("Fig. 4 example (median Δs in the signal region)", "SCT z", "Event", "rank", "Δs", "Δw")]
for sct, zl in (("Z1160", "1.16 mm"), ("Z0", "none")):
    dd = f4[sct][f4[sct].ellipse != True].groupby("sample").first()
    for s in R.SAM:
        r_ = dd.loc[s]; g.append(C(R.SAM[s]["name"], zl, str(int(r_.event_id)), f"{int(r_['rank'])} of {int(r_.n_sr_events)}", f"{r_.ds_cm*1e4:.0f} µm", f"{r_.dw_cm:.3f} cm"))
g.append(C("paper example (colored)", "—", "—", "—", "83 µm", "0.074 cm"))
S += [Spacer(1, 4), P("Figure 4: hits of one signal event in the plane's coordinates", "h3"), grid(g, [62, 20, 20, 24, 22, 26]), Spacer(1, 2), img("F29_fig4_Z0", 150)]
S += explain([("What it shows", "The hits of the signal-region event with the median Δs (no SCT z smearing), projected on the fitted plane (n₃, n₂); dotted ellipses: the layers; zoom: the strip."),
              ("Mechanism", "The two quirks oscillate about the pair's direction n₃; the hits fill a strip of full width ≈ the belt width L of arXiv:2002.07503 Eq. III.1, Δw ≈ L/√12 for a uniform strip."),
              ("Comparison", "Same pattern as the paper's Fig. 4 (hits on a narrow strip along n₃). The paper's example has Δw = 0.074 cm and Δs = 83 µm; ours (fixed median rule) is wider."),
              ("Limitation", "One event per panel, chosen by a fixed rule; with 1.16 mm (F29_fig4_Z1160, previous report) only one colored event passes.")])
S += [Spacer(1, 6), P("Figure 5: Δs and Δw distributions", "h3")]
g = [H("Population", "SCT z", "N", "Δs median", "paper", "Δw median", "paper", "Δs &lt; 0.01 cm: k / N, ε ± σ", "paper")]
for pop, lab in [("colored", "Colored Quirk"), ("EW", "EW Quirk"), ("converted γ + pile-up", "Converted gamma"), ("pile-up", "Pileup")]:
    for sct, zl in (("Z0", "none"), ("Z1160", "1.16 mm")):
        if pop in ("converted γ + pile-up", "pile-up") and sct == "Z0": continue
        x = F5[sct][F5[sct].population == pop]; k, n = int((x.ds < 0.01).sum()), len(x)
        g.append(C(pop, zl if pop in ("colored", "EW") else "580 µm, [34]", str(n), f"{x.ds.median()*1e4:.0f} µm", f"{PM[lab][0]*1e4:.0f} µm", f"{x.dw.median():.3f} cm", f"{PM[lab][1]:.3f} cm",
                   f"{k} / {n} = {es(k, n, 2)}", f"{PAPER_BELOW[lab]:.2f}"))
S += [grid(g, [28, 18, 10, 16, 14, 18, 14, 40, 14]), Spacer(1, 2), img("F30_fig5_Z0", 172)]
S += explain([("What it shows", "Δs (plane thickness) and Δw (strip width) of signal events after the plane and hit cuts (before the Δs cut), and of the backgrounds; unit area; dotted: the paper."),
              ("Mechanism", "The true plane thickness is a few µm (Section 6.2), so Δs is set by the detector resolution: pixel rounding (14–115 µm RMS) and the SCT 34 µm rφ give ≈ 40 µm; "
               "an SCT z smearing of 0.58–1.16 mm adds ≈ 100–200 µm. Δw is set by the oscillation amplitude and the boost (belt width)."),
              ("Comparison", "Without SCT z smearing the signal Δs (38 / 43 µm) is close to the paper's (32 / 28 µm) and nearly all signal lies left of the cut, while backgrounds lie to the right. "
               "Δw is wider than the paper's: colored 5×, EW 2×."),
              ("Agreement / limitation", "Δs: good only without SCT z smearing (with 1.16 mm: F30_fig5_Z1160, ≈ 150 µm). Δw: poor. 8 colored and 50 EW signal events.")])

# 6 width and thickness tests
S += [P("6. Tests of Δw and of the plane thickness", "h2"), P("6.1 Δw (strip width)", "h3")]
dd29 = D29[D29.plane.astype(bool)]
g = [H("Test", "Colored", "EW", "Paper")]
g.append(C("Δw median, production, plane + hit cut (SCT z none)", f"{c[('FIRST','Z0')]['dw_med_cm']:.3f} cm", f"{e[('FIRST','Z0')]['dw_med_cm']:.3f} cm", f"{PM['Colored Quirk'][1]:.3f} / {PM['EW Quirk'][1]:.3f} cm"))
p24 = P24[P24.fid.astype(str) == "True"]; p24z = p24[(p24.sct == "Z0") & (p24.plane_any.astype(str) == "True")]
g.append(C("Δw median, population “plane found”, before the hit and Δs cuts (authors: Fig. 5 is before the Δs and Δw cuts)",
           f"{p24z[p24z['sample']=='COL2000'].dw_any.median():.3f} cm", f"{p24z[p24z['sample']=='EW2000'].dw_any.median():.3f} cm", "—"))
r_c = dd29[dd29["sample"] == "COL2000"]; r_e = dd29[dd29["sample"] == "EW2000"]
g.append(C("belt width L (2002.07503 Eq. III.1), median over fiducial events", f"{D29[D29['sample']=='COL2000'].L_belt_cm.median():.3f} cm", f"{D29[D29['sample']=='EW2000'].L_belt_cm.median():.3f} cm", "—"))
g.append(C("Δw / L (median); uniform strip: 1/√12 = 0.289", f"{np.median(r_c.dw_cm / r_c.L_belt_cm):.3f}", f"{np.median(r_e.dw_cm / r_e.L_belt_cm):.3f}", "—"))
g.append(C("Spearman correlation of Δw with L", f"{r_c[['dw_cm','L_belt_cm']].corr('spearman').iloc[0,1]:.2f}", f"{r_e[['dw_cm','L_belt_cm']].corr('spearman').iloc[0,1]:.2f}", "—"))
dq = D32[(D32.fid_lab == True)]; g.append(C("Δw median, string at equal CM time instead of lab time (D40)", f"{dq[(dq['sample']=='COL2000')].cm_Z0_dw_cm.median():.3f} cm",
                                           f"{dq[(dq['sample']=='EW2000') & (dq.lambda_keV==4)].cm_Z0_dw_cm.median():.3f} cm", "—"))
if D41: g.append(C(f"Δw median, EW LO sample B ({N41} events), Λ = 4 keV, plane found", "—", f"{D41[4]['dw_med_cm']:.3f} cm", "—"))
g.append(C("EW LO sample B, showered without matching", "—", (f"{D41s[4]['dw_med_cm']:.3f} cm" if D41s else "<i>pending</i>"), "—"))
S += [grid(g, [86, 28, 28, 32]), P("Our Δw follows the analytic belt width of our own kinematics (ratio ≈ 1/√12, strong correlation) and does not change with the population, the string convention or the "
                                     "LO sample. The 2–5× difference to the paper is not produced by the reconstruction; its origin (event kinematics or the plotted definition) is open.", "m")]
S += [P("6.2 Plane thickness without detector effects", "h3")]
g = [H("Truth thickness (exact first crossings, no resolution)", "Colored 2 keV", "EW 4 keV")]
for lab, col in (("this work, string at equal lab time (production)", "ds_truth_lab_um"), ("string at equal CM time (paper / 2002.07503 Sec. VIII)", "ds_truth_cm_um")):
    g.append(C(lab, f"{dq[dq['sample']=='COL2000'][col].median():.2f} µm", f"{dq[(dq['sample']=='EW2000') & (dq.lambda_keV==4)][col].median():.2f} µm"))
g.append(C("analytic: 1911.02223 Eq. III.12 / 2002.07503 Eq. V.6", f"{D29[D29['sample']=='COL2000'].d_1911_um.median():.2f} / {D29[D29['sample']=='COL2000'].d_2002_um.median():.2f} µm",
           f"{D29[D29['sample']=='EW2000'].d_1911_um.median():.2f} / {D29[D29['sample']=='EW2000'].d_2002_um.median():.2f} µm"))
S += [grid(g, [92, 41, 41])]
g = [H("Effect of the string convention (D40)", "lab time: ε<sub>reco</sub> (none)", "CM time", "Δs median lab → CM")]
for smp, lam in (("COL2000", 2), ("EW2000", 1), ("EW2000", 2), ("EW2000", 4)):
    x = dq[(dq["sample"] == smp) & (dq.lambda_keV == lam)]; n = len(x)
    g.append(C(f"{'colored' if smp=='COL2000' else 'EW'} {lam} keV", f"{int(x.lab_Z0_final.sum())}/{n} = {es(int(x.lab_Z0_final.sum()), n, 2)}", f"{int(x.cm_Z0_final.sum())}/{n} = {es(int(x.cm_Z0_final.sum()), n, 2)}",
               f"{x[x.lab_Z0_plane == True].lab_Z0_ds_um.median():.1f} → {x[x.cm_Z0_plane == True].cm_Z0_ds_um.median():.1f} µm"))
S += [Spacer(1, 3), grid(g, [44, 46, 46, 38]), P("Our production code takes the string direction at equal lab time; the paper states the straight string in the CM frame. This raises the truth thickness "
                                                   "(EW 13 → 0.6 µm) and lowers the EW Δs without SCT z smearing by 5–9 µm, but changes ε<sub>reco</sub> by at most 2 events. It does not explain the Table I differences.", "m")]

# 7 backgrounds
S += [P("7. Backgrounds and the converted-photon upper limit", "h2")]
g = [H("Sample", "Events", "Plane", "+ hit mult.", "Signal region", "per-event rate")]
for lab, k_ in (("converted γ + μ = 50, SCT z 580 µm (cited model)", "conv580"), ("converted γ + μ = 50, SCT z 1.16 mm, no [34] energy loss", "conv1160"),
                ("converted γ + μ = 50, no SCT z smearing", "conv0")):
    b_ = BG[k_]; g.append(C(lab, str(b_["n"]), str(b_["plane"]), str(b_["mult"]), f"{b_['sr']} / {b_['n']}", es(b_["sr"], b_["n"], 4)))
g.append(C("pile-up only, μ = 50, SCT z 580 µm", "5000", "—", "—", f"{BG['pu580']['sr']} / 5000", es(BG["pu580"]["sr"], 5000, 4)))
g.append(C("pile-up: plane with ≥ 1 hit in ≥ 4 of 8 layers (paper ~10⁻³)", "5000", "", "", f"{BG['pu580']['r4']} / 5000", es(BG["pu580"]["r4"], 5000, 4)))
g.append(C("pile-up: plane with ≥ 1 hit in all 8 layers (paper 6×10⁻⁵)", "5000", "", "", f"{BG['pu580']['r8']} / 5000", es(BG["pu580"]["r8"], 5000, 5)))
S += [grid(g, [74, 14, 14, 16, 26, 30])]
ul = R.ul95(9139); exp = lambda xs: 300 * xs * 1e3 * 0.01
g = [H("Converted photons at 300 fb⁻¹", "σ(Z(νν)γ + j)", "conversions (×1%)", "signal-region fraction", "expected events")]
for lab, xs in (("this work's cross section", 0.211), ("paper's cross section", 1.0)):
    g.append(C(f"{lab}, SCT z 580 µm", f"{xs} pb", f"{exp(xs):.0f}", f"0/9139 → 95% UL {sci(ul)}", f"&lt; {exp(xs) * ul:.2f}"))
    fr = BG["conv0"]["sr"] / 9139; g.append(C(f"{lab}, no SCT z smearing", f"{xs} pb", f"{exp(xs):.0f}", f"{BG['conv0']['sr']}/9139 = {es(BG['conv0']['sr'], 9139, 4)}", f"{exp(xs) * fr:.1f} ± {exp(xs) * R.sig(BG['conv0']['sr'], 9139)[1]:.1f}"))
S += [Spacer(1, 3), grid(g, [56, 24, 26, 40, 28])]
S += [P(f"<b>Why the upper limit is the same for both cross sections.</b> The signal-region fraction is measured per converted photon on the same 9139 simulated events. With 0 passing, its 95% upper limit is "
        f"1 − 0.05<super>1/9139</super> = {sci(ul)}, which depends only on the number of simulated events. The cross section enters only the next step, the expected number of conversions "
        f"(300 fb⁻¹ × σ × 1%): {exp(0.211):.0f} or {exp(1.0):.0f}, hence &lt; {exp(0.211)*ul:.2f} or &lt; {exp(1.0)*ul:.2f} events. If the background is simulated without SCT z smearing, "
        f"{BG['conv0']['sr']} conversions pass and the expected number becomes {exp(0.211)*BG['conv0']['sr']/9139:.0f}–{exp(1.0)*BG['conv0']['sr']/9139:.0f} events: the zero-background statement "
        "relies on the SCT z smearing of the background, which is the setting the signal efficiencies do not tolerate.", "b")]

# 8 investigation record
S += [P("8. Investigation record since 9 October", "h2")]
g = [H("Record", "Question", "Result", "Status")]
for r in [("D14", "are 300 RK4 steps per period enough?", "hit positions not converged (median shift 0.4–0.6 mm vs 6000); signal-region counts change by ±1 (EW: 7 events flip both ways)", "accepted; listed as numerical uncertainty"),
          ("D17–D28", "why the paper's Fig. 2 |L| differs", "L definition, charges, axes, EOM variants, two independent codes, B = 0 test, CM-frame integration: our pattern is the solution of Eq. 3", "verified; paper's curve unexplained"),
          ("D27", "are the equations implemented as written?", "Eq. 3, Lorentz force, units, Eq. 4, energy: agreement 10⁻¹⁶–10⁻⁵", "verified"),
          ("D29, D37–D38", "annihilation at |L| ≈ 0", "classical |L| at even meetings &lt; 10⁻⁵ of the peak (not converged); worst case small at the benchmarks; quantum toy follows the classical return", "open (needs a quantum estimate)"),
          ("D33–D34", "literature (Setford thesis; 2002.07503; 2404.13814; 2108.06748; 1911.02223)", "material neglected in the paper; App. A of 2002.07503 = our Fig. 2; EW trigger 0.10 = LO ratio (1911.02223)", "integrated"),
          ("D35–D36", "settings, model, tests", "colored quirk is a fermion; config files with strict checks; 6 physics tests pass; outputs unchanged (byte-identical)", "done"),
          ("D38", "repeated crossings", f"{c['multi_cross']}/22 colored and {e['multi_cross']}/62 EW fiducial events have &gt; 2 hits on a layer (paper: “most likely … only once”)", "verified"),
          ("D39–D40", "string direction at equal CM time", "truth thickness EW 13 → 0.6 µm; ε<sub>reco</sub> within ±2 events", "verified; modelling approximation listed"),
          ("D41", "EW sample as LO QQ̄ + 1 jet", f"ε<sub>trig</sub> 0.096 (= paper 0.10), ε<sub>fid</sub> {d4['fid']/N41:.3f} (paper 0.28); ε<sub>reco</sub> unchanged",
           "running" if not FINAL41 else "complete (showered: " + ("done" if D41s else "pending") + ")")]:
    g.append(C(*r))
S += [grid(g, [16, 40, 86, 32])]

# 9 unresolved
S += [P("9. Unresolved differences and next steps", "h2")]
x2 = LS[(LS["sample"] == "EW2000") & (LS["mode"] == "FIRST") & (LS.sct == "Z0") & (LS.lambda_keV == 2)].iloc[0]
S += B([f"<b>EW ε<sub>reco</sub> at Λ = 1–2 keV</b> above the paper (2 keV: production {es(int(x2.k_ge2), int(x2.n_fid), 2)}, LO {es(D41[2]['sr'], D41[2]['fid'], 2)}, paper 0.41). Not removed by the LO sample, "
        "the string convention or the step size.",
        "<b>SCT z resolution.</b> The authors' stated resolution (580 µm) gives ε<sub>reco</sub> far below Table I; only no smearing reproduces it. Question for the authors: which coordinate and value.",
        "<b>Signal Δw</b> 2× (EW) and 5× (colored) the paper's; our Δw follows the analytic belt width of our kinematics.",
        "<b>Fig. 2</b>: the paper's unequal half-oscillations; questions: L frame and point, whether L includes the string's share, the event's charges and momenta.",
        "<b>Annihilation</b>: a quantum per-meeting estimate is needed to turn the worst case into a number.",
        "<b>Next:</b> finish D41 (3000 events) and its showered sensitivity; ask the authors; pile-up 4-of-8 plane rate (6.6×10⁻³ vs ~10⁻³) remains open."])

# 10 provenance and references
S += [P("10. Provenance", "h2")]
g = [H("Result", "Data file(s)", "Script")]
for r in [("production counts, Table I", "tables/all_crossings_per_event.csv; quirk_2000_event_fresh_regeneration_v1/events/*/matched_events_full.csv", "P18_all_crossings.py"),
          ("Λ column", "tables/lambda_scan_summary.csv, lambda_scan_z1160_summary.csv", "P20_lambda_scan.py, P20b"),
          ("EW LO trigger and sample B", "inputs_D41/ (MG5 logs, banners, LHE, shower CSV); logs/D41_mg5_373_lo_events.jsonl", "D41_ew_lo_ratio_pipeline.py"),
          ("backgrounds", "logs/P10_chunks_*, P21_chunks_REF34_Z580, P8_chunks_LITERAL", "P10, P21"),
          ("Fig. 2", "tables/fig2_final/*.csv; tables/D16–D22, D17_fig2_torque_decomposition.txt", "F38_report_2026_10_15_figs.py; D16–D25"),
          ("Fig. 3, 4, 5", "FINAL_FIGURES/F30_fig3, F29_fig4_*, F30_fig5_* (source CSVs); tables/paper_fig5_vector.json", "F30_report_figs.py, F29"),
          ("annihilation", "tables/D27_annihilation_A.csv, D27/D28 txt, D22 txt", "D27, D28, D22"),
          ("width / thickness", "tables/D29_li_pei_formulas.csv, D32_cm_time_string_reco.csv, fig5_author_population.csv", "D29, D32, P24"),
          ("all numbers of this report", "—", "R_data_2026_10_15.py (assertions), R_report_2026-10-15.py")]:
    g.append(C(*r))
S += [grid(g, [36, 96, 42]), P("Settings: config/detector.yaml, reconstruction.yaml, benchmarks.yaml (checked by T1_config_check.py); physics tests T0_physics_tests.py. Decision log entries D17–D41.", "m")]
S += [P("References", "h3")] + [P(x, "c") for x in [
    "[paper] S. Knapen, H. K. Lou, M. Papucci, J. Setford, Phys. Rev. D 96, 115015 (2017), arXiv:1708.02243; J. Setford, PhD thesis, Univ. of Sussex (2018), Ch. 5.",
    "[27] ATLAS, “The Expected Performance of the ATLAS Inner Detector”, ATL-PHYS-PUB-2009-002.   [34] S. Knapen, S. Pagan Griso, M. Papucci, D. J. Robinson, arXiv:1612.00850, App. A.",
    "J. Li, T. Li, J. Pei, W. Zhang, “The quirk trajectory”, Eur. Phys. J. C (2020), arXiv:2002.07503 (Appendix A: L invariant at every second meeting; Sec. VIII: CM-time string).",
    "J. Li, T. Li, J. Pei, W. Zhang, “Uncovering quirk signal via energy loss inside tracker”, arXiv:1911.02223 (App. A: EW trigger efficiency 0.1 as an LO ratio).",
    "J. Li, J. Pei, L. Ran, W. Zhang, “The quirk signal at FASER and FASER 2”, JHEP 12 (2021) 109, arXiv:2108.06748 (torque over a full oscillation; material).",
    "J. L. Feng, J. Li, X. Liao, J. Ni, J. Pei, arXiv:2404.13814 (annihilation from the ground state); code PreFASERQuirkSim (github.com/eliwelch17/PreFASERQuirkSim).",
    "J. Kang, M. A. Luty, JHEP 11 (2009) 065, arXiv:0805.4642.   MadGraph5_aMC@NLO: J. Alwall et al., JHEP 07 (2014) 079.   Pythia 8: C. Bierlich et al., SciPost Phys. Codeb. 8 (2022)."]]

def deco(cv_, d):
    cv_.saveState(); cv_.setFont("DV", 7.3); cv_.setFillColor(MUTED)
    cv_.drawString(18 * mm, 10 * mm, "Reproduction of Table I of arXiv:1708.02243 · update of 15 October 2026" + ("" if FINAL41 else f" · D41 provisional ({N41}/3000 events)"))
    cv_.drawRightString(192 * mm, 10 * mm, f"{d.page}"); cv_.restoreState()
doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=14 * mm, bottomMargin=16 * mm, title="Reproduction of Table I of arXiv:1708.02243 — update", author="")
doc.addPageTemplates([PageTemplate("p", [Frame(18 * mm, 16 * mm, 174 * mm, 267 * mm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=deco)])
doc.build(S); print("wrote", OUT, "| D41 events", N41)
