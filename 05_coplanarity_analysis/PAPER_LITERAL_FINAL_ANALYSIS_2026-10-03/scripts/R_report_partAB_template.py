#!/usr/bin/env python3
"""TABLE_I_REPRODUCTION_REPORT_2026-10-21_partAB.pdf (user's request of 2026-10-21): the report restructured into
  Part A, the paper's literal method only (LO 0 + 1 jet MLM-matched, SCT z = 1.16 mm for signal and background, eps_trig = matched count with pT(QQ) > 200 GeV,
          no K-factor, no N_Q factor): Table I, Figs. 2-7 and Fig. 6 with the paper's numbers alongside; no K-factor or LO-ratio statements in Part A or the summary;
  Part B, deviations we tested (our additional study): no SCT z smearing, LO-ratio trigger, sigma scaling (K-factor), N_Q = 2, colored without f_ch, annihilation,
          each with one line on why it was tested;
  Table II: expected events at 300 fb-1 for every signal benchmark and background, with each cross section, for SCT z = 1.16 mm on signal AND background and for
          no SCT z smearing on signal AND background;
  plus formulas in plain words, the reasons for the Delta_s and Delta_w cuts, open points, conclusion and final remarks on the paper.
  L tables in units of 1e8 hbar (tables only; figures unchanged); the same L tables written as CSV to L_VALUES_CSV_2026-10-21/.
No number is recomputed differently from R_report_2026-10-21_v2.py: the Fig. 2, annihilation, repeated-crossing, Fig. 3 and Fig. 7 blocks are taken from it
(scripts/R_build_partAB.py assembled this file); Fig. 6 split figures from F6_07_partA_partB_figs.py (same grid)."""
#<<HEAD>>

# ---------------------------------------------------------------- common inputs of the new structure
GEN = {s: json.load(open(f"{R.EV}/generation/{v['tag']}/generation_stats.json")) for s, v in R.SAM.items()}
SIG = {s: GEN[s]["matched_xsec_pb"] * 1e3 for s in GEN}                          # matched LO cross section (fb) of the Table I samples
LUMI = 300.0
LAMS = {"COL2000": (1, 2, 3, 5, 10), "EW2000": (1, 2, 3, 4, 5)}
NAME = {"COL2000": "colored 1800 GeV", "EW2000": "EW 800 GeV"}
ZL = {"Z1160": "SCT z 1.16 mm", "Z0": "no SCT z smearing"}
PAPER_R = R.PAPER_L
def lsr(s_, lam, sct): return LS[(LS["sample"] == s_) & (LS.lambda_keV == lam) & (LS.sct == sct) & (LS["mode"] == "FIRST")].iloc[0]
RCH = pd.read_csv(f"{R.L_}/fig6/F6_reach.csv"); RSE = pd.read_csv(f"{R.L_}/fig6/F6_reach_sensitivity.csv")
_C6 = pd.read_csv(f"{R.L_}/fig6/inputs/counts.csv"); EWT = {int(r.mass_gev): (int(r.n_trigger), int(r.n_matched)) for r in _C6[_C6.channel == "EW"].itertuples()}
LOR = pd.read_csv(f"{R.L_}/fig6/F6_ew_lo_ratio.csv").set_index("mass_gev").ratio.to_dict()
def rr(sct, var, ch, c_):
    q = RCH[(RCH.channel == ch) & (RCH.sct == sct) & (RCH.variant == var) & (RCH.contour == c_)]
    return f"{int(q.m_max_GeV.iloc[0])} ({int(q.m_max_lo.iloc[0])}–{int(q.m_max_hi.iloc[0])})" if len(q) else "–"
_m = lambda ch, c_, sct: int(RCH[(RCH.channel == ch) & (RCH.sct == sct) & (RCH.variant == "charge factor included") & (RCH.contour == c_)].m_max_GeV.iloc[0])
PAPER_REACH = {("colored", "exclusion"): 1793, ("colored", "discovery"): 1707, ("EW", "exclusion"): 762, ("EW", "discovery"): 688}
_d = lambda ch, c_, sct: 100 * (_m(ch, c_, sct) / PAPER_REACH[(ch, c_)] - 1)
def rs(ch, var, sct):
    q = RSE[(RSE.channel == ch) & (RSE.sct == sct) & (RSE.variant == var)].set_index("contour")
    return f"{q.loc['exclusion', 'm_max']} / {q.loc['discovery', 'm_max']}" if len(q) else "–"
st["part"] = ParagraphStyle("part", fontName="DVB", fontSize=14, leading=18, textColor=colors.white, backColor=ACC, borderPadding=(5, 6, 5, 6), spaceBefore=6, spaceAfter=8)
def bad1(s_, sct): return [str(l) for l in LAMS[s_] if not dec(int(lsr(s_, l, sct).k_ge2), int(lsr(s_, l, sct).n_fid), float(lsr(s_, l, sct).paper_reco))]
def verdict(s_, sct):
    b_ = bad1(s_, sct)
    if not b_: return "consistent with the paper at every Λ"
    if len(b_) == len(LAMS[s_]): return "inconsistent with the paper at every Λ"
    return f"inconsistent at Λ = {', '.join(b_)} keV, consistent at the other Λ"
EP = {s_: {l: (int(lsr(s_, l, z).k_ge2), int(lsr(s_, l, z).n_fid)) for l in LAMS[s_] for z in ("Z1160", "Z0")} for s_ in LAMS}
def er(s_, lam, sct): k, n = int(lsr(s_, lam, sct).k_ge2), int(lsr(s_, lam, sct).n_fid); return k / n
_RAT = [float(lsr(s_, l, "Z1160").paper_reco) / er(s_, l, "Z1160") for s_ in LAMS for l in LAMS[s_] if er(s_, l, "Z1160") > 0]
LOWER = f"{np.floor(min(_RAT)):.0f}–{np.ceil(max(_RAT)):.0f}"                    # paper / ours, eps_reco with SCT z 1.16 mm (k > 0)
_GAIN = [int(lsr(s_, l, "Z0").k_ge2) / int(lsr(s_, l, "Z1160").k_ge2) for s_ in LAMS for l in LAMS[s_] if int(lsr(s_, l, "Z1160").k_ge2) > 0]
GAIN = f"{np.floor(min(_GAIN)):.0f}–{np.ceil(max(_GAIN)):.0f}"                   # signal without / with SCT z smearing
_AN = [int(RCH[(RCH.channel == ch) & (RCH.sct == z) & (RCH.variant == "charge factor included") & (RCH.contour == c_)].m_max_GeV.iloc[0]) - int(RSE[(RSE.channel == ch) & (RSE.sct == z) & (RSE.variant == "annihilation worst") & (RSE.contour == c_)].m_max.iloc[0])
       for ch in ("colored", "EW") for z in ("Z0", "Z1160") for c_ in ("exclusion", "discovery")]
ANN = f"{min(_AN)}–{max(_AN)}"

# ---------------------------------------------------------------- title and summary
S = [P("Reproduction of arXiv:1708.02243: Table I and Figures 2–7", "h1"),
     P("Knapen, Lou, Papucci, Setford, Phys. Rev. D 96, 115015 (2017) · report of 21 October 2026 · Part A: the paper's literal method · Part B: deviations we tested · "
       "Table II: expected events at 300 fb⁻¹", "m"), Spacer(1, 4)]
