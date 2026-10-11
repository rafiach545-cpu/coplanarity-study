#!/usr/bin/env python3
"""Builds TABLE_I_RESULTS_2026-10-06.pdf: every layer crossing within 25 ns used as a hit (v7 table), both readings of the multiplicity cut,
Every p-value is recomputed here (exact two-sided binomial vs the paper's quoted value) and asserted equal to the stored
analysis tables; categories follow the agreed scale (p<0.01 strongly inconsistent, 0.01-0.05 inconsistent,
0.05-0.10 borderline, >=0.10 consistent). Run with a Python that has reportlab."""
import os, sys, json, pandas as pd, numpy as np
from scipy import stats
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, Image,
                                KeepTogether, PageBreak)
HERE = os.path.dirname(os.path.abspath(__file__)); L = os.path.abspath(f"{HERE}/.."); T = f"{L}/tables"; FIG = f"{L}/FINAL_FIGURES"
OLD = os.path.abspath(f"{L}/../FINAL_FIGURES_2000_EVENT_2026-09-30")
OUT = f"{L}/TABLE_I_RESULTS_2026-10-06.pdf"
F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", F + "DejaVuSans.ttf")); pdfmetrics.registerFont(TTFont("DVB", F + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVM", F + "DejaVuSansMono.ttf")); pdfmetrics.registerFont(TTFont("DVO", F + "DejaVuSans.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("DV", normal="DV", bold="DVB", italic="DVO", boldItalic="DVB")
INK, MUTED, RULE, ACC = colors.HexColor("#1b2328"), colors.HexColor("#5b6770"), colors.HexColor("#d5dbde"), colors.HexColor("#1f6f8b")
OKB, OKF = colors.HexColor("#e2f2e8"), colors.HexColor("#1d6b3c"); BADB, BADF = colors.HexColor("#f9e3e1"), colors.HexColor("#a1302a")
WB, WF = colors.HexColor("#fbf0d6"), colors.HexColor("#8a5a00"); NOTE = colors.HexColor("#edf3f6"); HEAD = colors.HexColor("#eef1f2")
st = {"h1": ParagraphStyle("h1", fontName="DVB", fontSize=17, leading=21, textColor=INK, spaceAfter=4),
      "h2": ParagraphStyle("h2", fontName="DVB", fontSize=12.5, leading=16, textColor=INK, spaceBefore=6, spaceAfter=4),
      "b": ParagraphStyle("b", fontName="DV", fontSize=9.2, leading=13, textColor=INK),
      "m": ParagraphStyle("m", fontName="DV", fontSize=8.2, leading=11, textColor=MUTED),
      "cap": ParagraphStyle("cap", fontName="DVO", fontSize=7.8, leading=10, textColor=MUTED, spaceBefore=2),
      "c": ParagraphStyle("c", fontName="DV", fontSize=7.8, leading=10, textColor=INK),
      "cb": ParagraphStyle("cb", fontName="DVB", fontSize=7.8, leading=10, textColor=INK),
      "ch": ParagraphStyle("ch", fontName="DVB", fontSize=7.2, leading=9, textColor=MUTED),
      "pt": ParagraphStyle("pt", fontName="DV", fontSize=9, leading=12.5, textColor=INK, leftIndent=9, bulletIndent=0)}
P = lambda t, s="b": Paragraph(t, st[s])

# ---------- statistics (recomputed and cross-checked) ----------
def wilson(k, n, z=1.959963984540054):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0, c - h), min(1, c + h)
def ul(k, n): return stats.beta.ppf(0.95, k + 1, n - k)
def pexact(k, n, p0): return stats.binomtest(k, n, p0).pvalue
def cls(p):
    if p is None or np.isnan(p): return ("n/a", None)
    if p < 0.01: return ("Strongly inconsistent", "bad")
    if p < 0.05: return ("Statistically inconsistent", "bad")
    if p < 0.10: return ("Borderline / mild tension", "warn")
    return ("Consistent", "ok")
def fp(p):
    if p is None or np.isnan(p): return "—"
    if p >= 0.1: return f"{p:.2f}"
    if p >= 0.01: return f"{p:.2g}"
    if p >= 0.001: return f"{p:.4f}".rstrip("0")
    m, e = f"{p:.1e}".split("e"); sup = str(int(e)).replace("-", "⁻").translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))
    return f"{m}×10{sup}"
