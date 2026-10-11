# Correction: Acceptance and Longitudinal Treatments (2026-10-03, v2)

This document supersedes the earlier classification in this directory. That classification called the finite-barrel acceptance "literal".

No new events were generated. The audit re-analysed the existing exact crossings, then reprocessed the existing conversion photons through the existing code. No frozen file was modified. Figure 6 was not touched, and nothing was committed.

**Scripts:**
- `scripts/P4c_acceptance_longitudinal_audit.py` → `tables/acceptance_longitudinal_per_event.csv`, `tables/acceptance_longitudinal_matrix.csv`.
  - Self-check: at SCT z 1160 / common shift it reproduces the earlier P4 decisions exactly for both acceptances, with Δs within 10⁻⁷ cm.
- `scripts/P9d_conversion_acceptance_A.py` → `tables/conversion_acceptance_A_cutflow.csv`.
  - Self-check: identical to the stored SYS_ETA rows.
- `scripts/P13_v2_tables.py` → `tables/v2_primary_table_I.csv`, `tables/v2_finite_barrel_sensitivity.csv`, `tables/v2_beamspot_readings.csv`.
- `tables/v2_source_status.csv`.

## 1. Acceptance (items 1, 2, 7)

The paper (Sec. III A) says: "For simplicity, we only included the barrel of the pixel and SCT detectors in our simulations, which effectively restricts the fiducial range to |η| ≲ 1.8."

| Model | Status | COL1000 | COL2000 | EW1000 | EW2000 |
|---|---|---|---|---|---|
| **A. Barrel only, effective \|η\| < 1.8, no finite-z boundary (PRIMARY)** | PAPER-STATED | 7/27 | **25/68** | 40/89 | **94/186** |
| B. Finite barrel lengths of Ref. [27] | INFERRED (sensitivity) | 6/27 | 22/68 | 33/89 | 62/186 |

- **The primary fiducial denominators return to 25 (COL2000) and 94 (EW2000).** These are identical to the 30-Sep project counts, re-verified event by event.
- **Correction to the request:** the finite-barrel EW2000 fiducial count is **62**, not 61. The final count of 10 is correct.
- **No direct evidence** was found that the authors applied finite-z boundaries. Ref. [27] lists the lengths, but the paper only states the |η| ≲ 1.8 consequence.
- **Consequence, stated plainly:** under the paper-stated acceptance, the EW fiducial efficiency (0.45 and 0.51) is **strongly inconsistent** with the paper's 0.28 (p = 8×10⁻⁴ and 1×10⁻¹⁰). Only the inferred finite barrel reproduces 0.28. This is reported, not used to choose.

## 2. SCT resolution: what Ref. [27] actually says (item 4)

Ref. [27] (ATL-PHYS-PUB-2009-002, read through arXiv:0901.0512 pp. 40–43; text in `notes/ref27_CSC_ID_chapter_pages40-43.txt`) says:
- "this detector uses small-angle (40 mrad) stereo strips to measure both coordinates";
- "The intrinsic accuracies per module in the barrel are 17 µm (R−φ) and 580 µm (z)";
- Table 2: "Barrel 17 (R-φ) 580 (z)¹", with footnote 1: "Arises from the 40 mrad stereo angle between back-to-back sensors".

**Result:**
- **The 17 µm applies only to R-φ**, so 34 µm R-φ is paper rule × REFERENCE-STATED.
- **The SCT z accuracy is not undocumented in the reference:** Ref. [27] gives 580 µm (z) explicitly. This corrects the premise of item 4. The project's own `04_detector_sim/atlas_geometry.py` had flagged 580 µm as "UNVERIFIED" because Ref. [27] was unavailable then. It is now verified.
- **What is not stated** is whether the paper's "twice the intrinsic accuracy quoted in [27]" was applied to z. The sentence names no coordinate.

So the longitudinal treatments are:

