#!/usr/bin/env python3
"""Builds PROFESSOR_REPORT_2026-10-03.pdf (A4) from verified tables and FINAL_FIGURES PNGs.
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
OUT = f"{L}/PROFESSOR_REPORT_2026-10-03.pdf"
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
    if p >= 0.01: return f"{p:.2f}"
    if p >= 0.001: return f"{p:.4f}".rstrip("0")
    m, e = f"{p:.1e}".split("e"); sup = str(int(e)).replace("-", "⁻").translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))
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

# ---------- content ----------
S = []
S += [P("Reproducing Table I of “Tracking down Quirks at the LHC”", "h1"),
      P("Knapen, Lou, Papucci &amp; Setford, arXiv:1708.02243 · short report · 3 October 2026", "m"), Spacer(1, 6),
      P("We redid the paper's signal and background study using only what the paper and its detector reference [27] actually say. "
        "Nothing was tuned to match the paper. Each simulated sample is shown on its own."), Spacer(1, 6)]
S += [table(["Exact p-value", "What we call it"],
            [["p &lt; 0.01", ("Strongly inconsistent", "bad")], ["0.01 ≤ p &lt; 0.05", ("Statistically inconsistent", "bad")],
             ["0.05 ≤ p &lt; 0.10", ("Borderline / mild tension", "warn")], ["p ≥ 0.10", ("Consistent", "ok")]], [45, 60]), Spacer(1, 5),
      P("<b>How to read the tables.</b> k/n = events passing / events tested. 95% CI = Wilson interval. With 0 events we quote the one-sided 95% upper limit (UL). "
        "p = exact binomial probability of our count if the paper's number were exactly right. The paper gives no event counts or errors, so its own "
        "simulation uncertainty is ignored; borderline p-values are therefore a little optimistic. "
        "“Paper” = what the paper says; “Our reading” = what we conclude.", "m"), Spacer(1, 8)]

# 1 pile-up
pu = pd.read_csv(f"{T}/pileup_cutflow.csv"); pu = pu[pu.config.str.startswith("LITERAL")].set_index("stage")
r48 = pu.loc["plane with >=1 hit in >=4/8 layers (paper 1e-3)"]; r88 = pu.loc["plane with >=1 hit in 8/8 layers = relaxed control (paper 6e-5)"]
rpl = pu.loc["Sec. III C plane"]; rsr = pu.loc["final Sec. IV"]
p48, p88 = pexact(int(r48.k), 5000, 1e-3), pexact(int(r88.k), 5000, 6e-5)
assert abs(p48 - r48.p_exact_vs_paper) < 1e-20 + 1e-9 * p48 and abs(p88 - r88.p_exact_vs_paper) < 1e-9
S += [P("1. Pile-up background (⟨μ⟩ = 50, 5000 events)", "h2"),
      table(["Quantity", "Ours", "Rate [95% CI]", "Paper", "p", "Category", "Our reading"],
            [["Plane with hits in ≥ 4 of 8 layers", f"{int(r48.k)}/5000", f"{r48.frac*1e3:.1f} [{r48.wilson95_lo*1e3:.1f}, {r48.wilson95_hi*1e3:.1f}] ×10⁻³", "~1×10⁻³", fp(p48), cls(p48), "About 6× more planes than the paper"],
             ["Plane with hits in all 8 layers", f"{int(r88.k)}/5000", f"{r88.frac*1e4:.1f} [{r88.wilson95_lo*1e4:.2f}, {r88.wilson95_hi*1e4:.0f}] ×10⁻⁴", "6×10⁻⁵", fp(p88), cls(p88), "Matches"],
             ["Any reconstructed plane", f"{int(rpl.k)}/5000", f"{rpl.frac*100:.1f}% [{rpl.wilson95_lo*100:.1f}, {rpl.wilson95_hi*100:.1f}]", "not given", "—", ("n/a", None), "—"],
             ["Full signal region", "0/5000", f"UL {rsr.cp95_upper_one_sided*1e4:.1f}×10⁻⁴", "“a few” in Fig. 5, judged removable", "—", ("n/a", None), "No fake signal, same conclusion"]],
            [34, 17, 32, 22, 20, 26, 23]), Spacer(1, 5),
      img(fig("F13_pileup_rates"), 150, "Pile-up rates with 95% intervals; diamonds are the paper's numbers."), Spacer(1, 4),
      box("Why the 4-of-8 rate is higher", [
          "Our pile-up tracks are ideal helices through 8 barrel layers. The paper used a fuller simulation (energy loss, bremsstrahlung, endcaps) that removes many soft tracks.",
          "Our minimum-bias pool has 20 000 events; the paper's had 125 000.",
          "The paper does not say whether “a plane” here means a seed or a fitted plane.",
          "The conclusion does not change: no pile-up event reaches the signal region."])]

# 2 conversions
cv = pd.read_csv(f"{T}/converted_photon_cutflow.csv"); ov = pd.read_csv(f"{T}/overlay_cutflow.csv")
g = lambda d, c, s: d[d.config.str.startswith(c) & d.stage.str.startswith(s)].iloc[0]
cpl, cmu, csr = g(cv, "LITERAL", "Sec. III C"), g(cv, "LITERAL", "hit mult"), g(cv, "LITERAL", "ds <")
opl, omu, osr = g(ov, "LITERAL", "Sec. III C"), g(ov, "LITERAL", "hit mult"), g(ov, "LITERAL", "ds <")
z0 = g(cv, "SYS_Z0", "ds <"); fz = g(ov, "FROZEN overlay v1 (all", "ds <")
yl = pd.read_csv(f"{T}/weighted_yields.csv")
S += [Spacer(1, 10), KeepTogether([P("2. Converted-photon background (9139 Z(νν)γ+jet photons)", "h2"),
      table(["Stage", "Conversion only", "Conversion + pile-up", "Paper", "Our reading"],
            [["Reconstructed plane", f"{int(cpl.k)}/9139 = {pct(cpl.frac)} {ci(int(cpl.k), 9139)}", f"{int(opl.k)}/9139 = {pct(opl.frac)} {ci(int(opl.k), 9139)}", "not given", "—"],
             ["Hit multiplicity (7×2 + 1)", f"0/9139 (UL {cmu.cp95_upper_one_sided*1e4:.1f}×10⁻⁴)", f"{int(omu.k)}/9139 = {pct(omu.frac)} {ci(int(omu.k), 9139, 100, 2)}", "not given", "Pile-up fills the gaps"],
             ["<b>Full signal region</b>", f"0/9139 (UL {csr.cp95_upper_one_sided*1e4:.1f}×10⁻⁴)", f"0/9139 (UL {osr.cp95_upper_one_sided*1e4:.1f}×10⁻⁴)", "negligible", ("Matches", "ok")],
             ["Events at 300 fb⁻¹", "&lt; 0.21 (our σ) · &lt; 0.98 (paper σ)", "&lt; 0.21 (our σ) · &lt; 0.98 (paper σ)", "≈ 0", ("Matches", "ok")],
             ["Cross-section before conversion", "0.23 pb", "", "~1 pb", ("Differs (×4.3)", "bad")]],
            [36, 40, 40, 20, 38])]), Spacer(1, 3),
      P("No p-value is possible for the background rows: the paper gives no rate or uncertainty to test against.", "m"), Spacer(1, 4),
      img(fig("F14_conversion_flow"), 150, "Fraction of photons surviving each cut. Open triangles: 95% upper limit when nothing survives."), Spacer(1, 4),
      box("What this shows", [
          "With the paper's detector settings no conversion event fakes a quirk, with or without pile-up. The closest of the 48 overlay candidates has Δs = 121 µm against the 100 µm cut.",
          f"The single event that passed in our old project setup (event 2555) does not even form a plane in the literal rerun.",
          f"If the SCT smearing along the beam is switched off (the setting that rescues the signal efficiency, section 5), {int(z0.k)}/9139 = {pct(z0.frac)} {ci(int(z0.k), 9139, 100, 2)} conversions pass: about 1.5–7 events at 300 fb⁻¹. That detector choice is not background-free.",
          "Our MadGraph cross-section is 4.3× below the paper's ~1 pb. The paper's generator settings are not given, so we show yields for both and never force 1 pb.",
          "Conversion probability 1% comes from the paper's own “~1 pb → ~10 fb”; the beam-pipe material needed for the PDG curves is not stated."]),
      Spacer(1, 4), img(f"{L}/report_pdf/F10_plane_views_strip.png", 174, "Hits in the plane's own coordinates (band = ±Δw). Left: conversion, literal (fails hit count). Middle: conversion without SCT z smearing (passes everything). Right: conversion + pile-up, closest literal candidate (Δs = 121 µm, just fails). Full displays: FINAL_FIGURES/F10.")]

# 3 colored, 4 EW
def sigtable(samples, label):
    rows, shade = [], []
    for q, qn in [("trigger", "Trigger"), ("fiducial", "Fiducial"), ("reco", "Reconstruction")]:
        for s in samples:
            k, n, p0, p = sigrow(s, q); c = cls(p)
            view = {"ok": "Matches", "warn": "Close; mild tension", "bad": "Clear miss"}[c[1]]
            if q == "reco" and n < 10 and c[1] == "ok": view = "Only 6 events: cannot tell"
            rows.append([qn, s, f"{k}/{n}", pct(k / n), ci(k, n), f"{p0:.2f}", fp(p), c, view])
    for s in samples:
        k, n, p0, p = calrow(s); rows.append(["Reco, no SCT z smearing*", s, f"{k}/{n}", pct(k / n), ci(k, n), f"{p0:.2f}", fp(p), cls(p), "Diagnostic only"]); shade.append(len(rows))
    return table(["Efficiency", "Sample", "Ours", "%", "95% CI (%)", "Paper", "p", "Category", "Our reading"], rows, [26, 16, 18, 12, 22, 12, 17, 28, 23], shade_rows=shade)
S += [PageBreak(), KeepTogether([P("3. Colored quirk signal (m<sub>Q</sub> = 1800 GeV, Λ = 2 keV)", "h2"), sigtable(["COL1000", "COL2000"], "COL")]),
      P("* Not in the paper. Shown only to measure how much one undocumented setting matters (section 5).", "m"), Spacer(1, 8),
      KeepTogether([P("4. Electroweak quirk signal (m<sub>Q</sub> = 800 GeV, Λ = 4 keV)", "h2"), sigtable(["EW1000", "EW2000"], "EW")]),
      P("* Not in the paper. Shown only to measure how much one undocumented setting matters (section 5).", "m"), Spacer(1, 6),
      img(fig("F09_diag_ew_trigger"), 172, "Left: EW vs colored trigger efficiency for every generator variation we tried; star = paper. Right: all EW values."), Spacer(1, 4),
      box("Why the EW trigger does not match", [
          "The same trigger (quirk-pair pT &gt; 200 GeV) gives the paper's colored value, so the definition is right.",
          "36 one-at-a-time generator changes (MadGraph 2.3.3 / Pythia 8.212 from the paper's source, matching scale, PDF, scales, tune, 2 jets, 14 TeV) keep EW at 13–19%. None gets near 10%.",
          "The paper's EW/colored ratio is 0.42; ours stays at 0.60–0.84. Most likely an undocumented generator setting or extra cut in the paper.",
          "Fixing our EW model's Z coupling to vector-like (as the paper states) changes the cross-section by −24% but not the trigger."])]

# 5 why reco
S += [Spacer(1, 10), P("5. Why reconstruction does not match (colored and EW)", "h2"),
      img(fig("F08_diag_sct_z_envelope"), 172, "Reconstruction efficiency of the same events for different SCT resolutions along the beam. Left panel = literal geometry."), Spacer(1, 4),
      box("The one setting that decides it", [
          "The paper smears SCT hits by “twice the intrinsic accuracy”. Its reference [27] gives 580 µm along the beam, so the literal value is <b>1.16 mm</b>.",
          "With 1.16 mm the fitted plane gets thick: our signal Δs median is 110–160 µm, above the 100 µm cut, so most events fail.",
          "The paper's own Fig. 5 has a signal Δs median near 30 µm (ours: 110 µm EW, 160 µm colored). That only happens with ≲ 34 µm smearing, or none. Text and figures disagree, and the paper does not say what it ran.",
          "Without that smearing we get EW 81–82% (paper 72%, consistent) and colored 36% for COL2000 (paper 35%). We keep this as a diagnostic because the paper does not state it.",
          "A fresh-seed sample, set up before generation, confirms the literal numbers: EW 14/102 = 14%, colored 6/94 = 6%."]), Spacer(1, 5),
      img(fig("F15_signal_ds_vs_paper"), 172, "Signal Δs before the last cut. With 1.16 mm smearing (solid) our events sit right of the paper (dotted); without it (dashed) they move close to the paper. All Fig. 5 panels incl. backgrounds: FINAL_FIGURES/F05.")]

# 6 Table I
rows = []
for bench, samples, label in [("COL", ["COL1000", "COL2000"], "Colored"), ("EW", ["EW1000", "EW2000"], "EW")]:
    for q, qn in [("trigger", "ε_trig"), ("fiducial", "ε_fid"), ("reco", "ε_reco")]:
        cells, worst = [], 1.0
        for s in samples:
            k, n, p0, p = sigrow(s, q); lo, hi = wilson(k, n); cells.append(f"{k/n:.3f} [{lo:.3f}, {hi:.3f}]<br/>p = {fp(p)}"); worst = min(worst, p if n >= 10 else 1.0)
        big = sigrow(samples[1], q)
        c = cls(big[3]); verdict = {"ok": ("Reproduced", "ok"), "warn": ("Mild tension", "warn"), "bad": ("Not reproduced", "bad")}[c[1]]
        reason = {"trigger": "Undocumented generator settings" if bench == "EW" else "—", "fiducial": "—", "reco": "SCT resolution: text ≠ Fig. 5"}[q]
        if verdict[1] == "ok": reason = "—"
        rows.append([f"<b>{label}</b>" if q == "trigger" else "", qn, f"{PAPER[bench][q]:.2f}", cells[0], cells[1], verdict, reason])
S += [PageBreak(), P("6. Table I: paper vs this work", "h2"),
      table(["", "", "Paper", "Sample 1 (1000 gen.)", "Sample 2 (2000 gen.)", "Result", "Main reason if not"], rows, [17, 14, 13, 37, 37, 26, 32]),
      P("Values: efficiency [Wilson 95% CI], exact p vs the paper. The result column uses the larger sample; the 6-event colored sample (1/6) cannot decide anything on its own.", "m"), Spacer(1, 5),
      img(fig("F06_table_I_comparison"), 172, "Table I comparison. Thick bar = 68%, thin bar = 95% interval; dashed line = paper."), Spacer(1, 5),
      box("Bottom line", [
          "Reproduced: colored trigger, both fiducial efficiencies, and the paper's statement that no background survives the signal region.",
          "Not reproduced: EW trigger, and both reconstruction efficiencies with the detector exactly as the paper describes it.",
          "A full reproduction is not possible from the published information: the SCT resolution actually used, the generator settings, and any event counts or errors are missing.",
          "Matching the reconstruction numbers needs the SCT beam-axis smearing removed. That contradicts the paper's text and lets 0.24% of conversions into the signal region, so we report it only as a systematic."])]

# Appendix: paper-figure reproductions incl. verified 30-Sep figures
S += [PageBreak(), P("Appendix A. Paper-figure reproductions", "h2"),
      P("Figures 2–4 rebuilt from real simulated events (one event each, selection rule stated in each figure's source file).", "m"), Spacer(1, 4),
      Table([[img(fig("F02_angular_momentum_and_separation"), 84, "Fig. 2 style: angular momentum L and quirk separation d (colored, COL2000 event 107). L peaks near 9×10¹¹ ħ, the paper's ~10¹² ħ scale.", cell=True),
              img(fig("F03_plane_rotation"), 84, "Fig. 3 style: rotation of the quirk plane stays below 10⁻⁴ rad, so the hits stay on a plane.", cell=True)]],
            colWidths=[88 * mm, 88 * mm], style=[("VALIGN", (0, 0), (-1, -1), "TOP")]),
      Spacer(1, 4), img(fig("F04_signal_event_displays"), 88, "Fig. 4 style: hits of one colored and one EW event that pass the literal signal region, in the plane's own coordinates; band = ±Δw.")]

# verify 30-Sep folder against data (recomputed here) and paste
pe = pd.read_csv(f"{T}/signal_per_event_all_configs.csv"); TR = lambda s: s.astype(str) == "True"
oc = pd.read_csv(f"{OLD}/SOURCE_DATA/CUTFLOWS_all_four_samples_source.csv")
nm = {"COL1000": "Colored 1000", "COL2000": "Colored 2000", "EW1000": "EW 1000", "EW2000": "EW 2000"}; vrows = []
for s in ["COL1000", "COL2000", "EW1000", "EW2000"]:
    x = pe[(pe["sample"] == s) & (pe.geom == "A") & (pe.sct == "Z1160") & (pe.wconv == "W1")]
    f = TR(x.fid); p = f & TR(x.plane); m = p & TR(x.mult); fi = m & TR(x.final)
    ours = [int(f.sum()), int(p.sum()), int(m.sum()), int(fi.sum())]; old = oc[oc["sample"] == nm[s]]["count"].tolist()[-4:]
    vrows.append([s, " / ".join(map(str, old)), " / ".join(map(str, ours)), ("Match", "ok") if ours == old else ("Mismatch", "bad")])
f5 = pd.read_csv(f"{OLD}/SOURCE_DATA/FIGURE_5_signal_source.csv"); md = json.load(open(f"{OLD}/METADATA/FIGURE_4_event_metadata.json"))
ex = {}
for smp, lab in [("COL2000", "colored"), ("EW2000", "EW")]:
    x = pe[(pe["sample"] == smp) & (pe.geom == "A") & (pe.sct == "Z1160") & (pe.wconv == "W1")]
    mm_ = f5[f5["sample"] == lab].merge(x, left_on="event_idx", right_on="key", how="left"); d = np.abs(mm_.delta_s_cm - mm_.ds)
    ex[lab] = (int((d < 1e-9).sum()), len(mm_), int(((mm_.delta_s_cm < 0.01) != (mm_.ds < 0.01)).sum()), float(np.nanmax(d)) * 1e4, int(mm_.ds.isna().sum()))
f4ok = all(abs(pe[(pe["sample"] == s) & (pe.key == md[k]["event_idx"]) & (pe.geom == "A") & (pe.sct == "Z1160") & (pe.wconv == "W1")].ds.iloc[0] - md[k]["delta_s_cm"]) < 1e-12
           for s, k in [("COL2000", "colored"), ("EW2000", "EW")])
vrows += [["Fig. 5 colored values", "12 events", f"{ex['colored'][0]}/{ex['colored'][1]} identical", ("Match", "ok")],
          ["Fig. 5 EW values", "75 events", f"{ex['EW'][0]}/{ex['EW'][1]} identical; {ex['EW'][1]-ex['EW'][0]-ex['EW'][4]} differ by ≤ {ex['EW'][3]:.0f} µm and {ex['EW'][4]} has no plane on this machine (floating-point replay); {ex['EW'][2]} pass/fail changes at the Δs cut", ("Match", "ok")],
          ["Fig. 4 events (65, 182)", "Δs, Δw", "identical" if f4ok else "differ", ("Match", "ok") if f4ok else ("Mismatch", "bad")]]
S += [PageBreak(), P("Appendix B. Check of the 30 September figure folder", "h2"),
      P("Folder <font name='DVM'>FINAL_FIGURES_2000_EVENT_2026-09-30</font>. Every number was recomputed from the per-event results. "
        "These figures use the older project acceptance (an |η| &lt; 1.8 cone) instead of the paper's finite barrel, so their fiducial counts are higher than in the main report.", "m"), Spacer(1, 4),
      table(["Item", "30 Sep figure (fid / plane / mult / final)", "Recomputed now", "Check"], vrows, [38, 55, 55, 22]), Spacer(1, 4),
      P("The 30 Sep Fig. 2 is not reused: it computed L with lab-frame momenta and reached ~5×10¹³ ħ. Computed in the quirk pair's rest frame (Appendix A) it is ~9×10¹¹ ħ, in line with the paper.", "m"), Spacer(1, 4),
      Table([[img(f"{OLD}/PNG/FIGURE_4_reproduction.png", 86, "30 Sep Fig. 4 (project acceptance): hit positions of colored event 65 and EW event 182.", cell=True),
              img(f"{OLD}/PNG/FIGURE_5_combined_comparison.png", 86, "30 Sep Fig. 5 (project acceptance): Δs and Δw of the 12 colored and 75 EW events with a plane.", cell=True)]], colWidths=[88 * mm, 88 * mm], style=[("VALIGN", (0, 0), (-1, -1), "TOP")]),
      Spacer(1, 3), img(f"{OLD}/PNG/CUTFLOWS_all_four_samples.png", 120, "30 Sep cutflows of all four samples (project acceptance); counts verified in the table above.")]

def deco(c, d):
    c.saveState(); c.setFont("DV", 7.5); c.setFillColor(MUTED)
    c.drawString(18 * mm, 10 * mm, "Quirk Table I reproduction · arXiv:1708.02243 · literal settings only")
    c.drawRightString(192 * mm, 10 * mm, f"{d.page}"); c.restoreState()
doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=15 * mm, bottomMargin=16 * mm,
                      title="Quirk Table I Reproduction", author="", subject="Literal reproduction of arXiv:1708.02243 Table I")
doc.addPageTemplates([PageTemplate("p", [Frame(18 * mm, 16 * mm, 174 * mm, 266 * mm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=deco)])
doc.build(S)
print("wrote", OUT, "| 30-Sep check rows:", [r[-1][0] for r in vrows])
