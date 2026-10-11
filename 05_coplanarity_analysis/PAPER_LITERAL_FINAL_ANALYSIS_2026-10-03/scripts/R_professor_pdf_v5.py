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
OUT = f"{L}/PROFESSOR_REPORT_2026-10-04_v5.pdf"
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

# ---------- content (v3: final results only) ----------
OK_LABEL = "No statistically significant inconsistency"
def cls(p):
    if p is None or np.isnan(p): return ("n/a", None)
    if p < 0.01: return ("Strongly inconsistent", "bad")
    if p < 0.05: return ("Statistically inconsistent", "bad")
    if p < 0.10: return ("Borderline / mild tension", "warn")
    return (OK_LABEL, "ok")
V = pd.read_csv(f"{T}/v2_primary_table_I.csv"); SB = pd.read_csv(f"{T}/v2_finite_barrel_sensitivity.csv"); MX = pd.read_csv(f"{T}/acceptance_longitudinal_matrix.csv")
PU = pd.read_csv(f"{T}/v3_pileup_primary.csv"); CV3 = pd.read_csv(f"{T}/v3_conversion_primary.csv")
TRT = {"z1160": "SCT z 1160 um (2x580, INFERRED)", "z580": "SCT z 580 um (1x Ref.[27], sensitivity)", "z0": "no SCT z smearing (UNDOCUMENTED)"}
TL = {"z1160": "1.16 mm", "z580": "0.58 mm", "z0": "none"}
def vrow(s, q, t="—"):
    r = V[(V["sample"] == s) & (V.quantity == q) & (V.treatment == t)].iloc[0]; k, n = int(r.k), int(r.n)
    p0 = PAPER["COL" if s.startswith("COL") else "EW"][{"trigger": "trigger", "fiducial": "fiducial", "reconstruction": "reco"}[q]]
    p = pexact(k, n, p0); assert abs(p - r.p_exact_vs_paper) <= 1e-9 * max(p, 1e-300) + 1e-300
    return k, n, p0, p
def epm(k, n): e = k / n; return f"{e:.3f} ± {np.sqrt(e*(1-e)/n):.3f}"
def w95(k, n):
    lo, hi = wilson(k, n)
    return f"[{lo:.3f}, {hi:.3f}]" if hi >= 0.01 else f"[{sci(lo)}, {sci(hi)}]"
def ulf(k, n): return f"UL {sci(ul(k, n))}"
EQ = ParagraphStyle("eq", fontName="DV", fontSize=9, leading=13, textColor=INK, leftIndent=10)
E = lambda t: Paragraph(t, EQ)
S = []
S += [P("Reproducing Table I of “Tracking down Quirks at the LHC”", "h1"),
      P("Knapen, Lou, Papucci &amp; Setford, arXiv:1708.02243 · paper-stated acceptance with an inferred longitudinal detector model · 3 October 2026", "m"), Spacer(1, 6),
      box("Setup", [
          "<b>Stated in the paper or its detector reference [27]:</b> pixel and SCT barrel only (|η| ≲ 1.8); pixel-centre hits; neighbouring pixels merged; SCT 34 µm across (2 × 17 µm); 45 mm beam spot; 25 ns timing; trigger pT(QQ̄) &gt; 200 GeV; the paper's plane-finding algorithm and signal region.",
          "<b>Our reading (not stated):</b> SCT smearing along the beam of 1.16 mm (2 × the 0.58 mm in [27]); the 45 mm beam spot as one common shift per event, with the fit measured from the true vertex.",
          "<b>Also shown:</b> 0.58 mm (the value in [27], not doubled) and no smearing along the beam (no source).",
          "Two independent samples per benchmark (1000 and 2000 generated events), never combined. No tuning to the paper."]), Spacer(1, 6),
      P("Definitions", "h2"),
      E("ε<sub>trig</sub> = N(pT of the quirk pair &gt; 200 GeV) / N(matched events)"),
      E("ε<sub>fid</sub> = N(triggered, every quirk crosses all 8 layers inside |η| &lt; 1.8, within 25 ns) / N(triggered)"),
      E("ε<sub>reco</sub> = N(fiducial and plane found, 2 hits in 7 layers + ≥ 1 in the 8th, Δw &lt; 1 cm, Δs &lt; 0.01 cm) / N(fiducial)"),
      E("ε = ε<sub>trig</sub> × ε<sub>fid</sub> × ε<sub>reco</sub>   (paper Eq. 12)"), Spacer(1, 2),
      P("Colored only: both R-hadrons must be charged; this cut is applied to the triggered events before ε<sub>fid</sub> (27 of 101 and 68 of 207 events). "
        "The paper does not say which factor contains it.", "m"), Spacer(1, 4),
      E("Standard error: SE = √( ε (1 − ε) / n )"),
      E("Wilson 95% interval: [ ε + z²/2n ± z √( ε(1−ε)/n + z²/4n² ) ] / (1 + z²/n),  z = 1.96"),
      E("Upper limit (UL): when 0 of n events pass, the largest true rate that still gives 0 events in at least 5% of experiments: UL = 1 − 0.05<super>1/n</super> ≈ 3/n"),
      E("p-value (exact two-sided binomial test): if the paper's value were exactly right, the probability of getting a count as unlikely as ours or more (the paper gives no counts or errors, so its own uncertainty is ignored)"),
      Spacer(1, 4),
      table(["p-value", "Verdict"], [["p &lt; 0.01", ("Strongly inconsistent", "bad")], ["0.01 ≤ p &lt; 0.05", ("Statistically inconsistent", "bad")],
                                      ["0.05 ≤ p &lt; 0.10", ("Borderline / mild tension", "warn")], ["p ≥ 0.10", (OK_LABEL, "ok")]], [40, 75])]

