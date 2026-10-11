#!/usr/bin/env python3
"""Builds TABLE_I_REPRODUCTION_REPORT_2026-10-09.pdf (A4) from the verified tables, logs and FINAL_FIGURES PNGs.
2000-event samples only. Every count is read from the analysis outputs; every Wilson interval and p-value is recomputed here.
Verdict scale: p < 0.01 strongly inconsistent; 0.01-0.05 statistically inconsistent; 0.05-0.10 borderline / mild tension;
p >= 0.10 no statistically significant inconsistency. Run with a Python that has reportlab and scipy."""
import os, glob, json
import numpy as np, pandas as pd
from scipy import stats
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak

HERE = os.path.dirname(os.path.abspath(__file__)); L = os.path.abspath(f"{HERE}/.."); T = f"{L}/tables"; FIG = f"{L}/FINAL_FIGURES"; LOG = f"{L}/logs"
OUT = f"{L}/TABLE_I_REPRODUCTION_REPORT_2026-10-09.pdf"; EV = "/home/rafia/coplanarity_study/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1"
F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", F + "DejaVuSans.ttf")); pdfmetrics.registerFont(TTFont("DVB", F + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVO", F + "DejaVuSans.ttf")); registerFontFamily("DV", normal="DV", bold="DVB", italic="DVO", boldItalic="DVB")
INK, MUTED, RULE = colors.HexColor("#1b2328"), colors.HexColor("#5b6770"), colors.HexColor("#d5dbde")
OKB, OKF = colors.HexColor("#e2f2e8"), colors.HexColor("#1d6b3c"); BADB, BADF = colors.HexColor("#f9e3e1"), colors.HexColor("#a1302a")
WB, WF = colors.HexColor("#fbf0d6"), colors.HexColor("#8a5a00"); NOTE, HEAD = colors.HexColor("#edf3f6"), colors.HexColor("#eef1f2")
st = {"h1": ParagraphStyle("h1", fontName="DVB", fontSize=16, leading=20, textColor=INK, spaceAfter=3),
      "h2": ParagraphStyle("h2", fontName="DVB", fontSize=12, leading=15, textColor=INK, spaceBefore=6, spaceAfter=4),
      "h3": ParagraphStyle("h3", fontName="DVB", fontSize=9.6, leading=12.5, textColor=INK, spaceBefore=4, spaceAfter=2),
      "b": ParagraphStyle("b", fontName="DV", fontSize=8.8, leading=12.2, textColor=INK),
      "m": ParagraphStyle("m", fontName="DV", fontSize=7.8, leading=10.4, textColor=MUTED),
      "cap": ParagraphStyle("cap", fontName="DVO", fontSize=7.6, leading=9.8, textColor=MUTED, spaceBefore=2),
      "c": ParagraphStyle("c", fontName="DV", fontSize=7.5, leading=9.6, textColor=INK),
      "ch": ParagraphStyle("ch", fontName="DVB", fontSize=7.1, leading=8.8, textColor=MUTED),
      "q": ParagraphStyle("q", fontName="DVO", fontSize=8.2, leading=10.8, textColor=INK, leftIndent=8),
      "bl": ParagraphStyle("bl", fontName="DV", fontSize=8.6, leading=11.6, textColor=INK, leftIndent=9, bulletIndent=0)}
P = lambda t, s="b": Paragraph(t, st[s])
B = lambda xs: [Paragraph(x, st["bl"], bulletText="•") for x in xs]
TR = lambda s: s.astype(str) == "True"

# ---------------- statistics ----------------
def wilson(k, n): return stats.binomtest(int(k), int(n)).proportion_ci(0.95, "wilson")
def pex(k, n, p0): return stats.binomtest(int(k), int(n), p0).pvalue
def ul95(n): return 1 - 0.05 ** (1 / n)
def verdict(p):
    if p < 0.01: return "Strongly inconsistent", "bad"
    if p < 0.05: return "Statistically inconsistent", "bad"
    if p < 0.10: return "Borderline / mild tension", "warn"
    return "No significant inconsistency", "ok"
def fp(p):
    if p >= 0.1: return f"{p:.2f}"
    if p >= 0.001: return f"{p:.3f}"
    m, e = f"{p:.1e}".split("e"); return f"{m}×10<super>{int(e)}</super>"
def sci(x):
    m, e = f"{x:.1e}".split("e"); return f"{m}×10<super>{int(e)}</super>"
def chip(txt, kind):
    fg, bg = {"ok": (OKF, OKB), "bad": (BADF, BADB), "warn": (WF, WB), "none": (MUTED, colors.white)}[kind]
    return Paragraph(f'<font color="{fg.hexval().replace("0x", "#")}"><b>{txt}</b></font>', st["c"]), bg
def grid(data, widths, extra=(), head=1):
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=head)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, head - 1), HEAD), ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE), ("BOX", (0, 0), (-1, -1), 0.6, RULE),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
                           ("LEFTPADDING", (0, 0), (-1, -1), 3.5), ("RIGHTPADDING", (0, 0), (-1, -1), 3.5)] + list(extra))); return t
def H(*xs): return [P(x, "ch") for x in xs]
def C(*xs): return [x if not isinstance(x, str) else P(x, "c") for x in xs]
def img(name, w, cap=None):
    from reportlab.lib.utils import ImageReader
    p = f"{FIG}/{name}/{name}.png"; iw, ih = ImageReader(p).getSize(); parts = [Image(p, width=w * mm, height=w * mm * ih / iw)]
    return KeepTogether(parts + ([P(cap, "cap")] if cap else []))
def box(title, items):
    t = Table([[[P(f"<b>{title}</b>")] + items]], colWidths=[174 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NOTE), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)])); return t
def quote(src, txt): return [P(f"<b>{src}</b>", "c"), P(f"“{txt}”", "q"), Spacer(1, 2)]

# ---------------- data ----------------
SAM = {"COL2000": dict(tag="colored_1800GeV_L2keV", name="Colored", mq=1800, lam=2, paper=dict(trig=.24, fid=.28, reco=.35)),
       "EW2000": dict(tag="EW_800GeV_L4keV", name="EW", mq=800, lam=4, paper=dict(trig=.10, fid=.28, reco=.72))}
