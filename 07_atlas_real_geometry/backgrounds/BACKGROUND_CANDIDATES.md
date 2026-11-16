# Background processes for the COP signal region: candidates (2026-11-15)

Supervisor comment (after the presentation): pile-up is not a background. It is overlaid on every process. The converted photon is one background, but other processes can also reach the signal region.

A background event must pass two requirements:

1. **Trigger:** MET > 200 GeV, as for the signal.
2. **COP selection:** a plane with 2 hits in all but one layer, ≥ 1 hit in the remaining layer, Δs < 0.01 cm and Δw < 1.0 cm (R10 Sec. IV). In practice this needs a very collimated pair of charged particles that comes from (or points back to) the beam line. Their hits then lie in one thin plane.

References (R1–R13, MG) are listed in `../references/REFERENCES.md`.

## A. Processes that pass the trigger

R9 lists the backgrounds of a MET-triggered selection. Cross sections below are our MG5 LO numbers at 13.6 TeV, with N = σ × 332 fb⁻¹ (`xsec_mg5/X01_xsec_13p6TeV.csv`).

| Process | Role in R9 | σ (MET > 200 GeV, LO) | Events in 332 fb⁻¹ |
|---|---|---|---|
| Z(νν̄)+jets | dominant | 10.8 pb | 3.6 × 10⁶ |
| W(ℓν)+jets, mostly W → τν | significant | ≤ 12.2 pb (upper bound: the charged lepton must also be lost) | ≤ 4.1 × 10⁶ |
| Z(ℓℓ)+jets, tt̄, single top, diboson | small | not computed yet | — |
| multijet with fake MET | small | not computed yet | — |
| non-collision (beam-induced, cosmic) | per-mille of the monojet SR | — | — |
| Z(νν̄)+γ+j (already tested, as in R10) | — | 0.230 pb | 7.6 × 10⁴ |

**Main point:** Z(νν̄)+jets alone is about 47 times larger than the Z(νν̄)+γ+j process we tested. Its jets contain π⁰, η, K_S and Λ, which our test did not have, because it used only the isolated photon.

## B. What inside these events can make a fake plane

| # | Source | Why it can fake a plane | Numbers (verified, R8 / R7 / R6) | Expected size |
|---|---|---|---|---|
| B1 | Photons from π⁰ → γγ and η → γγ in jets converting in material | Collimated e⁺e⁻ pair, the same topology as the tested background but from jets | BR(π⁰ → γγ) = 98.8%, BR(η → γγ) = 39.4%. Conversion probability P = 1 − exp(−7x/9X0). Be pipe wall only: x/X0 = 0.227% gives P = 0.18% per photon at η = 0; IBL (1.88%) gives 1.5% | probably the largest: many photons per jet |
| B2 | Dalitz decays π⁰ → e⁺e⁻γ, η → e⁺e⁻γ | Very collimated e⁺e⁻ pair from the primary vertex, no material needed | BR(π⁰ → e⁺e⁻γ) = 1.174%, BR(η → e⁺e⁻γ) = 0.69% | per π⁰ about 3× more e⁺e⁻ pairs than beam-pipe conversions (1.17% vs 2 × 0.18%) (DERIVED) |
| B3 | K_S → π⁺π⁻, Λ → pπ⁻ | Two tracks from a displaced vertex that points back to the PV, the same geometry as a conversion | cτ(K_S) = 2.684 cm, BR = 69.2%; cτ(Λ) = 7.846 cm, BR = 64.1% | The opening angle is large (m ≠ 0), so the Δw < 1 cm cut should reject most of them. Only very hard ones survive, and those decay late. Must be simulated |
| B4 | Hadronic τ decays (3 prongs) | 2–3 collimated tracks from the PV | from W → τν (R9) | Must be simulated |
| B5 | Hadronic interactions in the material (beam pipe, IBL, pixel supports) | Secondary tracks from a point in the material | Studied in R6; not modelled in R10 (R10 Sec. III D) | Needs a hadronic model (Geant4 or a parametrisation) |
| B6 | Cosmic-ray muons near the beam line | One straight track gives exactly 2 hits per layer on one line, so Δs ≈ 0 | non-collision background is per-mille of the monojet SR (R9) | Removed in real analyses by timing and impact-parameter cuts. We have no such cut yet |
| B7 | Detector effects: one track crossing two overlapping modules, split clusters, δ-rays | 2 hits in one layer from one particle | IBL φ overlap 1.82° (R2) | Needs the module geometry (07 step 2) |

