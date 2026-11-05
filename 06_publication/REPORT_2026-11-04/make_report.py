#!/usr/bin/env python3
"""Report 2026-11-04: quirk coplanarity search at 13 TeV (Run 2) and 13.6 TeV (Run 3), Knapen geometry, with and without pile-up.
Every number in the tables is read from the stage CSVs (06_publication/S1_*, S2_*) or the plot-ready CSVs of FIGURES_ROOT_2026-11-04/data; figures are the ROOT
figures of FIGURES_ROOT_2026-11-04 (PNG rendered from their PDF). Style as the reproduction reports (reportlab, DejaVu).
Run with /home/rafia/venvs/f6fast/bin/python. Output: QUIRK_13_13p6TeV_REPORT_2026-11-04.pdf (this folder)."""
import os, re, json, numpy as np, pandas as pd
from scipy import stats, optimize
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.utils import ImageReader
HERE = os.path.dirname(os.path.abspath(__file__)); PUB = f"{HERE}/.."; FIG = f"{PUB}/FIGURES_ROOT_2026-11-04"; D = f"{FIG}/data"
S1 = f"{PUB}/S1_13TeV_139fb_knapen_noPU_cop"; S2 = f"{PUB}/S2_13p6TeV_run3_knapen_noPU_cop"; OUT = f"{HERE}/QUIRK_13_13p6TeV_REPORT_2026-11-04.pdf"
F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", F + "DejaVuSans.ttf")); pdfmetrics.registerFont(TTFont("DVB", F + "DejaVuSans-Bold.ttf"))
registerFontFamily("DV", normal="DV", bold="DVB", italic="DV", boldItalic="DVB")
INK, MUTED, RULE, HEAD, NOTE = colors.HexColor("#1b2328"), colors.HexColor("#5b6770"), colors.HexColor("#d5dbde"), colors.HexColor("#dbe7f0"), colors.HexColor("#edf3f6")
ACC, ACCL, KEYB, KEYL = colors.HexColor("#1f5f8b"), colors.HexColor("#e3edf5"), colors.HexColor("#fff4dc"), colors.HexColor("#d8930f")
st = {"h1": ParagraphStyle("h1", fontName="DVB", fontSize=15, leading=19, textColor=ACC, spaceAfter=3),
      "h2": ParagraphStyle("h2", fontName="DVB", fontSize=11.5, leading=14, textColor=ACC, backColor=ACCL, borderPadding=(3, 4, 3, 4), spaceBefore=10, spaceAfter=6),
      "h3": ParagraphStyle("h3", fontName="DVB", fontSize=9.6, leading=12, textColor=ACC, spaceBefore=6, spaceAfter=2),
      "b": ParagraphStyle("b", fontName="DV", fontSize=8.8, leading=12, textColor=INK),
      "m": ParagraphStyle("m", fontName="DV", fontSize=7.6, leading=10, textColor=MUTED),
      "cap": ParagraphStyle("cap", fontName="DV", fontSize=7.8, leading=10.2, textColor=INK, spaceBefore=2, spaceAfter=6),
      "c": ParagraphStyle("c", fontName="DV", fontSize=7.6, leading=9.6, textColor=INK),
      "ch": ParagraphStyle("ch", fontName="DVB", fontSize=7.2, leading=9, textColor=INK),
      "bl": ParagraphStyle("bl", fontName="DV", fontSize=8.6, leading=11.4, textColor=INK, leftIndent=9, bulletIndent=0)}
P = lambda t, s="b": Paragraph(t, st[s]); B = lambda xs: [Paragraph(x, st["bl"], bulletText="•") for x in xs]
H = lambda *xs: [P(x, "ch") for x in xs]; Cc = lambda *xs: [P(str(x), "c") for x in xs]
def grid(data, widths, extra=()):
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HEAD), ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE), ("BOX", (0, 0), (-1, -1), 0.6, RULE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2), ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)] + list(extra)))
    return t
def key(text):
    t = Table([[P(text)]], colWidths=[174 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), KEYB), ("LINEBEFORE", (0, 0), (0, -1), 3, KEYL), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)])); return t
def box(title, items):
    t = Table([[[P(f"<b>{title}</b>")] + items]], colWidths=[174 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NOTE), ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 5)])); return t
NFIG = [0]
def fig(name, w=174, head=None):
    p = f"{FIG}/{name}/{name}.png"; iw, ih = ImageReader(p).getSize(); cap = open(f"{FIG}/{name}/caption.md").read().strip()
    NFIG[0] += 1; cap = re.sub(r"^\*\*Fig\. \d+\.\*\*", f"**Figure {NFIG[0]}.**", cap)                 # numbered in report order; file tag kept
    cap = cap.replace("**", "").replace("σ_z", "σ<sub>z</sub>").replace("ε_trig", "ε<sub>trig</sub>").replace("f_ch", "f<sub>ch</sub>").replace("m_Q", "m<sub>Q</sub>").replace("CL_s", "CL<sub>s</sub>").replace("s_req", "s<sub>req</sub>")
    cap = cap.replace("(3,1)_{2/3}", "(3,1)<sub>2/3</sub>").replace("(1,1)_1", "(1,1)<sub>1</sub>").replace("σ_γ", "σ<sub>γ</sub>").replace("fb⁻¹", "fb<super>−1</super>")
    return KeepTogether(([head] if head else []) + [Image(p, width=w * mm, height=w * mm * ih / iw), P(cap + f' <font color="#5b6770">[{name}]</font>', "cap")])
def s95(b):                                                                  # 95% CLs signal, n_obs = round(b) (as S1/S2 summaries)
    n = int(round(b)); return optimize.brentq(lambda s: stats.poisson.cdf(n, s + b) / stats.poisson.cdf(n, b) - 0.05, 1e-3, 300)
fb = "fb<super>−1</super>"; f0 = lambda x: "–" if pd.isna(x) else f"{x:.0f}"

R = pd.read_csv(f"{D}/reach_summary.csv"); BV = pd.read_csv(f"{D}/background_vs_mu.csv"); TB = pd.read_csv(f"{D}/background_13p6TeV_thresholds.csv")
X = pd.read_csv(f"{D}/xsec_and_trigger.csv"); MX = pd.read_csv(f"{D}/mix_test_mu50.csv"); BT = pd.read_csv(f"{D}/bootstrap.csv"); RV = pd.read_csv(f"{D}/reach_variants.csv")
FA = pd.read_csv(f"{D}/factors_13_vs_13p6.csv"); EV = pd.read_csv(f"{D}/expected_events.csv");
UB, UR, UM, US = (pd.read_csv(f"{D}/unc_{f}.csv") for f in ("budget", "reach", "consistency_mass", "consistency")); S1B = pd.read_csv(f"{S1}/S1_background_run2.csv")
XS = {l.split()[0]: float(l.split()[1]) for l in open(f"{S2}/inputs/zgamma_xsec_13p6TeV.txt")}
def rch(scen, ch, sct, cn):
    r = R[(R.scenario == scen) & (R.channel == ch) & (R.sct == sct) & (R.contour == cn)]
    if not len(r): return "–"
    r = r.iloc[0]; return f"{r.m_max:.0f}" + ("" if pd.isna(r.lo) else f" ({r.lo:.0f}–{r.hi:.0f})")
