# PPT Sourcebook — Final v5 (2026-09-21)

New file (v4 untouched). Consolidates the complete, independently
re-verified project state as of the FINAL CONSOLIDATED PHYSICS REPORT.
All numbers below were recomputed from authoritative files this session,
not copied from prior chat summaries. Text slides only, no PPTX.

---
## Slide 1 — Title
- Tracking Down Quirks at the LHC — Independent Reproduction, Final Consolidated Freeze
- Based on arXiv:1708.02243v2 (Knapen, Lou, Papucci, Setford)
**Source:** paper PDF, reread in full this session · **Limitation:** —

## Slide 2 — Scope and Methodology Overview
- Reproduce Sec. IIIC coplanarity search: signal simulation, background modeling, detector response, plane-finding, Sec. IV cuts
- Every number in this deck independently recomputed from authoritative CSVs/JSONs this session
- Nothing in this project is claimed exact — every figure/number is labeled approximate or carries a statistical caveat
**Source:** `docs/FINAL_CONSOLIDATED_PHYSICS_REPORT_v1.md`

## Slide 3 — Quirk Physics
- Nambu-Goto confining string + Lorentz force (Eq.3), validated against exact B=0 solution (Eq.4) to 9.26e-13
- Benchmarks: Colored (3,1)_2/3 QCD (mQ=1.8TeV,Λ=2keV); EW (1,1)_1 Drell-Yan (mQ=800GeV,Λ=4keV)
**Source:** `03_trajectory_sim/quirk_trajectory.py`, `validate_against_eq4.py`

## Slide 4 — Trajectory Propagation Validation
- RK4, validated: Eq.4 (9.26e-13), dt-convergence (<1e-4 rel. err down to 30 steps/period, 300 used), exact-helix (4/4, max pos diff 1.2e-7cm)
- Step count scales ~1/Λ² (period~1/Λ² at the steps/period floor) — confirmed empirically (7.1x slower at 5keV vs 2keV)
**Source:** `validate_dt_convergence.py`, `validate_helix.py`

## Slide 5 — Recovered Generator Configuration
- Original MadGraph5_aMC@NLO 3.7.3 + Pythia8 cards located and preserved (outside git originally, never before version-controlled)
- Colored: 1000 LHE → 419 matched (41.9%). EW: 1000 LHE → 511 matched (51.1%). Seed=21 both. PDF=NNPDF2.3LO. xqcut=30GeV
- Paper does not publish PDF/scale/seed — this project's own choices, now fully preserved
**Source:** `madgraph_pilot_v1/metadata/GENERATOR_CONFIGURATION_SUMMARY.md`

