# Stage 2 · Run 3 · ATLAS — quirk reach with the ATLAS inner detector at 13.6 TeV, 332 fb⁻¹, 10k signal samples (folder 07)

**Status, 2026-11-17: final for the 13 mass points of Stage 1 · Run 3 · Ideal plus EW 1200 GeV (14 points).**

- All three Λ bands (0.1–25 keV) were propagated on the server, in two runs on the same events:
  - `signal/runs/large_atlas`: G01 atlas geometry;
  - `signal/runs/large_ideal`: G01 stage2 geometry, the 8 barrel layers of Stage 1 · Run 3 · Ideal.
- Every table and figure below is rebuilt from the server runs (`reach/R00_postprocess.sh central_b`).
- The earlier laptop propagation is kept only for the reproducibility check in §9. It is in `signal/runs/atlas_large_laptop_INTERIM_2026-11-17`; it is superseded and not used for any result.
- EW 1200 GeV was generated and propagated on the server on 2026-11-17 (all bands, both geometries). It closes the EW region at high mass (§6).

All numbers are read from saved files. The full tables are in `tables/R02_results_summary.md` (written by `reach/R02_results_summary.py`). The Stage 1 · Run 3 · Ideal vs Stage 2 · Run 3 · ATLAS comparison is in `compare/X02_SUMMARY.md`.

**Naming (simulation matrix, 2026-11-17).**

| Name | Geometry | √s | L | Here |
|---|---|---|---|---|
| Stage 0 · Paper · Ideal | Knapen et al. (R10) barrel | 13 TeV | 300 fb⁻¹ | `05_coplanarity_analysis` |
| Stage 1 · Run 2 · Ideal | same | 13 TeV | 139 fb⁻¹ | `06_publication/S1_13TeV_139fb_knapen_noPU_cop` |
| Stage 1 · Run 3 · Ideal | same | 13.6 TeV | 332 fb⁻¹ | 2k: `06_publication/S2_13p6TeV_run3_knapen_noPU_cop`; 10k: `signal/runs/large_ideal` |
| Stage 2 · Run 3 · ATLAS | ATLAS ID, barrel + end-caps | 13.6 TeV | 332 fb⁻¹ | `signal/runs/large_atlas` (this document) |
| Stage 2 · Run 2 · ATLAS, Stage 2 · Run 2/3 · CMS | — | — | — | not done |

- Tables and files use the short tags `S1_Run3_Ideal`, `S1_Run3_Ideal_2k` and `S2_Run3_ATLAS`.
- In older files, "Stage 2" (and folder names with `S2_`) means Stage 1 · Run 3 · Ideal with 2k events. Folder names are unchanged.
- "Ideal" and "ATLAS" below are short for Stage 1 · Run 3 · Ideal and Stage 2 · Run 3 · ATLAS.



## Headline: realistic SCT (A580), with background, 332 fb⁻¹

**Background simulated.** Only Z(νν̄)γ conversions are simulated, with pile-up. Z(νν̄)+jets (47× larger σ) is estimated, not simulated (`backgrounds/BACKGROUND_CANDIDATES.md`, `backgrounds/ZJETS_PLAN.md`).

**SCT setting.** The headline uses the ATLAS intrinsic SCT resolution (A580: 17 µm × 580 µm, R3). Each geometry has its own converted-photon background:
- ATLAS: C01 with end-caps and the material conversion probability;
- Ideal: barrel only, with a flat 1% conversion probability at the beam pipe, as in 06 S2.

**Background value.** The background is the central MC estimate, with b = 0 when no MC photon passes. The MC 95% upper limit is given only as a systematic variant.

Reach at 332 fb⁻¹ (exclusion / discovery, GeV; `tables/X08_reach_with_background.csv`, figure G09):

| channel | geometry | μ = 0 | μ = 20 | μ = 50 |
|---|---|---|---|---|
| colored | **ATLAS** | **1697 / 1618** | **1697 / 1618** | **1697 / 1591** |
| colored | Ideal | 1591 / 1515 | 1591 / 1478 | 1591 / 1488 |
| EW | **ATLAS** | **768 / 681** | **768 / 681** | **768 / 651** |
| EW | Ideal | 631 / 560 | 631 / 532 | 631 / 540 |

