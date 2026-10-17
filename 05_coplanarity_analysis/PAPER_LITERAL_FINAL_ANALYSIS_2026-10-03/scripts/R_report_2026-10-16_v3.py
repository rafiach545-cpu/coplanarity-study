#!/usr/bin/env python3
"""TABLE_I_REPRODUCTION_REPORT_2026-10-16.pdf: v2 (2026-10-15) plus, on request of 2026-10-16: coloured headings and key boxes, Table I cut-flow at every
Lambda for both benchmarks, Fig. 3 Delta_phi table, background cut-flow (pass / fail), two annihilation points (classical L vs impact parameter;
return of L is not annihilation). No 580 um, no quantum toy. Numbers from R_data_2026_10_15 (assertions). Uncertainty sigma = sqrt(e(1-e)/n).
Decision rule: "consistent" if |eps - paper| <= 2 sigma_0, sigma_0 = sqrt(p(1-p)/n) with the paper value p and our n; cross-checked against the
Wilson 95% interval (any disagreement is printed when the report is built)."""
import os, sys, json, subprocess
import numpy as np, pandas as pd
from scipy import stats
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import R_data_2026_10_15 as R
if not os.environ.get("D41_NMAX"): os.environ["D41_NMAX"] = str(R.d41()["n"])
subprocess.run([sys.executable, f"{HERE}/F38_report_2026_10_15_figs.py"], check=True, env=os.environ, capture_output=True)
OUT = f"{R.L_}/TABLE_I_REPRODUCTION_REPORT_2026-10-16.pdf"; FIG = R.FIG; T = R.T
F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", F + "DejaVuSans.ttf")); pdfmetrics.registerFont(TTFont("DVB", F + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVO", F + "DejaVuSans.ttf")); registerFontFamily("DV", normal="DV", bold="DVB", italic="DVO", boldItalic="DVB")
INK, MUTED, RULE, HEAD = colors.HexColor("#1b2328"), colors.HexColor("#5b6770"), colors.HexColor("#d5dbde"), colors.HexColor("#eef1f2")
OKB, BADB, NOTE = colors.HexColor("#e2f2e8"), colors.HexColor("#f9e3e1"), colors.HexColor("#edf3f6")
ACC, ACCL, KEYB, KEYL = colors.HexColor("#1f5f8b"), colors.HexColor("#e3edf5"), colors.HexColor("#fff4dc"), colors.HexColor("#d8930f")
HEAD = colors.HexColor("#dbe7f0")
st = {"h1": ParagraphStyle("h1", fontName="DVB", fontSize=15, leading=19, textColor=ACC, spaceAfter=3),
      "h2": ParagraphStyle("h2", fontName="DVB", fontSize=11.5, leading=14, textColor=ACC, backColor=ACCL, borderPadding=(3, 4, 3, 4), spaceBefore=10, spaceAfter=6),
      "h3": ParagraphStyle("h3", fontName="DVB", fontSize=9.6, leading=12, textColor=ACC, spaceBefore=5, spaceAfter=2),
      "b": ParagraphStyle("b", fontName="DV", fontSize=8.8, leading=12, textColor=INK),
      "m": ParagraphStyle("m", fontName="DV", fontSize=7.6, leading=10, textColor=MUTED),
      "c": ParagraphStyle("c", fontName="DV", fontSize=7.6, leading=9.6, textColor=INK),
      "ch": ParagraphStyle("ch", fontName="DVB", fontSize=7.2, leading=9, textColor=INK),
      "eq": ParagraphStyle("eq", fontName="DV", fontSize=8.6, leading=12, textColor=INK, leftIndent=12),
      "q": ParagraphStyle("q", fontName="DVO", fontSize=8.2, leading=10.8, textColor=INK, leftIndent=8),
      "bl": ParagraphStyle("bl", fontName="DV", fontSize=8.6, leading=11.4, textColor=INK, leftIndent=9, bulletIndent=0)}
P = lambda t, s="b": Paragraph(t, st[s]); EQ = lambda t: P(t, "eq")
B = lambda xs: [Paragraph(x, st["bl"], bulletText="•") for x in xs]
H = lambda *xs: [P(x, "ch") for x in xs]
C = lambda *xs: [x if not isinstance(x, str) else P(x, "c") for x in xs]
def grid(data, widths, extra=()):
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HEAD), ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE), ("BOX", (0, 0), (-1, -1), 0.6, RULE),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                           ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)] + list(extra))); return t
def img(name, w):
    from reportlab.lib.utils import ImageReader
    p = f"{FIG}/{name}/{name}.png"; iw, ih = ImageReader(p).getSize(); return Image(p, width=w * mm, height=w * mm * ih / iw)
def key(text):
    """highlighted key message (What we learn / Answer / Conclusion)"""
    t = Table([[P(text)]], colWidths=[174 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), KEYB), ("LINEBEFORE", (0, 0), (0, -1), 3, KEYL), ("LEFTPADDING", (0, 0), (-1, -1), 7),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)])); return t
def box(title, items):
    t = Table([[[P(f"<b>{title}</b>")] + items]], colWidths=[174 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NOTE), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)])); return t
def es(k, n, d=2):
    e = k / n; return f"{e:.{d}f} ± {np.sqrt(e * (1 - e) / n):.{d}f}"
def sci(x, d=1):
    """4.2e+08 -> 4.2×10<super>8</super>"""
    m, ex_ = f"{x:.{d}e}".split("e"); return f"{m}×10<super>{int(ex_)}</super>"