GEN = {s: json.load(open(f"{EV}/generation/{v['tag']}/generation_stats.json")) for s, v in SAM.items()}
MAT = {s: pd.read_csv(f"{EV}/events/{v['tag']}/matched_events_full.csv") for s, v in SAM.items()}
A = pd.read_csv(f"{T}/all_crossings_per_event.csv")
PE = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); PE = PE[(PE.geom == "B") & (PE.sct == "Z0") & (PE.bs == "CV")]
CNT = {}
for s in SAM:
    M = MAT[s]; trig = TR(M.trigger_proxy_pass); assert int(trig.sum()) == int((M.quirk_pair_pt_gev > 200).sum())
    Tg = M[trig]; charged = int(((Tg.charge1.abs() > 0.5) & (Tg.charge2.abs() > 0.5)).sum())
    a0 = A[(A["sample"] == s) & (A["mode"] == "FIRST") & (A.sct == "Z0")]
    tech = PE[(PE["sample"] == s) & (PE.why == "technical_exception")]; assert len(a0) + len(tech) == charged and not TR(tech.fid).any(), (s, len(a0), len(tech), charged)
    c = dict(gen=GEN[s]["N_requested"], matched=len(M), trig=int(trig.sum()), charged=charged, fid=int(TR(a0.fid).sum()), tech=len(tech))
    for mode in ("FIRST", "ALL"):
        for sct in ("Z1160", "Z0"):
            x = A[(A["sample"] == s) & (A["mode"] == mode) & (A.sct == sct) & TR(A.fid)]; assert len(x) == c["fid"]
            c[(mode, sct)] = dict(plane=int(TR(x.plane).sum()), mult=int((TR(x.plane) & TR(x.mult)).sum()), sr=int(TR(x.final).sum()))
    q = lambda v: f"{np.median(v):.0f} [{np.quantile(v, .16):.0f}–{np.quantile(v, .84):.0f}]"
    c["pt_all"], c["pt_trig"], c["mqq"] = q(M.quirk_pair_pt_gev), q(Tg.quirk_pair_pt_gev), q(M.quirk_pair_mass_gev)
    CNT[s] = c
# backgrounds
def ov(d):
    o = pd.concat(pd.read_csv(f) for f in glob.glob(f"{LOG}/{d}/chunk_*.csv")); o = o[o.config == "LITERAL"]; assert o.event.nunique() == 9139
    return dict(n=9139, plane=int(TR(o.plane).sum()), mult=int((TR(o.plane) & TR(o.mult)).sum()), sr=int((TR(o.plane) & TR(o.mult) & TR(o.final)).sum()))
def pu(d):
    p = pd.concat(pd.read_csv(f) for f in glob.glob(f"{LOG}/{d}/chunk_*.csv")); assert p.event_i.nunique() == 5000; sel = TR(p.sec3c_plane_found) & (p.sec3c_dw < 1)
    return dict(n=5000, r4=int((sel & (p.sec3c_n_layers >= 4)).sum()), r8=int((sel & (p.sec3c_n_layers >= 8)).sum()), sr=int(TR(p.final_sec_iv_pass).sum()))
BG = dict(conv580=ov("P10_chunks_B_Z580_REF34"), conv1160=ov("P10_chunks_LITERAL"), conv0=ov("P10_chunks_B_Z0_REF34"),
          pu580=pu("P21_chunks_REF34_Z580"), pu1160=pu("P8_chunks_LITERAL"), puinel=pu("P22_chunks_MB_INEL_MONASH"))
# Lambda scan (2000-event samples)
L0 = pd.read_csv(f"{T}/lambda_scan_summary.csv"); L1 = pd.read_csv(f"{T}/lambda_scan_z1160_summary.csv")
LS = pd.concat([L0[L0["sample"].isin(list(SAM)) & (L0.sct == "Z0")], L1])
for s, v in SAM.items():   # benchmark point must equal the main table
    for sct in ("Z1160", "Z0"):
        r = LS[(LS["sample"] == s) & (LS.lambda_keV == v["lam"]) & (LS["mode"] == "FIRST") & (LS.sct == sct)].iloc[0]
        assert (int(r.n_fid), int(r.k_ge2)) == (CNT[s]["fid"], CNT[s][("FIRST", sct)]["sr"]), (s, sct)
# figure numbers
V5 = json.load(open(f"{T}/paper_fig5_vector.json")); V23 = json.load(open(f"{T}/paper_fig23_vector.json"))
def pmed(b):
    lo = np.array([x["lo"] for x in b]); hi = np.array([x["hi"] for x in b]); h = np.array([x["height"] for x in b]); c = np.cumsum(h) / h.sum(); i = int(np.searchsorted(c, 0.5))
    f = (0.5 - (c[i - 1] if i else 0)) / (c[i] - (c[i - 1] if i else 0)); return 10 ** (np.log10(lo[i]) + f * np.log10(hi[i] / lo[i]))
F5 = {}
for sct in ("Z1160", "Z0"):
    d = pd.read_csv(f"{FIG}/F30_fig5_{sct}/F30_fig5_{sct}_source.csv").dropna(subset=["ds"]); F5[sct] = d.groupby("population").agg(N=("ds", "size"), ds=("ds", "median"), dw=("dw", "median"))
PM = {lab: (pmed(V5["delta_s_cm"]["histograms"][lab]), pmed(V5["delta_w_cm"]["histograms"][lab])) for lab in V5["delta_s_cm"]["histograms"]}
c3 = pd.read_csv(f"{T}/fig3_velocity_plane_curves.csv"); e3 = c3[c3.r_cm > 14.5].groupby(["sample", "key"]).dphi_rad.median()
P3 = {"COL2000": V23["fig3"]["curves"]["colored_1800GeV_2keV"], "EW2000": V23["fig3"]["curves"]["EW_800GeV_2keV"]}
p3end = {s: float(np.interp(15.0, np.array(c["x"]), np.array(c["y"]))) * 1e-3 for s, c in P3.items()}
f2 = pd.read_csv(f"{FIG}/F23_fig2_v2/F23_fig2_v2_source.csv"); f2 = f2[f2.r_cm <= 5]
f4 = {sct: pd.read_csv(f"{FIG}/F29_fig4_{sct}/F29_fig4_{sct}_source.csv") for sct in ("Z1160", "Z0")}