| Treatment | Status |
|---|---|
| 45 mm beam-spot z smearing | **PAPER-STATED** |
| SCT z 1160 µm (2 × 580 µm) | **INFERRED** (the paper's rule applied to the reference z value; the original project choice; contradicted by the paper's Fig. 5) |
| SCT z 580 µm (1 × Ref. [27]) | INFERRED sensitivity (contradicts "twice") |
| No SCT z measurement smearing | **UNDOCUMENTED** (no source; not paper-stated) |

## 3. Beam spot: common shift or per hit (item 5)

The paper says: "We further apply a uniform, gaussian smearing with width 45 mm to the z-coordinates of all the hits", and "We will assume that the primary vertex is identified correctly, and is located at the origin." The wording does not settle the question, so all three readings are reported. Counts below are acceptance A.

| Reading | COL2000: fid / final (z 1160 · 580 · 0) | EW2000: fid / final (z 1160 · 580 · 0) |
|---|---|---|
| CV: one common shift per event, fit from the true vertex (implemented so far) | 25 / 3 · 5 · 11 | 94 / 21 · 29 · 76 |
| CO: one common shift per event, fit from the origin | 25 / 0 · 0 · 0 | 94 / 3 · 3 · 4 |
| PH: independent N(0, 45 mm) shift of every hit | 21 / 0 · 0 · 0 | 66 / 0 · 0 · 0 |

- **Under PH no plane is found in any event, for any SCT setting.** The 45 mm per-hit noise is about 450× the 0.01 cm Δs cut.
- **Under CO** the planes, which pass through the true vertex, miss the origin.
- **The primary tables use CV.** The paper says the primary vertex is identified correctly, which only has meaning if hits are measured from that vertex. This is the stated reason; agreement with Table I was not used. CO and PH are listed as alternative readings (full matrix: `tables/v2_beamspot_readings.csv`; finite barrel B is included there too).

## 4. Primary Table I comparison (items 6, 8)

Primary configuration:
- acceptance A (PAPER-STATED);
- beam spot CV (INFERRED reading);
- SCT R-φ 34 µm;
- SCT z under every treatment.

Columns: p = exact binomial against the paper; category on the agreed scale.

| Sample | Quantity | Treatment | k/n | ε [Wilson 95%] | p | Category |
|---|---|---|---|---|---|---|
| COL1000 | trigger | — | 101/419 | 0.241 [0.203, 0.284] | 0.95 | Consistent |
| COL1000 | fiducial | — | 7/27 | 0.259 [0.132, 0.447] | 1.00 | Consistent |
| COL1000 | reco | z 1160 | 1/7 | 0.143 [0.026, 0.513] | 0.43 | Consistent (N = 7) |
| COL1000 | reco | z 580 | 3/7 | 0.429 [0.158, 0.750] | 0.70 | Consistent (N = 7) |
| COL1000 | reco | no z smear | 5/7 | 0.714 [0.359, 0.918] | 0.056 | Borderline |
| COL2000 | trigger | — | 207/873 | 0.237 [0.210, 0.266] | 0.87 | Consistent |
| COL2000 | fiducial | — | 25/68 | 0.368 [0.263, 0.486] | 0.14 | Consistent |
| COL2000 | reco | z 1160 | 3/25 | 0.120 [0.042, 0.300] | 0.019 | Statistically inconsistent |
| COL2000 | reco | z 580 | 5/25 | 0.200 [0.089, 0.391] | 0.14 | Consistent |
| COL2000 | reco | no z smear | 11/25 | 0.440 [0.267, 0.629] | 0.40 | Consistent |
| EW1000 | trigger | — | 89/511 | 0.174 [0.144, 0.209] | 2.8×10⁻⁷ | Strongly inconsistent |
| EW1000 | fiducial | — | 40/89 | 0.449 [0.350, 0.553] | 8.2×10⁻⁴ | Strongly inconsistent |
| EW1000 | reco | z 1160 | 6/40 | 0.150 [0.071, 0.291] | 9.1×10⁻¹⁴ | Strongly inconsistent |
| EW1000 | reco | z 580 | 10/40 | 0.250 [0.142, 0.402] | 9.4×10⁻¹⁰ | Strongly inconsistent |
| EW1000 | reco | no z smear | 34/40 | 0.850 [0.709, 0.929] | 0.078 | Borderline |
| EW2000 | trigger | — | 186/1045 | 0.178 [0.156, 0.202] | 1.8×10⁻¹⁴ | Strongly inconsistent |
| EW2000 | fiducial | — | 94/186 | 0.505 [0.434, 0.576] | 1.3×10⁻¹⁰ | Strongly inconsistent |
| EW2000 | reco | z 1160 | 21/94 | 0.223 [0.151, 0.318] | 2.4×10⁻²³ | Strongly inconsistent |
| EW2000 | reco | z 580 | 29/94 | 0.309 [0.224, 0.408] | 1.5×10⁻¹⁶ | Strongly inconsistent |
| EW2000 | reco | no z smear | 76/94 | 0.809 [0.717, 0.875] | 0.065 | Borderline |

