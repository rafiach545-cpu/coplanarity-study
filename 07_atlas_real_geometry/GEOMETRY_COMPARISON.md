# Detector geometry: Stage 1 (Ideal) vs Stage 2 (ATLAS)

**Date:** 2026-11-17.

**Sources of the numbers.** Every number below is read from the objects the simulation uses:
- `sim/detsim07.build("stage2")` for the Ideal geometry and `sim/detsim07.build("atlas")` for the ATLAS geometry;
- `geometry/atlas_run2_id_geometry.csv` and `geometry/atlas_run2_id_material.csv`;
- `tables/X06_*.csv`, written by `compare/X06_geometry_comparison.py`.

Reference IDs (R1–R14) are those of `references/REFERENCES.md`. Each quote was checked against the saved reference text in `references/text/`.

## 1. Where the two geometries come from

**Stage 0 and Stage 1 · Ideal: 8 barrel layers, no end-caps.**

- **Structure, from Knapen et al. (R10, arXiv:1708.02243).** The paper says: *"For simplicity, we assume a detector geometry of 8 layers of detector, following the ATLAS pixel layers and SCT"*. The paper gives no numerical radii.
  - Its detector simulation (Ref. [34] of R10 = R11, arXiv:1612.00850, App. A) takes *"the resolution and geometry of each component from the ATLAS technical design report"*. R11 also gives no numbers.
- **Radii, from ATLAS documentation.** Knapen et al. define the 8-layer Pixel+SCT structure; the numerical layer radii used in our simplified cylindrical implementation are taken from ATLAS detector documentation:
  - R1 = ATLAS, *Alignment of the ATLAS Inner Detector in Run-2*, arXiv:2007.07624, Table 1: IBL 33.25 mm; pixel 50.5, 88.5, 122.5 mm; SCT 299, 371, 443, 514 mm.
  - R2 = ATLAS IBL Collaboration, *Production and Integration of the ATLAS Insertable B-Layer*, JINST 13 (2018) T05008, arXiv:1803.00844: IBL active |z| = 330.15 mm.
  - R3 = ATLAS, JINST 3 (2008) S08003 ch. 4: pixel active length 801 mm; SCT barrel active length 1498 mm.
- **Beam pipe.** *"The inner radius was reduced from 29 mm to 23.5 mm"* (R2, Sec. on the beam pipe), to make room for the IBL. The Run-2 beam pipe is a 0.8 mm beryllium pipe with inner radius 23.5 mm (R6, arXiv:1707.02826, Sec. 2).
- **IBL radius conflict.** R2 gives a sensor-centre radius of 33.5 mm; R1 gives 33.25 mm. We use 33.25 mm in both stages.

**Stage 2 · ATLAS: the same 8 barrel layers, plus the end-caps.**

| Part | Elements | Positions | Source |
|---|---|---|---|
| Pixel disks | 3 per side | \|z\| = 495, 580, 650 mm; r = 88.8–149.6 mm | R1 Table 1; R3 Table 4.3 |
| SCT end-caps | 9 disks per side, each made of rings (outer, middle, inner): 22 ring surfaces per side | disk \|z\| = 853.8–2720.2 mm; ring radii; ±15.25 mm ring displacement | R3 Tables 4.6 and the SCT module table |
| Material | per element | — | R2, R3, R6, PDG (§4) |

In total the ATLAS geometry has 58 surfaces: 8 barrel, 6 pixel disk, and 44 SCT ring surfaces.

## 2. Barrel layers: identical in both stages