WIL = []
def dec(k, n, p):
    """consistent if |k/n - p| <= 2 sqrt(p(1-p)/n); cross-check with Wilson 95%"""
    ok = abs(k / n - p) <= 2 * np.sqrt(p * (1 - p) / n); lo, hi = stats.binomtest(int(k), int(n)).proportion_ci(0.95, "wilson")
    if ok != (lo <= p <= hi): WIL.append((k, n, p, ok, round(lo, 3), round(hi, 3)))
    return ok
def cell(k, n, p):
    ok = dec(k, n, p); return P(("consistent" if ok else "<b>inconsistent</b>"), "c"), (OKB if ok else BADB)

CNT = R.production(); BG = R.backgrounds(); LT = R.lo_trigger(); D41 = R.d41(); S2 = R.fig2()[0]; CH = R.checks(); LS = R.lambda_scan()
N41 = D41["n"]; c, e = CNT["COL2000"], CNT["EW2000"]
V5 = json.load(open(f"{T}/paper_fig5_vector.json"))
def pmed(b):
    lo = np.array([x["lo"] for x in b]); hi = np.array([x["hi"] for x in b]); h = np.array([x["height"] for x in b]); cc = np.cumsum(h) / h.sum(); i = int(np.searchsorted(cc, 0.5))
    f = (0.5 - (cc[i - 1] if i else 0)) / (cc[i] - (cc[i - 1] if i else 0)); return 10 ** (np.log10(lo[i]) + f * np.log10(hi[i] / lo[i]))
PM = {lab: (pmed(V5["delta_s_cm"]["histograms"][lab]), pmed(V5["delta_w_cm"]["histograms"][lab])) for lab in V5["delta_s_cm"]["histograms"]}
PBELOW = {lab: sum(b["height"] for b in V5["delta_s_cm"]["histograms"][lab] if b["hi"] <= 0.0101) / sum(b["height"] for b in V5["delta_s_cm"]["histograms"][lab]) for lab in V5["delta_s_cm"]["histograms"]}
F5 = {sct: pd.read_csv(f"{FIG}/F40_fig5_{sct}/F40_fig5_{sct}_source.csv").dropna(subset=["ds"]) for sct in ("Z1160", "Z0")}
f4 = {sct: pd.read_csv(f"{FIG}/F29_fig4_{sct}/F29_fig4_{sct}_source.csv") for sct in ("Z1160", "Z0")}

def surv(smp, lev):
    rows = [l.split() for l in open(f"{T}/D27_annihilation_B.txt") if l.split()[:2] == [smp, str(lev)] and "c_sigma=1" in l]
    v = {r[3]: float(r[-2]) for r in rows}; return f"{v['0.02']:.3f} / {v['0.05']:.3f}"
def bad(s_, lams, sct):
    out = []
    for lam in lams:
        r = LS[(LS["sample"] == s_) & (LS.lambda_keV == lam) & (LS.sct == sct) & (LS["mode"] == "FIRST")].iloc[0]
        if not dec(int(r.k_ge2), int(r.n_fid), float(r.paper_reco)): out.append(str(lam))
    return out
def learn():
    t = []
    for s_, nm, lams in (("COL2000", "Colored", (1, 2, 3, 5, 10)), ("EW2000", "EW", (1, 2, 3, 4, 5))):
        b0, b1 = bad(s_, lams, "Z0"), bad(s_, lams, "Z1160")
        z0 = f"consistent at every Λ" if not b0 else f"inconsistent at Λ = {', '.join(b0)} keV (higher than the paper), consistent elsewhere"
        z1 = "consistent at every Λ" if not b1 else ("inconsistent at every Λ" if len(b1) == len(lams) else f"inconsistent at Λ = {', '.join(b1)} keV")
        t.append(f"{nm}: no smearing {z0}; 1.16 mm {z1}.")
    return " ".join(t)
S = [P("Reproduction of Table I of arXiv:1708.02243", "h1"),
     P(f"Knapen, Lou, Papucci, Setford, Phys. Rev. D 96, 115015 (2017) · 16 October 2026 · production samples 2000 events each · EW LO sample: first {N41} of 3000 events (run in progress)", "m"), Spacer(1, 4)]
# questions first
S += [box("Questions to answer", B([
    "<b>Q1. Why is the converted-photon upper limit the same for both cross sections?</b> → Section 7.",
    "<b>Q2. Figure 2: why does our |L| go to zero at every second meeting while the paper's does not?</b> → Section 3 (with Appendix A of arXiv:2002.07503).",
    "<b>Q3. Which smearing was applied, and how?</b> → Section 1.",
    "<b>Q4. Which uncertainties are quoted?</b> → Section 1 (formula) and every table (k/n = ε ± σ)."]))]

# 1 smearing + uncertainty
S += [P("1. How the hits are smeared, and the uncertainty used", "h2")]
g = [H("Detector part", "Formula applied to the true crossing point", "Value")]
g += [C("Pixel layers (4)", "hit moved to the centre of its pixel:  x<sub>meas</sub> = p · round(x / p)", "p = 50 µm (rφ); 250 µm (IBL z), 400 µm (other z)"),
      C("SCT layers (4), rφ", "(rφ)<sub>meas</sub> = rφ + σ<sub>rφ</sub> · g,   g = Gaussian random number (mean 0, width 1)", "σ<sub>rφ</sub> = 34 µm (2 × 17 µm)"),
      C("SCT layers (4), z", "z<sub>meas</sub> = z + σ<sub>z</sub> · g", "σ<sub>z</sub> = 0 (“no smearing”) or 1.16 mm (2 × 580 µm)"),
      C("Beam spot", "all hits of an event shifted by the same z<sub>0</sub>,  z<sub>0</sub> = 45 mm · g", "45 mm"),
      C("Neighbouring pixels", "hits in adjacent pixels of one layer merged into one hit", "—")]