# 1 pile-up
def pur(stg): return PU[PU.stage == stg].iloc[0]
prow = []
for nm, stg in [("Plane, hits in ≥ 4 of 8 layers", "plane with >=1 hit in >=4 of 8 layers"), ("Plane, hits in all 8 layers", "plane with >=1 hit in all 8 layers"),
               ("Any reconstructed plane", "Sec. III C plane"), ("Hit multiplicity", "hit multiplicity 7x2+1"), ("Signal region", "ds < 0.01 cm = signal region")]:
    r = pur(stg); k, n = int(r.k), int(r.n)
    rate = f"{sci(k/n)} ± {sci(np.sqrt(k/n*(1-k/n)/n))}" if k else "0"
    rng = f"[{sci(r.wilson95_lo)}, {sci(r.wilson95_hi)}]" if k else ulf(k, n)
    pap = {"plane with >=1 hit in >=4 of 8 layers": "≈ 1×10⁻³", "plane with >=1 hit in all 8 layers": "≈ 6×10⁻⁵"}.get(stg, "—")
    cmp_ = r.comparison if isinstance(r.comparison, str) else ("no event passes" if k == 0 else "—")
    prow.append([nm, f"{k}/{n}", rate, rng, pap, cmp_[0].upper() + cmp_[1:]])
S += [PageBreak(), KeepTogether([P("1. Pile-up background (⟨μ⟩ = 50, 5000 events)", "h2"),
      table(["Quantity", "k/n", "Rate ± SE", "Wilson 95% / UL", "Paper", "Comparison"], prow, [42, 18, 34, 34, 18, 28])]),
      P("The paper gives approximate rates without counts or errors, so no formal test is made.", "m"), Spacer(1, 4),
      img(fig("F13v3_pileup"), 150, "Pile-up rates with Wilson 95% intervals; ◁ = 95% upper limit when no event passes; diamonds = paper."), Spacer(1, 4),
      box("Reading", [
          "The 4-of-8 rate is about 12× the paper's. Possible reasons, <b>not tested here</b>: our pile-up tracks are ideal helices with no energy loss, bremsstrahlung or endcaps; our pool has 20 000 minimum-bias events (paper 125 000); the paper does not define “a plane” for this number.",
          "“Compatible” for the all-8-layer rate and the signal region only means our 5000 events are not sensitive enough: the 95% upper limit (6×10⁻⁴) is 10× above the paper's 6×10⁻⁵."])]

# conversion: paper Fig. 5 population (conversion + pile-up after plane + multiplicity), fb normalisation
import glob as _glob
def _ovpm(d_):
    o = pd.concat(pd.read_csv(f) for f in _glob.glob(f"{L}/logs/{d_}/chunk_*.csv")); o = o[o.config == "LITERAL"]; assert o.event.nunique() == 9139
    _T = lambda x: x.astype(str) == "True"; return o[_T(o.plane) & _T(o.mult)].ds