**Item 8: yes, the primary reconstruction denominators return to 25 (COL2000) and 94 (EW2000), and 7 / 40 for the 1000-event samples.**

**Final numerators under every defensible longitudinal treatment** (fid / final):

| Treatment | COL2000 | EW2000 |
|---|---|---|
| CV, z 1160 µm | 25 / 3 | 94 / 21 |
| CV, z 580 µm | 25 / 5 | 94 / 29 |
| CV, no z smear | 25 / 11 | 94 / 76 |
| CO, any z | 25 / 0 | 94 / 3–4 |
| PH, any z | 21 / 0 | 66 / 0 |

**Finite-barrel sensitivity (B, CV)** — moved out of the primary table, per item 7. Full table: `tables/v2_finite_barrel_sensitivity.csv`.

| Sample | Fiducial | Final, z 1160 | Final, 580 | Final, 0 |
|---|---|---|---|---|
| COL1000 | 6/27 | 1 | 2 | 5 |
| COL2000 | 22/68 | 1 | 3 | 8 |
| EW1000 | 33/89 | 2 | 5 | 27 |
| EW2000 | 62/186 | 10 | 14 | 50 |

## 5. Backgrounds under the paper-stated acceptance

| Background | Acceptance A (paper-stated) | Acceptance B (sensitivity) |
|---|---|---|
| Pile-up μ = 50, full SR | 0/5000 (existing project sweep: η-cone, SCT 34/1160 µm, no pixel merging) | 0/5000 (literal run with merging) |
| Pile-up, plane with ≥ 4/8 layers / all 8 layers | 59/5000 / 0/5000 | 33/5000 / 1/5000 |
| Converted photon, full SR (PV origin) | 0/9139 (z 1160), 0/9139 (z 580), **30/9139 (no z smear)** | 0/9139 (z 1160), 22/9139 (no z smear) |
| Conversion + pile-up, full SR | **1/9139 (existing project run: SCT 1160, conversion-point fit origin; event 2555)** | 0/9139 (PV origin) |

Not run, because each would need a new 1.5 h pile-up pass:
- the overlay under acceptance A with the primary-vertex origin;
- any background with no SCT z smearing plus pile-up.

**Correction of my earlier labels:** the existing pile-up sweep and frozen conversion v4 used SCT 34/1160 µm, not "SCT z 0" as two of my table labels said. The labels are fixed in `scripts/P8b_pileup_tables.py` and `scripts/P9c_conversion_tables.py`, and the tables are regenerated.

## 6. What changes in the conclusions

