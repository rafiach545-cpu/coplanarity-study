# Corrected SCT smearing — exact implementation

**Notation:**
- **SCT**: the ATLAS semiconductor tracker, called "silicon microstrip tracker (SCT)" in the paper.
- **R-φ**: the azimuthal coordinate along the layer circumference, R·φ.
- **z**: the longitudinal coordinate along the beam axis.
- **σ_Rφ, σ_z**: Gaussian standard deviations, in µm.

## Paper statement (arXiv:1708.02243v2, Sec. III A, verbatim)

> "Specifically, for the pixel detector we use the pixel size rather than the resolution and for the silicon microstrip tracker (SCT) we conservatively assume a resolution of twice the intrinsic accuracy quoted in [27]."

## Detector reference values

ATLAS Collaboration, JINST 3 S08003 (2008), Table 4.1 ("intrinsic accuracy"):

| Detector | R-φ | z |
|---|---|---|
| Pixel barrel | 10 µm | 115 µm (pixel size 50 µm × 400 µm) |
| SCT barrel, per module | 17 µm | 580 µm |

The SCT z value carries the footnote "arises from the 40 mrad stereo angle". Ref. [27] (ATL-PHYS-PUB-2009-002) could not be read (CERN CDS bot block). The JINST values are the standard published ones.

## Implementations compared

| | Previous project implementation (R0) — rejected | Corrected implementation (R2) — final |
|---|---|---|
| Pixel (unchanged) | hit placed at the centre of the pixel containing the true crossing (50 µm × 400 µm grid; IBL 50 µm × 250 µm) | same |
| SCT R-φ | Gaussian, σ_Rφ = 2 × 17 µm = **34 µm** | Gaussian, σ_Rφ = 2 × 17 µm = **34 µm** |
| SCT z | Gaussian, σ_z = 2 × 580 µm = **1160 µm** | **not smeared** (true crossing z kept) |
| Hit merging, units, random-number handling | — | unchanged (µm → cm via ×1e-4) |

Why R0 is rejected: the paper's own Fig. 5 signal Δs distributions are incompatible with it (KS p ≈ 0 for both benchmarks). See `PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/tables/fig5_shape_tests.csv`.

Code: `PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/scripts/corrected_detector_response.py` (`sct_sigma_cm("R2")`), applied in `scripts/02_final_full_chain.py`, function `reco`:

```
sr = 34 um * 1e-4 (cm);  sz = 0  (R2)
rphi_hit = rphi_true + sr * g1   (g1 ~ N(0,1))
z_hit    = z_true    + sz * g2   (g2 ~ N(0,1), drawn but multiplied by 0)
```

## Status of the choice

- **Verified:** R0 is inconsistent with the paper's published Δs distributions, so the z smearing of 1.16 mm cannot be what produced the paper's results.
- **Inferred:** R2 (z unsmeared) versus R3 (σ_z = σ_Rφ = 34 µm). Both are consistent with Fig. 5 for the colored benchmark, and Fig. 5 does not separate them.
- R2 corresponds to treating the SCT as an R-φ-measuring strip detector, with the coarse stereo z ignored in the resolution model.
- R3 is reported as a systematic (it overshoots ε_reco for both benchmarks).
- The R2/R3 choice was informed by Table I. R2's ε_reco agreement is therefore not an independent confirmation of R2.
