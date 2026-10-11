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
def w95(k, n): lo, hi = wilson(k, n); return f"[{lo:.3f}, {hi:.3f}]"
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
      E("p-value: exact binomial probability of a result at least as far from the paper's value as ours, taking the paper's value as exact (the paper gives no counts or errors)"),
      Spacer(1, 4),
      table(["p-value", "Verdict"], [["p &lt; 0.01", ("Strongly inconsistent", "bad")], ["0.01 ≤ p &lt; 0.05", ("Statistically inconsistent", "bad")],
                                      ["0.05 ≤ p &lt; 0.10", ("Borderline / mild tension", "warn")], ["p ≥ 0.10", (OK_LABEL, "ok")]], [40, 75])]

# 1 pile-up
def pur(st): return PU[PU.stage == st].iloc[0]
prow = []
for nm, st in [("Plane, hits in ≥ 4 of 8 layers", "plane with >=1 hit in >=4 of 8 layers"), ("Plane, hits in all 8 layers", "plane with >=1 hit in all 8 layers"),
               ("Any reconstructed plane", "Sec. III C plane"), ("Hit multiplicity", "hit multiplicity 7x2+1"), ("Signal region", "ds < 0.01 cm = signal region")]:
    r = pur(st); k, n = int(r.k), int(r.n)
    rate = f"{sci(k/n)} ± {sci(np.sqrt(k/n*(1-k/n)/n))}" if k else "0"
    rng = f"[{sci(r.wilson95_lo)}, {sci(r.wilson95_hi)}]" if k else ulf(k, n)
    pap = {"plane with >=1 hit in >=4 of 8 layers": "≈ 1×10⁻³", "plane with >=1 hit in all 8 layers": "≈ 6×10⁻⁵"}.get(st, "—")
    cmp_ = r.comparison if isinstance(r.comparison, str) else ("no event passes" if k == 0 else "—")
    prow.append([nm, f"{k}/{n}", rate, rng, pap, cmp_[0].upper() + cmp_[1:]])
S += [PageBreak(), KeepTogether([P("1. Pile-up background (⟨μ⟩ = 50, 5000 events)", "h2"),
      table(["Quantity", "k/n", "Rate ± SE", "Wilson 95% / UL", "Paper", "Comparison"], prow, [42, 18, 34, 34, 18, 28])]),
      P("The paper gives approximate rates without counts or errors, so no formal test is made.", "m"), Spacer(1, 4),
      img(fig("F13v3_pileup"), 150, "Pile-up rates with Wilson 95% intervals; ◁ = 95% upper limit when no event passes; diamonds = paper."), Spacer(1, 4),
      box("Why the 4-of-8 rate is higher", [
          "Our pile-up tracks are ideal helices in the 8 barrel layers; the paper's simulation adds energy loss, bremsstrahlung and endcaps, which remove soft tracks.",
          "Our minimum-bias pool has 20 000 events (paper: 125 000), and the paper does not define “a plane” for this number."])]

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
ovc = CV3[(CV3.setup.str.startswith("conversion + pile-up")) & (CV3.stage == "hit multiplicity")].iloc[0]
S += [Spacer(1, 10), KeepTogether([P("2. Converted-photon background (9139 Z(νν)γ+jet photons, |η| &lt; 1.8, fit from the vertex)", "h2"),
      table(["Setup", "Plane", "Hit mult.", "Signal region", "Wilson 95% / UL", "Events at 300 fb⁻¹ (our σ / paper σ)"], crow, [44, 20, 20, 22, 30, 38])]),
      P("Events at 300 fb⁻¹ = σ × 1% conversion probability × fraction × 300 fb⁻¹, with σ = 0.21 pb (our MadGraph) or ≈ 1 pb (paper). With 0 events the 95% upper limit is used.", "m"), Spacer(1, 4),
      img(fig("F14v3_conversion"), 150, "Fraction of photons passing each cut; open triangles = 95% upper limit when no event passes."), Spacer(1, 4),
      box("Reading", [
          "With SCT smearing along the beam (1.16 or 0.58 mm), no conversion passes, with or without pile-up, as the paper says.",
          f"Pile-up hits can fill the gaps of an e⁺e⁻ pair ({int(ovc.k)}/9139 pass the hit count), but none of them is thin enough to pass Δs.",
          "Without SCT smearing along the beam, 30/9139 = 0.33% of conversions pass. That setting is not background-free.",
          "Our cross-section is 4.3× below the paper's ≈ 1 pb (generator settings not given). The 1% conversion probability is taken from the paper's own “≈ 1 pb → ≈ 10 fb”."])]

