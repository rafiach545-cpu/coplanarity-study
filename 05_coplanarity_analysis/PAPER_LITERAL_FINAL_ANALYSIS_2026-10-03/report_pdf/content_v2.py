# ---------- content (v2: corrected acceptance / longitudinal classification) ----------
V = pd.read_csv(f"{T}/v2_primary_table_I.csv"); SB = pd.read_csv(f"{T}/v2_finite_barrel_sensitivity.csv")
MX = pd.read_csv(f"{T}/acceptance_longitudinal_matrix.csv")
TRT = {"z1160": "SCT z 1160 um (2x580, INFERRED)", "z580": "SCT z 580 um (1x Ref.[27], sensitivity)", "z0": "no SCT z smearing (UNDOCUMENTED)"}
TLAB = {"z1160": "SCT z 1.16 mm (inferred)", "z580": "SCT z 0.58 mm (sensitivity)", "z0": "no SCT z smearing (undocumented)"}
def vrow(d, s, q, t="—"):
    r = d[(d["sample"] == s) & (d.quantity == q) & (d.treatment == t)].iloc[0]
    k, n = int(r.k), int(r.n); p0 = PAPER["COL" if s.startswith("COL") else "EW"][{"trigger": "trigger", "fiducial": "fiducial", "reconstruction": "reco"}[q]]
    p = pexact(k, n, p0); assert abs(p - r.p_exact_vs_paper) <= 1e-9 * max(p, 1e-300) + 1e-300, (s, q, t)      # re-check
    return k, n, p0, p
S = []
S += [P("Reproducing Table I of “Tracking down Quirks at the LHC”", "h1"),
      P("Knapen, Lou, Papucci &amp; Setford, arXiv:1708.02243 · short report, version 2 · 3 October 2026", "m"), Spacer(1, 6),
      P("We redid the paper's signal and background study using only what the paper and its detector reference [27] say. Nothing was tuned to "
        "match the paper. Each simulated sample is shown on its own. Every setting is labelled by where it comes from."), Spacer(1, 6),
      box("What changed from version 1", [
          "The <b>paper-stated</b> acceptance is used as the main result: barrel only, which the paper says “effectively restricts the fiducial range to |η| ≲ 1.8”. "
          "The finite barrel lengths of reference [27] are now a labelled sensitivity study, since the paper never says it applied them.",
          "The fiducial denominators therefore return to <b>25</b> (colored, 2000-event sample) and <b>94</b> (EW, 2000-event sample).",
          "SCT resolution along the beam is now shown for every treatment: 1.16 mm (the paper's “twice the intrinsic accuracy” applied to the 580 µm that [27] quotes; inferred), "
          "0.58 mm (sensitivity) and no smearing (undocumented). None of them is stated outright by the paper.",
          "The 45 mm beam-spot sentence allows three readings; all three are shown (section 5)."]), Spacer(1, 6),
      table(["Exact p-value", "What we call it"],
            [["p &lt; 0.01", ("Strongly inconsistent", "bad")], ["0.01 ≤ p &lt; 0.05", ("Statistically inconsistent", "bad")],
             ["0.05 ≤ p &lt; 0.10", ("Borderline / mild tension", "warn")], ["p ≥ 0.10", ("Consistent", "ok")]], [45, 60]), Spacer(1, 4),
      P("<b>How to read the tables.</b> k/n = events passing / events tested. 95% CI = Wilson interval. With 0 events we quote the one-sided 95% upper limit (UL). "
        "p = exact binomial probability of our count if the paper's number were exactly right. The paper gives no counts or errors, so its own simulation "
        "uncertainty is ignored and borderline p-values are a little optimistic. Labels: <b>stated</b> = written in the paper or [27]; <b>inferred</b> = our reading of "
        "an unclear sentence; <b>undocumented</b> = no source.", "m")]

# 1 pile-up
pu = pd.read_csv(f"{T}/pileup_cutflow.csv")
def pur(cfg, stage):
    return pu[pu.config.str.startswith(cfg) & (pu.stage == stage)].iloc[0]
