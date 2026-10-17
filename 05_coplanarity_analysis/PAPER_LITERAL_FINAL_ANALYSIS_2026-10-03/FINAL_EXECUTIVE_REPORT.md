# Final Executive Report (v2) — Reproduction of arXiv:1708.02243v2 Table I

**Date:** 2026-10-03. **Machine / repository:** DESKTOP-OD6H911, `/home/rafia/coplanarity_study`, branch `transfer-2026-10-02`, HEAD `97258a5d` (no commit, no push). Figure 6 was not touched.

**Version 2 corrects the detector classification.** Version 1 is kept as `FINAL_EXECUTIVE_REPORT_v1_SUPERSEDED.md`. Full details are in `CORRECTION_ACCEPTANCE_AND_LONGITUDINAL_2026-10-03.md`; the source-status table is `tables/v2_source_status.csv`.
- **Primary acceptance:** the paper-stated one (barrel only, "effectively … |η| ≲ 1.8", no finite-z boundary). The finite barrel lengths of Ref. [27] are now an INFERRED sensitivity study. Older tables label the finite-barrel configuration "LITERAL"; read that label as "finite-barrel sensitivity".
- **SCT resolution:** R-φ 34 µm is paper rule × Ref. [27]. For z, Ref. [27] states 580 µm (z), but the paper's "twice the intrinsic accuracy" names no coordinate. So 1160 µm is INFERRED, 580 µm is a sensitivity, and no smearing is UNDOCUMENTED. All three are reported.
- **45 mm beam spot (PAPER-STATED):** reported under three readings. The primary one is a common shift per event, with the fit relative to the true vertex.

## 1. Headline (paper-stated acceptance, common-shift beam spot)

| Benchmark | Quantity | Paper | Sample 1 | Sample 2 | Category (sample 2) |
|---|---|---|---|---|---|
| Colored 1800 GeV, 2 keV | ε_trig | 0.24 | 101/419 = 0.241 | 207/873 = 0.237 | Consistent (p = 0.87) |
| | ε_fid (\|η\| < 1.8) | 0.28 | 7/27 = 0.26 | **25/68** = 0.37 | Consistent (p = 0.14) |
| | ε_reco, SCT z 1160 µm (inferred) | 0.35 | 1/7 = 0.14 | 3/25 = 0.12 | Statistically inconsistent (p = 0.019) |
| | ε_reco, SCT z 580 µm (sensitivity) | 0.35 | 3/7 = 0.43 | 5/25 = 0.20 | Consistent (p = 0.14) |
| | ε_reco, no SCT z smearing (undocumented) | 0.35 | 5/7 = 0.71 | 11/25 = 0.44 | Consistent (p = 0.40) |
| EW 800 GeV, 4 keV | ε_trig | 0.10 | 89/511 = 0.174 | 186/1045 = 0.178 | Strongly inconsistent (p = 2×10⁻¹⁴) |
| | ε_fid (\|η\| < 1.8) | 0.28 | 40/89 = 0.45 | **94/186** = 0.51 | Strongly inconsistent (p = 1×10⁻¹⁰) |
| | ε_reco, SCT z 1160 µm (inferred) | 0.72 | 6/40 = 0.15 | 21/94 = 0.22 | Strongly inconsistent |
| | ε_reco, SCT z 580 µm (sensitivity) | 0.72 | 10/40 = 0.25 | 29/94 = 0.31 | Strongly inconsistent |
| | ε_reco, no SCT z smearing (undocumented) | 0.72 | 34/40 = 0.85 | 76/94 = 0.81 | Borderline (p = 0.065) |

**The primary reconstruction denominators are back at 25 (COL2000) and 94 (EW2000), and 7 / 40 for the 1000-event samples.** These are identical to the 30-Sep project counts.

**Finite-barrel sensitivity** (fiducial; final at z 1160 · 580 · 0 µm):
- COL1000: 6/27; 1 · 2 · 5.
- COL2000: 22/68; 1 · 3 · 8.
- EW1000: 33/89; 2 · 5 · 27.
- EW2000: 62/186 (not 61); 10 · 14 · 50.