| Layer | Detector | r (cm) | half-length \|z\| (cm) | Pixel pitch r-φ × z (µm) | Straight-line \|η\| coverage at z0 = 0 | at z0 = +4.5 cm / −4.5 cm |
|---|---|---|---|---|---|---|
| 1 (IBL) | pixel | 3.325 | 33.015 | 50 × 250 | 0 – 2.99 | 2.85 / 3.12 |
| 2 (B-layer) | pixel | 5.05 | 40.05 | 50 × 400 | 0 – 2.77 | 2.65 / 2.87 |
| 3 | pixel | 8.85 | 40.05 | 50 × 400 | 0 – 2.22 | 2.10 / 2.32 |
| 4 | pixel | 12.25 | 40.05 | 50 × 400 | 0 – 1.90 | 1.79 / 2.00 |
| 5 | SCT | 29.9 | 74.9 | strips (80 µm, 40 mrad stereo) | 0 – 1.65 | 1.59 / 1.70 |
| 6 | SCT | 37.1 | 74.9 | strips | 0 – 1.45 | 1.40 / 1.51 |
| 7 | SCT | 44.3 | 74.9 | strips | 0 – 1.30 | 1.24 / 1.35 |
| 8 | SCT | 51.4 | 74.9 | strips | 0 – 1.17 | 1.12 / 1.22 |

- z0 is the vertex position along the beam. The beam spot has σ_z = 4.5 cm.
- Coverage is |η| < asinh((half-length ∓ z0)/r) for a straight line from (0, 0, z0).
- The radii, half-lengths and pitches are bit-identical in both stages (§1 of `compare/X02_SUMMARY.md`: the Δs and Δw of every ideal-selected event are identical in ATLAS).

## 3. End-cap elements: ATLAS only

The A side (+z) is listed; the C side (−z) is its mirror image.

| Element | \|z\| (cm) | r range (cm) | Straight-line \|η\| range at z0 = 0 |
|---|---|---|---|
| Pixel disk 1 | 49.5 | 8.88 – 14.96 | 1.91 – 2.42 |
| Pixel disk 2 | 58.0 | 8.88 – 14.96 | 2.06 – 2.58 |
| Pixel disk 3 | 65.0 | 8.88 – 14.96 | 2.18 – 2.69 |
| SCT disk 1: outer / middle | 83.86 / 86.91 | 43.88–56.00 / 33.76–45.53 | 1.19–1.40 / 1.40–1.67 |
| SCT disk 2: outer / middle / inner | 91.88 / 94.93 / 91.88 | 43.88–56.00 / 33.76–45.53 / 27.50–33.41 | 1.27–1.49 / 1.48–1.76 / 1.74–1.92 |
| SCT disk 3: o / m / i | 107.63 / 110.68 / 107.63 | as disk 2 | 1.41–1.63 / 1.62–1.90 / 1.89–2.07 |
| SCT disk 4: o / m / i | 128.47 / 131.52 / 128.47 | as disk 2 | 1.57–1.80 / 1.78–2.07 / 2.06–2.25 |
| SCT disk 5: o / m / i | 138.45 / 141.50 / 138.45 | as disk 2 | 1.64–1.87 / 1.85–2.14 / 2.13–2.32 |
| SCT disk 6: o / m / i | 175.62 / 178.67 / 175.62 | as disk 2 | 1.86–2.10 / 2.08–2.37 / 2.36–2.55 |
| SCT disk 7: o / m | 210.00 / 213.05 | 43.88–56.00 / 33.76–45.53 | 2.03–2.27 / 2.25–2.54 |
| SCT disk 8: o / short-middle | 248.98 / 252.03 | 43.88–56.00 / 40.28–45.53 | 2.20–2.44 / 2.41–2.53 |
| SCT disk 9: outer | 273.55 | 43.88–56.00 | 2.29–2.53 |

Values at z0 = ±4.5 cm are in `tables/X06_geometry_elements.csv`.

## 4. Resolution and material

**Resolution.** These are the same in both stages wherever the element exists.

