#!/usr/bin/env python3
"""Professor package (2026-11-18): 8 landscape slides as one PDF, built with reportlab (no LaTeX; as the 05 technical report).
Every number is copied from RESULTS_07_LARGE_SAMPLES.md / tables (X08, X10, X11, X12, X13, S01); figures are the ROOT PNGs, read, not changed.
Run: /home/rafia/venvs/f6fast/bin/python build_slides.py  ->  PROFESSOR_SLIDES_2026-11-18.pdf"""
import os
from PIL import Image as PImage
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); OUT = f"{HERE}/PROFESSOR_SLIDES_2026-11-18.pdf"
F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("S", F + "DejaVuSans.ttf")); pdfmetrics.registerFont(TTFont("SB", F + "DejaVuSans-Bold.ttf"))
registerFontFamily("S", normal="S", bold="SB", italic="S", boldItalic="SB")
PW, PH = 297 * mm, 167 * mm; M = 12 * mm; W = PW - 2 * M
INK, INK2, BLUE, LINE, ALT = (colors.HexColor(c) for c in ("#14213D", "#4A5568", "#2A6FDB", "#C9D1DC", "#EEF1F5"))
ST = {"eye": ParagraphStyle("eye", fontName="SB", fontSize=8.5, leading=11, textColor=BLUE),
      "h": ParagraphStyle("h", fontName="SB", fontSize=17, leading=21, textColor=INK, spaceAfter=6),
      "b": ParagraphStyle("b", fontName="S", fontSize=10, leading=13.5, textColor=INK2, spaceAfter=4),
      "bl": ParagraphStyle("bl", fontName="S", fontSize=10, leading=13.5, textColor=INK2, leftIndent=10, bulletIndent=0, spaceAfter=3),
      "n": ParagraphStyle("n", fontName="S", fontSize=8, leading=10.5, textColor=INK2),
      "c": ParagraphStyle("c", fontName="S", fontSize=8.8, leading=11, textColor=INK),
      "ch": ParagraphStyle("ch", fontName="SB", fontSize=8.8, leading=11, textColor=INK),
      "big": ParagraphStyle("big", fontName="SB", fontSize=26, leading=31, textColor=INK, spaceAfter=10),
      "lede": ParagraphStyle("lede", fontName="S", fontSize=13, leading=18, textColor=INK, spaceAfter=10)}
FIG = {"geo": f"{R}/FIGURES_GEOMETRY_2026-11-17/GEO1_rz_ideal_vs_atlas/GEO1_rz_ideal_vs_atlas.png",
       "g09": f"{R}/FIGURES_ROOT_2026-11-17/G09_reach_summary/G09_reach_summary.png",
       "x02": f"{R}/compare/FIGURES_X02/X02_contours_ideal_vs_atlas_332fb/X02_contours_ideal_vs_atlas_332fb.png",
       "g08": f"{R}/FIGURES_ROOT_2026-11-17/G08_background_vs_pileup/G08_background_vs_pileup.png",
       "s06": f"{R}/FIGURES_SIGNAL_2026-11-18/S06_merge_ratio_vs_mass/S06_merge_ratio_vs_mass.png"}
P = lambda t, s="b": Paragraph(t, ST[s])
B = lambda t: Paragraph(t, ST["bl"], bulletText="•")


def img(key, w=None, h=None):
    iw, ih = PImage.open(FIG[key]).size
    if w and h: s = min(w / iw, h / ih)
    else: s = (w / iw) if w else (h / ih)
    return Image(FIG[key], width=iw * s, height=ih * s)


def tab(rows, widths, right_from=1):
    data = [[Paragraph(str(c), ST["ch" if i == 0 else "c"]) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, 0), 0.8, INK), ("LINEBELOW", (0, 1), (-1, -1), 0.3, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LEFTPADDING", (0, 0), (-1, -1), 4)]))
    return t


def two(left, right, wl):
    t = Table([[left, right]], colWidths=[wl, W - wl]); t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)])); return t


def head(eye, h): return [P(eye, "eye"), Spacer(1, 2), P(h, "h")]