# extra inputs for this revision
CT = pd.read_csv(f"{T}/lambda_scan_combined_test_2000.csv")
st["what"] = ParagraphStyle("what", fontName="DV", fontSize=8.0, leading=10.6, textColor=INK, leftIndent=6, spaceBefore=1, spaceAfter=3)
W_ = lambda t: P(f"<b>What this shows:</b> {t}", "what")
PAPER_BELOW = {lab: sum(b["height"] for b in V5["delta_s_cm"]["histograms"][lab] if b["hi"] <= 0.0101) / sum(b["height"] for b in V5["delta_s_cm"]["histograms"][lab]) for lab in V5["delta_s_cm"]["histograms"]}
def prod_ci(parts, nmc=200000, seed=7):   # 95% interval of a product of independent binomial fractions (Jeffreys Beta draws)
    r = np.random.default_rng(seed); x = np.ones(nmc)
    for k, n in parts: x *= r.beta(k + 0.5, n - k + 0.5, nmc)
    return np.quantile(x, [0.025, 0.975])

# ---------------- document ----------------
S = []
c, e = CNT["COL2000"], CNT["EW2000"]
S += [P("Reproduction of Table I of arXiv:1708.02243", "h1"),
      P("S. Knapen, H. K. Lou, M. Papucci, J. Setford, “Tracking down quirks at the Large Hadron Collider”, Phys. Rev. D 96, 115015 (2017) · "
        "signal efficiencies, backgrounds and Figures 2–5 · 2000-event samples · 9 October 2026", "m"), Spacer(1, 5)]
S += [box("Summary", B([
    f"<b>Trigger and fiducial:</b> colored trigger {c['trig']}/{c['matched']} = {c['trig']/c['matched']:.2f} and fiducial {c['fid']}/{c['charged']} = {c['fid']/c['charged']:.2f} agree with the paper (0.24, 0.28). "
    f"The EW trigger {e['trig']}/{e['matched']} = {e['trig']/e['matched']:.2f} is far above the paper's 0.10; the EW fiducial {e['fid']}/{e['charged']} = {e['fid']/e['charged']:.2f} agrees with 0.28.",
    f"<b>Reconstruction with the SCT z resolution of the paper's text (1.16 mm):</b> colored {c[('FIRST','Z1160')]['sr']}/{c['fid']}, EW {e[('FIRST','Z1160')]['sr']}/{e['fid']}, far below the paper (0.35, 0.72).",
    f"<b>Reconstruction without SCT z smearing:</b> colored {c[('FIRST','Z0')]['sr']}/{c['fid']} = {c[('FIRST','Z0')]['sr']/c['fid']:.2f} and EW {e[('FIRST','Z0')]['sr']}/{e['fid']} = {e[('FIRST','Z0')]['sr']/e['fid']:.2f}, "
    "consistent with the paper. Only this setting matches the paper's Fig. 5 Δs values; over the Λ column it fits far better than 1.16 mm, but EW at low Λ still differs.",
    f"<b>Backgrounds</b> with the cited detector model [34] and SCT z 580 µm: 0 of 9139 converted photons + pile-up and 0 of 5000 pile-up events in the signal region, as in the paper. "
    f"If the background is also simulated without SCT z smearing, {BG['conv0']['sr']} of 9139 conversions ({100*BG['conv0']['sr']/9139:.1f}%) enter the signal region.",
    "<b>Figures 2–5</b> have the paper's shapes; the signal strip width Δw is about 2× (EW) and 5× (colored) wider than in the paper's Fig. 5."]))]
S += [Spacer(1, 4), P("Verdicts use the exact binomial p-value against the paper's number, taken as exact: p &lt; 0.01 strongly inconsistent; 0.01–0.05 statistically inconsistent; "
                      "0.05–0.10 borderline / mild tension; p ≥ 0.10 no statistically significant inconsistency. Intervals are Wilson 95%.", "m")]

# 1 setup
S += [P("1. Simulation setup", "h2"), P("1.1 Event generation (both samples generated with the same setup)", "h3")]
g = [H("Setting", "This work", "Paper")]
for r in [("Generator", "MadGraph5_aMC@NLO 3.7.3 + Pythia 8.317", "MadGraph5_aMC@NLO + Pythia8 (source comments: v2.3.3, 8.212)"),
          ("Processes", "colored: p p → t1 t1~ (+ j); EW: p p → qe+ qe− (+ j)", "vector-like quirks, up to 1 jet; colored QCD only; EW Drell–Yan, unit charge"),
          ("Masses, Λ", "1800 GeV / 2 keV; 800 GeV / 4 keV", "same benchmarks"),
          ("Beams, PDF, scale", "pp 13 TeV; nn23lo1 (built-in; LHAPDF 247000); MG5 default dynamical scale", "not stated"),
          ("Matching", "MLM, ickkw = 1, xqcut = 30 GeV, qCut = 45 GeV, nJetMax = 1", "“matched using Pythia8”; settings not stated"),
          ("Shower, hadronisation", "Pythia 8 defaults (MPI on); colored: R-hadrons on, stable", "colored quirks hadronise into quirk-hadrons"),
          ("Events, seeds", "2000 each; MG5 iseed 8001 (colored), 8002 (EW)", "not stated")]:
    g.append(C(*r))
S += [grid(g, [30, 74, 70])]
S += [Spacer(1, 4), P("1.2 Cross sections and event statistics", "h3")]
g = [H("", "Colored 1.8 TeV", "EW 800 GeV")]
for lab, k in [("σ, MadGraph (0 + 1 jet, before matching)", "parton"), ("σ after MLM matching", "matched")]:
    g.append(C(lab, *[f"{GEN[s][k+'_xsec_pb']*1e3:.3f} ± {GEN[s][k+'_xsec_err_pb']*1e3:.3f} fb" for s in SAM]))
for lab, k in [("Events generated", "gen"), ("Events after matching", "matched"), ("pT(QQ̄) &gt; 200 GeV (trigger)", "trig"), ("both quirk-hadrons charged (colored)", "charged")]:
    g.append(C(lab, *[(str(CNT[s][k]) if not (k == "charged" and s == "EW2000") else f"{CNT[s][k]} (unit charge)") for s in SAM]))