def sci(x, d=1):
    m, e = f"{x:.{d}e}".split("e"); sup = str(int(e)).replace("-", "⁻").translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))
    return f"{m}×10{sup}"
def pct(x): return f"{100*x:.1f}%" if x >= 0.01 else f"{100*x:.2f}%"
def ci(k, n, scale=100, d=1):
    lo, hi = wilson(k, n); return f"[{lo*scale:.{d}f}, {hi*scale:.{d}f}]"

sig = pd.read_csv(f"{T}/signal_efficiency_statistics.csv")
lit = sig[sig.config == "LITERAL"].set_index(["sample", "quantity"])
PAPER = {"COL": {"trigger": .24, "fiducial": .28, "reco": .35}, "EW": {"trigger": .10, "fiducial": .28, "reco": .72}}
Q = {"trigger": "trigger", "fiducial": "fiducial", "reco": "reconstruction (full Sec. IV SR)"}
def sigrow(s, q):
    r = lit.loc[(s, Q[q])]; k, n = int(r.N_pass), int(r.N_total); p0 = PAPER["COL" if s.startswith("COL") else "EW"][q]
    p = pexact(k, n, p0); assert abs(p - r.p_exact_vs_paper_quoted) < 1e-9 * max(1, p), (s, q)   # cross-check vs stored table
    lo, hi = wilson(k, n); assert abs(lo - r.wilson95_lo) < 1e-6 and abs(hi - r.wilson95_hi) < 1e-6   # stored table used z=1.96
    return k, n, p0, p
def calrow(s):
    r = sig[(sig["sample"] == s) & (sig.geometry == "B") & (sig.sct_z == "Z0") & (sig.dw_convention == "W1") & (sig.quantity == Q["reco"])].iloc[0]
    k, n = int(r.N_pass), int(r.N_total); p0 = PAPER["COL" if s.startswith("COL") else "EW"]["reco"]; return k, n, p0, pexact(k, n, p0)

# ---------- table helper ----------
def chip(text, kind):
    c = {"ok": (OKB, OKF), "bad": (BADB, BADF), "warn": (WB, WF), None: (colors.white, MUTED)}[kind]
    return Paragraph(f'<font color="{c[1].hexval().replace("0x", "#")}"><b>{text}</b></font>', st["c"]), c[0]
def table(header, rows, widths, chipcol=None, shade_rows=()):
    data = [[P(h, "ch") for h in header]]; bgs = []
    for i, r in enumerate(rows, 1):
        cells = []
        for j, v in enumerate(r):
            if isinstance(v, tuple) and len(v) == 2 and v[1] in ("ok", "bad", "warn", None):
                para, bg = chip(*v); cells.append(para); bgs.append(("BACKGROUND", (j, i), (j, i), bg))
            else: cells.append(v if not isinstance(v, str) else P(v, "c"))
        data.append(cells)
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    sty = [("BACKGROUND", (0, 0), (-1, 0), HEAD), ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
           ("BOX", (0, 0), (-1, -1), 0.6, RULE)] + bgs
    for i in shade_rows: sty.append(("TEXTCOLOR", (0, i), (-1, i), MUTED))
    t.setStyle(TableStyle(sty)); return t
def img(path, width_mm, caption=None, cell=False):
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(path).getSize(); w = width_mm * mm; im = Image(path, width=w, height=w * ih / iw)
    parts = [im] + ([P(caption, "cap")] if caption else [])
    return parts if cell else KeepTogether(parts)
def box(title, points):
    inner = [P(f"<b>{title}</b>", "b")] + [Paragraph(p, st["pt"], bulletText="•") for p in points]
    t = Table([[inner]], colWidths=[174 * mm]); t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NOTE), ("LEFTPADDING", (0, 0), (-1, -1), 8),
                                                                     ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t