def foot(c, d):
    c.saveState(); c.setFont("S", 7); c.setFillColor(INK2)
    c.drawString(M, 6 * mm, "Quirk coplanarity · ATLAS Run 2 inner detector (07) · status 18 November 2026"); c.drawRightString(PW - M, 6 * mm, str(d.page)); c.restoreState()


S = []
# 1 cover
S += [Spacer(1, 18 * mm), P("STATUS FOR DISCUSSION · 18 NOVEMBER 2026", "eye"), Spacer(1, 4),
      P("Quirk coplanarity search in the real ATLAS inner detector", "big"),
      P("With the realistic SCT resolution, the ATLAS geometry, end-caps included, reaches <b>1697 GeV</b> (colored) and <b>768 GeV</b> (EW) at 332 fb⁻¹. "
        "That is 106 and 137 GeV beyond the ideal barrel. The converted-photon background stays below 0.2 events up to μ = 50 with nominal pixel merging.", "lede"),
      P("Stage 2 · Run 3 · ATLAS vs Stage 1 · Run 3 · Ideal · 13.6 TeV · the same 10k-generated signal events per mass point · "
        "all numbers from 07_atlas_real_geometry/RESULTS_07_LARGE_SAMPLES.md", "n"), PageBreak()]
# 2 geometry
S += head("GEOMETRY", "The ATLAS inner detector adds end-cap disks to the ideal barrel")
S += [two(img("geo", h=112 * mm), [P("<b>Same barrel, plus disks</b>"),
      B("Ideal (Knapen et al.): 8 barrel layers, radii and lengths from ATLAS."),
      B("ATLAS Run 2 ID: the same 8 layers + 2 × 3 pixel disks + 2 × 9 SCT disks, with ATLAS material."),
      B("Forward quirk pairs now leave 8 measurements on disks, so more events are fiducial. Every gain comes from rows with an end-cap element."),
      Spacer(1, 4), P("EW 800 GeV, Λ = 4 keV: fiducial fraction 0.69 (ATLAS) vs 0.26 (Ideal); selection after fiducial 0.22 vs 0.28.", "n")], 150 * mm), PageBreak()]
# 3 headline
S += head("HEADLINE · SCT 17 µm × 580 µm (A580) · 332 fb⁻¹", "ATLAS reaches 106 GeV (colored) and 137 GeV (EW) further than the ideal barrel")
t3 = tab([["exclusion / discovery [GeV]", "μ = 0", "μ = 20", "μ = 50"],
          ["colored, ATLAS", "1697 / 1618", "1697 / 1618", "1697 / 1613"], ["colored, Ideal", "1591 / 1515", "1591 / 1515", "1591 / 1515"],
          ["EW, ATLAS", "768 / 681", "768 / 681", "768 / 675"], ["EW, Ideal", "631 / 560", "631 / 560", "631 / 560"]], [44 * mm, 30 * mm, 30 * mm, 30 * mm])
S += [two([t3, Spacer(1, 6),
           P("Each geometry with its own converted-photon background (central MC value). Exclusion: 95% CL<sub>s</sub>, 3.0 events needed at every μ. Discovery: max(5, Asimov Z = 5).", "n"), Spacer(1, 4),
           P("Best case σ<sub>long</sub> = 0 (Z0), for comparison: colored ATLAS 1871 → 1589 GeV and EW 994 → 690 GeV from μ = 0 to 50; its background grows to 69 events.", "n")],
          img("g09", h=118 * mm), 140 * mm), PageBreak()]
# 4 background
S += head("BACKGROUND · Z(νν̄)γ CONVERSIONS, 90 980 PHOTONS (100k GENERATED)", "The converted-photon background stays below 0.2 events, and every pass needs pile-up")
t4 = tab([["events at 332 fb⁻¹", "μ = 0", "μ = 20", "μ = 50"],
          ["A580, ATLAS", "0 (UL 0.13)", "0.069 ± 0.033", "0.198 ± 0.052"], ["A580, Ideal", "0 (UL 0.025)", "0.092 ± 0.028", "0.108 ± 0.030"],
          ["Z0, ATLAS", "0.34", "27.0", "69.2"], ["Z0, Ideal", "0.25", "9.2", "16.4"]], [36 * mm, 30 * mm, 30 * mm, 30 * mm])
