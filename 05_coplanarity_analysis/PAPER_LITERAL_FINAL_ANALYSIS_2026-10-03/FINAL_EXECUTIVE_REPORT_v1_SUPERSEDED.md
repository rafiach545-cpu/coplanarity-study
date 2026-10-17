# Final Executive Report — Literal Reproduction of arXiv:1708.02243v2

**Date:** 2026-10-03.
**Machine / repository:** DESKTOP-OD6H911, `/home/rafia/coplanarity_study`, branch `transfer-2026-10-02`, HEAD `97258a5d` (no commit, no push).
**Directory:** `05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/`.

**Rule followed:** only PAPER-STATED, REFERENCE-STATED and unavoidable DERIVED-DIRECTLY settings enter the authoritative result. Nothing was tuned toward Table I. Calibrated results are labelled and archived as non-authoritative in `05_coplanarity_analysis/ARCHIVE_NON_AUTHORITATIVE_2026-10-03/`; that archive is links and hashes only, with nothing moved or deleted. Figure 6 was not touched.

## 1. Headline

| Benchmark | Quantity | Paper | Literal, sample 1 | Literal, sample 2 | Status |
|---|---|---|---|---|---|
| Colored 1800 GeV, Λ = 2 keV | ε_trig | 0.24 | 101/419 = 0.241 | 207/873 = 0.237 | **reproduced** |
| | ε_fid | 0.28 | 6/27 = 0.22 | 22/68 = 0.32 | **reproduced** |
| | ε_reco | 0.35 | 1/6 = 0.17 (N too small) | 1/22 = 0.045 (p = 0.0013) | **not reproduced** |
| EW 800 GeV, Λ = 4 keV | ε_trig | 0.10 | 89/511 = 0.174 | 186/1045 = 0.178 | **not reproduced** (p ≤ 3e-7) |
| | ε_fid | 0.28 | 33/89 = 0.37 | 62/186 = 0.33 | **reproduced** |
| | ε_reco | 0.72 | 2/33 = 0.06 | 10/62 = 0.16 | **not reproduced** (p ≤ 2e-15) |

**Backgrounds (literal):**
- Pile-up only: 0/5000 events in the signal region.
- Converted photon only: 0/9139.
- Converted photon + pile-up: 0/9139.
- This agrees with the paper's conclusion that the signal-region background is negligible.
- The pile-up 4/8-layer plane rate is 6.6e-3 against the paper's ~1e-3 (differs). The 8/8 rate is 2e-4 against 6e-5 (compatible).

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

## 4. FINAL VERDICT

### 4.1 What reproduces

The paper value lies inside our 95% interval in every independent sample for:
- **colored ε_trig**: 0.241 and 0.237 vs 0.24;
- **EW ε_fid**: 0.37 and 0.33 vs 0.28;
- **colored ε_fid**: 0.22 and 0.32 vs 0.28.

The fiducial result requires the literal finite-barrel geometry of ref. [27]; the project's η-cone overshoots EW (F12).

Also reproduced:
- the qualitative Fig. 2/3 dynamics (L ~ 10¹² ħ for colored; slow plane rotation);
- the background conclusion (no pile-up, conversion or overlay event in the signal region);
- the pile-up 8/8-layer rate.

### 4.2 What is statistically compatible but weakly constrained