_f5c = __import__("json").load(open(f"{L}/../PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/tables/paper_fig5_extracted.json"))["delta_s_cm"]["histograms"]["Converted gamma"]
_ptot = sum(t["height"] for t in _f5c); _pin = sum(t["height"] for t in _f5c if t["hi"] <= 0.0100001)
_c5 = np.cumsum([t["height"] for t in _f5c]) / _ptot; _i5 = int(np.searchsorted(_c5, 0.5)); _pmd = np.sqrt(_f5c[_i5]["lo"] * _f5c[_i5]["hi"])
MAT = pd.read_csv(f"{T}/conversion_material_summary.csv").set_index("config")
poprows = [["Paper Fig. 5 (conversion + pile-up)", f"{_ptot:.3f} fb = {100*_ptot/10:.2f}% of 10 fb", f"≈ {_pmd*1e4:.0f} µm", f"{100*_pin/_ptot:.1f}%"]]
for d_, lab_ in [("P10_chunks_ETA", "+ pile-up, SCT z 1.16 mm"), ("P10_chunks_ETA_Z0", "+ pile-up, no SCT z smearing")]:
    v = _ovpm(d_); k = int((v < 0.01).sum()); n = len(v)
    poprows.append([lab_, f"{n}/9139 = {100*n/9139:.2f}%", f"{v.median()*1e4:.0f} µm", f"{k}/{n} = {100*k/max(n,1):.1f}%"])
for c_, lab_ in [("Z0_t0_none", "conversion only, no SCT z smearing"), ("Z0_t0.03_brem+ms", "conversion only, no SCT z, brem + scattering (3% X₀)"), ("Z0_t0.05_brem+ms", "conversion only, no SCT z, brem + scattering (5% X₀)")]:
    r_ = MAT.loc[c_]; poprows.append([lab_, f"{int(r_.mult_pass)}/9139 = {100*r_.mult_frac:.2f}%", f"{r_.ds_median_mult_um:.0f} µm" if r_.mult_pass else "—", f"{100*r_.frac_mult_below_cut:.0f}%" if r_.mult_pass else "—"])

# 2 conversions
SIG_OUR, SIG_PAP = 0.2310512 * 9139 / 10000 * 1e3, 1000.0   # fb
crow = []
for setup in ["conversion only, SCT z 1.16 mm", "conversion only, SCT z 0.58 mm", "conversion only, no SCT z smearing", "conversion + pile-up (mu=50), SCT z 1.16 mm"]:
    g = CV3[CV3.setup == setup].set_index("stage"); pl, mu_, sr = g.loc["plane"], g.loc["hit multiplicity"], g.loc["signal region"]
    k, n = int(sr.k), int(sr.n); f = k / n if k else ul(k, n)
    nev = lambda sig: sig * 0.01 * f * 300
    crow.append([setup.replace("mu=50", "μ = 50").replace("conversion only, ", "conversion only<br/>").replace("conversion + pile-up (μ = 50), ", "conversion + pile-up (μ = 50)<br/>"),
                 f"{int(pl.k)}/{n}", f"{int(mu_.k)}/{n}", f"{k}/{n}", (w95(k, n) if k else ulf(k, n)),
                 (f"{nev(SIG_OUR):.1f} / {nev(SIG_PAP):.1f}" if k else f"&lt; {nev(SIG_OUR):.2f} / &lt; {nev(SIG_PAP):.2f}")])