S += [two([t4, Spacer(1, 4), P("A580 passing rows: ATLAS 12 / 33, Ideal 11 / 13 (μ = 20 / 50). Z0 rows use 9 130 photons. Z(νν̄)+jets is not simulated.", "n"), Spacer(1, 6),
           P("<b>Mechanism</b>"), B("No photon passes at μ = 0."),
           B("Most passes are near-misses: a good plane with 14 hits, one short of the cut. One or two pile-up hits complete it."),
           B("So pile-up plus any MET event with a two-track object is a potential background; that part is not measured yet.")],
          [img("g08", w=W - 132 * mm), Spacer(1, 4),
           P("<b>Old 9 130-photon value checked.</b> The same photons with the server pile-up pool give 2 passes instead of 5 (100k prediction 1.1); only 1 photon passes in both. "
             "Which near-miss is completed is decided by the pile-up overlay: the old 0.42 events was an overlay fluctuation, not a different photon sample.", "n")], 132 * mm), PageBreak()]
# 5 merging scenarios
S += head("PIXEL MERGING AS ONE CORRELATED VARIATION (ATLAS, μ = 50)", "“Background < 1” is marginal only in the weakest-merging worst case")
t5 = tab([["scenario", "b [events]", "s<sub>excl</sub> / s<sub>disc</sub>", "colored excl. / disc. [GeV]", "EW excl. / disc. [GeV]"],
          ["nominal (a = 1)", "0.20", "3.0 / 5.16", "1697 / 1613", "768 / 675"],
          ["a = 0, main (b × 1.59, Z0 ratio)", "0.32", "3.0 / 5.86", "1724 (+27) / 1621 (+8)", "800 (+32) / 690 (+15)"],
          ["a = 0, pessimistic (b × 4.4, A580 ratio)", "0.87", "4.17 / 7.97", "1670 (−27) / 1576 (−37)", "746 (−22) / 640 (−35)"],
          ["a = 2 (b × 0.74 / 0.49)", "0.15 / 0.10", "3.0 / 5.0", "1666 (−31) / 1590 (−23)", "736 (−32) / 645 (−30)"]],
         [70 * mm, 26 * mm, 30 * mm, 72 * mm, 62 * mm])
S += [t5, Spacer(1, 8),
      B("Signal and background change together: a = 0 (only same-pixel hits merged, −50%) gives signal +16–26% and more background; a = 2 (+100%) lowers both."),
      B("Background ratios from the server runs (same photons, machine and pool): Z0 114.3 / 71.8 / 53.3 events (1189 / 663 / 584 rows); A580 0.35 / 0.080 / 0.039 (12 / 3 / 1 rows)."),
      B("In the pessimistic a = 0 case b ≈ 0.9 rounds to one observed event: the exclusion needs 4.17 events and the signal gain does not compensate it."),
      B("At μ = 0 and 20 the exclusion moves only with the signal: +27 / −31 GeV (colored), +32 / −32 GeV (EW). Ideal moves the same way."), PageBreak()]
# 6 threshold sensitivity
S += head("SENSITIVITY · MULTIPLICITY THRESHOLD T", "T = 15 stays the baseline; T = 16 is a fallback")
t6 = tab([["μ = 50, 332 fb⁻¹", "T = 14", "T = 15", "T = 16"],
          ["A580 background, ATLAS", "0.88", "0.198", "0.008"], ["A580 background, Ideal", "0.56", "0.108", "0.008"], ["Z0 background, ATLAS", "172", "69.2", "7.5"],
          ["A580 signal, ATLAS (EW 600–800, col. 1500–1800)", "× 1.08–1.10", "1", "× 0.79–0.83"]], [64 * mm, 24 * mm, 20 * mm, 24 * mm])
S += [two([t6, Spacer(1, 6), B("The selection is one-hit sensitive: T = 14 makes Z0 large even without pile-up (0.34 → 48.5 events at μ = 0)."),
           B("T = 16 removes most background but costs 13–21% of the signal, −32 to −37 GeV of A580 exclusion reach (ATLAS).")],
          [img("s06", w=W - 136 * mm), Spacer(1, 3),
           P("Signal ratio to production vs mass (paired errors). Merge a = 0: × 1.16–1.26; a = 2: × 0.80–0.84. Slightly larger at lower mass (1.6–2.0σ), the same in both geometries.", "n")],
          136 * mm), PageBreak()]