S48, S88, SPL, SSR = "plane with >=1 hit in >=4/8 layers (paper 1e-3)", "plane with >=1 hit in 8/8 layers = relaxed control (paper 6e-5)", "Sec. III C plane", "final Sec. IV"
rows = []
for nm, stg, p0, pap in [("Plane with hits in ≥ 4 of 8 layers", S48, 1e-3, "~1×10⁻³"), ("Plane with hits in all 8 layers", S88, 6e-5, "6×10⁻⁵"), ("Any reconstructed plane", SPL, None, "not given"), ("Full signal region", SSR, None, "“a few” in Fig. 5")]:
    cells = [nm]
    for cfg in ("FROZEN", "LITERAL"):
        r = pur(cfg, stg); k = int(r.k)
        cells.append(f"{k}/5000" + (f" = {r.frac:.1e}".replace("e-0", "×10⁻").replace("1×10⁻", "1×10⁻") if k else f" (UL {r.cp95_upper_one_sided:.1e})").replace("e-04", "×10⁻⁴").replace("e-03", "×10⁻³"))
    pA = pexact(int(pur("FROZEN", stg).k), 5000, p0) if p0 else None
    cells += [pap, fp(pA) if pA is not None else "—", cls(pA) if pA is not None else ("n/a", None)]
    rows.append(cells)
S += [Spacer(1, 8), KeepTogether([P("1. Pile-up background (⟨μ⟩ = 50, 5000 events per run)", "h2"),
      table(["Quantity", "|η| &lt; 1.8 run (paper-stated)", "Finite-barrel run (sensitivity)", "Paper", "p (|η| run)", "Category"], rows, [38, 33, 33, 22, 18, 30])]),
      P("The |η| &lt; 1.8 run is the existing project run (SCT 34/1.16 mm, no pixel merging); the finite-barrel run includes merging. No new pile-up events were generated.", "m"), Spacer(1, 4),
      img(fig("F13v2_pileup_by_acceptance"), 150, "Pile-up rates with 95% intervals for both runs; diamonds = paper."), Spacer(1, 4),
      box("Reading", [
          "No pile-up event reaches the signal region in either run (95% UL 6×10⁻⁴ per event), as the paper concludes.",
          "The all-8-layer rate agrees with the paper. The 4-of-8 rate is 6–12× higher. Likely reasons: our pile-up tracks are ideal helices "
          "with no energy loss, bremsstrahlung or endcaps; our pool has 20 000 minimum-bias events instead of 125 000; the paper does not define “a plane” there."])]

# 2 conversions
cA = pd.read_csv(f"{T}/conversion_acceptance_A_cutflow.csv"); ovt = pd.read_csv(f"{T}/overlay_cutflow.csv")
def cAr(cfg, st): r = cA[(cA.config == cfg) & (cA.stage == st)].iloc[0]; return int(r.k), r
def fmtk(k, r): return f"{k}/9139 = {pct(r.frac)}" if k else f"0/9139 (UL {r.cp95_upper_one_sided*1e4:.1f}×10⁻⁴)"
crow = []
for lab_, cfg in [("SCT z 1.16 mm (inferred)", "A_Z1160_PV"), ("SCT z 0.58 mm (sensitivity)", "A_Z580_PV"), ("no SCT z smearing (undocumented)", "A_Z0_PV")]:
    kp, rp = cAr(cfg, "Sec. III C plane"); km, rm = cAr(cfg, "hit multiplicity"); kf, rf = cAr(cfg, "final Sec. IV")
    crow.append([lab_, fmtk(kp, rp), fmtk(km, rm), fmtk(kf, rf), ("No fake signal", "ok") if kf == 0 else (f"{kf} fake signals", "bad")])