SCTN = {"Z1160": "1.16 mm", "Z0": "0"}
rows_set = [(ch, sct) for ch in ("colored", "EW") for sct in ("Z1160", "Z0")]

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=15 * mm, bottomMargin=15 * mm, title="Quirk coplanarity search at 13 and 13.6 TeV",
                        author="coplanarity study")
E = []
E += [P("Quirk coplanarity search at √s = 13 TeV (Run 2) and 13.6 TeV (Run 3)", "h1"),
      P("Knapen geometry, coplanarity selection; signal without pile-up, converted-photon background with pile-up μ = 0–60. Status 2026-11-04 (stages 1 and 2 of the publication plan).", "m"),
      Spacer(1, 4)]
r332 = lambda ch, sct, cn: R[(R.scenario == "13p6TeV_332fb") & (R.channel == ch) & (R.sct == sct) & (R.contour == cn)].iloc[0]
def loss(ch):                                                               # sigma_z = 0 reach lost to pile-up (mu = 20-60), min-max over exclusion and discovery
    v = [R[(R.scenario == "13p6TeV_332fb_mu0") & (R.channel == ch) & (R.sct == "Z0") & (R.contour == cn)].m_max.iloc[0] - R[(R.scenario == f"13p6TeV_332fb_mu{mu}") & (R.channel == ch) & (R.sct == "Z0") & (R.contour == cn)].m_max.iloc[0]
         for cn in ("exclusion", "discovery") for mu in (20, 50, 60)]; return f"{min(v):.0f}–{max(v):.0f}"
def gain(ch):                                                               # sigma_z = 0 over 1.16 mm without pile-up, 332 fb^-1
    v = [r332(ch, "Z0", cn).m_max - r332(ch, "Z1160", cn).m_max for cn in ("exclusion", "discovery")]; return f"{min(v):.0f}–{max(v):.0f}"
def lead(ch, mus=(50, 60)):                                                  # sigma_z = 0 with pile-up minus sigma_z = 1.16 mm, 332 fb^-1, min-max over contours and mu
    v = [R[(R.scenario == f"13p6TeV_332fb_mu{mu}") & (R.channel == ch) & (R.sct == "Z0") & (R.contour == cn)].m_max.iloc[0] - r332(ch, "Z1160", cn).m_max for cn in ("exclusion", "discovery") for mu in mus]
    return f"{min(v):.0f}–{max(v):.0f}"
def lumi140():                                                              # reach change 139 -> 140.1 fb^-1, from the 139 -> 300 fb^-1 slope in ln L (same 13 TeV sample)
    v = [(R[(R.scenario == "13TeV_300fb") & (R.channel == ch) & (R.sct == sct) & (R.contour == cn)].m_max.iloc[0] - R[(R.scenario == "13TeV_139fb") & (R.channel == ch) & (R.sct == sct) & (R.contour == cn)].m_max.iloc[0])
         * np.log(140.1 / 139) / np.log(300 / 139) for ch, sct in rows_set for cn in ("exclusion", "discovery")]
    return f"{max(v):.1f}"
s1z = BV[(BV.sqrt_s_TeV == 13) & (BV.sct == "Z0") & (BV.mu == 50)]; k146, k181 = int(s1z[s1z.note.isna()].sr.iloc[0]), int(s1z[s1z.note.notna()].sr.iloc[0])   # stage 1 mu = 50, both seeds
def ur(E, ch, sct, cn, mu=-1):
    r = UR[(UR.sqrt_s_TeV == E) & (UR.channel == ch) & (UR.sct == sct) & (UR.contour == cn) & (UR.mu == mu)]; return r.iloc[0]
pm = lambda r, m="all": f"<super>+{r[m + '_84'] - r.central:.0f}</super><sub>−{r.central - r[m + '_16']:.0f}</sub>"
pmt = lambda r, m="all": f"+{r[m + '_84'] - r.central:.0f} / −{r.central - r[m + '_16']:.0f}"
cv = lambda r, m="all": f"{r.central:.0f} {pm(r, m)}"
ubz = lambda sct: UB[(UB.sct == sct) & (UB.status == "computed")]
urng = lambda sct: f"{100 * ubz(sct).rel_tot_lo.min():.0f}–{100 * ubz(sct).rel_tot_hi.max():.0f}%"
gen_rng = f"{100 * UB.rel_sigma.min():.0f}–{100 * UB[UB.status == 'computed'].rel_gen.max():.0f}%"
U36 = UR[(UR.sqrt_s_TeV == 13.6) & (UR.mu == -1)]; u0 = U36[U36.sct == "Z0"]
z0rng = f"{min((u0.central - u0.all_16).min(), (u0.all_84 - u0.central).min()):.0f}–{max((u0.central - u0.all_16).max(), (u0.all_84 - u0.central).max()):.0f}"
ubk = UR[UR.mu >= 0]; bkmax = max((ubk.central - ubk.bkg_16).max(), (ubk.bkg_84 - ubk.central).max())
cst = lambda ch, sct: US[(US.channel == ch) & (US.sct == sct) & US.test.str.startswith("selection")].iloc[0]
pl = lambda ch, cn: R[(R.scenario == "13p6TeV_332fb_pooled_eff") & (R.channel == ch) & (R.sct == "Z1160") & (R.contour == cn)].iloc[0].m_max
E += [key(f"<b>Main results.</b> At 13.6 TeV with the ATLAS Run 3 recorded luminosity (332 {fb}) and the Knapen SCT resolution (σ<sub>z</sub> = 1.16 mm), the expected "
          f"exclusion / discovery reach is {cv(ur(13.6,'colored','Z1160','exclusion'))} / {cv(ur(13.6,'colored','Z1160','discovery'))} GeV for colored and "
          f"{cv(ur(13.6,'EW','Z1160','exclusion'))} / {cv(ur(13.6,'EW','Z1160','discovery'))} GeV for EW quirks (total statistical ±1σ, Sect. 5.4); this setting has zero background up to μ = 50 and 0.08 events at μ = 60, "
          f"so pile-up does not change it. With σ<sub>z</sub> = 0 the reach without pile-up is higher ({r332('colored','Z0','exclusion').m_max:.0f} / {r332('EW','Z0','exclusion').m_max:.0f} GeV exclusion), "
          f"but pile-up brings 9–17 background events and costs {loss('colored')} GeV (colored) and {loss('EW')} GeV (EW). This removes most of the σ<sub>z</sub> = 0 advantage, but not all of it: at μ = 50–60 σ<sub>z</sub> = 0 is still {lead('colored')} GeV (colored) and {lead('EW')} GeV (EW) ahead of σ<sub>z</sub> = 1.16 mm. The colored σ<sub>z</sub> = 1.16 mm reach at 13.6 TeV lies below the "
          f"expectation from the cross-section gain by 1.1–1.7σ (bootstrap), traced to 3–5 fewer selected events; a permutation test of the selection efficiency gives p = {cst('colored','Z1160').p_chi2:.2f} (global p = {cst('colored','Z1160').p_global_4tests:.2f} for the four channel tests), i.e. a normal fluctuation; pooling both samples gives ≈ {pl('colored','exclusion'):.0f} / "
          f"{pl('colored','discovery'):.0f} GeV."), Spacer(1, 6)]