fig = lambda name: f"{FIG}/{name}/{name}.png"



# ---------- results sheet (2026-10-06): every layer crossing, all SCT z scenarios, paper quotes ----------
import glob as _gl
OKL = "No statistically significant inconsistency"
def cls(p):
    if p < 0.01: return ("Strongly inconsistent", "bad")
    if p < 0.05: return ("Statistically inconsistent", "bad")
    if p < 0.10: return ("Borderline / mild tension", "warn")
    return (OKL, "ok")
def chipc(txt, kind):
    c = {"ok": (OKB, OKF), "bad": (BADB, BADF), "warn": (WB, WF)}[kind]
    return Paragraph(f'<font color="{c[1].hexval().replace("0x", "#")}"><b>{txt}</b></font>', st["c"]), c[0]
V = pd.read_csv(f"{T}/v7_primary_table_I.csv")
TZ = {"none": "Z0", "580": "Z580", "1160": "Z1160"}; M2 = {"ge": "at least 2 (primary)", "eq": "exactly 2 (sensitivity)"}
def vr(s, q, sz=None, m="ge"):
    x = V[(V["sample"] == s) & (V.quantity == q)]
    if sz: x = x[(x.sct == TZ[sz]) & (x.multiplicity == M2[m])]
    r = x.iloc[0]; assert len(x) == 1; k, n = int(r.k), int(r.n); p0 = float(r.paper_value)
    p = pexact(k, n, p0); assert abs(p - r.p_exact_vs_paper) <= 1e-9 * max(p, 1e-300) + 1e-300
    lo, hi = wilson(k, n); assert abs(lo - r.wilson95_lo) < 1e-6 and abs(hi - r.wilson95_hi) < 1e-6; return k, n, p0, p
def grid(data, widths, sty):
    tb = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HEAD), ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE), ("BOX", (0, 0), (-1, -1), 0.6, RULE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)] + sty)); return tb
RECO = "ε<sub>reco</sub> = N(fiducial, plane found, 2 hits in 7 layers + ≥ 1 in the 8th, Δw &lt; 1 cm, Δs &lt; 0.01 cm) / N(fiducial); every layer crossing within 25 ns gives a hit"
DEF = {"trigger": ("ε<sub>trig</sub> = N(pT of the quirk pair &gt; 200 GeV) / N(events after jet matching)", "Same cut as the paper (Sec. III B), on the final-state quirk pair."),
       "fiducial": ("ε<sub>fid</sub> = N(both quirks cross all 8 barrel layers inside the [27] lengths, within 25 ns) / N(triggered)", "The paper's definition (Sec. IV); colored: both R-hadrons charged, in numerator and denominator.")}
d1 = [[P(h, "ch") for h in ["Benchmark", "Sample", "k / n", "ε [Wilson 95%]", "Paper", "p", "Verdict"]]]; s1 = []; ri = 0
for q in ["trigger", "fiducial"]:
    ri += 1; d1.append([P(f"<b>{DEF[q][0]}</b><br/>{DEF[q][1]}", "c")] + [""] * 6); s1 += [("SPAN", (0, ri), (-1, ri)), ("BACKGROUND", (0, ri), (-1, ri), NOTE)]
    for s in ["COL1000", "COL2000", "EW1000", "EW2000"]:
        k, n, p0, p = vr(s, q); lo, hi = wilson(k, n); ch, bg = chipc(*cls(p)); ri += 1
        d1.append([P("Colored" if s == "COL1000" else ("EW" if s == "EW1000" else ""), "c"), P(s, "c"), P(f"{k} / {n}", "c"), P(f"{k/n:.3f} [{lo:.3f}, {hi:.3f}]", "c"), P(f"{p0:.2f}", "c"), P(fp(p), "c"), ch])
        s1.append(("BACKGROUND", (6, ri), (6, ri), bg))
T_ = lambda x: x.astype(str) == "True"
def ovk(d_):
    o = pd.concat(pd.read_csv(f) for f in _gl.glob(f"{L}/logs/{d_}/chunk_*.csv")); o = o[o.config == "LITERAL"]; assert o.event.nunique() == 9139
    return int((T_(o.plane) & T_(o.mult) & T_(o.final)).sum())