A580 background (events at 332 fb⁻¹, central values; MC passing photons in brackets):

| μ | ATLAS | Ideal |
|---|---|---|
| 0 | 0 (0) | 0 (0) |
| 20 | 0.077 (3) | 0.42 (5) |
| 50 | 0.34 (5) | 0.33 (4) |

- **Every passing A580 photon passes because of pile-up hits** (§7, "What the background is made of"). The "5" at ATLAS μ = 50 is 5 photon–region rows from 4 distinct photons. At μ = 0 the same photons pass Δs and Δw but fail the hit-multiplicity cut. One or two pile-up hits in the winning plane complete it.
- **These numbers cover Zγ conversions only.** Pile-up can complete a near-miss two-track object from any MET-triggered event, and it can also make planes on its own. A factorised estimate is planned (`backgrounds/PILEUP_FACTORISATION_PLAN.md`).
- In every case the A580 background is below one event, and the exclusion needs 3.0 signal events.
- The discovery needs max(5, Asimov Z = 5) signal events: 5.0–6.4.
- **Systematic variant: b = MC 95% upper limit when no photon passed.**
  - ATLAS: UL = 1.29 events; Ideal: UL = 0.25 events.
  - This changes only the μ = 0 exclusion: ATLAS 1650 GeV (colored) and 718 GeV (EW); Ideal unchanged.
  - The larger ATLAS UL comes from the larger per-photon weights of silicon-layer conversions with only 9 130 MC photons. It is an MC-statistics limit, not a physics effect.
- **Ideal discovery vs μ.** It is not monotonic in μ (EW 532 GeV at μ = 20, 540 GeV at μ = 50). This is MC statistics: 5 vs 4 passing photons give b = 0.42 vs 0.33 events.

**Best case: perfect SCT z (Z0, σ_long = 0), with background.** Z0 has the largest background. Reach (exclusion / discovery, GeV):

| channel | geometry | μ = 0 | μ = 20 | μ = 50 |
|---|---|---|---|---|
| colored | ATLAS | 1871 / 1749 | 1647 / 1517 | 1589 / 1447 |
| colored | Ideal | 1735 / 1646 | 1598 / 1465 | 1568 / 1427 |
| EW | ATLAS | 994 / 866 | 750 / 613 | 690 / 557 |
| EW | Ideal | 826 / 730 | 683 / 563 | 654 / 534 |

Z0 background (events at 332 fb⁻¹):

| μ | ATLAS | Ideal |
|---|---|---|
| 0 | 0.34 | 0.25 |
| 20 | 27.0 | 9.2 |
| 50 | 69.2 | 16.4 |

With pile-up, the ATLAS end-caps raise the Z0 background about 4 times, and the realistic A580 setting gives a larger reach than Z0 in ATLAS.

## 1. What was done

| Step | Script | Output | Check |
|---|---|---|---|
| 10 000 generated events per mass point (EW 100–1000 GeV, colored 600–2400 GeV; EW 1200 added), the MG5/Pythia cards of 06 S2, new seeds | `signal/G02_large_samples.py` (L01 and L02 of 06, unchanged) | `signal/inputs_large/` | σ and ε_trig agree with 06 S2 (largest pull 2.7σ) |
| Propagation, ATLAS geometry (barrel + end-caps, 8 ATLAS-like stations, D1) and ideal geometry (Stage 1 · Run 3 · Ideal), 3 SCT settings (D4) | `signal/G01_signal_07.py` atlas / stage2 (server) | `signal/runs/large_atlas`, `large_ideal` | T07, T08 |
| Grid N(m, Λ), reach, reach with background | `reach/R01_reach_07.py` (method of 06 S2 unchanged) | `tables/R01_*.csv` | T09 (reproduces S2 tables exactly), T11 (independent recount, 585/585 rows) |
| Ideal vs ATLAS (S1 · Run 3 · Ideal vs S2 · Run 3 · ATLAS): grids, reach, McNemar, crossings | `compare/X02_ideal_vs_atlas.py` | `tables/X02_*.csv` | the X02 ATLAS grid equals the R01 grid |
| End-cap gain checks | `compare/D01_endcap_gain.py`, `X04`, `X05` | `tables/D01_*`, `X04_*`, `X05_*` | — |
| Contour edges | `compare/X03_contour_edges.py` | `tables/X03_contour_edges.csv` | — |
| Laptop vs server reproducibility | `compare/X01*.py` | `tables/X01*.csv` | — |
| ROOT figures G01–G10 and X02 | `FIGURES_ROOT_2026-11-17/make_figures_07.py`, `compare/make_figures_X02.py` | pdf, png, root, C, caption, provenance | checked by eye |