- **Fiducial:** under the paper-stated |η| < 1.8 acceptance, the colored fiducial is consistent, but the EW fiducial is **not** (0.45–0.51 vs 0.28). The finite barrel that reproduces 0.28 is an inferred sensitivity, not the paper's stated model.
- **Reconstruction:** no treatment that has a source reproduces the EW 0.72. The SCT z of 1160 or 580 µm gives 0.15–0.31.
  - Only the UNDOCUMENTED no-z-smearing treatment comes close: 0.81–0.85, "borderline" (p = 0.065–0.078).
  - For colored, the 580 µm and no-smearing treatments are consistent with 0.35, while 1160 µm is statistically inconsistent for COL2000 (p = 0.019).
- **Trigger:** unchanged. Colored is consistent; EW is strongly inconsistent.
- **Full reproduction:** still impossible from published information. The acceptance actually used (the paper's "≲ 1.8" or the reference lengths), the SCT z treatment and the beam-spot reading are all not uniquely fixed by the text.

## 7. Source-status table (`tables/v2_source_status.csv`)

| Implementation choice | Exact source | Status | Resulting counts |
|---|---|---|---|
| Barrel only, 8 layers | Paper III A: "we only included the barrel of the pixel and SCT detectors" | PAPER-STATED | frame |
| **Effective \|η\| < 1.8 per hit, no finite z (primary)** | Paper III A: "effectively restricts the fiducial range to \|η\| ≲ 1.8" | PAPER-STATED | fid 7/27, 25/68, 40/89, 94/186 |
| Finite barrel lengths | Ref. [27]: "Sensitive barrel 0 < \|z\| < 400.5 / 749" mm; IBL arXiv:1803.00844 | INFERRED | fid 6/27, 22/68, 33/89, 62/186 |
| Layer radii | Ref. [27] ranges; ATLAS JINST; IBL arXiv:1803.00844 | REFERENCE-STATED (IBL INFERRED) | all |
| Pixel centre hits, 50 × 400 µm | Paper: "the center of each pixel hit is used", "pixel size rather than the resolution"; Ref. [27] | PAPER + REFERENCE-STATED | all |
| Neighbouring-pixel merging | Paper: "Hits in neightboring pixels … are merged" | PAPER-STATED (adjacency INFERRED) | all |
| SCT R-φ 34 µm | Paper: "twice the intrinsic accuracy quoted in [27]"; Ref. [27]: "17 µm (R−φ)" | PAPER rule × REFERENCE-STATED | all |
| SCT z 1160 µm | Same sentence, no coordinate named; Ref. [27]: "580 µm (z)" | INFERRED | final 1/7, 3/25, 6/40, 21/94 |
| SCT z 580 µm | Ref. [27] without doubling | INFERRED (sensitivity) | final 3/7, 5/25, 10/40, 29/94 |
| No SCT z smearing | none | UNDOCUMENTED | final 5/7, 11/25, 34/40, 76/94 |
| 45 mm beam spot | Paper: "gaussian smearing with width 45 mm to the z-coordinates of all the hits" | PAPER-STATED | — |
| Beam spot as common shift, fit from true vertex (primary) | Same + "primary vertex is identified correctly" | INFERRED | final 3/25, 21/94 (z 1160) |
| Beam spot as common shift, fit from origin | "located at the origin" read literally | INFERRED (alternative) | final 0/25, 3/94 |
| Beam spot per hit | "to the z-coordinates of all the hits" read per hit | INFERRED (alternative) | fid 21/68, 66/186; final 0, 0 |
| 25 ns timing cut | Paper Sec. IV | PAPER-STATED (location INFERRED) | all |
| Δw = √λ₂ | Paper Eq. 11 (Fig. 4 suggests ½) | PAPER-STATED | no change |
| Trigger pT(QQ̄) > 200 GeV | Paper III B | PAPER-STATED | 101/419, 207/873, 89/511, 186/1045 |
| Generator settings | not stated | UNDOCUMENTED | EW trigger 0.13–0.19 over 36 variations |
| Conversion background, acceptance A | Paper III D + the rows above | as above | 0/9139 (z 1160), 0 (580), 30/9139 (no z smear) |
