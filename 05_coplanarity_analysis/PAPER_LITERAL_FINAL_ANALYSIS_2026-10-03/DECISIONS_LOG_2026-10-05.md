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