- **COL1000 ε_reco** = 1/6 (Wilson 95% [0.03, 0.56]) is compatible with 0.35 only because N = 6. The larger COL2000 sample (1/22) is not.
- **Pile-up 8/8 rate:** 1/5000 vs 6e-5 (p = 0.26).
- **Background upper limits:**
  - 0/5000 pile-up events (UL 6.0e-4 per event);
  - 0/9139 conversion and overlay events (UL 3.3e-4; < 0.21 events at 300 fb⁻¹ with project σ, < 0.98 with the paper's 1 pb).

### 4.3 What differs

- **EW ε_trig:** 0.174–0.178 vs 0.10. It is unchanged by 36 one-at-a-time variations, including MG5 2.3.3 / Pythia 8.212 and the vector-like Z coupling. The independent confirmation sample gives 0.170. The EW/colored ratio is 0.60–0.84 vs the paper's 0.42.
- **ε_reco under the literal SCT reading:**
  - EW 0.06 and 0.16 vs 0.72;
  - colored 0.045 vs 0.35 (COL2000).
  - The independent fresh-seed sample confirms this: EW 14/102 = 0.14, colored 6/94 = 0.06.
- **Signal Δs distribution:** literal median ≈ 110–160 µm vs the paper's Fig. 5 ≈ 28–35 µm.
- **Pile-up 4/8-layer plane rate:** 6.6e-3 vs ~1e-3.
- **Z(νν)γj cross-section:** 0.23 pb (project) vs ~1 pb (paper).

### 4.4 What is impossible because it is undocumented

- **The SCT z resolution actually used by the paper.** The text gives 1.16 mm (2 × 580 µm, ref. [27]). The paper's Fig. 4/5 require ≲ 34 µm or no smearing. That one setting moves EW ε_reco between 0.06–0.16 and 0.81–0.92 (F08). **This alone prevents a 100% reproduction.**
- **The generator settings behind the EW trigger:** matching scale, PDF, scales, tune, any extra generator cut. These are not stated; we used the frozen values.
- **The paper's raw counts and uncertainties.** None are published; paper sample sizes are inferred from Fig. 5 quantisation (~1075 EW, ~525 colored).
- **Pile-up detector details** (1612.00850 App. A material, endcaps, pool size 125k) and **the meaning of "a plane"** in the 4/8 rate.
- **The beam-pipe material** needed to read the conversion probability from PDG Figs. 33.16/17. We use 1%, DERIVED from the paper's own numbers.
- **The generator setup behind "~1 pb".**

### 4.5 Genuine implementation errors (found and handled)

- **EW UFO Z coupling** was SM-chiral instead of vector-like. It has no effect on the efficiencies within statistics (trigger Fisher p = 0.60), but changes σ by −24%, which matters for Figure 6.
- **Stale contaminated numerators**, rejected and not used:
  - COL2000 plane 20/25 (rejected; contaminated): the fiducial intersection is 12 (frozen) and 9 (literal).
  - EW2000 plane 84/94 (rejected; contaminated): 75 (frozen) and 45 (literal).
- **Neighbouring-pixel merging** was absent from the frozen pile-up-only driver; the literal run applies it.
- **The frozen overlay's "Δs pass 78" and the pile-up sweep's "Δs pass 7"** are non-sequential counts, not signal-region counts.
- **Fit origin:** frozen conversion used the conversion point, while the paper's text uses the primary vertex. The literal run uses the primary vertex; the conversion-point origin changes nothing (SYS_CONVPT).

### 4.6 Modelling systematics (reported, not adopted)

- **SCT z resolution envelope** (geometry B, ranges over the two samples):

  | σ_z | EW ε_reco | Colored ε_reco |
  |---|---|---|
  | 0 or 34 µm | 0.81–1.00 | 0.36–0.83 |
  | 580 µm | 0.15–0.23 | 0.14–0.33 |
  | 1160 µm (literal) | 0.06–0.16 | 0.05–0.17 |
- **η-cone vs finite barrel:** EW ε_fid 0.45–0.51 vs 0.33–0.37.
- **Δw convention (½√λ₂ vs √λ₂):** no count changes.
- **Background consequence of the calibrated SCT z = 0 setting:** 22/9139 conversion-only events enter the signal region, i.e. 1.5 events at 300 fb⁻¹ with project σ, 7.2 with 1 pb. **The Table I-calibrated detector is therefore not background-free.** This is a further reason it cannot be adopted silently.
- **Pile-up detector simplification** (no energy loss, bremsstrahlung or endcaps; 20k pool).

### 4.7 Statistical limitations

- **Signal:** only 6–62 trigger ∧ fiducial events per sample, so ε_reco intervals are ±0.1–0.3 wide.
- **Paper:** the paper's own MC statistical uncertainty is unknown. Inferred N gives ±0.012–0.019 on ε_reco.
- **Background:** 5000 pile-up and 9139 conversion events cannot probe rates below ~3e-4 to 6e-4 per event, so the paper's 6e-5-level statements cannot be tested with power.

## 5. Recommendation

- **Report the literal result as the reproduction:**
  - trigger and fiducial reproduce, except the EW trigger;
  - reconstruction does not reproduce under the paper's literal SCT resolution.
- **Report the SCT-z envelope (F08) as the dominant, paper-internal ambiguity.**
- **If a calibrated configuration is used for Figure 6 later, label it calibrated**, cite U2, and include its conversion background (22/9139 conversion-only).
- **Figure 6 stays paused** pending your decision.

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