# expected events: 13 TeV N x gain ("should be") against 13.6 TeV N, per mass point (best Lambda)
e13, e136 = EV[EV.scenario == "13TeV_139fb"].set_index(["channel", "sct", "mass_gev"]), EV[EV.scenario == "13p6TeV_332fb"].set_index(["channel", "sct", "mass_gev"])
J = e13.join(e136, lsuffix="13", rsuffix="136", how="right"); J["gain"] = J.pre_N136 / J.pre_N13; J["ratio"] = np.where(J.status13 == "computed", J.best_N136 / (J.best_N13 * J.gain), np.nan)
rng = lambda v, f="{:.2f}": f"{f.format(np.nanmin(v))}–{f.format(np.nanmax(v))}"
jz = lambda ch, sct: J.xs((ch, sct), level=("channel", "sct"))
RVx = RV[RV.lumi_fb == 332]
shift = [r.expected_13TeVeff_x_13p6sigma - R[(R.scenario == "13TeV_139fb") & (R.channel == r.channel) & (R.sct == r.sct) & (R.contour == r.contour)].m_max.iloc[0] for r in RVx.itertuples()]

# ---- 0. plain-language summary
c12 = lambda ch, sct, cn: R[(R.scenario == "13TeV_139fb") & (R.channel == ch) & (R.sct == sct) & (R.contour == cn)].m_max.iloc[0]
E += [P("In simple words", "h2")]
E += B(["<b>What we did.</b> We ran the same quirk search twice: once at the Run 2 energy (13 TeV, 139 " + fb + ") and once at the Run 3 energy (13.6 TeV, 332 " + fb + "). "
        "Everything is the same (generator cards, seeds, detector, selection); only the beam energy and the amount of data change. For every mass point we count how many quirk "
        "events we expect to see after all cuts (Sect. 3.1, Fig. 11). A mass is <i>excluded</i> if we expect at least 3 events with no background, and <i>discoverable</i> with 5.",
        f"<b>What should happen.</b> At 13.6 TeV quirks are produced {rng(X[X.sqrt_s_TeV == 13.6].sigma_fb.values / X[X.sqrt_s_TeV == 13].set_index(['channel', 'mass_gev']).loc[list(zip(X[X.sqrt_s_TeV == 13.6].channel, X[X.sqrt_s_TeV == 13.6].mass_gev))].sigma_fb.values, '{:.2f}')} "
        f"times more often (Fig. 1) and Run 3 has {332 / 139:.1f} times more data. Together with the trigger and charge fractions, each mass point should have "
        f"{rng(J.gain, '{:.1f}')} times more events than at 13 TeV (column 'gain' in Sect. 3.1), and the reach should move up by {min(shift):.0f}–{max(shift):.0f} GeV.",
        f"<b>What we found.</b> σ<sub>z</sub> = 0 behaves as expected (colored {c12('colored','Z0','exclusion'):.0f} → {r332('colored','Z0','exclusion').m_max:.0f} GeV, EW "
        f"{c12('EW','Z0','exclusion'):.0f} → {r332('EW','Z0','exclusion').m_max:.0f} GeV), and so does EW at σ<sub>z</sub> = 1.16 mm ({c12('EW','Z1160','exclusion'):.0f} → "
        f"{r332('EW','Z1160','exclusion').m_max:.0f} GeV). Colored at σ<sub>z</sub> = 1.16 mm moves up less ({c12('colored','Z1160','exclusion'):.0f} → "
        f"{r332('colored','Z1160','exclusion').m_max:.0f} GeV) because at 1200–1800 GeV only 0–3 events of 54–85 simulated ones pass, fewer than at 13 TeV. "
        "All other factors (cross section, trigger, charge, kinematics) agree, so this is a statistical fluctuation of a small sample (1.1–1.7σ), not an error in the setup (Sect. 5.2).",
        "<b>Pile-up.</b> With the Knapen resolution (σ<sub>z</sub> = 1.16 mm) pile-up creates almost no fake signal (0 events up to μ = 50, 0.08 at μ = 60), so the reach stays the same. "
        f"With σ<sub>z</sub> = 0, pile-up creates 9–17 fake events, and the reach drops by {loss('colored')} GeV (colored) and {loss('EW')} GeV (EW). It is still "
        f"{lead('colored')} GeV (colored) and {lead('EW')} GeV (EW) better than σ<sub>z</sub> = 1.16 mm.",
        "<b>Caveat.</b> The signal itself is simulated without pile-up (as in the paper). Pile-up hits could also confuse the plane finder for real quirk events, mostly at "
        "σ<sub>z</sub> = 0, so the true reach with pile-up may be somewhat lower than shown.",
        f"<b>How sure are we.</b> Every number now has a statistical ±1σ (Sect. 5.4). The largest part comes from the small number of selected events k "
        f"({urng('Z1160')} on N at σ<sub>z</sub> = 1.16 mm, {urng('Z0')} at σ<sub>z</sub> = 0); σ, ε<sub>trig</sub> and f<sub>ch</sub> add only {gen_rng}. On the reach this is "
        f"{cv(ur(13.6,'colored','Z1160','exclusion'))} GeV (colored, 1.16 mm) and {cv(ur(13.6,'colored','Z0','exclusion'))} GeV (colored, σ<sub>z</sub> = 0). "
        f"The test 'are the 13 and 13.6 TeV selection efficiencies the same?' passes for all four channels (p = {US[US.test.str.startswith('selection')].p_chi2.min():.2f}–{US[US.test.str.startswith('selection')].p_chi2.max():.2f}).",
        "<b>Biggest limitation.</b> Too few simulated events near the reach limit (k = 0–9 passing events per point for colored, σ<sub>z</sub> = 1.16 mm). "
        "5–10 times larger samples there would remove the fluctuation question (Sect. 6, open points)."])