# 7 budget
S += head("UNCERTAINTY BUDGET · A580 EXCLUSION REACH, ATLAS / IDEAL", "Pixel merging is the largest entry, about ±30 GeV")
t7 = tab([["source", "variation", "colored [GeV]", "EW [GeV]"],
          ["pixel merging, signal + background (μ = 0 / 20)", "a = 0 / a = 2", "+27 −31 / +29 −31", "+32 −32 / +39 −36"],
          ["pixel merging, signal + background (μ = 50, ATLAS)", "a = 0 main, a = 0 pessimistic / a = 2", "+27, −27 / −31", "+32, −22 / −32"],
          ["background MC statistics (A580)", "central b vs MC 95% UL", "0", "0"], ["pile-up pool", "~12% on b", "0", "0"],
          ["laptop vs server numerics", "same events, two machines", "≤ 4", "≤ 4"],
          ["quirk multiple scattering (not in the integrator)", "Highland: initial / turning-point momentum", "−4 to −9 / −11 to −32", "same"],
          ["multiplicity threshold (a different selection)", "T = 16 fallback", "−32 / −32", "−37 / −38"]], [86 * mm, 78 * mm, 54 * mm, 50 * mm])
S += [t7, Spacer(1, 8), B("The merge effect is the same in both geometries, so the ATLAS gain over Ideal (+106 colored, +137 EW GeV) is not affected."),
      B("Signal MC statistics: the ±1σ Wilson band is drawn in figure G09 (slide 3)."), PageBreak()]
# 8 questions
S += head("DECISIONS NEEDED", "Four open questions before the next step")
q = [("1 · Z(νν̄)+jets", "Simulate it, or keep the estimate?", "47 × the Zγ cross-section; it counts only if it makes a near-miss two-track object. Not simulated yet."),
     ("2 · Pile-up-only background", "Run the factorised measurement?", "Rates needed to about 10⁻⁷ per event. About 2 days of coding and about 11 h on 160 server cores."),
     ("3 · 13 TeV, 10k signal", "Generate it for the 13 TeV stages?", "Stage 0 and the Run 2 stages still use 2k samples (kept: the frozen 06 figures need them). Code ready, not run."),
     ("4 · Threshold T = 16", "Keep T = 15, with T = 16 as a fallback?", "T = 16: A580 background 0.2 → 0.008 events at μ = 50, but −13 to −21% signal (−32 to −38 GeV).")]
cell = lambda a: [P(f"<font color='#C9531F'><b>{a[0]}</b></font>", "b"), P(f"<b>{a[1]}</b>", "b"), P(a[2], "b")]
tq = Table([[cell(q[0]), cell(q[1])], [cell(q[2]), cell(q[3])]], colWidths=[W / 2, W / 2])
tq.setStyle(TableStyle([("BOX", (0, 0), (0, 0), 0.5, LINE), ("BOX", (1, 0), (1, 0), 0.5, LINE), ("BOX", (0, 1), (0, 1), 0.5, LINE), ("BOX", (1, 1), (1, 1), 0.5, LINE),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
S += [tq, Spacer(1, 8), P("Also: GNN tracking on the same ATLAS geometry and events is being set up (folder 08), for a coplanarity vs GNN comparison. "
                          "Run 2 luminosity is kept at 139 fb⁻¹ on purpose (frozen 06 results); 140.1 fb⁻¹ would add 0.8% to every Run 2 count.", "n")]

doc = BaseDocTemplate(OUT, pagesize=(PW, PH), leftMargin=M, rightMargin=M, topMargin=10 * mm, bottomMargin=12 * mm,
                      title="Quirk coplanarity: ATLAS geometry status", author="07_atlas_real_geometry")
doc.addPageTemplates([PageTemplate(id="s", frames=[Frame(M, 12 * mm, W, PH - 22 * mm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=foot)])
doc.build(S); print("SLIDES_PDF", OUT)
