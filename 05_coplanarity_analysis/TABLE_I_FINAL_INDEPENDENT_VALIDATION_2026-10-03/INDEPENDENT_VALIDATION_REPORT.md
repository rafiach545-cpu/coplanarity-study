# Table I — Independent Validation (2026-10-03)

The provisional configuration is frozen as `PROVISIONAL_PAPER_MATCHED_CONFIGURATION_v1/` (a copy; the original directory is untouched). It is **not** authoritative. Figure 6 was not touched.

## 1. SCT smearing: circular selection removed

`notes/01_SCT_SOURCE_AUDIT.md` has the full detail.
- **Ref. [27] read directly** via its CSC-book publication (arXiv:0901.0512, pp. 40–43).
- **Ref. [27] quotes:** SCT intrinsic accuracy 17 µm (R-φ) and 580 µm (z), with the stereo strips measuring **both** coordinates. 17 µm is an intrinsic accuracy, not the 80 µm pitch.
- **The paper's** "twice the intrinsic accuracy" literally gives **σ_Rφ = 34 µm, σ_z = 1160 µm** (option d).
- The strip/line representation (e) is excluded by the paper ("a single hit is … its position three-vector").
- The literal reading is contradicted by the paper's own Fig. 5 and by its Fig. 4 event (Δs = 83 µm). **The paper does not determine the z treatment**, so all four alternatives are kept as an envelope.
- **"No z smearing" is labelled CALIBRATED, not paper-proven.**

## 2. Δw discrepancy: resolved for EW, quantified for colored

- **Definition:** the paper's Fig. 4 event, digitized and calibrated on its own plotted ±Δw band, gives √(Σ(x·n₂)²/(N−1)) = 0.148 cm = **2.00 × the caption Δw = 0.074 cm**. The paper's *quoted/plotted* Δw is 0.5 × the Eq. 10–11 statistic.
- **Units, normalisation, orientation:** all identical to ours. The factor is present at truth level, so it is not a smearing or merging effect.
- **EW:** with that convention our Δw agrees with Fig. 5 at every stage (KS p = 0.64–0.999).
- **Colored:** agreement needs, in addition, the plotted population to be "plane + multiplicity" (before cut 3), giving KS p = 0.06–0.16. A residual ~1.5× in the median remains on 10–21 events; it is carried as a systematic.
- **The paper's Fig. 2** colored event has quirk separations up to 3.5 cm, consistent with Eq. 1 and with our trajectories. The trajectory physics agrees.
- **Applying the halved Δw to the cuts** (W2) changes no efficiency; the Δw cut never binds.

## 3. Hit-multiplicity losses (all fiducial events, literal algorithm)

| Cause | EW (z unsmeared) | EW (z 1.16 mm) | Colored (z unsmeared) |
|---|---|---|---|
| ×3 growth rule after refit (hits rejected because pixel-quantization noise inflates Δs) | 27 | 1 | 5 |
| True pixel merging (< 2 hits available in > 1 layer) | 10 | 9 | 0 |
| Out-of-plane window \|x·n₁\| < 0.05 cm (SCT z noise) | 0 | 48 | 0 |
| In-plane window \|x·n₂\| < 1 cm (large colored oscillation amplitude) | 0 | 0 | 7 |
| Mixed | 1 | 3 | 1 |

- Seed selection or candidate ranking: no event (no other candidate would have passed).
- Numerical tolerance: no event under z-unsmeared (3 near-threshold under 1.16 mm).
- With truth hits (no detector effects): EW 0 failures; colored 9 (the n₂ window, physics amplitude).

## 4. EW benchmark model

- **The colored model is correct.**
- **The EW UFO's Z coupling is the SM electron's chiral coupling, not a (1,1)₁ vector-like singlet. This is an implementation error.** It was corrected in an isolated copy (`quirk_vlZ`):
  - σ falls by 24%;
  - the trigger efficiency does not change (0.166, Fisher p = 0.60 vs frozen).
- **Partonic channels:** > 99% of triggers come from 1-jet matrix-element events in both benchmarks.
  - Share of 1-jet events among matched: EW 0.55, colored 0.62.
  - Trigger efficiency within 1-jet events: EW 0.32, colored 0.38.
  - Together these give the EW/colored ratio of 0.75; the paper's ratio is 0.42.
- **Pre-shower pair pT trigger:** EW 0.118, colored 0.152.
- No model or channel property found explains the paper's EW value.

## 5. Paper statistical uncertainty

- **No raw counts or ancillary files exist** (arXiv /anc returns 404 for v1 and v2; the text has no signal sample sizes). Exact paper-vs-project significance therefore cannot be calculated.
- **Inference from integer quantization of the Fig. 5 histograms:** about 1,075 EW and 525 colored reconstructed-signal events. This implies paper uncertainties of about ±0.012–0.019 (reco), ±0.007 (fid) and ±0.002 (trig), plus ±0.003 from rounding.
- `tables/confirmation_paper_compatibility.csv` gives both the quoted-value tests and these two-sample tests.

## 6. Independent confirmation (configuration locked before generation)

- **Lock:** `notes/LOCKED_CONFIGURATION.md` (SHA-256 `07445b70…`), written while no confirmation file existed. The script hash was verified identical at run time.
- **Samples:** fresh MG5 seeds 9401 (EW, 4000 LHE, vector-like model) and 9501 (colored, 10000 LHE). Not pooled with anything.

| Quantity | N_pass/N_total | Eff. | Wilson 95% | Paper | Inside? | Two-sample p (paper n low/high) |
|---|---|---|---|---|---|---|
| EW trigger | 352/2069 | 0.170 | [0.155, 0.187] | 0.10 | no | < 1e-4 |
| COL trigger | 997/4331 | 0.230 | [0.218, 0.243] | 0.24 | yes | 0.17 / 0.19 |
| EW fiducial (B) | 102/352 | 0.290 | [0.245, 0.339] | 0.28 | yes | 0.70 |
| COL fiducial (B) | 94/333 | 0.282 | [0.237, 0.333] | 0.28 | yes | — |
| EW reco, Z0 / Z34 / Z580 / Z1160 | 78 / 93 / 20 / 14 of 102 | 0.765 / 0.912 / 0.196 / 0.137 | Z0 [0.674, 0.836] | 0.72 | Z0 only | Z0 0.31 |
| COL reco, Z0 / Z34 / Z580 / Z1160 | 42 / 51 / 16 / 6 of 94 | 0.447 / 0.543 / 0.170 / 0.064 | Z0 [0.350, 0.547] | 0.35 | none (Z0 at edge) | Z0 0.067–0.077 |

The geometry-A systematic and the Δw-convention systematic are in `tables/confirmation_efficiencies.csv`.

## Final decision for this stage

The conditions for a single authoritative Figure 6 are **not met**:
- the SCT z treatment is **not** independently justified (paper text and paper figures conflict);
- the EW trigger is unreproduced.

What is met:
- the reconstruction definition is fixed;
- Δw is resolved for EW and carried as a systematic for colored;
- the configuration was locked before the confirmation sample.

**Recommendation: two separate Figure 6 results.**
- **A. Original baseline.**
- **B. An explicitly labelled calibrated paper-matched model.**

This stage is superseded by the literal-reproduction task in `PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/`.