import glob as _g2
_oz = pd.concat(pd.read_csv(f) for f in _g2.glob(f"{L}/logs/P10_chunks_ETA_Z0/chunk_*.csv")); _oz = _oz[_oz.config == "LITERAL"]; assert _oz.event.nunique() == 9139
_TZ = lambda x: x.astype(str) == "True"; _zpl = int(_TZ(_oz.plane).sum()); _zmu = int((_TZ(_oz.plane) & _TZ(_oz.mult)).sum()); _zsr = int((_TZ(_oz.plane) & _TZ(_oz.mult) & _TZ(_oz.final)).sum())
_f = _zsr / 9139
crow.append(["conversion + pile-up (μ = 50)<br/>no SCT z smearing", f"{_zpl}/9139", f"{_zmu}/9139", f"{_zsr}/9139", w95(_zsr, 9139), f"{SIG_OUR*0.01*_f*300:.0f} / {SIG_PAP*0.01*_f*300:.0f}"])
ovc = CV3[(CV3.setup.str.startswith("conversion + pile-up")) & (CV3.stage == "hit multiplicity")].iloc[0]
S += [Spacer(1, 10), KeepTogether([P("2. Converted-photon background (9139 Z(νν)γ+jet photons, |η| &lt; 1.8, fit from the vertex)", "h2"),
      table(["Setup", "Plane", "Hit mult.", "Signal region", "Wilson 95% / UL", "Events at 300 fb⁻¹ (our σ / paper σ)"], crow, [44, 20, 20, 22, 30, 38])]),
      P("Events at 300 fb⁻¹ = σ × 1% conversion probability × fraction × 300 fb⁻¹, with σ = 0.21 pb (our MadGraph) or ≈ 1 pb (paper). With 0 events the 95% upper limit is used.", "m"), Spacer(1, 4),
      img(fig("F14v3_conversion"), 140, "Fraction of photons passing each cut; open triangles = 95% upper limit when no event passes."), Spacer(1, 4),
      KeepTogether([P("<b>Comparison with the paper's Fig. 5.</b> Its y-axis is dσ/d log Δs in fb per bin, and conversions there are overlaid with pile-up, so the matching population is "
                      "conversion + pile-up after plane and hit multiplicity (the events that meet the Δs cut).", "b"), Spacer(1, 2),
                    table(["Population", "Events reaching the Δs cut", "Δs median", "Δs below 0.01 cm"], poprows, [70, 44, 26, 34])]), Spacer(1, 4),
      box("Reading", [
          "With SCT smearing along the beam (1.16 or 0.58 mm), no conversion reaches the signal region, with or without pile-up. The paper does not claim none passes: its Fig. 5 “suggests a few background events after the final selection cut” (3.6% of its conversion histogram, ≈ 0.002 fb).",
          "With 1.16 mm + pile-up our population has the paper's width (median ≈ 210 vs ≈ 280 µm) but is 3× larger, and none of its 193 events falls below the cut.",
          f"Pile-up hits can fill the gaps of an e⁺e⁻ pair ({int(ovc.k)}/9139 pass the hit count), but none of them is thin enough to pass Δs.",
          f"Without SCT smearing along the beam and with pile-up, {_zsr}/9139 = {100*_zsr/9139:.1f}% of conversions reach the signal region (≈ {SIG_PAP*0.01*_f*300:.0f} events at 300 fb⁻¹ with the paper's σ). The paper's Fig. 5 has ≈ 0.002 fb there, so this reading does not match the paper's background.",
          "Without SCT smearing, conversion-only planes are thin (median ≈ 50 µm). Adding bremsstrahlung and multiple scattering (1–5% X₀ per layer; the simulation the paper cites includes bremsstrahlung but not scattering) "
          "only raises this to 53–67 µm, still ≈ 100% below the cut. Material effects therefore do not explain the paper's conversion width.",
          "Our cross-section is 4.3× below the paper's ≈ 1 pb (generator settings not given). The 1% conversion probability is taken from the paper's own “≈ 1 pb → ≈ 10 fb”."])]

# trigger combinations table
CB = pd.read_csv(f"{T}/trigger_combinations.csv")
CDESC = {"C1": "C1: xqcut 60 + cteq6l1 + scale ×2", "C2": "C2: C1 + production scales off", "C3": "C3: C1 + showerKt", "C4": "C4: C1 + showerKt + production scales off",
         "C5": "C5: 0 jets, no matching + cteq6l1 + scale ×2 (contradicts paper)", "C6": "C6: C5 + production scales off (contradicts paper)"}
combrows = []
for cfg, g in CB.groupby("config"):
    e_, c_ = g[g.bench == "EW"].iloc[0], g[g.bench == "COL"].iloc[0]
    combrows.append([CDESC[cfg], f"{int(e_.N_trigger)}/{int(e_.N_matched)} = {e_.eps_trig:.3f} [{e_.w95_lo:.3f}, {e_.w95_hi:.3f}]", f"{int(c_.N_trigger)}/{int(c_.N_matched)} = {c_.eps_trig:.3f} [{c_.w95_lo:.3f}, {c_.w95_hi:.3f}]",
                     f"{e_.eps_trig / c_.eps_trig:.2f}", ("yes", "ok") if bool(e_.joint_pass) else ("no", "bad")])