S += [box("Summary", B([
    "<b>How this report is organised.</b> <b>Part A</b> uses only the method written in the paper. <b>Part B</b> collects the changes we tried ourselves "
    "(our additional study), each with the reason. <b>Table II</b> (after Part B) lists the expected numbers of signal and background events.",
    f"<b>Part A, Table I.</b> Trigger efficiency: colored {c['trig']/c['matched']:.2f} (paper 0.24, agrees), EW {e['trig']/e['matched']:.2f} (paper 0.10, does not agree). "
    "Fiducial efficiency: agrees for both. Reconstruction efficiency with the paper's SCT z resolution of 1.16 mm: far below the paper "
    f"(colored 2 keV: {er('COL2000', 2, 'Z1160'):.2f} vs 0.35; EW 4 keV: {er('EW2000', 4, 'Z1160'):.2f} vs 0.72).",
    f"<b>Part A, Figure 6.</b> Largest mass reached (exclusion / discovery): colored {_m('colored', 'exclusion', 'Z1160')} / {_m('colored', 'discovery', 'Z1160')} GeV "
    f"(paper 1793 / 1707), EW {_m('EW', 'exclusion', 'Z1160')} / {_m('EW', 'discovery', 'Z1160')} GeV (paper 762 / 688).",
    "<b>Part A, backgrounds.</b> No converted-photon event (0 of 9139) and no pile-up event (0 of 5000) passes the signal region, as the paper says.",
    f"<b>Part B, no SCT z smearing (our additional study).</b> The signal efficiencies and the Figure 6 reach come close to the paper (colored {_m('colored', 'exclusion', 'Z0')} / "
    f"{_m('colored', 'discovery', 'Z0')} GeV, EW {_m('EW', 'exclusion', 'Z0')} / {_m('EW', 'discovery', 'Z0')} GeV), but then {BG['conv0']['sr']} of 9139 converted photons also pass "
    "(about 10–48 events at 300 fb⁻¹). No single SCT z setting gives both the paper's signal and its zero background.",
    "<b>Figures 2–5 and 7.</b> Fig. 2: in our simulation |L| returns to zero at every second meeting; in the paper it does not. Figs. 3 and 4: the shapes agree. "
    "Fig. 5: see above. Fig. 7: our hits are faster than the paper's, and its dE/dx panel could not be reproduced."]))]
S += [Spacer(1, 4), box("Questions to answer", B([
    "<b>Q1. Why is the converted-photon upper limit the same for both cross sections?</b> → Section A7.",
    "<b>Q2. Figure 2: why does our |L| go to zero at every second meeting while the paper's does not?</b> → Section A3.",
    "<b>Q3. Which smearing was applied, and how?</b> → Section A1 (paper's method) and Section B1 (no SCT z smearing).",
    "<b>Q4. Which uncertainties are quoted?</b> → Formulas (below) and every table (k/n = ε ± σ)."]))]

# ---------------------------------------------------------------- formulas
S += [P("Formulas used (in plain words)", "h2")]
S += [EQ("Trigger efficiency:   ε<sub>trig</sub> = N(events with p<sub>T</sub>(QQ̄) &gt; 200 GeV) / N(matched events)"),
      EQ("Fiducial efficiency:   ε<sub>fid</sub> = N(fiducial events) / N(triggered events)      (colored: triggered events in which both quirk-hadrons are charged)"),
      EQ("Reconstruction efficiency:   ε<sub>reco</sub> = N(events in the signal region) / N(fiducial events)"),
      EQ("Total efficiency (paper, Eq. 12):   ε = ε<sub>trig</sub> × ε<sub>fid</sub> × ε<sub>reco</sub>"),
      EQ("Expected signal events:   N = L × σ × ε × f<sub>ch</sub> = L × σ × N(signal region) / N(matched),   L = 300 fb<super>−1</super>"),
      P("f<sub>ch</sub> = fraction of the triggered colored events in which both quirk-hadrons are charged (EW: f<sub>ch</sub> = 1). σ = cross section of the sample.", "m"),
      EQ("Expected converted-photon events:   N = L × σ<sub>γ</sub> × P<sub>conv</sub> × N(pass) / 9139,   P<sub>conv</sub> = 1%"),
      P("P<sub>conv</sub> = 1% is taken from the paper's own numbers (“~1 pb … drops to ~10 fb if we require that the photon converts in the beampipe”).", "m"),
      EQ("Plane fit (paper, Eqs. 9–10):   T<sub>ij</sub> = Σ<sub>a</sub> x<sub>i</sub><super>a</super> x<sub>j</sub><super>a</super> / (N − 1);   Δs² = smallest eigenvalue of T;   Δw² = second eigenvalue of T"),
      P("Δs measures the thickness of the plane through the hits; Δw measures the width of the strip in which the hits lie.", "m"),
      EQ("Signal region (paper, Sec. IV):   a plane is found;   7 layers with 2 hits and 1 layer with ≥ 1 hit;   Δw &lt; 1 cm;   Δs &lt; 0.01 cm"),
      EQ("Angular momentum of the pair (Fig. 2):   L = (x<sub>1</sub>* − x<sub>2</sub>*) × (p<sub>1</sub>* − p<sub>2</sub>*) / 2   in the pair's rest frame;   impact parameter b = |L| / p*"),
      EQ("Figure 6:   exclusion where N = 3,   discovery where N = 5   (no background, as in the paper)"),
      EQ("Statistical uncertainty:   σ<sub>ε</sub> = √( ε (1 − ε) / n );    if k = 0:  95% upper limit = 1 − 0.05<super>1/n</super>"),
      EQ("Decision:   <b>consistent</b> with the paper if |ε − ε<sub>paper</sub>| ≤ 2 σ<sub>0</sub>,   σ<sub>0</sub> = √( ε<sub>paper</sub> (1 − ε<sub>paper</sub>) / n )")]

# ================================================================ PART A
S += [PageBreak(), P("PART A — The paper's literal method", "part"),
      P("Everything in Part A uses only what the paper states: LO 0 + 1 jet MLM-matched samples, SCT z resolution 1.16 mm on signal and background, "
        "ε<sub>trig</sub> = matched count with p<sub>T</sub>(QQ̄) &gt; 200 GeV, no K-factor, no N<sub>Q</sub> factor. The paper's numbers are shown next to ours.", "b")]
S += [P("A1. Settings", "h2")]
g = [H("Setting", "Value used in Part A", "Source")]
g += [C("Signal samples", "MadGraph5_aMC@NLO 3.7.3 + Pythia 8, LO, pp → QQ̄ + 0 or 1 jet, MLM-matched; 2000 events per sample", "paper: “0 + 1 jet … matched using Pythia8”"),
      C("Cross section σ", f"LO matched σ of the sample: colored 1800 GeV {SIG['COL2000']:.4f} fb, EW 800 GeV {SIG['EW2000']:.4f} fb; no K-factor", "the paper gives no σ"),
      C("N<sub>Q</sub> factor", "none (σ × 1)", "“N<sub>Q</sub> = 2” appears only in the titles of the paper's Fig. 6 panels and is never defined"),
      C("Trigger", "p<sub>T</sub>(QQ̄) &gt; 200 GeV; ε<sub>trig</sub> = matched count", "paper, Sec. IV"),
      C("Fiducial", "both quirks cross all 8 layers (4 pixel + 4 SCT) within t &lt; 25 ns", "paper, Sec. IV"),
      C("Layer crossings", "first crossing of each layer", "paper: each quirk “will most likely intersect each layer only once”"),
      C("Signal region", "plane found; 7 × 2 hits + 1 × ≥ 1 hit; Δw &lt; 1 cm; Δs &lt; 0.01 cm", "paper, Sec. IV"),
      C("Luminosity", "300 fb<super>−1</super>", "paper, Fig. 6"),
      C("Annihilation", "not simulated", "the paper assumes none")]