SCT settings (D4) set the SCT resolution in the long direction (barrel z, disk R):

- **Z0:** σ_long = 0, as 06 S2 "σ_z = 0";
- **A580:** the ATLAS intrinsic resolution, 17 µm × 580 µm (R3 Table 4.1; main setting);
- **Z1160:** the Knapen et al. (R10) value, 34 µm × 1.16 mm.

## 2. Signal samples

ε_trig is computed over matched events. For colored, f_ch is the fraction of triggered events with both quirks charged.

| channel | m (GeV) | σ (fb) | n_matched | n_trigger | ε_trig | f_ch | ε_trig S1 · Run 3 · Ideal (2k) |
|---|---|---|---|---|---|---|---|
| EW | 100 | 1226 | 6911 | 216 | 0.031 | 1 | 0.033 |
| EW | 400 | 7.097 | 5637 | 646 | 0.115 | 1 | 0.117 |
| EW | 1000 | 0.07986 | 5104 | 965 | 0.189 | 1 | 0.183 |
| EW | 1200 (added 2026-11-17) | 0.02623 | 5028 | 963 | 0.192 | 1 | — |
| colored | 600 | 964 | 3806 | 972 | 0.255 | 0.308 | 0.211 |
| colored | 1500 | 2.109 | 4062 | 1028 | 0.253 | 0.348 | 0.283 |
| colored | 2400 | 0.02349 | 4487 | 968 | 0.216 | 0.325 | 0.219 |

All points are in `tables/R02_results_summary.md` §2. Figures: G01, and G02 for the quirk velocity β = |p|/E. The median β falls from 0.96 (EW 100 GeV) to 0.68 (EW 1000 GeV), and from 0.73 (colored 600 GeV) to 0.50 (colored 2400 GeV).

## 3. Detector model relevant to the end-cap gain

**Geometry (R1–R3).**
- Ideal: 8 barrel layers, no end-caps. Knapen et al. (R10) define the 8-layer Pixel+SCT structure; the numerical layer radii and lengths of our simplified cylindrical implementation are taken from ATLAS detector documentation (R1 Table 1 radii, R2 IBL length, R3 active lengths). Full element-by-element comparison: `GEOMETRY_COMPARISON.md`.
- ATLAS: the same 8 barrel layers, plus 3 + 3 pixel disks (|z| = 49.5–65 cm, r = 8.9–15.0 cm) and 9 + 9 SCT disks with their rings (|z| = 83.9–273.5 cm, r = 27.5–56.0 cm). In the code, the barrel elements of both geometries are identical.

**η acceptance.**
- Ideal: all 8 barrel layers must be crossed inside their length. The SCT barrel at r = 51.4 cm has half-length 74.9 cm, which gives |η| < asinh(74.9/51.4) = 1.18 at z0 = 0 (T01: all 8 layers for |η| ≤ 1.15).
- ATLAS: 8 stations (D1, R14) and |η| < 2.5 for the line from the PV to station 8.
- Measured on the selected events (Z0, Λ = 4 keV; `tables/X04_eta_acceptance.csv`):
  - ideal: the largest |η_pair| is 1.08–1.27;
  - ATLAS: up to 2.41–2.50;
  - 45–60% of the ATLAS-selected events have |η_pair| > 1.2.
  - η_pair is the direction of P1 + P2. The string binds the pair, so the hits follow the pair, not each quirk's initial direction.