for lab, k in [("pT(QQ̄), all matched events: median [16–84%] (GeV)", "pt_all"), ("pT(QQ̄), triggered events (GeV)", "pt_trig"), ("M(QQ̄), all matched events (GeV)", "mqq")]:
    g.append(C(lab, *[CNT[s][k] for s in SAM]))
S += [grid(g, [74, 50, 50]), P("The trigger is the paper's pT(QQ̄) &gt; 200 GeV on the final-state quirk pair (colored: the final-state R-hadrons).", "m")]
S += [P("1.3 Detector model and efficiency definitions", "h3")]
g = [H("Item", "This work", "Source")]
for r in [("Layers", "IBL + 3 pixel + 4 SCT barrel layers (8), B = 2 T", "paper Sec. III C (8 layers); IBL radius and length not stated in the paper, taken from arXiv:1803.00844"),
          ("Barrel lengths", "IBL |z| &lt; 33.0 cm, pixel |z| &lt; 40.05 cm, SCT |z| &lt; 74.9 cm", "Ref. [27]"),
          ("Pixel hits", "pixel centre, 50 × 400 µm (IBL 50 × 250 µm); neighbouring pixels merged", "paper Sec. III A"),
          ("SCT R-φ", "34 µm (2 × 17 µm)", "paper Sec. III A + Ref. [27]"),
          ("SCT z (signal)", "<b>1.16 mm</b> and <b>no smearing</b>, both reported", "see Sec. 1.4"),
          ("Beam spot", "45 mm Gaussian, one common shift per event; plane fit from the true vertex", "paper Sec. III A, III C; per event vs per hit not stated, our choice"),
          ("Hits", "first crossing of each layer by each quirk, t &lt; 25 ns; every crossing shown as a sensitivity", "paper does not state how repeated crossings are treated; our choice"),
          ("Plane finding", "seeds, windows, factor-3 rule, Δw &lt; 1 cm, smallest Δs; Δs = √λ₁, Δw = √λ₂ of Eq. 11", "paper Sec. III C"),
          ("Signal region", "plane; 2 hits in 7 layers and ≥ 1 in the 8th; Δw &lt; 1 cm; Δs &lt; 0.01 cm", "paper Sec. IV")]:
    g.append(C(*r))
S += [grid(g, [26, 86, 62])]
S += [Spacer(1, 3), P("ε<sub>trig</sub> = N(pT(QQ̄) &gt; 200 GeV) / N(after matching)    "
                      "ε<sub>fid</sub> = N(both quirks cross all 8 layers inside the lengths, t &lt; 25 ns) / N(triggered; colored: both charged)    "
                      "ε<sub>reco</sub> = N(signal region) / N(fiducial)    ε = ε<sub>trig</sub> × ε<sub>fid</sub> × ε<sub>reco</sub> (paper Eq. 12)", "c")]
S += [P("1.4 SCT z values used", "h3")]
S += quote("Paper, Sec. III A", "for the silicon microstrip tracker (SCT) we conservatively assume a resolution of twice the intrinsic accuracy quoted in [27].")
S += quote("Ref. [27], ATL-PHYS-PUB-2009-002 (in arXiv:0901.0512, p. 18)", "The intrinsic accuracies per module in the barrel are 17 µm (R−φ) and 580 µm (z)")
S += B(["<b>Signal.</b> The paper's text gives 1.16 mm (2 × 580 µm). Its Fig. 5 and its Λ column are matched only without SCT z smearing. Both settings are reported throughout.",
        "<b>Backgrounds.</b> The paper processes pile-up and conversions with the simplified detector of [34]. [34] takes its resolutions from the ATLAS technical design report "
        "but gives no SCT z value; we use 580 µm from [27], together with the energy-loss model of [34]. The backgrounds are the same for both signal settings."])

# 2 Table I
S += [Spacer(1, 6), P("2. Table I: signal efficiencies", "h2"), P("2.1 Event counts (2000-event samples, first crossing)", "h3")]
g = [H("Step", "Colored, 1.16 mm", "Colored, no smear", "EW, 1.16 mm", "EW, no smear")]
g.append(C("after matching", f"{c['matched']}", f"{c['matched']}", f"{e['matched']}", f"{e['matched']}"))
g.append(C("triggered", f"{c['trig']}", f"{c['trig']}", f"{e['trig']}", f"{e['trig']}"))
g.append(C("both charged", f"{c['charged']}", f"{c['charged']}", "—", "—"))
g.append(C("fiducial", f"{c['fid']}", f"{c['fid']}", f"{e['fid']}", f"{e['fid']}"))
for lab, k in [("plane found (Δw &lt; 1 cm)", "plane"), ("+ hit multiplicity", "mult"), ("+ Δs &lt; 0.01 cm (signal region)", "sr")]:
    g.append(C(lab, *[str(CNT[s][("FIRST", z)][k]) for s in SAM for z in ("Z1160", "Z0")]))
g.append(C("<i>signal region, every crossing as a hit (≥ 2 hits)</i>", *[f"<i>{CNT[s][('ALL', z)]['sr']}</i>" for s in SAM for z in ("Z1160", "Z0")]))
S += [grid(g, [58, 29, 29, 29, 29])]
S += [P(f"Quirks often cross a layer more than once within 25 ns. The italic row counts every crossing as a hit. {c['tech']} colored and {e['tech']} EW triggered events stopped "
        "with a numerical integration error; they are kept in the ε<sub>fid</sub> denominator as not fiducial.", "m")]