S += [grid(g, [30, 86, 58])]
g = [H("Detector part", "Formula applied to the true crossing point", "Value")]
g += [C("Pixel layers (4)", "hit moved to the centre of its pixel:  x<sub>meas</sub> = p · round(x / p)", "p = 50 µm (rφ); 250 µm (IBL z), 400 µm (other z)"),
      C("SCT layers (4), rφ", "(rφ)<sub>meas</sub> = rφ + σ<sub>rφ</sub> · g,   g = Gaussian random number (mean 0, width 1)", "σ<sub>rφ</sub> = 34 µm (2 × 17 µm)"),
      C("SCT layers (4), z", "z<sub>meas</sub> = z + σ<sub>z</sub> · g", "<b>σ<sub>z</sub> = 1.16 mm</b> (2 × 580 µm)"),
      C("Beam spot", "all hits of an event shifted by the same z<sub>0</sub>,  z<sub>0</sub> = 45 mm · g", "45 mm"),
      C("Neighbouring pixels", "hits in adjacent pixels of one layer merged into one hit", "—")]
S += [Spacer(1, 3), grid(g, [32, 92, 50]),
      P("From the paper (Sec. III A) and its Ref. [27]. Pixel rounding gives an RMS error p/√12 (14 µm for 50 µm, 115 µm for 400 µm). One common z<sub>0</sub> per event is our reading "
        "of “a uniform, gaussian smearing … to the z-coordinates of all the hits”. The same smearing is applied to signal and background. σ<sub>z</sub> = 0 is tested in Part B.", "m")]

# A2 Table I
S += [P("A2. Table I (SCT z = 1.16 mm)", "h2")]
def tableA(s):
    C_ = CNT[s]; pv = R.SAM[s]["paper"]; n_trig = C_["charged"]; tk, tn = C_["trig"], C_["matched"]
    g = [H("Λ (keV)", "ε<sub>trig</sub> = N(p<sub>T</sub>(QQ̄) &gt; 200 GeV) / N(matched)", f"ε<sub>fid</sub> = N(fiducial) / N({'trig., both charged' if s == 'COL2000' else 'trig.'})",
           "ε<sub>reco</sub> = N(signal region) / N(fiducial), SCT z 1.16 mm", "paper ε<sub>reco</sub>", "decision")]; ex = []
    for i, lam in enumerate(LAMS[s], 1):
        r1 = lsr(s, lam, "Z1160"); k1, n1 = int(r1.k_ge2), int(r1.n_fid); p = float(r1.paper_reco); d1, b1 = cell(k1, n1, p)
        g.append(C(str(lam), f"{tk}/{tn} = {es(tk, tn)}", f"{n1}/{n_trig} = {es(n1, n_trig)}", f"<b>{k1}/{n1} = {es(k1, n1)}</b>", f"{p:.3g}", d1)); ex.append(("BACKGROUND", (5, i), (5, i), b1))
    dt, bt = cell(tk, tn, pv["trig"]); df, bf = cell(C_["fid"], n_trig, pv["fid"])
    g.append(C("paper", f"{pv['trig']:.2f}", f"{pv['fid']:.2f}", "see column", "", ""))
    g.append(C("dec.", dt, df, "", "", "")); j = len(g) - 1; ex += [("BACKGROUND", (1, j), (1, j), bt), ("BACKGROUND", (2, j), (2, j), bf)]
    return [P(f"<b>{NAME[s][0].upper() + NAME[s][1:]}</b> (2000 events generated, {tn} after matching)", "c"), grid(g, [13, 36, 36, 41, 16, 32], ex)]
S += tableA("COL2000") + [Spacer(1, 3)] + tableA("EW2000")
S += [P("ε<sub>fid</sub> is recomputed at every Λ. EW at 3 keV: 61 instead of 62 because one event (no. 127) could not be integrated at 3 keV; like every such failure it is counted as not "
        "fiducial. For k = 0 the one-sided 95% upper limit is given. Decision cells give |Δ| = |ε − ε<sub>paper</sub>| and 2σ₀.", "m"),
      key(f"<b>What we learn.</b> With the paper's method: colored ε<sub>reco</sub> is {verdict('COL2000', 'Z1160')}; EW ε<sub>reco</sub> is {verdict('EW2000', 'Z1160')}. "
          f"Where events pass, our values are {LOWER} times lower than the paper's. ε<sub>trig</sub> agrees for colored and is too high for EW ({e['trig']/e['matched']:.2f} vs 0.10); ε<sub>fid</sub> agrees for both.")]
PE = {"Z0": pd.read_csv(f"{T}/lambda_scan_per_event.csv"), "Z1160": pd.read_csv(f"{T}/lambda_scan_z1160_per_event.csv")}
def flow(s_, lam, sct):
    x = PE[sct]; x = x[(x["sample"] == s_) & (x.lambda_keV == lam) & (x["mode"] == "FIRST") & (x.sct == sct)]; f = x[x.fid.astype(str) == "True"]
    tr = lambda c_: f[c_].astype(str) == "True"
    o = dict(fid=len(f), plane=int(tr("plane").sum()), mult=int((tr("plane") & tr("mult")).sum()), sr=int(tr("final").sum()))
    r = lsr(s_, lam, sct); assert (o["fid"], o["sr"]) == (int(r.n_fid), int(r.k_ge2)), (s_, lam, sct, o); return o
def cutflow(s_, sct):
    C_ = CNT[s_]; pv = R.SAM[s_]["paper"]; ntr = C_["charged"]; et = C_["trig"] / C_["matched"]; lams = LAMS[s_]
    F_ = {l: flow(s_, l, sct) for l in lams}
    row = lambda lab, f: C(lab, *[f(F_[l]) for l in lams])
    g = [[P(f"Λ (keV) →  [{ZL[sct]}]", "ch")] + [P(f"<b>{l}</b>", "ch") for l in lams],
         row("fiducial (both quirks cross all 8 layers, t &lt; 25 ns)", lambda o: str(o["fid"])),
         row("plane found (Δw &lt; 1 cm)", lambda o: str(o["plane"])),
         row("+ hit multiplicity (2 hits in 7 layers, ≥ 1 in 8th)", lambda o: str(o["mult"])),
         row("<b>+ Δs &lt; 0.01 cm = signal region (pass)</b>", lambda o: f"<b>{o['sr']}</b>"),
         row("fail (fiducial − pass)", lambda o: str(o["fid"] - o["sr"])),
         row("ε<sub>reco</sub> = pass / fiducial", lambda o: f"{o['sr']/o['fid']:.2f}"),
         row("<b>ε = ε<sub>trig</sub> × ε<sub>fid</sub> × ε<sub>reco</sub></b>, ×10⁻²", lambda o: f"<b>{100*et*o['fid']/ntr*o['sr']/o['fid']:.2f}</b>"),
         C("paper ε ×10⁻² (product of its Table I entries)", *[f"{100*pv['trig']*pv['fid']*PAPER_R[s_][l]:.2f}" for l in lams])]
    ex = [("ALIGN", (1, 0), (-1, -1), "CENTER"), ("BACKGROUND", (0, 4), (-1, 4), KEYB), ("BACKGROUND", (0, 7), (-1, 7), KEYB)]
    return [P(f"<b>{NAME[s_][0].upper() + NAME[s_][1:]}</b>: matched {C_['matched']} → triggered {C_['trig']}" + (f" → both charged {ntr}" if s_ == "COL2000" else "") + " (same for every Λ).", "c"),
            grid(g, [74] + [20] * len(lams), ex)]
S += [P("Event counts at every Λ (cut-flow, first crossing)", "h3")] + cutflow("COL2000", "Z1160") + [Spacer(1, 3)] + cutflow("EW2000", "Z1160")