The EW fiducial matches the paper's 0.28 **only** under this inferred geometry.

**Beam-spot readings** (acceptance A, final at z 1160 · 580 · 0 µm):

| Reading | COL2000 | EW2000 |
|---|---|---|
| Common shift, fit from true vertex (primary) | 3 · 5 · 11 of 25 | 21 · 29 · 76 of 94 |
| Common shift, fit from origin | 0 · 0 · 0 of 25 | 3 · 3 · 4 of 94 |
| Independent per-hit 45 mm | 0 of 21 fiducial (no plane at all) | 0 of 66 fiducial (no plane at all) |

**Backgrounds, full signal region:**
- **Pile-up (\|η\| < 1.8, SCT 34 µm / 1.16 mm, pixel merging; `scripts/P8e_pileup_eta_merge.py`, same 5000 events):** 0/5000 in the signal region (UL 6.0×10⁻⁴). Merging joins only 0.04% of pile-up hits and changes no decision.
- **Converted photon, \|η\| < 1.8 with primary-vertex fit:** 0/9139 (SCT z 1160), 0/9139 (580), **30/9139 (no SCT z smearing)**.
- **Conversion + pile-up (\|η\| < 1.8, vertex fit, SCT 1.16 mm; `scripts/P10e_overlay_eta.py`, existing 9139 photons):** 9139 → 3323 plane → 193 hit multiplicity → **0 signal region** (UL 3.3×10⁻⁴). The closest event has Δs = 121 µm.
- **Primary background tables:** `tables/v3_pileup_primary.csv`, `tables/v3_conversion_primary.csv`.
- **Pile-up rates:** the 4/8-layer plane rate is 6.6–12×10⁻³ against the paper's ~10⁻³; the 8/8 rate is compatible.

**A 100% reproduction of Table I is not possible from the published information** (Sec. 4).

## 2. What was done (Phases 0–12)

| Phase | Output | Key result |
|---|---|---|
| 0 Preservation | `phase0/PHASE0_PRESERVATION_RECORD.md` | branch, HEAD and Figure 6 checkpoint hash recorded; no tracked modification |
| 1 Paper line by line | `tables/paper_requirement_matrix.csv` (347 rows), `PAPER_LINE_BY_LINE_IMPLEMENTATION_AUDIT.md` | every v2 sentence, TeX comment and v1→v2 change classified |
| 2 Detector from ref. [27] | `tables/detector_parameter_sources.csv`, `DETECTOR_LITERAL_IMPLEMENTATION_REPORT.md` | ref. [27] read via arXiv:0901.0512 pp. 40–43; SCT 17 µm / 580 µm → literal 34 / 1160 µm; finite barrel |
| 3 Trigger recount | `tables/P3_raw_trigger_recount.json`, `tables/signal_raw_counts.csv` | independent parse of the frozen LHE/HepMC; hard / post-shower / final levels |
| 4 Exact replay | `tables/signal_replay_vs_stored.csv` | stored seeds reproduce the frozen decisions (fiducial 370/370; finals all) |
| 5–7 Literal Sec. III C / IV | `SIGNAL_TABLE_I_RESULTS.md`; `signal_efficiency_statistics.csv`, `signal_event_closure.csv`, `paper_project_comparison.csv` | each sample separate; N/N, %, SE, Wilson 68/95, CP95, exact p, Fisher with inferred paper N |
| 8 Pile-up | `PILEUP_BACKGROUND_RESULTS.md`, `pileup_cutflow.csv` | 5000 events, literal detector (validated 200/200 against the frozen sweep) |
| 9 Conversion | `CONVERTED_PHOTON_RESULTS.md`, `converted_photon_cutflow.csv`, `converted_photon_event_changes.csv` | 9139 × 4 configs (validated 300/300 against frozen v4); per-event change reasons |
| 10 Conversion + pile-up | `CONVERTED_PHOTON_PILEUP_OVERLAY_RESULTS.md`, `overlay_cutflow.csv` | 9139 events; winner hit ancestry; displays |
| 11 Figures | `FINAL_FIGURES/` (F02–F12) | each with PNG/PDF/SVG, source CSV (the only data plotted), caption, provenance + SHA-256, script copy |
| 12 Validation | `tables/P12_validation_results.csv`, `SHA256_MANIFEST.txt` | all checks PASS (Sec. 6) |

