# Detector — Literal Implementation Report (Phase 2)

> **v2 CORRECTION (2026-10-03):** the classification in this document is superseded where it conflicts with `CORRECTION_ACCEPTANCE_AND_LONGITUDINAL_2026-10-03.md`. The paper-stated acceptance (barrel only, |η| ≲ 1.8, no finite-z boundary) is now PRIMARY. The finite barrel of Ref. [27] (called "literal" below) is an INFERRED sensitivity. SCT z 1160 µm is INFERRED, not stated; no SCT z smearing is UNDOCUMENTED. Primary denominators: COL2000 25, EW2000 94. See `FINAL_EXECUTIVE_REPORT.md` (v2) and `PROFESSOR_REPORT_2026-10-03_v2.pdf`.

**Sources read directly:**
- The paper: arXiv:1708.02243v2 LaTeX source, plus the v1 diff.
- **Ref. [27]**, ATL-PHYS-PUB-2009-002 "The Expected Performance of the ATLAS Inner Detector". CERN CDS is bot-blocked, so it was read through its identical publication as the ID chapter of the ATLAS CSC book, arXiv:0901.0512, PDF pp. 40–43. That text is in `notes/ref27_CSC_ID_chapter_pages40-43.txt`, with the PDF SHA-256 recorded.
- ATLAS JINST 3 S08003, for the intermediate layer radii.
- arXiv:1803.00844 and arXiv:2007.07624, for the IBL.

The full table with verbatim quotes is `tables/DETECTOR_PARAMETER_SOURCE_TABLE.csv` (copy: `detector_parameter_sources.csv`).

## Answers to the Phase 2 questions

| # | Question | Literal answer | Classification |
|---|---|---|---|
| 1 | Radii of the 8 layers | IBL 33.25 mm; pixel 50.5, 88.5, 122.5 mm; SCT 299, 371, 443, 514 mm. Ref. [27] gives the ranges "50.5 < R < 122.5" (3 layers) and "299 < R < 514" (4 layers); ATLAS JINST Fig. 4.1 gives each radius. The paper's own Fig. 4 hit spacing (n₃ ≈ 4.7, 7.8, 13.7, 18.7, 46, 57, 68, 79 cm; 79/46 = 51.4/29.9) confirms an IBL + 3 pixel + 4 SCT geometry. | REFERENCE-STATED; IBL **INFERRED** (not in the paper or [27]; derived from paper Fig. 4) |
| 2 | Pixel dimensions used as hit resolution | 50 × 400 µm ([27]: "minimum pixel size on a sensor is 50×400 µm²"); hit = centre of the hit pixel (paper: "the center of each pixel hit is used"; "pixel size rather than the resolution"). IBL 50 × 250 µm. | PAPER + REFERENCE-STATED; IBL pitch INFERRED |
| 3 | SCT intrinsic accuracy | **17 µm (R-φ) and 580 µm (z), per module**. The SCT "uses small-angle (40 mrad) stereo strips to measure both coordinates"; z footnote: "Arises from the 40 mrad stereo angle". 17 µm is an **intrinsic accuracy** (resolution), not the pitch (80 µm). [27] does not call it a Gaussian σ; treating it as one is the conventional reading. | REFERENCE-STATED (Gaussian form INFERRED) |
| 4 | "Twice the intrinsic accuracy" | σ_Rφ = 2 × 17 = **34 µm**, σ_z = 2 × 580 = **1160 µm**. The paper's sentence names no coordinate, and [27] quotes both, so the literal reading doubles both. | PAPER-STATED + REFERENCE-STATED |
| 5 | Neighbour-hit merging | "Hits in neightboring pixels … are merged to a single hit" (paper's spelling). Implemented as transitive 8-neighbour adjacency in pixel-index space, merged at the cluster centroid; SCT hits not merged. | PAPER-STATED (adjacency and centroid INFERRED) |
| 6 | Physical barrel lengths | Pixel sensitive barrel 0 < \|z\| < 400.5 mm; SCT sensitive barrel 0 < \|z\| < 749 mm ([27] table); IBL \|z\| < 330.15 mm. | REFERENCE-STATED; IBL INFERRED |
| 7 | Finite z, explicit η cut, or both? | The paper says only "we only included the barrel of the pixel and SCT detectors … which effectively restricts the fiducial range to \|η\| ≲ 1.8". There is **no explicit η cut** in the text. **Literal: finite barrel cylinders, no η cut.** The paper's "≲ 1.8" does not equal the all-8-finite-layers limit (\|η\| ≲ 1.17 at the outer SCT layer) and is recorded as an unresolved difference. The η-cone (project) is kept as a systematic; the combination of both is not used (the paper does not describe it). | PAPER + REFERENCE-STATED |
| 8 | 45 mm beam spot | "a uniform, gaussian smearing with width 45 mm to the z-coordinates of all the hits". "Uniform" over all hits = **one common per-event z shift**; independent 45 mm shifts per hit would destroy every plane. Equivalent to displacing the vertex, because the EOM is z-translation invariant. The fit uses the true vertex ("primary vertex is identified correctly"). | DERIVED DIRECTLY |
| 9 | 25 ns timing | "We also include a 25 ns timing cut" in ε_fid; the location is not stated. Implemented as the maximum of the 16 tracker-layer crossing times < 25 ns (the paper's Sec. III A treats timing as relevant only for detectors further out). | PAPER-STATED (location INFERRED) |

## Conflicts between the literal reading and the paper's own figures

- **SCT z = 1160 µm vs paper Fig. 5 / Fig. 4.**
  - The paper's signal Δs (median ≈ 28 µm EW, 35 µm colored; ≈ 90% < 0.01 cm) and its Fig. 4 event (Δs = 83 µm) are incompatible with 1.16 mm SCT z smearing.
  - Literal median ≈ 150 µm; KS p ≈ 0 for both benchmarks.
  - **No paper-text-based resolution of this exists.** The literal value stays authoritative, and z ∈ {0, 34, 580} µm is reported as a systematic envelope. Z0 ("no z smearing") is **calibrated, not paper-proven**.
- **\|η\| ≲ 1.8 vs finite barrel.** See row 7.
- **Δw definition vs paper Fig. 4.** Not a detector parameter. The Eq. 11 statistic is 2× the paper's plotted Δw (`UNRESOLVED_DIFFERENCES.md`).

## Project implementation status

- **Frozen project code: not modified.** The literal response is in `scripts/literal_detector.py` and `scripts/P4_literal_signal.py`. It is the frozen response with one change, acceptance = finite barrel (no η cut).
- **Exactness of the replay:** every literal-geometry SCT hit is also accepted by the frozen η-cone at the SCT radii, so all literal signal hits use the project's own recorded random draws (0 extra draws needed).