#<<FIG2>>
#<<FIG3>>
S += [P("A5. Figure 4: hits of one signal event", "h2")]
g = [H("Fig. 4 example event", "Δs (plane thickness)", "Δw (strip width)", "match with the paper")]
g.append(C("Paper (colored)", "83 µm", "0.074 cm", "—"))
dd = f4["Z1160"][f4["Z1160"].ellipse != True].groupby("sample").first()
for s_ in ("COL2000", "EW2000"):
    r_ = dd.loc[s_]
    g.append(C(f"This work, {'colored' if s_ == 'COL2000' else 'EW'}, SCT z 1.16 mm", f"{r_.ds_cm*1e4:.0f} µm", f"{r_.dw_cm:.3f} cm",
               ("Δs yes (both below the 100 µm cut)" if r_.ds_cm < 0.01 else "Δs no") + f"; Δw {'no (wider)' if r_.dw_cm > 0.15 else 'close'}"))
S += [grid(g, [56, 30, 30, 58]), P("Each example is the signal event with the median Δs among the events in the signal region. All hits lie on a thin strip, as in the paper.", "m"),
      Spacer(1, 2), img("F29_fig4_Z1160", 120)]
def fig5rows(sct):
    g = [H("Fig. 5", "Δs median: ours / paper", "Δw median: ours / paper", "fraction with Δs &lt; 0.01 cm: ours / paper", "decision")]; ex = []; i = 0
    for pop, lab in (("colored", "Colored Quirk"), ("EW", "EW Quirk"), ("converted γ + pile-up", "Converted gamma"), ("pile-up", "Pileup")):
        x = F5[sct][F5[sct].population == pop]
        if not len(x): continue
        k, n = int((x.ds < 0.01).sum()), len(x); dd_, bb = cell(k, n, PBELOW[lab]); i += 1
        g.append(C(pop + (" signal" if pop in ("colored", "EW") else ""), f"{x.ds.median()*1e4:.0f} / {PM[lab][0]*1e4:.0f} µm", f"{x.dw.median():.3f} / {PM[lab][1]:.3f} cm",
                   f"{k}/{n} = {es(k, n)} / {PBELOW[lab]:.2f}", dd_)); ex.append(("BACKGROUND", (4, i), (4, i), bb))
    return grid(g, [34, 34, 34, 46, 26], ex)
fr = lambda pop, sct: f"{(F5[sct][F5[sct].population == pop].ds < 0.01).mean():.2f}"
S += [P("A6. Figure 5: Δs and Δw distributions (SCT z 1.16 mm on signal and background)", "h2"), fig5rows("Z1160"), Spacer(1, 2), img("F40_fig5_Z1160", 118),
      key(f"<b>What we learn.</b> With 1.16 mm no converted photon passes the Δs cut, as in the paper (paper {PBELOW['Converted gamma']:.2f}), but most of the signal fails it too: "
          f"only {fr('colored', 'Z1160')} (colored) and {fr('EW', 'Z1160')} (EW) of the signal planes have Δs &lt; 0.01 cm, against about 0.9 in the paper. "
          f"Our median Δw is {F5['Z1160'][F5['Z1160'].population == 'colored'].dw.median() / PM['Colored Quirk'][1]:.0f}× (colored) and {F5['Z1160'][F5['Z1160'].population == 'EW'].dw.median() / PM['EW Quirk'][1]:.0f}× (EW) the paper's.")]

# A7 backgrounds
ul = R.ul95(9139); ex_ = lambda xs: 300 * xs * 1e3 * 0.01
cv1, cv0, pu1 = BG["conv1160"], BG["conv0"], BG["pu1160"]
S += [P("A7. Backgrounds (SCT z 1.16 mm)", "h2")]
g = [H("Background sample", "events", "plane found (Δw &lt; 1 cm)", "+ hit multiplicity", "<b>pass</b> (signal region)", "fail", "paper")]
g += [C("converted γ + pile-up (μ = 50)", "9139", str(cv1["plane"]), str(cv1["mult"]), f"<b>{cv1['sr']}</b>", str(9139 - cv1["sr"]), "“a few” events at 300 fb⁻¹, “can easily be removed”"),
      C("pile-up only (μ = 50)", "5000", f"{pu1['r4']} (≥ 4 of 8 layers); {pu1['r8']} (all 8)", "—", f"<b>{pu1['sr']}</b>", str(5000 - pu1["sr"]), "none in the signal region")]
g2 = [H("Pile-up planes (5000 events)", "ours: k / n", "rate", "paper (approx.)", "decision")]; ex2 = []
for i_, (lab, k, pp_) in enumerate((("selected plane, ≥ 1 hit in ≥ 4 of 8 layers", pu1["r4"], 1e-3), ("selected plane, ≥ 1 hit in all 8 layers", pu1["r8"], 6e-5)), 1):
    d_, b_ = cell(k, 5000, pp_); g2.append(C(lab, f"{k} / 5000", sci(k / 5000), f"~{sci(pp_, 0)}", d_)); ex2.append(("BACKGROUND", (4, i_), (4, i_), b_))
S += [grid(g, [44, 14, 30, 20, 20, 14, 32], [("BACKGROUND", (4, 1), (4, 2), OKB)]), Spacer(1, 3), grid(g2, [62, 26, 24, 30, 32], ex2),
      P("Converted photons from Z(→νν) + γ (MadGraph, MET &gt; 200 GeV), converted in the beam pipe, with pile-up μ = 50 overlaid.", "m"),
      P("Converted photons: why the upper limit is the same for both cross sections (Q1)", "h3")]
g = [H("Converted γ + pile-up (9139 events)", "in signal region", "per conversion", "expected events at 300 fb⁻¹: our σ (0.211 pb) / paper σ (~1 pb)")]
g.append(C("SCT z 1.16 mm", f"{cv1['sr']} / 9139", f"&lt; {sci(ul)} (95% UL)", f"&lt; {ex_(0.211)*ul:.2f} / &lt; {ex_(1.0)*ul:.2f}"))
S += [grid(g, [46, 26, 36, 66]),
      key(f"<b>Answer.</b> The limit is a property of our 9139 simulated conversions: 0 pass, so the 95% upper limit per conversion is 1 − 0.05<super>1/9139</super> = {sci(ul)}, whatever the cross section. "
          f"The cross section only sets how many conversions are expected (300 fb⁻¹ × σ × 1% = {ex_(0.211):.0f} or {ex_(1.0):.0f}), which is why the last column differs.")]

# A8 Figure 6 (paper's method only)
S += [PageBreak(), P("A8. Figure 6: discovery and exclusion contours (paper's method)", "h2")]
S += B(["<b>Paper:</b> contours of 3 (exclusion) and 5 (discovery) signal events at 300 fb<super>−1</super>, “assuming negligible irreducible backgrounds”; N = L σ ε<sub>trig</sub> ε<sub>fid</sub> ε<sub>reco</sub>.",
        "<b>This work:</b> 13 samples (MG5 3.7.3 + Pythia8, MLM-matched, 2000 events per mass: colored 600–2400 GeV, EW 100–1000 GeV) through the Table I pipeline at Λ = 0.1–25 keV, "
        "signal SCT z 1.16 mm. σ = LO matched σ of each sample; ε<sub>trig</sub> = matched count; colored includes the both-charged factor f<sub>ch</sub>; no K-factor; no N<sub>Q</sub> factor.",
        ETRIG_TXT,
        "<b>Not computed:</b> Λ &gt; 25 keV (the integrator's 20-million-step ceiling removes 5–56% of the fiducial events at 30–35 keV), Λ &lt; 100 eV, colored &lt; 600 GeV, EW &lt; 100 GeV; "
        "low-Λ edges at light masses are not resolved (0 events passed, red ✕)."])