# 3 & 4 signal
def sigtab(samples):
    rows = []
    for q, qn in [("trigger", "ε<sub>trig</sub>"), ("fiducial", "ε<sub>fid</sub>")]:
        for s in samples:
            k, n, p0, p = vrow(s, q); rows.append([qn, s, f"{k}/{n}", epm(k, n), w95(k, n), f"{p0:.2f}", fp(p), cls(p)])
    for key in ("z1160", "z580", "z0"):
        for s in samples:
            k, n, p0, p = vrow(s, "reconstruction", TRT[key]); rows.append([f"ε<sub>reco</sub>, SCT z {TL[key]}", s, f"{k}/{n}", epm(k, n), w95(k, n), f"{p0:.2f}", fp(p), cls(p)])
    return table(["Efficiency", "Sample", "k/n", "ε ± SE", "Wilson 95%", "Paper", "p", "Verdict"], rows, [32, 16, 17, 23, 25, 12, 18, 31])
S += [Spacer(1, 10), KeepTogether([P("3. Colored quirks (m<sub>Q</sub> = 1800 GeV, Λ = 2 keV)", "h2"), sigtab(["COL1000", "COL2000"])]), Spacer(1, 10),
      KeepTogether([P("4. Electroweak quirks (m<sub>Q</sub> = 800 GeV, Λ = 4 keV)", "h2"), sigtab(["EW1000", "EW2000"])]), Spacer(1, 6),
      box("Reading", [
          "<b>Colored:</b> trigger and fiducial agree with the paper. Reconstruction agrees for 0.58 mm and for no smearing; at 1.16 mm the larger sample is low (3/25).",
          "<b>EW trigger:</b> 17–18% against 10%. The lowest EW value we reach, in any single setting or combination, is 0.126 [0.110, 0.145] (C4); it does not reach 0.10, whatever happens to colored, so this holds even if the paper used different settings per sample.",
          "Secondary: every setting that lowers EW also lowers colored, so the EW/colored ratio stays at 0.60–0.85 (paper 0.42). This argument assumes common settings for both samples, which the paper does not state.",
          "Not testable with generator settings, so left open: a misprint, a different denominator, or an unstated EW-specific cut. These need the authors; we stop the trigger search here.",
          "<b>EW fiducial:</b> 45–51% against 28%. Using the detector lengths of [27] instead of |η| &lt; 1.8 gives 33–37%, close to 28% (section 6), but the paper does not say it used them.",
          "<b>EW reconstruction:</b> 15–31% with SCT smearing along the beam; 81–85% only without it."]), Spacer(1, 4),
      KeepTogether([P("<b>Trigger: pre-registered combinations</b> (written down and hashed before running; 2000 generated events per benchmark; pass = paper inside Wilson 95% for both; the PDF was checked in the compiled MadGraph code, cteq6l1 for both benchmarks)", "b"), Spacer(1, 2),
      table(["Combination", "EW: k/n, ε [Wilson 95%]", "Colored: k/n, ε [Wilson 95%]", "EW/col.", "Both pass?"], combrows, [58, 40, 40, 14, 22])]), Spacer(1, 4),
      img(fig("F09v3_trigger_variations"), 172, "(a) EW vs colored ε_trig for every configuration run on both benchmarks, labelled (blue = one-at-a-time, green = combinations, grey = settings that contradict the paper's 'up to 1 jet, matched', orange = baseline, star = paper). (b) EW/colored ratio per configuration. (c) All EW values incl. the generator-version pilot (pink); open markers = 500 or 1000 events.")]

# evidence table (computed from per-event files)
import json as _json
_f5 = _json.load(open(f"{L}/../PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/tables/paper_fig5_extracted.json"))["delta_s_cm"]["histograms"]
def _pb(h): tot = sum(t["height"] for t in h); return sum(t["height"] for t in h if t["hi"] <= 0.0100001) / tot
def _pmed(h):
    c = np.cumsum([t["height"] for t in h]); c = c / c[-1]; i = int(np.searchsorted(c, 0.5)); return np.sqrt(h[i]["lo"] * h[i]["hi"])
