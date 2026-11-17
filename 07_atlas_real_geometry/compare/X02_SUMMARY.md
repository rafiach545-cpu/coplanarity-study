# Ideal vs ATLAS geometry on the 10k samples (2026-11-17)

This document compares the server runs (pulled in commit aa9b62a) of the ideal and ATLAS geometries on the same 10k-generated events. All values below come from the files in `tables/`; scripts and logs are listed at the end.

## 1. Laptop vs server, ATLAS geometry, row by row

The laptop G02 propagation was stopped on 2026-11-17 at 11:14. Before it stopped, it had finished:

- all low and mid bands;
- high_a for EW 100–600 GeV;
- 314 of 891 events of EW 800 GeV high_a.

Comparison: `compare/X01_laptop_vs_server_atlas.py` and `X01b_difference_classes.py`; results in `tables/X01*.csv`.

- **The results are not identical.** Of 82 155 (event, Λ) rows:
  - 50 045 are identical;
  - 30 000 differ only in floating-point values. Most differences are about 1e-11 relative; in chaotic cases the coplanarity distances Δs and Δw can differ much more;
  - 2 110 (2.6%) differ in a discrete field. The fiducial flag (`fid`) flips in 526 rows, `Z0_final` in 479, `A580_final` in 185 and `Z1160_final` in 134.
- **The flips have no direction.** The net changes (laptop minus server) are +12 for fid, +31 for Z0, −1 for A580 and −8 for Z1160. All are consistent with zero: for Z0, +31 of 479 flips is 1.4σ.
- **The cause is the machine, not the code or the seeds.**
  - Test: 8 events with flips (EW 100 GeV, mid) were rerun on the laptop with the same inputs.
  - Laptop rerun against the earlier laptop output: 56/56 rows bit-identical.
  - Laptop rerun against the server output: only 13/56 identical.
  - So each machine reproduces itself exactly. The difference comes from floating-point arithmetic, which differs between machines (CPU instructions and numba/numpy/libm versions). The quirk integration amplifies these small differences.
- **Effect on the result** (`compare/X01c_reach_laptop_vs_server.py`, both grids on Λ = 0.1–10 keV; corrected 2026-11-17, an earlier version compared only two rows and said "within 1 GeV"):
  - k differs in 253 of 468 cells, by at most 8 events (≤ 0.71 √k);
  - the reach differs by 0–2 GeV in 11 of 12 cases and by 4 GeV for EW Z1160 discovery, where the best Λ moves between 4 and 5 keV;
  - systematic: ≤ 4 GeV on m_max.
- The laptop runs were moved to `signal/runs/atlas_large_laptop_INTERIM_2026-11-17` and are superseded.

## 2. N and reach, 332 fb⁻¹

**Method.** N = L σ ε_trig f_ch k/n, using the Stage 2 method unchanged (`reach/R01_reach_07.py`, T09).

- For colored, ε_trig f_ch = (triggered and both charged) / matched.
- k/n has a Wilson 68% band.
- All 585 grid rows of both setups are computed, for Λ = 0.1–25 keV.

**Tables:**
- `tables/X02_N_grid_{ideal,atlas}_300fb.csv`: N at 300 fb⁻¹, the R01 reference luminosity;
- `tables/X02_reach_332fb.csv`: the reach;
- `tables/X02_contours_332fb.csv`: the contour lines.

**Reach at 332 fb⁻¹.** Each cell gives exclusion / discovery in GeV, with the ±1σ Wilson range in brackets.

| channel | SCT | ideal (10k) | ATLAS (10k) | Stage 2 (2k, barrel) |
|---|---|---|---|---|
| colored | Z0 | 1734 [1717, 1752] / 1659 | 1871 [1857, 1885] / 1777 | 1785 [1738, –] / 1681 |
| colored | A580 | 1590 [1564, 1618] / 1515 | 1697 [1674, 1719] / 1618 | — |
| colored | Z1160 | 1497 / 1430 | 1612 [1584, 1640] / 1529 | 1468 / 1352 |
| EW | Z0 | 826 [813, 838] / 744 | 994 [988, 999] / 900 | 809 / 743 |
| EW | A580 | 631 [607, 653] / 560 | 767 [754, 781] / 681 | — |
| EW | Z1160 | 565 / 500 | 671 [651, 690] / 588 | 589 / 465 |

- Ideal (10k) agrees with Stage 2 (2k) within the Stage 2 Wilson bands. This is the expected check, since ideal uses the same geometry as Stage 2.
- ATLAS is higher than ideal by about 100–140 GeV (colored) and about 90–170 GeV (EW).

Figure: `compare/FIGURES_X02/X02_contours_ideal_vs_atlas_332fb/` (ROOT; pdf, png, root, C, caption, provenance).

## 3. Paired ideal vs ATLAS comparison (McNemar)

Tables: `tables/X02_mcnemar_per_point.csv` (per mass and Λ) and `tables/X02_mcnemar_per_lambda.csv` (summed over the masses of a channel).