# ---- 1. setup
E += [P("1. Setup (identical at both energies except the beam energy)", "h2")]
E += [grid([H("Step", "Setting"),
            Cc("Signal generation", "MG5_aMC 3.7.3 + Pythia8 (R-hadrons on), p p → Q Q̄ + 0, 1 jet, MLM merging (xqcut 30 GeV), nn23lo1; 2000 events per mass point, the same seed per point at both energies; colored (3,1)<sub>2/3</sub>: 600–2400 GeV, EW (1,1)<sub>1</sub>: 100–1000 GeV"),
            Cc("Trigger", "p<sub>T</sub>(Q Q̄) > 200 GeV; colored: both quirk-hadrons charged (f<sub>ch</sub>)"),
            Cc("Propagation", "Nambu–Goto quirk-pair integrator, B = 2 T, 8-layer barrel of arXiv:1708.02243 (Knapen et al.), t < 25 ns; Λ = 0.1–25 keV (15 values); per-event seeds identical at both energies"),
            Cc("Selection", "paper plane search (Δs, Δw cuts), 8-layer hit multiplicity, signal region; SCT z resolution σ<sub>z</sub> = 1.16 mm (Knapen) and σ<sub>z</sub> = 0"),
            Cc("Signal yield", "N = L σ ε<sub>trig</sub> f<sub>ch</sub> k / n; ±1σ: Wilson 68% on k/n; points with k = 0 are not interpolated"),
            Cc("Background", "converted photons from Z(νν̄)γj (MET > 200 GeV), 1% conversion probability, overlaid with minimum-bias pile-up (Pythia8 SoftQCD:nonDiffractive, Monash, 20 000-event pool) at μ = 0, 20, (33.7), 50, 60; pile-up only (no photon) as a cross-check"),
            Cc("Statistics", "zero background: N = 3 exclusion, N = 5 discovery (as the paper); with background b: exclusion = 95% CL<sub>s</sub> with n<sub>obs</sub> = round(b), discovery = max(5, Asimov Z = 5)")],
           [32, 142])]
E += [P("Energy and luminosity", "h3")]
E += B([f"√s = 13.6 TeV (6.8 TeV per beam) since 5 July 2022 (ATLAS press statement; CMS; CERN Courier, 'Run 3 physics gets under way').",
        f"Run 3 luminosity: 332 {fb} is the ATLAS <i>recorded</i> Run 3 pp total given in the ATLAS status talk at the 166th LHCC open session (1 June 2026, E. Schopf: 31.0 {fb} recorded in 2026, "
        f"Run 3 total 332 {fb}). It is the recorded value, not the final 'good for physics' value, which will be a few per cent lower. 300 {fb} is shown for comparison with Knapen et al.; "
        f"355 {fb} (CMS delivered) is in the CSVs.",
        f"Run 2 luminosity: stage 1 keeps 139 {fb}, the value of the reproduced paper and of the earlier ATLAS Run 2 analyses. The final ATLAS value is 140.1 ± 1.2 {fb} "
        f"(ATLAS, Eur. Phys. J. C 83 (2023) 982, arXiv:2212.09379): +0.8% in N, which moves the reach by at most {lumi140()} GeV (from the 139 → 300 {fb} change of the same sample). "
        "⟨μ⟩ = 33.7 (ATLAS 2015–2018) is used besides μ = 20 and 50."])

# ---- 2. 13 TeV
E += [PageBreak(), fig("F03_reach_13TeV_139fb", 150, head=P("2. Stage 1: 13 TeV, 139 fb<super>−1</super>", "h2"))]
E += [grid([H("Channel", "SCT σ<sub>z</sub>", f"Exclusion, 139 {fb} (±1σ)", f"Discovery, 139 {fb} (±1σ)", f"Exclusion / discovery, 300 {fb}")] +
           [Cc(ch, SCTN[sct], rch("13TeV_139fb", ch, sct, "exclusion"), rch("13TeV_139fb", ch, sct, "discovery"),
               f"{rch('13TeV_300fb', ch, sct, 'exclusion').split(' ')[0]} / {rch('13TeV_300fb', ch, sct, 'discovery').split(' ')[0]}") for ch, sct in rows_set], [22, 20, 46, 46, 40])]
E += [P("Maximum m<sub>Q</sub> reach in GeV (over Λ), zero background.", "m")]
b13 = BV[(BV.sqrt_s_TeV == 13)].sort_values(["sct", "mu"])
E += [P("Background at 13 TeV (converted photons + pile-up), 139 fb<super>−1</super>", "h3"),
      grid([H("SCT σ<sub>z</sub>", "μ", "plane / mult / SR (of 9139)", f"N<sub>bkg</sub> (139 {fb})", "required s (95% CL<sub>s</sub>)")] +
           [Cc(SCTN[r.sct], f"{r.mu:g}" + (" (2nd seed)" if isinstance(r.note, str) else ""), f"{'–' if pd.isna(r.plane) else int(r.plane)} / {'–' if pd.isna(r.mult) else int(r.mult)} / {r.sr}",
               f"< {139 * 2.112 * r.frac_UL95:.3f}" if r.sr == 0 else f"{139 * 2.112 * r.frac:.2f}",
               "3.0" if r.sr <= 1 else f"{s95(139 * 2.112 * r.frac):.2f}")
            for r in b13.itertuples()], [22, 22, 50, 40, 40])]
E += [P("σ<sub>γ</sub> × 1% = 2.112 fb at 13 TeV. With σ<sub>z</sub> = 1.16 mm no event passes at any μ. With σ<sub>z</sub> = 0, 1 event passes without pile-up and 115–181 with pile-up; the "
        "μ = 50 value 146 is a low fluctuation (Sect. 5.3; 181 with a second pile-up seed). μ = 0: only the signal-region count is stored.", "m")]

# ---- 3. 13.6 TeV signal
E += [PageBreak(), P("3. Stage 2: signal at 13.6 TeV", "h2"), fig("F01_cross_sections", 165)]
x13, x136 = X[X.sqrt_s_TeV == 13].set_index(["channel", "mass_gev"]), X[X.sqrt_s_TeV == 13.6].set_index(["channel", "mass_gev"])
E += [grid([H("Channel", "m<sub>Q</sub> [GeV]", "σ 13 TeV [fb]", "σ 13.6 TeV [fb]", "ratio", "ε<sub>trig</sub> 13 / 13.6", "f<sub>ch</sub> 13 / 13.6")] +
           [Cc(ch, m, f"{x13.loc[(ch, m)].sigma_fb:.4g}", f"{x136.loc[(ch, m)].sigma_fb:.4g}", f"{x136.loc[(ch, m)].sigma_fb / x13.loc[(ch, m)].sigma_fb:.2f}",
               f"{x13.loc[(ch, m)].eps_trig:.3f} / {x136.loc[(ch, m)].eps_trig:.3f}", f"{x13.loc[(ch, m)].f_ch:.3f} / {x136.loc[(ch, m)].f_ch:.3f}" if ch == "colored" else "1 / 1")
            for ch, m in x136.index], [20, 20, 28, 28, 18, 32, 28])]
E += [fig("F02_trigger_and_charge", 174)]
E += [fig("F04_reach_13p6TeV_332fb")]
E += [grid([H("Channel", "SCT σ<sub>z</sub>", f"13.6 TeV, 332 {fb} (±1σ)", f"13.6 TeV, 300 {fb} (±1σ)", f"13.6 TeV, 355 {fb}", f"13 TeV, 139 {fb}")] +
           sum([[Cc(ch, SCTN[sct] + f" – {cn[:4]}.", rch("13p6TeV_332fb", ch, sct, cn), rch("13p6TeV_300fb", ch, sct, cn), rch("13p6TeV_355fb", ch, sct, cn).split(" ")[0], rch("13TeV_139fb", ch, sct, cn).split(" ")[0])
                 for cn in ("exclusion", "discovery")] for ch, sct in rows_set], []), [20, 26, 38, 38, 26, 26])]
