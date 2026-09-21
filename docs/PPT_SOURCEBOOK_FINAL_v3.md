# PPT Sourcebook — Final v3 (2026-09-21)

Corrects and expands `PPT_SOURCEBOOK_FINAL_v2.md` (does not overwrite it).
Incorporates: (1) the corrected, now-ACHIEVED Figure 3 reproduction
(supersedes v2's "NOT achieved" verdict — the prior result was a
measurement-definition bug, not real physics); (2) the regenerated
Figure 4 vertex-fixed reproduction (event 386, current pipeline); (3) the
frozen Figure 5 four-component + corrected-absolute package; (4) the
Figure 6 future-work grid proposal (still not executed); (5) a full
global stale-value correction pass.

---
## Slide 1 — Title
- Tracking Down Quirks at the LHC — Independent Reproduction
- Based on arXiv:1708.02243v2 (Knapen, Lou, Papucci, Setford)
**Figure:** none · **Source:** paper.txt p.1 · **Speaker notes:** frame as independent reproduction/audit, not new physics. · **Limitation:** —

## Slide 2 — Research Objective and Reproduction Scope
- Reproduce Sec. IIIC coplanarity methodology, signal/background cutflows, Figs. 1–7, Table I
- Paper has exactly **7 figures** (not 10) — confirmed by direct page inspection
- Scope explicitly excludes new large Monte Carlo production this task
**Figure:** none · **Source:** this document · **Speaker notes:** state the 7-figure correction up front. · **Limitation:** —

## Slide 3 — What Are Quirks?
- HSCP pairs bound by a confining flux tube (Nambu-Goto string, Eq. 2)
- Regime: mQ ≫ Λ, quirk pair remains connected, oscillates rather than hadronizing apart
- Benchmarks: Colored (3,1)_2/3 QCD production; EW (1,1)_1 Drell-Yan production
**Equation:** S = -mQ Σ∫dτᵢ - Λ²∫dA + S_ext (Eq.2) · **Figure:** none · **Source:** paper.txt Sec II · **Limitation:** —

## Slide 4 — Why Quirk Trajectories Are Approximately Coplanar
- Pair produced with negligible angular momentum → trajectories stay on a plane
- B-field torque induces large L (~10¹²ℏ) but tiny plane rotation (Δφ≲10⁻³)
- Strategy: search for coplanar hit pairs across 8 tracker layers
**Equation:** Eq. 5–9 · **Figure:** `figure1_schematic_v1/Figure_1_reproduced_v1.png` (full-slide) · **Source:** paper.txt Sec II · **Limitation:** schematic is project-native, not paper's bitmap

## Slide 5 — Figure 1: Project Schematic
- Green: quirk pair trajectories · Blue: ISR jet · Gray: 3 tracker layer cylinders
- Black dots: hits, all exactly on the shaded red plane
- Label: *"Project schematic inspired by Paper Figure 1 — conceptual, not simulated data."*
**Figure:** `figure1_schematic_v1/Figure_1_reproduced_v1.png` · **Source:** `figure1_schematic_v1/figure1_metadata_v1.json` · **Speaker notes:** visually verified all hits lie exactly on the shaded plane by construction. · **Limitation:** conceptual only, no numeric result.