S += [img("F6_fig6_partA", 172)]
g = [H("Largest mass reached (GeV), ±1σ", "colored exclusion", "colored discovery", "EW exclusion", "EW discovery")]
g.append(C("<b>paper, Fig. 6</b>", "1793", "1707", "762", "688")); g.append(C("<b>paper, abstract</b>", "–", "1600", "–", "650"))
g.append(C("<b>this work, paper's method (SCT z 1.16 mm)</b>", *[rr("Z1160", "charge factor included", ch, c_) for ch, c_ in (("colored", "exclusion"), ("colored", "discovery"), ("EW", "exclusion"), ("EW", "discovery"))]))
g.append(C("difference from the paper's figure", *[f"{_d(ch, c_, 'Z1160'):+.0f}%" for ch, c_ in (("colored", "exclusion"), ("colored", "discovery"), ("EW", "exclusion"), ("EW", "discovery"))]))
S += [Spacer(1, 3), grid(g, [62, 28, 28, 28, 28], [("BACKGROUND", (0, 1), (-1, 2), KEYB)]),
      key(f"<b>What we learn.</b> With the paper's method our contours have the paper's shape (lower edge near 1 keV, largest mass at Λ ≈ 4–7 keV), but they reach less far: "
          f"colored {_d('colored', 'exclusion', 'Z1160'):+.0f}% / {_d('colored', 'discovery', 'Z1160'):+.0f}%, EW {_d('EW', 'exclusion', 'Z1160'):+.0f}% / {_d('EW', 'discovery', 'Z1160'):+.0f}% "
          "(exclusion / discovery). The reason is the low ε<sub>reco</sub> with SCT z 1.16 mm (Section A2).")]
#<<FIG7>>
#<<REPEAT>>
S += [key(f"<b>What Part A shows.</b> With only the paper's stated settings we reproduce the trigger efficiency for colored quirks, the fiducial efficiencies, the flat planes "
          "(Figs. 3 and 4), and a background-free signal region."
          f" We do not reproduce the reconstruction efficiency ({LOWER} times lower), the EW trigger efficiency "
          f"({e['trig']/e['matched']:.2f} vs 0.10), Figure 2 after the first meeting and Figure 7. Because ε<sub>reco</sub> is low, the Figure 6 reach is also lower than the paper's.")]

# ================================================================ PART B
S += [PageBreak(), P("PART B — Deviations we tested (our additional study)", "part"),
      P("Each deviation changes Part A in one respect. They are not part of the paper's method; they show which change would bring our numbers closer to the paper's.", "b")]
g = [H("Deviation", "Why we tested it (one line)", "Section")]
g += [C("<b>No SCT z smearing</b> (σ<sub>z</sub> = 0, signal and background)", "With the paper's 1.16 mm our ε<sub>reco</sub> is far below Table I; we checked whether a better z resolution reproduces the paper.", "B1"),
      C("<b>LO-ratio trigger</b>", "Our EW ε<sub>trig</sub> (0.18) is far above the paper's 0.10; arXiv:1911.02223 computes the trigger as an LO cross-section ratio, so we tried that.", "B2"),
      C("<b>σ scaling (K-factor)</b>", "The paper gives no cross sections; scaling σ shows how much the Fig. 6 reach depends on the normalisation.", "B3"),
      C("<b>N<sub>Q</sub> = 2</b>", "The paper's Fig. 6 titles say “N<sub>Q</sub> = 2 Quirks” without a definition; we tried reading it as a factor 2 on σ.", "B4"),
      C("<b>Colored without f<sub>ch</sub></b>", "The paper quotes ~30% for both quirk-hadrons charged but does not say whether this factor enters Fig. 6.", "B5"),
      C("<b>Annihilation</b>", "Our |L| returns to zero at every second meeting, so the quirks might annihilate; we estimated a worst case.", "B6")]
S += [grid(g, [48, 112, 14])]

# B1 no SCT z smearing
S += [P("B1. No SCT z smearing on signal and background", "h2"),
      P("Everything as in Part A, but σ<sub>z</sub> = 0 in the SCT for the signal and for the backgrounds. This is our additional study.", "b")]
def tableB1(s):
    g = [H("Λ (keV)", "ε<sub>reco</sub>, no SCT z smearing", "paper ε<sub>reco</sub>", "decision", "ε<sub>reco</sub>, SCT z 1.16 mm (Part A)")]; ex = []
    for i, lam in enumerate(LAMS[s], 1):
        r0, r1 = lsr(s, lam, "Z0"), lsr(s, lam, "Z1160"); k0, n0, k1, n1 = int(r0.k_ge2), int(r0.n_fid), int(r1.k_ge2), int(r1.n_fid); p = float(r0.paper_reco)
        d0, b0 = cell(k0, n0, p); g.append(C(str(lam), f"<b>{k0}/{n0} = {es(k0, n0)}</b>", f"{p:.3g}", d0, f"{k1}/{n1} = {es(k1, n1)}")); ex.append(("BACKGROUND", (3, i), (3, i), b0))
    return [P(f"<b>{NAME[s][0].upper() + NAME[s][1:]}</b>", "c"), grid(g, [16, 48, 22, 40, 48], ex)]
S += tableB1("COL2000") + [Spacer(1, 3)] + tableB1("EW2000")
S += [key(f"<b>What we learn.</b> Without SCT z smearing: colored ε<sub>reco</sub> is {verdict('COL2000', 'Z0')}; EW ε<sub>reco</sub> is {verdict('EW2000', 'Z0')} "
          "(at 1 and 2 keV ours is higher than the paper's). So the paper's Table I is reproduced only if the SCT z position is measured much better than 1.16 mm.")]
S += [P("Cut-flow without SCT z smearing", "h3")] + cutflow("COL2000", "Z0") + [Spacer(1, 3)] + cutflow("EW2000", "Z0")
S += [Spacer(1, 3), img("F38_lambda", 150),
      P("ε<sub>reco</sub> vs Λ: the paper, our production samples with SCT z none and 1.16 mm, and the EW leading-order sample (Section B2), all with simple binomial σ.", "m")]
S += [P("Figures 4 and 5 without SCT z smearing", "h3")]
g = [H("Fig. 4 example event", "Δs (plane thickness)", "Δw (strip width)", "match with the paper")]
g.append(C("Paper (colored)", "83 µm", "0.074 cm", "—"))
dd = f4["Z0"][f4["Z0"].ellipse != True].groupby("sample").first()
for s_ in ("COL2000", "EW2000"):
    r_ = dd.loc[s_]
    g.append(C(f"This work, {'colored' if s_ == 'COL2000' else 'EW'}, no SCT z smearing", f"{r_.ds_cm*1e4:.0f} µm", f"{r_.dw_cm:.3f} cm",
               ("Δs yes (both below the 100 µm cut)" if r_.ds_cm < 0.01 else "Δs no") + f"; Δw {'no (wider)' if r_.dw_cm > 0.15 else 'close'}"))
S += [grid(g, [56, 30, 30, 58]), Spacer(1, 2), img("F29_fig4_Z0", 112), Spacer(1, 3), fig5rows("Z0"), Spacer(1, 2), img("F40_fig5_Z0", 112),
      P("Pile-up only was not simulated without SCT z smearing.", "m")]