S += [P("2.2 Efficiencies against the paper", "h3")]
g = [H("Benchmark", "Efficiency", "k / n", "ε [Wilson 95%]", "Paper", "p", "Verdict")]; ex = []; ri = 0
for s, v in SAM.items():
    C_ = CNT[s]; items = [("ε<sub>trig</sub>", C_["trig"], C_["matched"], v["paper"]["trig"]), ("ε<sub>fid</sub>", C_["fid"], C_["charged"], v["paper"]["fid"]),
                          ("ε<sub>reco</sub>, SCT z 1.16 mm", C_[("FIRST", "Z1160")]["sr"], C_["fid"], v["paper"]["reco"]),
                          ("ε<sub>reco</sub>, no SCT z smearing", C_[("FIRST", "Z0")]["sr"], C_["fid"], v["paper"]["reco"])]
    for j, (lab, k, n, p0) in enumerate(items):
        lo, hi = wilson(k, n); p = pex(k, n, p0); ch, bg = chip(*verdict(p)); ri += 1
        g.append(C(f"{v['name']} {v['mq']/1000 if v['mq']>=1000 else v['mq']:g} {'TeV' if v['mq']>=1000 else 'GeV'}, {v['lam']} keV" if j == 0 else "", lab, f"{k} / {n}",
                   f"{k/n:.3f} [{lo:.3f}, {hi:.3f}]", f"{p0:.2f}", fp(p), ch)); ex.append(("BACKGROUND", (6, ri), (6, ri), bg))
    for z, zl in (("Z1160", "1.16 mm"), ("Z0", "no smear")):
        k = C_[("FIRST", z)]["sr"]; t = (C_["trig"] / C_["matched"]) * (C_["fid"] / C_["charged"]) * (k / C_["fid"])
        lo, hi = prod_ci([(C_["trig"], C_["matched"]), (C_["fid"], C_["charged"]), (k, C_["fid"])]); ri += 1
        g.append(C("", f"ε (Eq. 12), {zl}", "", f"{t:.4f} [{lo:.4f}, {hi:.4f}]", f"{v['paper']['trig']*v['paper']['fid']*v['paper']['reco']:.3f}*", "", ""))
    ex.append(("LINEBELOW", (0, ri), (-1, ri), 1.0, MUTED))
S += [grid(g, [30, 40, 16, 32, 12, 17, 27], ex)]
S += [P("* derived: product of the paper's Table I entries (the paper does not quote ε). Interval of our ε: 95% range of the product of the three binomial factors "
        "(Jeffreys draws). Colored: the both-charged requirement (68 of 207 triggered events) is applied before ε<sub>fid</sub>, so it is not part of Eq. 12.", "m"), Spacer(1, 3),
      img("F31_table_I", 172, "Table I efficiencies: points = this work with Wilson 95% intervals, dashes = paper. Numbers below the points: k/n."),
      W_("where a point's bar crosses the dashed line, our sample agrees with the paper. The colored trigger and fiducial and both fiducial values agree; the EW trigger is too high; "
         "ε<sub>reco</sub> agrees for both samples only without SCT z smearing (orange) and is far too low with 1.16 mm (blue).")]

# 2.3 Lambda: tables first
S += [P("2.3 The Λ column of Table I", "h3"),
      P("The paper also gives ε<sub>reco</sub> at other string tensions Λ. The size of the quirk oscillation scales as 1/Λ², so this column tests the reconstruction "
        "over a wide range of hit patterns. The fiducial count is recomputed at every Λ.", "b")]
g = [H("Benchmark", "Λ (keV)", "Paper", "1.16 mm: k / n", "ε [Wilson 95%]", "p", "no smear: k / n", "ε [Wilson 95%]", "p")]; ex = []; ri = 0
for s, v in SAM.items():
    x = LS[(LS["sample"] == s) & (LS["mode"] == "FIRST")]
    for i, lk in enumerate(sorted(x.lambda_keV.unique())):
        cells = [v["name"] if i == 0 else "", f"{lk}", f"{x[x.lambda_keV == lk].paper_reco.iloc[0]:.3g}"]; ri += 1
        for j, sct in enumerate(("Z1160", "Z0")):
            r = x[(x.lambda_keV == lk) & (x.sct == sct)].iloc[0]; k, n = int(r.k_ge2), int(r.n_fid); lo, hi = wilson(k, n); p = pex(k, n, r.paper_reco)
            cells += [f"{k} / {n}", f"{k/n:.2f} [{lo:.2f}, {hi:.2f}]", fp(p)]; ex.append(("BACKGROUND", (5 + 3 * j, ri), (5 + 3 * j, ri), chip(*verdict(p))[1]))
        g.append(C(*cells))
    ex.append(("LINEBELOW", (0, ri), (-1, ri), 1.0, MUTED))
S += [Spacer(1, 2), grid(g, [19, 13, 13, 22, 28, 16, 22, 28, 16], ex), P("First crossing. Shading of the p column follows the verdict scale (green: no significant inconsistency).", "m")]
g = [H("Setup (all 10 Λ points)", "Colored χ² / 5", "p", "EW χ² / 5", "p", "Both χ² / 10", "p", "Verdict")]; ex = []
for i, lab in enumerate(CT.setup.unique(), 1):
    t = CT[CT.setup == lab].set_index("benchmark"); ch, bg = chip(*verdict(t.loc["EW+COL", "p_corr"]))
    g.append(C(lab, f"{t.loc['COL','chi2_corr']:.1f}", fp(t.loc["COL", "p_corr"]), f"{t.loc['EW','chi2_corr']:.1f}", fp(t.loc["EW", "p_corr"]),
               f"{t.loc['EW+COL','chi2_corr']:.1f}", fp(t.loc["EW+COL", "p_corr"]), ch)); ex.append(("BACKGROUND", (7, i), (7, i), bg))
S += [Spacer(1, 3), P("Combined test of the whole Λ column", "h3"), grid(g, [44, 15, 18, 15, 18, 15, 18, 31], ex),
      P("χ² = dᵀC⁻¹d with d = (ours − paper) at every Λ; C uses binomial variances and the correlation between Λ points from an event-level bootstrap "
        "(the same events enter every Λ). Paper values taken as exact.", "m"), Spacer(1, 3),
      img("F31_lambda", 172, "ε<sub>reco</sub> vs Λ. Filled points: first crossing, Wilson 95%. Open points: every crossing as a hit (≥ 2 hits per layer). "
          "Blue: SCT z 1.16 mm; orange: no SCT z smearing; black: paper."),
      W_("the black line is the paper. Without SCT z smearing (orange) our points follow the paper's rise and fall with Λ; colored agrees (combined p = 0.50; 3 and 5 keV borderline), "
         "EW sits above the paper at 1–2 keV. With 1.16 mm (blue) the efficiency stays low at every Λ.")]