BG = {"580": (ovk("P10_chunks_B_Z580_REF34"), "cited material model"), "1160": (ovk("P10_chunks_LITERAL"), "no material model"), "none": (ovk("P10_chunks_B_Z0_REF34"), "cited material model")}
SCEN = [("A", "none", "580"), ("B", "580", "580"), ("C", "1160", "1160"), ("D", "none", "none")]
LBL = {"none": "no smearing", "580": "580 µm", "1160": "1.16 mm"}
def tot(s, sz):
    t = vr(s, "trigger"); f = vr(s, "fiducial"); r = vr(s, "reconstruction", sz); return (t[0] / t[1]) * (f[0] / f[1]) * (r[0] / r[1])
d2 = [[P(h, "ch") for h in ["", "SCT z: signal / background", "ε<sub>reco</sub> COL2000 (paper 0.35)", "ε<sub>reco</sub> EW2000 (paper 0.72)", "Conversion + pile-up in signal region (paper ≈ 2 of 9139)", "Total ε COL / EW (paper 0.024 / 0.020)", "Signal / background like the paper?"]]]; s2 = []
for i, (sc, ss, sb) in enumerate(SCEN, 1):
    cells = [P(f"<b>{sc}</b>", "b"), P(f"{LBL[ss]} / {LBL[sb]}", "c")]; oks = []
    for smp in ["COL2000", "EW2000"]:
        k, n, p0, p = vr(smp, "reconstruction", ss); lo, hi = wilson(k, n); oks.append(p >= 0.05); cells.append(P(f"{k}/{n} = {k/n:.2f} [{lo:.2f}, {hi:.2f}]<br/>p = {fp(p)}", "c"))
    kb, mdl = BG[sb]; lo, hi = wilson(kb, 9139); bok = lo <= 2.4e-4 <= hi
    cells.append(P(f"{kb} / 9139" + (f" (UL {sci(ul(kb, 9139))})" if kb == 0 else f" = {100*kb/9139:.1f}%") + f"<br/>{mdl}", "c"))
    cells.append(P(f"{tot('COL2000', ss):.3f} / {tot('EW2000', ss):.3f}", "c"))
    sig_ok = all(oks); verdict = ("signal ✓  background ✓", "ok") if sig_ok and bok else ((("signal ✗  background ✓", "bad") if bok else ("signal ✓  background ✗", "bad")) if (sig_ok or bok) else ("signal ✗  background ✗", "bad"))
    ch, bg = chipc(*verdict); cells.append(ch); s2.append(("BACKGROUND", (6, i), (6, i), bg)); d2.append(cells)
d3 = [[P(h, "ch") for h in ["Sample (paper)", "SCT z", "≥ 2 hits k/n", "ε [Wilson 95%]", "p", "Verdict", "exactly 2 k/n", "ε [Wilson 95%]", "p"]]]; s3 = []; ri = 0
ri += 1; d3.append([P(f"<b>{RECO}</b>", "c")] + [""] * 8); s3 += [("SPAN", (0, ri), (-1, ri)), ("BACKGROUND", (0, ri), (-1, ri), NOTE)]
for s in ["COL1000", "COL2000", "EW1000", "EW2000"]:
    for sz in ["none", "580", "1160"]:
        k, n, p0, p = vr(s, "reconstruction", sz); lo, hi = wilson(k, n); vt, vk = cls(p); ch, bg = chipc(vt.replace("No statistically significant", "No significant"), vk); ri += 1
        k2, n2, _, p2 = vr(s, "reconstruction", sz, "eq"); l2, h2 = wilson(k2, n2)
        d3.append([P(f"{s}<br/>({p0:.2f})" if sz == "none" else "", "c"), P(LBL[sz].replace("no smearing", "none"), "c"), P(f"{k}/{n}", "c"), P(f"{k/n:.2f} [{lo:.2f}, {hi:.2f}]", "c"), P(fp(p), "c"), ch,
                   P(f"{k2}/{n2}", "c"), P(f"{k2/n2:.2f} [{l2:.2f}, {h2:.2f}]", "c"), P(fp(p2), "c")])
        s3.append(("BACKGROUND", (5, ri), (5, ri), bg))
        if sz == "1160" and s != "EW2000": s3.append(("LINEBELOW", (0, ri), (-1, ri), 1.0, MUTED))