**Resolution on the disks** (`sim/detsim07.py` respond):
- SCT rings measure r-φ and R:
  - r-φ: 34 µm (Z0, Z1160) or 17 µm (A580);
  - R (the coarse coordinate): Gaussian with σ_long = 0 / 1.16 mm / 580 µm, z = the ring's |z|.
- Pixel disks are quantised: radial pitch 400 µm (σ = 400/√12 = 115 µm), r-φ pitch 50 µm at the disk's mean radius.

**Material.**
- There is no multiple scattering and no energy loss for the quirks: the quirk integrator of Stages 0–1 is used unchanged (README "to do": dE/dx in the integrator).
- Disk material, x/X0 per crossing, enters only the electron tracks of the background: bremsstrahlung and ionisation, no multiple scattering.
  - SCT disk: 3.75% (R3 Sec. 4.10), counted per ring crossing.
  - Pixel disk: 3.57%, the per-layer pixel barrel value of R3, used for lack of a disk value.
- The conversion probability uses the full material (M01).

**Plane fit** (`sim/cop07.py`).
- There is one fit per event, not an OR of separate barrel and end-cap fits.
- Every hit gets a station 1–8: the number of pixel (SCT) elements crossed by the straight line PV → hit, plus 1. This is the k-th measurement along the track, as ATLAS counts measurements on barrel layers and disks alike (R14).
- The paper's algorithm then runs on stations 1–8 exactly as on layers 1–8, with barrel and disk hits in the same fit.

## 4. Check of the end-cap gain ("Stage 2 · Run 3 · ATLAS > Stage 1 · Run 3 · Ideal")

**(a) Paired comparison on the same events** (`tables/X02_mcnemar_*.csv`; McNemar exact test, Holm correction).
- No event selected in ideal is lost in ATLAS: b = 0 in all 195 (mass, Λ) tests, for fid and for all three selections.
- All significant differences are ATLAS gains:

| quantity | significant tests (of 195) |
|---|---|
| fid | 195 |
| Z0 | 119 |
| A580 | 71 |
| Z1160 | 46 |

- Summed over masses, k_ATLAS / k_ideal is about 1.7–2.4 at Λ = 1–15 keV.

**(b) Why Δs and Δw are bit-identical for events selected in both.**
- These events have no end-cap hit at all: 0 of 598 control events at 7 (point, Λ) combinations, in `tables/D01_control_endcap_hits.csv`.
- Over the full grid, `<sct>_endcap` is False for every one of the 9 489 (Z0), 2 715 (A580) and 1 511 (Z1160) rows selected in both (`tables/X05_endcap_flag_full.csv`).
- The reason: a quirk pair inside the barrel acceptance leaves the barrel at |z| < 75 cm. The first SCT disk is at |z| = 83.9 cm, and the pixel disks (r < 15 cm, |z| ≥ 49.5 cm) need |η| > 1.9.
- Without end-cap hits, the station of each hit equals its barrel layer, and the hits and SCT random numbers are the same in both geometries (same seeds). So the fit inputs are identical. This is the T05/T07 property: with the barrel only, every hit's station is its layer.

**(c) What the extra events are.** Over the full grid, every ATLAS-only selected row has `<sct>_endcap` = True: 11 036 (Z0), 2 606 (A580), 1 414 (Z1160). There is no barrel-only gain.

D01 reran the extra events on the laptop and recorded the element of every station of the winner plane. Points: EW 400 GeV at Λ = 1, 4, 15 keV; EW 1000 GeV at 4 keV; colored 900 GeV at 1 and 4 keV; colored 1800 GeV at 4 keV (`tables/D01_endcap_gain.csv`).

| class | Z0 | A580 | Z1160 |
|---|---|---|---|
| barrel + end-cap (mixed) | 786 | 202 | 116 |
| end-cap only | 0 | 0 | 0 |
| barrel only | 0 | 0 | 0 |

- The number of end-cap stations in the extra planes is 1–6 of 8, never 7 or 8.
- End-cap-only planes cannot occur inside |η| < 2.5: the IBL (|z| < 33 cm at r = 3.3 cm) and the first pixel layer always give stations 1 and 2 on the barrel.
- The laptop rerun reproduced 1 104 of the 1 114 server selections in these groups (99.1%). The other 10 are the numerical difference of §9.