_pe = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); _cv = pd.read_csv(f"{T}/conversion_acceptance_A_per_event.csv"); _TR = lambda x: x.astype(str) == "True"
def _sig(z): return _pe[(_pe["sample"] == "EW2000") & (_pe.geom == "A") & (_pe.sct == z) & (_pe.bs == "CV") & _TR(_pe.fid) & _TR(_pe.plane) & _TR(_pe.mult)].ds
def _con(z): return _cv[(_cv.config == f"A_{z}_PV") & _TR(_cv.plane)].ds
Z3 = ["Z1160", "Z580", "Z0"]
def _reco(s, key): k, n, p0, p = vrow(s, "reconstruction", TRT[key]); return f"{k/n:.2f}"
evrows = [["EW reconstruction (EW2000)", "0.72"] + [_reco("EW2000", k) for k in ("z1160", "z580", "z0")],
          ["Colored reconstruction (COL2000)", "0.35"] + [_reco("COL2000", k) for k in ("z1160", "z580", "z0")],
          ["EW signal Δs below the cut", f"{100*_pb(_f5['EW Quirk']):.0f}%"] + [f"{100*(_sig(z) < 0.01).mean():.0f}%" for z in Z3],
          ["EW signal Δs median", f"≈ {_pmed(_f5['EW Quirk'])*1e4:.0f} µm"] + [f"{_sig(z).median()*1e4:.0f} µm" for z in Z3],
          ["Conversion + pile-up reaching the Δs cut", f"{100*sum(t['height'] for t in _f5['Converted gamma'])/10:.2f}%"] + [f"{100*len(_ovpm('P10_chunks_ETA'))/9139:.2f}%", "not run", f"{100*len(_ovpm('P10_chunks_ETA_Z0'))/9139:.2f}%"],
          ["Conversion + pile-up Δs median", f"≈ {_pmed(_f5['Converted gamma'])*1e4:.0f} µm"] + [f"{_ovpm('P10_chunks_ETA').median()*1e4:.0f} µm", "not run", f"{_ovpm('P10_chunks_ETA_Z0').median()*1e4:.0f} µm"],
          ["Conversion + pile-up below the cut", f"{100*_pb(_f5['Converted gamma']):.1f}%"] + [f"{100*(_ovpm('P10_chunks_ETA') < 0.01).mean():.1f}%", "not run", f"{100*(_ovpm('P10_chunks_ETA_Z0') < 0.01).mean():.1f}%"]]

# 5 reconstruction
bsrows = []
for bs, lab_ in [("CV", "One common shift per event, fit from the true vertex (used)"), ("CO", "One common shift per event, fit from the origin"), ("PH", "Separate 45 mm shift of every hit")]:
    c2 = MX[(MX["sample"] == "COL2000") & (MX.acceptance == "A") & (MX.beamspot == bs)].set_index("sct_z"); e2 = MX[(MX["sample"] == "EW2000") & (MX.acceptance == "A") & (MX.beamspot == bs)].set_index("sct_z")
    f = lambda m: f"{int(m.loc['Z1160'].final)} · {int(m.loc['Z580'].final)} · {int(m.loc['Z0'].final)}  of {int(m.loc['Z1160'].fiducial)}"
    bsrows.append([lab_, f(c2), f(e2)])
S += [PageBreak(), P("5. What decides reconstruction", "h2"),
      img(fig("F08v3_reco_vs_sct_z"), 100, "Reconstruction efficiency of the same events for each SCT smearing along the beam. Bars = Wilson 95%; lines = paper."), Spacer(1, 3),
      img(fig("F16v2_ds_signal_vs_conversion"), 150, "Δs against the paper's Fig. 5. Left: EW signal (unit area). Right: conversion + pile-up after plane and hit multiplicity, in fb per bin like the paper. Solid = 1.16 mm SCT smearing along the beam, dashed = none, dotted = paper."), Spacer(1, 4),
      KeepTogether([P("<b>Can the paper's own figures pick the SCT setting?</b>", "b"), Spacer(1, 2),
      table(["Paper observable", "Paper", "SCT z 1.16 mm", "0.58 mm", "none"], evrows, [62, 24, 30, 28, 30])]), Spacer(1, 4),
      box("Reading", [
          "[27] gives the SCT accuracy as 17 µm across and 0.58 mm along the beam. The paper doubles “the intrinsic accuracy” without naming the direction, so 1.16 mm is our reading of the text.",
          "The signal rows favour no smearing along the beam: the signal planes get thin enough and the efficiencies come close to Table I.",
          "The conversion rows favour 1.16 mm: with pile-up, 1.16 mm gives the paper's width (median ≈ 210 vs ≈ 280 µm), while no smearing gives 9× too many conversions reaching the cut, a median of ≈ 80 µm and 67% below the cut (paper 3.6%).",
          "Electron material effects do not remove this tension: bremsstrahlung plus multiple scattering (1–5% X₀ per layer) thicken conversion planes only to ≈ 50–70 µm.",
          "So no single SCT setting reproduces both the signal and the conversion panels of the paper's Fig. 5 in our simulation. The figures cannot decide the setting; we keep all three treatments and report the conversion background for each."]), Spacer(1, 5)]