QS = ParagraphStyle("q", fontName="DVO", fontSize=8.4, leading=11, textColor=INK, leftIndent=8)
def quote(src, txt): return [Paragraph(f"<b>{src}</b>", st["c"]), Paragraph(f"“{txt}”", QS), Spacer(1, 3)]
SM = ParagraphStyle("sm", fontName="DV", fontSize=8.6, leading=11.5, textColor=INK, leftIndent=9, bulletIndent=0)
B_ = lambda xs: [Paragraph(x, SM, bulletText="•") for x in xs]
mc = pd.read_csv(f"{T}/audit_multiple_crossings.csv")
S = [P("Quirk Table I reproduction", "h1"), P("arXiv:1708.02243 · colored m<sub>Q</sub> = 1.8 TeV, Λ = 2 keV · EW m<sub>Q</sub> = 800 GeV, Λ = 4 keV · results as of 6 October 2026 · Wilson 95% intervals · p = exact binomial against the paper's value", "m"), Spacer(1, 4),
     P("Trigger and fiducial efficiency (the same in every SCT setting)", "h2"), grid(d1, [19, 17, 19, 34, 12, 17, 56], s1), Spacer(1, 6),
     P("Four ways to set the SCT resolution along the beam (z)", "h2"), grid(d2, [8, 28, 30, 30, 30, 22, 26], s2),
     P("ε<sub>reco</sub> here: every layer crossing within 25 ns gives a hit, ≥ 2 hits in 7 layers. Background: converted photon + μ = 50 pile-up, 9139 photons, Ref. [27] lengths, fit from the vertex "
       "(unchanged: GeV electrons cross each layer once). Pile-up only (5000 events, 1.16 mm): 0 in the signal region. Total ε uses the 2000-event samples. "
       "✓ = paper value inside our Wilson 95% interval (signal: p ≥ 0.05 for both samples).", "m")]
S += [PageBreak(), P("Reconstruction efficiency: every SCT setting, both readings of the hit cut", "h2"), grid(d3, [17, 17, 13, 27, 15, 30, 13, 27, 15], s3), Spacer(1, 4),
      img(fig("F27_reco_all_crossings"), 174, "Same numbers as the table. Circles: ≥ 2 hits in 7 layers; squares: exactly 2. Bars = Wilson 95%; dashed = paper."), Spacer(1, 4),
      P("What we found in the review (and corrected)", "h2")] + B_([
      "<b>A quirk often crosses the same layer more than once within 25 ns</b> (it swings back and forth while moving out slowly). Fiducial events with a repeated crossing: "
      + ", ".join(f"{sm} {int((g.n_layer_quirk_with_multiple_crossings > 0).sum())}/{len(g)}" for sm, g in mc[T_(mc.fid)].groupby("sample")) + ". Our earlier code kept only the first crossing. "
      "The paper computes “the intersections of the trajectories”, so every crossing is now a hit.",
      "<b>The hit cut can be read two ways.</b> The paper says “All but one layer must contain 2 hits”. With extra crossings a layer can hold 3–5 hits. "
      "Reading it as ≥ 2 keeps those events; reading it as exactly 2 removes them (EW drops from about 0.8 to 0.44–0.55). With first crossings only, both readings gave nearly the same numbers.",
      "<b>Fig. 2 and 3 redone</b> in the exact centre-of-mass frame (before: equal lab time and a plane normal from x₁ × x₂, which gave gaps). Fig. 4 now shows the median-Δs event, not a hand-picked one."])