| Quantity | Stage 1 · Ideal | Stage 2 · ATLAS |
|---|---|---|
| Pixel barrel hit | quantised to the pitch: 50 × 250 µm (IBL), 50 × 400 µm. σ = pitch/√12 = 14 × 72 µm and 14 × 115 µm (R10, R3) | same |
| SCT barrel r-φ | 34 µm (2 × 17 µm intrinsic, R10) | 34 µm, or 17 µm in the A580 setting (R3 Table 4.1) |
| SCT barrel z | 0 (Z0) or 1.16 mm (Z1160) | 0 (Z0), 1.16 mm (Z1160) or 580 µm (A580) |
| Pixel disk hit | — | quantised: 50 µm r-φ at the disk's mean radius × 400 µm in R, i.e. σ_R = 115 µm |
| SCT disk (rings) | — | r-φ as the barrel (34 / 17 µm); the coarse coordinate is **R**, with σ = 0 / 1.16 mm / 580 µm; z = the ring's \|z\| |
| Timing | every hit t < 25 ns | same |
| Magnetic field | uniform 2 T | uniform 2 T (R4: 1.998 T at the IP, ~1.8 T at z = 1.7 m; the field map is not used yet) |

**Material.** Values are x/X0 at normal incidence.

| Element | Stage 1 · Ideal | Stage 2 · ATLAS |
|---|---|---|
| Beam pipe | 0.19% (Ref. [27], 2009 Run-1 figure, digitised). The γ conversion probability is a flat 1% at r = 2.35 cm | 0.227%: Be wall only, 0.8 mm / X0(Be) = 35.28 cm (R6, R7b), a lower bound. Variants: 0.45% (Run-1 pipe, R3) and ×2 |
| IBL | 3.73% (inferred: the pixel value, since the IBL did not exist in 2009) | 1.88% (R2). Alternative 1.5% (R6), a CONFLICT that is kept as a variant |
| Pixel barrel layer | 3.73% (Ref. [27]) | 3.57% = 10.7% / 3 (R3 Sec. 4.10) |
| SCT barrel layer | 3.29% (Ref. [27]) | 2.96% = 11.8% / 4 (R3 Sec. 4.10) |
| Pixel disk | — | 3.57% (pixel barrel value used; no disk value in the references) |
| SCT disk | — | 3.75% per disk: modules 1.81%, services 1.47%, support (R3 Sec. 4.10). Applied per ring crossing |
| Where material is used | electrons only (bremsstrahlung and ionisation); flat conversion | electrons only, and the conversion probability layer by layer: P = 1 − exp(−7t/9), t = (x/X0)/\|cos α\| (R7, M01) |
| Quirks (signal) | no material effect | no material effect (the integrator is unchanged) |
| Multiple scattering | none | none |

## 5. η acceptance

**Fiducial rule.**
- Ideal: each quirk must cross all 8 barrel layers inside their length, with t < 25 ns.
- ATLAS: each quirk's hits must give 8 stations, i.e. at least 4 pixel and at least 4 SCT measurements (barrel or disk; D1, R14), and the line from the PV to station 8 must have |η| < 2.5.

**Straight lines from (0, 0, z0)** (`tables/X06_eta_station_coverage.csv`):

| z0 | Ideal: all 8 barrel layers | ATLAS: ≥ 4 pixel and ≥ 4 SCT, \|η\| < 2.5 |
|---|---|---|
| 0 | \|η\| ≤ 1.17 | \|η\| ≤ 1.17, 1.20–1.90, 1.92–2.49 |
| +4.5 cm | \|η\| ≤ 1.12 | ≤ 1.12, 1.15–1.78, 1.83–2.49 |
| −4.5 cm | \|η\| ≤ 1.21 | ≤ 1.21, 1.24–2.49 |

- The ideal limit is the last SCT layer: asinh(74.9/51.4) = 1.18 at z0 = 0. T01 found all 8 layers for |η| ≤ 1.15.
- The small ATLAS gaps are at the barrel/end-cap transition (around 1.2) and between the pixel barrel and the pixel disks (around 1.9).
- Strings and curvature bend the quirk tracks, so these gaps are partly filled in the real events.

**Measured on the selected events** (Z0, Λ = 4 keV; `tables/X04_eta_acceptance.csv`; η of the pair momentum):

