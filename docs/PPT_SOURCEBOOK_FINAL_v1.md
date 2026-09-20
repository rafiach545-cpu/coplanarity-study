# PPT Sourcebook — Final (v1) — 2026-09-21

Read-only compilation. No simulation launched to produce this document.

---
### Slide 1 — Title
**Bullets:**
- Reproducing "Tracking down Quirks at the LHC" (Knapen, Lou, Papucci, Setford, arXiv:1708.02243v2)
- Coplanarity-based tracker search for quirk pairs
**Table/Figure:** none
**Source:** paper.txt page 1
**Speaker note:** frame this as an independent reproduction project, not a new physics result.
**Limitation:** —

---
### Slide 2 — Method summary
**Bullets:**
- Quirks: pairs bound by a confining string, non-helical tracker hits
- Sec IIIC: coplanarity plane-fit, Δs (thickness), Δw (width) via eigenvalue decomposition of tensor T_ij (Eq. 11)
- Sec IV signal region: plane found + hit-multiplicity + Δw<1cm + Δs<0.01cm
**Equations:** Eq. 10 (RMS distance), Eq. 11 (T_ij), Eq. 12 (ε=ε_trig×ε_fid×ε_reco)
**Source:** paper.txt lines 480–657, 738–809
**Speaker note:** ε_reco is the Sec IIIC plane-found efficiency, NOT the full Sec IV pass rate — this distinction drove a major mid-project correction.
**Limitation:** —

---
### Slide 3 — Colored quirk cutflow
**Bullets:**
- N_matched(full)=**419**; charge-filtered subset N=125 (only pairs with both R-hadrons charged, per Sec II)
- Trigger 27/125=0.216 → Fiducial 7/27=0.259 → Sec IIIC plane 5/7=0.714 (**N=7, statistically inconclusive**) → hit-mult 3/5 → final 1/7
**Table:** `final_freeze_v1/master_cutflow_table.csv`, row 1
**Source:** `colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv`
**Speaker note:** N=7 is too small to confirm or reject agreement with the paper — present as "consistent within statistics," not "matches."
**Limitation:** extremely small-N; final Wilson 95% CI is wide (roughly [0.03, 0.51] for 1/7).

---
### Slide 4 — EW quirk cutflow
**Bullets:**
- N_matched=**511** (full sample, no filter needed — color singlet, fixed unit charge)
- Trigger 89/511=0.174 → Fiducial 40/89=0.449 → Sec IIIC plane 32/40=0.800 → hit-mult 16/32 → final 6/40
**Table:** `master_cutflow_table.csv`, row 2
**Source:** `ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv`
**Speaker note:** EW ε_reco (0.800) is the strongest single agreement point with the paper's Table I (0.72).
**Limitation:** ε_trig/ε_fid show real tension vs paper (see Slide 5) — likely a trigger-proxy definition mismatch, not a reconstruction bug.

---
### Slide 5 — Table I: paper vs project
**Bullets:**
- Colored: ε_trig 0.24 (paper) / 0.216 (project); ε_fid 0.28 / 0.259; **ε_reco 0.35 / 0.714 — N_fid=7, statistically inconclusive, NOT confirmed agreement**
- EW: ε_trig 0.10 / 0.174 (tension); ε_fid 0.28 / 0.449 (tension); ε_reco 0.72 / 0.800 (consistent)
**Table:** `table1_extraction_v1/paper_vs_project_comparison.csv`
**Figure:** `table1_extraction_v1/table1_crop_400dpi.png`
**Source:** PDF page 8, exact transcription verified two independent ways (zero discrepancies)
**Speaker note:** state explicitly that overlapping-rounded-values is not proof of agreement; colored ε_reco is wide-interval and only borderline consistent.
**Limitation:** EW ε_trig/ε_fid tension unresolved — flagged as an open item, not silently absorbed.

---
### Slide 6 — Pile-up-only background (μ=0,5,10,20,50)
**Bullets:**
- Direct full-statistics cutflow at n=5000/μ: N_plane = 0,3,6,22,172; N_final = **0/5000 at every μ** (directly computed, not inferred)
- "Zero observed, not zero probability" — Wilson 95% UL≈7.68e-4 at every μ
**Table:** `master_cutflow_table.csv`, pileup rows
**Source:** `pileup_mu{0,5,10,20,50}_n5000_sec3c_fullcutflow_v1.csv`
**Speaker note:** this upgraded an earlier logical-inference-based proof to a direct full-statistics result.
**Limitation:** 20,000-event pool (paper: 125,000), with replacement — reduced statistical independence, documented project simplification.

---
### Slide 7 — Converted-photon-only baseline (no pile-up)
**Bullets:**
- N_total=9139, N_plane=2982, N_mult=4/2982 (w_mult=0.001341), N_final=0/9139
- Explicitly a **conversion-only / μ=0-equivalent baseline**, NOT the paper's converted-photon background
**Table:** `master_cutflow_table.csv`
**Source:** `conversion_scan_results_v4_FULL_DIAGNOSTICS.csv`
**Speaker note:** this result was necessary scaffolding, not the final answer — the overlay (Slide 8) supersedes it as the paper-equivalent quantity.
**Limitation:** —

---
### Slide 8 — Converted-photon + Pile-up μ=50 (paper-required overlay)
**Bullets:**
- N_total=**9139**, N_plane=**3276**, N_mult=**203**, N_final=**1**
- Raw probability = 1/9139 = 1.094×10⁻⁴; **Wilson 95% = [1.93×10⁻⁵, 6.20×10⁻⁴]** (corrected — see Slide 11); 1%-weighted equivalent = **1.094×10⁻⁶**
**Table:** `master_cutflow_table.csv`, final two rows
**Source:** `conversion_with_pileup_mu50_v1.csv`
**Speaker note:** call this a "paper-matched overlay implementation with documented simplifications," not an exact paper reproduction.
**Limitation:** a single event — one realization of a small-number process; does not by itself establish agreement with the paper's "removed almost entirely" claim.