ofz = ovt[ovt.config.str.startswith("FROZEN overlay v1 (all")]; olt = ovt[ovt.config.str.startswith("LITERAL")]
def og(d, k): return d[d.stage.str.startswith(k)].iloc[0]
crow.append(["+ pile-up, SCT 1.16 mm, fit from conversion point (old run)", fmtk(int(og(ofz, "Sec. III C").k), og(ofz, "Sec. III C")), fmtk(int(og(ofz, "hit mult").k), og(ofz, "hit mult")), "1/9139 (event 2555)", ("1 fake signal", "warn")])
crow.append(["+ pile-up, finite barrel, SCT 1.16 mm, fit from vertex", fmtk(int(og(olt, "Sec. III C").k), og(olt, "Sec. III C")), fmtk(int(og(olt, "hit mult").k), og(olt, "hit mult")), "0/9139 (UL 3.3×10⁻⁴)", ("No fake signal", "ok")])
S += [Spacer(1, 8), KeepTogether([P("2. Converted-photon background (9139 Z(νν)γ+jet photons)", "h2"),
      table(["Setup (|η| &lt; 1.8 unless stated)", "Plane", "Hit multiplicity", "Signal region", "Result"], crow, [52, 34, 34, 30, 24])]),
      P("No p-value: the paper gives no background rate to test against. Expected events at 300 fb⁻¹ = σ × 1% × fraction × 300 fb⁻¹: with 0/9139 the 95% "
        "limit is &lt; 0.21 events (our σ = 0.23 pb) or &lt; 0.98 (paper σ ≈ 1 pb); 30/9139 gives ≈ 2.1 (our σ) to 9.8 (paper σ) events.", "m"), Spacer(1, 4),
      img(fig("F14v2_conversion_by_acceptance"), 150, "Fraction of photons surviving each cut. Open triangles: 95% upper limit when nothing survives."), Spacer(1, 4),
      box("Reading", [
          "With the SCT smearing that [27] implies (1.16 or 0.58 mm), no conversion fakes a quirk, as the paper says.",
          "Without SCT z smearing, the setting that brings the signal closest to the paper (section 5), 30/9139 = 0.33% of conversions pass. That setting is not background-free.",
          "The old project overlay run had one passing event (2555), fitted from the conversion point; the paper fits from the primary vertex. In the finite-barrel run with the vertex fit, nothing passes. "
          "An overlay run with |η| &lt; 1.8 and the vertex fit was not made (it needs a new 1.5 h pile-up pass).",
          "Our Z(νν)γ+jet cross-section is 4.3× below the paper's ~1 pb; generator settings are not given. The 1% conversion probability comes from the paper's own “~1 pb → ~10 fb”."])]

# 3 colored, 4 EW
def sigtab(samples):
    rows, shade = [], []
    for q, qn in [("trigger", "Trigger"), ("fiducial", "Fiducial (|η| &lt; 1.8)")]:
        for s in samples:
            k, n, p0, p = vrow(V, s, q); c = cls(p); rows.append([qn, s, f"{k}/{n}", pct(k / n), ci(k, n), f"{p0:.2f}", fp(p), c])
    for key in ("z1160", "z580", "z0"):
        for s in samples:
            k, n, p0, p = vrow(V, s, "reconstruction", TRT[key]); rows.append([f"Reco, {TLAB[key]}", s, f"{k}/{n}", pct(k / n), ci(k, n), f"{p0:.2f}", fp(p), cls(p)])
            if key != "z1160": shade.append(len(rows))
    return table(["Efficiency", "Sample", "Ours", "%", "95% CI (%)", "Paper", "p", "Category"], rows, [52, 17, 16, 13, 23, 12, 17, 24])
S += [PageBreak(), KeepTogether([P("3. Colored quirk signal (m<sub>Q</sub> = 1800 GeV, Λ = 2 keV)", "h2"), sigtab(["COL1000", "COL2000"])]), Spacer(1, 3),
      P("Grey rows: other SCT z treatments (sensitivity / undocumented). Reconstruction denominators are the |η| &lt; 1.8 fiducial events (7 and 25).", "m"), Spacer(1, 8),
      KeepTogether([P("4. Electroweak quirk signal (m<sub>Q</sub> = 800 GeV, Λ = 4 keV)", "h2"), sigtab(["EW1000", "EW2000"])]), Spacer(1, 3),
      P("Reconstruction denominators: 40 and 94.", "m"), Spacer(1, 5),
      box("Reading", [
          "Colored: trigger and fiducial agree. Reconstruction agrees for the 0.58 mm and no-smearing treatments, and is statistically inconsistent for 1.16 mm in the larger sample (3/25, p = 0.019).",
          "EW trigger: 17–18% against 10%. 36 one-at-a-time generator changes keep it at 13–19% (next figure); the same definition gives the paper's colored value, so an undocumented generator setting is the likely cause.",
          "EW fiducial: with the paper-stated |η| &lt; 1.8 our value is 45–51% against 28% (strongly inconsistent). Only the finite barrel of [27] gives 28% (33–37%), but the paper does not say it used it. Unresolved.",
          "EW reconstruction: 15–31% with any SCT z smearing that has a source; 81–85% (borderline, p ≈ 0.07) only without SCT z smearing, which no source supports."]), Spacer(1, 4),
      img(fig("F09_diag_ew_trigger"), 172, "Left: EW vs colored trigger efficiency for every generator variation tried; star = paper. Right: all EW values.")]