| | Stage 1 · Ideal | Stage 2 · ATLAS |
|---|---|---|
| Largest \|η_pair\| | 1.08–1.27 | 2.41–2.50 |
| 90% quantile | 1.00–1.10 | 2.07–2.22 |
| Fraction with \|η_pair\| > 1.2 | 0–3% | 45–60% |

### 5.1 Why 1.17 and not the paper's "|η| ≲ 1.8"

**What Knapen et al. wrote** (R10, Sec. III A): *"For simplicity, we only included the barrel of the pixel and SCT detectors in our simulations, which effectively restricts the fiducial range to |η| ≲ 1.8."*

- This sentence states a *consequence* of using the barrel only. It is not a cut that the paper applies.
- The paper gives no barrel lengths, and no η cut appears anywhere in it (05 `EW_PAPER_REPRODUCTION_FOLLOWUP_2026-10-02/FOLLOWUP_REPORT.md`).
- Its fiducial rule is that "each quirk intersects each layer at least once", within 25 ns.

**Where 1.17 comes from.** Our Stages 0–1 use the finite ATLAS barrel lengths of Ref. [27] (pixel |z| < 40.05 cm, SCT |z| < 74.9 cm; IBL |z| < 33.015 cm from R2), with no η cut. This was decided in 05 `DECISIONS_LOG_2026-10-05.md`, D1. With these lengths, requiring all 8 layers gives |η| < asinh(74.9/51.4) = 1.17 at z0 = 0: the last SCT layer sets the limit.

**Where |η| = 1.8 lies in the detector.** A straight line from z0 = 0 reaches z = r · sinh(1.8) = 2.94 r at each layer:

| Layer | r (cm) | z at η = 1.8 (cm) | half-length (cm) | crossed? |
|---|---|---|---|---|
| IBL | 3.325 | 9.8 | 33.0 | yes |
| Pixel 1 | 5.05 | 14.9 | 40.05 | yes |
| Pixel 2 | 8.85 | 26.0 | 40.05 | yes |
| Pixel 3 | 12.25 | 36.0 | 40.05 | yes |
| SCT 1 | 29.9 | 88.0 | 74.9 | no |
| SCT 2 | 37.1 | 109.2 | 74.9 | no |
| SCT 3 | 44.3 | 130.3 | 74.9 | no |
| SCT 4 | 51.4 | 151.2 | 74.9 | no |

So a track at |η| = 1.8 is still inside the pixel barrel, but it has already left the SCT barrel. In the real detector it would continue into the SCT end-cap disks, which the paper did not simulate. With finite barrel lengths, such a track crosses 4 of the 8 layers and is not fiducial.

**Why not 1.8.**
- 1.8 does not match any "all 8 finite layers" acceptance. It lies between the pixel layer 4 edge (1.90) and the first SCT layer edge (1.65).
- The 1.8 reading was tested as a per-hit cut in the sensitivity study `05_.../tables/v6_sensitivity_eta_acceptance.csv`. The EW fiducial efficiency then becomes 0.45 (EW 1000 GeV) and 0.51 (EW 2000 GeV), against the paper's 0.28: strongly inconsistent (p = 8 × 10⁻⁴ and 1 × 10⁻¹⁰).
- With the finite lengths (≈ 1.17), all four paper benchmarks agree with the paper's 0.28 within the Wilson 95% interval (05 D1: COL1000 6/27, COL2000 22/68, EW1000 33/89, EW2000 62/186).

### 5.2 Is 2.5 in the ATLAS geometry a fixed cut, or does it follow from the elements?

Both conditions are applied (`signal/G01_signal_07.py`, D1):

1. **Geometry.** Each quirk's hits must give 8 stations: at least 4 pixel and at least 4 SCT measurements. The η range where this is possible follows from the element positions (§3). For a straight line it ends at |η| = 2.52 (z0 = 0), 2.49 (z0 = +4.5 cm) and 2.54 (z0 = −4.5 cm), at the outer SCT disks.
2. **Fixed cut |η| < 2.5** on the line PV → station-8 hit. This is the ATLAS track acceptance (R14: Loose tracks, |η| < 2.5).