E += [P("Maximum m<sub>Q</sub> reach in GeV, no pile-up, zero background (13.6 TeV σ<sub>z</sub> = 0 background without pile-up: 0.25 events at 332 fb<super>−1</super>).", "m")]

# ---- 3.1 expected events per mass point
E += [PageBreak(), fig("F11_expected_events", 165, head=P("3.1 Expected signal events at every mass point: what should happen and what we see", "h2"))]
nf = lambda x: f"{x:.0f}" if x >= 100 else f"{x:.3g}"
def nk(r): return nf(r.best_N) + ("  (bound)" if r.status == "bound" else f"  ({int(r.best_k)}/{r.n_prop})")
rows_e = []
for ch, sct in rows_set:
    for m in sorted(set(e136.loc[(ch, sct)].index) | set(e13.loc[(ch, sct)].index)):
        a, b = e13.loc[(ch, sct, m)], e136.loc[(ch, sct, m)]; g = b.pre_N / a.pre_N; exp = a.best_N * g
        rows_e.append(Cc(ch, SCTN[sct], m, nk(a), f"{g:.2f}", nf(exp) if a.status == "computed" else "–", nk(b), f"{b.best_N / exp:.2f}" if a.status == "computed" else "–"))
E += [grid([H("Channel", "SCT σ<sub>z</sub>", "m<sub>Q</sub> [GeV]", f"13 TeV, 139 {fb}: N (k/n)", "gain", "13.6 TeV should be", f"13.6 TeV, 332 {fb}: N (k/n)", "seen / should")] + rows_e,
           [17, 18, 16, 33, 13, 24, 33, 20])]
E += [P("N = expected signal events at the Λ with the largest N (Λ is chosen per mass point; N at Λ = 2 keV and the Λ of each maximum are in data/expected_events.csv). "
        "k/n: events passing all cuts / events propagated. gain = (L σ ε<sub>trig</sub> f<sub>ch</sub>)<sub>13.6 TeV, 332</sub> / (L σ ε<sub>trig</sub> f<sub>ch</sub>)<sub>13 TeV, 139</sub>: "
        "the factor the event count should grow by if the selection efficiency k/n stays the same. 'should be' = 13 TeV N × gain. Every simulated mass point is included; "
        "colored 2400 GeV was not propagated at 13 TeV because even with 100% selection N would be only 0.12.", "m")]
zc = pd.concat([jz("colored", "Z0"), jz("EW", "Z0")]); zk = pd.concat([jz("colored", "Z1160"), jz("EW", "Z1160")]); cz = jz("colored", "Z1160")
E += [key(f"<b>Reading the table.</b> 'seen / should' near 1 means 13.6 TeV behaves as expected. Where many events pass (σ<sub>z</sub> = 0, k = {rng(zc.best_k136, '{:.0f}')}) it stays "
          f"within {rng(zc.ratio)}. At σ<sub>z</sub> = 1.16 mm, where k = {rng(zk.best_k136, '{:.0f}')}, it swings more: {rng(zk.ratio)}; for colored {rng(cz.ratio)}. At 1200 GeV 13.6 TeV sees 2 of 85 events against 7 of 70 at 13 TeV, which is what "
          f"pulls the 13.6 TeV reach down. With k this small, one or two events more or less change N by a factor 2; Sect. 5.2 shows this is a 1.1–1.7σ fluctuation.")]

# ---- 4. backgrounds and pile-up at 13.6 TeV
E += [PageBreak(), P("4. Stage 2: converted-photon background and pile-up at 13.6 TeV", "h2")]
E += B([f"Z(νν̄)γj regenerated at 13.6 TeV (same cards and seed as the 13 TeV sample): σ = {XS['sigma_generated_pb']:.4f} pb, {int(XS['n_events_after_MET'])} of 10 000 events with post-shower "
        f"MET > 200 GeV, σ<sub>γ</sub> = {XS['sigma_after_MET_pb']:.4f} pb (13 TeV: 0.2111 pb); σ<sub>γ</sub> × 1% = {XS['sigma_after_MET_pb'] * 10:.3f} fb.",
        "Minimum-bias pool regenerated at 13.6 TeV (same code, events and seed as at 13 TeV): 113.9 charged particles per event (13 TeV: 112.8, +0.9%)."])
E += [fig("F06_background_vs_pileup")]
b136 = BV[BV.sqrt_s_TeV == 13.6].sort_values(["sct", "mu"]); tb = TB.set_index(["sct", "mu"])
E += [grid([H("SCT σ<sub>z</sub>", "μ", "plane / mult / SR (of 9130)", f"N<sub>bkg</sub> (332 {fb})", "s exclusion", "s discovery")] +
           [Cc(SCTN[r.sct], f"{r.mu:g}", f"{int(r.plane)} / {int(r.mult)} / {r.sr}", f"< {tb.loc[(r.sct, r.mu)].b_used_332fb:.2f}" if r.sr == 0 else f"{tb.loc[(r.sct, r.mu)].N_bkg_332fb:.2f}",
               f"{tb.loc[(r.sct, r.mu)].s_excl_332fb:.1f}", f"{tb.loc[(r.sct, r.mu)].s_disc_332fb:.1f}") for r in b136.itertuples()], [22, 16, 50, 34, 26, 26])]
E += [P("Pile-up alone (no photon, σ<sub>z</sub> = 1.16 mm, 5000 events): 12 / 101 / 183 planes at μ = 20 / 50 / 60, none in the signal region (< 6×10<super>−4</super> per event, 95%). "
        "At μ = 60 one σ<sub>z</sub> = 1.16 mm event passes: its plane has 14 conversion hits and one pile-up hit, which completes the 8-layer multiplicity.", "m")]
E += [fig("F05_reach_13p6TeV_pileup")]
E += [grid([H("Channel", "SCT σ<sub>z</sub>", "contour", "μ = 0", "μ = 20", "μ = 50", "μ = 60")] +
           [Cc(ch, SCTN[sct], cn, *[rch(f"13p6TeV_332fb_mu{mu}", ch, sct, cn).split(" ")[0] for mu in (0, 20, 50, 60)]) for ch, sct in rows_set for cn in ("exclusion", "discovery")],
           [22, 22, 26, 26, 26, 26, 26])]
E += [P(f"Maximum m<sub>Q</sub> reach in GeV at 13.6 TeV, 332 {fb}, with the background of each μ (signal efficiencies without pile-up).", "m")]