S += [grid(g, [32, 92, 50]), P("Pixel rounding gives an RMS error p/√12 (14 µm for 50 µm, 115 µm for 400 µm). Everything is from the paper (Sec. III A) and Ref. [27], "
                                 "except σ<sub>z</sub> = 0 (our choice: it is the only value that reproduces the paper's numbers) and one common z<sub>0</sub> per event (our reading).", "m")]
S += [EQ("Uncertainty of an efficiency ε = k / n:   σ = √( ε (1 − ε) / n )      (statistical only)"),
      EQ("Decision:  <b>consistent</b> with the paper if |ε − ε<sub>paper</sub>| ≤ 2 σ<sub>0</sub>,  σ<sub>0</sub> = √( ε<sub>paper</sub> (1 − ε<sub>paper</sub>) / n )")]

# 2 Table I
S += [P("2. Table I", "h2"), P("2.1 Efficiencies at every Λ", "h3")]
def tableI(s, lams, nm):
    C_ = CNT[s]; pv = R.SAM[s]["paper"]; n_trig = C_["charged"]
    g = [H("Λ (keV)", f"ε<sub>trig</sub> = N(p<sub>T</sub>(QQ̄) &gt; 200 GeV) / N(matched)", f"ε<sub>fid</sub> = N(fiducial) / N({'trig., both charged' if s == 'COL2000' else 'trig.'})",
           "ε<sub>reco</sub> = N(signal region) / N(fiducial), no smearing", "paper ε<sub>reco</sub>", "decision", "ε<sub>reco</sub>, SCT z 1.16 mm", "decision")]
    ex = []; tk, tn = C_["trig"], C_["matched"]
    for i, lam in enumerate(lams, 1):
        r0 = LS[(LS["sample"] == s) & (LS.lambda_keV == lam) & (LS.sct == "Z0") & (LS["mode"] == "FIRST")].iloc[0]
        r1 = LS[(LS["sample"] == s) & (LS.lambda_keV == lam) & (LS.sct == "Z1160") & (LS["mode"] == "FIRST")].iloc[0]
        k0, n0, k1 = int(r0.k_ge2), int(r0.n_fid), int(r1.k_ge2); p = float(r0.paper_reco)
        d0, b0 = cell(k0, n0, p); d1, b1 = cell(k1, int(r1.n_fid), p)
        g.append(C(str(lam), f"{tk}/{tn} = {es(tk, tn)}" if i == 1 else "same", f"{n0}/{n_trig} = {es(n0, n_trig)}", f"{k0}/{n0} = {es(k0, n0)}", f"{p:.3g}", d0, f"{k1}/{int(r1.n_fid)} = {es(k1, int(r1.n_fid))}", d1))
        ex += [("BACKGROUND", (5, i), (5, i), b0), ("BACKGROUND", (7, i), (7, i), b1)]
    dt, bt = cell(tk, tn, pv["trig"]); df, bf = cell(C_["fid"], n_trig, pv["fid"])
    g.append(C("paper", f"{pv['trig']:.2f} → {'consistent' if dec(tk, tn, pv['trig']) else 'inconsistent'}", f"{pv['fid']:.2f} → {'consistent' if dec(C_['fid'], n_trig, pv['fid']) else 'inconsistent'}", "", "", "", "", ""))
    return [P(nm, "c"), grid(g, [10, 24, 25, 30, 13, 22, 28, 22], ex)]
S += tableI("COL2000", (1, 2, 3, 5, 10), "<b>Colored quirk, m = 1800 GeV</b> (2000 events generated, 873 after matching)")
S += [Spacer(1, 3)] + tableI("EW2000", (1, 2, 3, 4, 5), "<b>EW quirk, m = 800 GeV</b> (2000 events generated, 1045 after matching)")
S += [Spacer(1, 3), img("F38_lambda", 160),
      key("<b>What we learn.</b> " + learn() + " The SCT z smearing decides the result: without it our ε<sub>reco</sub> is close to the paper, with the paper's 1.16 mm it is far below.")]
# 2.2 cut-flow at every Lambda
PE = {"Z0": pd.read_csv(f"{T}/lambda_scan_per_event.csv"), "Z1160": pd.read_csv(f"{T}/lambda_scan_z1160_per_event.csv")}
def flow(s_, lam, sct):
    x = PE[sct]; x = x[(x["sample"] == s_) & (x.lambda_keV == lam) & (x["mode"] == "FIRST") & (x.sct == sct)]; f = x[x.fid.astype(str) == "True"]
    tr = lambda c: f[c].astype(str) == "True"
    o = dict(fid=len(f), plane=int(tr("plane").sum()), mult=int((tr("plane") & tr("mult")).sum()), sr=int(tr("final").sum()))
    r = LS[(LS["sample"] == s_) & (LS.lambda_keV == lam) & (LS.sct == sct) & (LS["mode"] == "FIRST")].iloc[0]
    assert (o["fid"], o["sr"]) == (int(r.n_fid), int(r.k_ge2)), (s_, lam, sct, o); return o
