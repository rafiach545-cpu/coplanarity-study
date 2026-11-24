# Athena string-model systematic, Stage 1 · Run 2 · Ideal (13 TeV, 8 layers, no material)

**LOW STATISTICS** (pilot: the G07 impact subset; 20–48 fiducial events per point). Not for the final systematic; see the planned run (G13).

Same events, vertices and SCT draws. Nominal: Eq. 3 (DOP853, rtol 1e-10). Variation: Athena string vectors (Geant4 QuirkPheno_fix, maxBoost 0.01; maxBoost 0.001 gives 0 flips).
ε = k / N_fid with the Wilson 68 % interval. Flips: events that pass the SR with Athena and fail with Eq. 3 (+), and the reverse (−).

| Sample | Λ (keV) | σ_z (SCT) | N_fid | ε, Eq. 3 | ε, Athena | Flips (+/−) | ε_Athena / ε_Eq.3 |
|---|---|---|---|---|---|---|---|
| colored, 1800 GeV | 2 | 1160 µm | 20 | 0.150 [0.087, 0.246] | 0.150 [0.087, 0.246] | +0 / −0 | 1.00 |
| colored, 1800 GeV | 2 | 580 µm | 20 | 0.200 [0.126, 0.303] | 0.200 [0.126, 0.303] | +0 / −0 | 1.00 |
| colored, 1800 GeV | 4 | 1160 µm | 20 | 0.150 [0.087, 0.246] | 0.150 [0.087, 0.246] | +0 / −0 | 1.00 |
| colored, 1800 GeV | 4 | 580 µm | 20 | 0.250 [0.167, 0.357] | 0.250 [0.167, 0.357] | +0 / −0 | 1.00 |
| colored, 1800 GeV | 7 | 1160 µm | 20 | 0.150 [0.087, 0.246] | 0.150 [0.087, 0.246] | +0 / −0 | 1.00 |
| colored, 1800 GeV | 7 | 580 µm | 20 | 0.300 [0.209, 0.410] | 0.350 [0.253, 0.461] | +1 / −0 | 1.17 |
| colored, 1800 GeV | 10 | 1160 µm | 20 | 0.200 [0.126, 0.303] | 0.200 [0.126, 0.303] | +0 / −0 | 1.00 |
| colored, 1800 GeV | 10 | 580 µm | 20 | 0.300 [0.209, 0.410] | 0.300 [0.209, 0.410] | +0 / −0 | 1.00 |
| EW, 800 GeV | 2 | 1160 µm | 48 | 0.146 [0.102, 0.204] | 0.146 [0.102, 0.204] | +0 / −0 | 1.00 |
| EW, 800 GeV | 2 | 580 µm | 48 | 0.146 [0.102, 0.204] | 0.146 [0.102, 0.204] | +0 / −0 | 1.00 |
| EW, 800 GeV | 4 | 1160 µm | 48 | 0.146 [0.102, 0.204] | 0.146 [0.102, 0.204] | +0 / −0 | 1.00 |
| EW, 800 GeV | 4 | 580 µm | 48 | 0.188 [0.138, 0.250] | 0.250 [0.193, 0.317] | +3 / −0 | 1.33 |
| EW, 800 GeV | 7 | 1160 µm | 48 | 0.125 [0.085, 0.181] | 0.146 [0.102, 0.204] | +1 / −0 | 1.17 |
| EW, 800 GeV | 7 | 580 µm | 48 | 0.167 [0.120, 0.227] | 0.208 [0.156, 0.273] | +2 / −0 | 1.25 |
| EW, 800 GeV | 10 | 1160 µm | 48 | 0.104 [0.068, 0.157] | 0.167 [0.120, 0.227] | +4 / −1 | 1.60 |
| EW, 800 GeV | 10 | 580 µm | 48 | 0.167 [0.120, 0.227] | 0.208 [0.156, 0.273] | +4 / −2 | 1.25 |
| EW, 600 GeV | 4 | 1160 µm | 37 | 0.108 [0.067, 0.170] | 0.108 [0.067, 0.170] | +0 / −0 | 1.00 |
| EW, 600 GeV | 4 | 580 µm | 37 | 0.135 [0.088, 0.201] | 0.135 [0.088, 0.201] | +0 / −0 | 1.00 |
| EW, 600 GeV | 5 | 1160 µm | 37 | 0.081 [0.046, 0.138] | 0.054 [0.027, 0.104] | +0 / −1 | 0.67 |
| EW, 600 GeV | 5 | 580 µm | 37 | 0.135 [0.088, 0.201] | 0.135 [0.088, 0.201] | +1 / −1 | 1.00 |

Fiducial decisions: identical in every point (0 flips). Sum over all points: +16 / −5.

Source: `out_G01/G11_table.csv` (G11_athena_impact.py, G11_table.py, 2026-11-24).
