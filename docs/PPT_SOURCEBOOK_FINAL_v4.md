# PPT Sourcebook — Final v4 (2026-09-21)

Corrects and expands `PPT_SOURCEBOOK_FINAL_v3.md` (v3 untouched, new file).
All figure references now point exclusively at
`05_coplanarity_analysis/FINAL_FIGURES_FOR_PPT/` per this task's
requirement. Incorporates: the EW trigger/fiducial discrepancy audit
verdict (no bug found), the colored-statistics feasibility verdict (no
run launched), Figure 6 readiness/pilot findings, and the Figure 7
Bethe-Bloch feasibility module. Text slides only, no PPTX.

---
## Slide 1 — Title
- Tracking Down Quirks at the LHC — Independent Reproduction
- Based on arXiv:1708.02243v2 (Knapen, Lou, Papucci, Setford)
**Figure:** none · **Source:** paper PDF p.1 · **Limitation:** —

## Slide 2 — Research Objective and Reproduction Scope
- Reproduce Sec. IIIC coplanarity methodology, signal/background cutflows, Figs. 1–7, Table I
- Paper has exactly **7 figures** — reconfirmed this task by direct 10-page PDF extraction
- Nothing in this project is claimed as an EXACT reproduction — every figure/number is labeled approximate or carries a statistical-consistency caveat
**Figure:** none · **Source:** `docs/FINAL_PAPER_REPRODUCTION_REPORT_v1.md` · **Limitation:** —

## Slide 3 — What Are Quirks?
- HSCP pairs bound by a confining flux tube (Nambu-Goto string, Eq. 2)
- Benchmarks: Colored (3,1)_2/3 QCD production; EW (1,1)_1 Drell-Yan production
**Equation:** Eq.2 · **Source:** paper Sec II · **Limitation:** —