def cutflow(s_, lams, nm):
    C_ = CNT[s_]; pv = R.SAM[s_]["paper"]; ntr = C_["charged"]; et = C_["trig"] / C_["matched"]
    h1 = [P("Λ (keV) →", "ch")] + sum([[P(f"<b>{l}</b>", "ch"), ""] for l in lams], [])
    h2 = [P("step ↓ / SCT z →", "ch")] + [P(z, "ch") for _ in lams for z in ("none", "1.16")]
    F_ = {(l, z): flow(s_, l, z) for l in lams for z in ("Z0", "Z1160")}
    row = lambda lab, f: C(lab, *[f(F_[(l, z)], l) for l in lams for z in ("Z0", "Z1160")])
    g = [h1, h2,
         row("fiducial (both quirks cross all 8 layers, t &lt; 25 ns)", lambda o, l: str(o["fid"])),
         row("plane found (Δw &lt; 1 cm)", lambda o, l: str(o["plane"])),
         row("+ hit multiplicity (2 hits in 7 layers, ≥ 1 in 8th)", lambda o, l: str(o["mult"])),
         row("<b>+ Δs &lt; 0.01 cm = signal region (pass)</b>", lambda o, l: f"<b>{o['sr']}</b>"),
         row("fail (fiducial − pass)", lambda o, l: str(o["fid"] - o["sr"])),
         row("ε<sub>reco</sub> = pass / fiducial", lambda o, l: f"{o['sr']/o['fid']:.2f}"),
         row("<b>ε = ε<sub>trig</sub> · ε<sub>fid</sub> · ε<sub>reco</sub></b> (Eq. 12), ×10⁻²", lambda o, l: f"<b>{100*et*o['fid']/ntr*o['sr']/o['fid']:.2f}</b>"),
         C("paper ε ×10⁻² (= paper ε<sub>trig</sub>·ε<sub>fid</sub>·ε<sub>reco</sub>)", *sum([[f"{100*pv['trig']*pv['fid']*PAPER_R[s_][l]:.2f}", ""] for l in lams], []))]
    ex = [("SPAN", (1 + 2 * i, 0), (2 + 2 * i, 0)) for i in range(len(lams))] + [("SPAN", (1 + 2 * i, 9), (2 + 2 * i, 9)) for i in range(len(lams))]
    ex += [("BACKGROUND", (0, 1), (-1, 1), HEAD), ("ALIGN", (1, 0), (-1, -1), "CENTER"), ("BACKGROUND", (0, 5), (-1, 5), KEYB), ("BACKGROUND", (0, 8), (-1, 8), KEYB)]
    ex += [("LINEBEFORE", (1 + 2 * i, 0), (1 + 2 * i, -1), 0.8, ACC) for i in range(len(lams))]
    return [P(f"{nm}: matched {C_['matched']} → triggered {C_['trig']}" + (f" → both charged {ntr}" if s_ == "COL2000" else "") + " (same for every Λ).", "c"),
            grid(g, [54] + [12] * (2 * len(lams)), ex)]
PAPER_R = R.PAPER_L
S += [P("2.2 Event counts at every Λ (cut-flow, first crossing)", "h3")]
S += cutflow("COL2000", (1, 2, 3, 5, 10), "<b>Colored 1800 GeV</b>") + [Spacer(1, 4)] + cutflow("EW2000", (1, 2, 3, 4, 5), "<b>EW 800 GeV</b>")
S += [P("“none” = no SCT z smearing, “1.16” = SCT z 1.16 mm. ε<sub>fid</sub> = fiducial / " + f"{c['charged']} (colored, both charged) or {e['charged']} (EW). "
        "The paper does not quote ε; its value here is the product of its Table I entries.", "m"),
      P("2.3 EW trigger with the LO sample", "h3")]
lt, lt2, lc = LT[("3.7.3", "EW")], LT[("2.3.3", "EW")], LT[("3.7.3", "COL")]
g = [H("EW sample", "ε<sub>trig</sub>", "ε<sub>fid</sub> (4 keV)", "ε<sub>reco</sub> at 1 / 2 / 3 / 4 / 5 keV (no smearing)")]
g.append(C("Production: MadGraph + Pythia, matched, showered", es(e["trig"], e["matched"], 3), es(e["fid"], e["charged"], 3),
           " / ".join(f"{int(LS[(LS['sample']=='EW2000')&(LS.lambda_keV==l)&(LS.sct=='Z0')&(LS['mode']=='FIRST')].k_ge2.iloc[0])/int(LS[(LS['sample']=='EW2000')&(LS.lambda_keV==l)&(LS.sct=='Z0')&(LS['mode']=='FIRST')].n_fid.iloc[0]):.2f}" for l in (1, 2, 3, 4, 5))))
g.append(C(f"LO, no shower: QQ̄ + 1 jet with p<sub>T</sub>(j) &gt; 200 GeV ({N41} events)", f"{lt['r']:.3f} ± {lt['dr']:.3f} (= σ(QQ̄j)/σ(QQ̄); MG5 2.3.3: {lt2['r']:.3f})",
           es(D41[4]["fid"], N41, 3), " / ".join(f"{D41[l]['sr'] / D41[l]['fid']:.2f}" for l in (1, 2, 3, 4, 5))))
g.append(C("Paper", "0.10", "0.28", "0.11 / 0.41 / 0.65 / 0.72 / 0.74"))
S += [Spacer(1, 4), grid(g, [62, 40, 24, 48]),
      P(f"With the LO sample the EW trigger (0.096) and fiducial ({D41[4]['fid']/N41:.2f}) efficiencies match the paper; the reconstruction efficiency does not change. "
        f"For colored, the same LO ratio gives {lc['r']:.2f} (paper 0.24), and the matched sample matches (0.24).", "m"),]