## Slide 6 — Figure 2/3: Trajectory Dynamics — BOTH ACHIEVED (CORRECTED 2026-09-21)
- Figure 2: L and d vs radial CM distance r — achieved, L~10¹²ℏ matches paper's order of magnitude
- **Figure 3: Δφ vs r — now ACHIEVED (APPROXIMATE), correcting the prior "NOT achieved" verdict.** Root cause of the earlier failure: the prior measurement used the WRONG observable (internal angular momentum direction) and, even after switching to the paper's own definition (rotation of the plane spanned by the quirks' velocity vectors, v1×v2), an over-loose validity threshold let numerical noise at near-degenerate crossings dominate the reported maximum. Neither was a real physical degeneracy.
- Corrected result: the SAME simple, unperturbed configuration used for Figure 2 reproduces Δφ(r) with max ≈4.6×10⁻⁴ rad (colored) / 6.1×10⁻⁴ rad (EW) — within the paper's own stated range (Eq.9 ~10⁻⁵, text "not larger than 10⁻³", Fig.3 y-axis 0–4×10⁻⁴) and the correct qualitative shape (rises from 0, oscillates, plateaus)
- Paper's own caption for Fig.3 literally reads "Δθ" but its axis label and Eq.8–9 both use "Δφ" — verified paper-internal inconsistency (unchanged from v2)
**Figure:** `figure2_figure3_v1/Figure_2_reproduced_v1.png`; `figure3_diagnostic_v2/Figure_3_diagnostic_v2.png` · **Source:** `figure3_diagnostic_v2/README.md`, `figure3_diagnostic_metadata_v2.json` · **Speaker notes:** emphasize this was a measurement bug fix, not new physics discovered — worth flagging as a QA lesson. · **Limitation:** initial orientation (boost/tilt relative angle) is a project assumption, not read from a specific ISR-recoil event; residual angle-unwrapping spike artifacts at a few isolated r values, documented not hidden; d touches 0 at r≈4.2cm in Fig.2, in tension with paper's "never vanishes except at origin" claim (unchanged from v2).

## Slide 7 — Signal Benchmarks and Production Channels
- Colored: mQ=1.8TeV, Λ=2keV, QCD pair production
- EW: mQ=800GeV, Λ=4keV, Drell-Yan
- Both generated via MadGraph5_aMC@NLO + Pythia8, MLM matching (xqcut=30GeV)
**Table:** `final_freeze_v1/master_cutflow_table.csv` · **Source:** MadGraph banners · **Limitation:** —