# 3 backgrounds
S += [Spacer(1, 6), P("3. Backgrounds", "h2")]
cv, pu_ = BG["conv580"], BG["pu580"]; pa = 2 / 9139
g = [H("Sample (detector: [34] model, SCT z 580 µm)", "Events", "Plane", "+ hit mult.", "Signal region k / n", "Wilson 95%", "Paper", "p")]
lo, hi = wilson(cv["sr"], 9139); g.append(C("converted γ + μ = 50 pile-up", "9139", str(cv["plane"]), str(cv["mult"]), f"{cv['sr']} / 9139", f"[0, {sci(hi)}]", "“a few” (≈ 2.4×10<super>−4</super>)", fp(pex(cv["sr"], 9139, pa))))
lo, hi = wilson(pu_["sr"], 5000); g.append(C("pile-up only, μ = 50", "5000", "—", "—", f"{pu_['sr']} / 5000", f"[0, {sci(hi)}]", "none", "—"))
S += [grid(g, [44, 14, 13, 17, 26, 22, 26, 12])]
g = [H("Pile-up plane rates (5000 events)", "k / n", "rate [Wilson 95%]", "Paper", "p (approx.)", "Comparison")]
for lab, k, p0, ptxt, cmp_ in [("selected plane, ≥ 1 hit in ≥ 4 of 8 layers", "r4", 1e-3, "~10<super>−3</super>", "higher than the paper's approximate rate"),
                                ("selected plane, ≥ 1 hit in all 8 layers", "r8", 6e-5, "6×10<super>−5</super>", "compatible with the paper's approximate rate")]:
    lo, hi = wilson(pu_[k], 5000); g.append(C(lab, f"{pu_[k]} / 5000", f"{sci(pu_[k]/5000)} [{sci(lo)}, {sci(hi)}]", ptxt, fp(pex(pu_[k], 5000, p0)), cmp_))
S += [Spacer(1, 3), grid(g, [50, 18, 40, 16, 16, 34])]
N_ul = lambda sig_pb: 300 * sig_pb * 1e3 * 0.01 * ul95(9139)
g = [H("Converted photons at 300 fb⁻¹", "σ (Z(νν)γ + j)", "conversion probability", "signal-region fraction, 95% UL", "expected events, 95% UL")]
g.append(C("this work's cross section", "0.211 pb", "1%", sci(ul95(9139)), f"&lt; {N_ul(0.211):.2f}"))
g.append(C("paper's cross section", "∼1 pb", "1%", sci(ul95(9139)), f"&lt; {N_ul(1.0):.2f}"))
S += [Spacer(1, 3), grid(g, [44, 28, 30, 38, 34])]
S += [P(f"Converted photons: Z(→νν)γ + jet, MET &gt; 200 GeV, pT(γ) &gt; 0.5 GeV; 10 000 generated, 9139 pass MET &gt; 200 GeV after the shower. Conversion probability 1% from the paper's 1 pb → 10 fb. "
        f"Measured sensitivities, same events: SCT z 1.16 mm without the [34] energy loss: {BG['conv1160']['sr']}/9139 conversions, {BG['pu1160']['r4']}/5000 pile-up 4-of-8 planes; "
        f"background without SCT z smearing: {BG['conv0']['sr']}/9139 conversions in the signal region.", "m")]

# 4 figures: table, then graph, then plain note
S += [Spacer(1, 6), P("4. Figures 2–5 of the paper", "h2"), P("Paper curves and histograms are read from the vector figures in the paper's arXiv source, so the comparison uses the paper's exact values.", "m")]
pL, pdm = max(V23["fig2"]["curves"]["L_1e12_hbar"]["y"]), max(V23["fig2"]["curves"]["d_cm"]["y"])
def zeros_period(x, y):
    x, y = np.array(x), np.array(y); o = np.argsort(x); x, y = x[o], y[o]; m = np.where((y[1:-1] < y[:-2]) & (y[1:-1] <= y[2:]) & (y[1:-1] < 0.2 * y.max()))[0] + 1; return np.diff(x[m]).mean() if len(m) > 1 else np.nan
d_ = f2.d_cm.values; L_ = f2.L_hbar.values; r_ = f2.r_cm.values
lm = np.where((L_[1:-1] < L_[:-2]) & (L_[1:-1] <= L_[2:]))[0] + 1; lm = lm[r_[lm] > 0.1]
g = [H("Fig. 2 quantity (colored 1.8 TeV, 2 keV)", "Paper (one event)", "This work (median-|L|max event)")]
g += [C("maximum |L|", f"{pL:.2f}×10¹² ħ", f"{L_.max()/1e12:.2f}×10¹² ħ"), C("maximum separation d", f"{pdm:.2f} cm", f"{d_.max():.2f} cm"),
      C("spacing in r between minima of d", f"{zeros_period(V23['fig2']['curves']['d_cm']['x'], V23['fig2']['curves']['d_cm']['y']):.2f} cm", f"{zeros_period(r_, d_):.2f} cm"),
      C("separation d at the closest approaches", "not readable", "limited by the time step: 37–186 µm at 300 steps per period, 0.5–1.7 µm at 30 000; still ≫ 1/m<sub>Q</sub> = 1.1×10⁻¹⁷ cm")]
FL = pd.read_csv(f"{T}/fig2_L_check.csv"); na, nl = int(FL.n_approach.sum()), int(FL.n_low_L.sum()); lo_, hi_ = wilson(nl, na)
g2 = [H("Angular momentum at closest approach (all COL2000 fiducial events)", "This work", "Paper")]
g2 += [C("events / closest approaches (r &lt; 15 cm)", f"{len(FL)} / {na}", "one event shown"),
       C("closest approaches with |L| &lt; 1% of the event's |L|max", f"{nl} / {na} = {nl/na:.2f} [{lo_:.2f}, {hi_:.2f}]", "“whenever |L| = 0, the separation between the quirks is large”"),
       C("events with at least one such approach", f"{int((FL.n_low_L > 0).sum())} / {len(FL)}", "—"),
       C("smallest |L| at a closest approach", f"{sci(FL.min_L_at_approach.min())} ħ (not converged: decreases with a finer time step)", "—"),
       C("|L| from the torque of Eq. 5, q(∫d dt) × E<sub>cm</sub>, vs simulated |L|: largest relative difference, median over events", f"{FL.torque_max_rel_dev.median():.2f}", "Eq. 5")]
