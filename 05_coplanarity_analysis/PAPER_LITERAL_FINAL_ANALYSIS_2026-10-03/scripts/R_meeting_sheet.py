#!/usr/bin/env python3
"""Builds PROFESSOR_REPORT_2026-10-04_v5.pdf (corrected acceptance/longitudinal classification; v1 PDF is left untouched) (A4) from verified tables and FINAL_FIGURES PNGs.
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
OUT = f"{L}/MEETING_SHEET_2026-10-05.pdf"
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


# ---------- meeting sheet (2026-10-05): current results only ----------
OKL = "No statistically significant inconsistency"
def cls(p):
    if p < 0.01: return ("Strongly inconsistent", "bad")
    if p < 0.05: return ("Statistically inconsistent", "bad")
    if p < 0.10: return ("Borderline / mild tension", "warn")
    return (OKL, "ok")
V = pd.read_csv(f"{T}/v6_primary_table_I.csv")
TZ0 = "no SCT z smearing (UNDOCUMENTED in text; best-supported reading for the signal)"
DEF = {"trigger": ("ε<sub>trig</sub> = N(pT of the quirk pair &gt; 200 GeV) / N(events after jet matching)",
                   "Same cut as the paper (Sec. III B), on the final-state quirk pair."),
       "fiducial": ("ε<sub>fid</sub> = N(both quirks cross all 8 barrel layers inside the [27] lengths, within 25 ns) / N(triggered)",
                    "The paper's definition (Sec. IV); colored: both R-hadrons charged, in numerator and denominator."),
       "reconstruction": ("ε<sub>reco</sub> = N(plane found, 2 hits in 7 layers + ≥ 1 in the 8th, Δw &lt; 1 cm, Δs &lt; 0.01 cm) / N(fiducial)",
                          "The paper's plane algorithm and signal-region cuts (Sec. III C, IV); SCT z not smeared.")}
PAP = {"COL": {"trigger": .24, "fiducial": .28, "reconstruction": .35}, "EW": {"trigger": .10, "fiducial": .28, "reconstruction": .72}}
data = [[P(h, "ch") for h in ["Benchmark", "Sample", "k / n", "ε [Wilson 95%]", "Paper", "p", "Verdict"]]]; sty = []; ri = 0
for bench, label in [("COL", "Colored"), ("EW", "EW")]:
    for q in ["trigger", "fiducial", "reconstruction"]:
        ri += 1; data.append([P(f"<b>{DEF[q][0]}</b><br/>{DEF[q][1]}", "c"), "", "", "", "", "", ""]); sty += [("SPAN", (0, ri), (-1, ri)), ("BACKGROUND", (0, ri), (-1, ri), NOTE)]
        for s in (["COL1000", "COL2000"] if bench == "COL" else ["EW1000", "EW2000"]):
            r = V[(V["sample"] == s) & (V.quantity == q) & (V.treatment == ("—" if q != "reconstruction" else TZ0))].iloc[0]
            k, n = int(r.k), int(r.n); p0 = PAP[bench][q]; p = pexact(k, n, p0); assert abs(p - r.p_exact_vs_paper) <= 1e-9 * max(p, 1e-300) + 1e-300
            lo, hi = wilson(k, n); txt, kind = cls(p); ri += 1
            c = {"ok": (OKB, OKF), "bad": (BADB, BADF), "warn": (WB, WF)}[kind]
            data.append([P(label if s.endswith("1000") else "", "c"), P(s, "c"), P(f"{k} / {n}", "c"), P(f"{k/n:.3f} [{lo:.3f}, {hi:.3f}]", "c"), P(f"{p0:.2f}", "c"), P(fp(p), "c"),
                         Paragraph(f'<font color="{c[1].hexval().replace("0x", "#")}"><b>{txt}</b></font>', st["c"])])
            sty.append(("BACKGROUND", (6, ri), (6, ri), c[0]))
tb = Table(data, colWidths=[w * mm for w in [19, 17, 19, 34, 12, 17, 56]])
tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HEAD), ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE), ("BOX", (0, 0), (-1, -1), 0.6, RULE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)] + sty))
SM = ParagraphStyle("sm", fontName="DV", fontSize=8.6, leading=11.5, textColor=INK, leftIndent=9, bulletIndent=0)
def blk(title, pts): return [P(f"<b>{title}</b>", "b")] + [Paragraph(x, SM, bulletText="•") for x in pts]
S = [P("Quirk Table I reproduction: decision meeting", "h1"), P("arXiv:1708.02243 · colored m<sub>Q</sub> = 1.8 TeV, Λ = 2 keV · EW m<sub>Q</sub> = 800 GeV, Λ = 4 keV · Wilson 95% intervals · p = exact binomial against the paper's value", "m"), Spacer(1, 5), tb, Spacer(1, 6)]
S += blk("Two choices we made", ["<b>Fiducial uses the barrel lengths of [27]</b> (pixel |z| &lt; 40.05 cm, SCT |z| &lt; 74.9 cm), the detector reference the paper names.",
                                 "<b>Signal uses no SCT smearing along the beam.</b> It is the only setting that brings both benchmarks to the paper's ε<sub>reco</sub> and Δs shape. The paper's text does not state it."])
S += [Spacer(1, 3)] + blk("Background", ["Converted photon + pile-up, with the detector model the paper cites ([34]: bremsstrahlung, SCT z 580 µm): <b>0 / 9139</b> in the signal region, "
                                           "i.e. &lt; 1 event at 300 fb⁻¹ (95% upper limit). The paper's level is ≈ 0.7 events, so this agrees at the upper-limit level."])
S += [Spacer(1, 3)] + blk("Finding", ["Signal and background only match the paper at <b>different</b> SCT resolutions. With one realistic resolution, either ε<sub>reco</sub> drops by 2.5–5× "
                                        "(580 µm), or the conversion background becomes ≈ 10 (our σ) to 48 (paper σ) events at 300 fb⁻¹ (no smearing)."])
EQ = ParagraphStyle("eq", fontName="DV", fontSize=9, leading=13.5, textColor=INK, leftIndent=8)
E = lambda t: Paragraph(t, EQ)
S += [PageBreak(), P("Definitions", "h2"),
      E("ε<sub>trig</sub> = N(pT of the quirk pair &gt; 200 GeV) / N(events after jet matching)"),
      E("ε<sub>fid</sub> = N(triggered, both quirks cross all 8 barrel layers inside the [27] lengths, within 25 ns) / N(triggered)"),
      E("ε<sub>reco</sub> = N(fiducial, plane found, 2 hits in 7 layers + ≥ 1 in the 8th, Δw &lt; 1 cm, Δs &lt; 0.01 cm) / N(fiducial)"),
      E("ε = ε<sub>trig</sub> × ε<sub>fid</sub> × ε<sub>reco</sub>   (paper Eq. 12)"),
      P("Colored: both R-hadrons must be charged; this is applied to the triggered events before ε<sub>fid</sub> (27 of 101 and 68 of 207 events).", "m"), Spacer(1, 3),
      E("Wilson 95% interval for k of n (ε = k/n, z = 1.96):  [ ε + z²/2n ± z √( ε(1−ε)/n + z²/4n² ) ] / (1 + z²/n)"),
      E("95% upper limit when 0 of n pass:  UL = 1 − 0.05<super>1/n</super> ≈ 3/n"),
      E("p = exact binomial probability, if the paper's value were exactly right, of a count as unlikely as ours or more"), Spacer(1, 8),
      img(fig("G1_table_I_current"), 172, "Table I efficiencies, each sample separately; bars = Wilson 95%; dashed = paper. ε<sub>reco</sub> without SCT smearing along the beam."), Spacer(1, 6),
      img(fig("G3_one_resolution_for_both"), 172, "Left: ε<sub>reco</sub> for each SCT z setting. Right: converted-photon + pile-up events in the signal region at 300 fb⁻¹ (paper σ ≈ 1 pb, 1% conversion); triangle = 95% upper limit for 0 events."),
      PageBreak(), P("Paper Figure 5: Δs and Δw", "h2"),
      img(fig("F21_fig5_current"), 176, "Δs (top) and Δw (bottom), unit area on the paper's bins; dotted = paper's Fig. 5. Signal: no SCT smearing along the beam. Converted γ + pile-up: SCT z 580 µm with the cited material model. Pile-up: existing run (SCT z 1.16 mm), all planes. Our Δw is √λ₂ (paper Eq. 11); the paper's plotted Δw appears to be ½√λ₂."),
      PageBreak(), P("Paper Figures 2, 3 and 4", "h2"),
      Table([[img(fig("F02_angular_momentum_and_separation"), 84, "Fig. 2: angular momentum L and quirk separation d for one colored event (COL2000 event 107). L reaches ≈ 9×10¹¹ ħ, the paper's ≈ 10¹² ħ scale.", cell=True),
              img(fig("F03_plane_rotation"), 84, "Fig. 3: rotation of the quirk plane stays below 10⁻⁴ rad, so the hits stay on one plane.", cell=True)]],
            colWidths=[88 * mm, 88 * mm], style=[("VALIGN", (0, 0), (-1, -1), "TOP")]),
      Spacer(1, 4), img(fig("F04v2_signal_event_displays_current"), 92, "Fig. 4: hits of one colored (COL2000 event 201) and one EW (EW2000 event 23) event in the plane's own coordinates, current setup; both pass the signal region (Δs = 28 and 37 µm). Band = ±Δw.")]

def deco(c, d):
    c.saveState(); c.setFont("DV", 7.5); c.setFillColor(MUTED)
    c.drawString(18 * mm, 10 * mm, "Quirk Table I reproduction · decision meeting · 5 October 2026")
    c.drawRightString(192 * mm, 10 * mm, f"{d.page}"); c.restoreState()
doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=15 * mm, bottomMargin=16 * mm,
                      title="Quirk Table I Reproduction", author="", subject="Literal reproduction of arXiv:1708.02243 Table I")
doc.addPageTemplates([PageTemplate("p", [Frame(18 * mm, 16 * mm, 174 * mm, 266 * mm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=deco)])
doc.build(S)
print("wrote", OUT)