g = [H("Background (9139 converted γ + pile-up)", "pass", "fraction", "expected events at 300 fb⁻¹: our σ (0.211 pb) / paper σ (~1 pb)")]
g.append(C("no SCT z smearing", f"{cv0['sr']} / 9139", es(cv0["sr"], 9139, 4), f"{ex_(0.211)*cv0['sr']/9139:.0f} / {ex_(1.0)*cv0['sr']/9139:.0f}"))
g.append(C("SCT z 1.16 mm (Part A)", f"{cv1['sr']} / 9139", f"&lt; {sci(ul)} (95% UL)", f"&lt; {ex_(0.211)*ul:.2f} / &lt; {ex_(1.0)*ul:.2f}"))
S += [Spacer(1, 3), grid(g, [56, 22, 34, 62], [("BACKGROUND", (1, 1), (1, 1), BADB), ("BACKGROUND", (1, 2), (1, 2), OKB)]),
      key(f"<b>What we learn.</b> Without smearing the signal Δs (≈ 40 µm) is close to the paper's (≈ 30 µm) and all signal passes the Δs cut (paper ≈ 90%), "
          f"but {fr('converted γ + pile-up', 'Z0')} of the converted-photon planes also pass (paper {PBELOW['Converted gamma']:.2f}), i.e. {cv0['sr']} of 9139, about 10 (our σ) to 48 (paper's σ) "
          "events at 300 fb⁻¹. With 1.16 mm no converted photon passes, but most signal fails too. <b>No single SCT z setting reproduces both the paper's signal and its background.</b>")]
S += [P("Figure 6 without SCT z smearing", "h3"), img("F6_fig6_partB_noSCT", 168)]
g = [H("Largest mass reached (GeV), ±1σ", "colored exclusion", "colored discovery", "EW exclusion", "EW discovery")]
g.append(C("<b>paper, Fig. 6</b>", "1793", "1707", "762", "688"))
g.append(C("this work, no SCT z smearing", *[rr("Z0", "charge factor included", ch, c_) for ch, c_ in (("colored", "exclusion"), ("colored", "discovery"), ("EW", "exclusion"), ("EW", "discovery"))]))
g.append(C("difference from the paper's figure", *[f"{_d(ch, c_, 'Z0'):+.0f}%" for ch, c_ in (("colored", "exclusion"), ("colored", "discovery"), ("EW", "exclusion"), ("EW", "discovery"))]))
g.append(C("this work, SCT z 1.16 mm (Part A)", *[rr("Z1160", "charge factor included", ch, c_) for ch, c_ in (("colored", "exclusion"), ("colored", "discovery"), ("EW", "exclusion"), ("EW", "discovery"))]))
S += [grid(g, [62, 28, 28, 28, 28], [("BACKGROUND", (0, 1), (-1, 1), KEYB)]),
      P("Without SCT z smearing the converted-photon background is not zero (above), so these contours, drawn without background as in the paper, are optimistic.", "m")]

# B2 LO-ratio trigger
#<<LO>>
g = [H("Figure 6 with the LO-ratio trigger (GeV)", "SCT z 1.16 mm: EW excl. / disc.", "no SCT z smearing: EW excl. / disc.")]
g += [C("EW ε<sub>trig</sub> = matched count (Part A)", rs("EW", "K1", "Z1160"), rs("EW", "K1", "Z0")),
      C(f"EW ε<sub>trig</sub> = LO ratio ({LOR[800]:.3f} at 800 GeV)", rs("EW", "EW LO-ratio trigger", "Z1160"), rs("EW", "EW LO-ratio trigger", "Z0")),
      C("LO-ratio trigger and ε<sub>fid</sub>, ε<sub>reco</sub> from the LO sample at 800 GeV", rs("EW", "EW fully LO", "Z1160"), rs("EW", "EW fully LO", "Z0")),
      C("paper, Fig. 6", "762 / 688", "762 / 688")]
S += [Spacer(1, 3), grid(g, [90, 42, 42]),
      P(f"The LO ratio lowers EW ε<sub>trig</sub> by a factor {min(LOR[m] * EWT[m][1] / EWT[m][0] for m in EWT):.2f}–{max(LOR[m] * EWT[m][1] / EWT[m][0] for m in EWT):.2f} (100–1000 GeV). "
        "The paper does not state this method.", "m")]

# B3-B6 normalisation deviations
def sens(rows):
    g = [H("Variant", "SCT z 1.16 mm: colored excl. / disc.", "SCT z 1.16 mm: EW excl. / disc.", "no smearing: colored excl. / disc.", "no smearing: EW excl. / disc.")]
    for var, lab in rows: g.append(C(lab, rs("colored", var, "Z1160"), rs("EW", var, "Z1160"), rs("colored", var, "Z0"), rs("EW", var, "Z0")))
    g.append(C("paper, Fig. 6", "1793 / 1707", "762 / 688", "1793 / 1707", "762 / 688")); return grid(g, [54, 30, 30, 30, 30], [("BACKGROUND", (0, 1), (-1, 1), KEYB)])
S += [P("B3. σ scaling (K-factor)", "h2"),
      P("All cross sections multiplied by K (largest mass reached in GeV; not a fit). K = 1 is Part A (left) and B1 (right).", "b"),
      sens([("K1", "σ × 1 (our LO)"), ("K0.8", "σ × 0.8"), ("K0.9", "σ × 0.9"), ("K1.2", "σ × 1.2"), ("K1.4", "σ × 1.4"), ("K1.5", "σ × 1.5"), ("K1.8", "σ × 1.8"), ("K2", "σ × 2")]),
      Spacer(1, 2), img("F6_kfactor", 150),
      P("Figure: no SCT z smearing, σ × K. Dotted grey (EW): LO-ratio trigger (B2).", "m"),
      key("<b>What we learn.</b> Without SCT z smearing, EW matches the paper's figure with K ≈ 0.85–0.9, while colored needs K ≈ 1.5–1.7, so one common NLO K-factor cannot explain "
          "both. With SCT z 1.16 mm even σ × 2 stays below the paper. The paper gives no σ, so the origin cannot be identified.")]
S += [P("B4. N<sub>Q</sub> = 2 read as a factor 2 on σ", "h2"),
      P("“N<sub>Q</sub> = 2” appears only in the titles of the paper's Fig. 6 panels (arXiv v1 and v2) and is never defined or used in the text. It could mean two quirk species "
        "(a factor 2 on σ) or only the two quirks of each pair (no factor). The row σ × 2 of the table above is this reading.", "b")]
S += [P("B5. Colored without the both-charged factor f<sub>ch</sub>", "h2")]
g = [H("Colored, largest mass reached (GeV), ±1σ", "SCT z 1.16 mm: excl.", "SCT z 1.16 mm: disc.", "no smearing: excl.", "no smearing: disc.")]
g += [C("with f<sub>ch</sub> (Part A, B1)", rr("Z1160", "charge factor included", "colored", "exclusion"), rr("Z1160", "charge factor included", "colored", "discovery"),
        rr("Z0", "charge factor included", "colored", "exclusion"), rr("Z0", "charge factor included", "colored", "discovery")),
      C("without f<sub>ch</sub>", rr("Z1160", "without charge factor", "colored", "exclusion"), rr("Z1160", "without charge factor", "colored", "discovery"),
        rr("Z0", "without charge factor", "colored", "exclusion"), rr("Z0", "without charge factor", "colored", "discovery")),
      C("paper, Fig. 6", "1793", "1707", "1793", "1707")]
S += [grid(g, [54, 30, 30, 30, 30]),
      P(f"f<sub>ch</sub> = {c['charged']}/{c['trig']} = {c['charged']/c['trig']:.2f} at 1800 GeV (paper, Sec. II: ~30%). The paper's ε<sub>fid</sub> for colored quirks is defined "
        "for triggered events with both quirk-hadrons charged, so f<sub>ch</sub> is needed to turn its ε into a number of events; the paper does not say whether its Fig. 6 includes it.", "m")]
#<<ANNI>>
S += [sens([("annihilation worst", "annihilation, worst case (α = 0.05, chance at every second meeting)")]),
      P("Effect on Figure 6 of the worst case above (largest mass reached in GeV).", "m")]