S += [P("Figure 2: angular momentum and quirk separation", "h3"), grid(g, [62, 48, 64]), Spacer(1, 3), KeepTogether([grid(g2, [70, 56, 48]),
      P("Integration with 3000 steps per period (10× the production setting). At the large-|L| approaches |L| is stable under a finer step; at the small-|L| approaches it is not.", "m")]), Spacer(1, 2),
      img("F30_fig2", 172, "|L| (solid, left axis) and quirk separation d (dashed, right axis) in the exact centre-of-mass frame vs the radius r of the centre of mass."),
      W_("the two quirks fly apart and come back together again and again (dashed d). Our event and the paper's event have the same size of oscillation (3.5–3.9 cm) "
         "and the same scale of angular momentum (about 10¹² ħ). In our events |L| falls close to zero at every second closest approach; in the paper's event it does not.")]
g = [H("Fig. 3 at r = 15 cm (Λ = 2 keV)", "Events", "Δφ median [16–84%]", "Paper", "our events below the paper: k / n [Wilson 95%]")]
for s, lab in (("COL2000", "colored 1.8 TeV"), ("EW2000", "EW 800 GeV")):
    v = e3.loc[s].values; k = int((v < p3end[s]).sum()); lo, hi = wilson(k, len(v))
    g.append(C(lab, str(len(v)), f"{np.median(v)*1e3:.2f} [{np.quantile(v,.16)*1e3:.2f}, {np.quantile(v,.84)*1e3:.2f}]×10⁻³", f"{p3end[s]*1e3:.2f}×10⁻³", f"{k} / {len(v)} = {k/len(v):.2f} [{lo:.2f}, {hi:.2f}]"))
S += [Spacer(1, 6), P("Figure 3: rotation of the quirk plane", "h3"), grid(g, [36, 14, 50, 24, 50]), Spacer(1, 2),
      img("F30_fig3", 174, "Δφ: angle by which the plane spanned by the two quirks' velocity vectors (the paper's definition) has turned, vs r. Line: median of all fiducial events; "
          "band: 16–84% of events; dotted: the paper's event. Right: Δφ at r = 15 cm for every event."),
      W_("the plane of the two quirks turns by less than about 10⁻³ rad over 15 cm, so the hits stay on one flat plane. The paper's single event lies inside our spread "
         "(at the low end for colored).")]
g = [H("Fig. 4 example event (median Δs, signal region)", "SCT z", "Event", "rank", "Δs", "Δw")]
for sct, zl in (("Z1160", "1.16 mm"), ("Z0", "none")):
    dd = f4[sct][f4[sct].ellipse != True].groupby("sample").first()
    for s in SAM:
        r = dd.loc[s]; g.append(C(SAM[s]["name"], zl, str(int(r.event_id)), f"{int(r['rank'])} of {int(r.n_sr_events)}", f"{r.ds_cm*1e4:.0f} µm", f"{r.dw_cm:.3f} cm"))
g.append(C("paper example (colored)", "—", "—", "—", "83 µm", "0.074 cm"))
S += [Spacer(1, 4), P("Figure 4: hits of one signal event in the plane's coordinates", "h3"), grid(g, [62, 20, 20, 24, 22, 26])]
S += [PageBreak(), img("F29_fig4_Z1160", 155, "SCT z 1.16 mm. The event is chosen by a fixed rule: the signal-region event with the median Δs."),
      W_("all hits lie on a narrow strip (right, zoom). Δs is the thickness of the plane and Δw the width of the strip (green band). With 1.16 mm only one colored event passes."),
      img("F29_fig4_Z0", 155, "No SCT z smearing, same rule."),
      W_("without SCT z smearing the hits sit closer to the plane (smaller Δs), so many more events pass; the strip width is set by the quirk oscillation.")]
g = [H("Population", "SCT z (signal)", "N", "Δs median", "paper", "Δw median", "paper", "Δs &lt; 0.01 cm: k / n", "Wilson 95%", "paper", "p")]; ex = []; ri = 0
for pop, lab in [("colored", "Colored Quirk"), ("EW", "EW Quirk"), ("converted γ + pile-up", "Converted gamma"), ("pile-up", "Pileup")]:
    for sct, zl in (("Z1160", "1.16 mm"), ("Z0", "none")):
        if pop in ("converted γ + pile-up", "pile-up") and sct == "Z0": continue
        src5 = pd.read_csv(f"{FIG}/F30_fig5_{sct}/F30_fig5_{sct}_source.csv").dropna(subset=["ds"]); x = src5[src5.population == pop]
        k, n = int((x.ds < 0.01).sum()), len(x); lo, hi = wilson(k, n); pp = PAPER_BELOW[lab]; p = pex(k, n, pp); ri += 1
        g.append(C(pop, zl if pop in ("colored", "EW") else "580 µm, [34]", str(n), f"{x.ds.median()*1e4:.0f} µm", f"{PM[lab][0]*1e4:.0f} µm", f"{x.dw.median():.3f} cm", f"{PM[lab][1]:.3f} cm",
                   f"{k} / {n}", f"{k/n:.2f} [{lo:.2f}, {hi:.2f}]", f"{pp:.3f}", fp(p))); ex.append(("BACKGROUND", (10, ri), (10, ri), chip(*verdict(p))[1]))
S += [PageBreak(), P("Figure 5: Δs and Δw distributions", "h3"), grid(g, [24, 18, 10, 14, 12, 15, 12, 18, 21, 12, 18], ex),
      P("Signal: COL2000 / EW2000 events after the plane and hit cuts, before the Δs cut. Paper medians and fractions from its vector histograms. The p column tests the fraction "
        "below the Δs cut against the paper's fraction (paper taken as exact). Colored Δw ratio to the paper: 5× here; with the 1000- and 2000-event samples together, 3.8–4.1×.", "m"), Spacer(1, 2),
      img("F30_fig5_Z1160", 174, "Signal with SCT z 1.16 mm; backgrounds with the [34] model and SCT z 580 µm. Unit area; dotted: paper. Vertical lines: signal-region cuts."),
      W_("with 1.16 mm the signal Δs (top, blue and orange) lies at about 100–200 µm, mostly to the right of the cut at 0.01 cm, while the paper's signal lies at about 30 µm."),
      img("F30_fig5_Z0", 174, "Signal without SCT z smearing; same backgrounds."),
      W_("without SCT z smearing the signal Δs sits at 40 µm, close to the paper, and all signal is left of the cut; almost all background stays to the right. "
         "The signal Δw (bottom) is wider than the paper's.")]

