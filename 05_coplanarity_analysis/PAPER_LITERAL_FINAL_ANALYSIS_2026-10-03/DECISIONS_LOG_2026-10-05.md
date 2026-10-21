# Decisions log, 2026-10-05

## D1. Fiducial: primary definition moved to the Ref. [27] barrel lengths
- **Primary:** pixel |z| < 40.05 cm, SCT |z| < 74.9 cm (Ref. [27]); IBL |z| < 33.015 cm (arXiv:1803.00844); no η cut.
- **Status:** INFERRED application of REFERENCE-STATED lengths. The paper states the consequence ("effectively |η| ≲ 1.8") but not the lengths.
- **The paper's "|η| ≲ 1.8" wording as a per-hit cut** becomes the sensitivity study: `tables/v6_sensitivity_eta_acceptance.csv`.
- **Primary fiducial counts:** COL1000 6/27, COL2000 22/68, EW1000 33/89, EW2000 62/186 (`tables/v6_primary_table_I.csv`). All four have the paper's 0.28 inside Wilson 95%.

## D2. Signal: "no SCT z measurement smearing" is the best-supported reading
- **Basis:**
  - The paper's Fig. 5 signal Δs: EW 99% below the cut vs paper 90%; median 41 µm vs ≈ 28 µm. With 1.16 mm: 44%, 110 µm.
  - Reconstruction with the primary lengths: EW1000 27/33 = 0.82 [0.66, 0.91] (p = 0.25); EW2000 50/62 = 0.81 [0.69, 0.89] (p = 0.16); COL2000 8/22 = 0.36 [0.20, 0.57] (p = 1.0).
- **Status:** still UNDOCUMENTED in the text. The paper's "twice the intrinsic accuracy" applied to Ref. [27]'s 580 µm would give 1.16 mm.
- **COL1000 caveat:** 5/6 = 0.83 [0.44, 0.97] vs 0.35, p = 0.022, statistically inconsistent. This is n = 6; the larger COL2000 sample agrees.
- **Conversion caveat:** with this reading the conversion background is larger than the paper's Fig. 5. See D3 for the cited-model test.

## D3. Conversions with the paper's cited detector model ([34] = arXiv:1612.00850 App. A)
- **Model:** bremsstrahlung (deterministic, single tangential photon) + Bethe-Bloch most-probable ionisation; no multiple scattering; 25 ns stop; kinetic-energy stop.
- **X₀:** [34] takes radiation lengths from Andreazza:2009zz = ATL-COM-PHYS-2008-105. Its bibliography entry carries `%%CITATION = ATL-PHYS-PUB-2009-002`, the public version, which is paper ref. [27] (arXiv:0901.0512).
  - The only material numbers there are Fig. 3 (X₀ vs |η| per subdetector). It was vector-digitised at |η| < 0.5: beam pipe 0.0019, pixel 0.116, SCT 0.137 X₀.
  - Per layer at normal incidence: pixel 3.7%, SCT 3.3%. IBL = pixel value, INFERRED, since the IBL is not in the 2009 reference.
  - Files: `tables/material_X0_per_layer_ref27.csv`, `notes/ref27_CSC_page43_figure3.png`, `notes/ref27_CSC_page43_material_figure3.txt`.
- **Code:** `scripts/P17_conversion_ref34.py` (conversion only) and `scripts/P17b_overlay_ref34.py` (conversion + μ = 50 pile-up; pile-up tracks still ideal helices).
- **Validation:** with material off, all four geometry × SCT configurations reproduce the earlier runs event by event.
- **Conversion only, primary setup (B, no SCT z):** signal region 22/9139 → **1/9139** with the [34] model. Planes stay thin (median ≈ 2 µm).
- **Conversion + pile-up (primary setup B, no SCT z, [34] model, μ = 50; `logs/P10_chunks_B_Z0_REF34`, 9139/9139 events, exit 0):**
  - 9139 → 4105 plane → 285 hit multiplicity (3.1%) → **146 signal region (1.6%)**.
  - Hit-multiplicity population: Δs median 97 µm, 51% below the cut.
  - Signal region ≈ 0.16 fb with the paper's σ ≈ 1 pb (≈ 48 events at 300 fb⁻¹; ≈ 10 with our σ).
  - **Paper Fig. 5:** 0.67% reach the cut, median ≈ 280 µm, 3.6% below the cut, ≈ 0.0024 fb in the signal region.
  - The cited material model reduces the conversion background but leaves it ≈ 65× above the paper's Fig. 5.
  - **The no-SCT-z reading therefore still does not reproduce the paper's conversion background.**

## D4. EW trigger: no further compute
- **Final statement:** lowest EW ε_trig in any one-at-a-time variation or pre-registered combination = 0.126 [0.110, 0.145] (C4). 0.10 was not reached, whatever colored does.
- **Open (ask the authors):** a misprint, a different denominator, or an unstated EW-specific cut.
- **Fig. 6 test (logged, not run):** use the paper's Fig. 6 EW exclusion curve. At the excluded mass, the signal yield σ(m) × ε_trig × ε_fid × ε_reco × L must equal the paper's excluded event count. This allows backing out the effective ε_trig the authors used, with ε_fid and ε_reco from Table I, and checking whether it equals 0.10 or our ≈ 0.18. It needs the paper's Fig. 6 EW curve, its luminosity and its excluded-yield assumption. It is deferred together with Figure 6, which stays paused.

## D5. qCut confirmed = 45 GeV
- All four frozen signal samples (EW/colored × 1000/2000) use MG `JetMatching:qCut = -1` (automatic) with xqcut = 30.
- Pythia's command files contain `JetMatching:qCut = 4.5000000000e+01`, i.e. 45, not 4.5. The Pythia run logs' settings tables show "qCut 45.000" in effect.
- The Figure 6 pilot cards also have 45. The trigger-screen baseline B0 used `JetMatching:qCut = 45.0`.

## D6. Pre-registered test: conversion background at SCT z 580 µm (written BEFORE the run)
- **Hypothesis (review, 2026-10-05):** the paper simulated the signal without SCT z smearing but the conversion background with the cited model [34], whose resolution comes from the ATLAS TDR (SCT z ≈ 580 µm).
- **Verified:** [34] says "We take the resolution and geometry of each component from the ATLAS technical design report". The TDR is not available here; Ref. [27] gives 580 µm (z), used as the TDR value.
- **Run:** conversion + μ = 50 pile-up, Ref. [27] lengths, [34] material model (bremsstrahlung + ionisation, no multiple scattering), **SCT z 580 µm for conversion and pile-up hits**, SCT R-φ 34 µm, fit from the vertex. Same 9139 photons and seeds. Signal numbers are not affected.
- **Pass criterion, fixed now:** the paper's signal-region fraction 2.4×10⁻⁴ (0.0024 fb / 10 fb, ≈ 2 of 9139) lies inside the Wilson 95% interval of k/9139. That means k ≤ 6. k = 0 also passes (UL 3.3×10⁻⁴).
  - **Pass:** the paper's signal and background are both reproduced, with the background simulated at a coarser SCT z resolution than the signal. Finding: the background-free claim depends on that difference.
  - **Fail (k ≥ 7):** genuine tension with the paper's background statement.
- **Not verified by me:** the statement that a Fig. 6 check shows the EW 0.10 is not a misprint. No Fig. 6 check was run in this analysis (D4 lists it as not run).