## 5. Reach, zero background, 332 fb⁻¹ (figures G05, G09, X02)

Values are exclusion (N = 3) / discovery (N = 5) in GeV. Brackets give the ±1σ Wilson range of the exclusion reach.

| channel | SCT | S2 · Run 3 · ATLAS (10k) | S1 · Run 3 · Ideal (10k) | S1 · Run 3 · Ideal (2k, 06 S2) |
|---|---|---|---|---|
| colored | **A580 (headline)** | 1697 [1674, 1719] / 1618 | 1590 [1564, 1618] / 1515 | — |
| colored | Z1160 | 1612 [1584, 1640] / 1529 | 1497 [1466, 1535] / 1430 | 1468 / 1352 |
| colored | Z0 (best case) | 1871 [1857, 1885] / 1777 | 1734 [1717, 1752] / 1659 | 1785 / 1681 |
| EW | **A580 (headline)** | 767 [754, 781] / 681 | 631 [607, 653] / 560 | — |
| EW | Z1160 | 671 [651, 690] / 588 | 565 [541, 593] / 500 | 589 / 465 |
| EW | Z0 (best case) | 994 [988, 999] / 900 | 826 [813, 838] / 744 | 809 / 743 |

- S1 · Run 3 · Ideal with 10k events agrees with the 2k sample (06 S2) within the 2k Wilson bands. This is the expected check, because the geometry is the same.
- ATLAS exceeds ideal by about 100–140 GeV (colored) and about 90–170 GeV (EW). This is the end-cap gain of §4.
- The reach is at its maximum at Λ = 4–5 keV.

## 6. Where the contours cross the grid, and where they leave it

**(a) Interpolation between mass points** (`tables/X02_crossings_mass.csv`). Each crossing is computed log-linear, as the reach method does, and with a 3-point quadratic as a check.
- At the maximum reach the two differ by at most 8 GeV (ATLAS) and 14 GeV (ideal). This is below the Wilson half-range in every case, except EW Z0 ATLAS discovery, where −5.7 GeV is about equal to the half-range of 5.5 GeV.
- **Finer mass points are not needed for m_max.**
- On the flanks (Λ ≤ 1 keV or ≥ 20 keV) the two interpolations differ by up to 44–55 GeV, in 18 of 276 crossings. This affects only the shape of the lines.

**(b) Grid edges** (`tables/X03_contour_edges.csv`; N ≥ threshold at an edge point means the contour is open there).

| edge | status |
|---|---|
| bottom (Λ = 0.1 keV) | closed everywhere |
| right (highest mass: colored 2400, EW 1200 GeV) | closed everywhere |
| left (EW 100 / colored 600 GeV) | open everywhere, including the 2k sample of 06 S2: the region starts at the lowest generated mass |
| top (Λ = 25 keV) | open for Z0 in both channels: N(25 keV) ≥ 3 for EW 100–400 GeV and colored 600–1500 GeV (ATLAS; ideal similar). Also open for colored A580 (600, 900 GeV) and colored Z1160 (600 GeV). Closed for EW A580 and EW Z1160. The 2k sample (06 S2) is also open at the top for Z0. |

- **EW with the 1200 GeV point.** For ATLAS Z0, N = 8.59 at 800 GeV, 2.90 at 1000 GeV and at most 0.92 at 1200 GeV (all Λ). The N = 3 line therefore crosses between 800 and 1000 GeV (994 GeV). There is no crossing between 1000 and 1200 GeV, and the right edge is closed.
  - At 1200 GeV the largest N is: ATLAS A580 0.23, Z1160 0.12; Ideal Z0 0.39, A580 0.11, Z1160 0.06.
  - At 355 fb⁻¹ the EW Z0 exclusion is 1006 GeV, now inside the grid. `reach_beyond_grid` is False everywhere.
  - The EW reach values did not change with the new point.
- **The top edge:** closing it needs Λ points above 25 keV. Above 15 keV, the integration failures grow (EW: 3.2% at 15 keV, 8.7% at 20 keV, 20.4% at 25 keV; 2k sample, 06 S2: 3.4%, 9.9%, 22.2%). They count as not fiducial, so N at the top edge is underestimated by up to about 20%. Larger Λ would first need the integrator step limit to be raised.