**Earlier frozen numbers recomputed from their stored per-event files** (`tables/frozen_background_cutflows.csv`):
- Conversion-only v4: 9139 → 2982 plane → 4 multiplicity → 0 final.
- Overlay v1: 9139 → 3276 → 203 → 1 (event 2555).
- The previously quoted "9139 → 3276 → 203" was the **overlay** cutflow, not conversion-only.

## 3. Figures (`FINAL_FIGURES/`)

| Figure | Content |
|---|---|
| F02 / F03 | Paper Fig. 2/3-style: angular momentum, quirk separation and plane rotation for real COL2000 / EW2000 events |
| F04 | Paper Fig. 4-style displays: one colored and one EW event passing the literal signal region |
| F05 (normalised, absolute) | Paper Fig. 5-style Δs / Δw for colored, EW, pile-up, conversion and conversion + pile-up, against the digitised paper Fig. 5 |
| F06 | Table I comparison with Wilson 68/95% intervals, each sample separately |
| F07 | Literal signal cutflow |
| F10 | Background event displays: conversion literal; conversion with SCT z unsmeared (calibrated); conversion + pile-up closest candidate |
| F11 | Background cutflows and weighted yields at 300 fb⁻¹ |
| F08, F09, F12 | Diagnostics: SCT z envelope (U2), EW trigger variation scan (U1), fiducial geometry (U4). The Δw factor 2 (U3) is quantified in F05 and `UNRESOLVED_DIFFERENCES.md`. |


**v2 figures** (`FINAL_FIGURES/`):

| Figure | Content |
|---|---|
| F06v2 | Primary Table I with \|η\| < 1.8 and reconstruction for each SCT z treatment |
| F08v2 | SCT z envelope, A primary vs B sensitivity |
| F12v2 | Fiducial efficiency, A vs B |
| F13v2 | Pile-up rates, both acceptance runs |
| F14v2 | Conversion background by acceptance |
| F15v2 | Signal Δs vs paper Fig. 5, \|η\| < 1.8 |

**Superseded by v2:** F06, F07, F08, F12 and F15. They show the finite barrel as primary; they are kept for provenance.

**v2 tables:**
- `acceptance_longitudinal_matrix.csv`
- `v2_primary_table_I.csv`
- `v2_finite_barrel_sensitivity.csv`
- `v2_beamspot_readings.csv`
- `conversion_acceptance_A_cutflow.csv`
- `v2_source_status.csv`

## 4. FINAL VERDICT (v2)

### 4.1 What reproduces with paper-stated settings
- Colored ε_trig (0.241, 0.237 vs 0.24).
- Colored ε_fid under \|η\| < 1.8 (0.26, 0.37 vs 0.28).
- No background in the signal region: pile-up 0/5000; conversions 0/9139 with SCT z of 1160 or 580 µm.
- The pile-up 8/8-layer rate.
- The Fig. 2/3 dynamics: L ~ 10¹² ħ, and a plane rotation below 10⁻⁴ rad.

### 4.2 Statistically compatible but weakly constrained
- Colored ε_reco: compatible with 0.35 for SCT z 580 µm (5/25) and for no smearing (11/25). At 1160 µm only the 7-event sample is compatible.
- EW ε_reco without SCT z smearing: 0.81–0.85, borderline (p = 0.065–0.078). This treatment is undocumented.