## Slide 4 — Trigger and Fiducial Definitions (re-verified this task)
- Trigger: pT(quirk-pair CM)>200GeV — verified this task to be the paper's EXACT criterion (page 4, word-for-word), not an approximation as earlier project docs implied
- Fiducial: each quirk crosses all 8 layers within |eta|<1.8, within 25ns of the interaction — verified exact (page 7, word-for-word)
- ε_reco = plane-found efficiency, CONDITIONAL on trigger AND fiducial (paper's own Eq.12 definition, verified)
**Source:** paper Sec IIIB/IV, `docs/FINAL_PAPER_REPRODUCTION_REPORT_v1.md` Sec.8 · **Limitation:** —

## Slide 5 — Figure 1: Project Schematic
- Green: quirk trajectories · Blue: ISR jet · Gray: tracker layers · Black dots: hits on shaded plane
**Figure:** `FINAL_FIGURES_FOR_PPT/PNG/FIGURE_1_FINAL_Quirk_Schematic.png` · **Status:** conceptual, illustrative only

## Slide 6 — Figure 2/3: Trajectory Dynamics — BOTH ACHIEVED
- Figure 2: L~10¹²ℏ, matches paper's order of magnitude
- Figure 3: Δφ max ≈4.6×10⁻⁴ (colored) / 6.1×10⁻⁴ (EW) rad — within the paper's stated range, correct qualitative shape. Corrects a prior "NOT ACHIEVED" verdict that was itself a measurement bug (wrong observable + over-loose numerical threshold), not real physics
**Figure:** `FINAL_FIGURES_FOR_PPT/PNG/FIGURE_2_FINAL_Angular_Momentum_Separation_DIAGNOSTIC.png`, `FIGURE_3_FINAL_Plane_Rotation.png` · **Limitation:** initial orientation is a project assumption; residual angle-unwrapping spikes documented

## Slide 7 — Signal Benchmarks and Production
- Colored: mQ=1.8TeV, Λ=2keV, QCD. EW: mQ=800GeV, Λ=4keV, Drell-Yan
- MadGraph5_aMC@NLO + Pythia8, MLM-matched — **PDF set/merging scale/shower tune NOT specified by the paper** (verified this task, full-text search), and not preserved in this project's own generation records either
**Source:** `final_tables_v1/10_cross_sections_and_weights.csv` · **Limitation:** generator settings unresolved both sides

## Slide 8 — RK4 Propagation and Validation
- Validated against Eq.4 (B=0 exact) to 1e-12; 300-steps/period floor validated
**Source:** `quirk_trajectory.py`, `validate_dt_convergence.py`

## Slide 9 — Detector Geometry
- 8-layer ATLAS-like barrel, B=2T, |η|<1.8, 45mm beamspot
**Source:** `atlas_geometry.py`, ATLAS arXiv:2007.07624

## Slide 10 — Sec. IIIC: Coplanarity Fit
- T_ij tensor, Δs=smallest eigenvalue, Δw=second, n3=flight direction
**Source:** `coplanarity_fit.py`

## Slide 11 — Figure 4: Vertex-Fixed Event Reproduction
- Event 386 (colored), deterministic replay, bit-identical to authoritative CSV
- Δs=0.009367cm (1.13× paper's 0.0083cm) — close. Δw=0.242530cm (3.28× paper's 0.074cm) — root-caused to genuine per-event trajectory-level kinematic variation, verified via direct per-layer quirk-quirk separation measurement (0.25-0.73cm, 1-2 orders of magnitude above any detector-resolution effect)
**Figure:** `FINAL_FIGURES_FOR_PPT/PNG/FIGURE_4_FINAL_Reconstructed_Event_VERTEX_FIXED.png` · **Status:** approximate, single-event

## Slide 12 — Colored Quirk Cutflow
- 419 matched → 125 charged → 27 trigger → 7 fiducial → 5 planes → 3 mult. → **1 final** (event 386)
- ε_trig=0.216 (paper 0.24, CONSISTENT), ε_fid=0.259 (paper 0.28, CONSISTENT), ε_reco=0.714 (paper 0.35, N=7 too small to judge)
**Source:** `final_tables_v1/01_colored_complete_cutflow.csv`

## Slide 13 — Colored Statistics Feasibility (NEW this task)
- No unused matched-event reservoir exists (419 IS the complete matched sample)
- Extending to N_fiducial≈50 needs ~7.2× more matched events — a NEW MadGraph production, not a reuse of stored data
- **NOT launched** this task — MadGraph generation runtime is unknown/unbounded from stored history; exact future command documented
**Source:** `05_coplanarity_analysis/colored_statistics_feasibility_v1.md`

## Slide 14 — EW Quirk Cutflow
- 511 matched → 89 trigger → 40 fiducial → 32 planes → 16 mult. → **6 final** (events 260,313,322,332,362,438)
- ε_trig=0.174 (paper 0.10, TENSION), ε_fid=0.449 (paper 0.28, TENSION), ε_reco=0.800 (paper 0.72, CONSISTENT)
**Source:** `final_tables_v1/02_EW_complete_cutflow.csv`

## Slide 15 — EW Trigger/Fiducial Discrepancy Audit (NEW this task)
- Full 511-event audit table built; cut definitions/denominators independently verified EXACT vs. paper text
- **NO BUG FOUND.** Root cause: undocumented MC generation settings (neither paper nor project preserves them), compounded by Drell-Yan pT spectra's known sensitivity to merging-scale choices (vs. QCD production, which shows close agreement)
- Retained as unresolved modeling difference; no code changed
**Source:** `05_coplanarity_analysis/ew_discrepancy_audit_v1/EW_trigger_fiducial_discrepancy_audit_v1.md`

## Slide 16 — Table I: Paper vs. Project
| Benchmark | Quantity | Paper | Project | Verdict |
|---|---|---|---|---|
| Colored | trig/fid/reco | 0.24/0.28/0.35 | 0.216/0.259/0.714 | trig,fid CONSISTENT; reco N=7 inconclusive |
| EW | trig/fid/reco | 0.10/0.28/0.72 | 0.174/0.449/0.800 | trig,fid TENSION (audited); reco CONSISTENT |
**Source:** `final_tables_v1/03_paper_table1_comparison.csv`

## Slide 17 — Pile-up-Only Results
- μ=0,5,10,20,50: N_plane=0,3,6,22,172 of 5000 each. Final Sec IV: **0 at every μ**
- "Zero observed, not zero probability" (Wilson 95% UL≈7.68×10⁻⁴)
**Source:** `final_tables_v1/04_pileup_and_master_cutflow_all_mu.csv`

## Slide 18 — Converted-Photon Background and 1% Weighting
- Z+γ+j, Z→νν, MET>200GeV (paper's exact criterion, verified this task), pT_γ>0.5GeV
- Conversion-only: 9139→2982 planes→4 mult.→0 final. **μ=50 overlay: 9139→3276 planes→203 mult.→1 final** (event 2555)
**Source:** `final_tables_v1/06,07_*.csv`

## Slide 19 — Event 2555 Forensic Explanation
- One 0.242GeV pion (below the Loose-model 0.4GeV tracking threshold) fills layers 1&2 at μ=50, flipping the result from FAIL (μ=0) to PASS
**Source:** `final_tables_v1/08_event_2555_per_layer/`

## Slide 20 — Figure 5: Frozen Four-Component + Corrected Absolute
- 4-component shape: colored N=5, EW N=32, pileup_mu50 N=172, converted-γ+PU_mu50 N=3276
- Corrected absolute: colored 7.5036×10⁻⁴ fb/evt (N=419 denom.), EW 4.5738×10⁻⁴, converted-γ+PU 2.3105×10⁻⁴ fb/evt
**Figure:** `FINAL_FIGURES_FOR_PPT/PNG/FIGURE_5_FINAL_DeltaS_DeltaW_FOUR_COMPONENT.png`, `FIGURE_5C_FINAL_Absolute_Three_Component_CORRECTED.png`

## Slide 21 — Figure 6: Verified Grid Plan, Not Launched (updated this task)
- 91-point grid plan verified (axis coverage, checkpoint infra proven); colored+EW cross-sections both now recovered (0.0003144pb, 0.0002337pb) — corrects an earlier stale "colored xsec missing" entry
- **NOT launched**: generator settings unverifiable for the 2 existing points; physics-pipeline-only cost ≈425h alone; MadGraph generation cost unknown
- **FIGURE 6 NOT YET COMPLETE — VERIFIED GRID PLAN READY**
**Source:** `figure6_figure7_blockers_v1/Figure_6_readiness_and_pilot_v1.md`

## Slide 22 — Figure 7: Standalone Bethe-Bloch Validation (NEW this task)
- Paper explicitly did NOT use dE/dx in its own analysis (Appendix A, verified verbatim)
- Standalone Bethe-Bloch mean-dE/dx module built & validated: MIP dE/dx in Si = 1.694 vs PDG 1.664 MeV·cm²/g (1.8% agreement); 10/10 tests pass
- **NOT integrated** — material budget/path-length per layer unspecified by paper or project geometry; none invented
- **FIGURE 7 BLOCKED — MATERIAL MODEL NOT SPECIFIED/IMPLEMENTED**
**Source:** `figure7_dedx_feasibility_v1/README.md`

## Slide 23 — Conclusions and Next Steps
- Nothing claimed exact. Figures 1-5 approximate; Figs 6/7 blocked with verified readiness work
- EW discrepancy: audited, no bug, unresolved modeling difference
- Colored statistics: feasibility assessed, no unsafe run launched
- **Next steps:** reconstruct/archive MadGraph run_cards; benchmark generation time at small scale; if authorized, run the verified Fig.6 grid or digitize the Fig.7 material model
**Source:** `docs/FINAL_PAPER_REPRODUCTION_REPORT_v1.md` Sec.27

---
# APPENDIX SLIDES

## A1 — Full Figure 1-7 Completion Matrix
**Source:** `final_tables_v1/15_final_figure_1_to_7_completion_matrix.csv`

## A2 — Paper Requirement vs. Implementation Matrix (25 items, NEW this task)
**Source:** `final_tables_v1/12_paper_requirement_vs_implementation_matrix.csv`

## A3 — Assumptions and Limitations
**Source:** `final_tables_v1/13_assumptions_and_limitations.csv`

## A4 — Authoritative vs. Obsolete File Inventory
**Source:** `final_tables_v1/14_authoritative_vs_obsolete_file_inventory.csv`

## A5 — Statistical Intervals (Wilson/Clopper-Pearson, all stages)
**Source:** `final_tables_v1/09_statistical_intervals/`

## A6 — Bugs Found and Corrections (full project history)
**Source:** `docs/FINAL_PAPER_REPRODUCTION_REPORT_v1.md` Sec.23

## A7 — Runtime and Resources Summary
**Source:** `docs/FINAL_PAPER_REPRODUCTION_REPORT_v1.md` Sec.20