## Slide 8 — Trigger, ISR Recoil, Quirk Equation of Motion
- Trigger proxy: pT(pair)>200GeV (truth-level, project simplification vs. paper's real HLT/MET trigger)
- Eq. 3: Nambu-Goto EOM with Lorentz-force external term
- Eq. 4: exact B=0 analytic solution, validated to 1e-12
**Equation:** Eq. 3, Eq. 4 · **Source:** paper.txt Sec II, `validate_against_eq4.py` · **Limitation:** trigger proxy ≠ paper's real trigger simulation.

## Slide 9 — RK4 Propagation and Validation
- Fixed-step RK4, string+Lorentz force, validated against Eq.4 (B=0) to 1e-12
- Gyroradius cross-check for pure Lorentz force: 4e-5 precision
- Adaptive step coarsening with a validated 300-steps/period floor
**Figure:** `docs/report/figs/fig2_rk4_convergence.png` (project-internal validation, not a paper figure) · **Source:** `03_trajectory_sim/quirk_trajectory.py` · **Limitation:** —

## Slide 10 — Simplified Eight-Layer Detector Geometry
- 8-layer ATLAS-like barrel (4 pixel + 4 SCT), no endcap/TRT/ECAL
- B=2T solenoid field
- |η|<1.8 fiducial acceptance
**Table:** layer radii, `atlas_geometry.py` · **Source:** code · **Limitation:** barrel-only simplification (documented throughout project).

## Slide 11 — Hit Formation, Acceptance, 25ns Timing
- Hits formed at each layer crossing, η/timing cuts applied inline
- 25ns fiducial timing cut (Sec IV, post-Eq.12)
- Per-hit η/timing rejection counts NOT separately logged (pre-existing limitation)
**Source:** `trajectory_to_hits.py` · **Limitation:** per-hit rejection reasons unavailable without a rerun.

## Slide 12 — Pixel Quantization, Clustering, SCT Smearing
- Pixel hits quantized to effective resolution; SCT hits Gaussian-smeared
- Neighboring-pixel merge applied exactly once (validated, re-used correctly in the overlay driver)
**Source:** `trajectory_to_hits.py::merge_neighboring_pixel_hits` · **Limitation:** —

## Slide 13 — Sec. IIIC: Plane Definition, Δs, Δw
- T_ij tensor (Eq.11), eigen-decomposition
- Δs² = smallest eigenvalue (thickness); Δw² = second (width); n3 = flight direction
**Equation:** Eq. 10, Eq. 11 · **Source:** `coplanarity_fit.py` · **Limitation:** —

## Slide 14 — Seeding and Iterative Plane Finding
- Seed from layers 7&8 (Δφ<0.1, Δz<2cm), 4-hit combos, Δs<0.05cm, Δw<1cm
- Iterative outside-in add (layers 6→1), growth factor ≤3
- Event Selection: Δw<1cm, keep smallest Δs
**Source:** `coplanarity_fit.py::seeding_and_iterative_fit` · **Limitation:** —

## Slide 15 — Sec. IV: Hit-Multiplicity and Final Cuts
- Cut 1: ≥1 plane reconstructed · Cut 2: all-but-one layer ≥2 hits, remaining ≥1 · Cut 3: Δw<1cm & Δs<0.01cm
- **ε_reco = Sec. IIIC plane-found efficiency only** (paper's own Eq.12 definition)
- **Sec. IV final-pass rate** = the stricter, complete result — never the same quantity
**Equation:** Eq. 12 · **Source:** paper.txt Sec IV · **Limitation:** —

## Slide 16 — Figure 4: Representative Event Reproduction (Vertex-Fixed Pipeline) — 2026-09-21
- Deterministic single-event replay: event 386, colored benchmark, current vertex-fixed pipeline. Δs=0.009367cm, Δw=0.242530cm — bit-identical match to the pre-existing authoritative cutflow CSV row, confirming reproducibility
- **Δs vs paper (0.0083cm): 1.13× — close agreement**, consistent with detector-resolution-dominated behavior working correctly
- **Δw vs paper (0.074cm): 3.28× — larger discrepancy, root cause verified (not assumed):** the real 3D separation between the two quirks' hit positions at each layer (measured directly: 0.25–0.73cm) is 1–2 orders of magnitude larger than any detector resolution effect, proving this is TRAJECTORY-LEVEL kinematic variation for this specific event, not a detector-modeling artifact
- "Event 12" (as referenced in earlier task framing) could not be located in the current authoritative colored-quirk cutflow CSV; event 386 was substituted as the closest Δs match to the paper's reference value among the 5 Sec IIIC plane-found colored events, and is also the sole Sec IV final-pass event — documented, not silently substituted
- Old `fig4_data_v2.json`/`fig4_best_candidate_v2.pkl` remain CONFIRMED OBSOLETE (predate the vertex-relative-fit correction, commit b8f017f) — unchanged from v2
**Figure:** `figure4_vertex_fixed_v1/Figure_4_reproduced_vertex_fixed_v1.png` · **Source:** `figure4_vertex_fixed_v1/README.md`, `figure4_vertex_fixed_v1/Figure_4_metadata_v1.json` · **Speaker notes:** emphasize the per-layer separation measurement as the concrete evidence for the trajectory-variation conclusion — this was verified, not assumed. · **Limitation:** single-event result; paper does not publish which exact event/momenta correspond to its own Fig.4, so exact numerical agreement is not expected.

## Slide 17 — Colored Quirk Cutflow
- 419 matched → 125 charge-filtered → 27 trigger → 7 fiducial → 5 planes → 3 multiplicity → **1 final**
- ε_trig=0.216, ε_fid=0.259, ε_reco=0.714 (**N=7, statistically inconclusive**), Sec.IV final-pass=0.143
- Weight = 7.5036×10⁻⁴ fb/event
**Table:** `final_freeze_v1/master_cutflow_table.csv` row 1 · **Source:** `colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv` · **Limitation:** N=7 too small to confirm/reject paper agreement.

## Slide 18 — EW Quirk Cutflow
- 511 matched → 89 trigger → 40 fiducial → 32 planes → 16 multiplicity → **6 final**
- ε_trig=0.174, ε_fid=0.449, ε_reco=0.800, Sec.IV final-pass=0.150
- Weight = 4.5738×10⁻⁴ fb/event
**Table:** `final_freeze_v1/master_cutflow_table.csv` row 2 · **Source:** `ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv` · **Limitation:** ε_trig/ε_fid tension vs. paper (Slide 19).

## Slide 19 — Table I: Paper vs. Project
| Benchmark | Quantity | Paper | Project |
|---|---|---|---|
| Colored | ε_trig / ε_fid / ε_reco | 0.24 / 0.28 / 0.35 | 0.216 / 0.259 / 0.714 (N=7, inconclusive) |
| EW | ε_trig / ε_fid / ε_reco | 0.10 / 0.28 / 0.72 | 0.174 / 0.449 / 0.800 |
**Figure:** `table1_extraction_v1/table1_crop_400dpi.png` · **Source:** PDF p.8, 2 independent transcriptions, 0 discrepancies · **Speaker notes:** colored trigger/fiducial consistent; EW trigger/fiducial tension unresolved; EW reconstruction consistent. · **Limitation:** overlapping rounded values ≠ proof of agreement.

## Slide 20 — Pile-up Modelling, Ancestry, Tracking Suppression
- ⟨μ⟩=50, 45mm beamspot, 20,000-event minbias pool (paper: 125,000), with replacement
- Ancestry-aware Bernoulli track suppression (Loose selection, ATL-PHYS-PUB-2015-051 curve)
**Source:** `pileup_hits_suppressed.py`, `ancestry_classifier.py` · **Limitation:** pool size simplification, documented.

## Slide 21 — Pile-up-Only Results
- μ=0,5,10,20,50: N_plane = 0, 3, 6, 22, 172 (of 5000 each)
- **Sec. IV final-pass = 0/5000 at every μ** (direct, not inferred) — "zero observed, not zero probability" (Wilson 95% UL≈7.68×10⁻⁴)
**Table:** pileup rows, master_cutflow_table.csv · **Source:** `pileup_mu{0,5,10,20,50}_n5000_sec3c_fullcutflow_v1.csv` · **Limitation:** —

## Slide 22 — Converted-Photon Model and 1% Weighting
- Z+γ+j, Z→νν, MET>200GeV, pT_γ>0.5GeV; fiducial σ≈1pb→~10fb after conversion probability
- 1% conversion probability applied as an END weight, never a stochastic filter, never double-counted
- Selected-plane fraction (conversion-only, no pile-up) = **2982/9139 = 0.3263** — NOT called ε_reco (background, not signal)
**Source:** `convert_and_analyze.py` · **Limitation:** —

## Slide 23 — Converted-Photon-Only vs. μ=50 Overlay
- Conversion-only: 9139 → 2982 planes → 4 multiplicity → 0 final
- **μ=50 overlay (paper-required): 9139 → 3276 planes → 203 multiplicity → 1 final**
- P_raw=1/9139=1.09421×10⁻⁴; **Wilson 95%=[1.93×10⁻⁵,6.20×10⁻⁴]**; P_weighted=0.01×(1/9139)=1.09421×10⁻⁶; σ_final,MC=2.3105×10⁻⁴ fb
**Table:** master_cutflow_table.csv, last 2 rows · **Source:** `conversion_with_pileup_mu50_v1.csv` · **Speaker notes:** runtime 14.79h, describe as "paper-matched overlay implementation with documented simplifications." · **Limitation:** single-event result.

## Slide 24 — Event 2555 Forensic Explanation
- μ=0: layers 1,2,5 deficient (3<2-hit layers, only 1 allowed) → FAIL, Δs=0.00582cm already <0.01cm
- μ=50: one primary pion, pT=0.242GeV, pool event 3628 particle 10, filled layers 1&2 → PASS, Δs=0.00910cm
- Under the implemented Loose tracking model, pT=0.242GeV<0.4GeV gives ε_track=0; therefore its hits were retained in the simulated unassociated-hit pool — **a statement about this project's implemented model, not a universal ATLAS fact**
**Figure:** `event_2555_forensic_v1/event2555_layer_comparison.png` · **Source:** `event_2555_forensic_v1/*` · **Limitation:** per-hit timing/η-rejection unavailable.

## Slide 25 — Figure 5: Frozen Four-Component Shape + Corrected Absolute Products (2026-09-21)
- **Product A (4-component, unit-area shape, AUTHORITATIVE)**: colored N=5, EW N=32, pileup_mu50 N=172 (full population, NOT the old biased N=59 subsample), converted-γ+pileup_mu50 N=3276 (full overlay, NOT the conversion-only N=2982)
- **Product B (3-component, CORRECTED absolute, AUTHORITATIVE)**: colored (7.5036×10⁻⁴ fb/evt, integral 3.7518×10⁻³ fb), EW (4.5738×10⁻⁴ fb/evt, integral 1.4636×10⁻² fb), converted-γ+PU (2.3105×10⁻⁴ fb/evt, integral 0.756924 fb); pile-up excluded (no cross-section concept)
- Both old versions are now OBSOLETE: the 2026-09-17 shape figure (biased pileup N=59, no converted-photon curve at all) and the no-suffix absolute plot (colored curve 3.352× too high, wrong N=125 denominator)
**Figure:** `figure5_final_freeze_v1/Figure_5_four_component_v2_AUTHORITATIVE.png`; `figure5_final_freeze_v1/Figure_5_absolute_three_component_v2_CORRECTED.png` · **Source:** `figure5_final_freeze_v1/README.md`, `SHA256_MANIFEST.json` · **Limitation:** absolute normalization not available for pile-up (structural); pile-up reweighting ambiguity (1-hit-per-layer denominator) unresolved for both products.

## Slide 26 — Figure 6/7: Confirmed Structural Blockers (Verified, Not Re-attempted)
- **Figure 6** (exclusion/discovery contours, mQ-Λ plane): 2 benchmark points cannot support a continuous contour — a 91-point future grid (7×7 colored + 6×7 EW, ≥2000 events/point, ≥182,000 total events) is proposed but **NOT executed**; missing components: full production σ(mQ,Λ) grid, luminosity-normalized discovery prescription, background treatment (paper assumes negligible, consistent with but not derived from this project's own measurements)
- **Figure 7** (dE/dx, Appendix A): BLOCKED — zero Bethe-Bloch/material-budget/path-length code exists anywhere in the repository (confirmed by exhaustive grep); implementing it was explicitly out of scope this task
**Source:** `converted_photon_with_pileup_v1/figure6_requirement_matrix.csv`, `figure6_figure7_blockers_v1/Figure_6_future_work_grid_proposal_v1.md`, `figure_inventory_v2/Figure_7_NOT_REPRODUCIBLE.md` · **Limitation:** neither figure was reproduced; this slide documents why, not a result.

## Slide 27 — Conclusions, Limitations, Next Steps
- **Conclusions:** EW ε_reco (0.800) tracks paper (0.72) closely; colored ε_reco inconclusive (N=7); first-ever nonzero converted-γ+pileup result, traced to one 0.242GeV pion, not tuned; Figure 3 "degeneracy" was a measurement bug, now corrected and achieved; Figure 4 regenerated via targeted deterministic replay (event 386)
- **Limitations:** Fig.6/7 structurally blocked; pool-size simplification; EW trigger/fiducial tension unresolved; Fig.3 initial orientation is a project assumption, not read from a real ISR-recoil event; Fig.3 plot has residual angle-unwrapping spike artifacts, documented not hidden
- **Next steps (not started):** Fig.3 first-principles single-event replay (read real 4-momenta instead of parametric scan); Fig.6/7 require explicit new authorization and a dedicated runtime-gated task
**Table:** `figure_inventory_v2/completion_matrix_v1.csv` · **Source:** this document

---
# APPENDIX SLIDES

## A1 — Figure 1–3 Reproduction Details
- Fig.1: pure matplotlib schematic, no simulation
- Fig.2: 1 event, ~16s wall time, tilt=[0,0,1] (degenerate but physically sane for L,d)
- Fig.3: corrected 2026-09-21 — same tilt=[0,0,1] configuration as Fig.2, properly measured via v1×v2 plane rotation with percentile-filtered validity — achieved, magnitude and shape match paper's stated range
**Source:** `03_trajectory_sim/figure1_schematic_v1.py`, `figure2_figure3_reproduction_v1.py`, `figure3_diagnostic_v2.py`

## A2 — Wilson-Interval Bug (QA)
- Missing leading z-multiplier in margin formula → CI too narrow to contain point estimate
- Caught on k=1,n=9139: wrong [1.66×10⁻⁴,4.73×10⁻⁴] → corrected [1.93×10⁻⁵,6.20×10⁻⁴]
- Regression test added, 5/5 pass (re-verified 2026-09-21)
**Source:** `docs/wilson_interval_bug_correction_v1.md`, `tests/test_wilson_interval_regression.py`

## A3 — Figure 3 Measurement-Bug QA (NEW, 2026-09-21)
- Two compounding bugs in how Δφ was measured (not physics): wrong observable (L instead of v1×v2), then an over-loose numerical validity threshold that let near-degenerate-crossing noise dominate a naive max() statistic
- Fixed via percentile-based exclusion of near-crossing samples; same unperturbed Fig.2 configuration then reproduces Fig.3's magnitude and shape
- Residual angle-unwrapping spike artifacts remain at a few isolated r values — documented, a concrete next-step fix identified (running angular-velocity integral instead of post-hoc arccos)
**Source:** `figure3_diagnostic_v2/README.md`, `figure3_diagnostic_metadata_v2.json`

## A4 — Authoritative/Obsolete File Inventory
- Full classification of every major CSV/plot: AUTHORITATIVE / OBSOLETE / SUPERSEDED
- Updated 2026-09-21: figure5_final_freeze_v1 products added as AUTHORITATIVE; 2026-09-17 Fig.5 shape figure reclassified OBSOLETE (was incorrectly still marked AUTHORITATIVE in the prior inventory version — corrected this task)
**Source:** `final_freeze_v1/authoritative_obsolete_file_inventory.csv`

## A5 — Detailed Confidence Intervals
- Wilson 68%/95%, Clopper-Pearson 68%/95% for every efficiency in the master table
**Source:** `ppt_statistics_v1/ew_complete_statistics.json`, `colored_complete_statistics.json`

## A6 — Figure 6 Requirement Matrix + Future-Work Grid Proposal
- Full mQ-Λ grid, cross-section, efficiency, luminosity, background-assumption requirements
- 2 benchmark points only — cannot be interpolated into a contour
- NEW: concrete future grid proposal (91 points, ≥182,000 events, order-of-magnitude runtime estimate) — proposal only, NOT executed
**Source:** `converted_photon_with_pileup_v1/figure6_requirement_matrix.csv`, `figure6_figure7_blockers_v1/Figure_6_future_work_grid_proposal_v1.md`

## A7 — Figure 7 Status (only Fig.7 exists; no Fig.8-10)
- BLOCKED: no Bethe-Bloch/material-budget code anywhere in repo
**Source:** `figure_inventory_v2/Figure_7_NOT_REPRODUCIBLE.md`

## A8 — Detector Parameters
- 8-layer barrel, B=2T, |η|<1.8, 25ns timing, Loose tracking efficiency curve
**Source:** `atlas_geometry.py`, `tracking_efficiency.py`

## A9 — Runtime/Resources Summary
- Photon+PU overlay: 53240.8s (14.79h) · Pileup sweep (all μ): ~24700s total · Fig.2/3: ~1min (Fig.2) + ~11 configs × ~15-30s (Fig.3 diagnostic scan) · Fig.4 replay: 4115.4s (~68.6 min; documented worst-case low-boost-event step count, existing validated code path, unmodified)
**Source:** provenance JSONs throughout

## A10 — Complete Assumptions Table
- 20k vs 125k pool · trigger proxy · pile-up reweighting ambiguity · barrel-only detector · no dE/dx · Fig.3 initial orientation not read from a real ISR-recoil event · Fig.4 event substitution (event 386 for referenced "event 12")
**Source:** all prior audit docs, this sourcebook