The fixed cut removes only the thin band 2.50–2.54, so the acceptance is set almost entirely by the geometry. In the ideal geometry there is no explicit η cut at all: its limit (≈ 1.17) comes only from the barrel lengths.

## 6. What is the same and what differs

| Item | Same / different |
|---|---|
| 8 barrel layers: radii, half-lengths, pitches, SCT smearing settings Z0 and Z1160 | **same** |
| End-caps (6 pixel disks, 44 SCT ring surfaces) | **ATLAS only** |
| Fiducial rule | different: 8 barrel layers vs 8 stations with \|η\| < 2.5 |
| η acceptance | about \|η\| < 1.2 vs \|η\| < 2.5 |
| SCT setting A580 (ATLAS intrinsic 17 µm × 580 µm) | added in Stage 2 · Run 3 · ATLAS (D4); the barrel response is the same code |
| Material values | different sources (2009 figure vs Run-2 papers); they affect only the electron background and the conversion probability |
| Beam pipe | Stage 1: r = 2.35 cm, flat 1% conversion. Stage 2: inner r = 23.5 mm (R6), 0.227% X0 + layer-by-layer conversion |
| Field, timing, integrator, seeds, coplanarity algorithm | same |

## 7. Correction to earlier wording

Earlier files said that the ideal radii are "the ATLAS radii" and that the half-lengths are "those of Stage 2". This is corrected here:

- Knapen et al. define only the 8-layer structure.
- The numerical radii and lengths in both stages come from ATLAS documentation (R1, R2, R3).

## 8. Does material act on the quirks? (signal vs background)

**In this study, no: the material is used only for the background electrons and photons.**

**Quirks (signal).** The quirk trajectories come from the Stages 0–1 integrator, which is unchanged. It has no ionisation energy loss and no multiple scattering, in either geometry. This follows Knapen et al. (R10, Sec. III A):

> *"the rotation induced by the torque exerted by interactions with the detector material is small: the forces exerted by the ionization process when the quirks traverse a silicon layer are of the order ∼ (100 eV)², which induce an angular acceleration of up to α ∼ 10 ns⁻² … the shift in angle is ∆φ ∼ 10⁻³ for each layer the quirks traverse. We therefore neglect this effect in our simulations."*

**Background (C01, converted photons).** The material enters in two places:
1. **Where the photon converts.** The probability is computed layer by layer, P = 1 − exp(−7t/9) (R7), with t taken from the x/X0 of §4 (M01).
2. **The e⁺e⁻ tracks.** They lose energy by bremsstrahlung and ionisation at every element crossed: barrel layers, and also the disks in Stage 2 · Run 3 · ATLAS. This is the model of R11, App. A, as in Stages 0–1.

### 8.1 Multiple-scattering estimate for the quirks (2026-11-17)

The simulation does not include multiple scattering. To see whether it would matter, the Highland displacement was estimated for every selected event (`compare/X07_multiple_scattering.py`, `X07b_ds_with_ms.py`, `X07c_reach_with_ms.py`; tables `X07*`).

**How the estimate is made**
- Each event is taken at Λ = 4 keV, from the server runs.
- The path is a straight line along the pair direction. It crosses the beam pipe (0.227% X0) and every ATLAS element with its x/X0: divided by |sin θ| for a barrel layer and by |cos θ| for a disk.
- The scattering angle is the Highland formula: θ0 = 13.6 MeV / (βcp) · √t · (1 + 0.038 ln(t/β²)) (PDG, R7).
- The displacement at each silicon measurement is the out-of-plane sum of all earlier scatters.
- Two momentum choices:
  - (a) the quirk's initial lab momentum;
  - (b) a conservative lower bound p_min = m · βγ(pair), the momentum of a quirk momentarily at rest in the pair frame (the turning point of the string oscillation).

**Results**