# 3 Figure 2
S += [P("3. Figure 2 and Appendix A of arXiv:2002.07503", "h2"), P("<b>Equations used</b> (the paper's model, solved numerically):", "b"),
      EQ("Eq. 3:  d(mγ<b>v</b>)/dt = −Λ² [ √(1−v<sub>⊥</sub>²) ŝ + (v<sub>∥</sub>/√(1−v<sub>⊥</sub>²)) <b>v</b><sub>⊥</sub> ] + q <b>v</b> × <b>B</b>     (string + magnetic force)"),
      EQ("L = (<b>x</b>₁ − <b>x</b>₂) × (<b>p</b>₁ − <b>p</b>₂) / 2  in the pair's rest frame;   d = |<b>x</b>₁ − <b>x</b>₂|;   r = distance of the pair's centre from the beam"),
      EQ("Eq. 5:  in the pair's rest frame the magnetic field acts as an electric field <b>E</b>* = γ<sub>cm</sub> <b>v</b><sub>cm</sub> × <b>B</b>;  torque  <b>τ</b> = q <b>d</b> × <b>E</b>*"),
      Spacer(1, 3), P("<b>What Appendix A of arXiv:2002.07503 shows</b> (Li, Li, Pei, Zhang, “The quirk trajectory”, same equation, uniform magnetic field):", "b")]
S += B(["Eqs. (II.11)–(II.14): in the pair's rest frame the two quirks move back and forth on one line and meet at every integer g (g = Λ²t/(2mρ) is the time in units of half an oscillation).",
        "Text after Eq. (A.4): “the average torque on the system of two quirks is zero when g is increased from 2n to 2n + 2 such that the total angular momentum of the quirk pair is also invariant at g = 2n”.",
        "Eq. (A.5): z₁(2n) = −z₂(2n) = 0, i.e. at every second meeting the quirks meet head-on, as at production."])
S += [key("<b>Why.</b> Between two meetings the separation <b>d</b> points one way, in the next half-oscillation the other way. The field <b>E</b>* is constant, so the torque q<b>d</b>×<b>E</b>* "
        "has the same size and the opposite sign in the two halves: L goes up, then back to zero. Our simulation shows exactly this.")]
tq = CH["torque_constructed"]
g = [H("Change of L in each half-oscillation (event with the paper's kinematics, units 10¹² ħ)", "1st", "2nd", "3rd", "4th")]
g += [C("total change of L in our simulation", *[f"{r_[0]:+.2f}" for r_ in tq]),
      C("   from the magnetic force (torque q<b>d</b>×<b>E</b>*)", *[f"{r_[1]:+.2f}" for r_ in tq]),
      C("   from the string's own term in Eq. 3", *[f"{r_[2]:+.2f}" for r_ in tq]),
      C("<b>paper's Fig. 2</b> (read from its curves)", *[f"<b>{x:+.2f}</b>" for x in S2["paper"]["dL_half"]])]
S += [grid(g, [102, 18, 18, 18, 18]), P("In our simulation each half-oscillation adds or removes the same amount (±0.64), so L returns to zero after every two halves. "
                                          "In the paper the halves are unequal (+0.65, −0.84, +0.71, −0.80), so L never returns to zero at a meeting.", "m")]
pp, cc_, kk = S2["paper"], S2["constructed"], S2["key8"]; f2 = lambda xs: " / ".join(f"{x:.2f}" for x in xs[:4])
g = [H("Fig. 2 value", "Paper (arXiv:1708.02243)", "This work: event with the paper's kinematics¹", "This work: one event of our sample²")]
g += [C("largest separation d (cm)", f"{pp['dmax']:.2f}", f"{cc_['dmax']:.2f}", f"{kk['dmax']:.2f}"),
      C("distance in r between meetings (cm)", f"{pp['spacing']:.2f}", f"{cc_['spacing']:.2f}", f"{kk['spacing']:.2f}"),
      C("|L| at meetings 1–4 (10¹² ħ)", f2(pp["Lapp"]), f2(cc_["Lapp"]), f2(kk["Lapp"])),
      C("match with the paper", "—", "d and first |L|: yes; later |L|: no", "pattern as in the middle column")]
S += [Spacer(1, 3), grid(g, [44, 40, 48, 42]),
      P("¹ v* = 0.556 and centre speed 0.0975 c, read from the paper's d curve; charges ±2/3.  ² Event no. 8 of our colored sample (MadGraph + Pythia), chosen because its d curve is the "
        "closest to the paper's; charges ±1.", "m"), Spacer(1, 2), img("F39_fig2_combined", 174),
      key("<b>Conclusion.</b> Our Fig. 2 is what the paper's own equation gives; the same result is found analytically in arXiv:2002.07503 (Appendix A) and with an independent code. "
        "The paper's later |L| values cannot be obtained from its stated equation; the paper does not give the event's charges and momenta or how L was computed.")]

# 4 annihilation
LR = CH["L_residual"]; HBC = 1.973e-14; PST = 1204.1; INV_M = HBC / 1800   # hbar*c in GeV cm; p* (GeV) and 1/m_Q (cm) of the event with the paper's kinematics (D22)
S += [P("4. Does L = 0 mean the quirks annihilate?", "h2"),
      P("<b>Paper (Sec. II, text of Fig. 2):</b> “whenever |L| = 0, the separation between the quirks is large”, so they do not annihilate. <b>This work and arXiv:2002.07503 (App. A):</b> |L| returns to its "
        "production value at every second meeting. So the paper's reason does not hold. Two points show why this still does not mean annihilation:", "b"),
      P("4.1 Classical L ≈ 0 is not a collision", "h3")]