## 7. Converted-photon background and pile-up (figures G06–G08)

**What is simulated.** Only Z(νν̄)γ conversions are simulated, with pile-up. Z(νν̄)+jets (47× larger σ) is estimated, not simulated.

**Samples.** 9 130 Z(νν̄)γ+j photons (10 000 generated; MET > 200 GeV). The same photons, seeds and pile-up are used in every run. The pile-up pool has 20 000 minimum-bias events.

Background at 332 fb⁻¹, central values (`tables/X08_background_used.csv`):

| SCT | geometry | μ = 0 | μ = 20 | μ = 50 | μ = 60 |
|---|---|---|---|---|---|
| A580 | ATLAS | 0 (UL 1.29) | 0.077 ± 0.045 | 0.34 ± 0.24 | not run (user) |
| A580 | Ideal | 0 (UL 0.25) | 0.42 | 0.33 | — |
| Z0 | ATLAS | 0.34 ± 0.12 | 27.0 ± 2.7 | 69.2 ± 4.4 | 74.6 ± 4.6 |
| Z0 | Ideal | 0.25 | 9.2 | 16.4 | 16.7 |
| Z1160 | ATLAS | 0 (UL 1.29) | 0 | 0 | 0 |
| Z1160 | Ideal | 0 (UL 0.25) | 0 | 0 | 0.08 |

**What the background is made of (2026-11-17, `compare/X10_pileup_completion.py`, `tables/X10_pileup_completion.csv`).** The conversion pair supplies the plane, and pile-up supplies the missing hits.
- **A580.** None of the passing photons passes at μ = 0.
  - ATLAS: all passing photons (3 at μ = 20; 5 rows / 4 photons at μ = 50) are "near-misses" at μ = 0. That means a plane with Δw < 1 cm and Δs < 0.01 cm, but only 14 hits on 8 stations, while the multiplicity cut needs 15 (7 stations with 2 hits). At μ = 20/50 the winning plane has 13–14 conversion hits plus 1–2 pile-up hits.
  - Ideal: 5 of 5 (μ = 20) and 3 of 4 (μ = 50) are near-misses at μ = 0. All have 1–2 pile-up hits in the plane.
- **Z0.** At μ = 50, 679 of 687 passing photons are near-misses at μ = 0, 7 already pass at μ = 0, and 685 have at least one pile-up hit in the winning plane.
- **Completion probability per near-miss** (one pile-up overlay each):

  | setting | near-misses at μ = 0 | μ = 20 | μ = 50 |
  |---|---|---|---|
  | ATLAS A580 | 470 | 3/470 = 0.6% | 5/470 = 1.1% |
  | ATLAS Z0 | 20 046 | 1.8% | 3.4% |
  | Ideal A580 | 122 | 4.1% | 2.5% |

- **Why only 215 of about 690 photons pass in both pool runs.** Which near-miss gets completed depends on where the pile-up hits fall, so it changes with the pool. The photon is still needed, because it provides the coplanar pair.
- **Consequence.** The background is (near-miss two-track objects per triggered event) × (completion probability by pile-up), plus planes made from pile-up alone.
  - Any MET-triggered event (about 10⁷ at 332 fb⁻¹: Z(νν̄)+jets, W+jets, Zγ) can contribute, not only Zγ conversions. Examples are π⁰/η conversions, Dalitz pairs and K_S decays.
  - The pile-up-only rate in the ATLAS geometry is not measured yet. The only measurement is Ideal Z1160: 0 of 5 000 events.
  - The numbers in the table above are therefore the Zγ part only. Below one event in total requires the per-event rate to be below about 10⁻⁷. The plan is in `backgrounds/PILEUP_FACTORISATION_PLAN.md`.

**Method.** Exclusion: 95% CL_s with n_obs = round(b). Discovery: max(5, Asimov Z = 5), using the central b. The reach tables for both geometries and both variants (central b; UL as systematic) are in `tables/X08_reach_with_background.csv` and in the headline section above.