| | Selected in both geometries (barrel, \|η_pair\| ≈ 0.6) | Selected only in ATLAS (\|η_pair\| ≈ 1.8) |
|---|---|---|
| Material up to station 8 (median Σ x/X0) | 0.30 | 0.52 |
| Displacement at station 8, initial p (median / 90%) | 6–8 / 23–29 µm | 18 / 58–70 µm |
| RMS over the 8 measurements, initial p (median) | 4–5 µm | 12–13 µm |
| RMS over the 8 measurements, p_min (median) | 27–31 µm | 21–30 µm |
| Selected events still passing Δs < 100 µm (Δs and MS added in quadrature), initial p | 97–99.6% | 93–96% |
| Same, p_min | 79–88% | 82–95% |

Effect on the reach at 332 fb⁻¹, with these fractions applied to the whole grid (an approximation):

| | Change of the reach |
|---|---|
| Initial p | −4 to −9 GeV |
| Conservative p_min | −11 to −32 GeV |

Example: colored Z0 exclusion goes from 1871 GeV to 1866 GeV (initial p) or 1851 GeV (p_min). EW A580 exclusion goes from 767 GeV to 759 / 740 GeV.

**Conclusions**
- Multiple scattering is not negligible against the pixel and SCT resolution (10–17 µm). It is, however, mostly below the Δs cut of 100 µm.
- The forward (ATLAS-only) events are affected about three times more than the barrel events at the initial momentum.
- The gain of ATLAS over Ideal (about 100–170 GeV) stays much larger than this effect.
- A full treatment (multiple scattering inside the integrator, for both geometries) is still to do. This is an estimate, not a simulation: the plane fit absorbs part of a common tilt, and the momentum along the string oscillation lies between choices (a) and (b).
- Knapen et al. estimate only the ionisation torque (Δφ ~ 10⁻³ per layer), not multiple scattering.

### 8.2 Background acceptance

The C01 converted-photon background (`backgrounds/C01_conversion_bkg.py`, geom = atlas) was simulated with the full ATLAS model:
- barrel and end-caps (`detsim07.build('atlas')`);
- the same station-based coplanarity selection as the signal (cop07, D1);
- pile-up tracks within the reconstruction acceptance |η| < 2.5 (R14);
- no η cut on the photons: 38% have |η| > 1.2 and 3% have |η| > 2.5 (`06_.../inputs/zgamma_13p6TeV/zgamma_photons.csv`).

Most of the background passing the selection comes from planes that use an end-cap element (`tables/S02_conversion_breakdown.csv`, 332 fb⁻¹):

| Setting | Total | with an end-cap element |
|---|---|---|
| Z0, μ = 50 | 69.2 | 56.8 |
| Z0, μ = 20 | 27.0 | 23.5 |
| A580, μ = 50 | 0.34 | 0.32 |

The background numbers therefore apply to the same end-cap acceptance as the ATLAS signal. The A580 statement "below one event" holds for the full |η| < 2.5 acceptance, within the MC statistics (3–5 passing photons).

## 9. Figures

Folder: `FIGURES_GEOMETRY_2026-11-17/`. GEO1–GEO3 are drawn with ROOT 6.40 by `make_geometry_figures.py`; GEO4–GEO5 with matplotlib by `make_geometry_3d.py`.

Panel names give only the detector: "Ideal (Knapen et al.)" and "ATLAS Run 2 ID". Every caption states that the layers are thin surfaces, that no material effects act on the quirk trajectories, and that the TRT is not included; GEO1 and GEO2 also state that the η lines start at z0 = 0. GEO1 and GEO4 add that Knapen et al. took their parameters from ATL-PHYS-PUB-2009-002, a pre-IBL document, and that the IBL follows their detector model in arXiv:1612.00850. Each figure has pdf, png, root, C, caption and provenance with sha256 of the inputs. All positions are read from `tables/X06_geometry_elements.csv`.

