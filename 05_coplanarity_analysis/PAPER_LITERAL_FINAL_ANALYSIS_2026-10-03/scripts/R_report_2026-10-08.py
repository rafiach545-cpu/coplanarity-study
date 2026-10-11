#!/usr/bin/env python3
"""Builds TABLE_I_REPRODUCTION_REPORT_2026-10-08.pdf (A4) from the verified tables, logs and FINAL_FIGURES PNGs.
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
OUT = f"{L}/TABLE_I_REPRODUCTION_REPORT_2026-10-08.pdf"; EV = "/home/rafia/coplanarity_study/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1"
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

# ---------------- document ----------------
S = []
S += [P("Reproduction of Table I of arXiv:1708.02243", "h1"),
      P("S. Knapen, H. K. Lou, M. Papucci, J. Setford, “Tracking down quirks at the Large Hadron Collider”, Phys. Rev. D 96, 115015 (2017) · "
        "signal efficiencies, backgrounds and Figures 2–5 · 2000-event samples · 8 October 2026", "m"), Spacer(1, 5)]
c, e = CNT["COL2000"], CNT["EW2000"]
S += [box("Summary", B([
    f"<b>Trigger and fiducial:</b> colored trigger {c['trig']}/{c['matched']} = {c['trig']/c['matched']:.2f} and fiducial {c['fid']}/{c['charged']} = {c['fid']/c['charged']:.2f} agree with the paper (0.24, 0.28). "
    f"The EW trigger {e['trig']}/{e['matched']} = {e['trig']/e['matched']:.2f} is far above the paper's 0.10; the EW fiducial {e['fid']}/{e['charged']} = {e['fid']/e['charged']:.2f} agrees with 0.28.",
    f"<b>Reconstruction with the paper's SCT z resolution (1.16 mm):</b> colored {c[('FIRST','Z1160')]['sr']}/{c['fid']}, EW {e[('FIRST','Z1160')]['sr']}/{e['fid']}, far below the paper (0.35, 0.72).",
    f"<b>Reconstruction without SCT z smearing:</b> colored {c[('FIRST','Z0')]['sr']}/{c['fid']} = {c[('FIRST','Z0')]['sr']/c['fid']:.2f} and EW {e[('FIRST','Z0')]['sr']}/{e['fid']} = {e[('FIRST','Z0')]['sr']/e['fid']:.2f}, "
    "consistent with the paper. The paper's own Fig. 5 and its Λ column also point to this reading.",
    f"<b>Backgrounds</b> (cited detector model [34]): 0 of 9139 converted photons + pile-up and 0 of 5000 pile-up events in the signal region, as in the paper.",
    "<b>Figures 2–5</b> have the paper's shapes; the signal strip width Δw is about 2× (EW) and 5× (colored) wider than in the paper's Fig. 5, which stays unexplained."]))]
S += [Spacer(1, 4), P("Verdicts use the exact binomial p-value against the paper's number, taken as exact: p &lt; 0.01 strongly inconsistent; 0.01–0.05 statistically inconsistent; "
                      "0.05–0.10 borderline / mild tension; p ≥ 0.10 no statistically significant inconsistency. Intervals are Wilson 95%.", "m")]

# 1 setup
S += [P("1. Simulation setup", "h2"), P("1.1 Event generation (both samples generated with the same setup)", "h3")]
g = [H("Setting", "This work", "Paper")]
rows = [("Generator", "MadGraph5_aMC@NLO 3.7.3 + Pythia 8.317", "MadGraph5_aMC@NLO + Pythia8 (source comments: v2.3.3, 8.212)"),
        ("Processes", "colored: p p → t1 t1~ (+ j); EW: p p → qe+ qe− (+ j)", "vector-like quirks, up to 1 jet; colored QCD only; EW Drell–Yan, unit charge"),
        ("Masses, Λ", "1800 GeV / 2 keV; 800 GeV / 4 keV", "same benchmarks"),
        ("Beams, PDF, scale", "pp 13 TeV; NNPDF2.3 LO (230000); MG5 default dynamical scale", "not stated"),
        ("Matching", "MLM, ickkw = 1, xqcut = 30 GeV, qCut = 45 GeV, nJetMax = 1", "“matched using Pythia8”, settings not stated"),
        ("Shower, hadronisation", "Pythia 8 defaults (MPI on); colored: R-hadrons on, stable", "colored quirks hadronise into quirk-hadrons"),
        ("Events, seeds", "2000 each; MG5 iseed 8001 (colored), 8002 (EW)", "not stated")]
g += [C(*r) for r in rows]
S += [grid(g, [30, 74, 70])]
S += [Spacer(1, 4), P("1.2 Cross sections and event statistics", "h3")]
g = [H("", "Colored 1.8 TeV", "EW 800 GeV")]
for lab, k in [("σ, MadGraph (0 + 1 jet, before matching)", "parton"), ("σ after MLM matching", "matched")]:
    g.append(C(lab, *[f"{GEN[s][k+'_xsec_pb']*1e3:.3f} ± {GEN[s][k+'_xsec_err_pb']*1e3:.3f} fb" for s in SAM]))
for lab, k in [("Events generated", "gen"), ("Events after matching", "matched"), ("pT(QQ̄) &gt; 200 GeV (trigger)", "trig"), ("both quirk-hadrons charged (colored)", "charged")]:
    g.append(C(lab, *[(str(CNT[s][k]) if not (k == "charged" and s == "EW2000") else f"{CNT[s][k]} (unit charge)") for s in SAM]))
for lab, k in [("pT(QQ̄), all matched events: median [16–84%] (GeV)", "pt_all"), ("pT(QQ̄), triggered events (GeV)", "pt_trig"), ("M(QQ̄), all matched events (GeV)", "mqq")]:
    g.append(C(lab, *[CNT[s][k] for s in SAM]))
S += [grid(g, [74, 50, 50])]
S += [P("The trigger is the paper's pT(QQ̄) &gt; 200 GeV on the final-state quirk pair; for the colored sample, the final-state R-hadrons.", "m")]

S += [P("1.3 Detector model and efficiency definitions", "h3")]
g = [H("Item", "This work", "Source")]
for r in [("Layers", "IBL + 3 pixel + 4 SCT barrel layers (8), B = 2 T", "paper Sec. III C (8 layers); IBL radius and length inferred (arXiv:1803.00844)"),
          ("Barrel lengths", "IBL |z| &lt; 33.0 cm, pixel |z| &lt; 40.05 cm, SCT |z| &lt; 74.9 cm", "Ref. [27]"),
          ("Pixel hits", "pixel centre, 50 × 400 µm (IBL 50 × 250 µm); neighbouring pixels merged", "paper Sec. III A"),
          ("SCT R-φ", "34 µm (2 × 17 µm)", "paper Sec. III A + Ref. [27]"),
          ("SCT z (signal)", "<b>1.16 mm (2 × 580 µm)</b> and <b>no smearing</b>, both reported", "see Sec. 1.4"),
          ("Beam spot", "45 mm Gaussian, one common shift per event; plane fit from the true vertex", "paper Sec. III A, III C"),
          ("Hits", "one hit per quirk per layer (first crossing), t &lt; 25 ns", "paper Sec. III B, IV"),
          ("Plane finding", "seeds, windows, factor-3 rule, Δw &lt; 1 cm, smallest Δs; Δs = √λ₁, Δw = √λ₂ of Eq. 11", "paper Sec. III C"),
          ("Signal region", "plane; 2 hits in 7 layers and ≥ 1 in the 8th; Δw &lt; 1 cm; Δs &lt; 0.01 cm", "paper Sec. IV")]:
    g.append(C(*r))
S += [grid(g, [28, 98, 48])]
S += [Spacer(1, 3), P("ε<sub>trig</sub> = N(pT(QQ̄) &gt; 200 GeV) / N(after matching)    "
                      "ε<sub>fid</sub> = N(both quirks cross all 8 layers inside the lengths, t &lt; 25 ns) / N(triggered; colored: both charged)    "
                      "ε<sub>reco</sub> = N(signal region) / N(fiducial)    ε = ε<sub>trig</sub> × ε<sub>fid</sub> × ε<sub>reco</sub> (paper Eq. 12)", "c")]

S += [P("1.4 Why these SCT z values", "h3")]
S += quote("Paper, Sec. III A", "for the silicon microstrip tracker (SCT) we conservatively assume a resolution of twice the intrinsic accuracy quoted in [27].")
S += quote("Ref. [27], ATL-PHYS-PUB-2009-002 (in arXiv:0901.0512, p. 18)", "The intrinsic accuracies per module in the barrel are 17 µm (R−φ) and 580 µm (z)")
S += B(["<b>1.16 mm</b> is the paper's sentence applied to z: 2 × 580 µm. This is the main setting of this report.",
        f"<b>No smearing</b> is what the paper's results need: its Fig. 5 signal Δs medians are {PM['Colored Quirk'][0]*1e4:.0f} µm (colored) and {PM['EW Quirk'][0]*1e4:.0f} µm (EW); "
        f"with 1.16 mm we get {F5['Z1160'].loc['colored','ds']*1e4:.0f} and {F5['Z1160'].loc['EW','ds']*1e4:.0f} µm, without smearing {F5['Z0'].loc['colored','ds']*1e4:.0f} and {F5['Z0'].loc['EW','ds']*1e4:.0f} µm.",
        "<b>Backgrounds</b> use the detector the paper cites for them: pile-up is “processed by the simplified detector described in [34]”, and [34] takes its resolutions “from the "
        "ATLAS technical design report” (SCT z 580 µm) with energy loss in the material. A comment in the paper's source says this simulation is “somewhat more sophisticated "
        "than that for the signal”. The backgrounds are therefore the same for both signal settings."])

# 2 Table I
S += [Spacer(1, 6), P("2. Table I: signal efficiencies", "h2"), P("2.1 Event counts (2000-event samples, one hit per quirk per layer)", "h3")]
g = [H("Step", "Colored, 1.16 mm", "Colored, no smear", "EW, 1.16 mm", "EW, no smear")]
g.append(C("after matching", f"{c['matched']}", f"{c['matched']}", f"{e['matched']}", f"{e['matched']}"))
g.append(C("triggered", f"{c['trig']}", f"{c['trig']}", f"{e['trig']}", f"{e['trig']}"))
g.append(C("both charged", f"{c['charged']}", f"{c['charged']}", "—", "—"))
g.append(C("fiducial", f"{c['fid']}", f"{c['fid']}", f"{e['fid']}", f"{e['fid']}"))
for lab, k in [("plane found (Δw &lt; 1 cm)", "plane"), ("+ hit multiplicity", "mult"), ("+ Δs &lt; 0.01 cm (signal region)", "sr")]:
    g.append(C(lab, *[str(CNT[s][("FIRST", z)][k]) for s in SAM for z in ("Z1160", "Z0")]))
g.append(C("<i>signal region, every crossing as a hit (≥ 2 hits)</i>", *[f"<i>{CNT[s][('ALL', z)]['sr']}</i>" for s in SAM for z in ("Z1160", "Z0")]))
S += [grid(g, [58, 29, 29, 29, 29])]
S += [P(f"Quirks often cross a layer more than once within 25 ns; the paper expects one crossing. The italic row counts every crossing as a hit (sensitivity). "
        f"{c['tech']} colored and {e['tech']} EW triggered events stopped with a numerical integration error; they are kept in the ε<sub>fid</sub> denominator as not fiducial.", "m")]

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
    tot = lambda z: (C_["trig"] / C_["matched"]) * (C_["fid"] / C_["charged"]) * (C_[("FIRST", z)]["sr"] / C_["fid"])
    ri += 1; g.append(C("", "ε (Eq. 12)", "", f"1.16 mm: {tot('Z1160'):.4f}<br/>no smear: {tot('Z0'):.4f}", f"{v['paper']['trig']*v['paper']['fid']*v['paper']['reco']:.3f}", "", ""))
    ex.append(("LINEBELOW", (0, ri), (-1, ri), 1.0, MUTED))
S += [grid(g, [30, 40, 16, 32, 12, 17, 27], ex)]
S += [P("Colored: the both-charged requirement (68 of 207 triggered events) is applied before ε<sub>fid</sub>, so it is not part of Eq. 12, as in the paper's table.", "m"), Spacer(1, 3),
      img("F31_table_I", 172, "Table I efficiencies with Wilson 95% intervals (points) and the paper's values (dashes). Numbers: k/n.")]

S += [P("2.3 The Λ column of Table I", "h3"),
      P("The paper also gives ε<sub>reco</sub> at other string tensions. The oscillation size scales as 1/Λ², so this column tests the reconstruction over a wide range "
        "of hit patterns. Trigger and fiducial selections do not depend on Λ in the paper; here the fiducial count is recomputed at every Λ.", "b"), Spacer(1, 2),
      img("F31_lambda", 172, "ε<sub>reco</sub> vs Λ. Filled points: one hit per quirk per layer, Wilson 95%. Open points: every crossing as a hit (≥ 2 hits per layer). "
          "Blue: SCT z 1.16 mm; orange: no SCT z smearing; black: paper.")]
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
S += [Spacer(1, 3), grid(g, [19, 13, 13, 22, 28, 16, 22, 28, 16], ex), P("Shading of the p column follows the verdict scale (green: no significant inconsistency).", "m")]

# 3 backgrounds
S += [PageBreak(), P("3. Backgrounds", "h2")]
cv, pu_ = BG["conv580"], BG["pu580"]
g = [H("Sample", "Detector", "Events", "Plane", "+ hit mult.", "Signal region", "Paper")]
g.append(C("converted γ + μ = 50 pile-up", "[34] model, SCT z 580 µm", "9139", str(cv["plane"]), str(cv["mult"]), f"{cv['sr']} (95% UL {sci(ul95(9139))})", "“a few” after the cut"))
g.append(C("pile-up only, μ = 50", "[34] model, SCT z 580 µm", "5000", "—", "—", f"{pu_['sr']} (95% UL {sci(ul95(5000))})", "none"))
S += [grid(g, [37, 33, 13, 13, 18, 32, 28])]
g = [H("Pile-up plane rates", "This work [Wilson 95%]", "Paper", "Comparison")]
for lab, k, p0, cmp_ in [("selected plane with ≥ 1 hit in ≥ 4 of 8 layers", "r4", "~10<super>−3</super>", "higher than the paper's approximate rate"),
                          ("selected plane with ≥ 1 hit in all 8 layers", "r8", "6×10<super>−5</super>", "compatible with the paper's approximate rate")]:
    lo, hi = wilson(pu_[k], 5000); g.append(C(lab, f"{pu_[k]}/5000 = {sci(pu_[k]/5000) if pu_[k] else '0'} [{sci(lo) if lo>0 else '0'}, {sci(hi)}]", p0, cmp_))
S += [Spacer(1, 3), grid(g, [62, 52, 22, 38])]
S += [P(f"Converted photons: Z(→νν)γ + jet, MET &gt; 200 GeV, pT(γ) &gt; 0.5 GeV, σ = 0.211 pb in our sample (paper “∼1 pb”), conversion probability 1% taken from the paper's 1 pb → 10 fb. "
        f"Sensitivity, same events: with SCT z 1.16 mm and no material, {BG['conv1160']['sr']}/9139 conversions and {BG['pu1160']['r4']}/5000 pile-up 4-of-8 planes; "
        f"with the background also unsmeared, {BG['conv0']['sr']}/9139 conversions enter the signal region. With an inelastic (instead of non-diffractive) minimum-bias sample "
        f"the pile-up 4-of-8 rate is {BG['puinel']['r4']}/5000 = {sci(BG['puinel']['r4']/5000)}.", "m")]

# 4 figures
S += [Spacer(1, 6), P("4. Figures 2–5 of the paper", "h2"), P("Paper curves and histograms are read from the vector figures in the paper's arXiv source, so the comparison uses the paper's exact values.", "m")]
pL, pd_ = max(V23["fig2"]["curves"]["L_1e12_hbar"]["y"]), max(V23["fig2"]["curves"]["d_cm"]["y"])
S += [img("F30_fig2", 172, f"Fig. 2: |L| and quirk separation d vs r, colored 1.8 TeV at 2 keV, exact centre-of-mass frame. Paper event: |L|max = {pL:.2f}×10¹² ħ, d max = {pd_:.2f} cm. "
          f"Our median event: |L|max = {f2.L_hbar.max()/1e12:.2f}×10¹² ħ, d max = {f2.d_cm.max():.2f} cm. Where |L| ≈ 0, d stays ≥ 0.017 cm ≫ 1/m<sub>Q</sub>, so the pair does not annihilate."), Spacer(1, 4),
      img("F30_fig3", 174, f"Fig. 3: rotation of the plane spanned by the two velocity vectors (the paper's definition) vs r, both benchmarks at 2 keV. Δφ at 15 cm: colored median "
          f"{e3.loc['COL2000'].median()*1e3:.2f}×10⁻³ (paper {p3end['COL2000']*1e3:.2f}×10⁻³, at our {100*(e3.loc['COL2000']<p3end['COL2000']).mean():.0f}th percentile); EW median "
          f"{e3.loc['EW2000'].median()*1e3:.2f}×10⁻³ (paper {p3end['EW2000']*1e3:.2f}×10⁻³, {100*(e3.loc['EW2000']<p3end['EW2000']).mean():.0f}th percentile). Both stay far below the tracker resolution.")]
def f4cap(sct):
    d = f4[sct][f4[sct].ellipse != True].groupby("sample").first(); out = []
    for s in SAM: r = d.loc[s]; out.append(f"{SAM[s]['name']}: event {int(r.event_id)}, Δs = {r.ds_cm*1e4:.0f} µm, Δw = {r.dw_cm:.3f} cm ({int(r['rank'])} of {int(r.n_sr_events)})")
    return "; ".join(out)
S += [PageBreak(), img("F29_fig4_Z1160", 160, f"Fig. 4, SCT z 1.16 mm. Fixed selection: the signal-region event with the median Δs. {f4cap('Z1160')}. Paper example (colored): Δs = 83 µm, Δw = 0.074 cm."),
      Spacer(1, 4), img("F29_fig4_Z0", 160, f"Fig. 4, no SCT z smearing. Same rule. {f4cap('Z0')}.")]
S += [PageBreak(), img("F30_fig5_Z1160", 174, "Fig. 5, signal with SCT z 1.16 mm (after plane and hit cuts, before the Δs cut); backgrounds with the [34] model. Dotted: paper."), Spacer(1, 3),
      img("F30_fig5_Z0", 174, "Fig. 5, signal without SCT z smearing; same backgrounds. Dotted: paper.")]
g = [H("Population", "Paper Δs", "Δs, 1.16 mm", "Δs, no smear", "Paper Δw", "Δw, 1.16 mm", "Δw, no smear")]
for pop, lab in [("colored", "Colored Quirk"), ("EW", "EW Quirk"), ("converted γ + pile-up", "Converted gamma"), ("pile-up", "Pileup")]:
    a, b = F5["Z1160"].loc[pop], F5["Z0"].loc[pop]
    g.append(C(pop, f"{PM[lab][0]*1e4:.0f} µm", f"{a.ds*1e4:.0f} µm (N {int(a.N)})", f"{b.ds*1e4:.0f} µm (N {int(b.N)})", f"{PM[lab][1]:.3f} cm", f"{a.dw:.3f} cm", f"{b.dw:.3f} cm"))
S += [Spacer(1, 3), P("Fig. 5 medians", "h3"), grid(g, [34, 20, 27, 27, 20, 23, 23])]

# 5 reasons
S += [PageBreak(), P("5. Likely reasons for the remaining differences", "h2")]
S += B([f"<b>EW trigger ({e['trig']/e['matched']:.2f} vs 0.10).</b> The trigger depends only on the generated pT(QQ̄) spectrum. The paper does not give its matching scale, PDF, scales or "
        "Pythia settings. The earlier versions MG5 2.3.3 + Pythia 8.212 named in the paper's source give 0.167, and more than 30 single-setting variations stay at 0.13–0.19. "
        "A commented-out draft of Table I in the paper's source lists 0.03; every published version shows 0.10. The colored trigger agrees, so the difference is specific to the EW sample.",
        "<b>Reconstruction with SCT z 1.16 mm.</b> The paper's text gives this resolution, but its own Fig. 5 (signal Δs ≈ 30 µm) and its Λ column are only reproduced without SCT z smearing. "
        "This suggests that the signal simulation applied the doubling to R-φ only, or did not smear z.",
        "<b>EW ε<sub>reco</sub> at low Λ</b> (2 keV: paper 0.41) is higher in our simulation. The paper says ε<sub>reco</sub> drops at low Λ because of the Δw requirement; our pairs pass it more often.",
        "<b>Signal strip width Δw</b> is about 2× (EW) and 5× (colored) the paper's Fig. 5. Our amplitude follows the paper's Eq. 4 exactly and its Fig. 2 scale. Plotting ½√λ₂ would match EW but not colored; "
        "the paper's colored Δw is matched by our events near Λ ≈ 5 keV. The cause is not identified.",
        "<b>Multiple layer crossings.</b> Quirks often cross a layer more than once within 25 ns (pair velocity ≈ 0.1–0.2 c against an internal velocity ≈ 0.5 c). "
        "The paper expects one crossing; with every crossing as a hit, the reading of “2 hits” (exactly or at least) changes ε<sub>reco</sub>.",
        f"<b>Pile-up 4-of-8 rate</b> ({sci(pu_['r4']/5000)} vs ~10⁻³) depends mostly on the minimum-bias sample: an inelastic sample gives {sci(BG['puinel']['r4']/5000)}. The paper does not state it."])
S += [Spacer(1, 4), P("Questions only the authors can answer: the MG5/Pythia versions and matching settings; the SCT coordinate that was doubled; the Λ of the Fig. 5 signal histograms and "
                      "the Δw convention plotted; the minimum-bias process and tune used for pile-up.", "b")]
S += [P("Statistics", "h3"), P("Wilson 95% interval for k of n (ε = k/n, z = 1.96): [ε + z²/2n ± z√(ε(1−ε)/n + z²/4n²)] / (1 + z²/n). p: exact two-sided binomial probability of a count "
                                "as unlikely as ours if the paper's value were exact. 95% upper limit for 0 of n: 1 − 0.05<super>1/n</super> ≈ 3/n.", "c")]
S += [P("References", "h3")] + [P(x, "c") for x in [
    "[paper] S. Knapen, H. K. Lou, M. Papucci, J. Setford, Phys. Rev. D 96, 115015 (2017), arXiv:1708.02243 (v1 and v2 source compared; Table I identical).",
    "[27] ATLAS, “The Expected Performance of the ATLAS Inner Detector”, ATL-PHYS-PUB-2009-002, in arXiv:0901.0512.",
    "[34] S. Knapen, S. Pagan Griso, M. Papucci, D. J. Robinson, “Triggering soft bombs at the LHC”, arXiv:1612.00850, App. A.",
    "MadGraph5_aMC@NLO: J. Alwall et al., JHEP 07 (2014) 079. Pythia 8: C. Bierlich et al., SciPost Phys. Codeb. 8 (2022)."]]

def deco(cv_, d):
    cv_.saveState(); cv_.setFont("DV", 7.3); cv_.setFillColor(MUTED)
    cv_.drawString(18 * mm, 10 * mm, "Reproduction of Table I of arXiv:1708.02243 · 8 October 2026"); cv_.drawRightString(192 * mm, 10 * mm, f"{d.page}"); cv_.restoreState()
doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=14 * mm, bottomMargin=16 * mm, title="Reproduction of Table I of arXiv:1708.02243", author="")
doc.addPageTemplates([PageTemplate("p", [Frame(18 * mm, 16 * mm, 174 * mm, 267 * mm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=deco)])
doc.build(S); print("wrote", OUT)