# 6 Table I
rows = []
for bench, samples, label in [("COL", ["COL1000", "COL2000"], "Colored"), ("EW", ["EW1000", "EW2000"], "EW")]:
    for q, qn, t in [("trigger", "ε<sub>trig</sub>", "—"), ("fiducial", "ε<sub>fid</sub>", "—"), ("reconstruction", "ε<sub>reco</sub>, z 1.16 mm", TRT["z1160"]),
                     ("reconstruction", "ε<sub>reco</sub>, z 0.58 mm", TRT["z580"]), ("reconstruction", "ε<sub>reco</sub>, no z smear", TRT["z0"])]:
        cells = []
        for s in samples:
            k, n, p0, p = vrow(s, q, t); cells.append(f"{k}/{n} = {epm(k, n)}<br/>{w95(k, n)}, p = {fp(p)}")
        k, n, p0, p = vrow(samples[1], q, t)
        rows.append([f"<b>{label}</b>" if q == "trigger" else "", qn, f"{p0:.2f}", cells[0], cells[1], cls(p)])
sens = []
for s in ["COL1000", "COL2000", "EW1000", "EW2000"]:
    f_ = SB[(SB["sample"] == s) & (SB.quantity == "fiducial")].iloc[0]; k, n = int(f_.k), int(f_.n)
    fin = [int(SB[(SB["sample"] == s) & (SB.treatment == TRT[k_])].iloc[0].k) for k_ in ("z1160", "z580", "z0")]
    sens.append([s, f"{k}/{n} = {epm(k, n)}", w95(k, n), fp(f_.p_exact_vs_paper), " · ".join(map(str, fin)) + f"  of {k}"])
S += [PageBreak(), KeepTogether([P("6. Table I: paper vs this work", "h2"),
      table(["", "Quantity", "Paper", "1000-event sample: ε ± SE, Wilson 95%, p", "2000-event sample: ε ± SE, Wilson 95%, p", "Verdict (2000)"], rows, [17, 27, 12, 42, 42, 34])]), Spacer(1, 4),
      box("Bottom line", [
          "<b>Agrees with the paper:</b> colored trigger and fiducial efficiency; colored reconstruction for 0.58 mm or no SCT smearing along the beam.",
          "<b>Does not agree:</b> EW trigger (0.18 vs 0.10, also with combined generator settings), EW fiducial (0.51 vs 0.28), and EW reconstruction with SCT smearing along the beam (0.22–0.31 vs 0.72).",
          "<b>Backgrounds:</b> pile-up only and conversion only give no signal-region event, and so does the conversion + pile-up overlay with this setup. "
          f"Without SCT smearing along the beam, {100*_zsr/9139:.1f}% of conversions (with pile-up) would pass, far more than the paper's Fig. 5 shows.",
          "<b>Why a full reproduction is not possible:</b> the paper does not fix the SCT smearing along the beam, the beam-spot treatment, the exact acceptance or the generator settings; its own Fig. 5 is not consistent with any single SCT setting in our simulation; and it gives no event counts or errors."]), Spacer(1, 4),
      KeepTogether([P("<b>Sensitivity check: detector lengths from [27]</b> (pixel |z| &lt; 40.05 cm, SCT |z| &lt; 74.9 cm) instead of |η| &lt; 1.8", "b"), Spacer(1, 2),
      table(["Sample", "ε_fid = k/n ± SE", "Wilson 95%", "p vs 0.28", "Signal region (z 1.16 · 0.58 mm · none)"], sens, [22, 40, 30, 22, 60])])]