| Figure | Content |
|---|---|
| GEO1_rz_ideal_vs_atlas | R–z quarter section with lines of constant η: (a) Stage 1 · Ideal, (b) Stage 2 · ATLAS with the SCT disk numbers |
| GEO2_rz_pixel_zoom | the pixel region, with every radius, length and disk \|z\| labelled |
| GEO3_xy_barrel | transverse view at z = 0, with every barrel radius labelled |
| GEO4_3d_ideal | 3D cut-away view (true scale) of the Ideal geometry, each barrel layer labelled with r and \|z\| (matplotlib, `make_geometry_3d.py`) |
| GEO5_3d_atlas | 3D cut-away view (true scale) of the full ATLAS Run 2 ID model: barrel, pixel disks and SCT end-cap rings on both sides (matplotlib) |

**Google Colab version:** `FIGURES_GEOMETRY_2026-11-17/geometry_visualization_colab.ipynb`.
- It needs only numpy and matplotlib, and no file upload.
- Its element table is written from the same CSV by `build_colab_notebook.py`; the notebook prints the sha256 of that CSV.
- It draws the same three views and prints the element table with the |η| range of every element.
- All its code cells were run before delivery and give the same element table.

## 10. References

| ID | Reference | Used for |
|---|---|---|
| R1 | ATLAS Collaboration, *Alignment of the ATLAS Inner Detector in Run-2*, Eur. Phys. J. C 80 (2020) 1194, arXiv:2007.07624 | barrel radii, pixel disk \|z\|, SCT disk \|z\| range, pitches, intrinsic resolutions (Table 1) |
| R2 | ATLAS IBL Collaboration, *Production and Integration of the ATLAS Insertable B-Layer*, JINST 13 (2018) T05008, arXiv:1803.00844 | IBL length (\|z\| < 330.15 mm), 14 staves, 14° tilt, sensor radius 33.5 mm (conflict with R1); IBL material 1.88% X0; beam pipe inner radius reduced from 29 mm to 23.5 mm |
| R3 | ATLAS Collaboration, *The ATLAS Experiment at the CERN LHC*, JINST 3 (2008) S08003, ch. 4 | pixel and SCT active lengths, pixel disk radii (Table 4.3), SCT barrel (Table 4.5), SCT end-cap disks and rings (Table 4.6), resolutions (Table 4.1), material per layer and disk (Sec. 4.10) |
| R4 | same paper, ch. 2 | solenoid field: 1.998 T at the IP, ~1.8 T at z = 1.7 m |
| R6 | ATLAS Collaboration, *Study of the material of the ATLAS inner detector for Run 2 of the LHC*, JINST 12 (2017) P12009, arXiv:1707.02826 | Run-2 beam pipe (0.8 mm Be, inner radius 23.5 mm); IBL material 1.5% X0 (alternative value) |
| R7, R7b | Particle Data Group, *Review of Particle Physics* (2024), ch. 34; PDG atomic and nuclear properties of Be and Si | conversion probability 1 − exp(−7x/9X0); X0(Be) = 35.28 cm, X0(Si) = 9.370 cm |
| R10 | S. Knapen, H. K. Lou, M. Papucci, J. Setford, *Tracking down quirks at the LHC*, Phys. Rev. D 96 (2017) 115015, arXiv:1708.02243 | 8-layer barrel structure; "\|η\| ≲ 1.8" statement; material torque neglected |
| R11 | S. Knapen, S. Pagan Griso, M. Papucci, D. J. Robinson, *Triggering soft bombs at the LHC*, JHEP 08 (2017) 076, arXiv:1612.00850 | detector-response model (App. A): bremsstrahlung, ionisation, 25 ns, 2 T |
| R14 | ATLAS Collaboration, *Track and vertex reconstruction with the ATLAS Inner Detector*, CERN-EP-2026-096, arXiv:2605.07585 | hit counting on barrel layers and disks alike; track acceptance \|η\| < 2.5 |
| [27] | ATL-PHYS-PUB-2009-002, arXiv:0901.0512 (Ref. [27] of R10) | Stages 0–1 barrel lengths and per-layer material (Fig. 3, digitised) |

Local copies of the references are in `references/pdf/` and `references/text/`, and are listed in `references/REFERENCES.md`.