---
### Slide 9 — Event 2555: why it passed
**Bullets:**
- At μ=0: layers 1, 2, 5 all below required 2-hit multiplicity (3 deficient layers, only 1 exception allowed) → FAIL. Δs=0.00582cm already under the final cut.
- At μ=50: **one primary charged pion, pT=0.242GeV**, from minbias pool event 3628, particle 10, crossed layers 1–4, filling layers 1 and 2 → only layer 5 remains the allowed exception → PASS. Δs grew to 0.00910cm, still <0.01cm.
- pT=0.242GeV is below the Loose tracking-efficiency reconstruction threshold (pT>0.4GeV) → reconstruction efficiency is **exactly zero** there by construction, so this track was guaranteed to be "unassociated" pile-up — consistent with ref[33]'s own definition of this background source.
**Figure:** `event_2555_forensic_v1/event2555_layer_comparison.png`, `event2555_selected_plane_xy_rz.png`
**Source:** `event_2555_forensic_v1/*`, deterministic replay evidence
**Speaker note:** n_candidates=1 at both μ states, normal vector rotated only 0.371° — pile-up enlarged the existing plane, did not create a new one.
**Limitation:** timing/η-rejection counts per hit remain unavailable (pre-existing limitation, not new).

---
### Slide 10 — Figure 5: two separate products
**Bullets:**
- **Product A (shape-only, 4 components)**: colored, EW, pileup, converted-γ+pileup — unit-area normalized, unaffected by any weight bug
- **Product B (absolute, 3 components, CORRECTED)**: colored, EW, converted-γ+pileup — pile-up excluded (no cross-section concept exists for a per-bunch-crossing overlay)
**Figures:** `fig5_reproduction_2026-09-17/fig5_left_panel_ds.png` (Product A); `fig5_absnorm_audit_v1/figure5_left_panel_ABSOLUTE_3curves_v2_CORRECTED.png` (Product B, **authoritative**)
**Source CSVs:** `fig5_data_v3_2026-09-17.json`; `figure5_left_panel_ABSOLUTE_source_v2_CORRECTED.csv`
**Speaker note:** the OLD absolute plot (`..._3curves.png`, no `_v2_CORRECTED` suffix) is **OBSOLETE** — its colored curve was high by 3.352× due to a wrong weight denominator (N=125 instead of N=419). Never present it.
**Limitation:** Figure 5 is not an exact 4-component absolute reproduction — pile-up's absolute normalization remains structurally blocked.

---
### Slide 11 — Statistics discipline: the Wilson-interval bug
**Bullets:**
- A margin-formula bug (missing leading `z` multiplier) made some Wilson 95% CIs too narrow to contain their own point estimate
- Caught on k=1,n=9139: reported [1.66×10⁻⁴, 4.73×10⁻⁴] did not contain phat=1.094×10⁻⁴ — **now corrected to [1.93×10⁻⁵, 6.20×10⁻⁴]**
- Regression test with 5 known cases added; 5/5 pass
**Source:** `docs/wilson_interval_bug_correction_v1.md`, `tests/test_wilson_interval_regression.py`
**Speaker note:** this affected only PPT-table efficiency intervals and the overlay's Phase-9 cutflow intervals — pile-up-only and converted-photon-only freeze results were independently confirmed unaffected.
**Limitation:** —

---
### Slide 12 — Figure 6 status
**Bullets:**
- Requires a production-cross-section × efficiency SCAN over a continuous (mQ,Λ) grid at L=300fb⁻¹
- Project has only 2 discrete benchmark points, and (until this session) no colored-quirk cross-section at all
- **BLOCKED** — not started, no values invented
**Table:** `converted_photon_with_pileup_v1/figure6_requirement_matrix.csv`
**Speaker note:** do not attempt Figure 6 without either a cross-section scan or explicit new authorization for one.
**Limitation:** structural, not a data-processing gap.

---
### Slide 13 — Overall status matrix
**Bullets:**
- EW signal (no pileup): COMPLETED, reconstruction-efficiency discrepancy noted (ε_trig/ε_fid tension)
- Colored signal (no pileup): COMPLETED, small-statistics limitation (N=7)
- Pile-up-only: COMPLETED AND FROZEN
- Converted-photon-only: COMPLETED BASELINE
- **Converted-photon + pile-up: COMPLETED (first time), single-event result**
- EW/colored + pile-up: NOT RUN
- Figure 5: diagnostic/approximate — NOT an exact 4-component absolute reproduction
- Figure 6: NOT STARTED, blocked on cross-section grid
**Source:** this document
**Limitation:** see individual slides.

---
### Slide 14 — Limitations and assumptions (consolidated)
**Bullets:**
- 20,000- vs 125,000-event pile-up pool
- Pile-up curve has no absolute cross-section concept
- Pile-up reweighting denominator ambiguous (2 interpretations preserved)
- EW ε_trig/ε_fid tension vs paper — likely definitional, unresolved
- Single-event overlay result — not a rate measurement
**Source:** all prior audit docs
**Limitation:** (this slide IS the limitations slide)

---
### Slide 15 — Next steps (not started)
**Bullets:**
- EW/colored + pile-up overlay (mirrors converted-photon work)
- Repeated-statistics μ=50 overlay batch (to move past N=1)
- Figure 6 cross-section scan (large scope, needs explicit authorization)
**Limitation:** none started per explicit instruction this session.