### 4.3 What differs
- **EW ε_trig:** 0.174–0.178 vs 0.10. Unchanged under 36 one-at-a-time generator variations; the vector-like model gives 0.170.
- **EW ε_fid with the paper-stated \|η\| < 1.8:** 0.45–0.51 vs 0.28.
- **EW ε_reco with any SCT z smearing that has a source:** 0.15–0.31 vs 0.72.
- **Colored ε_reco at SCT z 1160 µm:** COL2000 0.12 vs 0.35 (p = 0.019).
- **Pile-up 4/8-layer rate.**
- **Z(νν)γj cross-section:** 0.23 pb vs ~1 pb.

### 4.4 Impossible to settle because undocumented or ambiguous
- **Which acceptance the authors used.** The paper says "\|η\| ≲ 1.8", but only the Ref. [27] finite barrel reproduces the EW 0.28.
- **Whether the "twice the intrinsic accuracy" rule was applied to z** (580 µm in Ref. [27]). The paper's Fig. 5 Δs (~30 µm) suggests little or no z smearing.
- **The beam-spot treatment** (three readings).
- **Generator settings.**
- **The paper's raw counts and uncertainties.**
- **Pile-up detector details and pool size.**
- **The beam-pipe material** for the conversion probability.

### 4.5 Implementation errors found and handled
- **EW UFO Z coupling** was SM-chiral, not vector-like. Trigger-neutral, but σ −24%.
- **Stale contaminated numerators** COL2000 20/25 and EW2000 84/94 rejected.
- **My own v1 labels:** the frozen pile-up sweep and conversion v4 were described as "SCT z 0"; they used 34/1160 µm. Corrected.
- **My own v1 classification:** the finite barrel was called "literal". Corrected in v2.
- **Fit origins:** the frozen conversion and overlay fitted from the conversion point; the paper says primary vertex.

### 4.6 Modelling systematics
- SCT z envelope {1160, 580, 0} µm.
- Acceptance A vs B.
- Beam-spot readings.
- Δw convention (no count changes).
- The pile-up detector simplification.

**Important:** the no-SCT-z-smearing treatment that brings EW reconstruction near Table I lets 30/9139 (\|η\| < 1.8) or 22/9139 (finite barrel) conversions into the signal region.

### 4.7 Statistical limitations
- 7–94 fiducial events per sample.
- The paper's own MC uncertainty is unknown.
- 5000 pile-up / 9139 conversion events bound background rates only to ~3–6×10⁻⁴ per event.

## 5. Recommendation
- **Report the paper-stated configuration as the main result,** with the SCT z treatment shown for all three options. The 1160 µm value is the most direct reading, but it is inferred.
- **Report the finite barrel as a labelled sensitivity.** It is the only way to get the EW 0.28.
- **Treat any calibrated choice (no SCT z smearing) as calibrated,** and show its conversion background.
- **Figure 6 stays paused** pending your decision.

**Professor reports:**
- `PROFESSOR_REPORT_2026-10-03_v3.pdf` is the version to send: final results only, with formulas, ε ± SE and Wilson 95% in every table.
- `PROFESSOR_REPORT_2026-10-03_v2.pdf` is kept.
- `PROFESSOR_REPORT_2026-10-03.pdf` (v1) and `PROFESSOR_SHORT_REPORT.html` (published v1 page) are superseded and left unchanged.

## 6. Validation (Phase 12, `tables/P12_validation_results.csv`)

All checks PASS. They cover:
- recomputed percentages and k/n in every table;
- monotone sequential cutflows;
- the per-event subset chain final ⊆ multiplicity ⊆ plane ⊆ fiducial, with no duplicates;
- literal k/n rebuilt from per-event data;
- no stale 20/25 or 84/94 used as a result;
- Δs/Δw units in cm;
- every figure's source-CSV hash matching its provenance;
- paper values cited correctly against the TeX source;
- LITERAL rows using only B / Z1160 / W1;
- frozen signal LHE/HepMC hashes unchanged since Phase 3, and frozen conversion CSVs unchanged;
- no tracked file modified, HEAD unchanged;
- the Figure 6 checkpoint hash unchanged, and no Figure 6 process running.

The full file hash list is in `SHA256_MANIFEST.txt`.