# ---- 5. checks
E += [PageBreak(), P("5. Checks", "h2"), P("5.1 Validation of the 13.6 TeV chain against 13 TeV", "h3")]
E += B(["Signal generation: EW 800 GeV regenerated at 13 TeV with the new script reproduces the September sample (1024 matched events, σ = 0.2341 fb, all 1 222 451 HepMC particle lines identical). "
        "A first attempt segfaulted because MG5 recompiled parts with the system gfortran 13.3 against objects built with the conda gfortran 16.2; the hep environment is now first in PATH.",
        "Propagation driver: 6 EW 800 GeV events reproduce the 13 TeV checkpoints exactly (42 rows); extraction: charges of all 11 620 13 TeV quirk-hadrons reproduced.",
        "Minimum-bias pool: the first 300 events (32 986 particles) of the 13 TeV pool are reproduced exactly.",
        "Overlay at μ = 0: 0/9139 (σ<sub>z</sub> = 1.16 mm) and 1/9139 (σ<sub>z</sub> = 0), the stage 1 values; the first 1000 rows of the original 13 TeV μ = 50 run are reproduced exactly.",
        "Z(νν̄)γj regenerated at 13 TeV: not bit-identical (the process folder keeps grids of later runs), statistically the same: σ = 0.2316 ± 0.0007 pb against 0.2311 pb, "
        "9149 against 9139 events after MET, KS p = 0.46–0.93 for p<sub>T</sub>(γ), MET, |η|, E."])
E += [P("5.2 Colored σ<sub>z</sub> = 1.16 mm: lower reach at 13.6 TeV", "h3")]
bm = FA[(FA.channel == "colored") & (FA.mass_gev == 1800) & (FA.lambda_keV.isna() | (FA.lambda_keV == 2))]
lab = {"sigma_fb": "σ [fb]", "eps_trig": "ε<sub>trig</sub>", "f_ch": "f<sub>ch</sub>", "eps_fid": "ε<sub>fid</sub>", "eps_reco": "ε<sub>reco</sub>", "k/n": "k/n"}
E += [grid([H("Factor (1800 GeV, 2 keV)", "SCT", "13 TeV", "13.6 TeV", "ratio", "z")] +
           [Cc(lab[r.factor], {"Z1160": "1.16 mm", "Z0": "0"}.get(r.sct, "–") if isinstance(r.sct, str) else "–", r.counts13 if isinstance(r.counts13, str) and r.counts13 else f"{r.v13:.3f}",
               r.counts13p6 if isinstance(r.counts13p6, str) and r.counts13p6 else f"{r.v13p6:.3f}", f"{r.ratio:.2f}" if np.isfinite(r.ratio) else "–", f"{r.z:+.1f}" if np.isfinite(r.z) else "–")
            for r in bm.itertuples()], [40, 20, 32, 32, 22, 22])]
E += B(["At the benchmark the only difference is ε<sub>reco</sub> at σ<sub>z</sub> = 1.16 mm (3/20 against 0/18); on the same fiducial events the σ<sub>z</sub> = 0 selection gives 11/20 against 10/18.",
        "ε<sub>trig</sub> at all colored points: z = −1.5 … +2.4 with both signs; f<sub>ch</sub> |z| ≤ 1.6; quirk p<sub>T</sub>, |η|, β, p<sub>T</sub>(QQ̄): 1 of 48 KS tests with p < 0.05. No sign of a setup difference (PDF, matching, Pythia)."])
E += [fig("F10_selection_efficiency_colored")]
rv = RV[RV.lumi_fb == 332]
E += [grid([H("Channel", "SCT", "contour", f"13 TeV (300 {fb})", "expected", "13.6 TeV", "pooled ε", "Δ / σ<sub>boot</sub>")] +
           [Cc(r.channel, SCTN[r.sct], r.contour, f0(r.reach_13TeV_300fb), f0(r.expected_13TeVeff_x_13p6sigma), f0(r.reach_13p6TeV), f0(r.pooled_eff_13p6sigma),
               (lambda b: f"{b.delta_observed:+.0f} / {b.sigma_boot:.0f} = {b.delta_observed / b.sigma_boot:+.1f}")(BT[(BT.channel == r.channel) & (BT.sct == r.sct) & (BT.contour == r.contour)].iloc[0]))
            for r in rv.itertuples()], [18, 18, 20, 26, 20, 20, 20, 32])]
E += [P(f"Reach in GeV at 332 {fb}. Expected: 13 TeV selection efficiencies with the 13.6 TeV σ ε<sub>trig</sub> f<sub>ch</sub>. Pooled: efficiencies of both samples combined. "
        "Δ = 13.6 TeV − expected; σ<sub>boot</sub> from 500 bootstrap replicas.", "m"), fig("F09_bootstrap_13_vs_13p6", 150)]
E += [key("<b>Conclusion 5.2.</b> The colored σ<sub>z</sub> = 1.16 mm deficit is a 1.1–1.7σ fluctuation of ε<sub>reco</sub> in a selection with k = 0–9 events per point; σ, f<sub>ch</sub>, "
          "ε<sub>fid</sub> and the kinematics agree (ε<sub>trig</sub> scatters more, Sect. 5.4, but enters with its own value at each energy), and the σ<sub>z</sub> = 0 selection on the same events gives the expected gain. Deviations of both signs occur (EW σ<sub>z</sub> = 0 exclusion −1.9σ). "
          "The permutation test of Sect. 5.4 confirms it. Larger samples at 1200–2100 GeV would settle it.")]
E += [fig("F07_mix_test_mu50", 150, head=P("5.3 σ<sub>z</sub> = 0 background at μ = 50: 146 (13 TeV) against 196 (13.6 TeV)", "h3"))]
E += [grid([H("Photons", "Pile-up pool", "plane / mult / SR", "fraction [%] (68%)")] +
           [Cc(f"{r.photons_TeV:g} TeV", f"{r.pileup_TeV} TeV", f"{r.plane} / {r.mult} / {r.sr} of {r.n}", f"{100 * r.frac:.2f} ({100 * r.frac_lo:.2f}–{100 * r.frac_hi:.2f})") for r in MX.itertuples()], [30, 46, 54, 44])]
E += [key("<b>Conclusion 5.3.</b> Three combinations and the second-seed 13 TeV run cluster at ≈ 2%; only the original 13 TeV run (146) is low. Different pile-up configurations select "
          "different events (50–68 of ≈ 190 shared), so the runs are nearly independent samples: 146 is a low fluctuation, not an energy effect. The 13.6 TeV numbers stand; the stage 1 "
          "μ = 50 σ<sub>z</sub> = 0 background (4.7 events at 139 fb<super>−1</super>) would be ≈ 5.8 with the second seed; the stage 1 tables are left unchanged.")]

# ---- 5.4 statistical uncertainties
E += [PageBreak(), P("5.4 Statistical uncertainties of every number", "h3")]
E += [P("Script S2_11_uncertainties.py. Statistical only: MG5 integration error on σ; Wilson 68% on ε<sub>trig</sub>, f<sub>ch</sub>, k/n and the background fraction; toys and "
        "permutations as described below. Not included: PDF, scale, shower and detector systematics.", "m")]