The test compares the same events in both geometries, one pair per event:

- **b** = events that pass in ideal only;
- **c** = events that pass in ATLAS only.

The test is an exact binomial test on b and c, with the Holm correction applied within each quantity (195 tests).

- **b = 0 in every test**, for fid and for all three selections. Every event selected in ideal is also selected in ATLAS. For the 9 489 ideal-selected Z0 rows, Δs and Δw are bit-identical in ATLAS, and none of their planes uses an end-cap element.
  - **Why b = 0:** the barrel radii of the ideal geometry are the ATLAS radii; heavy quirks do not feel the material; the seeds are the same. Therefore ATLAS = ideal + extra events whose planes use end-cap stations.
- **Significant differences after the Holm correction:**
  - fid: 195 of 195 tests;
  - Z0_final: 119;
  - A580_final: 71;
  - Z1160_final: 46.
  - In every one of them ATLAS is higher.
- **Tests that are not significant** are at the edges, where k is small: Λ ≤ 0.3 keV and Λ = 25 keV, the heaviest points, Z1160.
- **Summed per Λ:** k_ATLAS / k_ideal ≈ 1.7–2.4 for Λ between 1 and 15 keV (Z0 EW: 2.1–2.4). See the column `ratio_k_atlas_over_ideal`.

## 4. Where the contours cross between grid points

Tables:
- `tables/X02_crossings_mass.csv`: one row per Λ and per crossing in mass;
- `tables/X02_crossings_lambda.csv`: one row per mass and per crossing in Λ.

Each row gives:
- the mass interval and N at both ends;
- the log-linear crossing, which is the one the reach uses;
- a 3-point quadratic crossing, as a check of the interpolation;
- the crossings of the Wilson band ends.

The table below gives, for each maximum reach, the grid interval and the difference between the quadratic and log-linear crossings.

| setup | channel / SCT | exclusion: interval, N at ends, quadratic − log-linear | discovery: interval, quadratic − log-linear |
|---|---|---|---|
| ATLAS | colored Z0 | 1800–2100, 4.28 → 0.95, −7.9 GeV | 1500–1800, +0.6 |
| ATLAS | colored A580 | 1500–1800, 9.48 → 1.64, −1.1 | 1500–1800, +7.8 |
| ATLAS | colored Z1160 | 1500–1800, 5.86 → 0.97, −3.1 | 1500–1800, +2.0 |
| ATLAS | EW Z0 | 800–1000, 8.59 → **2.90**, −0.8 | 800–1000, −5.7 |
| ATLAS | EW A580 | 600–800, 8.03 → 2.48, −3.6 | 600–800, −5.7 |
| ATLAS | EW Z1160 | 600–800, 4.59 → 1.39, −3.6 | 400–600, −6.5 |
| ideal | colored Z0 / A580 / Z1160 | 1500–1800 / 1500–1800 / 1200–1500, ≤ 1.3 | ≤ 7.3 |
| ideal | EW Z0 / A580 / Z1160 | 800–1000 / 600–800 / 400–600, −3.7 / −5.0 / −13.9 | ≤ 4.7 |

**Conclusions for the grid:**

1. **At the maximum reach, finer mass points are not needed.** The two interpolations differ by at most 8 GeV for ATLAS and 14 GeV for ideal. The full Wilson ±1σ ranges (hi − lo) are 11–56 GeV for ATLAS and 25–69 GeV for ideal. In every case the difference is smaller than the Wilson half-range, except EW Z0 ATLAS discovery, where −5.7 GeV is about equal to the half-range of 5.5 GeV.
2. **EW needs a point above 1000 GeV.** For ATLAS Z0, N at 1000 GeV is 2.90 (Wilson high value 2.98, at Λ = 4 keV), just below 3. The exclusion reach of 994 GeV therefore sits at the edge of the grid. At 355 fb⁻¹, or with a small change, it would leave the grid. A point at EW 1200 GeV (or 1100 GeV) is recommended.
3. **On the flanks of the contours** (low Λ ≤ 1 keV and high Λ ≥ 20 keV), the two interpolations differ by up to 44–55 GeV, in 18 of 276 crossings, with 200–300 GeV spacing between points. This affects the shape of the contour lines, not m_max. If the shape matters for the paper, these regions would need intermediate points:
   - colored 1050 and 1350 GeV;
   - EW 300 GeV;
   - a Λ point between 0.5 and 1 keV already exists (0.7 keV).

## Scripts and logs

- `compare/X01_laptop_vs_server_atlas.py`, `compare/X01b_difference_classes.py`; logs in `logs/X01*.log`
- `compare/X02_ideal_vs_atlas.py`; log `logs/X02_ideal_vs_atlas.log`
- `compare/make_figures_X02.py` (ROOT 6.40)
- The laptop rerun used for the reproducibility test is in the scratchpad only. It is not needed for the results.