## Slide 6 — Detector Model
- 8-layer ATLAS-like barrel (4 pixel+4 SCT), B=2T, |η|<1.8, 45mm beamspot, 25ns timing
- Pixel=pixel-pitch resolution, SCT=2x intrinsic (paper's own conservative choice)
- Barrel-only (no endcap/TRT/calo) — documented simplification
**Source:** `atlas_geometry.py`; D1-D10 corrections suite 10/10 PASS (re-run this session)

## Slide 7 — Sec. IIIC Reconstruction
- T_ij tensor, eigen-decomposition: Δs=smallest eigenvalue, Δw=second, n3=flight direction
- Seed layers 7&8, iterative outside-in, selected plane = smallest Δs among Δw<1cm
**Source:** `coplanarity_fit.py`

## Slide 8 — Sec. IV Final Cuts
- Plane found + hit-multiplicity (all-but-one-layer≥2, remaining≥1) + Δw<1cm + Δs<0.01cm
- ε_reco = Sec.IIIC plane-found rate, CONDITIONAL on trigger+fiducial (paper's own Eq.12 definition, verified word-for-word)
**Equation:** Eq.12 · **Source:** paper p.7

## Slide 9 — Colored Signal Complete Cutflow
- 419 matched → 125 charge-filtered (29.8%, matches paper's ~30%) → 27 trigger → 7 fiducial → 5 planes → 3 mult. → **1 final** (event 386)
- ε_trig=0.216, ε_fid=0.259, ε_reco=0.714 (N=7)
**Source:** `FINAL_CONSOLIDATED_REPORT_v1/tables/04_colored_complete_cutflow.csv`

## Slide 10 — EW Signal Complete Cutflow
- 511 matched → 89 trigger → 40 fiducial → 32 planes → 16 mult. → **6 final** (events 260,313,322,332,362,438)
- ε_trig=0.174, ε_fid=0.449, ε_reco=0.800
**Source:** `FINAL_CONSOLIDATED_REPORT_v1/tables/05_ew_complete_cutflow.csv`

## Slide 11 — Table I: Full Statistical Comparison
| Benchmark | Quantity | k/n | Project | Paper | Wilson95 | Verdict |
|---|---|---|---|---|---|---|
| Colored | trig | 27/125 | 0.216 | 0.24 | [0.153,0.296] | CONSISTENT |
| Colored | fid | 7/27 | 0.259 | 0.28 | [0.132,0.447] | CONSISTENT |
| Colored | reco | 5/7 | 0.714 | 0.35 | [0.359,0.918] | INSUFFICIENT STATS (N=7) |
| EW | trig | 89/511 | 0.174 | 0.10 | [0.144,0.210] | TENSION |
| EW | fid | 40/89 | 0.449 | 0.28 | [0.350,0.553] | TENSION |
| EW | reco | 32/40 | 0.800 | 0.72 | [0.652,0.895] | CONSISTENT |
**Source:** `06_tableI_comparison.csv`, `17_statistical_intervals.csv`

## Slide 12 — EW Discrepancy: Audited, No Bug Found
- Cut definitions/denominators independently verified exact vs. paper text (word-for-word)
- Root cause: hypothesized (undocumented MC settings + DY pT-spectrum merging-scale sensitivity), NOT proven — neither side's exact settings are published/recoverable
- Colored (QCD) shows no such tension, consistent with this hypothesis
**Source:** `ew_discrepancy_audit_v1/EW_trigger_fiducial_discrepancy_audit_v1.md`

## Slide 13 — Pile-up Model and Poisson Validation
- ⟨μ⟩=50 nominal, 45mm beamspot, 20k-event pool (paper: 125k, documented simplification)
- Poisson mean/variance at μ=5,10,20,50: (4.97/4.97), (10.05/9.77), (20.04/19.60), (49.96/49.72) — all consistent with mean=variance=μ
**Source:** `07_pileup_poisson_statistics.csv`

## Slide 14 — Pile-up Tracking Suppression Statistics
| μ | Removed | Retained | Secondary | Ambiguous | Mean hits raw→retained |
|---|---|---|---|---|---|
| 5 | 309,736 | 438,493 | 82,503 | 37 | 1175→718 |
| 10 | 625,555 | 885,978 | 166,673 | 54 | 2373→1450 |
| 20 | 1,252,942 | 1,766,590 | 332,175 | 132 | 4741→2891 |
| 50 | 3,127,150 | 4,413,275 | 830,664 | 329 | 11843→7224 |
**Source:** `08_pileup_tracking_statistics.csv`

## Slide 15 — Pile-up-Only Complete Cutflow
- N=5000/μ (25,000 total bunch crossings). Planes: 0,3,6,22,172. **Final Sec IV: 0 at every μ**
- "Zero observed, not zero probability" — Wilson 95% UL = 7.68e-4 at μ=50
**Source:** `09_pileup_complete_cutflow.csv`

## Slide 16 — Pile-up vs. Paper: Correct Interpretation
- Paper ≥4/8 rate ~1e-3; project 59/5000=1.18e-2 — **≈11.8x paper, does NOT numerically reproduce it**
- Paper 8/8 rate ~6e-5; project 0/5000 — **insufficient statistics to test this** (Wilson 95% UL=7.68e-4)
- Final Sec IV rejection (0/5000 always) IS qualitatively consistent with paper's negligible-background assumption
- These are NOT directly comparable to the paper's intermediate coverage rates
**Source:** `10_pileup_paper_comparison.csv`

## Slide 17 — Converted-Photon-Only Result (μ=0 Baseline)
- Z+γ+j, Z→νν, MET>200GeV, pT_γ>0.5GeV (paper's exact criteria, verified word-for-word)
- 10000 raw → 9139 usable → 7811 with hits → **2982 selected planes** → 4 mult. → **0 final**
- Selected-plane fraction = 2982/9139 = 0.3263 — background quantity, NOT ε_reco
- Runtime: 16934.9s (4.704h)
**Source:** `11_converted_photon_only_cutflow.csv`

## Slide 18 — Converted-Photon + Pile-up μ=50 (Paper-Required)
- 9139 → **3276 planes** → **203 mult.** → **1 final** (event 2555)
- P_raw=1.09421e-4; P_weighted(1%)=1.09421e-6; σ_final=2.3105e-4 fb
- **Wilson 95%=[1.93e-5,6.20e-4]** (corrected, old wrong [1.66e-4,4.73e-4] confirmed absent everywhere live)
- Runtime: 53240.8s (14.79h). "One event does not establish agreement with the paper."
**Source:** `12_converted_photon_overlay_cutflow.csv`, `17_statistical_intervals.csv`

## Slide 19 — Event 2555 Forensic Explanation
- Pool event 3628, particle 10: charged pion, pT=0.242GeV, primary. Loose ε_track=0 below 0.4GeV → hits retained in unassociated pool (project-model-specific statement)
- μ=0: Δs=0.00582cm (already<0.01) but layers 1,2,5 fail multiplicity (3 deficient, only 1 allowed) → FAIL
- μ=50: pion hits fill layers 1,2 → PASS. Δs=0.00910cm. Plane preserved+enlarged, not replaced (0.371° rotation)
**Source:** `13_event2555_forensic_summary.csv`

## Slide 20 — Figure 1: Schematic
- Conceptual, not simulated data. Green trajectories, blue ISR jet, hits on shaded plane
**Figure:** `FIGURE_1_FINAL_Quirk_Schematic.png`

## Slide 21 — Figure 2: Diagnostic
- L~1e12ℏ, matches paper order of magnitude. Paper's exact initial conditions unavailable
**Figure:** `FIGURE_2_FINAL_Angular_Momentum_Separation_DIAGNOSTIC.png`

## Slide 22 — Figure 3: Corrected Plane Rotation
- Uses paper's own v1×v2 observable (not the earlier wrong angular-momentum proxy)
- Max Δφ≈4.6e-4/6.1e-4 rad, matches paper's stated range
**Figure:** `FIGURE_3_FINAL_Plane_Rotation.png`

## Slide 23 — Figure 4: Vertex-Fixed Event 386
- Δs=0.009367cm (1.13x paper 0.0083cm, close). Δw=0.242530cm (3.28x paper 0.074cm)
- Root-caused: real 3D quirk-quirk separation 0.25-0.73cm at each layer — genuine trajectory variation, not a detector bug
- Event 386 is a documented substitute for the paper's unlocatable "event 12"
**Figure:** `FIGURE_4_FINAL_Reconstructed_Event_VERTEX_FIXED.png`

## Slide 24 — Figure 5: Shape + Corrected Absolute
- 4-component: colored N=5, EW N=32, pileup N=172, converted-γ+PU N=3276 (not N=2982)
- Paper's own design confirmed: Δs panel absolute, Δw panel unit-normalized (this project provides both a unit-area 4-component AND a corrected absolute 3-component product)
- Absolute: colored 7.5036e-4 fb/evt (N=419), EW 4.5738e-4 (N=511), converted-γ+PU 2.3105e-4 (N=9139)
**Figures:** `FIGURE_5_FINAL_*`, `FIGURE_5A/B/C_FINAL_*`

## Slide 25 — Figure 6: Not Reproduced, Optimized Runtime Ready
- Paper: 300fb⁻¹, colored reach~1600GeV, EW reach~650GeV, Λ 100eV-30keV (documented, NOT project results)
- RK4 = 99.96-99.98% of downstream wall time (7/7 events). Optimized: 16.87x mean speedup, 6/6 exact+bit-identical
- Revised estimate: 437.7h → **~37.9h** (91.3% reduction). **No grid launched.**
**Source:** `perf_profile_v1/README.md`, `runtime/REVISED_FIGURE6_ESTIMATE.json`

## Slide 26 — Figure 7: Not Reproduced
- Standalone Bethe-Bloch validated (10/10 tests, 1.8% agreement with PDG MIP reference)
- Material budget/path-length unavailable — validation alone does NOT reproduce the figure. Nothing invented
**Source:** `figure7_dedx_feasibility_v1/README.md`

## Slide 27 — Bugs Found and Corrected (8 total)
- Wilson missing-z; colored weight wrong denominator (125→419); Fig.5 biased pileup (N=59→172); Fig.5 missing overlay curve; pre-vertex-fix Fig.4; Fig.3 wrong observable; EW charge backwards; EW vertex-transform missing
- 2 more found and fixed THIS session: stale xsec_and_weights_summary.json; eps_reco column mislabeled for background rows in 3 CSVs
**Source:** `19_bugs_and_corrections.csv`

## Slide 28 — Overall Verdict by Category
- **A. Core physics/reconstruction:** verified correct, Eq.3/4 to 9.3e-13
- **B. Signal efficiencies:** 4/6 Table I quantities consistent/inconclusive; EW trig/fid tension (audited, unexplained)
- **C. Background rejection:** final rates qualitatively consistent; intermediate rates not directly comparable
- **D. Full reach/all-figure reproduction:** Figs 1-5 approximate; Figs 6-7 not reproduced, Fig.6 path now optimized
**Source:** `docs/FINAL_CONSOLIDATED_PHYSICS_REPORT_v1.md` §28

## Slide 29 — Limitations and Assumptions
- Pool size (20k vs 125k), barrel-only detector, unpublished MC settings both sides, Fig.3 initial-orientation assumption, Fig.4 event substitution, Fig.5 pileup-reweighting ambiguity unresolved
**Source:** `18_limitations_and_assumptions.csv`

## Slide 30 — Exact Next Recommended Action
- Launch a bounded 2-3-mass-point Figure 6 pilot (not the full 91-point grid) using the optimized (16.87x) pipeline and recovered generator config, as a dedicated future task with explicit authorization
**Source:** `docs/FINAL_CONSOLIDATED_PHYSICS_REPORT_v1.md` §41

---
# APPENDIX SLIDES

## A1 — Full Authoritative File Inventory
**Source:** `01_authoritative_file_inventory.csv` — 15/15 FINAL_FIGURES_FOR_PPT hashes re-verified OK this session

## A2 — Paper-to-Code Requirement Matrix (25 items)
**Source:** `02_paper_to_code_matrix.csv`

## A3 — Generator Statistics
**Source:** `03_generator_statistics.csv`

## A4 — Statistical Intervals (10 quantities, Wilson 68/95 + CP95)
**Source:** `17_statistical_intervals.csv`

## A5 — Runtime and Resources Summary
**Source:** `16_runtime_and_resources.csv`

## A6 — Figure 5 Population and Normalization Detail
**Source:** `14_figure5_population_and_normalization.csv`

## A7 — Remaining Work
**Source:** `20_remaining_work.csv`

## A8 — References
- arXiv:1708.02243v2 (primary paper); arXiv:1612.00850 (detector sim basis, ref 34); ATL-PHYS-PUB-2015-051 (tracking efficiency, ref 33); PDG Review of Particle Physics (dE/dx, ref 35)