S += B(["Classically L = b × p, where b is the distance by which the two quirks miss each other (impact parameter): b = |L| / p.",
        f"To annihilate, the quirks must overlap at the quantum level, b ~ 1/m<sub>Q</sub> = {sci(INV_M)} cm for m<sub>Q</sub> = 1800 GeV. At that distance L is only about one ħ "
        f"(b &gt; 1/m<sub>Q</sub> needs |L| &gt; {INV_M * PST / HBC:.2f} ħ).",
        "In our simulation (and in the independent code) the left-over |L| at the even meetings is 10⁶–10⁸ ħ, so the quirks still miss each other by millions of times 1/m<sub>Q</sub>:"])
g = [H("time steps per oscillation", "|L| at meeting 2 (ħ)", "|L| at meeting 4 (ħ)", "b = |L| / p (cm)", "b / (1/m<sub>Q</sub>)")]
for n_, l2, l4 in LR:
    bb = [abs(x) * HBC / PST for x in (l2, l4)]
    g.append(C(f"{n_:,}", sci(abs(l2)), sci(abs(l4)), f"{sci(min(bb), 0)} – {sci(max(bb), 0)}", f"{sci(min(bb)/INV_M, 0)} – {sci(max(bb)/INV_M, 0)}"))
S += [grid(g, [38, 34, 34, 34, 34]),
      P(f"Event with the paper's kinematics, p* = {PST:.0f} GeV. A classical simulation cannot resolve L of a few ħ: the left-over L changes with the time step and does not converge, "
        "so we do not know where it would stop.", "m"),
      P("4.2 Even if L returns exactly to its production value, annihilation is not certain", "h3")]
S += B(["arXiv:2002.07503 (App. A, Eq. A.5): at every second meeting the quirks meet head-on, as at production, where the pair's angular momentum is zero "
        "(arXiv:2108.06748, Sec. 4: “the initial L′<sub>tot</sub> at the IP is zero”). With this symmetry annihilation becomes <b>possible</b>.",
        "Possible is not the same as happening. The annihilation cross section of heavy quirks is small, σv ∝ α²/m<sub>Q</sub>² (arXiv:2404.13814, Eq. 4.11). Worst case, if an "
        f"annihilation chance ≈ α²γv is allowed at every second meeting (α = 0.02 / 0.05), the fraction of pairs surviving inside the tracker is {surv('COL2000', 2000)} (colored, 2 keV), "
        f"{surv('EW2000', 4000)} (EW, 4 keV) and {surv('COL2000', 10000)} (colored, 10 keV): small at the benchmarks, not small at large Λ.",
        "The symmetry is not perfect in a real detector. arXiv:2108.06748 (Sec. 4) shows that ionisation in material gives the pair angular momentum, and L changes sharply when the "
        "pair enters or leaves material, or when only one quirk is inside it. Tracker layers are material. Radiation and a non-uniform field are also absent from the paper's model and ours. "
        "(The turning angle η of arXiv:2002.07503, Eq. A.6, rotates the oscillation but keeps the head-on meetings of Eq. A.5, so η alone does not stop L from returning.)",
        "arXiv:2404.13814 models annihilation only after the pair has radiated its energy and dropped into the quirkonium ground state, not during the oscillations. It finds that "
        "radiative energy loss matters only for Λ ≳ 100 keV, far above the keV values here."])
S += [key("<b>Conclusion.</b> L returning to zero (this work, Appendix A) removes the paper's argument, but it does not show that the quirks annihilate. "
          "That needs a quantum estimate of the per-meeting probability, which neither the paper nor this study provides. Table I assumes no annihilation.")]

# 5 repeated crossings
S += [P("5. Quirks crossing the same layer more than once", "h2")]
g = [H("Sample (fiducial events, all crossings within 25 ns)", "events with &gt; 2 hits on at least one layer", "fraction ± σ")]
g += [C("Colored 1800 GeV, 2 keV", f"{c['multi_cross']} / {c['fid']}", es(c["multi_cross"], c["fid"])), C("EW 800 GeV, 4 keV", f"{e['multi_cross']} / {e['fid']}", es(e["multi_cross"], e["fid"]))]
S += [grid(g, [78, 54, 42]), P("These are results of our simulation. The paper says each quirk “will most likely intersect each layer only once”. arXiv:2002.07503 (Sec. VI, Table I and "
                                 "Appendix D, Table II) also finds repeated crossings, more often at larger Λ and larger m/p<sub>T</sub>, with 4–8 hits on some layers at Λ = 2 keV; its percentages "
                                 "(~10%) are for other masses and the CMS tracker and are not directly comparable. Table I above uses the first crossing only.", "m")]

# 6 Figures 3-5
V23 = json.load(open(f"{T}/paper_fig23_vector.json")); c3 = pd.read_csv(f"{T}/fig3_velocity_plane_curves.csv"); e3 = c3[c3.r_cm > 14.5].groupby(["sample", "key"]).dphi_rad.median()
P3 = {"COL2000": V23["fig3"]["curves"]["colored_1800GeV_2keV"], "EW2000": V23["fig3"]["curves"]["EW_800GeV_2keV"]}
p3end = {s_: float(np.interp(15.0, np.array(v["x"]), np.array(v["y"]))) * 1e-3 for s_, v in P3.items()}
g = [H("Fig. 3: Δφ at r = 15 cm (Λ = 2 keV)", "fiducial events", "ours: median [16–84%]", "paper (one event)", "our events below the paper's: k / n = fraction ± σ", "match")]
for s_, lab in (("COL2000", "colored 1800 GeV"), ("EW2000", "EW 800 GeV")):
    v = e3.loc[s_].values; k = int((v < p3end[s_]).sum()); inside = np.quantile(v, .16) <= p3end[s_] <= np.quantile(v, .84)
    g.append(C(lab, str(len(v)), f"{np.median(v)*1e3:.2f} [{np.quantile(v,.16)*1e3:.2f}, {np.quantile(v,.84)*1e3:.2f}] ×10⁻³ rad", f"{p3end[s_]*1e3:.2f} ×10⁻³ rad",
               f"{k} / {len(v)} = {es(k, len(v))}", "inside our 16–84% band" if inside else "<b>at the low end of our spread</b>"))