# 3 & 4 signal
def sigtab(samples):
    rows = []
    for q, qn in [("trigger", "ε<sub>trig</sub>"), ("fiducial", "ε<sub>fid</sub>")]:
        for s in samples:
            k, n, p0, p = vrow(s, q); rows.append([qn, s, f"{k}/{n}", epm(k, n), w95(k, n), f"{p0:.2f}", fp(p), cls(p)])
    for key in ("z1160", "z580", "z0"):
        for s in samples:
            k, n, p0, p = vrow(s, "reconstruction", TRT[key]); rows.append([f"ε<sub>reco</sub>, SCT z {TL[key]}", s, f"{k}/{n}", epm(k, n), w95(k, n), f"{p0:.2f}", fp(p), cls(p)])
    return table(["Efficiency", "Sample", "k/n", "ε ± SE", "Wilson 95%", "Paper", "p", "Verdict"], rows, [33, 17, 17, 25, 27, 12, 17, 26])
S += [PageBreak(), KeepTogether([P("3. Colored quirks (m<sub>Q</sub> = 1800 GeV, Λ = 2 keV)", "h2"), sigtab(["COL1000", "COL2000"])]), Spacer(1, 10),
      KeepTogether([P("4. Electroweak quirks (m<sub>Q</sub> = 800 GeV, Λ = 4 keV)", "h2"), sigtab(["EW1000", "EW2000"])]), Spacer(1, 6),
      box("Reading", [
          "<b>Colored:</b> trigger and fiducial agree with the paper. Reconstruction agrees for 0.58 mm and for no smearing; at 1.16 mm the larger sample is low (3/25).",
          "<b>EW trigger:</b> 17–18% against 10%. The same definition gives the paper's colored value, and 36 generator variations keep EW at 13–19% (figure below). The paper's generator settings are not given.",
          "<b>EW fiducial:</b> 45–51% against 28%. Using the detector lengths of [27] instead of |η| &lt; 1.8 gives 33–37%, close to 28% (section 6), but the paper does not say it used them.",
          "<b>EW reconstruction:</b> 15–31% with SCT smearing along the beam; 81–85% only without it."]), Spacer(1, 4),
      img(fig("F09_diag_ew_trigger"), 160, "EW vs colored trigger efficiency for every generator variation tried (left; star = paper) and all EW values (right).")]

# 5 reconstruction
bsrows = []
for bs, lab_ in [("CV", "One common shift per event, fit from the true vertex (used)"), ("CO", "One common shift per event, fit from the origin"), ("PH", "Separate 45 mm shift of every hit")]:
    c2 = MX[(MX["sample"] == "COL2000") & (MX.acceptance == "A") & (MX.beamspot == bs)].set_index("sct_z"); e2 = MX[(MX["sample"] == "EW2000") & (MX.acceptance == "A") & (MX.beamspot == bs)].set_index("sct_z")
    f = lambda m: f"{int(m.loc['Z1160'].final)} · {int(m.loc['Z580'].final)} · {int(m.loc['Z0'].final)}  of {int(m.loc['Z1160'].fiducial)}"
    bsrows.append([lab_, f(c2), f(e2)])
S += [PageBreak(), P("5. What decides reconstruction", "h2"),
      img(fig("F08v3_reco_vs_sct_z"), 150, "Reconstruction efficiency of the same events for each SCT smearing along the beam. Bars = Wilson 95%; lines = paper."), Spacer(1, 3),
      img(fig("F15v2_signal_ds_vs_paper"), 160, "Signal Δs before the last cut. With 1.16 mm (solid) our events sit right of the paper's Fig. 5 (dotted); without smearing (dashed) they move close to it."), Spacer(1, 4),
      box("Reading", [
          "[27] gives the SCT accuracy as 17 µm across and 0.58 mm along the beam. The paper doubles “the intrinsic accuracy” without naming the direction, so 1.16 mm is our reading of the text.",
          "With 1.16 mm the reconstructed plane is too thick (signal Δs median 110–124 µm; cut 100 µm). The paper's own Fig. 5 (≈ 30 µm) fits only with little or no smearing along the beam."]), Spacer(1, 5),
      KeepTogether([P("<b>45 mm beam spot.</b> The paper smears “the z-coordinates of all the hits” and assumes the vertex “is identified correctly, and is located at the origin”. "
                      "Events passing the signal region for SCT z 1.16 · 0.58 mm · none:", "b"), Spacer(1, 3),
                    table(["Reading of the beam-spot sentence", "Colored 2000", "EW 2000"], bsrows, [96, 38, 38])])]

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
      table(["", "Quantity", "Paper", "1000-event sample: ε ± SE, Wilson 95%, p", "2000-event sample: ε ± SE, Wilson 95%, p", "Verdict (2000)"], rows, [15, 26, 11, 48, 48, 26])]), Spacer(1, 4),
      box("Bottom line", [
          "<b>Agrees with the paper:</b> colored trigger and fiducial efficiency; colored reconstruction for 0.58 mm or no SCT smearing along the beam.",
          "<b>Does not agree:</b> EW trigger (0.18 vs 0.10), EW fiducial (0.51 vs 0.28), and EW reconstruction with SCT smearing along the beam (0.22–0.31 vs 0.72).",
          "<b>Backgrounds:</b> pile-up only and conversion only give no signal-region event, and so does the conversion + pile-up overlay with this setup. "
          "Without SCT smearing along the beam, 0.33% of conversions would pass.",
          "<b>Why a full reproduction is not possible:</b> the paper does not fix the SCT smearing along the beam, the beam-spot treatment, the exact acceptance or the generator settings, and it gives no event counts or errors."]), Spacer(1, 4),
      img(fig("F06v2_table_I_primary"), 140, "Table I comparison; reconstruction shown for each SCT smearing along the beam. Bars = Wilson 95%; dashed = paper."), Spacer(1, 4),
      KeepTogether([P("<b>Sensitivity check: detector lengths from [27]</b> (pixel |z| &lt; 40.05 cm, SCT |z| &lt; 74.9 cm) instead of |η| &lt; 1.8", "b"), Spacer(1, 2),
      table(["Sample", "ε_fid = k/n ± SE", "Wilson 95%", "p vs 0.28", "Signal region (z 1.16 · 0.58 mm · none)"], sens, [22, 40, 30, 22, 60])])]