# ================================================================ Table II
S += [PageBreak(), P("Table II. Expected events at 300 fb⁻¹", "h2"),
      P("N = L × σ × N(pass) / N(sample), L = 300 fb<super>−1</super>. Two detector settings, each applied to signal <b>and</b> background: SCT z 1.16 mm (the paper's method, Part A) "
        "and no SCT z smearing (Part B1). For k = 0 the 95% upper limit is given. The uncertainty is statistical (binomial on N(pass) / N(sample)); the MadGraph σ error (≈ 2–3%) is not included.", "b")]
def nev(k, n, L_sig):
    if k == 0: return f"&lt; {L_sig * R.ul95(n):.2f}"
    p = k / n; return f"{L_sig * p:.2f} ± {L_sig * np.sqrt(p * (1 - p) / n):.2f}"
g = [H("Process", "Λ (keV)", "σ (fb)", "SCT z 1.16 mm: pass / sample", "SCT z 1.16 mm: N", "no SCT z smearing: pass / sample", "no SCT z smearing: N", "N with the paper's ε (our σ)")]
ex = []; tab2 = []
for s_ in ("COL2000", "EW2000"):
    C_ = CNT[s_]; nm = C_["matched"]; Ls = LUMI * SIG[s_]; fch = C_["charged"] / C_["trig"]; pv = R.SAM[s_]["paper"]
    for j, lam in enumerate(LAMS[s_]):
        k1, k0 = int(lsr(s_, lam, "Z1160").k_ge2), int(lsr(s_, lam, "Z0").k_ge2); npap = Ls * fch * pv["trig"] * pv["fid"] * PAPER_R[s_][lam]
        g.append(C(f"<b>{NAME[s_]}</b>" if j == 0 else "", str(lam), f"{SIG[s_]:.4f}" if j == 0 else "", f"{k1} / {nm}", f"<b>{nev(k1, nm, Ls)}</b>", f"{k0} / {nm}", f"<b>{nev(k0, nm, Ls)}</b>", f"{npap:.2f}"))
        tab2.append(dict(process=NAME[s_], lambda_keV=lam, sigma_fb=SIG[s_], pass_Z1160=k1, sample=nm, N_Z1160=Ls * k1 / nm, N_Z1160_UL95=Ls * R.ul95(nm) if k1 == 0 else np.nan,
                         pass_Z0=k0, N_Z0=Ls * k0 / nm, N_paper_eps=npap))
for lab, sg in (("converted γ + pile-up, our σ", 211.2), ("converted γ + pile-up, paper's σ", 1000.0)):
    Lg = LUMI * sg * 0.01
    g.append(C(f"<b>{lab}</b>", "–", f"{sg:.0f} × 1% conv.", f"{cv1['sr']} / 9139", f"<b>{nev(cv1['sr'], 9139, Lg)}</b>", f"{cv0['sr']} / 9139", f"<b>{nev(cv0['sr'], 9139, Lg)}</b>", "“a few”, removable"))
    tab2.append(dict(process=lab, lambda_keV=np.nan, sigma_fb=sg, pass_Z1160=cv1["sr"], sample=9139, N_Z1160=0.0, N_Z1160_UL95=Lg * R.ul95(9139), pass_Z0=cv0["sr"], N_Z0=Lg * cv0["sr"] / 9139, N_paper_eps=np.nan))
g.append(C("<b>pile-up only (μ = 50)</b>", "–", "not given", f"{pu1['sr']} / 5000", f"&lt; {sci(R.ul95(5000))} per event", "not simulated", "–", "none"))
tab2.append(dict(process="pile-up only", lambda_keV=np.nan, sigma_fb=np.nan, pass_Z1160=pu1["sr"], sample=5000, N_Z1160=np.nan, N_Z1160_UL95=np.nan, pass_Z0=np.nan, N_Z0=np.nan, N_paper_eps=np.nan))
nsig = len(LAMS["COL2000"]) + len(LAMS["EW2000"])
ex = [("BACKGROUND", (4, 1), (4, nsig), KEYB), ("BACKGROUND", (6, 1), (6, nsig), KEYB), ("LINEABOVE", (0, 1 + len(LAMS["COL2000"])), (-1, 1 + len(LAMS["COL2000"])), 0.8, ACC),
      ("LINEABOVE", (0, 1 + nsig), (-1, 1 + nsig), 0.8, ACC), ("BACKGROUND", (4, nsig + 1), (4, nsig + 3), OKB), ("BACKGROUND", (6, nsig + 1), (6, nsig + 2), BADB)]
S += [grid(g, [30, 12, 20, 22, 24, 22, 24, 20], ex),
      P("Signal: N(sample) = matched events; N(pass) = events in the signal region (for colored these are among the triggered events with both quirk-hadrons charged, so f<sub>ch</sub> is included). "
        f"Last column: the paper's ε = ε<sub>trig</sub> ε<sub>fid</sub> ε<sub>reco</sub> (Table I) × our σ × our f<sub>ch</sub> (colored {CNT['COL2000']['charged']/CNT['COL2000']['trig']:.2f}; EW 1). "
        "Converted photons: σ after MET &gt; 200 GeV (ours 0.211 pb, paper ~1 pb) × 1% conversion probability. Pile-up only: the paper gives no number of triggered events that the pile-up "
        "sits on, so only the probability per event is given.", "m"),
      key("<b>What Table II shows.</b> With SCT z 1.16 mm on both, the background is zero (upper limit &lt; 0.2–1 event), but the signal is also small: at most "
          f"{max(LUMI * SIG[s_] * int(lsr(s_, l, 'Z1160').k_ge2) / CNT[s_]['matched'] for s_ in LAMS for l in LAMS[s_]):.1f} events at these benchmarks. "
          f"Without SCT z smearing on both, the signal is {GAIN} times larger, but the converted-photon background (10 or 48 events) is then larger than the signal. "
          "At these benchmark masses (1800 and 800 GeV) the signal is below or near the 3-event exclusion level in both settings, consistent with Figure 6, where these masses lie at or beyond the reach (Figure 6 uses its own samples, e.g. EW 800 GeV ε<sub>trig</sub> = 0.148 instead of 0.178).")]
pd.DataFrame(tab2).to_csv(f"{R.L_}/tables/table_II_expected_events.csv", index=False)

# ================================================================ cuts, open points, conclusion, remarks
S += [P("Why the paper uses Δs &lt; 0.01 cm and Δw &lt; 1 cm", "h2")]
S += B(["<b>What they measure.</b> Δs is the thickness of the plane through the hits (smallest eigenvalue of T); Δw is the width of the strip in which the hits lie (second eigenvalue). "
        "The two quirks move in one plane, so their hits form a thin, narrow strip; random hits do not.",
        "<b>Δw &lt; 1 cm: reason given.</b> Sec. IV: “We deliberately do not impose a tight cut on Δw, as the efficiency for such a cut is strongly signal dependent. The rather loose cut of "
        "Δw &lt; 1.0 cm is intended to retain decent efficiencies for quirks with larger oscillation amplitude (low Λ).” The same 1 cm is used in the seeding and in the event selection "
        "(Sec. III C), and the paper attributes the low-Λ drop of ε<sub>reco</sub> “largely” to “a stringent Δw requirement”.",
        "<b>Δs &lt; 0.01 cm: no derivation given.</b> It appears only as “A signal selection cut Δs &lt; 0.01 cm is indicated on the left figure” (Fig. 5), i.e. it is read off Fig. 5, "
        "between the signal (≈ 30 µm) and the backgrounds (hundreds of µm). The scale is the expected one: the tracker resolution is “roughly ∼ 100 µm” (Sec. I). Looser windows are used "
        "earlier: seeding Δs &lt; 0.05 cm and |x·n<sub>1</sub>| &lt; 0.05 cm, growth factor 3 (Sec. III C).",
        "<b>General statement</b> (Sec. III C): “A tighter selection will generally boost computational efficiency at a cost of reduced signal efficiency, which is what has been chosen in this work.”",
        "<b>Our numbers:</b> signal Δs median 110–160 µm with SCT z 1.16 mm (Part A) and 38–44 µm without smearing (Part B); backgrounds 100–600 µm. The value of the cut is not the issue; "
        "the SCT z resolution decides whether the signal passes it."])