S += [P("6. Figures 3, 4, 5", "h2"), P("Figure 3: turning of the quirks' plane", "h3"),
      EQ("Δφ = angle between the plane of the two velocity vectors at radius r and at production (paper's definition)"),
      grid(g, [34, 18, 38, 24, 36, 24]), Spacer(1, 2), img("F30_fig3", 140),
      key("<b>What we learn.</b> The plane turns by less than about 10⁻³ rad over 15 cm in both samples, so the hits stay on one flat plane, as in the paper. The paper's single event "
          "lies inside our spread (colored: at its low end).")]
S += [P("Figure 4: hits of one signal event", "h3")]
g = [H("Fig. 4 example event", "Δs (plane thickness)", "Δw (strip width)", "match with the paper")]
g.append(C("Paper (colored)", "83 µm", "0.074 cm", "—"))
for sct, zl in (("Z0", "no smearing"), ("Z1160", "1.16 mm")):
    dd = f4[sct][f4[sct].ellipse != True].groupby("sample").first()
    for s_ in ("COL2000", "EW2000"):
        r_ = dd.loc[s_]; ok_s = "Δs yes" if r_.ds_cm < 0.01 else "Δs no"
        g.append(C(f"This work, {'colored' if s_ == 'COL2000' else 'EW'}, {zl}", f"{r_.ds_cm*1e4:.0f} µm", f"{r_.dw_cm:.3f} cm",
                   f"{ok_s} (both below the 100 µm cut); Δw {'no (wider)' if r_.dw_cm > 0.15 else 'close'}" if r_.ds_cm < 0.01 else f"{ok_s}; Δw {'no (wider)' if r_.dw_cm > 0.15 else 'close'}"))
S += [grid(g, [56, 30, 30, 58]), P("Each example is the signal event with the median Δs. All hits lie on a thin strip, as in the paper.", "m"), Spacer(1, 2), img("F29_fig4_Z0", 120)]
S += [P("Figure 5: Δs and Δw distributions", "h3")]
g = [H("Fig. 5", "smearing", "Δs median: ours / paper", "Δw median: ours / paper", "fraction with Δs &lt; 0.01 cm: ours / paper", "decision")]; ex = []; i = 0
for pop, lab in (("colored", "Colored Quirk"), ("EW", "EW Quirk"), ("converted γ + pile-up", "Converted gamma"), ("pile-up", "Pileup")):
    for sct, zl in (("Z0", "none"), ("Z1160", "1.16 mm")):
        x = F5[sct][F5[sct].population == pop]
        if not len(x): continue
        k, n = int((x.ds < 0.01).sum()), len(x); dd_, bb = cell(k, n, PBELOW[lab]); i += 1
        g.append(C(pop + (" signal" if pop in ("colored", "EW") else ""), zl, f"{x.ds.median()*1e4:.0f} / {PM[lab][0]*1e4:.0f} µm", f"{x.dw.median():.3f} / {PM[lab][1]:.3f} cm", f"{k}/{n} = {es(k, n)} / {PBELOW[lab]:.2f}", dd_))
        ex.append(("BACKGROUND", (5, i), (5, i), bb))
fr = lambda pop, sct: f"{(F5[sct][F5[sct].population == pop].ds < 0.01).mean():.2f}"
S += [grid(g, [24, 18, 32, 32, 44, 24], ex), Spacer(1, 2), img("F40_fig5_Z0", 118),
      key(f"<b>What we learn.</b> Without smearing the signal Δs (≈ 40 µm) is close to the paper's (≈ 30 µm) and all signal passes the Δs cut (paper ≈ 90%), "
        f"but {fr('converted γ + pile-up', 'Z0')} of the converted-photon planes also pass (paper {PBELOW['Converted gamma']:.2f}). With 1.16 mm no converted photon passes, as in the paper, "
        f"but most signal fails too. No single SCT z setting reproduces both the paper's signal and its background. "
        "Δw is about 5× (colored) and 2× (EW) the paper's; it follows the width expected from our own kinematics (arXiv:2002.07503 Eq. III.1: Δw ≈ belt width/√12).")]

# 7 backgrounds / UL
ul = R.ul95(9139); ex_ = lambda xs: 300 * xs * 1e3 * 0.01
S += [P("7. Backgrounds", "h2"), P("7.1 How many background events pass and fail", "h3")]
cv1, cv0, pu1 = BG["conv1160"], BG["conv0"], BG["pu1160"]
g = [H("Background sample", "SCT z", "events", "plane found (Δw &lt; 1 cm)", "+ hit multiplicity", "<b>pass</b> (signal region)", "fail", "paper")]
g += [C("converted γ + pile-up (μ = 50)", "1.16 mm", "9139", str(cv1["plane"]), str(cv1["mult"]), f"<b>{cv1['sr']}</b>", str(9139 - cv1["sr"]), "“a few” events at 300 fb⁻¹"),
      C("converted γ + pile-up (μ = 50)", "none", "9139", str(cv0["plane"]), str(cv0["mult"]), f"<b>{cv0['sr']}</b>", str(9139 - cv0["sr"]), "“a few” events at 300 fb⁻¹"),
      C("pile-up only (μ = 50)", "1.16 mm", "5000", f"{pu1['r4']} (≥ 4 of 8 layers); {pu1['r8']} (all 8)", "—", f"<b>{pu1['sr']}</b>", str(5000 - pu1["sr"]), "none in the signal region")]