# Appendix A
ss = pd.read_csv(f"{T}/v2_source_status.csv")
from xml.sax.saxutils import escape as X
def stc(s): return (s, "ok") if s.startswith(("PAPER", "REFERENCE")) else (s, "warn") if s.startswith("INFERRED") else (s, "bad") if s.startswith("UNDOC") else (s, None)
keep = ss[~ss.implementation_choice.str.startswith("Converted photon")].copy()
srows = [[X(r.implementation_choice.replace(" (PRIMARY)", "").replace(" (PRIMARY reading)", "")), X(r.exact_source.replace(". Original project choice", "")), stc(r.status.replace("PAPER-STATED (paper-internal inconsistency)", "PAPER-STATED")), X(r.resulting_counts)] for r in keep.itertuples()]
pm = PU[PU.stage == "ds < 0.01 cm = signal region"].iloc[0]; ovr = CV3[(CV3.setup.str.startswith("conversion + pile-up")) & (CV3.stage == "signal region")].iloc[0]
srows += [[X("Pile-up: mu = 50, 45 mm per vertex, ATLAS tracking-efficiency removal, pixel merging"), X("Paper Sec. III D; ATL-PHYS-PUB-2015-051; pool 20 000 events (paper: 125 000)"), ("PAPER-STATED (pool size differs)", "ok"), f"signal region {int(pm.k)}/{int(pm.n)}"],
          [X("Converted photon: conversion in the beam pipe, equal energy sharing, 1% probability; overlay with pile-up"), X("Paper Sec. III D (1% derived from '~1 pb -> ~10 fb')"), ("PAPER-STATED", "ok"),
           f"signal region 0/9139 (z 1.16), 0/9139 (0.58), 30/9139 (none); with pile-up {int(ovr.k)}/{int(ovr.n)}"]]
S += [PageBreak(), P("Appendix A. Where every setting comes from", "h2"),
      P("Green = stated in the paper or [27]; amber = our reading; red = no source. Counts are listed in the order COL1000, COL2000, EW1000, EW2000.", "m"), Spacer(1, 3),
      table(["Setting", "Source", "Status", "Resulting counts"], srows, [38, 60, 36, 40])]
S += [PageBreak(), P("Appendix B. Paper-figure reproductions", "h2"),
      Table([[img(fig("F02_angular_momentum_and_separation"), 84, "Fig. 2 style: angular momentum L and quirk separation d for one colored event (COL2000 event 107). L peaks near 9×10¹¹ ħ, the paper's ≈ 10¹² ħ scale.", cell=True),
              img(fig("F03_plane_rotation"), 84, "Fig. 3 style: the quirk plane rotates by less than 10⁻⁴ rad, so the hits stay on one plane.", cell=True)]],
            colWidths=[88 * mm, 88 * mm], style=[("VALIGN", (0, 0), (-1, -1), "TOP")]),
      Spacer(1, 4), img(fig("F04_signal_event_displays"), 90, "Fig. 4 style: hits of one colored (COL2000 event 201) and one EW (EW2000 event 23) event in the plane's own coordinates, SCT z 1.16 mm. Both pass the signal region (Δs = 52 and 96 µm). Band = ±Δw.")]