# 5 why reco + beam spot
bsrows = []
for bs, lab_ in [("CV", "One common shift per event, fit from the true vertex (used above)"), ("CO", "One common shift per event, fit from the origin"), ("PH", "Independent 45 mm shift of every hit")]:
    c2 = MX[(MX["sample"] == "COL2000") & (MX.acceptance == "A") & (MX.beamspot == bs)].set_index("sct_z"); e2 = MX[(MX["sample"] == "EW2000") & (MX.acceptance == "A") & (MX.beamspot == bs)].set_index("sct_z")
    f = lambda m: f"{int(m.loc['Z1160'].fiducial)} / {int(m.loc['Z1160'].final)} · {int(m.loc['Z580'].final)} · {int(m.loc['Z0'].final)}"
    bsrows.append([lab_, f(c2), f(e2)])
S += [PageBreak(), P("5. What decides reconstruction: SCT resolution along the beam, and the beam spot", "h2"),
      img(fig("F08v2_sct_z_envelope"), 172, "Reconstruction efficiency of the same events for each SCT z treatment. Left: paper-stated acceptance (main). Right: finite barrel (sensitivity)."), Spacer(1, 3),
      img(fig("F15v2_signal_ds_vs_paper"), 165, "Signal Δs before the last cut, paper-stated acceptance. With 1.16 mm smearing (solid) our events sit right of the paper's Fig. 5 (dotted); without it (dashed) they move close to it."), Spacer(1, 4),
      box("Reading", [
          "Reference [27] gives the SCT accuracy as 17 µm across and 580 µm along the beam. The paper doubles “the intrinsic accuracy” without naming a coordinate, so 1.16 mm along the beam is our reading, not a stated number.",
          "With 1.16 mm the fitted plane is thick (signal Δs median 110–124 µm, cut at 100 µm). The paper's own Fig. 5 shows ~30 µm, which needs little or no SCT z smearing. The paper does not say what it ran."]), Spacer(1, 5),
      KeepTogether([P("<b>The 45 mm beam spot.</b> The paper applies “a uniform, gaussian smearing with width 45 mm to the z-coordinates of all the hits” and assumes the primary vertex “is identified correctly, and is located at the origin”. Three readings, counts as fiducial / final for SCT z 1.16 mm · 0.58 mm · none (|η| &lt; 1.8):", "b"), Spacer(1, 3),
      table(["Beam-spot reading (all inferred)", "Colored 2000", "EW 2000"], bsrows, [94, 40, 40])]),
      P("Per-hit smearing (45 mm ≈ 450× the Δs cut) leaves no reconstructable plane at all; a fit from the origin misses planes that pass through the displaced vertex. "
        "We use the common shift with the vertex fit because the paper says the vertex is identified correctly; this choice was not based on matching Table I.", "m")]

# 6 Table I
rows = []
for bench, samples, label in [("COL", ["COL1000", "COL2000"], "Colored"), ("EW", ["EW1000", "EW2000"], "EW")]:
    for q, qn, t in [("trigger", "ε_trig", "—"), ("fiducial", "ε_fid (|η| &lt; 1.8)", "—"), ("reconstruction", "ε_reco, z 1.16 mm", TRT["z1160"]),
                     ("reconstruction", "ε_reco, z 0.58 mm", TRT["z580"]), ("reconstruction", "ε_reco, no z smear", TRT["z0"])]:
        cells = []
        for s in samples:
            k, n, p0, p = vrow(V, s, q, t); lo, hi = wilson(k, n); cells.append(f"{k}/{n} = {k/n:.3f} [{lo:.3f}, {hi:.3f}]<br/>p = {fp(p)}")
        k, n, p0, p = vrow(V, samples[1], q, t); c = cls(p)
        rows.append([f"<b>{label}</b>" if q == "trigger" else "", qn, f"{p0:.2f}", cells[0], cells[1], c])