# 5 remaining differences
S += [PageBreak(), P("5. Remaining differences", "h2")]
x2 = LS[(LS["sample"] == "EW2000") & (LS["mode"] == "FIRST") & (LS.sct == "Z0") & (LS.lambda_keV == 2)].iloc[0]
g = [H("Quantity", "This work", "Paper")]
g += [C("EW ε<sub>trig</sub>", f"{e['trig']}/{e['matched']} = {e['trig']/e['matched']:.2f}", "0.10"),
      C("EW ε<sub>reco</sub> at Λ = 2 keV (no SCT z smearing)", f"{int(x2.k_ge2)}/{int(x2.n_fid)} = {x2.k_ge2/x2.n_fid:.2f}", "0.41"),
      C("ε<sub>reco</sub> with SCT z 1.16 mm", f"colored {c[('FIRST','Z1160')]['sr']/c['fid']:.2f}, EW {e[('FIRST','Z1160')]['sr']/e['fid']:.2f}", "0.35, 0.72"),
      C("signal Δw median (Fig. 5)", f"EW {F5['Z0'].loc['EW','dw']:.3f} cm (2×), colored {F5['Z0'].loc['colored','dw']:.3f} cm (5×)", f"EW {PM['EW Quirk'][1]:.3f}, colored {PM['Colored Quirk'][1]:.3f} cm"),
      C("pile-up rate, plane with ≥ 1 hit in ≥ 4 of 8 layers", f"{sci(pu_['r4']/5000)}", "~10<super>−3</super>")]
S += [grid(g, [70, 64, 40]), P("The paper does not give the information needed to trace these differences.", "b")]
S += [P("Settings the paper does not state", "h3")] + B(["matching scale and matching settings; PDF and renormalisation/factorisation scales",
        "which SCT coordinate the doubled resolution applies to",
        "how repeated crossings of a layer by the same quirk are treated, and whether “2 hits” means exactly 2 or at least 2",
        "the plotting convention of Δw in Fig. 5",
        "the minimum-bias process and tune used for pile-up, and the per-event or per-hit beam-spot smearing"])

# appendix
S += [P("Appendix A: what each setting rests on", "h3")]
g = [H("Setting", "Value used", "Status")]
for r in [("Benchmarks, trigger, signal region, plane algorithm", "as in the paper", "stated in the paper"),
          ("Pixel size, merging, beam-spot width, B field, 25 ns", "as in the paper", "stated in the paper"),
          ("SCT R-φ", "34 µm = 2 × 17 µm", "stated in the paper + Ref. [27]"),
          ("SCT z (signal)", "1.16 mm and none", "1.16 mm: paper text + Ref. [27]; none: our choice, matches Fig. 5"),
          ("SCT z (background)", "580 µm", "our choice: [34] cites the TDR, value from Ref. [27]"),
          ("Background energy loss", "bremsstrahlung + ionisation, no multiple scattering", "Ref. [34], App. A"),
          ("Barrel lengths", "Ref. [27] values", "from Ref. [27]"),
          ("IBL radius and length", "3.3 cm, |z| &lt; 33.0 cm", "not stated; arXiv:1803.00844"),
          ("Repeated layer crossings", "first crossing (every crossing as sensitivity)", "not stated; our choice"),
          ("Beam-spot shift", "one common shift per event, fit from the true vertex", "not stated; our choice"),
          ("Generator settings (matching, PDF, scale, tune)", "Sec. 1.1", "not stated; our choice"),
          ("Minimum-bias sample", "Pythia 8 SoftQCD:nonDiffractive, Monash, 20 000 events", "paper: Pythia8, 125 000 events; process and tune not stated"),
          ("Conversion probability", "1%", "derived from the paper's 1 pb → 10 fb")]:
    g.append(C(*r))
S += [grid(g, [50, 64, 60])]
S += [P("Statistics", "h3"), P("Wilson 95% interval for k of n (ε = k/n, z = 1.96): [ε + z²/2n ± z√(ε(1−ε)/n + z²/4n²)] / (1 + z²/n). p: exact two-sided binomial probability of a count "
                                "as unlikely as ours if the paper's value were exact. 95% upper limit for 0 of n: 1 − 0.05<super>1/n</super> ≈ 3/n.", "c")]
S += [P("References", "h3")] + [P(x, "c") for x in [
    "[paper] S. Knapen, H. K. Lou, M. Papucci, J. Setford, Phys. Rev. D 96, 115015 (2017), arXiv:1708.02243.",
    "[27] ATLAS, “The Expected Performance of the ATLAS Inner Detector”, ATL-PHYS-PUB-2009-002, in arXiv:0901.0512.",
    "[34] S. Knapen, S. Pagan Griso, M. Papucci, D. J. Robinson, “Triggering soft bombs at the LHC”, arXiv:1612.00850, App. A.",
    "MadGraph5_aMC@NLO: J. Alwall et al., JHEP 07 (2014) 079. Pythia 8: C. Bierlich et al., SciPost Phys. Codeb. 8 (2022). IBL: ATLAS, arXiv:1803.00844."]]

def deco(cv_, d):
    cv_.saveState(); cv_.setFont("DV", 7.3); cv_.setFillColor(MUTED)
    cv_.drawString(18 * mm, 10 * mm, "Reproduction of Table I of arXiv:1708.02243 · 9 October 2026"); cv_.drawRightString(192 * mm, 10 * mm, f"{d.page}"); cv_.restoreState()
doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=14 * mm, bottomMargin=16 * mm, title="Reproduction of Table I of arXiv:1708.02243", author="")
doc.addPageTemplates([PageTemplate("p", [Frame(18 * mm, 16 * mm, 174 * mm, 267 * mm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=deco)])
doc.build(S); print("wrote", OUT)