The conversion background already tested also changes with the real material:

- The flat 1% conversion probability at the beam pipe is replaced by layer-by-layer conversion with P = 1 − exp(−7x/9X0), using `../geometry/atlas_run2_id_material.csv`.
- A conversion in the IBL or a later layer gives one layer without hits. The selection allows one layer with only 1 hit, and a pile-up hit can fill it.

## C. Plan to test them (proposal, not yet run)

1. **B01, generation:** Z(νν̄)+jets and W(ℓν)+jets at 13.6 TeV, MET > 200 GeV, MG5 + Pythia8. Pythia8 8.312 decays π⁰, η, K_S and Λ by default (`mayDecay = True`; K_L, K±, π± stable). The displaced decay vertices are therefore in the HepMC files (checked 2026-11-15).
2. **B02, detector:** all charged final-state particles propagated with helices in the 07 geometry; photon conversions layer by layer from the material table; pile-up overlaid as in Stage 2.
3. **B03, selection:** the same COP selection and SCT z settings as the signal.
4. **B04, normalisation:** the full statistics (3.6 × 10⁶ Z+jets events at 332 fb⁻¹) cannot be simulated. We therefore measure the pass probability per object (per photon, π⁰, K_S, τ) and multiply by the number of such objects per event, with an upper limit when nothing passes.
5. **Separate studies:** hadronic interactions (B5) and cosmic muons (B6).

**Not done yet:** tt̄, single top, diboson and multijet cross sections; the B5 model; the cosmic-muon rate.

## D. Result M01 (2026-11-15): conversion probability from the material (decision D2)

- **Beam pipe (before the IBL):** mean P_conv = 0.40% for all 9130 photons and 0.27% for \|η\| < 1.8, compared with the flat 1% used so far. This is 2.5–4× lower.
- **Uncertainty of the beam pipe value:** the Be wall alone is a lower bound, because the polyimide tapes are missing. Doubling the pipe material (variant BP_x2) gives 0.79% / 0.54%.
- **IBL:** P_conv = 2.8% (all) / 2.2% (\|η\| < 1.8), 5–7× more frequent than the beam pipe. These pairs have no IBL hit, but the selection allows one station with only 1 hit, which a pile-up hit could supply. This must be checked in D3 step 1.
- **Check:** the silicon total at \|η\| < 0.5 is 18%. R12 reports about 20% for the whole ID including the TRT, so the numbers are consistent.

Tables: `../tables/M01_conversion_summary.csv`, `../tables/M01_conversion_per_photon.csv`. Log: `logs/M01_conversion_probability.log`.

## E. C01 (2026-11-15): Z(νν̄)+γ+j conversions through the ATLAS geometry, material and station COP

**Setup** (`C01_conversion_bkg.py atlas`):

- Barrel + end-caps.
- Conversion on the first three material surfaces of each photon's path (beam pipe, then the first two silicon elements), each weighted with its material probability (D2).
- Electrons with brems and ionisation; pile-up with \|η\| < 2.5 track suppression; COP on per-hit stations (D1).
- Validated by T02–T05 (`../logs/`); T05 reproduces Stage 2 event by event in the barrel-only configuration.

**μ = 0, all 9130 photons** (`../tables/S01_C01_atlas_mu0.csv`, L = 332 fb⁻¹):