pc = lambda x: f"{100 * x:.0f}" if x >= 0.095 else f"{100 * x:.1f}"
def kb(r): return "–" if r.status == "bound" else f"{int(r.k)}/{int(r.n)}: −{pc(r.rel_kn_lo)}/+{pc(r.rel_kn_hi)}"
def tb(r): return "–" if r.status == "bound" else f"−{pc(r.rel_tot_lo)}/+{pc(r.rel_tot_hi)}"
ub = UB.set_index(["sqrt_s_TeV", "channel", "sct", "mass_gev"]); rows_u = []
for ch in ("colored", "EW"):
    for m in sorted(UB[UB.channel == ch].mass_gev.unique()):
        for E_ in (13.0, 13.6):
            if (E_, ch, "Z0", m) not in ub.index: continue
            a, b = ub.loc[(E_, ch, "Z1160", m)], ub.loc[(E_, ch, "Z0", m)]
            rows_u.append(Cc(ch if E_ == 13.0 else "", m if E_ == 13.0 else "", f"{E_:g}", pc(a.rel_sigma), pc(a.rel_eps_trig), pc(a.rel_f_ch) if ch == "colored" else "–", kb(a), tb(a), kb(b), tb(b)))
E += [P("(a) Uncertainty budget of the expected events N at each mass point (best Λ), relative 68% uncertainty in %", "h3"),
      grid([H("Channel", "m<sub>Q</sub>", "√s", "σ", "ε<sub>trig</sub>", "f<sub>ch</sub>", "1.16 mm: k/n, unc.", "1.16 mm total", "σ<sub>z</sub> = 0: k/n, unc.", "σ<sub>z</sub> = 0 total")] + rows_u,
           [16, 13, 11, 10, 12, 11, 30, 23, 28, 20])]
E += [P(f"13 TeV at 139 {fb}, 13.6 TeV at 332 {fb}. Total = quadrature sum. k/n dominates everywhere; at σ<sub>z</sub> = 1.16 mm with k = 2–3 it is −50/+97%. "
        "Colored 2400 GeV at 13 TeV is not propagated (bound).", "m")]
E += [fig("F13_reach_uncertainty", 165, head=P("(b) Maximum reach with statistical uncertainties", "h3"))]
rows_r = []
for ch, sct in rows_set:
    for cn in ("exclusion", "discovery"):
        a, b = ur(13.0, ch, sct, cn), ur(13.6, ch, sct, cn)
        rows_r.append(Cc(ch, SCTN[sct], cn, cv(a, "kn"), cv(a), cv(b, "kn"), cv(b, "gen"), cv(b), f"{b.all_50:.0f}"))
E += [grid([H("Channel", "SCT σ<sub>z</sub>", "contour", "13 TeV: k/n only", "13 TeV: total", "13.6 TeV: k/n only", "13.6 TeV: σ ε f only", "13.6 TeV: total", "13.6 TeV toy median")] + rows_r,
           [16, 16, 18, 22, 22, 22, 22, 22, 14])]
E += [P(f"Maximum m<sub>Q</sub> in GeV with 16–84% of 1000 toys each (13 TeV 139 {fb}, 13.6 TeV 332 {fb}, zero background). 'k/n only': events resampled (bootstrap); "
        "'σ ε f only': σ, ε<sub>trig</sub>, f<sub>ch</sub> varied; 'total': both. The bootstrap cannot move a k = 0 point up, so the upper error is slightly underestimated where k = 0 occurs. "
        "For colored σ<sub>z</sub> = 1.16 mm at 13.6 TeV the toy median lies above the central value: the central value itself sits low in its own distribution, as a downward fluctuation would.", "m")]
rows_b = []
for ch in ("colored", "EW"):
    for mu in (0, 20, 50, 60):
        for cn in ("exclusion", "discovery"):
            r = ur(13.6, ch, "Z0", cn, mu)
            rows_b.append(Cc(ch, mu, cn, f"{r.threshold:.1f}", f"{r.central:.0f}", pmt(r, "bkg"), pmt(r, "kn"), pmt(r, "gen"), pmt(r, "all")))
E += [P(f"(c) σ<sub>z</sub> = 0 at 13.6 TeV, 332 {fb}, with the pile-up background", "h3"),
      grid([H("Channel", "μ", "contour", "s<sub>req</sub>", "reach [GeV]", "background count", "k/n", "σ ε f", "total")] + rows_b, [18, 12, 22, 16, 22, 26, 20, 18, 20])]
b136z = BV[(BV.sqrt_s_TeV == 13.6) & (BV.sct == "Z0")].set_index("mu")
E += [P("Background count: signal-region events of the 9130 converted photons, varied binomially "
        f"({', '.join(f'μ = {mu:g}: {int(b136z.loc[mu].sr)} ({100 * b136z.loc[mu].frac_lo:.2f}–{100 * b136z.loc[mu].frac_hi:.2f}%)' for mu in (0, 20, 50, 60))}); "
        "the required signal s<sub>req</sub> is recomputed for each toy (95% CL<sub>s</sub>, Asimov). "
        f"The background statistics move the reach by ≤ {bkmax:.0f} GeV; the signal k/n stays the largest part.", "m")]

E += [PageBreak(), fig("F12_pulls_13_vs_13p6", 160, head=P("(d) Is the 13.6 TeV selection efficiency the same as at 13 TeV?", "h3"))]
rows_m = [Cc(r.channel, SCTN[r.sct], r.mass_gev, f"{100 * r.eff13:.2f} ({r.k13_sum}/{r.n13 * 15})", f"{100 * r.eff13p6:.2f} ({r.k13p6_sum}/{r.n13p6 * 15})", f"{r.ratio:.2f}", f"{r.z:+.2f}", f"{r.p_two_sided:.2f}")
          for r in UM.itertuples()]
E += [grid([H("Channel", "SCT σ<sub>z</sub>", "m<sub>Q</sub>", "13 TeV: pass [%] (k/n·15)", "13.6 TeV: pass [%] (k/n·15)", "ratio", "z", "p (two-sided)")] + rows_m, [17, 18, 14, 36, 36, 15, 15, 20])]
E += [P("Pass fraction = passing (event, Λ) pairs / (propagated events × 15 Λ values). z and p from 5000 permutations of the pooled events of each mass point "
        "(keeps the correlation between the Λ values of one event).", "m")]
lab_t = {"eps_trig": "ε<sub>trig</sub>", "f_ch": "f<sub>ch</sub>"}
rows_t = [Cc(lab_t.get(r.test, "selection k/n"), r.channel, SCTN.get(r.sct, "–") if isinstance(r.sct, str) else "–", f"{r.chi2:.1f} / {r.n_points}", f"{r.p_chi2:.3f}", f"{r.signed_z:+.2f}",
             f"{r.p_signed_two:.3f}", "–" if pd.isna(r.p_global_4tests) else f"{r.p_global_4tests:.2f}") for r in US.itertuples()]