**Pool test (2026-11-17, `compare/X09_pool_test.py`, `tables/X09_pool_test_by_region.csv`).** ATLAS Z0 at μ = 50 was rerun on the server with a new 20k minimum-bias pool (seed 20261117). Photons, per-photon seeds and conversion points were the same as in production (laptop, pool seed 20260916). Errors on the difference are paired, photon by photon.

| region | passing photons, production → test | N production | N test | difference (paired) |
|---|---|---|---|---|
| beam pipe | 517 → 527 | 17.6 ± 0.8 | 18.3 ± 0.9 | +0.7 ± 0.9 (0.7σ) |
| IBL (+ SCT disk 6 inner) | 162 → 159 | 47.3 ± 4.0 | 50.1 ± 4.3 | +2.8 ± 5.6 (0.5σ) |
| Pixel B0 (+ SCT disk 7 middle) | 8 → 14 | 4.2 ± 1.6 | 8.9 ± 2.5 | +4.7 ± 3.0 (1.6σ) |
| **total** | **687 → 700** | **69.2 ± 4.4** | **77.3 ± 5.1** | **+8.1 ± 6.5 (1.3σ)** |

- Passing photons change by only 2%, but N changes by 12%. Two things cause this:
  - Pixel B0 has the largest conversion probability per photon (mean p_conv 0.06–0.08), and its passing photons go from 8 to 14. This gives 4.7 of the 8.1 events.
  - In the IBL region, fewer photons pass (159 vs 162), but the passing photons carry larger weights (mean p_conv 0.037 vs 0.034). This gives +2.8 events.
- Only 215 of the about 690 passing photons pass in both runs. At μ = 50, whether a given photon passes is decided mainly by the pile-up overlay, not by the photon. The paired error (6.5) is therefore almost the unpaired one (6.7), and the test cannot separate a pool effect from MC statistics.
- The test also changes the machine (laptop vs server, §9). The difference therefore contains both the pool and the machine floating point.
- **Result.** The difference is consistent with statistics (1.3σ), so the 20k pool (each event reused about 23 times at μ = 50) is adequate, and no 125k pool was run. As a conservative choice, the observed difference is kept as a **pool systematic of about 12% on the Z0 background at μ = 50**. The background-aware reach tables do not yet include it.
- **Server pool.** The server's default pool, regenerated with seed 20260916, has sha256 `94e81e1f…`, not the laptop's `52b465f5…`. It is a different but statistically equivalent pool (same seed and code, machine floating point in Pythia). Server background runs that use the default pool therefore use a different pool from the laptop production runs. Exact equality would need the laptop pool copied (`~/minbias_pool_20000_13p6TeV.csv.gz`).

**History.** Before 2026-11-17 the UL was used as b when no photon passed. That made the ATLAS A580 reach at μ = 0 lower than at μ = 20, which is unphysical; it is now only the systematic variant.

## 8. Integration failures

The integrator cannot reach its minimum number of steps per period ("MIN_STEPS_PER_PERIOD not reached"). These events count as not fiducial, as in 06 S2.

| | S2 · Run 3 · ATLAS | S1 · Run 3 · Ideal (2k, 06 S2) |
|---|---|---|
| Λ ≤ 10 keV | about 0.8% | about 1% |
| Λ = 15 / 20 / 25 keV (EW) | 3.2 / 8.7 / 20.4% | 3.4 / 9.9 / 22.2% |
| Λ = 15 / 20 / 25 keV (colored) | 1.7 / 5.6 / 15.7% | 1.4 / 3.9 / 15.0% |
| all Λ | 2.60% | 2.85% |

Source: `tables/R02_integration_failures.csv`.

## 9. Numerical reproducibility (laptop vs server): systematic uncertainty

The same events, seeds and code were run on the laptop (stopped on 2026-11-17 after low and mid, and part of high_a) and on the server (`compare/X01*.py`).

**Row level** (82 155 event–Λ rows, `tables/X01b_difference_classes.csv`):

| class | rows |
|---|---|
| identical | 50 045 |
| floats only (mostly ~1e-11 relative) | 30 000 |
| a discrete field flips | 2 110 (2.6%) |