### D6 result (appended after the run; the pre-registered text above verified unchanged against notes/D6_prereg_sha256.txt)
- **Run:** `scripts/P17c_overlay_ref34_z580.py`, `logs/P10_chunks_B_Z580_REF34`; 9139/9139 events, exit 0.
- **Cutflow:** 9139 → 3399 plane → 419 hit multiplicity (4.6%) → **0 signal region**.
  - Wilson 95% [0, 4.2×10⁻⁴]; one-sided 95% UL 3.3×10⁻⁴ (< 0.98 events at 300 fb⁻¹ with the paper's σ).
- **Verdict by the pre-registered criterion: PASS** (k = 0 ≤ 6; the paper's 2.4×10⁻⁴ lies inside the interval).
- **Conversion only (same model, `tables/conversion_ref34_B_Z580_per_event.csv`):** 0/9139.
- **Shape vs the paper's Fig. 5 conversion histogram:**
  - Hit-multiplicity population: Δs median 212 µm (16–84%: 170–254 µm) vs paper ≈ 280 µm, close.
  - Closest event 116 µm; 0% below the cut vs paper 3.6% ("a few").
  - Population size 4.6% vs paper ≈ 0.67% (≈ 7× larger).
- **Conclusion:** with the signal simulated without SCT z smearing and the conversion background with the cited model (SCT z 580 µm, bremsstrahlung, Ref. [27] lengths), the paper's signal efficiencies (except the EW trigger) and its conversion signal-region background are both reproduced.
- **Finding:** the paper's background-free statement for conversions relies on simulating the background at a coarser SCT z resolution than the signal. With the signal's resolution, the same model gives 146/9139 (≈ 10–48 events at 300 fb⁻¹; D3).
- **Remaining differences:** the size of the conversion population reaching the Δs cut (≈ 7×) and the missing small tail below the cut.

## D7. Implementation review, 2026-10-06 (paper re-read: Sec. III A–C, IV)
**Bugs found and corrected**
- **Only the first crossing of each layer was used.** Quirks often cross a layer 3 or 5 times within 25 ns (fiducial events with a repeated crossing: COL2000 13/22, EW2000 31/62; `tables/audit_multiple_crossings.csv`, `tables/audit_crossing_separation.csv`). The paper calculates "the intersections of the trajectories"; its "each quirk will most likely intersect each layer only once" is an expectation, not a cut. **Primary now: every crossing with t < 25 ns inside the [27] lengths is a hit** (`scripts/P18_all_crossings.py`; FIRST mode reproduces the stored results with 0 mismatches).
- **Fig. 2** used equal-lab-time L → now exact CM frame (`scripts/F22_dynamics_v2.py`, `scripts/F23_fig2_fig3_v2.py`). |L| is plotted; at |L| ≈ 0, d = 0.017–0.019 cm ≫ 1/m_Q.
- **Fig. 3** used a plane normal from x₁ × x₂ (gaps) → now L̂ (and a windowed plane fit, same within 10%), r = 0–15 cm. The earlier caption claim "< 10⁻⁴ rad" is withdrawn: colored median 0.42×10⁻³, EW 2 keV 0.89×10⁻³ (paper values at our 9th / 23rd percentile).
- **Fig. 4** was a hand-picked event → now the median-Δs signal-region event per sample (`scripts/F25_fig4_median_events.py`: COL2000 event 212, EW2000 event 270).
- **Fig. 5** signal → remade from all crossings, plane + hit cut, before the Δs cut (`scripts/F26_fig5_v3.py`).

**Checked, no change**
- Plane algorithm (seeds, windows, factor-3 rule, smallest-Δs choice, T about the PV) matches Sec. III C line by line.
- Δs = √λ₁ and Δw = √λ₂ of Eq. 11 ("Second eigenvalue of (11), or the 'width', (∆w)²").
- Charges: EW (−1, +1); colored (+1, −1) 65 events, (+2, −1) 3 events.
- Conversion background: GeV electrons cross each layer once, so it is unaffected. Low-pT pile-up loopers could recross (helix code uses the first crossing); noted, not changed.

**Open ambiguity (reported, not decided):** "All but one layer must contain 2 hits, the remaining layer must contain at least 1 hit". Primary = ≥ 2; sensitivity = exactly 2. With every crossing these differ strongly (EW2000 Z0: 49/62 vs 27/62). Results: `tables/v7_primary_table_I.csv`, `TABLE_I_RESULTS_2026-10-06.pdf`.
## D8. Pre-registered test: pile-up 4-of-8 rate with the cited detector model [34] (written BEFORE the run, 2026-10-08)
- **Question:** our pile-up rate of planes with >= 1 hit in >= 4 of 8 layers is 31/5000 = 6.2e-3 (selected Sec. III C plane, Delta_w < 1) and
  33/5000 = 6.6e-3 (any candidate), against the paper's "~1e-3" (Sec. IV). Changing the definition does not remove the gap; hit density
  (490-1670 per layer, paper "O(1000)"), 45 mm vertex spread and mu = 50 are as in the paper.
- **Run:** `scripts/P21_pileup_ref34.py REF34_Z580 5000`: same 5000 events and seeds as P8 (SeedSequence([90210777, 50, i])),
  two changes only: (1) every pile-up particle propagated with the [34] model (bremsstrahlung for electrons, most-probable ionisation
  with 1/beta^2 scaling, no multiple scattering, stop below 10% kinetic/mass, X0 from Ref. [27] Fig. 3); (2) SCT z 580 um.
  Unchanged: Ref. [27] lengths, pixel merging, track suppression, plane finding.
- **Validation done before the run:** material off + SCT z 1160 on events 0-199 reproduces logs/P8_chunks_LITERAL: plane / multiplicity /
  final identical for 200/200; hits per layer identical except 2 events (one layer-4 hit); Delta_s differs by <= 5.5 um in 7 events.
  Cause: gyroradius constant 333.564 vs 333.569 cm per GeV/T (1.5e-5) between the two helix solvers.
- **Primary statistic:** fraction of the 5000 events whose selected plane (Sec. III C, Delta_w < 1 cm) has >= 1 hit in >= 4 layers.
- **Outcomes, fixed now:**
  - rate <= 2e-3: the gap is explained by the missing material model.
  - 2e-3 < rate < 4e-3: partly explained.
  - rate >= 4e-3 (around 6e-3): unresolved; bug hunt on pile-up stops here.

### D8 result (appended after the run; pre-registered text verified unchanged against notes/D8_prereg_sha256.txt)
- **Run:** `scripts/P21_pileup_ref34.py REF34_Z580 5000`, `logs/P21_chunks_REF34_Z580`; 5000/5000 events, exit 0 (4718 s).
- **Primary statistic:** 33/5000 = 6.6e-3 (Wilson 95% [4.7e-3, 9.3e-3]); before (P8, no material, SCT z 1160): 31/5000 = 6.2e-3.
  Any candidate: 33/5000 (before 33/5000). 8/8 selected plane: 1/5000 (before 1/5000). Signal region: 0/5000 (before 0/5000).
- Hits per layer drop by 0-5% (material stops slow particles); the plane rates do not change.
- **Verdict by the pre-registered criterion: UNRESOLVED** (rate >= 4e-3). The missing material model does not explain the ~6x gap
  to the paper's "~1e-3". Bug hunt on pile-up stops here.

## D9. Closing the bug hunt (2026-10-08)
**Code checks, all clean (no bug found)**
- Trajectory amplitude: simulated first maximum of the quirk separation / 2 m_Q (gamma* - 1) / Lambda^2 = 0.99998-0.999999 at B = 0
  and B = 2 T for 146 trajectories (`scripts/D1_dcm_eq1_test.py`, `tables/dcm_eq1_test.csv`). No factor 2. String force = Lambda^2 per quirk (Eq. 3).
- Time is lab time: t(last layer) / [R_8 / (beta_T c)] = 1.00; lab / proper time = gamma (1.09 colored, 1.13 EW).
  25 ns cut drop: COL2000 0/22, COL1000 3/9, EW 0-2% ("slight drop", paper Sec. IV).
- 25 ns used consistently for hits and fiducial; no crossing >= 25 ns in fiducial events; Lambda scan fiducial = stored fiducial (0 mismatches).
- Colored R-hadron charges from Pythia8 particle data (COL2000: (+1,-1) x 65, (+2,-1) x 3), passed unchanged to the Lorentz force;
  momenta = final status-1 R-hadrons (Pythia), gamma* - 1 hard process vs R-hadron ratio 1.002 (FSR negligible).
- Plane fit: T = x^T x / (N-1) about the vertex, Delta_s = sqrt(lambda_1), Delta_w = sqrt(lambda_2) (Eq. 10-11).
- Hit merging applied after all crossings; extra crossings within one pixel of the first: 0/526 (colored), 12/790 (EW).

**Physics checks**
- Fig. 3 4-keV anomaly = L-hat estimator artefact. With the paper's definition (plane of the velocity vectors, `scripts/D2_dphi_estimators.py`):
  medians colored 0.22e-3, EW 2 keV 0.46e-3, EW 4 keV 0.56e-3; paper values at our 14th / 37th percentile.
- Delta_w is NOT caused by repeated crossings: same events FIRST vs ALL Delta_w 0.482/0.487 cm (colored), 0.096/0.096 cm (EW);
  single-crossing events alone: 0.54 cm colored, 0.086 cm EW (paper ~0.09, ~0.045). Unexplained.
- Lambda scan of eps_reco (`scripts/P20_lambda_scan.py`, `tables/lambda_scan_pooled.csv`, `tables/lambda_scan_combined_test.csv`;
  correlated chi2 with bootstrap): SCT z 580 chi2 238/10 and "exactly 2" 102/10 are rejected over the whole column;
  first crossing 33.1/10 (p 2.6e-4) and all crossings >= 2 47.3/10 (p 8e-7). Colored is consistent with both (p 0.17, 0.095);
  EW fails at low Lambda (2 keV: 0.63-0.67 vs 0.41; 1 keV: 0.20-0.23 vs 0.11).
- EW (gamma* - 1) reweighting (`scripts/D4_ew_gamma_reweight.py`, `tables/ew_gamma_reweight_test.csv`): eps_trig is flat in gamma* - 1
  (0.15-0.23 in 10 bins; Spearman with pT(QQ) 0.015), so no reweighting reaches 0.10; joint 6-point fits p <= 2e-4. EW work stops.

**Remaining differences (attributed to settings the paper does not state; not closable by code checks)**
- EW trigger 0.18 vs 0.10 (generator: matching, Pythia 6 vs 8, PDF, scales not stated; refs [25], [26]).
- EW eps_reco at low Lambda; Delta_w 2-5x larger than the paper's Fig. 5.
- Pile-up 4-of-8 rate ~6x the paper's ~1e-3, with and without the [34] material model.
- Hit-cut reading (first crossing vs all crossings >= 2) left to the supervisor; first crossing fits the Lambda column better.

## D10. Generator provenance of the production samples (2026-10-08, read from run banners and logs)
All four production samples were made with the SAME generator setup; MG5 2.3.3 was never used for a production sample.

| Sample | Run directory (/home/rafia/hep_tools/...) | MG5_aMC | Pythia | Events | Matching (from banner) | Momenta file used by the analysis |
|---|---|---|---|---|---|---|
| COL1000 | quirk_signal_1800gev_2kev/Events/run_01 | 3.7.3 | 8.317 | 1000 | MLM, ickkw = 1, xqcut = 30, JetMatching:qCut = 45, merge = on | 01_signal_generation/quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv |
| EW1000 | quirk_ew_800gev_4kev/Events/run_01 | 3.7.3 | 8.317 | 1000 | same | 01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv |
| COL2000 | quirk_2000_fresh_regen_runs/colored_1800GeV_L2keV/Events/run_fresh | 3.7.3 | 8.317 | 2000 | same | quirk_2000_event_fresh_regeneration_v1/events/colored_1800GeV_L2keV/trigger_passing_events.csv |
| EW2000 | quirk_2000_fresh_regen_runs/EW_800GeV_L4keV/Events/run_fresh | 3.7.3 | 8.317 | 2000 | same | quirk_2000_event_fresh_regeneration_v1/events/EW_800GeV_L4keV/trigger_passing_events.csv |

- Versions: `<generator name='MadGraph5_aMC@NLO' version='3.7.3'>` in each run banner; "This is PYTHIA version 8.317" in each tag_1_pythia8.log.
- HepMC hashes (2000 samples) equal generation_stats.json: COL b4b21771..., EW a703b339... . 1000 samples: COL c983da09..., EW d94c83d6... (sha256 prefixes).
- **MG5 2.3.3 + Pythia 8.212** were used ONLY in the trigger-variation pilot (EW eps_trig 0.167; see UNRESOLVED_DIFFERENCES.md U1), because the
  paper's LaTeX source names them in comments (quirks_prd_v2.tex lines 203-204: "%MG5 v2.3.3", "%Pythia 8.212").

**Pythia 6 hypothesis (ref. [26] = PYTHIA 6.4 manual).** The paper's text says "matched using \texttt{Pythia8}~\cite{Sjostrand:2006za,Sjostrand:2014zea}"
(TeX line 206). [26] is cited as a pair with the Pythia 8.2 introduction, which is the standard citation for Pythia 8. The same authors' ref. [34]
(arXiv:1612.00850, softbombs.tex line 291) uses the identical pair for "\texttt{Pythia 8.212}". Together with the "%Pythia 8.212" comment, the paper's
own source therefore indicates Pythia 8.212, not Pythia 6. A Pythia 6 run is not motivated by the documents and was not run.
**Question for the authors (still valid):** "Which Pythia version was used for the MLM matching (the source comments say 8.212), and with which
xqcut / qCut, PDF and scale settings?"
## D11. Pre-registered test: pile-up minimum-bias generator variants (written BEFORE the runs, 2026-10-08)
- **Source search first (done):** the paper's TeX comments (v1, v2 = latest) and the source of ref. [34] (softbombs.tex) contain no
  minimum-bias settings; [34] says only "minimum bias events generated with Pythia 8". Our pool: SoftQCD:nonDiffractive, default tune
  (Monash), 13 TeV, 20 000 events, Pythia 8.312 (paper: 125 000 events).
- **Runs:** `scripts/P22_pileup_minbias_variants.py`, identical to P21 REF34_Z580 except the pool (20 000 events, seed 20260916, `scripts/P22a_minbias_pool.py`):
  V1 = SoftQCD:inelastic, Monash; V2 = SoftQCD:nonDiffractive, Tune:pp = 5 (A2-CTEQ6L1).
  Check: the P22 code with the P21 pool must reproduce P21 chunk 0 (events 0-99).
- **Primary statistic (as D8):** fraction of the 5000 events whose selected Sec. III C plane (Delta_w < 1 cm) has >= 1 hit in >= 4 layers. Baseline (P21): 33/5000 = 6.6e-3.
- **Outcomes, fixed now (per variant):** rate <= 2e-3: explained by the minimum-bias generator setting. Otherwise: not explained, and the
  pile-up investigation stops.

### D11 result (appended after the runs; pre-registered text verified unchanged against notes/D11_prereg_sha256.txt)
**Step 1, paper source (arXiv tarball = v2; v1 and v2 TeX compared):**
- No xqcut, qCut, PDF, scale, SCT, smearing or minimum-bias setting in any comment. Comments found: "%MG5 v2.3.3", "%Pythia 8.212" (lines 203-204).
- A commented-out earlier Table I (lines 340-356): eps_trig EW **0.03**, colored **0.21**; eps_fid 0.27-0.28 per Lambda; eps_reco identical to the
  final table (colored 4 keV = 0.71 later commented out, 10 keV added). The trigger column changed between drafts; the reconstruction did not.
- Commented line 300: the background simulation "is somewhat more sophisticated than that for the signal, since energy loss in the detector
  material does tend to be significant for the fairly soft particles that comprise pile-up events" (signal and background detectors differ; supports scenario A).
- Line 338 (text): eps_reco drops at low Lambda "largely due to a stringent Delta_w requirement"; commented line 249: the trigger "biases the sample
  towards relatively narrow strips (small Delta_w)".
- v1 vs v2: wording only; Table I, Sec. III C and Sec. IV cuts identical; v2 adds the "(Delta_w)^2" summary list.
- Fig. 5 from the vector source figures (Deltat.pdf, Deltaw.pdf; `scripts/S1_fig5_vector_extract.py`, `tables/paper_fig5_vector.json`; axis residual <= 0.002 dex):
  identical bin by bin to the digitisation used so far (difference 0). Signal fraction above Delta_s = 0.01 cm: colored 0.101, EW 0.084.
- Ref. [34] source: "minimum bias events generated with Pythia 8", no further settings.

**Step 2, minimum-bias variants** (`scripts/P22a_minbias_pool.py`, `scripts/P22_pileup_minbias_variants.py`, `logs/P22_chunks_*`; pools in 02_backgrounds/pileup/,
20 000 events, Pythia 8.312). Check: P22 code with the P21 pool reproduces P21 events 0-99 exactly. A PicklingError stopped the first launch
before any event; fixed by a local wrapper (no change to the physics), logged in logs/P22.log.

| Pool | 4/8 rate (primary) | 8/8 | Signal region | Hits L1 / L8 (median) |
|---|---|---|---|---|
| Baseline: nonDiffractive, Monash (P21) | 33/5000 = 6.6e-3 [4.7e-3, 9.3e-3] | 1 | 0 | 1666 / 467 |
| V1: inelastic, Monash | 12/5000 = 2.4e-3 [1.4e-3, 4.2e-3] | 0 | 0 | 1331 / 372 |
| V2: nonDiffractive, A2 | 35/5000 = 7.0e-3 [5.0e-3, 9.7e-3] | 0 | 0 | 1721 / 486 |

- **Verdict by the pre-registered criterion (<= 2e-3): not explained by either variant. Pile-up investigation stops.**
- Observation (not a change of the criterion): V1 lowers the rate by ~2.8x with ~20% fewer hits per layer, and the paper's ~1e-3 lies just below
  its Wilson interval. The minimum-bias generator choice is the largest pile-up lever found; the paper does not state it.
- Pools not committed (size); sha256:
  - 786e572a61e544b8925ae84061d42cead5476c9ee983c2431e15126fdcb9378f  02_backgrounds/pileup/minbias_pool_20000_MB_INEL_MONASH_v1.csv
  - ffa5aa38768274105f9cfdaeecf022b6315deecb1b56275b616298683316bf58  02_backgrounds/pileup/minbias_pool_20000_MB_ND_A2_v1.csv
- Reproducibility (2026-10-08): both pools regenerated from scratch with `scripts/P22a_minbias_pool.py` settings (seed 20260916, Pythia 8.312,
  PYTHIA8DATA = hep env xmldoc) are byte-identical to the stored files (sha256 786e572a... and ffa5aa38...). A backup is therefore not needed;
  the script, seed and Pythia version recreate them.
- Exact Fig. 5 medians (vector source, log-interpolated in the median bin): Delta_s colored 31.9 um, EW 28.1 um; Delta_w colored 0.0921 cm,
  EW 0.0484 cm. Ours (no SCT z smear, plane + hit cut, first / all crossings): Delta_s 37.7 / 38.2 um and 44.1 / 44.5 um; Delta_w 0.482 / 0.490 cm
  and 0.097 / 0.097 cm. Delta_w ratio ours/paper: colored 5.2, EW 2.0; with 0.5 sqrt(lambda_2): colored 2.6, EW 1.0.

## D12. Two follow-up checks (2026-10-08, existing data and published versions only)
**Colored Delta_w vs Lambda** (`tables/lambda_scan_per_event.csv`, COL1000 + COL2000, no SCT z smear, plane + hit cut; median [16th-84th percentile]):
| Lambda | first crossing | all crossings >= 2 | ratio to paper 0.0921 cm |
|---|---|---|---|
| 1 keV | 0.365 (N 3) | 0.515 (N 4) | 4.0-5.6 |
| 2 keV | 0.352 [0.143-0.542] (N 13) | 0.382 [0.168-0.603] (N 16) | 3.8-4.1 |
| 3 keV | 0.218 (N 23) | 0.218 (N 21) | 2.4 |
| 5 keV | 0.100 [0.039-0.209] (N 26) | 0.101 [0.042-0.203] (N 23) | 1.1 |
| 10 keV | 0.047 (N 15) | 0.038 (N 12) | 0.4-0.5 |
- The paper's colored 0.0921 cm is reached at Lambda ~ 5.3 keV (log interpolation between 3 and 5 keV), not at the labelled 2 keV.
  The pooled 2 keV ratio is 3.8-4.1 (the earlier 5.2 used COL2000 only, N 8-11).
- Same check for EW (paper 0.0484 cm, labelled 4 keV): ours 0.102-0.105 at 4 keV, 0.073-0.084 at 5 keV; match extrapolated at ~6.6 keV.
- A single relabelling does not fit both (colored needs x2.6 in Lambda, EW x1.65), and the eps_reco(Lambda) shift goes the other way
  (paper loses MORE events at low Lambda). Colored Delta_w stays unexplained.
**Printed Table I in every version:** arXiv v1 PDF (7 Aug 2017, fetched, sha256 b6097157...) and v2 PDF (13 Nov 2017) both print EW eps_trig 0.10,
colored 0.24, eps_fid 0.28 and identical eps_reco; v1 TeX prints the same (0.03 / 0.21 appear only in the commented-out draft table in both v1 and v2).
PRD 96, 115015: received 20 Sep 2017, published 19 Dec 2017; no erratum listed by APS or INSPIRE. The journal PDF itself was not accessible
(paywall); v2 ("minor changes", after the journal received the paper) is the latest version we can read.
=> 0.03 -> 0.10 happened before the first public version, not after refereeing.

## D13. EW trigger: quirk-pair momentum level (2026-10-09; observation + hypothesis, test not yet run)
**Observation** (`scripts/D5_trigger_pair_definition.py`, `tables/trigger_pair_definition.csv`, read directly from the 2000-event HepMC files):
- The analysis builds the pair from the final-state particles: EW status-1 |pdg| = 9000011; colored status-1 R-hadrons (1800 +- 30 GeV).
  This reproduces every stored trigger decision (EW 1045/1045, colored 873/873) and agrees with a MET-like recoil of the visible particles.
- eps_trig by pair definition (paper: EW 0.10, colored 0.24):

| Definition | EW | Colored |
|---|---|---|
| final-state pair, after the parton shower (analysis) | 186/1045 = 0.178 (p = 1.8e-14) | 207/873 = 0.237 (p = 0.87) |
| MET-like recoil of visible particles | 187/1045 = 0.179 | 206/873 = 0.236 |
| hard-process pair (status 23), before the parton shower | 121/1045 = 0.116 (p = 0.089) | 138/873 = 0.158 (p = 3.9e-9) |

- Before the shower, 0-jet matrix-element events have pT(QQ) ~ 0 (EW 471/1045, colored 330/873).
- No single definition reproduces both samples.

**Hypothesis (not confirmed):** the paper applied the pT > 200 GeV cut to the EW quirk pair before the parton shower (matrix-element / LHE level).
It explains the EW 0.10 but would lower the colored efficiency to 0.16, so it would require different treatments of the two samples.

**Conditions for the test (to be fixed in a pre-registration before any run):**
1. Denominators: with the 121 hard-level triggered EW events, eps_fid = N(fiducial) / 121 and eps_reco = N(signal region) / N(fiducial among the 121).
   Comparisons with the 186-event (shower-level) sample must use these denominators explicitly.
2. Two effects recorded separately: (a) the trigger-cut level (which events are selected), with the trajectories always started from the
   shower-level final-state momenta; (b) a change of the trajectory input momenta (hard-level vs shower-level), if tested, as a separate configuration.
3. Wording: a favourable result is reported as "hypothesis supported", never "confirmed", unless the paper or the authors verify the implementation.
- Question for the authors: "Was the pT > 200 GeV cut applied to the quirk pair before or after the parton shower, and in the same way for both samples?"
### D13 summary and pre-registered test (written BEFORE the run, 2026-10-09)
- **Established:** the particle selection is correct (stored trigger decisions reproduced 1045/1045 EW and 873/873 colored), and the three
  definitions give the eps_trig numbers in the D13 table above.
- **Hypothesis (label: hypothesis):** the paper used the matrix-element (LHE-level, before the parton shower) quirk momenta for EW and the Pythia
  output (after the shower) for colored. If so, the EW trajectories also started from the pre-shower momenta.
- **Test** (`scripts/P23_ew_hard_momenta.py`): the EW2000 events whose pre-shower pair has pT > 200 GeV (121 of 1045). Full pipeline: fiducial
  (Ref. [27] lengths, t < 25 ns), then eps_reco at Lambda = 1, 2, 4 keV, SCT z not smeared, one hit per quirk per layer.
  - Column H (test): trajectories from the pre-shower (status-23) quirk momenta.
  - Column S (control): the same 121 events, trajectories from the after-shower final-state momenta.
  - Both columns use identical beam-spot and SCT R-phi random draws per event (SeedSequence([23, hepmc_event_index])), so H - S isolates the
    momentum effect and S - (186-event reference) the selection effect.
  - Denominators: eps_fid = N(fiducial) / 121; eps_reco = N(signal region) / N(fiducial) within each column.
- **Reference (current, after-shower trigger, 186 events):** eps_fid = 62/186 = 0.333; eps_reco(2 keV) = 40/62 = 0.645 (1 keV 12/62, 4 keV 50/62).
- **Criteria, fixed now (applied to column H; "toward the paper" = at least half of the gap closed):**
  - fiducial condition: eps_fid(H) <= 0.307 (half way from 0.333 to the paper's 0.28);
  - low-Lambda condition: eps_reco(H, 2 keV) <= 0.53 (half way from 0.645 to the paper's 0.41).
  - **Supported:** both conditions met. **Rejected:** neither met. **Partial:** one met.
  - Attribution: a condition counts for the momentum effect only if column S does not meet it as well; otherwise the change is due to the
    event selection.
- Point estimates are used; with ~121 events the fiducial fraction has a statistical spread of about +-0.04, so Wilson 95% intervals are
  reported next to every number. A supported result will be written as "hypothesis supported", not "confirmed". The draft value 0.03 is not
  part of this test. This is the last EW test.

## D14. Result of the D13 test: EW trajectories from pre-shower momenta (2026-10-09; pre-registered text verified unchanged against notes/D13_prereg_sha256.txt)
- **Run:** `scripts/P23_ew_hard_momenta.py`, `logs/P23_events.jsonl`, `tables/ew_hard_momenta_test.csv`; 121 events (pre-shower pT(QQ) > 200 GeV;
  114 of them also pass the after-shower trigger), exit 0. 2 events in column S (HepMC index 655, 992) stopped with a numerical error and count as not fiducial.

| | Column H (pre-shower momenta) | Column S (same events, after-shower momenta) | Reference (186 after-shower triggered events) | Paper |
|---|---|---|---|---|
| eps_fid | 44/121 = 0.364 [0.283, 0.452] | 48/121 = 0.397 [0.314, 0.486] | 62/186 = 0.333 | 0.28 |
| eps_reco 1 keV | 8/43 = 0.19 [0.10, 0.33] | 10/48 = 0.21 [0.12, 0.34] | 12/62 = 0.19 | 0.11 |
| eps_reco 2 keV | 26/44 = 0.59 [0.44, 0.72] | 35/48 = 0.73 [0.59, 0.83] | 40/62 = 0.65 | 0.41 |
| eps_reco 4 keV | 33/44 = 0.75 [0.61, 0.85] | 40/48 = 0.83 [0.70, 0.91] | 50/62 = 0.81 | 0.72 |

(1 keV fiducial in column H: 43, since the fiducial flag is recomputed per Lambda.)
- **Verdict by the pre-registered criteria: REJECTED.** Fiducial condition (<= 0.307): not met (0.364, further from the paper than the reference).
  Low-Lambda condition (eps_reco 2 keV <= 0.53): not met (0.59).
- Observation (not a change of the verdict): at fixed events, the pre-shower momenta lower eps_reco by 0.08-0.14 (H vs S), i.e. in the
  direction of the paper, but not enough; the selection itself (S vs reference) raises eps_fid and eps_reco(2 keV).
- **Conclusion:** the pre-shower-momentum hypothesis explains only the EW trigger number; it does not explain the EW fiducial or low-Lambda
  differences. The trigger match (0.116 vs 0.10) is therefore treated as a possible coincidence. **EW investigation closed.**

## D15. Sensitivity (requested 2026-10-09, written before the run): D13/D14 test repeated with SCT z 1.16 mm
- Same 121 events, columns H and S, same random draws (the stored SCT z normals now multiply 1.16 mm); everything else as P23.
- Descriptive only: no new criterion, and the D14 verdict (EW investigation closed) is not reopened by this run.
- The trigger efficiency does not depend on the SCT z setting (cut on generator momenta before the detector simulation): EW 121/1045 before
  and 186/1045 after the shower; colored 138/873 and 207/873.
### D15 result (`scripts/P23b_ew_hard_momenta_z1160.py`, `tables/ew_hard_momenta_test_z1160.csv`, exit 0)
| SCT z | Column | eps_fid | eps_reco 1 keV | eps_reco 2 keV | eps_reco 4 keV |
|---|---|---|---|---|---|
| none | H (pre-shower) | 44/121 = 0.36 | 8/43 = 0.19 | 26/44 = 0.59 | 33/44 = 0.75 |
| none | S (after shower) | 48/121 = 0.40 | 10/48 = 0.21 | 35/48 = 0.73 | 40/48 = 0.83 |
| 1.16 mm | H (pre-shower) | 44/121 = 0.36 | 0/43 = 0.00 | 1/44 = 0.02 | 3/44 = 0.07 |
| 1.16 mm | S (after shower) | 48/121 = 0.40 | 0/48 = 0.00 | 4/48 = 0.08 | 7/48 = 0.15 |
| 1.16 mm | 186-event reference | 62/186 = 0.33 | 2/62 = 0.03 | 8/62 = 0.13 | 10/62 = 0.16 |
| paper | | 0.28 | 0.11 | 0.41 | 0.72 |
- Fiducial is unchanged by the SCT z setting, as expected. With 1.16 mm, eps_reco collapses for both momentum choices (4 keV: 0.07 and 0.15 vs 0.72),
  so pre-shower momenta do not rescue the paper-text resolution. EW investigation stays closed.

## D16. Report revision 2026-10-09 (TABLE_I_REPRODUCTION_REPORT_2026-10-09.pdf, `scripts/R_report_2026-10-09.py`)
- Rule applied: every statement is either from the paper or our measurement; speculative explanations removed; settings the paper does not
  state are listed as "not stated; our choice". Tables with k/n, Wilson 95% and p precede every graph; each graph has a plain-language note.
- PDF corrected to nn23lo1 = LHAPDF 247000 (LHE init block and MG5 3.7.3 banner.py mapping; the run-card lhaid 230000 is inactive with pdlabel = nn23lo1).
- Combined Lambda-column test for the report scope (2000-event samples): `scripts/D3b_lambda_combined_test_2000.py`, `tables/lambda_scan_combined_test_2000.csv`.
- Fig. 3 numbers in the report come from `scripts/F28_fig3_velocity_plane.py` (reference plane at the first point with r > 0.05 cm): colored 0.19e-3
  (paper at our 9th percentile), EW 0.52e-3 (39th). The D9 values 0.22e-3 / 0.46e-3 (14th / 37th) used `scripts/D2_dphi_estimators.py` with the
  reference at r > 0.5 cm. Same definition (velocity-vector plane), different reference point; the report uses F28 throughout.

## D17. Fig. 2: |L| near zero at every second closest approach (2026-10-09)
- Paper (Sec. II): "whenever |L| = 0, the separation between the quirks is large". Our Fig. 2 event (COL2000 key 35) has |L| ~ 0 at every second
  minimum of d.
- Step-size test (same event; 300 / 3000 / 30000 steps per period): |L| at the large-L approaches converged (7.98e11 hbar); at the small-L approaches
  5.0e8 / 8.6e8 / 5.6e7 hbar (not converged, drops with resolution); d_min shrinks with resolution at every approach (sampling-limited).
- All 22 COL2000 fiducial events, 3000 steps per period (`scripts/D6_fig2_angular_momentum_check.py`, `tables/fig2_L_check.csv`):
  132 of 276 closest approaches (every event) have |L| < 1% of the event's |L|max; smallest |L| at an approach 4.5e6 hbar (not converged).
- Torque test: |L(t)| agrees with the paper's Eq. 5 mechanism, L_pred = q (integral of d dt) x E_cm with E_cm = gamma (v_cm x B):
  maximum relative deviation median 0.11 over the 22 events (max 0.61).
- No code error found; the alternating pattern follows from the equations used (Eq. 3 with the Lorentz force). The difference to the paper's
  Fig. 2 and statement is recorded as unexplained. Annihilation is not modelled (neither in the paper).
### D17 follow-up (2026-10-09): three checks on the Fig. 2 event (COL2000 key 35, 3000 steps per period)
1. Spacing of closest approaches in r: predicted from the event's own kinematics (gamma* = 1.2172, v* = 0.5701, beta_cm,T = 0.0724, gamma_cm = 1.0028;
   Eq. 4 period x lab dilation x beta_T) 0.895 cm = measured 0.895 cm. With the 3D distance instead of the transverse r: 0.929 vs 0.930 cm.
   The paper's 1.155 cm with its d max 3.56 cm needs beta*gamma(CM) = 0.098 (ours 0.073): a different event, not a definition error.
   Over the 22 colored fiducial events the spacing ranges 0.42-3.18 cm (median 1.36), d max 0.95-6.38 cm (median 2.79).
2. |L| definition: |d x (p1* - p2*)/2| equals |sum (x_i - x_cm) x p_i| to 5e-11 of |L|max; |L|(t = 0) = 0; units GeV^-1 x GeV = hbar.
3. The alternation is in the momenta: at closest approaches with |L| = 7.98e11 hbar the transverse relative momentum is 6.7 / 8.8 / 41.6 GeV;
   at the other two it is 0.014 / 0.033 GeV. At every turning point (d max) p_perp = 0.002 GeV and |L| = 3.27-3.28e11 hbar (= d x p_perp).
   This matches the torque picture of Eq. 5 (L proportional to the integral of d dt). The paper's |L| minima at large d remain unexplained.

## D18. Reply from the authors (received 2026-10-10, relayed by the user; verbatim)
> "The detector resolutions were taken as in the experimental paper we cite. For the signal, we matched madgraph with pythia up to one jet, to get a
> realistic ISR spectrum. Fig 5 is before applying the \Delta s and \Delta w cuts, as those are the quantities plotted."
**What this settles**
- Resolutions follow the cited experimental paper (Ref. [27]: 17 um R-phi, 580 um z per SCT module). This does NOT support "no SCT z smearing" as the
  authors' implementation; that setting stays only as the reading that reproduces the paper's numbers. Whether the factor 2 of the paper's text was
  applied (and to which coordinate) is not stated in the reply.
- Generator: MLM matching of MadGraph with Pythia, up to one jet, for a realistic ISR spectrum (our setup). Settings (xqcut, qCut, PDF, scales) not given.
  The pT(QQ) > 200 GeV trigger on the ISR-recoiling pair after the shower is consistent with this; the pre-shower definition (D13-D14, rejected) is further disfavoured.
- Fig. 5 population: before the Delta_s and Delta_w cuts. Our Fig. 5 used plane + hit multiplicity with Delta_w < 1 cm inside the plane selection;
  whether the hit-multiplicity cut is applied in Fig. 5 is not stated.
**Check with existing data (2000-event samples, first crossing):** signal Delta_s median (plane found / plane + hit cut) and eps_reco:
| SCT z | colored Delta_s | colored eps_reco | EW Delta_s | EW eps_reco |
|---|---|---|---|---|
| none | 38 / 38 um | 8/22 = 0.36 | 43 / 44 um | 50/62 = 0.81 |
| 580 um (Ref. [27]) | 184 / 176 um | 3/22 = 0.14 (p = 0.042) | 149 / 127 um | 14/62 = 0.23 (p = 1e-15) |
| 1.16 mm | 169 / 160 um | 1/22 = 0.05 | 160 / 110 um | 10/62 = 0.16 |
| paper | 32 um (Fig. 5) | 0.35 | 28 um (Fig. 5) | 0.72 |
With the resolutions the authors confirm, our signal Delta_s is 4-6x the paper's Fig. 5 and eps_reco is far below Table I. This is now an open
discrepancy between our simulation with the authors' stated resolution and their published results.
### D18 follow-up (2026-10-11): Fig. 5 signal with the authors' population (`scripts/P24_fig5_population_author.py`, `tables/fig5_author_population.csv`,
`FINAL_FIGURES/F32_fig5_author_population`)
- Smallest-Delta_s plane without the final Delta_w < 1 cm cut (Sec. III C seed cuts and factor-3 rule kept): no event has Delta_w >= 1 cm in any setting,
  so the population equals "plane found". Check: the Delta_w < 1 selection reproduces all_crossings_per_event.csv (0 mismatches).
- Signal medians, plane found (no hit cut): colored Delta_s 38 / 184 / 169 um, EW 43 / 149 / 160 um for SCT z none / 580 um / 1.16 mm (paper 32, 28 um);
  Delta_w colored 0.498 / 0.498 / 0.495 cm, EW 0.096 / 0.096 / 0.099 cm (paper 0.092, 0.048 cm). Delta_w does not depend on the SCT z setting.
- The Fig. 5 population does not explain the Delta_s difference at the authors' resolution.

## D19. Fig. 2 v3 (2026-10-11): `scripts/F33_fig2_v3.py`, `FINAL_FIGURES/F33_fig2_v3`
- Exact CM frame, 3000 steps per period, paper's axes; panels: paper (vector figure), key 35 (median |L|max, fixed rule), key 8 (charged triggered colored
  event with d max and spacing nearest the paper's event, chosen from kinematics only: d max 4.19 cm, spacing 1.05 cm; paper 3.56, 1.155 cm).
- At successive closest approaches |L| alternates high/low in all three: paper 0.67 / 0.20 / 0.53 / 0.29 e12; key 35 0.80 / ~0 / 0.80 / ~0 / 0.80 e12;
  key 8 0.86 / ~0 / 0.86 / ~0 e12. Paper's |L| touches zero between closest approaches (r = 1.91, 2.67, 4.10 cm, near turning points); ours touches
  zero at the low closest approaches. Unexplained (D17 and notes/D7_problem2_findings.md).

## D20. Fig. 2 with a constructed event of the paper's kinematics (2026-10-11): `scripts/D8_fig2_toy_event.py`, `tables/D8_fig2_toy*.csv`, `FINAL_FIGURES/F34_fig2_v4`
- Constructed event: v* = 0.556, CM transverse speed 0.0975 along x, production at the origin, 1800 GeV, 2 keV, B = 2 T, 3000 steps per period.
  d max 3.61 cm, spacing 1.16 cm (paper 3.56, 1.155): matched by construction.
- Charges +-2/3 (bare quirk): first |L| peak 0.64e12 (paper 0.65e12); +-1: 0.96e12. Oscillation axis along x or z: same result; along y (parallel to E_cm): L = 0.
- Later peaks 0 / 0.64 / 0 e12 vs paper 0.19 / 0.52 / 0.29 e12; |L| = 0 at the low closest approaches (r = 2.33, 4.65 cm) instead of at large d.
- Centre-of-energy L in the lab agrees with our CM-frame L to <= 5% (axis x) and exactly (axis z).
- Note on the pasted review: the plot it describes (v* = 0.6, beta = 0.3, d max 4.44 cm, first peak 2.9e12) is not one of ours; our Fig. 2 panels use
  simulated events (key 35: v* 0.570, beta_T 0.072).
- Question for the authors: "In Fig. 2, about which point and in which frame is L computed, and what were the event's charges and initial momenta?"

## D21. Fig. 2 follow-up checks (2026-10-11)
1. Simulated event COL2000 key 8 (panel 3): |L| at closest approaches 0.86 / ~0 / 0.86 / ~0 e12 hbar, same pattern as the constructed event.
   The pattern is therefore not a consequence of the constructed event being too simple.
2. Correction of D20 wording: the first peak 0.64e12 is consistent with charges +-2/3, but charge and oscillation direction cannot be separated:
   charges +-1 with the axis tilted 48.2 deg from z towards y, and charges (+1, -1/3) with the axis along z, also give 0.64e12 (all with 0 at the second approach).
3. Signed-slope test on the paper's own curves (`scripts/D9_fig2_signed_slope.py`, `tables/D9_fig2_signed_slope.csv`): fit dL_s/dr = (a*sigma_k + b)*d with
   sigma_k alternating per arch of d. Paper: a = 0.28, b/a = -0.06 (per-arch ratios +0.27 / -0.29 / +0.27 / -0.29 / +0.31). Our constructed event: a = 0.22,
   b/a = -0.003. Integrating the paper's fit on the paper's d curve gives |L| at approaches 0.71 / 0.09 / 0.62 / 0.19 with zeros at r = 2.06 / 2.57 / 4.25
   (paper 0.65 / 0.19 / 0.52 / 0.29; 1.91 / 2.67 / 4.10); with b = 0: 0.76 / 0 / 0.76 / 0. Measured: the paper's L contains a small torque component
   (about 6-10% of the alternating one) that does not change sign; ours does not. Its origin is not given by the paper.
- Fig. 2 for the report: `FINAL_FIGURES/F34_fig2_v4` (panels labelled PAPER / CONSTRUCTED / SIMULATED).

## D22. Baseline vs fast integrator (2026-10-11): `scripts/D10_integrator_baseline_vs_v2.py`
- Same initial conditions, parameters and dt (constructed Fig. 2 event, 3000 steps per period, 119 881 steps): t identical bit for bit; x and p NOT bit-for-bit
  identical (~88% of elements differ in the last digits): max relative difference 4.1e-9 (x), 2.3e-10 (p); max |dx| = 0.034 GeV^-1 = 6.8e-16 cm.
  The docstring of quirk_trajectory_optimized_v2.py ("bit-for-bit") does not hold for this run; the differences are floating-point rounding.
- CM-frame L(t): max |difference| 0.86 hbar out of |L|max 6.4e11 (1.3e-12 relative). Runtime: baseline 27.3 s, v2 3.0 s (median of 3; 9.0x faster).
- The optimisation does not change the physics model or the initial conditions, so it is not the source of the Fig. 2 difference.

## D23. Fig. 2: further checks of the |L| pattern (2026-10-12)
1. L definition (constructed event, axes x / z, charges +-2/3, `scratchpad` check, no new files): lab-frame d x (p1 - p2)/2 at equal lab time, lab centre of
   energy, and lab about the production point (axis z) all give |L| at closest approaches 0.64 / 0 / 0.64 / 0 e12 hbar, as the CM frame does.
   (About the production point with axis x |L| grows with r: 0.14 / 0.40 / 1.34 / 1.82; not the paper's shape either.)
2. Charge assignments x axes (`scripts/D15_fig2_charge_axis_scan.py`, `tables/D15_fig2_charge_axis_scan.txt`): charges (+-2/3), (+-1), (+1, 0), (0, -1),
   (+1, -1/3), (+2/3, -1/3), (+-1/3); axes x, y, z, xz 45 deg, yz 45 deg. Every case with nonzero L has |L| = 0.00 at the 2nd and 4th closest approach;
   the first peak scales with (q1 - q2)/2 and with the axis component perpendicular to E_cm. Unequal charges do not produce the paper's non-reversing part.
3. Conclusion: within Eq. 3 plus the Lorentz force, the frame of L, the charges and the oscillation axis do not produce the paper's |L| values at the 2nd/4th
   approach (0.19 / 0.29 e12). The paper's curves need a torque component of about 6% that does not change sign (D21); its source is not stated by the paper.
   No parameter is adjusted to force agreement. Open question for the authors (D20).

## D24. Fig. 2: four checks (2026-10-12): `scripts/D16_fig2_four_checks.py`, `tables/D16_fig2_four_checks.txt`
1. Paper curves, parabolic minima on each curve's own points: d minima at r = 1.161 / 2.314 / 3.467 / 4.620 cm (d = 0.05-0.11 cm); |L| there
   0.645 / 0.194 / 0.514 / 0.287 e12 hbar. |L| minima at r = 1.909 / 2.664 / 4.105 cm (|L| 0.013-0.018), where d = 3.19 / 3.01 / 3.50 cm (near the d maxima).
   Signed per half-oscillation (sign flipped at each |L| zero): dL = +0.645 / -0.839 / +0.708 / -0.801, i.e. the negative half-oscillations are ~20% larger.
2. Implementation: magnetic force of the integrator's right-hand side = q v x B with B along +z (checked numerically). Constructed event: p1* + p2* = 0,
   |v*| = 0.556 both, v_cm = (0.0975, 0, 0), charges +-2/3, d max 3.612 cm (energy conservation 3.607). Key 8: |v*| = 0.5876 both, |v_cm,T| = 0.0808,
   charges +-1, d max 4.196 cm (4.188). (Key 8: the CSV energies are 2.7e-4 / 1.8e-4 above on-shell for m = 1800 GeV; the code uses on-shell E.)
3. Signed L: L stays along one fixed axis (constructed: angle 0 deg; key 8: <= 0.65 deg); the projection goes from 0 to +|L|max and back to 0
   (min -0.001 to -0.002 of |L|max): L touches zero, it does not change sign.
4. Torque per half-oscillation (projection on that axis): dL(trajectory) +0.643 / -0.643 / +0.643 / -0.643 / +0.644 (key 8: +-0.862);
   exact CM-frame electromagnetic torque integral +-0.556 (key 8 +-0.731), identical to the paper's form q d x E_cm. The trajectory's dL is 16% (18%)
   larger than the electromagnetic torque; this extra part also alternates in sign (it is from the remaining force, i.e. the string force as
   implemented in the lab frame; not further decomposed). Every part cancels over two half-oscillations to <= 1e-3 of |L|max.
   Result: the cancellation follows from the equations as implemented, not from a sign or frame error. The paper's curves have unequal
   alternate half-oscillations (item 1), which our trajectories (equal half-oscillations) do not produce.

## D25. Fig. 2 torque decomposition (2026-10-12): `scripts/D17_fig2_torque_decomposition.py`, `tables/D17_fig2_torque_decomposition.txt`
Forces from the integrator's own right-hand side (string only: B = 0; electromagnetic only: Lambda = 0); L about the centre of energy;
dL = int tau_EM + int tau_string - int (dX/dt x P) + residual, per half-oscillation (projection on the L axis, 1e12 hbar).
- Constructed event (CM frame = lab result here): dL +0.6434 / -0.6430 / +0.6426 / -0.6429 = EM +-0.556 + string +-0.087 + frame 0; residual <= 9e-5.
  Key 8, CM frame (Fig. 2 definition): dL +-0.862 = EM +-0.731 + string +-0.131; residual <= 5e-4. string/EM = 0.156 (constructed), 0.179 (key 8), same sign as EM
  in every half-oscillation. (Key 8 in the lab frame: large opposite string and frame terms, +-620, because the pair has net momentum; their sum closes.)
- Check: the integrator's EM force transformed to the CM frame equals q(E* + v* x B*) to 6e-16.
- Origin of the string torque: in the CM frame the implemented string force deviates from the CM separation line by median 5.7e-6 deg (1.0e-7 rad;
  key 8 4.8e-5 deg). With the string force ~1e6 times the EM force, this angle gives the 16-18%. The integrator applies Eq. 3 in the lab frame with the
  separation at equal lab time; the paper states the straight-string limit "in the center of mass frame". Which of the two (simultaneity or the
  v_par v_perp term of Eq. 3 in the lab) produces the angle is not separated here.
- The extra term alternates with the EM term, so it changes the size of the |L| peaks by ~16-18% but not the pattern (zero at every second approach).

## D26. Fig. 2 string torque at B = 0 (2026-10-12): `scripts/D18_fig2_B0_string_test.py`, `tables/D18_fig2_B0_string_test.txt`
Constructed event (v* = 0.556, 1800 GeV, 2 keV), B = 0, initial L0 = 0.5e12 hbar from a 0.08 um offset along y (perpendicular to motion and boost),
v_cm = 0 / 0.0975 / 0.3 along x; quirk L in the initial CM frame at equal CM time about the centre of energy.
- In all three runs L/L0 = 0.8312 at every turning point (d max) and 1.000 at every closest approach (1/gamma* = 0.8312). L keeps its direction.
- The variation does not depend on v_cm (0.831205 / 0.831201 / 0.831202 at the first turning point); with v_cm the values at closest approach
  drift by <= 5e-4 over 8 approaches (v_cm = 0: <= 1.7e-4).
- Result: the string torque of D25 is not a lab-frame / simultaneity effect. It is the non-central v_par v_perp term of Eq. 3 (the string carries
  part of the angular momentum); it is present at v_cm = 0 and is part of the paper's equation of motion. The quirk L plotted in Fig. 2 therefore
  depends on whether the string's share is included; the paper does not say which L it plots.

## D27. Recheck of the equations in the simulation (2026-10-12): `scripts/D19_eom_recheck.py`, `tables/D19_eom_recheck.txt`
1. Paper Eq. 3 written literally (v_par = v.s signed, s from the partner to the quirk) vs the integrator's _rhs at 2000 random states: max difference 9e-16 Lambda^2.
2. Lorentz force = q v x B (B along +z); e = sqrt(4 pi alpha) = 0.302822 (code 0.30282212); 1 T = 1.95353e-16 GeV^2 (code 1.9535e-16, 1.5e-5 rounding).
3. Gyroradius (p_T 50 GeV, 2 T): 83.391 m expected, simulated within 1.2 mm (1.4e-5, the constant's rounding).
4. Eq. 4 (B = 0, v = 0.556): d/2 = d_cm(t) to 4e-11 of the amplitude over two periods; boosted (v_cm = 0.3, CM frame): 1e-4.
5. Energy E1 + E2 + Lambda^2 d: constant to 7e-12 (median); 7e-5 only at the single step where the quirks cross (d = 0, force direction flips).
6. Fig. 2 event, 3000 vs 6000 steps/period: |L| at closest approaches 0.6434/0.0004/0.6430/0.0001 vs 0.6435/0.0002/0.6433/0.0003.
No error found. Not tested here: material effects (not in the code; the paper does not state them for Fig. 2).

## D28. Fig. 2: scan of the possibilities behind the three author questions (2026-10-12)
`scripts/D20_fig2_possibilities.py` (`tables/D20_fig2_possibilities.txt`), `scripts/D21_fig2_cm_frame_integration.py` (`tables/D21_fig2_cm_frame_integration.txt`).
Metric: |L| at closest approaches 1-4 and ratio |L(2nd)|/|L(1st)|; paper 0.645 / 0.194 / 0.514 / 0.287, ratio 0.30.
- Q1 definition of L (base trajectory): CM equal time; non-relativistic m v; lab midpoint; lab centre of energy; about the production point;
  vs r of quirk 1; total L of quirks + string (integral of the EM torque, 0.556). All: second approach 0.000 (ratio 0.001).
- Q2 charges and initial momenta: 60 random configurations (isotropic axis, random transverse CM direction, longitudinal CM speed 0-0.5,
  charges +-2/3, +-1, (+1, 0), (+1, -1/3)): ratio median 0.0004, max 0.0012.
- Q3 equation of motion (own RK4, C0 reproduces the production result 0.643 / 0.000): without the v_par v_perp term 0.643 / 0.000; constant string
  force 0.636 / 0.000; non-relativistic 0.631 / 0.000; B x gamma_cm 0.646 / 0.000; RK4 300 steps 0.643 / 0.005 / 0.640 / 0.006.
  Forward Euler: 3000 steps 0.650 / 0.008 / 0.670 / 0.016; 300 steps 0.700 / 0.075 / 0.869 / 0.170 with d max growing to 4.21 cm (energy not
  conserved). This is the only variant with |L| != 0 at the 2nd approach, but its peaks and d max grow, while the paper's d max is constant
  (3.556 in every arch) and its peaks decrease.
- CM-frame integration (E* = gamma v_cm x B, B* = gamma B): full Eq. 3 gives 0.6434 in the CM frame and 0.6434 in the lab frame (D26 confirmed:
  the 16% string share is physical and frame independent). Without the v_par v_perp term: 0.556 in the CM frame vs 0.643 in the lab frame,
  i.e. that truncated equation is frame dependent; the D20 C1 result (0.643) is a lab-frame effect of the truncated equation.
- Result: none of the tested definitions, charge / momentum configurations or equation-of-motion variants with conserved energy gives the
  paper's pattern. The three questions to the authors remain open.

## D29. Fig. 2: |L| at the "L = 0" closest approaches in units of hbar (annihilation question, 2026-10-12)
`scripts/D22_fig2_L_residual_annihilation.py`, `tables/D22_fig2_L_residual_annihilation.txt`. Constructed event, production integrator; signed L
interpolated to the time of minimum d. 2nd / 4th closest approach: 3000 steps/period +4.2e8 / +1.3e8 hbar; 10000: -5.9e6 / -2.4e7; 30000: +5.5e7 / +5.8e7;
100000: +5.5e6 / +2.1e6 hbar (1st / 3rd: 6.435e11, stable). Not converged (sign and size change with step size): the classical value is below
~1e-5 of the peak and cannot be resolved further with this integrator; a value of order hbar is not excluded.
- Paper (Sec. II): "whenever |L| = 0, the separation between the quirks is large, and annihilation is suppressed by a small wave-function
  overlap". In our trajectories (paper's Eq. 3 + Lorentz force) |L| is minimal exactly at every second closest approach, so this protection
  is not present there. Annihilation is simulated neither in the paper nor here; Table I assumes no annihilation.

## D30. Fig. 2 test with the pair simulator supplied by the user (2026-10-12): `scripts/D23_fig2_external_simulator_test.py`,
`tables/D23_fig2_external_simulator_test.txt`, `FINAL_FIGURES/F35_fig2_external_sim_test/`
Supplied code (simulate_quirk_pair_tracks; mm, ns, GeV, T) differs from the paper in: Lorentz term 0.3 q beta x B without c (force 3.34x too large;
confirmed: |L| peak 3.184 vs 0.955 with c); constant string force T s (no sqrt(1-v_perp^2) and no v_par v_perp term of Eq. 3); quirks start 2 mm apart;
relative momentum always transverse and perpendicular to the pair momentum, i.e. parallel to E_cm.
Fig. 2 kinematics (v* = 0.556, CM transverse speed 0.0975, charges +-1):
- as supplied: d max 3.79 cm, spacing 1.339 cm, |L| = 0 throughout (axis parallel to E_cm: no torque).
- c fixed, start at one point, axis z: d max 3.59 cm, spacing 1.305 cm, |L| at closest approaches 0.955 / 0.000 / 0.955 (same pattern as our simulation).
- c fixed, 2 mm start, axis z: |L| ~1.2e4 e12 hbar from the initial offset (2 mm x p*).
The supplied simulator does not produce the paper's pattern either. Its spacing (1.305 cm) differs from the paper (1.155) and from Eq. 3 (1.163).

## D31. Improved version of the supplied pair simulator (2026-10-12): `scripts/quirk_pair_sim_eq3.py`; test `scripts/D24_fig2_improved_simulator_test.py`,
`tables/D24_fig2_improved_simulator_test.txt`, `FINAL_FIGURES/F36_fig2_improved_simulator/`
Same interface and units (mm, ns, GeV, T, Lambda in eV) as the supplied simulate_quirk_pair_tracks; equations changed to the paper's: full Eq. 3,
Lorentz force with c (0.29979e-3 GeV/(T mm) x q v[mm/ns] x B), production at one point (sep0_mm = 0), CM-frame back-to-back momenta along rel_dir boosted
to the lab, separate charges, string direction from the relative velocity at zero separation. Validation, 3000 steps per period:
- constructed event (+-2/3, axis z): production d max 3.607, spacing 1.164, |L| 0.6434 / 0.0004 / 0.6430 / 0.0001; improved simulator 3.607, 1.163, 0.6434 / 0.0002 / 0.6430 / 0.0008.
- COL2000 key 8 (+-1): production 4.191, 1.047, 0.8620 / 0.0001 / 0.8622 / 0.0005; improved simulator 4.188, 1.047, 0.8619 / 0.0005 / 0.8599 / 0.0003.
The improved simulator reproduces the production integrator; the paper's Fig. 2 pattern is not obtained.

## D32. Fig. 2 cross-check with PreFASERQuirkSim (2026-10-12): `scripts/D25_fig2_prefaser_check.py`, `tables/D25_fig2_prefaser_check.txt`,
driver `scripts/external/D25_prefaser_driver.cxx` (compiled against github.com/eliwelch17/PreFASERQuirkSim src/, downloaded to the scratchpad, not in the repo)
Package (C++ port of the Mathematica code of arXiv:2404.13814) read: CalculateForces = Eq. 3 (both terms, Lambda^2/100 and /6.58 for um, ns, eV) +
0.587 q v x B (0.587/6.58 = 0.0892 GeV/(T ns); exact 0.29979^2 = 0.0899, i.e. 0.74% low) + dE/dx along v; string direction with a CM-simultaneity
correction and separate lab times t1, t2 per quirk (CalculateCt); p += F dt, trapezoidal r; dt = min(0.03 ns, t1q/divStep), t1q = closest-approach
interval; integer charges only. Driver: the package's functions and main-loop step, uniform 2 T, no material, production at the origin.
- constructed (+-1): production 3.607 cm, 1.164 cm, 0.9651 / 0.0006 / 0.9646 / 0.0002; PreFASER divStep 10000: 3.613, 1.165, 0.9587 / 0.0074 / 0.9667 / 0.0084;
  divStep 40000: 3.609, 1.164, 0.9583 / 0.0007 / 0.9590 / 0.0010.
- key 8 (+-1): production 4.191, 1.047, 0.8620 / 0.0001 / 0.8622 / 0.0005; PreFASER 10000: 4.195, 1.048, 0.8556 / 0.0009 / 0.8607 / 0.0029; 40000: 4.191, 1.048, 0.8571 / 0.0007 / 0.8570 / 0.0006.
- An independent code with a different string-direction convention (CM simultaneity) and integrator gives the same pattern (|L| = 0 at every
  second closest approach); peaks 0.6% lower, consistent with its 0.74% lower magnetic constant.

## D33. PhD thesis of J. Setford (University of Sussex, March 2018), Chapter 5 = arXiv:1708.02243 (read 2026-10-12)
Source: https://inspirehep.net/files/cc16a891fef1fa911454ec3528371b8d (135 pages). Declaration: "My role in this paper was to simulate the quirk
trajectories and understand their dynamics." Chapter 5 reproduces the paper (Eqs. 5.1-5.12, Fig. 5.2 = Fig. 2, Table 5.1 = Table I) with the same text.
Differences / additional information found:
- Sec. 5.2: in the CM frame "the magnetic field is seen as a combination of an E-field and a B-field. If we neglect the effect of the B-field in
  this frame, we can estimate the torque due to the E-field" (the paper: "seen as an E-field"). This concerns the estimate Eq. 5.5 only; the
  numerical solution uses Eq. 5.3 "with F_ext the Lorentz force" and "a uniform 2T magnetic field along the z-direction".
- Material: "We therefore neglect this effect in our simulations" (also in the paper, Sec. II, line 190 of the tex source; our earlier wording
  "the paper does not state material for Fig. 2" in D27 and the sheet is corrected: the paper states that material is neglected).
- No integrator, step size, L definition (frame / point), or the initial conditions of the Fig. 2 event are given. No code reference.
Effect on the three author questions: Q3 is answered for material (neglected); Q1 and Q2 remain open.

## D34. Li-Pei group papers read (2026-10-12; PDFs from arxiv.org, text extracted with PyMuPDF)
**arXiv:2002.07503, "The quirk trajectory" (Li, Li, Pei, Zhang, EPJC 2020)**, quirks in a tracker with uniform B (CMS, 4 T):
- EoM (II.1-II.3): Eq. 3 string force; F_ext = q v x B - <dE/dx> v_hat. s_hat in the CoM frame approximately parallel to the separation.
- Sec. II.B / App. A: analytic solution with uniform B, motion decomposed in the CoM frame into z+ (from B_c) and z- (from E_z = CoM electric field).
  App. A: "the average torque on the system of two quirks is zero when g is increased from 2n to 2n + 2 such that the total angular momentum of the
  quirk pair is also invariant at g = 2n" (g = Lambda^2 t_c / (2 m rho); the quirks meet at every integer g), and "two quirks meet each other and
  have opposite velocity at g = 2n in the CoM frame"; the system at g + 2 equals the system at g rotated by a small angle eta.
  This is the same result as ours with the magnetic field: L returns to its initial value (0) at every second meeting (D17-D32).
- Sec. V / App. B: analytic plane thickness d (Eq. V.5-V.9: d_E = 2 m q E_z rho asinh(rho) / Lambda^4, d_B = 2 m q B_c (rho - atan rho) / Lambda^4),
  linear in the quirk charge for a neutral pair; agrees with their numerical thickness within an order of magnitude (App. C).
- Sec. VI: ~10% of events with > 2 hits on at least one layer (Table I, CMS).
- Sec. VIII: string direction with CoM simultaneity, t1 - t2 = beta.(r1 - r2) (VIII.1), step condition (VIII.2), s_hat from (VIII.3-4);
  a fixed s_hat changes the plane thickness strongly. (PreFASERQuirkSim implements VIII.1-VIII.4; D32: same Fig. 2 result as our lab-frame method.)
**arXiv:2404.13814 (Feng, Li, Liao, Ni, Pei 2024)**: EoM (5.1-5.3) = string force + ionization; "we ignore [magnetic fields] in our simulation for
  simplicity" (the C++ port PreFASERQuirkSim includes field maps). Annihilation is treated only from the quirkonium ground state after radiative
  energy loss (Sec. 4, Eq. 4.10-4.11: S-wave sigma v |psi(0)|^2); radiative de-excitation times are orders of magnitude longer than annihilation.
**arXiv:2108.06748 (FASER, 2021)**: Eq. (4.1) L_tot = r1 x p1 + r2 x p2 in the lab; L'_tot = the same after boosting to the CoM frame ("The initial
  L'_tot at the IP is zero"); torque from ionization; torque integrated over a complete oscillation ~0 (no magnetic field in that paper).
  (Equation numbers given in D-chat earlier as "Eq. 18 / 30" came from an automated summary; the PDF numbers are (4.1)-(4.12).)
Wording for reports: "Independent groups using the same Eq. 3 find that the torque cancels over a full oscillation: arXiv:2002.07503 (uniform
  magnetic field, App. A) and arXiv:2108.06748 (material); this agrees with our result and not with the |L| shown in Fig. 2 of arXiv:1708.02243."
Note on scripts/quirk_pair_sim_eq3.py (D31): changes are relative to the simulate_quirk_pair_tracks text pasted on 2026-10-12; a Colab version was
  not available here and was not compared.

## D35. Review points from a comparison with another implementation (2026-10-12): verified and applied
1. Colored model: the production process (quirk_2000_fresh_regen_runs/colored_1800GeV_L2keV) uses PDG 1000006 (named t1 / QC), but it is a Dirac
   fermion: param_card QNUMBERS 1000006 "2 = number of spin states", particles.py spin = 2, colour 3, charge 2/3; matrix elements use fermion
   wave functions (IXXXXX/OXXXXX with MDL_MQC) and FFV1 vertices. Only the PDG number is borrowed from the stop. Our eps_trig (P3 recount):
   COL2000 207/873 = 0.237, COL1000 0.241, EW2000 186/1045 = 0.178, EW1000 0.174 (the other implementation, with VLQ_UFO / VLLS_NLO models,
   is reported to give 0.243 / 0.175; not verified here).
2. Step-by-step cut-flow: `scripts/D26_stepwise_cutflow.py`, `tables/D26_stepwise_cutflow.csv` (Wilson 95% per step; final counts equal the stored
   Table I counts: COL Z0 8/22, Z580 3/22; EW Z0 50/62, Z580 14/62). Losses (SCT z none): colored: layer-8 seed pair 3 (keys 48 49 55),
   seed Delta_w 1 (key 42), hit multiplicity 10 of 18 planes; EW: hit multiplicity 12 of 62, nothing else. With 580 um: colored Delta_s 6 of 9,
   EW hit multiplicity 16 and Delta_s 31 of 45. The last row is the eps_reco numerator; the denominator is the fiducial count.
3. Settings: `config/analysis_settings.yaml` (all production settings with their code locations) + `scripts/T1_config_check.py` (compares the file
   with the values in the code, exit 1 on a difference; config sha256 printed). Run 2026-10-12: all settings agree. The code is not changed to read it.
4. Physics tests: `scripts/T0_physics_tests.py` (4 s): Eq. 3 vs integrator 7e-16; Lorentz direction; gyroradius 1.4e-5; energy at B = 0 6.6e-12;
   d max vs 2(gamma-1)m/Lambda^2 5e-14; torque balance |L(2nd)|/|L(1st)| = 6.6e-4. All pass.
5. Fig. 5 population "plane found, before hit pattern and Delta_s / Delta_w cuts" was already done for the signal (P24, D18 follow-up):
   colored Delta_w median 0.498 cm (after hit multiplicity 0.482), EW 0.096 (0.097); paper 0.092 / 0.048. The population does not change Delta_w.
   Backgrounds in that population were not re-made.
6. Generator settings: `tables/generator_settings_2000.csv` from the run banners (MG5 3.7.3, Pythia 8.317, seeds 8001 / 8002, nn23lo1,
   dynamical scale -1, ickkw 1, xqcut 30, ptj 20, maxjetflavor 4, qCut 45, nJetMax 1, nQmatch 4, doShowerKt off, scheme 1). For the next report.
   Not applied: stopping the integration once both quirks are outside and moving outward (all-crossings mode needs the full trajectory, and the
   production simulator is not changed).

## D36. Settings moved to three config files read by the production code (2026-10-12; supersedes D35 item 3)
- `config/detector.yaml` (mm, T, ns; source per line: [paper] Sec. III A, [27] = ATL-PHYS-PUB-2009-002 (verified in the .bbl), [ours]):
  B 2 T, beam pipe 23.5 mm, timing 25 ns, beam spot 45 mm (mode common_shift_fit_true_vertex), SCT r-phi 0.034 mm (2 x 17 um), SCT z primary 0
  with options 0 / 0.034 / 0.58 / 1.16 mm, merge_hits_in [pixel], 8 layers (IBL marked [ours]: not in [27], which predates the IBL).
- `config/reconstruction.yaml`: integrator, 300 steps per period (D14), max radius 600 mm, hit mode first_crossing (options first / all),
  multiplicity rule at_least_2 (exactly_2 implemented in P18.mult_ok), all Sec. III C / IV cuts in mm with the paper's cm value, prefilter none.
- `config/benchmarks.yaml`: colored 1800 GeV, Table I Lambda [1000, 2000, 3000, 5000, 10000] eV, production 2000, charged fraction 0.3, seed 8001;
  EW 800 GeV, [1000 ... 5000], production 4000, 1.0, seed 8002; trigger 200 GeV; 300 fb^-1; pile-up mu 0 (signal) / 50 (background).
- `scripts/analysis_config.py`: strict loader. Unknown key, missing key, option outside its list, production Lambda outside the Table I list,
  unimplemented choice -> error. Every key is declared with the code that reads it (scope signal / background / limits); `assert_used("signal")`
  fails if a signal key was not read; `write_provenance(out)` writes `<out>.config.json` with the sha256 of the three files and the values read.
- Code changes: P4_literal_signal (HALF, SZ, PAR, beam spot, layers, step floor, B, max radius from the config; mm -> cm rounded to 12 digits so
  that the values are bit-identical), P18_all_crossings (timing cut, SCT r-phi, all cuts, multiplicity rule, B, max radius; provenance),
  D26 (same). `scripts/T1_config_check.py` (15 checks incl. 4 rejection tests and equality with the former literals): all pass.
- End-to-end: D26 re-run under the config: output byte-identical to the run before the change, 0 mismatches vs p18.reco,
  provenance tables/D26_stepwise_cutflow.csv.config.json (config sha256 23a00dda02bbda4b...).
- Not changed: scripts that do not go through P4/P18 keep their own constants (the earlier D-scripts and background scripts); background-scope
  keys (beam pipe, pile-up mu 50) are declared for those scripts but not wired yet.

## D37. Annihilation at the L ~ 0 meetings: worst-case estimate and quantum toy test (2026-10-13)
`scripts/D27_annihilation_tests.py`, `tables/D27_annihilation_A.csv`, `tables/D27_annihilation_B.txt`, `logs/D27_annihilation_stdout.log`.
A. Worst case: S-wave at every second meeting. |psi(0)|^2 = mu F / 2 pi (any S state of V = F r), Gamma = sigma v |psi(0)|^2, one full oscillation
   T = 4 m gamma* v* / Lambda^2 -> P_osc = c_sigma alpha^2 gamma* v* (m and Lambda cancel). c_sigma = 1, or the dark-gluon channel of arXiv:2404.13814
   Eq. 4.11 with N_IC = 2 (1/8 colored, 3/8 colour-neutral); alpha = 0.02, 0.05 (not given by the paper). Per fiducial event: gamma* v* (median 0.58
   colored, 0.69 EW), N = full oscillations until the CM reaches r = 51.4 cm or 25 ns. Mean survival (min over events):
   - colored 2 keV (N ~ 19): 0.995 / 0.970 (c=1, alpha 0.02 / 0.05); dark gluons 0.999 / 0.996.
   - colored 10 keV (N ~ 470): 0.887 / 0.494; dark gluons 0.985 / 0.911.
   - EW 4 keV (N ~ 93): 0.971 / 0.835; dark gluons 0.989 / 0.934.  EW 5 keV (N ~ 145): 0.955 / 0.756; dark gluons 0.983 / 0.899.
   Survival falls with Lambda (N ~ Lambda^2). Above 95% everywhere only for alpha = 0.02 with the dark-gluon sigma v; for alpha = 0.05 or c_sigma = 1
   it drops to 0.5-0.9 at the highest Lambda of Table I. Order of magnitude (non-relativistic formula, v* ~ 0.6).
B. Quantum toy model (2D relative coordinate, hbar = mu = F = 1, H = p^2/2 + r - f x, packet from the origin with p0 = 8 along z, split-operator FFT
   768^2, t <= 64, four meetings). Probability inside r < 1 at each meeting relative to the field-free run, quantum <L> +- spread, classical L:
   - f = 0.029 (classical L peak 10): meetings 1-4: ratio 0.35 / 0.98 / 0.36 / 0.93; <L> = 10.0 / 0.7 / 8.7 / 2.4 (spread ~6); classical 10.0 / 0.2 / 10.1 / 0.5.
   - f = 0.088 (peak 30): ratio 0.001 / 0.89 / 0.019 / 0.57; <L> = 28.6 / 3.2 / 27.2 / 10.7 (spread 7-12); classical 28.8 / 1.7 / 30.1 / 6.2.
   The quantum evolution follows the classical torque cancellation: at every second meeting the overlap at the origin returns to (nearly) the
   field-free value; the angular momentum does not protect against annihilation there. (In the toy, L / (p0 A) ~ 0.04-0.1, so the cancellation is
   less complete than in the real system, where it is ~1e-6 of the peak.) Norm loss <= 5% (absorbing boundary).
Conclusion: the paper's statement that |L| = 0 only at large separation is not supported classically (D29) or quantum mechanically (B). Whether
annihilation changes Table I depends on alpha_dark and sigma v, which the paper does not give: negligible at 2 keV colored, up to ~10-50% loss at the
highest Lambda in the pessimistic setting. Reported as a worst-case systematic, not a prediction.

## D38. Quantum toy checks and repeated layer crossings (2026-10-14)
**Toy model (D37 B), f = 0.0879 (classical L peak 30), meeting-4 overlap 0.57** (`scripts/D28_quantum_toy_checks.py`, `tables/D28_quantum_toy_checks.txt`):
- Finer grid 1024^2 (dx 0.094) and dt 0.0025: overlap ratios 0.001 / 0.892 / 0.022 / 0.565, <L> 28.1 / 3.2 / 27.1 / 10.1 (D27: 0.001 / 0.889 / 0.019 / 0.573): converged.
- Classical ensemble of 4000 trajectories from the Wigner function of the same initial packet: 0.005 / 0.917 / 0.024 / 0.521, <L> 29.3 / 3.9 / 28.6 / 13.4.
- The incomplete return at meeting 4 is reproduced by the classical ensemble: it is the spread of the initial packet (momentum spread 0.7 / p0 = 9%
  in the toy), not a quantum effect. Single classical trajectory: L 28.8 / 1.7 / 30.1 / 6.2.
**Repeated crossings of the same layer** (tables/all_crossings_per_event.csv, fiducial events, SCT z none; hits after the t < 25 ns, acceptance and
pixel-merging steps; mode ALL vs FIRST):
- COL2000: 13/22 = 0.59 [Wilson 0.39, 0.77] have > 2 hits on at least one layer (max-hits distribution 2: 9, 4: 7, 6: 3, 8: 3; median 9 extra hits).
- EW2000: 31/62 = 0.50 [0.38, 0.62] (2: 31, 3: 3, 4: 18, 5: 1, 6: 6, 8: 3). (1000-event samples: COL1000 1/6, EW1000 12/33 = 0.36 [0.22, 0.53].)
- arXiv:1708.02243 Sec. III B: the pT > 200 GeV requirement implies the pair is "sufficiently boosted, such that each quirk will most likely
  intersect each layer only once". Our 2000-event samples have repeated crossings in half or more of the fiducial events.
- arXiv:2002.07503 Sec. VI / Table I (CMS, m = 100-500 GeV, pT > 100-300 GeV, Lambda 0.2-2 keV): F(n_max > 2) ~ 10%, rising with Lambda and m/pT.
  Our benchmarks have larger m/pT (1800 or 800 GeV at pT > 200 GeV) and Lambda (2-4 keV), the direction in which that paper finds more
  repeated crossings; the numbers are not directly comparable (different detector and benchmarks).

## D39. Amendment to D9 ("no code error found") and pre-registered test (2026-10-14)
String direction taken at equal lab time instead of equal CM time; inflates the truth plane thickness (EW median 15 um vs 1.1 um, D30; each
convention converged in step size, D31: lab 5-55 um at 1500 / 3000 / 6000 steps, CM 0.6-1.6 um at divStep 3000 / 30000). This is a modelling
approximation that departs from the paper's stated straight-string limit "in the center of mass frame" (and from 2002.07503 Sec. VIII,
1911.02223 Sec. III B), not a crash or a wrong formula. Fig. 2 / |L| is unaffected (D21). Effect on Table I under study: pre-registration
notes/D39_prereg.md (sha256 in notes/D39_prereg_sha256.txt), written before the run.
Other results of 2026-10-14 (scripts/D29_li_pei_formulas.py, tables/D29_li_pei_formulas.csv; MG5 LO runs in the scratchpad):
- Delta_w vs the belt width L of 2002.07503 Eq. III.1: Spearman 0.74 (colored), 0.96 (EW); Delta_w / L median 0.28 / 0.35, close to 1/sqrt(12) = 0.29
  for a uniform strip. Our Delta_w follows the analytic width of our kinematics; the paper's 2-5x smaller Delta_w is not explained by the reconstruction.
- Repeated crossings: the strict condition D' < R < L' (App. D) holds for 2/22 colored and 0/62 EW events (observed 13 / 31); the second condition
  "R >> L'" applies to all our layers. 2002.07503 Table II (CMS, Lambda = 2 keV) also shows 4-8 hits on several layers: qualitatively consistent.
- Truth plane thickness (lab-time string): colored median 4.1 um, EW 13 um; measured Delta_s 38 / 43 um: Delta_s is dominated by the detector resolution.
  1911.02223 Eq. III.12: 2.1 / 0.06 um; 2002.07503 Eq. V.6: 0.55 / 0.12 um.
- EW trigger: MG5 3.7.3 LO, 13 TeV, our model: sigma(pp -> QE+ QE-) = 2.321e-4 pb, sigma(pp -> QE+ QE- j, pT(j) > 200 GeV) = 2.195e-5 pb, ratio 0.095.
  Colored 1800 GeV: 3.120e-4 pb and 4.395e-5 pb, ratio 0.141. 1911.02223 App. A: "the trigger efficiency (pT(j) > 200 GeV) for Ec production
  process is 0.1, which coincides with the number in the Table I of the Ref. [1]". Inference: the paper's EW 0.10 equals the LO ratio, while its
  colored 0.24 matches the matched + showered sample (ours 0.237); this suggests different procedures for the two benchmarks.
- 1911.02223 (CMS): hit resolution 10 um for all hits; no information on ATLAS SCT z. Footnote 9: "In Ref. [1], they assume 8 layers for the ATLAS
  tracker. We use the actual ATLAS tracker which has 3 layer for the pixel detector and 4 layers for the silicon-strip detector."

## D40. Result of the D39 pre-registered test (pre-registered text verified unchanged: sha256 eb59c8f7... OK), 2026-10-15
`scripts/D32_cm_time_string_reco.py`, `tables/D32_cm_time_string_reco.csv` (+ .config.json), `logs/D32_stdout.log`. Validation: the lab-time results
equal the stored production values (COL 2 keV 8/22, 3/22; EW 4 keV 50/62, 14/62; EW 1 / 2 keV 12/62, 40/62 = tables/lambda_scan_per_event.csv).
CM-time step converged at divStep 30000 (one EW event: 0.918 / 0.544 / 0.538 um at 3000 / 30000 / 100000). All lab-fiducial events stay fiducial.
| benchmark | truth thickness lab / CM | SCT z none: eps_reco lab -> CM (changed) ; Delta_s median | SCT z 580 um: eps_reco lab -> CM (changed) ; Delta_s |
| COL 2 keV | 4.1 / 1.9 um | 8/22 -> 8/22 (2) ; 37.7 -> 40.1 um | 3/22 -> 3/22 (0) ; 184 -> 151 um |
| EW 1 keV  | 12.4 / 7.3 um | 12/62 -> 11/62 (1) ; 37.2 -> 27.8 um | 4/62 -> 5/62 (1) ; 132 -> 153 um |
| EW 2 keV  | 13.1 / 2.0 um | 40/62 -> 42/62 (6) ; 42.0 -> 32.9 um | 16/62 -> 15/62 (3) ; 162 -> 149 um |
| EW 4 keV  | 13.0 / 0.6 um | 50/62 -> 51/62 (7) ; 43.1 -> 37.9 um | 14/62 -> 15/62 (5) ; 149 -> 141 um |
Against the expectations: EW 4 keV Delta_s (none) fell to 37.9 um (expected ~40), not to 28 um: as expected. Colored unchanged: as expected.
eps_reco changed by at most 2 events net at every benchmark (no change of 5 or more): as expected. 580 um: small change: as expected.
EW 1-2 keV "can only rise": 2 keV +2, 1 keV -1 (not confirmed in direction; within the event-level changes). Individual events change in both
directions (up to 7 at EW 4 keV), the same size as the step-size changes of D14 (300 vs 6000 steps: 7 EW events), since the two codes differ also in
integrator and step. Delta_w unchanged (0.093-0.552 vs 0.096-0.547 cm).
Conclusion: the string-direction convention changes the truth plane thickness (EW 13 -> 0.6-7 um) and lowers the EW Delta_s without SCT z smearing
by 5-9 um, but it does not change eps_reco beyond +-2 events and does not explain the Table I differences (EW trigger, low-Lambda eps_reco,
Delta_w, SCT z). Production is kept with the lab-time string; the convention is listed as a modelling approximation (D39).

## D42. Updated report of 2026-10-15 (TABLE_I_REPRODUCTION_REPORT_2026-10-15.pdf, 10 pages; the 2026-10-09 report is unchanged)
Scripts: R_data_2026_10_15.py (all numbers, read from the outputs with assertions), F38_report_2026_10_15_figs.py (F38_table_I, F38_lambda, F38_fig2),
R_report_2026-10-15.py (built with reportlab 4.2.5 in the scratchpad venv). Uncertainties: simple binomial sigma = sqrt(e(1-e)/n) with each
efficiency's own denominator; MG integration errors for the LO ratio; quadrature of relative sigma for Eq. 12; 95% UL 1 - 0.05^(1/n) for 0/n.
No Wilson intervals or p-values (request of 2026-10-15). D41 enters as a frozen snapshot (D41_NMAX; 2118 of 3000 events at build time), the same
for tables and figures; the report states "run in progress". Independent verification against the raw CSV / jsonl and the PDF text: 27 of 27 checks.
New input copies: inputs_D41/ (MG5 logs and banners, LHE of sample B, showered CSV, Pythia settings). Detached waiter logs/D41_waiter.sh starts the
showered run after the main run reaches 3000 events. To rebuild after D41 finishes:
  <python with reportlab> scripts/R_report_2026-10-15.py   (unset D41_NMAX; uses all finished events)

## D43 (2026-10-15) Report v2
- New `TABLE_I_REPRODUCTION_REPORT_2026-10-15_v2.pdf` (script `scripts/R_report_2026-10-15_v2.py`); the first 2026-10-15 report is kept.
- Only SCT z none and 1.16 mm are shown. Fig. 5 is rebuilt as `F40_fig5_<sct>`, with the backgrounds at the same SCT z as the signal (F30 used 580 µm backgrounds). No pile-up-only sample exists without SCT z smearing.
- Decision rule: consistent if |ε − p| ≤ 2√(p(1−p)/n). It agrees with Wilson 95% for every cell.

## D44 (2026-10-16) Report v3
- New `TABLE_I_REPRODUCTION_REPORT_2026-10-16.pdf` (script `scripts/R_report_2026-10-16_v3.py`); v2 is kept.
- Added coloured headings and key boxes.
- Added a cut-flow at every Λ for both benchmarks (fiducial, plane, +hits, SR pass/fail, ε_reco, ε from Eq. 12 vs the paper's product), built from `lambda_scan_*per_event.csv`. It is asserted equal to the summary counts.
- Added the Fig. 3 Δφ table and the background pass/fail cut-flow (1.16 mm and none; pile-up at 1.16 mm only).
- Rewrote the annihilation section in two parts:
  - **4.1:** b = |L|/p from D22: the left-over |L| is 2e6–4e8 ħ, so b·m_Q is 3e6–6e8. 1/m_Q = 1.1e-17 cm, not 1e-16.
  - **4.2:** checked against the papers.
    - 2108.06748 Sec. 4 says the initial L' is zero and that material changes L.
    - 2404.13814 Eq. 4.11 gives the annihilation cross section; annihilation happens only from the ground state, and radiation matters only for Λ ≳ 100 keV.
    - η (2002.07503 Eq. A.6) keeps the head-on meetings of Eq. A.5, so it is not written as a cause.

## D45 (2026-10-16) Final meeting report
- New `TABLE_I_REPRODUCTION_REPORT_2026-10-16_final.pdf` (script `scripts/R_report_2026-10-16_final.py`). The 10-16 v3 report is kept.
- Table I: actual values in every row. For k = 0 the 95% UL is given (k = n: 95% LL). Every decision cell shows |Δ| and 2σ₀. The 2σ₀ rule agrees with Wilson in every cell.
- EW 3 keV n_fid = 61: event 127 could not be integrated at 3 keV (step limit), so it is counted as not fiducial. This is not a typo.
- Section 2.3: production vs LO (3000 events) vs LO + Pythia shower (2792 of 3000 with pT(QQ) > 200 GeV after the shower; complete).
  - The trigger cells use |Δ| ≤ max(2σ, 0.005), because the paper quotes 0.10 to two decimals: LO 0.096 consistent, showered 0.089 inconsistent.
  - ε_reco (no SCT z) is above the paper in the LO sample at Λ = 1–5 keV.
  - The showered run stopped at 2120 events when the machine restarted (checkpoint intact) and was resumed. It finished at 13:08 with 111 failures in 13960 trajectories.
- F41_appendixA_diagram: (a) is a conceptual sketch with Eq. A.5 at g = 0 and 2; (b) and (c) are simulation output. It is included in Section 3.

## D46 (2026-10-16) Final meeting report v2
- `TABLE_I_REPRODUCTION_REPORT_2026-10-16_final_v2.pdf` (script `R_report_2026-10-16_final_v2.py`); `_final` is kept.
- Section 3 adds two tables built with `scripts/T_fig2_meeting_table.py`:
  - the initial values of the constructed event and of key 8 (`fig2_initial_values.csv`);
  - the per-meeting comparison with the paper: r, |L|, signed L, ΔL per half, zeros, b = |L|/p* (`fig2_meetings_detail.csv`).
- Formulas and key-box labels are shown in red. The L definition now states "*, equal CM time", and Eq. 5 also gives the paper's form.

## D47 (2026-10-17) Figure 6 restarted with the Table I pipeline
- The user asked to move to Figure 6 with "the best consistent results"; this lifts the earlier "do not resume Figure 6" constraint.
- The old figure6_full_v1 production (paused 2026-09-24; 20/91 cells; SCT z 1.16 mm; EW trigger counted on matched events; old pipeline) is NOT resumed. It is kept unchanged as an archive.
- Kept: the 13 generated HepMC samples (hep_tools/figure6_full_v1_runs).
  - `scripts/F6_01_extract_events.py` writes fig6/inputs/<tag>_events.csv (needs PYTHIA8DATA for the R-hadron charge table) and counts.csv.
- New: `scripts/F6_02_grid.py`, the Table I pipeline per event:
  - Λ = 1, 2, 3, 4, 5, 7, 10 keV; first crossing;
  - reco with SCT z none and 1.16 mm using the same draws;
  - colored: both charged |q| > 0.5;
  - seeds SeedSequence([6, m, i]);
  - append-only logs/F6_<tag>_events.jsonl.
- Pilots (6 colored 1800 events, 3 EW 100 events): ~120–140 s CPU per event for all 7 Λ (half of it at 10 keV); about 70 s wall per event with 3 workers on 4 vCPU. The full grid of ~1160 events takes about one day.
- Launched detached: logs/F6_runner.sh (benchmarks first), started 2026-10-17 00:56.
- Fig. 6 has no background (paper: "assuming negligible irreducible backgrounds"). Main contour: SCT z 1.16 mm for signal and background, where our background is 0/9139, so the assumption holds. Comparison contour: signal with no SCT z smearing, which reproduces Table I, but the same-smearing background is 146/9139 there.

## D48 (2026-10-17) Figure 6 overnight run (user: "fig 6 subah tk", decisions: show f_ch both ways; use current samples, mark unresolved edges)
- Full paper reread. Settings and checks are in fig6/README_FIG6.md.
- The high-Λ band (15–35 keV) costs about 38 min per event, about 2 days in total, so it is not run tonight. The figure marks Λ > 10 keV as not computed.
- Run: low band (0.1–0.7 keV) and mid band (1–10 keV), 9 workers on 10 vCPU (WSL raised to 10 processors by the user). logs/F6_overnight.sh started 01:47.
- EW LO ratios: 12 MG5 3.7.3 runs in hep_tools/F6_EW_LO_ratio (nn23lo1, MQE set; B: ptj 200, ickkw 0, xqcut 0). At 800 GeV: 0.0961.
- Paper Fig. 6 curves: scripts/S4_fig6_vector_extract.py → tables/paper_fig6_vector.json. The 12.9 fb⁻¹ regions are taken from their solid outlines; the filled paths are hatch tiles.
- Analysis and plot: scripts/F6_03_contours.py → fig6/F6_N_grid.csv, FINAL_FIGURES/F6_fig6/.
- 2026-10-17 09:00: the run finished (low + mid, 11 points). Figure FINAL_FIGURES/F6_fig6. Reach and checks are in fig6/README_FIG6.md.
  - Contour fix: k = 0 points are no longer given an arbitrary value; no contour passes through them.
  - No SCT z smearing, with the charge factor: discovery colored 1591 / EW 643 GeV (paper abstract 1600 / 650; paper figure 1707 / 688); exclusion 1702 / 712 (paper 1793 / 762).
  - SCT z 1.16 mm, with the charge factor: discovery 1424 / 428; exclusion 1497 / 474.

## D49 (2026-10-17) Fig. 6 normalisation sensitivity and caption (user's list)
- K-factor overlay F6_kfactor: colored ×1.5 and EW ×1.4 bring the maxima onto the paper's; ×2 (N_Q reading) overshoots.
- Bug fixed before reporting: a "bound" point scaled above the threshold was being used as a measured N. It is now "not determined beyond the last computed mass".
- Main figure:
  - title: "left: signal SCT z = 1.16 mm (literal text); right: signal without SCT z smearing (what the paper's results require)";
  - the maxima with ±1σ are written in each panel;
  - notes: LO σ, no K-factor, N_Q = 2 not applied, EW ε_trig = LO ratio (the matched count would add ~60–80 GeV), red ✕ regions untested, Λ > 10 keV not computed, annihilation worst case −30 (colored) / −25…−40 (EW) GeV.

## D50 (2026-10-17) Fig. 6 high band moved to another machine; numba integrator
- 03_trajectory_sim/quirk_trajectory_numba.py is a compiled copy of quirk_trajectory_optimized_v2.
  - Bitwise identical trajectories.
  - Full-pipeline validation: 396 rows, 0 differences (scripts/F6_06_validate_numba.py). 15–37× faster.
  - F6_02_grid.py uses it with FAST=1.
- The high-band pilot on this laptop was killed twice by the OOM killer (one 30–35 keV trajectory ≈ 2 GB; WSL has 8 GB). By the user's decision the high band runs on another machine.
- Portability (no change in results on this machine):
  - BASE in P4 and in the forensic pipeline can be set with env COPLANARITY_BASE;
  - the sys.path inserts in trajectory_to_hits, optimized_v2 and numba are now relative to the file;
  - F6_03 reads fig6/F6_ew_lo_ratio.csv when the MG5 log is absent, and reads high-band checkpoints when they exist.
- Bundle: FIG6_HIGH_BAND_BUNDLE_2026-10-17.tar.gz (3 MB) with RUN_FIG6_HIGH_BAND.sh and README_FIG6_HIGH_BAND.md. Tested unpacked elsewhere:
  - no file was opened from the original repo (audit hook);
  - validation passed;
  - the grid checksum is identical.

## D51 (2026-10-18) Fig. 6 high band on the laptop: memory fix, step-ceiling scan, 15–25 keV run (user: "you start running here, work overnight")
- Memory:
  - one 15–35 keV event used > 5 GB (killed by the guard);
  - fixes: F6_02 frees each trajectory before the next Λ, and a positions-only numba integrator (XONLY=1; the momenta are never read by the hit/crossing code; bitwise identical positions; full-pipeline validation PASSED again: 396 rows, 0 differences);
  - peak per process is now 2.4 GB.
- NWORKERS=1 runs in-process: a killed process exits, and its lane restarts it from the checkpoint.
- Step-ceiling scan (fig6/F6_high_step_ceiling_scan.csv): the 20-million-step ceiling of simulate_quirk_hits removes, among the events fiducial at 10 keV,
  - 0–4% at 15–20 keV;
  - 0–13% at 25 keV;
  - 5–56% at 30–35 keV.
  So 30–35 keV would be strongly biased low. They are not run; they need a larger ceiling and about 5–7 GB per process. The ceiling and the physics are unchanged.
- Run: band high_a = 15, 20, 25 keV, all 11 points. Two lanes of 1 process each, plus a memory watchdog (kills the largest process if MemAvailable < 700 MB). Started 2026-10-18 00:52.
- 2026-10-18 02:26: the 15–25 keV run finished.
  - 11 points complete, no duplicates, no watchdog action.
  - Ceiling failures among events fiducial at 10 keV: 0–1 at 15–20 keV, 0–3 at 25 keV.
  - Figure, reach and sensitivity rebuilt; the maxima are unchanged.
  - The caption now says "Λ = 15–25 keV computed; Λ > 25 keV not computed (step ceiling)".

## D52 (2026-10-18) Figure 7, new report, ROOT CSVs, cleanup (user: "pehle 3 kaam kro or purani files ki safai ... har csv save ... delta s delta w ka answer")
- Figure 7 (Appendix A; scripts/F7_dedx.py, S5_fig7_vector_extract.py):
  - βγ = |p|/m at each pixel-layer crossing; dE/dx = PDG Eq. 34.12 most probable value, silicon with density effect, IBL 200 µm / 250 µm (paper does not state the thickness). Check: 1.11 MeV cm²/g at the minimum in 250 µm.
  - Medians: ours βγ 0.66 / 0.42 (EW / colored), paper 0.35 / 0.22.
  - The paper has 7–10% / 16–22% of its hits below βγ = 0.1; we find ≤ 2.3% in every selection (trigger or not, timing cut or not, all crossings).
  - The paper's dE/dx histogram (19–47 MeV cm²/g) is not the PDG MPV of its own βγ histogram (which spans 1–47, median 6 / 13).
- Report TABLE_I_REPRODUCTION_REPORT_2026-10-18.pdf (scripts/R_report_2026-10-18.py, 13 pages): adds
  - Fig. 2 on a log scale with the time-step table (3.1);
  - the reason for the Δs / Δw values from a reread of the paper (6.4);
  - Figure 6 with the reach and sensitivity tables (8);
  - Figure 7 (9);
  - updated open points.
- ROOT_CSV_2026-10-18/ (scripts/R_export_root_csv.py): every plotted number as one-header CSV (-999 = missing), a README with columns and units, and plot_examples.C, tested with ROOT (root-env): Fig. 6 contours and Table I.
- Cleanup: 692 files (80 entries: old audit / pilot folders and loose files in 05_coplanarity_analysis that no active script uses, plus 12 superseded report PDFs and the *_SUPERSEDED docs).
  - Zipped to /home/rafia/coplanarity_archive/coplanarity_study_ARCHIVE_2026-10-18.zip. Every file is verified by SHA-256 (0 mismatches). Manifest in docs/ARCHIVE_MANIFEST_2026-10-18.csv.
  - Removed with git rm, so they also stay in the git history.
  - Kept: the 10-09 report, 10-16_final_v2, 10-18, all data and logs, and every folder an active script uses.
  - After the cleanup, the Fig. 6 grid is rebuilt identically (same checksum), and the report and ROOT export rebuild.

## D53 (2026-10-19) Figure 6 EW trigger from the matched + shower sample (user: "papaer k closest approach ... han paper waly sy kro matched shower wala")
- Question: the EW main line took ε_trig from the LO ratio σ(QQ̄ + j, pT > 200)/σ(QQ̄) and ε_fid, ε_reco from the matched + shower sample (two different samples).
- Paper: one sample ("0 + 1 jet ... matched using Pythia8"), trigger pT(QQ̄) > 200 GeV; no LO ratio is stated (the 0.10 of Table I is reproduced by the LO ratio, as in arXiv:1911.02223).
- Decision (user's choice): main EW ε_trig = N(pT(QQ̄) > 200)/N(matched) of the same sample, as for colored. The LO ratio stays as a labelled alternative (F6_05 variants "EW LO-ratio trigger", "EW fully LO"; column eps_trig_LO in F6_N_grid.csv).
- EW 1000 GeV now has N_max 3.72 ≥ 3 and was run (logs/F6_EW1000.sh; low, mid, high_a; 190 events; 36 min). Max N = 0.88 (4 keV), so it does not move the contour; no mass outside the grid is needed.
- Result (no SCT z smearing, with charge factor): EW 792 / 701 GeV (paper 762 / 688); with SCT z 1.16 mm 524 / 473. Colored unchanged 1702 / 1591. LO-ratio alternative 712 / 643.
- Fixes found on the way: F6_03 asserts that every checkpoint is complete; counts.csv n_trigger_both_charged uses abs(q) > 0.5 (as F6_02/F6_03); F6_kfactor hatch moved from 10 to 25 keV.
- New outputs (older versions kept): TABLE_I_REPRODUCTION_REPORT_2026-10-19.pdf (scripts/R_report_2026-10-19.py), ROOT_CSV_2026-10-19/.

## D54 (2026-10-20) Consequences of the EW trigger change (review pasted by the user: "ye dekho")
- K-factor: with the matched trigger, EW is above the paper's figure at K = 1 (792 / 701 vs 762 / 688); added EW K = 0.8, 0.9 (K = 0.9: 772 / 686). EW needs K ≈ 0.85–0.9, colored ~1.5–1.7: one common K-factor cannot explain both. Stated in the report Section 8, the open points, the Fig. 6 caption and README_FIG6.
- Abstract: only colored discovery (1591) still matches the abstract (1600); EW discovery (701) is closer to the figure (688) than to the abstract (650). No text claims both match.
- EW trigger 0.178 vs 0.148: run banners diffed, identical cards except iseed (8002 / 9504). Decision: each calculation keeps its own sample; the headline value compared with the paper is the combination 338/2069 = 0.163 (Wilson 95% 0.148–0.180), quoted the same way in the Table I section, Section 8 and the caption.
- Report 2026-10-19 rebuilt (15 pages) with the one-line summary of Fig. 6 from the review.

## D55 (2026-10-20) Fig. 7: test of the paper's dE/dx definition (user's request, no simulation)
- The paper's own βγ histogram (right panel) was converted to dE/dx with 4 definitions: PDG MPV (MeV cm²/g), Bethe mean (MeV cm²/g), Bethe mean × ρ (MeV/cm), MPV × ρ (MeV/cm); bins with βγ < 0.1 left out, as the paper states for its left panel (variant 0.05).
- Criterion fixed before running: both samples, median within 15% and 10%/90% quantiles within 25% of the paper's dE/dx histogram.
- Result: none passes (either βγ cut). The paper's histogram starts sharply at 18.9 (10% quantile 19.5–19.9); every conversion puts 33–82% of the hits below 18.9. Bethe mean in MeV/cm is closest in median (0.79 / 1.26) but not in range.
- Report: the existing statement ("the paper does not give enough detail") stays; the test is report Section 9.1 (scripts/F7_02_dedx_definition_test.py, tables/F7_dedx_definition_test.csv, ROOT_CSV_2026-10-19/Fig7/fig7_dedx_definition_test.csv). Our dE/dx definition is unchanged.

## D56 (2026-10-21) Final check before submission (user: "final check krlo report ko")
- Report 2026-10-19 re-read page by page and its numbers recomputed. Found and corrected in a new version, TABLE_I_REPRODUCTION_REPORT_2026-10-21.pdf (scripts/R_report_2026-10-21.py); the 2026-10-19 PDF is unchanged:
  - Sec. 3.1: "at least 500×" was wrong; the paper's 1.94×10^11 ħ at meeting 2 against our largest residual 4.2×10^8 ħ gives about 460× (now computed in the script).
  - Sec. 3: the paper's first-half change appears as +0.64 (meeting table, from its curve's first point 0.008) and +0.65 (half-oscillation table, from 0); note added.
  - Fig. 6: its embedded caption printed at ~4 pt and carried change-log wording; the report shows the figure without it (cropped copy report_pdf/F6_fig6_report_2026-10-21.png) plus a readable caption. The full caption stays in FINAL_FIGURES/F6_fig6.
  - Open points, Fig. 7: removed "it is not consistent with its own βγ histogram" (stronger than the test shows; the test covers four definitions only).
  - References: ROOT_CSV_FIGURES_2026-10-21/ and ROOT_GENERATED_GRAPHS/ added; date 21 October 2026.
- ROOT READMEs: the paper's Fig. 5 medians were bin centres (e.g. converted γ Δs 0.028 cm); they are now the report's within-bin interpolation (0.031 cm), and the Fig. 7 paper dE/dx medians are now the report's 22.4 / 20.7 (the log prints the bin centres, 22.7 / 20.9). No plot changed.
- Checked and consistent: Table I decisions and products, cut-flows, Q1 numbers, Fig. 6 reach / K-factor statements, Fig. 7 tables. All 12 ROOT graphs render; no errors in the logs.

## D57 (2026-10-21) Review of the final check (pasted by the user)
- What D56 checked: the report's numbers were recomputed from its own inputs (tables, CSVs, digitised paper curves), so it shows the report is internally consistent. It does not re-verify the inputs themselves (for example the digitisation of the paper's curves, or our simulation residuals such as 4.2×10^8 ħ).
- Why the interpolated median is used for the paper's binned histograms (Fig. 5): the paper gives only bin contents in 0.1-decade bins. Taking the centre of the bin where the cumulative fraction reaches 0.5 can only return a bin centre, so its error is up to half a bin (±12% in Δ). Interpolating in log Δ within that bin, assuming a uniform distribution in log Δ inside the bin, gives the 50% point continuously and is the standard estimate. The report always used it; the ROOT READMEs now do too.
- Fig. 3: the ROOT README's paper value 3.53×10⁻⁴ rad (EW) was not a rounding of 0.3556×10⁻³. It is the digitised point nearest to r = 15 cm (r = 15.026 cm); the report interpolates at r = 15.0 cm (3.556×10⁻⁴). The README now quotes the report's values and documents the macro's nearest-point value; the plots are unchanged (the difference is < 1%).
- Embedded text: the full text of all 9 report figures and all 12 ROOT graphs was read. There is no internal or change-log wording; only F6_fig6, which is not shown in the report since D56, had it. Found: the F6_kfactor titles show the paper's maxima truncated (1792, 687 GeV; the curves give 1792.8, 687.5), while the report table rounds them (1793, 688). Not changed, because changing it would regenerate a graph; the user decides.

## D58 (2026-10-21) Report 21 Oct against 16 Oct v2 (the version the professor has), for the changelog
- Method: text of both PDFs extracted and diffed line by line over the shared sections; embedded images compared by pixel hash.
- UNCHANGED: Sec. 1; 2.1 (every efficiency and decision); 2.2 (every cut-flow count and ε product); the 2.3 tables (LO samples, trigger and fiducial table: EW εtrig 186/1045 = 0.18); Sec. 4, 5, 6 (Figs. 3–5 tables), 7; all 6 figures of 16 v2 (pixel-identical).
- So the 19 Oct EW trigger change (matched count) affected only Fig. 6. Table I already used the matched count 186/1045 in 16 v2, and it still does.
- CHANGED, text only: 2.3 "Why" and "Result" (0.18 → "0.163, both matched samples combined", plus the paragraph on the two samples 0.178 / 0.148); Sec. 3 note on +0.64 / +0.65; date; open points and references extended.
- NEW (not in 16 v2): Sec. 3.1 with the log-scale Fig. 2 (including the 460× statement); 6.4 (cut rationale); 8, Fig. 6 with the reach tables and the K-factor figure (neither existed in 16 v2); 9 and 9.1, Fig. 7 with the dE/dx definition test.
- Therefore "500× → 460×" and the withdrawn Fig. 7 claim are corrections only relative to 18 / 19 Oct, not to 16 v2.

## D59 (2026-10-21) Combined EW trigger value 0.163 removed from the report (user's request, with conditions)
- (1) Same definition: both EW 800 GeV samples were parsed with the same code (extract_pilot_data.parse_hepmc, trigger_proxy_pass = quirk_pair_pt_gev > 200, checked row by row in both CSVs). Their MG5/Pythia cards were diffed again today: the only difference is iseed (8002 Table I, 9504 Fig. 6). Both were generated before the 19 Oct change (Fig. 6 sample: 22 Sep; Table I sample: 25 Sep). The 19 Oct change concerned which efficiency Fig. 6 uses (matched count instead of the LO ratio), not the trigger definition.
- (2) Table I: 186/1045 = 0.178 ± 0.012; Fig. 6: 152/1024 = 0.148 ± 0.011 (binomial). The difference is 0.030 ± 0.016, i.e. 1.8σ: consistent at the 2σ level used in the report.
- (3) 0.163 entered no calculation. Table I uses 186/1045, and Fig. 6 uses its own per-mass counts; 0.163 appeared only in text (Sec. 2.3 "Why" and "Result", the Sec. 8 bullet, the F6_fig6 figure caption, fig6/README_FIG6.md).
- Following the user's rule ("if 0.163 is not used anywhere, remove it"): new TABLE_I_REPRODUCTION_REPORT_2026-10-21_v2.pdf (scripts/R_report_2026-10-21_v2.py). Sec. 2.3 is back to 0.18 as in 16 Oct v2; the Fig. 6 sample value 0.148 ± 0.011 is stated separately with its reason (Fig. 6 takes all efficiencies of a point from one sample) and the 1.8σ difference. The Sec. 8 bullet has the same text. No number in any table changed. TABLE_I_REPRODUCTION_REPORT_2026-10-21.pdf is kept.
- Not changed: the F6_fig6 figure caption (not shown in the report since D56; changing it would mean regenerating the figure) and fig6/README_FIG6.md (dated history). Both still quote 0.163.