S += [PageBreak(), P("What the paper and its references say", "h2")]
S += quote("Paper, Sec. III A (signal detector)", "The intersections of the trajectories with a simplified model of the ATLAS inner detector are calculated, and the center of each pixel hit is used as the input for our analysis. We hereby use the parameters of the various detector elements as specified in [27]. Specifically, for the pixel detector we use the pixel size rather than the resolution and for the silicon microstrip tracker (SCT) we conservatively assume a resolution of twice the intrinsic accuracy quoted in [27].")
S += quote("Ref. [27] (ATL-PHYS-PUB-2009-002, in arXiv:0901.0512, p. 18 = PDF p. 42)", "The intrinsic accuracies per module in the barrel are 17 µm (R−φ) and 580 µm (z)")
S += quote("Paper, Sec. III B (trigger)", "the quirk/anti-quirk pair is essentially always central and sufficiently boosted, such that each quirk will most likely intersect each layer only once.")
S += quote("Paper, Sec. IV (signal region)", "2. All but one layer must contain 2 hits, the remaining layer must contain at least 1 hit 3. ∆w < 1.0 cm and ∆s < 0.01 cm")
S += quote("Paper, Sec. III C (Δs and Δw)", "The smallest eigenvalue, ∆s², then gives the minimum value of d² … Then second eigenvalue, denoted by ∆w, then provide a measure of the width of the quirks’ oscillations. … – Second eigenvalue of (11), or the “width”, (∆w)²")
S += quote("Paper, Sec. III D (backgrounds)", "We model pile-up by randomly selecting minimum bias events ... processed by the simplified detector described in [34]. ... The e⁺e⁻ pair is then passed through the same detector simulation as described for the pile-up background.")
S += quote("Ref. [34] (arXiv:1612.00850), App. A", "We take the resolution and geometry of each component from the ATLAS technical design report")
S += quote("Paper, Sec. IV (results)", "the reconstruction efficiency for these cuts can be as high as ∼73%.  …  Even though Fig. 5 suggests a few background events after the final selection cut of Δs < 0.01 cm, we suspect that they can easily be removed")
S += [Spacer(1, 4), P("<b>How each choice rests on these lines</b>", "b")] + B_([
      "<b>Δs = √λ₁ and Δw = √λ₂</b> of Eq. 11 (the summary list gives (Δw)² as the second eigenvalue). We use this.",
      "<b>Every crossing is a hit:</b> the paper calculates “the intersections”; its “only once” is an expectation, not a cut. Whether a layer may then hold more than 2 hits is not stated.",
      "<b>SCT z, scenarios B and C</b> follow the signal sentence literally: “twice the intrinsic accuracy” of [27] gives 1.16 mm (C); undoubled [27] is 580 µm (B). The paper does not say which direction is doubled.",
      "<b>Scenario A</b> follows the paper's results: no smearing reproduces the ≈ 73% and the Fig. 5 signal shape; the background uses the cited detector [34] (≈ 580 µm from the TDR). No sentence states “no smearing”.",
      f"<b>Scenario D</b> (no smearing for both) reproduces the signal but gives {BG['none'][0]} / 9139 conversions in the signal region, against the paper's “a few”."])
EQ = ParagraphStyle("eq", fontName="DV", fontSize=9, leading=13.5, textColor=INK, leftIndent=8)
E = lambda t: Paragraph(t, EQ)
S += [Spacer(1, 6), P("Definitions", "h2"),
      E("ε<sub>trig</sub> = N(pT of the quirk pair &gt; 200 GeV) / N(events after jet matching)"),
      E("ε<sub>fid</sub> = N(triggered, both quirks cross all 8 barrel layers inside the [27] lengths, within 25 ns) / N(triggered)"),
      E(RECO), E("ε = ε<sub>trig</sub> × ε<sub>fid</sub> × ε<sub>reco</sub>   (paper Eq. 12)"),
      P("Colored: both R-hadrons must be charged; applied to the triggered events before ε<sub>fid</sub> (27 of 101 and 68 of 207 events).", "m"), Spacer(1, 3),
      E("Wilson 95% interval for k of n (ε = k/n, z = 1.96):  [ ε + z²/2n ± z √( ε(1−ε)/n + z²/4n² ) ] / (1 + z²/n)"),
      E("95% upper limit (UL) when 0 of n pass:  UL = 1 − 0.05<super>1/n</super> ≈ 3/n"),
      E("p = exact binomial probability, if the paper's value were exactly right, of a count as unlikely as ours or more")]