E += [P("(e) Combined tests per channel", "h3"),
      grid([H("Quantity", "Channel", "SCT σ<sub>z</sub>", "χ² / ndf", "p(χ²)", "mean pull Σz/√M", "p (two-sided)", "global p (4 tests)")] + rows_t, [30, 18, 18, 20, 18, 26, 22, 22])]
E += [P("Selection k/n: permutation p-values. ε<sub>trig</sub>, f<sub>ch</sub>: two-proportion z per mass point, χ² and normal p. Global p = 1 − (1 − p<sub>min</sub>)<super>4</super>: "
        "the chance that at least one of the four channel × SCT tests looks this extreme.", "m")]
et_c, et_e = US[(US.test == "eps_trig") & (US.channel == "colored")].iloc[0], US[(US.test == "eps_trig") & (US.channel == "EW")].iloc[0]
E += [key(f"<b>Conclusion 5.4.</b> The selection efficiency agrees between 13 and 13.6 TeV in all four channels (p(χ²) = {US[US.test.str.startswith('selection')].p_chi2.min():.2f}–"
          f"{US[US.test.str.startswith('selection')].p_chi2.max():.2f}). For colored σ<sub>z</sub> = 1.16 mm the pulls are {UM[(UM.channel == 'colored') & (UM.sct == 'Z1160')].z.min():+.1f} to {UM[(UM.channel == 'colored') & (UM.sct == 'Z1160')].z.max():+.1f} with mean {cst('colored','Z1160').signed_z:+.2f} "
          f"(p = {cst('colored','Z1160').p_signed_two:.2f}); even picking the worst of the four channels, the global p is {cst('colored','Z1160').p_global_4tests:.2f}. "
          f"So the lower colored reach is a statistical fluctuation. Of 24 single points, one is at 2σ (colored σ<sub>z</sub> = 0, 900 GeV, p = 0.05), as expected by chance. "
          f"ε<sub>trig</sub> scatters more than its errors (colored χ² = {et_c.chi2:.1f}/{et_c.n_points}, p = {et_c.p_chi2:.3f}, both signs; EW mean pull {et_e.signed_z:+.1f}, "
          f"p = {et_e.p_signed_two:.2f}, higher at 13.6 TeV as a harder recoil would give). Each energy uses its own measured ε<sub>trig</sub>, so this does not bias N; "
          f"it is a point to check with the larger samples. The reach uncertainty is dominated by k/n: {z0rng} GeV for σ<sub>z</sub> = 0 and {pm(ur(13.6, 'colored', 'Z1160', 'exclusion'))} GeV for colored σ<sub>z</sub> = 1.16 mm (exclusion).")]

# ---- 6. overview
E += [PageBreak(), fig("F08_reach_summary", 160, head=P("6. Overview", "h2"))]
sc = [("13TeV_139fb", f"13 TeV, 139 {fb}"), ("13p6TeV_332fb", f"13.6 TeV, 332 {fb}"), ("13p6TeV_332fb_mu50", f"13.6 TeV, 332 {fb}, μ = 50"), ("13p6TeV_332fb_pooled_eff", "13.6 TeV, 332, pooled ε")]
E += [grid([H("Channel", "SCT σ<sub>z</sub>") + H(*[s[1] for s in sc])] +
           [Cc(ch, SCTN[sct], *[" / ".join(rch(s, ch, sct, cn).split(" ")[0] for cn in ("exclusion", "discovery")) for s, _ in sc]) for ch, sct in rows_set], [20, 20, 34, 34, 34, 32])]
E += [P("Exclusion / discovery reach in GeV.", "m")]
E += [P("Conclusions", "h3")]
E += B([f"With the Knapen SCT resolution the search is background-free up to μ = 50 (0.08 events at μ = 60) at both energies; Run 3 (13.6 TeV, 332 {fb}) reaches "
        f"{r332('colored','Z1160','exclusion').m_max:.0f} GeV (colored) and {r332('EW','Z1160','exclusion').m_max:.0f} GeV (EW) for exclusion, against 1388 and 451 GeV in Run 2 (139 {fb}).",
        f"With σ<sub>z</sub> = 0 the reach without pile-up is {gain('colored')} GeV (colored) and {gain('EW')} GeV (EW) higher. The pile-up background (≈ 2% of converted photons at μ ≥ 50) "
        f"removes most of that gain but not all: at μ = 50–60 σ<sub>z</sub> = 0 is still {lead('colored')} GeV (colored) and {lead('EW')} GeV (EW) ahead.",
        "All reach values use signal efficiencies without pile-up (as the paper). At σ<sub>z</sub> = 0 pile-up hits can also disturb the plane finder for signal events, so the reach with "
        "pile-up may be lower than given here.",
        "The 13 → 13.6 TeV comparison shows no setup difference; the colored σ<sub>z</sub> = 1.16 mm reach is limited by sample size (k = 0–9 selected events per point)."])
E += [P("Open points", "h3")]
E += B(["Sample size is the largest limitation: colored σ<sub>z</sub> = 1.16 mm has k = 0–9 passing events per point. 5–10 times larger samples near the contours "
        "(colored 1200–2100 GeV, EW 400–800 GeV) are cheap on the 160-core server and would close the 13.6 TeV fluctuation question; best done before the ATLAS-/CMS-like stage, "
        "where the same limitation would appear.",
        f"The stage 1 μ = 50 σ<sub>z</sub> = 0 background ({k146} → {k181} with a second seed, ×{k181 / k146:.2f}) affects equally the reproduction report of 2026-10-21 "
        f"(Part A/B) and the slides, which quote 10–48 events at 300 {fb}: with the second seed this is ≈ {10 * k181 / k146:.0f}–{48 * k181 / k146:.0f} events. Those documents are not changed here.",
        "Signal efficiencies with pile-up overlaid (here, as in the paper, without).",
        "Next stages of the plan (not started): ATLAS-like and CMS-like detectors, GNN, HL-LHC."])
E += [P("Files", "h3")]
E += [P("Stage folders: 06_publication/S1_13TeV_139fb_knapen_noPU_cop, 06_publication/S2_13p6TeV_run3_knapen_noPU_cop (scripts S2_01–S2_10, README). Figures: "
        "06_publication/FIGURES_ROOT_2026-11-04 (prepare_data.py → data/*.csv; make_figures_root.py, ROOT 6.40 → Fxx/*.pdf, .png, .root, .C, caption.md, provenance.json with "
        "sha256 of every input). This report: 06_publication/REPORT_2026-11-04/make_report.py.", "m")]
def foot(c, d):
    c.saveState(); c.setFont("DV", 7); c.setFillColor(MUTED); c.drawString(18 * mm, 8 * mm, "Quirk coplanarity search, 13 and 13.6 TeV — 2026-11-04"); c.drawRightString(192 * mm, 8 * mm, f"{d.page}"); c.restoreState()
doc.build(E, onFirstPage=foot, onLaterPages=foot); print("REPORT", OUT)
