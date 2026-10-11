# Converted-Photon Background (no pile-up) — Literal Reproduction (Phase 9)

> **v2 CORRECTION (2026-10-03):** the classification in this document is superseded where it conflicts with `CORRECTION_ACCEPTANCE_AND_LONGITUDINAL_2026-10-03.md`. The paper-stated acceptance (barrel only, |η| ≲ 1.8, no finite-z boundary) is now PRIMARY. The finite barrel of Ref. [27] (called "literal" below) is an INFERRED sensitivity. SCT z 1160 µm is INFERRED, not stated; no SCT z smearing is UNDOCUMENTED. Primary denominators: COL2000 25, EW2000 94. See `FINAL_EXECUTIVE_REPORT.md` (v2) and `PROFESSOR_REPORT_2026-10-03_v2.pdf`.

## Paper statement (Sec. III D, verbatim excerpts)

- "generating a Z+γ+j sample with MadGraph5_aMC@NLO, where we decay the Z to neutrinos and require at least 200 GeV of MET … the p_T of the photon be larger than 0.5 GeV."
- "The fiducial cross section for this process is ∼1 pb, which drops to ∼10 fb if we require that the photon converts in the beampipe using the conversion probability from figures 33.16 and 33.17 of [PDG]."
- "we assume equal energy sharing between both electrons"
- "The e⁺e⁻ pair is then passed through the same detector simulation as described for the pile-up background. We subsequently overlay pile-up hits …" The overlay is in `CONVERTED_PHOTON_PILEUP_OVERLAY_RESULTS.md`.

## Input sample and seeds

- **Photons:** the frozen photon sample `02_backgrounds/photon_conversion/zgamma_photons.csv` holds 9139 photons that pass the shower-level MET > 200 GeV, out of 10 000 generated, with σ_MG5 = 0.2310512 pb.
- **Event index:** the row index i of that CSV (0–9138).
- **Seeds:** `SeedSequence([99, 1708, i])`.

## Literal implementation

1. The vertex is z0 ~ N(0, 45 mm).
2. The photon goes straight to the beam pipe at r = 2.35 cm.
3. The energy is split into collinear e⁺ and e⁻ (E/2 each).
4. Each e± is propagated as an **exact helix (the pile-up detector simulation)**, with that simulation's per-hit 25 ns cut.
5. Detector: finite barrel, pixel-centre hits, SCT 34/1160 µm, neighbouring-pixel merging.
6. Literal Sec. III C fit relative to the **primary vertex** ("the primary vertex is identified correctly").

**Systematic configurations** (same random numbers per event; one change each):
- SYS_CONVPT: fit origin = conversion point (frozen project convention).
- SYS_Z0: SCT z not smeared (**calibrated, not literal**).
- SYS_ETA: η-cone acceptance.

**Validation:** with the frozen v4 code path and its sequential rng(99), the first 300 events reproduce the stored v4 rows exactly (300/300). The literal run completed 9139 × 4 configs with status `ok` for all (`P9_EXIT=0`).

## Cutflows (`tables/converted_photon_cutflow.csv`)

The first two count rows are not sequential cuts. Each is counted on its own over all 9139 photons.

| Stage | FROZEN v4 | **LITERAL** | SYS_CONVPT | SYS_ETA | SYS_Z0 (calibrated) |
|---|---|---|---|---|---|
| photons (MET > 200) | 9139 | 9139 | 9139 | 9139 | 9139 |
| plane with ≥ 1 hit in ≥ 4/8 layers | — | 1745 | 1746 | 2979 | 4311 |
| plane with ≥ 1 hit in 8/8 layers | — | 834 | 836 | 1437 | 505 |
| Sec. III C plane | 2982 | **1746** | 1746 | 3005 | 4323 |
| hit multiplicity 7 × 2 + 1 | 4 | **0** | 0 | 0 | 22 |
| Δw < 1 cm | 4 | 0 | 0 | 0 | 22 |
| Δs < 0.01 cm = final Sec. IV | 0 | **0** | 0 | 0 | **22** |
| CP95 upper limit on the final fraction | 3.3e-4 | **3.3e-4** | 3.3e-4 | 3.3e-4 | [2.4e-3 point; UL 3.4e-3] |

- The FROZEN v4 events passing the multiplicity cut are 3578, 5240, 5805 and 7723; all four fail Δs.
- The SYS_Z0 final events are 42, 450, 480, 705, 1382, 2616, 2962, 2982, 3608, 3656, 5806, 6131, 6589, 6605, 6616, 7235, 7531, 7733, 8216, 8436, 8810 and 8878 (row indices).