- The flips are fid in 526 rows, Z0 selection in 479, A580 in 185 and Z1160 in 134.
- They have no direction. Net (laptop − server): +12, +31, −1 and −8. For Z0, +31 of 479 flips is 1.4σ.

**Cause.**
- Each machine reproduces itself bit for bit: 8 events rerun on the laptop gave 56/56 rows identical to the earlier laptop rows, and 13/56 identical to the server rows.
- The difference therefore comes from floating-point arithmetic, which differs between machines (CPU instructions and library versions). The quirk integration is sensitive to it. It is not a code or seed difference.

**Effect on the result** (`tables/X01c_*.csv`; both grids built with R01 on Λ = 0.1–10 keV):
- k differs in 253 of 468 grid cells, by at most 8 events, which is ≤ 0.71 √k.
- The reach differs by 0–2 GeV in 11 of 12 cases.
- In one case the difference is 4 GeV: EW Z1160 discovery, where the best Λ moves between 4 and 5 keV.
- **Systematic: ≤ 4 GeV on m_max.** This is at most about 25% of the Wilson half-range (17 GeV in that case).

## 10. Open points

1. **Backgrounds not simulated:** Z(νν̄)+jets (47× larger σ) and W(ℓν)+jets, plus the sources B1–B7 of `BACKGROUND_CANDIDATES.md`. A plan is in `backgrounds/ZJETS_PLAN.md`. **Pile-up as a background in its own right (priority):** passing photons are near-misses completed by pile-up hits (§7). The pile-up-only fake-plane rate and the completion probability must be measured to about 10⁻⁷ per triggered event; the plan is in `backgrounds/PILEUP_FACTORISATION_PLAN.md`.
2. **Top edge of the contour (Λ > 25 keV):** see §6 (b). Integration failures limit the high-Λ region.
3. **Background MC statistics:** A580 rests on 3–5 passing photons (errors 58–71%). The upper limit when none pass is 1.29 (ATLAS) / 0.25 (Ideal) events. 100k Zγ photons are planned (`backgrounds/SERVER_BACKGROUND_RUNS.md`). The pool test (§7) gives a conservative pool systematic of about 12% on the Z0 background at μ = 50 (+8.1 ± 6.5 events, 1.3σ); a 125k pool was not needed.
4. **Forward material:** M01 matches R12 at low |η| (20% conversion) but gives 38% at |η| ≈ 2.3, where R12 states up to about 65%. The end-cap background may be underestimated, most for Z0.
5. **Quirk material effects** (dE/dx, multiple scattering) are not in the integrator, for either geometry. A Highland estimate (`GEOMETRY_COMPARISON.md` §8.1, `tables/X07*`):
   - The RMS displacement over the 8 measurements is about 12–13 µm for the forward (ATLAS-only) events and 4–5 µm in the barrel (median, initial momentum).
   - The Δs cut survival is 93–96% and 97–99.6% respectively.
   - The reach changes by −4 to −9 GeV with the initial momentum, and by −11 to −32 GeV with the conservative turning-point momentum.
   - The ATLAS gain is unaffected in substance. A full treatment inside the integrator is still to do.
   - The background acceptance (C01) is the full ATLAS one, including the end-caps (§8.2 there).
6. **Not yet included** (README "to do"): module tilts and gaps, field map, SCT timing, hit efficiency and noise.

## 11. Tests

All pass; logs in `logs/`.

| Test | Purpose |
|---|---|
| T01 | geometry coverage against R3 |
| T02 | propagation |
| T03 | end-cap response and stations |
| T04 | exact speed-ups |
| T05 | 06 S2 background reproduced event by event |
| T06, T06e | SCT settings, C01 regression |
| T07 | 06 S2 signal reproduced |
| T08 | event_id seeds |
| T09 | reach code reproduces the S2 tables exactly |
| T10 | contour code reproduces the 06 contours exactly |
| T11 | the grid recounted from the raw server files: 630/630 rows (14 points) |

## 12. References

R1–R14 and MG are listed in `references/REFERENCES.md`, with the table or section each number comes from. Decisions D1–D6 are in `DECISIONS.md`.
