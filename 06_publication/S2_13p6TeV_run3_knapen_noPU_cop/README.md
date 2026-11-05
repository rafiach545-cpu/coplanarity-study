# Stage 2: 13.6 TeV (LHC Run 3), Knapen geometry, no pile-up, coplanarity

Publication plan (whiteboard, 2026-11-03), step 1b: the stage 1 analysis at the Run 3 energy. Started 2026-11-03.

## Energy and luminosity (references)

- **√s = 13.6 TeV**, 6.8 TeV per beam. Run 3 began with stable beams on 5 July 2022 ([ATLAS press statement](https://atlas-public.web.cern.ch/Updates/Press-Statement/LHC-Run3-Starts), [CMS](https://cms.cern/node/2106), [CERN Courier](https://cerncourier.com/a/run-3-physics-gets-under-way/)). Long Shutdown 3 is scheduled to start after the 2026 run.
- **ATLAS recorded, per year** (13.6 TeV pp, [ATLAS Data Quality page](https://twiki.cern.ch/twiki/bin/view/AtlasPublic/DataQualityResults); good for physics in brackets):

  | Year | Recorded (fb⁻¹) | Good for physics (fb⁻¹) |
  |---|---|---|
  | 2022 | 34 | 31 |
  | 2023 | 28.8 | 27.2 |
  | 2024 | 116 | 108 |
  | 2025 | 119 | 115 |
  | 2026 (partial, nominal + low μ) | 29.2 + 1.26 | 28.1 + 1.22 |

  - Sum ≈ 328 fb⁻¹ recorded, ≈ 311 fb⁻¹ good for physics.
  - The cumulative Run 3 totals appear only as plots on the [ATLAS Run 3 luminosity page](https://twiki.cern.ch/twiki/bin/view/AtlasPublic/LuminosityPublicResultsRun3) (r51, 2026-05-18). The user's figure of 332 fb⁻¹ recorded is consistent with these numbers, but it is not stated in text on either page.
- **CMS:** the [CMS luminosity page](https://twiki.cern.ch/twiki/bin/view/CMSPublic/LumiPublicResults) (r213, 2026-06-02) gives Run 3 numbers only as plots. The user's figure of 355 fb⁻¹ delivered could not be checked in text.
- **Luminosity used:**
  - Main: L = 300 fb⁻¹ (user's choice for Run 3, 2026-11-03).
  - Also given: L = 332 fb⁻¹ (ATLAS-like recorded) and 355 fb⁻¹ (CMS-like delivered).
  - N is linear in L, so changing L needs no new simulation.

## What changes relative to 13 TeV

- **Only the beam energy:** ebeam1 = ebeam2 = 6800 GeV. Everything else is the same as the validated 13 TeV Fig. 6 production (figure6_full_v1):
  - generation: MG5 3.7.3 process directories, the same cards (0 + 1 jet, MLM xqcut 30, nn23lo1, Pythia8 R-hadrons), 2000 events and the same seed per mass point;
  - extraction and trigger: pT(QQ̄) > 200 GeV, and for colored both quirk-hadrons charged;
  - propagation and selection: unchanged F6_02_grid.py, loaded as a module (numba integrator).
- **Mass points:** colored 600–2400 GeV (2400 is propagated too, because σ is larger at 13.6 TeV); EW 100–1000 GeV.
- **Λ bands:** low 0.1–0.7, mid 1–10 and high_a 15–25 keV, as in the reproduction.

## Scripts

| Step | Script | Output |
|---|---|---|
| 1 | `S2_01_generate.py` | `/home/rafia/hep_tools/S2_13p6TeV_runs/<tag>/`, `generation_statistics_13p6TeV.csv` |
| 2 | `S2_02_extract.py` | `inputs/<tag>_events.csv`, `inputs/counts.csv` |
| 3 | `S2_03_propagate.py` (one point, one band) | `logs/F6_<tag>[_<band>]_events.jsonl` |
| 4 | `S2_04_run_all.py` (all points and bands, memory watchdog) | as step 3 |
| 5 | `S2_05_reach.py` | `S2_N_grid_300fb.csv`, `S2_reach.csv`, `S2_fig_reach.png/.pdf` |
| 6 | `S2_06_zgamma_generate.py` (Zγj at 13.6 TeV, run card from the 13 TeV run_02 banner) | `inputs/zgamma_photons_13p6TeV.csv`, `inputs/zgamma_xsec_13p6TeV.txt` |
| 7 | `S2_07_minbias_pool.py` (20 000 minimum-bias events, seed 20260916, eCM 13.6 TeV) | `inputs/minbias_pool_20000_13p6TeV.csv` |
| 8 | `S2_08_background.py` (P10 / P17b / P8, unchanged, with 13.6 TeV photons and pool), `S2_08_chain.sh` | `logs/bkg_13p6TeV/<run>_mu<mu>/` |
| 9 | `S2_09_background_summary.py` | `S2_background_13p6TeV.csv`, `S2_reach_with_background.csv` |
| 10 | `S2_10_compare_13_vs_13p6.py` (factor by factor, kinematics, reach variants, bootstrap) | `S2_compare_*.csv`, `logs/S2_10_compare.log` |
| 11 | `S2_11_uncertainties.py` (statistical uncertainty budget, reach toys with all statistical sources, permutation test 13 vs 13.6 TeV) | `S2_unc_*.csv`, `logs/S2_11_uncertainties.log` |

## Checks

- **Propagation driver:** on 6 EW 800 GeV events of the 13 TeV inputs it reproduces the reproduction's checkpoints exactly (42 rows, 0 differences).
- **Generation environment (problem found and fixed, 2026-11-03):**
  - The 13 TeV objects were compiled with conda-forge gfortran 16.2 from the hep env.
  - Started without the hep env in PATH, MG5 recompiles the edited parts with Ubuntu gfortran 13.3. The mixed binary segfaults in madevent at both 13 and 13.6 TeV.
  - `S2_01_generate.py` therefore puts the hep env first in PATH.
  - The broken copies were deleted.
  - Check (passed): EW 800 GeV regenerated at 13 TeV with seed 9504 in a separate folder (`/home/rafia/hep_tools/S2_validation_13TeV_runs`, `logs/S2_01_validation_13TeV_EW800.log`) gives 1024 matched events and σ = 0.2341 ± 0.0052 fb, as in September. All 1,222,451 HepMC particle lines are identical; the file hash differs only in the header.

## Results (2026-11-03)

Propagation: all 13 points × 3 bands finished on the first attempt (`logs/S2_04_run_all.log`, PROPAGATION_EXIT=0). Zero background, 3 events = exclusion, 5 = discovery; ±1σ is the Wilson 68% band on k/n at 300 fb⁻¹.

| Channel | SCT | 13.6 TeV, 300 fb⁻¹ excl. / disc. (GeV) | excl. ±1σ | 332 fb⁻¹ excl. / disc. | 355 fb⁻¹ excl. / disc. | 13 TeV, 300 fb⁻¹ excl. / disc. |
|---|---|---|---|---|---|---|
| colored | Z1160 | 1445 / 1329 | 1299–1548 | 1468 / 1352 | 1483 / 1368 | 1497 / 1424 |
| colored | Z0 | 1764 / 1660 | 1717–1804 | 1785 / 1681 | 1798 / 1694 | 1702 / 1591 |
| EW | Z1160 | 563 / 456 | 459–622 | 589 / 465 | 602 / 475 | 524 / 473 |
| EW | Z0 | 795 / 732 | 775–816 | 809 / 743 | 819 / 751 | 792 / 701 |

- **Expected shift from σ alone:** the rise in σ (×1.3–1.4 for colored at 1.5–1.8 TeV, ×1.17 for EW at 800 GeV) moves the reach by roughly +60 GeV (colored) and +25 GeV (EW). Z0 shows this (colored +62 / +69 GeV).
- **Colored Z1160 is lower at 13.6 TeV (1445 vs 1497 GeV). This is statistical, not physical:**
  - Pooled over 900–2100 GeV and Λ = 2, 5, 10 keV, the signal-region fraction is 44/1011 = 4.4% at 13.6 TeV against 47/951 = 4.9% at 13 TeV, which is consistent.
  - The difference comes from single points, e.g. 1200 GeV, Λ = 5 keV: k = 2/85 against 5/70.
  - The 13 TeV value lies inside the 13.6 TeV ±1σ band.
- **Same pooling at Z0:** colored 229/1011 = 22.7% against 168/951 = 17.7%; EW 17.4% against 18.6%. The Λ points share the same events, so these counts are correlated and the difference should not be read as significant.
- **Luminosity:** going from 300 to 355 fb⁻¹ adds 20–40 GeV.
- **Larger samples needed:** with n ≈ 50–190 propagated events per point, the reach moves by tens of GeV with sample fluctuations. Larger samples near the contour (colored 1200–1800 GeV, EW 400–800 GeV) would make the 13 vs 13.6 TeV comparison sharper.

## Backgrounds at 13.6 TeV and the reach with pile-up (2026-11-04)

### Validation (13 TeV inputs regenerated with the new scripts)

- **Minimum-bias pool:** `S2_07_minbias_pool.py` at 13 TeV reproduces the first 300 events of the 13 TeV pool exactly (32,986 particles). The 13.6 TeV pool has 113.9 charged particles per event, against 112.8 at 13 TeV (+0.9%).
- **Overlay at μ = 0:** `S2_08_background.py P10/P17b 0 13TeV` gives 0/9139 (Z1160) and 1/9139 (Z0), the stage 1 μ = 0 numbers (`logs/bkg_13TeV/`).
- **Zγj regenerated at 13 TeV** (same cards, seed 27; `logs/S2_06_zgamma_13TeV_check.log`):
  - The sample is not bit-identical: the LHE events differ from the first event on (the process directory kept grids from later runs with other cuts).
  - It is statistically the same: σ = 0.2316 ± 0.0007 pb against 0.2311 pb, and 9149 against 9139 events after MET > 200 GeV. KS tests on pT(γ), MET, |η| and E give p = 0.46–0.93.

### Inputs

- **Zγj at 13.6 TeV:** σ = 0.2521 pb (13 TeV: 0.2311 pb, ×1.09). 9130 of 10 000 events pass MET > 200 GeV, so σ_γ = 0.2301 pb (13 TeV: 0.211 pb). Background normalisation: σ_γ × 1% = 2.30 fb.
- **μ values:** 0 (no pile-up), 20 (low), 50 and 60 (Run 3 range of the plan).

### Background (signal region, 300 fb⁻¹)

| Background | μ | plane / multiplicity / SR | N_bkg (300 fb⁻¹) | exclusion s (95% CLs) | discovery s |
|---|---|---|---|---|---|
| conversion + PU, σ_z = 1.16 mm | 0 | 1872 / 0 / 0 of 9130 | < 0.23 | 3.0 | 5 |
| | 20 | 1930 / 21 / 0 | < 0.23 | 3.0 | 5 |
| | 50 | 2114 / 54 / 0 | < 0.23 | 3.0 | 5 |
| | 60 | 2223 / 62 / 1 | 0.08 | 3.0 | 5 |
| conversion + PU, σ_z = 0 | 0 | 4073 / 3 / 3 | 0.23 | 3.0 | 5.3 |
| | 20 | 4082 / 165 / 110 | 8.3 | 7.3 | 18.2 |
| | 50 | 4195 / 334 / 196 | 14.8 | 9.6 | 23.1 |
| | 60 | 4236 / 368 / 200 | 15.1 | 9.4 | 23.3 |
| pile-up only, σ_z = 1.16 mm | 20 / 50 / 60 | 12 / 101 / 183 planes, SR 0 of 5000 each | prob. < 6×10⁻⁴ per event | — | — |

- **Thresholds:** exclusion is 95% CLs with n_obs = round(b), as in stage 1; for k = 0 it uses the 95% upper limit on b. Discovery is max(5, s at Asimov Z = 5) for the central b. Because n_obs is rounded, the exclusion threshold is not monotonic in b (9.6 at μ = 50, 9.4 at μ = 60).
- **σ_z = 1.16 mm (Knapen):**
  - The background is zero up to μ = 50.
  - At μ = 60 one event passes (event 6003). Its plane has 14 conversion hits and 1 pile-up hit; that one hit completes the 8-layer multiplicity. At μ = 20 and 50 the same event forms a plane but fails multiplicity.
  - 0.08 events at 300 fb⁻¹ does not change any threshold.
- **σ_z = 0:**
  - μ = 0 gives 3/9130 against 1/9139 at 13 TeV; these Poisson counts are compatible.
  - μ = 20 gives 110 against 115 at 13 TeV.
  - μ = 50 gives 196 against 146 at 13 TeV (about 2.7σ). The pool is only 0.9% busier, so this is not understood. As at 13 TeV, which events pass is set mainly by the random pile-up configuration.

### Reach with background (`S2_reach_with_background.csv`, m_max in GeV, 300 fb⁻¹; 332 / 355 fb⁻¹ in the CSV)

| Channel | SCT | Contour | μ = 0 | μ = 20 | μ = 50 | μ = 60 |
|---|---|---|---|---|---|---|
| colored | Z1160 | exclusion / discovery | 1445 / 1329 | 1445 / 1329 | 1445 / 1329 | 1445 / 1329 |
| colored | Z0 | exclusion / discovery | 1764 / 1647 | 1590 / 1446 | 1539 / 1416 | 1542 / 1414 |
| EW | Z1160 | exclusion / discovery | 563 / 456 | 563 / 456 | 563 / 456 | 563 / 456 |
| EW | Z0 | exclusion / discovery | 795 / 724 | 687 / 577 | 655 / 545 | 657 / 544 |

- **Knapen setting (σ_z = 1.16 mm):** pile-up up to μ = 60 does not change the 13.6 TeV reach.
- **σ_z = 0:** with pile-up, the reach drops by about 170–230 GeV (colored) and 110–180 GeV (EW). Most of the loss is already there at μ = 20, and the Z0 advantage over Z1160 shrinks to about 100 GeV (colored exclusion) and 90 GeV (EW).
- **Signal efficiencies:** they are taken without pile-up on the signal, as in the paper and in stage 1.

## Review points (2026-11-04)

### 1. Luminosity: 332 fb⁻¹ is the Run 3 number

- **Main:** 332 fb⁻¹ (ATLAS recorded, Run 3; see the references above).
- **Also given:** 300 fb⁻¹ (comparison with the paper and Knapen) and 355 fb⁻¹ (CMS delivered, in the CSVs).
- **No new simulation:** N scales as 332/300 = 1.107.

Reach without pile-up (`S2_reach.csv`), m_max in GeV with the ±1σ Wilson band:

| Channel | SCT | Contour | 13.6 TeV, **332 fb⁻¹** | 13.6 TeV, 300 fb⁻¹ | 13 TeV, 300 fb⁻¹ |
|---|---|---|---|---|---|
| colored | Z1160 | exclusion | **1468** (1324–1564) | 1445 (1299–1548) | 1497 (1438–1558) |
| colored | Z1160 | discovery | **1352** (1199–1478) | 1329 (1191–1457) | 1424 (1368–1482) |
| colored | Z0 | exclusion | **1785** (1738–1817) | 1764 (1717–1804) | 1702 (1651–1747) |
| colored | Z0 | discovery | **1681** (1635–1724) | 1660 (1616–1704) | 1591 (1538–1639) |
| EW | Z1160 | exclusion | **589** (467–633) | 563 (459–622) | 524 (482–567) |
| EW | Z1160 | discovery | **465** (425–557) | 456 (416–536) | 473 (440–514) |
| EW | Z0 | exclusion | **809** (788–831) | 795 (775–816) | 792 (766–815) |
| EW | Z0 | discovery | **743** (727–760) | 732 (715–748) | 701 (681–722) |

Reach with pile-up at 332 fb⁻¹ (`S2_reach_with_background.csv`), exclusion / discovery in GeV:

| Channel | SCT | μ = 0 | μ = 20 | μ = 50 | μ = 60 |
|---|---|---|---|---|---|
| colored | Z1160 | 1468 / 1352 | 1468 / 1352 | 1468 / 1352 | 1468 / 1352 |
| colored | Z0 | 1785 / 1661 | 1599 / 1453 | 1560 / 1423 | 1548 / 1422 |
| EW | Z1160 | 589 / 465 | 589 / 465 | 589 / 465 | 589 / 465 |
| EW | Z0 | 809 / 732 | 693 / 585 | 668 / 553 | 661 / 552 |

N_bkg (Z0) at 332 fb⁻¹: 0.25 / 9.2 / 16.4 / 16.7 events at μ = 0 / 20 / 50 / 60.

### 2. Colored, σ_z = 1.16 mm: lower reach at 13.6 TeV, checked factor by factor (`S2_10_compare_13_vs_13p6.py`)

**Benchmark (1800 GeV, 2 keV):**

| Factor | 13 TeV | 13.6 TeV | ratio | z |
|---|---|---|---|---|
| σ (fb) | 0.319 | 0.440 | 1.38 | — |
| ε_trig | 227/854 = 0.266 | 197/840 = 0.235 | 0.88 | −1.5 |
| f_ch | 75/227 = 0.330 | 66/197 = 0.335 | 1.01 | +0.1 |
| ε_fid | 20/75 = 0.267 | 18/66 = 0.273 | 1.02 | +0.1 |
| ε_reco, Z1160 | 3/20 = 0.150 | 0/18 = 0 | 0 | −1.7 |
| ε_reco, Z0 (same events) | 11/20 = 0.55 | 10/18 = 0.56 | 1.01 | +0.0 |

- **The only difference at the benchmark is ε_reco at σ_z = 1.16 mm:** 3 against 0 events.
  - On the same fiducial events, the Z0 selection gives 11/20 against 10/18.
  - So the quirk trajectories and hits behave the same at both energies; only the 1.16 mm SCT smearing, which passes few events, gives fewer passes.
- **Generation and trigger, all mass points:**
  - ε_trig at 13.6/13 TeV goes up and down with mass: z = −1.5, +0.6, +1.6, +2.4, −1.5, +1.1, +0.9 for colored 600–2400 GeV, and −0.6 to +2.5 for EW. There is no common shift.
  - f_ch agrees everywhere (|z| ≤ 1.6).
  - Quirk pT, |η|, β and pT(QQ̄) of the propagated events agree. Of 48 KS tests, one has p < 0.05 (p = 0.048, as expected by chance).
  - There is therefore no sign of a setup difference (PDF, matching, Pythia).
- **Where the Z1160 deficit sits:**
  - The fewer passes at 13.6 TeV are at 1200–2100 GeV, Λ = 2–5 keV (e.g. 1200 GeV, 4 keV: 7/70 against 2/85, z = −2.0).
  - At 600–900 GeV, 13.6 TeV has more passes (900 GeV, 2 keV: 0/66 against 5/68).

**Reach variants** (m_max in GeV; the 13 TeV column is at 300 fb⁻¹, the others at the given luminosity):

| Channel | SCT | Contour | L | 13 TeV | Expected: 13 TeV ε × 13.6 TeV σ ε_trig f_ch | 13.6 TeV | Pooled ε (both samples) |
|---|---|---|---|---|---|---|---|
| colored | Z1160 | exclusion | 332 | 1497 | 1562 | 1468 | 1510 |
| colored | Z1160 | discovery | 332 | 1424 | 1496 | 1352 | 1434 |
| colored | Z0 | exclusion | 332 | 1702 | 1773 | 1785 | 1778 |
| colored | Z0 | discovery | 332 | 1591 | 1676 | 1681 | 1678 |
| EW | Z1160 | exclusion | 332 | 524 | 559 | 589 | 565 |
| EW | Z1160 | discovery | 332 | 473 | 502 | 465 | 498 |
| EW | Z0 | exclusion | 332 | 792 | 855 | 809 | 831 |
| EW | Z0 | discovery | 332 | 701 | 769 | 743 | 754 |

**Bootstrap (500 replicas; events resampled per mass point, all Λ of an event together, both samples), Δ = 13.6 TeV − expected at 332 fb⁻¹:**

| Channel | SCT | Contour | Δ observed | σ(Δ) | Δ / σ | fraction with Δ ≥ 0 |
|---|---|---|---|---|---|---|
| colored | Z1160 | exclusion | −94 | 81 | −1.1 | 18% |
| colored | Z1160 | discovery | −144 | 83 | −1.7 | 10% |
| colored | Z0 | exclusion | +12 | 42 | +0.3 | 66% |
| colored | Z0 | discovery | +5 | 45 | +0.1 | 63% |
| EW | Z1160 | exclusion | +29 | 53 | +0.6 | 75% |
| EW | Z1160 | discovery | −38 | 56 | −0.7 | 37% |
| EW | Z0 | exclusion | −46 | 24 | −1.9 | 3% |
| EW | Z0 | discovery | −26 | 25 | −1.0 | 16% |

**Conclusion:**
- The colored σ_z = 1.16 mm deficit is a 1.1–1.7σ fluctuation of ε_reco. It comes from small counts (k = 0–7 per point) in the selection with the 1.16 mm SCT smearing.
- σ, ε_trig, f_ch, ε_fid and the kinematics show no setup difference, and the Z0 selection on the same events reproduces the expected σ gain exactly (+12 / +5 GeV).
- The deviations have both signs: across the eight comparisons, one is at 1.9σ (EW Z0 exclusion) and the colored Z1160 ones are at 1.1–1.7σ.
- **Best estimate** for colored σ_z = 1.16 mm at 13.6 TeV, 332 fb⁻¹, using the pooled efficiencies of both samples: about 1510 (exclusion) / 1430 (discovery) GeV. Larger samples at 1200–2100 GeV would settle it.

### 3. σ_z = 0 background at μ = 50: 146 (13 TeV) against 196 (13.6 TeV), mixed test

P17b at μ = 50 with every combination of photons and pile-up pool (`S2_08_background.py P17b 50 {13TeV|ph13_pu13p6|ph13p6_pu13|13p6TeV}`, `logs/S2_08_mix_test_mu50.log`, `logs/S2_08_check_13TeV_mu50.log`). Signal-region events out of 9139 (13 TeV photons) or 9130 (13.6 TeV photons):

| Photons | Pile-up 13 TeV | Pile-up 13.6 TeV |
|---|---|---|
| 13 TeV | 146 (original seed); **181** (pile-up seed 20261104) | 182 |
| 13.6 TeV | 198 | 196 |

- **Code check:** the first 10 chunks (1000 rows) of the original 13 TeV run are reproduced exactly by the current code.
- **Mean pile-up hits per event:** 8078 (13 TeV pool) against 8053 (13.6 TeV pool). The 13.6 TeV pile-up is not busier in the detector.
- **Different pile-up configurations select different events:**
  - Changing photons or pool keeps only 50–68 of the ~190 passing events.
  - The runs are therefore nearly independent samples of the same rate.
- **The 146 is a low fluctuation:**
  - The same 13 TeV inputs with another pile-up seed give 181.
  - The five runs (146, 181, 182, 198, 196) scatter around 181 ± 9, i.e. about 2.0% of conversions.
  - There is no energy dependence: neither the photons nor the pool shift the count in a consistent direction.
- **Consequence for the reach:**
  - The 13.6 TeV numbers (196/9130) need no change.
  - The 13 TeV stage 1 value at μ = 50 (146/9139, 4.7 events at 139 fb⁻¹) is on the low side; with 181/9139 it would be 5.8 events.
  - The σ_z = 0 conclusions of stage 1 do not change: the background is a few events and needs ~6–7 signal events for exclusion.
  - The stage 1 tables are left as they are.

### 4. Statistical uncertainties (`S2_11_uncertainties.py`, 2026-11-05 seed)

- Budget per mass point (best Λ): k/n dominates (27–97% on N at σ_z = 1.16 mm, 14–43% at σ_z = 0); σ, ε_trig, f_ch together 1–15%.
- Reach, 1000 toys (events bootstrapped; σ Gaussian; ε_trig, f_ch binomial; background count binomial): 13.6 TeV, 332 fb⁻¹ colored σ_z = 1.16 mm exclusion 1468 +80/−65 GeV, σ_z = 0 1785 +36/−33 GeV. Central values reproduce S1/S2 exactly.
- Permutation test of the selection efficiency (pass fraction over 15 Λ, 5000 relabellings per mass point): colored σ_z = 1.16 mm χ² = 9.6/6, p = 0.13, mean pull −1.06 (p = 0.29); the four channel tests p = 0.13–0.73; global p (4 tests) 0.43. The colored deficit is a fluctuation.
- ε_trig scatters more than its Wilson errors (colored χ² = 15.0/7, p = 0.037, both signs; EW mean pull +2.2, p = 0.03). Each energy uses its own ε_trig, so N is not biased; to recheck with larger samples.