sens = []
for s in ["COL1000", "COL2000", "EW1000", "EW2000"]:
    f_ = SB[(SB["sample"] == s) & (SB.quantity == "fiducial")].iloc[0]
    fin = [int(SB[(SB["sample"] == s) & (SB.treatment == TRT[k_])].iloc[0].k) for k_ in ("z1160", "z580", "z0")]
    sens.append([s, f"{int(f_.k)}/{int(f_.n)} = {f_.frac:.2f}", f"{fp(f_.p_exact_vs_paper)}", " · ".join(map(str, fin))])
S += [PageBreak(), P("6. Table I: paper vs this work (paper-stated acceptance)", "h2"),
      table(["", "Quantity", "Paper", "Sample 1 (1000 gen.)", "Sample 2 (2000 gen.)", "Category (sample 2)"], rows, [16, 30, 12, 44, 44, 28]),
      P("Wilson 95% CI in brackets; exact p vs the paper. The category uses the larger sample.", "m"), Spacer(1, 4),
      img(fig("F06v2_table_I_primary"), 172, "Table I comparison with the paper-stated acceptance; reconstruction shown for each SCT z treatment. Bars = Wilson 95%; dashed = paper."), Spacer(1, 4),
      KeepTogether([P("<b>Sensitivity study: finite barrel lengths of [27]</b> (inferred, not the main result)", "b"), Spacer(1, 2),
      table(["Sample", "Fiducial", "p vs 0.28", "Final: z 1.16 mm · 0.58 mm · none"], sens, [30, 40, 30, 60])]), Spacer(1, 5),
      box("Bottom line", [
          "Reproduced with paper-stated settings: colored trigger, colored fiducial, and the absence of background in the signal region.",
          "Not reproduced: EW trigger (17–18% vs 10%), EW fiducial with the stated |η| &lt; 1.8 (45–51% vs 28%), and EW reconstruction with any SCT z smearing that has a source (15–31% vs 72%).",
          "Colored reconstruction depends on the SCT z treatment: 12–14% at 1.16 mm, 20–43% at 0.58 mm, 44–71% without smearing (paper 35%).",
          "A full reproduction is impossible from the published information: the acceptance actually used, the SCT resolution along the beam, the beam-spot treatment and the generator settings are not uniquely given, and the paper publishes no counts or errors."])]

# Appendix A: source status
ss = pd.read_csv(f"{T}/v2_source_status.csv")
def stc(s):
    s0 = s.split(" ")[0]
    return (s, "ok") if s.startswith("PAPER") or s.startswith("REFERENCE") else (s, "warn") if s.startswith("INFERRED") else (s, "bad") if s.startswith("UNDOC") else (s, None)
srows = [[r.implementation_choice, r.exact_source, stc(r.status), r.resulting_counts] for r in ss.itertuples()]
S += [PageBreak(), P("Appendix A. Where every setting comes from", "h2"),
      P("Colour: green = stated in the paper or [27]; amber = inferred; red = undocumented. Counts: fiducial or final as noted, samples in the order COL1000, COL2000, EW1000, EW2000 where four are given.", "m"), Spacer(1, 3),
      table(["Implementation choice", "Exact source", "Status", "Resulting counts"], srows, [40, 64, 30, 40])]

# Appendix B: figure reproductions
S += [PageBreak(), P("Appendix B. Paper-figure reproductions", "h2"),
      Table([[img(fig("F02_angular_momentum_and_separation"), 84, "Fig. 2 style: angular momentum L and quirk separation d (colored, COL2000 event 107). L peaks near 9×10¹¹ ħ, the paper's ~10¹² ħ scale.", cell=True),
              img(fig("F03_plane_rotation"), 84, "Fig. 3 style: rotation of the quirk plane stays below 10⁻⁴ rad, so the hits stay on a plane.", cell=True)]],
            colWidths=[88 * mm, 88 * mm], style=[("VALIGN", (0, 0), (-1, -1), "TOP")]),
      Spacer(1, 4), img(fig("F04_signal_event_displays"), 88, "Fig. 4 style: one colored (COL2000 event 201) and one EW (EW2000 event 23) event, SCT z 1.16 mm. Both pass the signal region with either acceptance (Δs = 52 and 96 µm).")]