| Conversion surface | SCT z | passing events | expected events (332 fb⁻¹) |
|---|---|---|---|
| beam pipe (mean P = 0.40%) | 0 | 10 | 0.34 |
| beam pipe | 1.16 mm | 0 | < 0.10 (95% UL) |
| first silicon element, mostly IBL (P = 2.9%) | 0 / 1.16 mm | 0 / 0 | < 0.73 |
| second silicon element, mostly PIX1 (P = 5.0%) | 0 / 1.16 mm | 0 / 0 | < 1.29 |

**Comparison with Stage 2** (barrel only, flat 1%, μ = 0): 3 events, 0.25 expected at SCT z = 0, and 0 at 1.16 mm.

- With the material the beam-pipe weight is 2.5× lower.
- The end-caps add photons that pass the selection (10 instead of 3).
- The net change is +40%.

**μ = 20, 50, 60** (`C01_chain.sh`, finished 2026-11-16; `../tables/S01_C01_atlas_mu*.csv`; split and stat errors by `S02_conversion_breakdown.py` → `../tables/S02_conversion_breakdown.csv`). Expected events at 332 fb⁻¹, SCT z = 0, ± stat:

| μ | beam pipe | first Si element (mostly IBL) | second Si element (mostly PIX1) | **total** | Stage 2 (barrel only, flat 1%) |
|---|---|---|---|---|---|
| 0 | 0.34 ± 0.12 (10 ev.) | 0 (< 0.73) | 0 (< 1.29) | **0.34 ± 0.12** | 0.25 |
| 20 | 11.5 ± 0.7 (332) | 13.3 ± 2.3 (39) | 2.3 ± 1.3 (3) | **27.0 ± 2.7** | 9.2 |
| 50 | 17.6 ± 0.8 (517) | 47.3 ± 4.0 (162) | 4.2 ± 1.6 (8) | **69.2 ± 4.4** | 16.4 |
| 60 | 17.4 ± 0.8 (531) | 50.0 ± 4.1 (174) | 7.1 ± 1.9 (16) | **74.6 ± 4.6** | 16.7 |

**SCT z = 1.16 mm:** 0 passing events in every region and every μ (95% UL per region: 0.10 / 0.73 / 1.29). As in Stage 2, the 1.16 mm longitudinal resolution removes this background.

**Checks and where the increase comes from** (S02):

- **Barrel-like part agrees with Stage 2.** Beam-pipe conversions whose 8 winner stations are all barrel layers: 113 / 181 / 203 events at μ = 20 / 50 / 60. Stage 2 (same photons, barrel only) has 110 / 196 / 200. Their weight is 2.35 / 3.7 / 4.1 events. Stage 2 gives 9.2 / 16.4 / 16.7 at a flat 1%. The ratio of about 0.25 is the material probability at central η (M01: 0.27% for \|η\| < 1.8).
- **The new background comes from the end-caps.**
  - Planes that use at least one disk element give 9.1 / 13.9 / 13.3 events from the beam pipe and 12.1 / 40.1 / 39.5 events from the IBL.
  - None of these events has \|η\| < 1 (S02 column `final_abs_eta_lt_1`).
  - Forward photons cross more material (t ∝ 1/sin θ), so the conversion weight is larger.
  - Pile-up has more hits on the disks, which adds the one or two hits needed for the multiplicity.
- **Pile-up hits are needed.** In ≥ 98% of the passing events at μ ≥ 20, the plane has ≥ 1 pile-up hit (median: 1 for the beam pipe, 2 for the IBL, 3–4 for PIX1). There are no mixed hits.
- **Statistics:** the IBL and PIX1 rows rest on 39–174 and 3–16 events, so their errors are 9–58%.

**Not yet included / open:**

- The disk-pair cut \|Δr\| < 2 cm is the end-cap analogue of the paper's \|Δz\| < 2 cm (D1). The paper has no end-cap rule, so this choice drives the end-cap number and should be varied.
- Conversions beyond the second silicon element are not simulated. They have fewer than 8 stations left after the conversion, so their contribution should be small, but this is not yet checked.
- The signal has not yet been rerun through the 07 geometry. The end-caps may also raise the signal acceptance, so the reach cannot be judged from the background alone.