**The 22 SYS_Z0 events are a physical population, not noise.**
- All have photon p_T in a narrow band, 14.7–16.6 GeV, versus a sample median of 29.7 GeV.
- All have exactly 15 winner hits (2 in each of layers 2–8 plus 1 in L1), Δs = 30–76 µm and Δw = 0.45–0.51 cm.
- Δw ≈ 0.5 cm is the expected order for the opposite bending of the e± pair. For 7.5 GeV e± in 2 T, R = p_T/(0.3·B) ≈ 12.5 m, and each track deviates from the photon line by r²/(2R) ≈ 1.06 cm at the outer SCT (r = 51.4 cm), in opposite directions. The hits therefore spread about ±1 cm across the plane, and their RMS-type width √λ₂ is ≈ 0.5 cm.
- Softer pairs bend more and exceed Δw < 1 cm, as the paper itself notes ("softer electrons would bend more strongly").
- Harder pairs presumably fail because their two hits merge in the pixel layers. This was not isolated and is a hypothesis.
- **Under the literal 1.16 mm SCT z smearing these pairs fail Δs.** So the calibrated setting that brings the signal toward Table I also lets a conversion background into the signal region. The paper reports none, though it does mention "a few background events" in Fig. 5.

## Per-event changes, FROZEN v4 → LITERAL (`tables/converted_photon_event_changes.csv`)

| Change | Events |
|---|---|
| plane: frozen yes → literal no | 2169 |
| plane: frozen no → literal yes | 933 |
| multiplicity: frozen yes → literal no | 4 (3578, 5240, 5805, 7723) |
| final Sec. IV | no change (0 → 0) |

**Reason tags.** A tag means that turning only that one setting back to its frozen value restores the frozen decision; common random numbers make this test exact.

| Reason | Events |
|---|---|
| finite barrel vs η-cone | 964 |
| SCT z smearing | 924 |
| fit origin | 2 |
| SCT z + fit origin together | 1 |
| none single-isolated (random stream, helix propagation, merging) | 1215 |

These last 1215 are expected: the literal run uses per-event seeds and the pile-up helix simulation, while frozen v4 used one sequential stream and its own propagation.

## Weighted yields (`tables/weighted_yields_conversion.csv`; factors kept separate)

yield = σ × C × D × L, where:
- **A:** project σ after MET = 0.2310512 pb × 9139/10000 = **0.2112 pb**.
- **B:** paper σ ≈ **1 pb**. This is an alternative row only, never a correction; the factor 4.7 between A and B is unexplained (U7).
- **C:** conversion probability **0.01**, DERIVED from the paper's own "~1 pb → ~10 fb". The PDG curves need the beam-pipe material, which the paper does not state. σ × C = 2.11 fb (A) or 10 fb (B).
- **D:** detector + signal-region efficiency k/9139.

| Config | D | Yield, σ = A (fb) | Yield, σ = B (fb) | N at 300 fb⁻¹ (A) | N at 300 fb⁻¹ (B) |
|---|---|---|---|---|---|
| **LITERAL** | 0/9139 (UL 3.3e-4) | 0 (UL 6.9e-4) | 0 (UL 3.3e-3) | 0 (UL 0.21) | 0 (UL 0.98) |
| FROZEN v4 | 0/9139 | 0 (UL 6.9e-4) | 0 (UL 3.3e-3) | 0 (UL 0.21) | 0 (UL 0.98) |
| SYS_Z0 (calibrated) | 22/9139 | 5.1e-3 (UL 7.3e-3) | 2.4e-2 (UL 3.4e-2) | 1.5 (UL 2.2) | 7.2 (UL 10.3) |

The CSV also gives 36.1, 139 and 3000 fb⁻¹.

## Verdict (conversion only)

- **Literal:** 0/9139 conversion-only events reach the signal region. The 95% upper limit is 0.21 events (project σ) or 0.98 events (paper σ) at 300 fb⁻¹. This agrees with the paper's conclusion that the background is negligible.
- **Calibrated (SCT z unsmeared):** 22/9139 pass, which is ~1.5–7 events at 300 fb⁻¹. **The Table I-calibrated detector model is therefore not background-free for conversions.** This is a further reason not to adopt it silently.
- **Unresolved:** the σ normalisation, A vs B (U7).