S += [P("Open points (what is still unclear)", "h2")] + B([
    "<b>SCT z resolution.</b> With the stated 1.16 mm our ε<sub>reco</sub> is far below Table I; only no SCT z smearing reproduces it, and then the converted-photon background is not zero.",
    f"<b>EW trigger efficiency.</b> Our matched count gives {e['trig']/e['matched']:.2f} (Fig. 6 sample: {ETR['k2']/ETR['n2']:.2f}); the paper's 0.10 is reproduced only by an LO cross-section ratio, which the paper does not mention.",
    "<b>Cross sections.</b> The paper gives no signal σ and no K-factor; “N<sub>Q</sub> = 2” is not defined.",
    "<b>Converted-photon normalisation.</b> Our σ after MET &gt; 200 GeV is 0.211 pb, the paper's ~1 pb (factor 4.7, not explained); the 1% conversion probability is derived from the paper's own numbers.",
    "<b>Pile-up.</b> No absolute normalisation is given in the paper; our rate of planes with hits in ≥ 4 of 8 layers is about 6× the paper's.",
    "<b>Δw.</b> Our signal Δw is 2–5 times the paper's.",
    "<b>Figure 2.</b> The paper's later |L| values cannot be obtained from its stated equation; the charges, momenta and L definition of its event are not given.",
    "<b>Figure 7.</b> Our hits are faster (median βγ about 2×); the paper's dE/dx panel is not reproduced from its own βγ panel by four standard definitions; thickness and selection are not stated.",
    "<b>Repeated layer crossings.</b> About half of our fiducial events cross some layer more than once; the paper assumes once. We use the first crossing.",
    "<b>Figure 6 coverage.</b> Λ &gt; 25 keV not computed (integrator step ceiling); low-Λ edges at light masses not resolved (larger samples needed).",
    "<b>Colored f<sub>ch</sub>.</b> Not stated whether the paper's Fig. 6 includes the both-charged factor."])
S += [P("Conclusion", "h2")] + B([
    "<b>Paper's method (Part A).</b> The trigger efficiency (colored), the fiducial efficiencies, the flat quirk planes and the background-free signal region are reproduced. "
    f"The reconstruction efficiency is {LOWER} times lower than Table I, and the Figure 6 reach is lower: colored {_m('colored', 'exclusion', 'Z1160')} / {_m('colored', 'discovery', 'Z1160')} GeV "
    f"(paper 1793 / 1707), EW {_m('EW', 'exclusion', 'Z1160')} / {_m('EW', 'discovery', 'Z1160')} GeV (paper 762 / 688).",
    f"<b>Our additional study (Part B).</b> Without SCT z smearing the signal numbers come close to the paper (Table I mostly consistent; reach colored {_m('colored', 'exclusion', 'Z0')} / "
    f"{_m('colored', 'discovery', 'Z0')} GeV, EW {_m('EW', 'exclusion', 'Z0')} / {_m('EW', 'discovery', 'Z0')} GeV), but the converted-photon background becomes 10–48 events at 300 fb⁻¹. "
    "No single setting reproduces both the paper's signal efficiency and its zero background.",
    "<b>EW trigger.</b> The paper's 0.10 matches an LO cross-section ratio, not the matched + shower count of the method it describes.",
    "<b>Figure 2.</b> With the paper's own equation, |L| returns to zero at every second meeting (also shown analytically in arXiv:2002.07503); the paper's curve does not. "
    f"L ≈ 0 does not by itself mean annihilation; a worst-case estimate lowers the reach by only {ANN} GeV (Section B6).",
    "<b>Expected events (Table II).</b> At the two benchmark masses the expected signal is a few events or less in both settings."])
S += [P("Final remarks on the paper", "h2")] + B([
    "The idea of the paper is clear and works in our simulation: quirk pairs leave hits on a thin plane (Δs of tens of µm before SCT z smearing), random hits rarely do, and the contours of Figure 6 have the paper's shape.",
    "The method is described in enough detail to implement the plane fit (Eqs. 9–10), the seeding and growing of planes, and the signal-region cuts; we implemented them as written.",
    "The numbers cannot be reproduced from the stated settings alone. Several inputs that decide them are missing: the SCT z resolution actually used, the signal cross sections and K-factors, "
    "the meaning of N<sub>Q</sub> = 2, how the trigger efficiency was obtained, the normalisation of the backgrounds, the event behind Figure 2, and the dE/dx definition of Figure 7.",
    "The paper's main conclusion, a nearly background-free search with ε<sub>reco</sub> up to ~70%, holds in our simulation only for a z resolution much better than the stated 1.16 mm, "
    "and in that case the converted-photon background is not negligible without further cuts (the paper suggests a Δφ(MET, n<sub>3</sub>) or dE/dx requirement, which it does not apply)."])
S += [P("References", "h2")] + [P(x, "c") for x in [
    "Paper: S. Knapen, H. K. Lou, M. Papucci, J. Setford, Phys. Rev. D 96, 115015 (2017), arXiv:1708.02243.   [27] ATLAS, ATL-PHYS-PUB-2009-002.",
    "J. Li, T. Li, J. Pei, W. Zhang, “The quirk trajectory”, arXiv:2002.07503 (Eqs. II.11–II.14, A.4–A.5; Sec. VI, App. D).",
    "J. Li, T. Li, J. Pei, W. Zhang, arXiv:1911.02223 (EW trigger 0.1 as an LO ratio, App. A).   J. Li et al., arXiv:2108.06748.   J. L. Feng et al., arXiv:2404.13814.",
    "Particle Data Group, C. Patrignani et al. (2016), Passage of particles through matter, Eq. 34.12 (most probable energy loss) and Table 34.4 (silicon).",
    "HSCP and monojet limits in Fig. 6: M. Farina, M. Low, private communication to the paper's authors (related: arXiv:1703.00912); taken here from the paper's figure."]]
S += [P("Data and scripts: R_data_2026_10_15.py (all numbers), R_report_2026-10-21_partAB.py, F38–F42, F6 (F6_07 for the Part A / Part B split), F7 figures; Table II as "
        "tables/table_II_expected_events.csv; L tables (10⁸ ħ) in L_VALUES_CSV_2026-10-21/; all plotted numbers as CSV in ROOT_CSV_FIGURES_2026-10-21/; ROOT versions of Figs. 2–7 in ROOT_GENERATED_GRAPHS/.", "m")]
def deco(cv_, d):
    cv_.saveState(); cv_.setFont("DV", 7.3); cv_.setFillColor(MUTED); cv_.drawString(18 * mm, 10 * mm, "Reproduction of arXiv:1708.02243 · 21 October 2026")
    cv_.drawRightString(192 * mm, 10 * mm, f"{d.page}"); cv_.restoreState()
doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=14 * mm, bottomMargin=16 * mm, title="Reproduction of arXiv:1708.02243", author="")
doc.addPageTemplates([PageTemplate("p", [Frame(18 * mm, 16 * mm, 174 * mm, 267 * mm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=deco)])
doc.build(S); print("wrote", OUT, "| 2-sigma rule vs Wilson disagreements:", WIL)