# Appendix A
ss = pd.read_csv(f"{T}/v2_source_status.csv")
from xml.sax.saxutils import escape as X
def stc(s): return (s, "ok") if s.startswith(("PAPER", "REFERENCE")) else (s, "warn") if s.startswith("INFERRED") else (s, "bad") if s.startswith("UNDOC") else (s, None)
keep = ss[~ss.implementation_choice.str.startswith("Converted photon")].copy()
keep.loc[keep.implementation_choice.str.startswith("Generator settings"), "resulting_counts"] = "EW trigger 0.13-0.19 over 36 single variations; 0.126-0.141 over 6 combinations (colored then 0.16-0.19)"
srows = [[X(r.implementation_choice.replace(" (PRIMARY)", "").replace(" (PRIMARY reading)", "")), X(r.exact_source.replace(". Original project choice", "")), stc(r.status.replace("PAPER-STATED (paper-internal inconsistency)", "PAPER-STATED")), X(r.resulting_counts)] for r in keep.itertuples()]
pm = PU[PU.stage == "ds < 0.01 cm = signal region"].iloc[0]; ovr = CV3[(CV3.setup.str.startswith("conversion + pile-up")) & (CV3.stage == "signal region")].iloc[0]
srows += [[X("Pile-up: mu = 50, 45 mm per vertex, ATLAS tracking-efficiency removal, pixel merging"), X("Paper Sec. III D; ATL-PHYS-PUB-2015-051; pool 20 000 events (paper: 125 000)"), ("PAPER-STATED (pool size differs)", "ok"), f"signal region {int(pm.k)}/{int(pm.n)}"],
          [X("Converted photon: conversion in the beam pipe, equal energy sharing, 1% probability; overlay with pile-up"), X("Paper Sec. III D (1% derived from '~1 pb -> ~10 fb')"), ("PAPER-STATED", "ok"),
           f"signal region 0/9139 (z 1.16), 0/9139 (0.58), 30/9139 (none); with pile-up {int(ovr.k)}/{int(ovr.n)}"]]
S += [PageBreak(), P("Appendix A. Where every setting comes from", "h2"),
      P("Green = stated in the paper or [27]; amber = our reading; red = no source. Counts are listed in the order COL1000, COL2000, EW1000, EW2000.", "m"), Spacer(1, 3),
      table(["Setting", "Source", "Status", "Resulting counts"], srows, [38, 60, 36, 40]), Spacer(1, 6),
KeepTogether([P("<b>45 mm beam spot.</b> The paper smears “the z-coordinates of all the hits” and assumes the vertex “is identified correctly, and is located at the origin”. "
                      "Events passing the signal region for SCT z 1.16 · 0.58 mm · none:", "b"), Spacer(1, 3),
                    table(["Reading of the beam-spot sentence", "Colored 2000", "EW 2000"], bsrows, [96, 38, 38])])]
S += [PageBreak(), P("Appendix B. Paper-figure reproductions", "h2"),
      Table([[img(fig("F02_angular_momentum_and_separation"), 84, "Fig. 2 style: angular momentum L and quirk separation d for one colored event (COL2000 event 107). L peaks near 9×10¹¹ ħ, the paper's ≈ 10¹² ħ scale.", cell=True),
              img(fig("F03_plane_rotation"), 84, "Fig. 3 style: the quirk plane rotates by less than 10⁻⁴ rad, so the hits stay on one plane.", cell=True)]],
            colWidths=[88 * mm, 88 * mm], style=[("VALIGN", (0, 0), (-1, -1), "TOP")]),
      Spacer(1, 4), img(fig("F04_signal_event_displays"), 90, "Fig. 4 style: hits of one colored (COL2000 event 201) and one EW (EW2000 event 23) event in the plane's own coordinates, SCT z 1.16 mm. Both pass the signal region (Δs = 52 and 96 µm). Band = ±Δw.")]

def deco(c, d):
    c.saveState(); c.setFont("DV", 7.5); c.setFillColor(MUTED)
    c.drawString(18 * mm, 10 * mm, "Quirk Table I reproduction · arXiv:1708.02243 · paper-stated acceptance, inferred longitudinal model")
    c.drawRightString(192 * mm, 10 * mm, f"{d.page}"); c.restoreState()
doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=15 * mm, bottomMargin=16 * mm,
                      title="Quirk Table I Reproduction", author="", subject="Literal reproduction of arXiv:1708.02243 Table I")
doc.addPageTemplates([PageTemplate("p", [Frame(18 * mm, 16 * mm, 174 * mm, 266 * mm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=deco)])
doc.build(S)
print("wrote", OUT)
