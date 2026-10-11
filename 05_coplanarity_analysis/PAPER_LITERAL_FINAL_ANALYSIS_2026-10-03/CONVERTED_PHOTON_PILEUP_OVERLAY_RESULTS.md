# Converted Photon + μ = 50 Pile-up Overlay — Literal Reproduction (Phase 10)

> **v2 CORRECTION (2026-10-03):** the classification in this document is superseded where it conflicts with `CORRECTION_ACCEPTANCE_AND_LONGITUDINAL_2026-10-03.md`. The paper-stated acceptance (barrel only, |η| ≲ 1.8, no finite-z boundary) is now PRIMARY. The finite barrel of Ref. [27] (called "literal" below) is an INFERRED sensitivity. SCT z 1160 µm is INFERRED, not stated; no SCT z smearing is UNDOCUMENTED. Primary denominators: COL2000 25, EW2000 94. See `FINAL_EXECUTIVE_REPORT.md` (v2) and `PROFESSOR_REPORT_2026-10-03_v2.pdf`.

## Paper statement (Sec. III D)

"The e⁺e⁻ pair is then passed through the same detector simulation as described for the pile-up background. We subsequently overlay pile-up hits and pass the resulting set of hits through our reconstruction algorithm."

## Implementation (`scripts/P10_literal_overlay.py`; run completed `P10_EXIT=0`, 9139/9139 events, 183 chunks)

- **Hard part:** identical to the P9 LITERAL configuration, with the same per-event seeds `SeedSequence([99, 1708, i])`, so the conversion hits are the same.
- **Pile-up:** μ = 50 from the 20k minimum-bias pool, with tracking-efficiency suppression, as in the frozen overlay driver.
  - Seeds: `SeedSequence([90210777, i]).spawn(2)`, the frozen overlay convention.
  - Detector response: literal (finite barrel, SCT 34/1160 µm).
- **Merging:** raw conversion and pile-up hits are merged once (neighbouring pixels).
- **Fit origin:** the primary vertex (LITERAL), or the conversion point (SYS_CONVPT).
- **Recorded per event:** the full cutflow and the ancestry of the winning plane's hits (conversion / pile-up / merged-mixed).
- **Displays:** the full hit lists of all plane + multiplicity events are stored in `logs/P10_chunks_LITERAL/displays_*.jsonl` (47 files).

## Cutflow (`tables/overlay_cutflow.csv`)

All counts are out of 9139 photons.

| Stage | FROZEN overlay v1 | **LITERAL** | SYS_CONVPT |
|---|---|---|---|
| plane with ≥ 1 hit in ≥ 4/8 layers (non-sequential) | — | 1886 | 1883 |
| plane with ≥ 1 hit in 8/8 layers (non-sequential) | — | 899 | 901 |
| Sec. III C plane | 3276 | **1990** | 1969 |
| hit multiplicity 7 × 2 + 1 | 203 | **48** | 50 |
| Δw < 1 cm | 203 | **48** | 50 |
| Δs < 0.01 cm = final Sec. IV | 1 (event 2555) | **0** | 0 |
| final fraction, CP95 one-sided upper limit | 1.1e-4 (point) / 5.2e-4 | **3.3e-4** | 3.3e-4 |

- **Frozen event 2555 has no reconstructed plane in the literal reprocessing**, in either configuration.
- The frozen overlay's stored "Δs pass = 78" is non-sequential; 1 event survives in sequence.
- **Literal plane + multiplicity events: 48.**
  - Δs ranges from 121 to 305 µm (median 222 µm). **None comes within the 100 µm cut**; the closest is event 3980 with Δs = 121 µm and Δw = 0.35 cm.
  - Every one of the 48 winning planes combines conversion hits (13.2 on average) with pile-up hits (2.9 on average). Pile-up hits supply the missing second hit in layers where the e⁺e⁻ hits merged. This is how the overlay creates multiplicity passes (48) that the conversion alone does not (0).
- **Winner ancestry over all 1990 literal planes** (`tables/overlay_winner_ancestry.csv`):
  - 1146 combine conversion and pile-up hits;
  - 705 contain conversion hits only;
  - 139 contain pile-up hits only.
  - "Mixed" here means the plane contains hits of both origins. No individual winner hit was formed by merging a conversion and a pile-up pixel.

## Per-event changes, FROZEN overlay → LITERAL (`tables/overlay_event_changes.csv`)

| Change | Events |
|---|---|
| plane: frozen yes → literal no | 2297 |
| plane: frozen no → literal yes | 1011 |
| plane + multiplicity: frozen yes → literal no | 200 |
| plane + multiplicity: frozen no → literal yes | 45 |
| final: frozen yes → literal no | 1 (event 2555) |

**Reasons for the changes:**
- The literal detector: finite barrel, SCT z smearing of 1160 µm, and the primary-vertex fit origin.
- The per-event conversion seed. Frozen v1 used a sequential stream.

Single-setting attribution was done for conversion only (P9, with common random numbers). It was not repeated here, because each overlay pass costs about 1.5 h.

## Weighted yields (`tables/weighted_yields_overlay.csv`; same factorisation as `CONVERTED_PHOTON_RESULTS.md`)

| Config | D | N at 300 fb⁻¹, σ = A (0.211 pb) | N at 300 fb⁻¹, σ = B (1 pb, alternative) |
|---|---|---|---|
| **LITERAL** | 0/9139 | **0 (95% UL 0.21)** | 0 (95% UL 0.98) |
| SYS_CONVPT | 0/9139 | 0 (UL 0.21) | 0 (UL 0.98) |
| FROZEN overlay v1 | 1/9139 | 0.069 (UL 0.33) | 0.33 (UL 1.56) |

The CSV also gives 36.1, 139 and 3000 fb⁻¹.

## Not run

- **Overlay with SCT z unsmeared (calibrated).** Conversion alone already gives 22/9139 signal-region events in that setting (`CONVERTED_PHOTON_RESULTS.md`), and pile-up can only add hits. It is therefore expected to stay at least of that order, but it was not simulated: it is not part of the literal analysis, and it would take another ~1.5 h pass.

## Verdict (overlay)

- **Literal:** 0/9139 converted-photon + pile-up events pass the signal region (UL < 0.21 events at 300 fb⁻¹ with the project σ, < 0.98 with the paper's 1 pb). This is consistent with the paper's conclusion of negligible background in the signal region.
- **Where the literal background is rejected:** at the Δs cut. Like the signal, it fails because of the 1.16 mm SCT z resolution.
- The one frozen-project final event (2555) does not reappear.
- Pile-up turns about 2.4% of conversion planes into multiplicity-passing candidates (48 vs 0). In the paper's Fig. 5 sense, these are the most signal-like background.