ex = [("BACKGROUND", (5, 1), (5, 1), OKB), ("BACKGROUND", (5, 2), (5, 2), BADB), ("BACKGROUND", (5, 3), (5, 3), OKB)]
g2 = [H("Pile-up planes (5000 events, 1.16 mm)", "ours: k / n", "rate", "paper (approx.)", "decision")]; ex2 = []
for i_, (lab, k, pp_) in enumerate((("selected plane, ≥ 1 hit in ≥ 4 of 8 layers", pu1["r4"], 1e-3), ("selected plane, ≥ 1 hit in all 8 layers", pu1["r8"], 6e-5)), 1):
    d_, b_ = cell(k, 5000, pp_); g2.append(C(lab, f"{k} / 5000", sci(k / 5000), f"~{sci(pp_, 0)}", d_)); ex2.append(("BACKGROUND", (4, i_), (4, i_), b_))
S += [grid(g, [36, 14, 13, 28, 22, 17, 13, 31], ex), Spacer(1, 3), grid(g2, [62, 26, 24, 30, 32], ex2),
      P("Pile-up only was not simulated without SCT z smearing. Green: no background in the signal region, as in the paper; red: background in the signal region.", "m"),
      P("7.2 Converted photons: why the upper limit is the same (Q1)", "h3")]
g = [H("Converted γ + pile-up (9139 events)", "in signal region", "per conversion", "expected events at 300 fb⁻¹: our σ (0.211 pb) / paper σ (~1 pb)")]
g.append(C("SCT z 1.16 mm", f"{BG['conv1160']['sr']} / 9139", f"&lt; {sci(ul)} (95% UL)", f"&lt; {ex_(0.211)*ul:.2f} / &lt; {ex_(1.0)*ul:.2f}"))
g.append(C("no SCT z smearing", f"{BG['conv0']['sr']} / 9139", es(BG["conv0"]["sr"], 9139, 4), f"{ex_(0.211)*BG['conv0']['sr']/9139:.0f} / {ex_(1.0)*BG['conv0']['sr']/9139:.0f}"))
S += [grid(g, [46, 26, 36, 66]),
      key(f"<b>Answer.</b> The limit is a property of our 9139 simulated conversions: 0 pass, so the 95% upper limit per conversion is 1 − 0.05<super>1/9139</super> = {sci(ul)}, whatever the cross section. "
        f"The cross section only sets how many conversions are expected (300 fb⁻¹ × σ × 1% = {ex_(0.211):.0f} or {ex_(1.0):.0f}), which is why the last column differs. "
        f"Without SCT z smearing on the background, {BG['conv0']['sr']} conversions pass and the background is no longer zero.")]

# 8 open + refs
S += [P("8. Open points", "h2")] + B(["SCT z: the authors' stated resolution gives efficiencies far below Table I; only no smearing reproduces it.",
                                      "EW ε<sub>reco</sub> at Λ = 1–2 keV above the paper (production and LO sample).", "Signal Δw 2–5× the paper's.",
                                      "Paper's Fig. 2: unequal half-oscillations; L definition, charges and momenta of its event not given.",
                                      f"EW LO sample: {N41}/3000 events done; showered version pending."])
S += [P("References", "h2")] + [P(x, "c") for x in [
    "Paper: S. Knapen, H. K. Lou, M. Papucci, J. Setford, Phys. Rev. D 96, 115015 (2017), arXiv:1708.02243.   [27] ATLAS, ATL-PHYS-PUB-2009-002.",
    "J. Li, T. Li, J. Pei, W. Zhang, “The quirk trajectory”, arXiv:2002.07503 (Eqs. II.11–II.14, A.4–A.5; Sec. VI, App. D).",
    "J. Li, T. Li, J. Pei, W. Zhang, arXiv:1911.02223 (EW trigger 0.1 as an LO ratio, App. A).   J. Li et al., arXiv:2108.06748.   J. L. Feng et al., arXiv:2404.13814."]]
S += [P(f"Data and scripts: R_data_2026_10_15.py (all numbers), R_report_2026-10-16_v3.py, F38/F39/F40 figures; decision log D17–D44.", "m")]
def deco(cv_, d):
    cv_.saveState(); cv_.setFont("DV", 7.3); cv_.setFillColor(MUTED); cv_.drawString(18 * mm, 10 * mm, "Reproduction of Table I of arXiv:1708.02243 · 16 October 2026")
    cv_.drawRightString(192 * mm, 10 * mm, f"{d.page}"); cv_.restoreState()
doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=14 * mm, bottomMargin=16 * mm, title="Reproduction of Table I of arXiv:1708.02243", author="")
doc.addPageTemplates([PageTemplate("p", [Frame(18 * mm, 16 * mm, 174 * mm, 267 * mm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=deco)])
doc.build(S); print("wrote", OUT, "| D41 events", N41, "| 2-sigma rule vs Wilson disagreements:", WIL)