S += [PageBreak(), P("Paper Figure 5: Δs and Δw before the Δs cut", "h2"),
      img(fig("F26_fig5_v3"), 176, "Unit area on the paper's bins; dotted = paper's Fig. 5. Signal: plane + hit cut (≥ 2), every crossing, no SCT z smearing, before the Δs cut "
          "(Δw &lt; 1 is part of the paper's plane search, so no event above 1 cm can appear). Converted γ + pile-up: SCT z 580 µm, cited material model. Pile-up: existing run (1.16 mm), all planes."), Spacer(1, 3)] + B_([
      "<b>Signal Δs:</b> median 38 µm (colored) and 45 µm (EW), against about 35 and 28 µm in the paper. All our signal events after the plane and hit cut already have Δs &lt; 0.01 cm; the paper has a tail above it (8–10%).",
      "<b>Signal Δw:</b> median 0.49 cm (colored) and 0.10 cm (EW), against about 0.09 and 0.045 cm in the paper. EW is about 2× wider, colored about 5×. Using ½√λ₂ would explain the EW factor but not the colored one."])
S += [PageBreak(), P("Paper Figures 2 and 3", "h2"),
      img(fig("F23_fig2_v2"), 120, "Fig. 2 on the paper's axes: |L| (magnitude of the angular momentum, solid) and separation d (dashed) in the exact centre-of-mass frame, vs the radius r of the centre of mass. "
          "Colored 1.8 TeV, 2 keV, COL2000 fiducial event with the median |L|<sub>max</sub>. Where |L| ≈ 0, d = 0.017–0.019 cm (≫ 1/m<sub>Q</sub>), so the pair does not annihilate. "
          "|L| is zero at production and grows like 1 − cos(ωt), so it peaks at every second minimum of d; the paper's single event shows a different pattern."), Spacer(1, 4),
      img(fig("F24_fig3_v2"), 176, "Fig. 3 on the paper's axes (r = 0–15 cm, Δφ in 10⁻³ rad): rotation of the plane of relative motion (normal from L̂; a sliding plane fit gives the same within 10%). "
          "Left: event closest to the paper's curve; middle: median event; right: Δφ at 15 cm for all fiducial events. Paper values (dotted): colored ≈ 0.09×10⁻³, EW ≈ 0.35×10⁻³. "
          "Our medians: colored 0.42×10⁻³, EW (2 keV) 0.89×10⁻³; the paper's values sit at our 9th and 23rd percentile. EW 4 keV (Table I benchmark): 11.5×10⁻³.")]
S += [PageBreak(), P("Paper Figure 4: median event, not hand-picked", "h2"),
      img(fig("F25_fig4_median_events"), 174, "Selection rule: among events that pass the full signal region (every crossing, no SCT z smearing, ≥ 2 hits), the one with the median Δs. "
          "Colored: COL2000 event 212 (6th of 11, Δs = 38 µm, Δw = 0.35 cm). EW: EW2000 event 270 (25th of 49, Δs = 45 µm, Δw = 0.10 cm). "
          "Left: all hits in the plane's (n₃, n₂) coordinates with the layers as ellipses; right: zoom with the ±Δw band. Paper's example: Δw ≈ 0.074 cm.")]

def deco(c, d):
    c.saveState(); c.setFont("DV", 7.5); c.setFillColor(MUTED)
    c.drawString(18 * mm, 10 * mm, "Quirk Table I reproduction · arXiv:1708.02243 · 6 October 2026")
    c.drawRightString(192 * mm, 10 * mm, f"{d.page}"); c.restoreState()
doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=15 * mm, bottomMargin=16 * mm,
                      title="Quirk Table I Reproduction", author="", subject="Reproduction of arXiv:1708.02243 Table I")
doc.addPageTemplates([PageTemplate("p", [Frame(18 * mm, 16 * mm, 174 * mm, 266 * mm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=deco)])
doc.build(S)
print("wrote", OUT)
