# Table I Reproduction Forensics — arXiv:1708.02243v2

Date: 2026-10-02. Machine: DESKTOP-OD6H911. Figure 6 was **not** resumed. No checkpoint, frozen sample, frozen source file or existing report was modified, and nothing was committed or pushed. New generation ran only in the isolated `/home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02/`.

## Bottom line

| | EW trig | EW fid | EW reco | COL trig | COL fid | COL reco |
|---|---|---|---|---|---|---|
| **Paper Table I** | 0.10 | 0.28 | 0.72 | 0.24 | 0.28 | 0.35 |
| Current project (frozen samples) | 0.177 ✗ | 0.487 ✗ | 0.20 ✗ | 0.237 ✓ | 0.337 ✓ | 0.125 ✗ |
| **Coherent config "B + R2 + A0"**, existing samples (fresh-seed detector randoms, `08`) | 0.177 ✗ | 0.342 (p=0.027) | **0.734 ✓** | **0.237 ✓** | **0.284 ✓** | **0.444 ✓** |
| **Same config, independent seeds** (MG 9101/9201) | 0.170 ✗ | **0.310 ✓** | **0.776 ✓** | **0.218 ✓** | **0.280 ✓** | **0.571 ✓** |

✓ = Table I value inside the Wilson 95% interval. The configuration:
- **Generation:** the frozen generator settings.
- **B:** finite ATLAS barrel half-lengths, with no η cone.
- **R2:** SCT hits smeared in R-φ only (σ = 2 × 17 µm), z unsmeared; pixel quantization unchanged.
- **A0:** the literal paper algorithm, i.e. the unmodified project `coplanarity_fit`.

On independent seeds **five of six Table I numbers are reproduced simultaneously by one configuration**. The **EW trigger efficiency is not reproduced by any defensible setting**.

That trigger result:
- holds across 19 pre-registered one-setting variations, in addition to the earlier MG5 2.3.3 / Pythia 8.212 study;
- is the paper-undocumented generator setup that prevents exact reproduction;
- the paper's EW/colored trigger ratio (0.42) lies outside everything any setting produced (0.60–0.84).

---

## PART A — Reconstruction forensic audit

### A1. Paper re-read (Sec. III C, Sec. IV, Eqs. 10–12, captions, detector sources)

- **Eq. 10:** d(n, x_a) = sqrt(1/(N−1) Σ (n·x_a)²), the RMS distance to a plane **through the vertex**.
- **Eq. 11:** T_ij = 1/(N−1) Σ x_i x_j. Δs² is the smallest eigenvalue and Δw² the second.
- **Units:** Δs and Δw are in cm.
- **Cuts:**
  - seed: Δs < 0.05 cm, Δw < 1 cm, x·n₃ > 0;
  - iteration: |x·n₁| < 0.05 cm, |x·n₂| < 1 cm, growth ≤ ×3;
  - selection: Δw < 1 cm, then smallest Δs;
  - signal region: plane + multiplicity + Δw < 1 cm + Δs < 0.01 cm.
- **Merging:** "Hits in neighbouring pixels … are merged". The project uses adjacency 1 in pixel-index space, transitive.

The project code (`coplanarity_fit.py`, `trajectory_to_hits.py`) implements all of these exactly. I verified this line by line and by an instrumented re-implementation that asserts identical candidates.

**Detector resolution sources:**
- **Paper (Sec. III A):** "for the pixel detector we use the pixel size rather than the resolution and for the … SCT we conservatively assume a resolution of twice the intrinsic accuracy quoted in [27]".
- **ATLAS JINST 3 S08003, Table 4.1 (primary source):** pixel 10 (R-φ) × 115 (z) µm; **SCT 17 (R-φ) × 580 (z) µm per module, the z "arising from the 40 mrad stereo angle"**. Ref [27] itself is unreadable (CDS bot block).
- **Project:** pixel quantized to the 50×400 µm pixel centre; SCT Gaussian σ = 34 µm (R-φ), **1160 µm (z)**. Units are correct (µm × 1e-4 → cm). Smearing is two-sided Gaussian.

### A2. Per-event forensics for every trigger+fiducial event (EW1000, EW2000, COL1000, COL2000)

`forensics/<sample>_R0_A0_events.jsonl`, one JSON record per fiducial event, containing:
- unsmeared, smeared and merged hits; hits available per layer;
- every seed pair and seed fit with its pass/fail reason;
- every candidate with plane parameters (n₁, n₂, n₃, Δs, Δw), assigned hits and a step-by-step growth log (added / not eligible with reason / rejected by the ×3 rule with values);
- the selected candidate and why; per-layer multiplicity; Δs, Δw; the first failed Sec. IV requirement.

**Reproduction of the stored project results** (events re-propagated with the project's own vertex z0 and random stream):

| Sample | Fiducial | Δs exact (1e-9) | Plane / mult / final / hit count match |
|---|---|---|---|
| EW1000 | 40 | 40/40 | all |
| COL1000 | 7 | 7/7 | all |
| COL2000 | 25 | 25/25 | all |
| EW2000 | 94 | 76/94 | final 94/94, hit count 94/94; plane 75 = 75 (one flip each way) |

The 18 EW2000 Δs differences are cross-machine floating-point non-reproducibility. The stored EW2000 results came from the source machine, and the project's *own* code, run here, gives the same values as my pipeline (shown for event 127). No count changes.

### A3. Root cause: SCT z smearing

- **Truth control:** planes fitted to *unsmeared* crossings have median Δs = 4–13 µm, 100% below 0.01 cm, in all samples. The trajectories are planar.
- **Plane orientation:** the plane normals have median |n₁·ẑ| ≈ 0.45, so z noise feeds directly into Δs.
- **Paper's own Fig. 5** (vector-extracted from the arXiv source PDF, axis-calibrated from its tick labels): signal Δs median 28 µm (EW) and 35 µm (colored), with 92% / 90% below 0.01 cm.
- **Project:** median 150 µm, only ~30% below 0.01 cm.

Pre-registered resolution readings (`notes/PREREGISTERED_VARIANTS.md`, written before any evaluation), Fig. 5 Δs test (KS p, population = plane + multiplicity):

| Model | Description | EW KS p | COL KS p | Verdict |
|---|---|---|---|---|
| R0 | project: SCT σ_z = 1.16 mm | ≈0 | ≈0 | **excluded by paper Fig. 5** |
| R1 | pixel Gaussian σ = pitch | ≈0 | ≈0 | excluded |
| R4 | pixel Gaussian σ = pitch/√12 | ≈0 | ≈0 | excluded; equivalent to quantization (the √12 question is irrelevant) |
| R2 | SCT R-φ only (z unsmeared) | ≈0 (scale right: core 40 vs 28 µm) | **0.69** | allowed |
| R3 | SCT 34 µm isotropic | ≈0 (scale right) | **0.45** | allowed |

**Verified implementation difference:** the project's literal application of 2 × 580 µm SCT z smearing to the fitted hits is incompatible with the paper's own published Δs distributions for both benchmarks.

It is also the cause of the multiplicity losses. Of the 22 EW2000 "hits available but not collected" failures:
- under R2, 21 pass the full SR (the 22nd fails multiplicity); under R3, all 22 pass;
- mechanism: the ×3 growth rule rejects SCT hits whose z noise inflates Δs.

### A4. Item 6 (algorithm questions)

| Question | Answer |
|---|---|
| Greedy selection / smallest-Δs ranking | A2 (coverage-first ranking, not paper text) changes no event in any model or sample. |
| Refitting after adding hits | Done after every accepted hit, as the paper says ("together with the list, recompute T"). |
| Retaining multiple planes / hit reuse | Candidates are independent and hits are reused across seeds; the paper describes nothing else. |
| Growth "factor 3" reference | A1 (relative to the seed) is not the literal reading. It lowers EW and colored efficiency under R0; under R2 it lowers both too. |
| Outcome | **No algorithmic error found.** The algorithm is the paper's. |

### A5. Variant efficiencies

`tables/variant_efficiencies.csv` holds all models × algorithms × samples, with k/n, SE, Wilson 68/95, CP95 and exact p. Event-level changes, with old/new first-failure reason and selected layers, are in `tables/variant_changed_events.csv`.

Pooled full-SR (exact project random stream, geometry A):

| Config | EW | p vs 0.72 | COL | p vs 0.35 | Both improve vs R0? |
|---|---|---|---|---|---|
| R0 A0 (current) | 27/134 = 0.20 | ≈0 | 4/32 = 0.125 | 0.008 | — |
| R2 A0 | 110/134 = 0.82 | 0.009 | 16/32 = 0.50 | 0.094 | **yes, both** |
| R3 A0 | 126/134 = 0.94 | ≈0 | 19/32 = 0.59 | 0.005 | EW overshoots |
| R3 A1 | 93/134 = 0.69 | 0.50 | 15/32 = 0.47 | 0.19 | yes, but non-literal algorithm |

**Honesty note on R2 vs R3:** Fig. 5 (the pre-registered criterion) excludes R0, R1 and R4, but **cannot discriminate R2 from R3**. Choosing R2 over R3 is therefore informed by Table I ε_reco, and R2's ε_reco agreement is not an independent confirmation of R2. What *is* independent:
- the Fig. 5 exclusion of R0;
- the independent-seed reproduction (seed-independence, not model-independence).

Physically, R2 is the reading in which an SCT module measures R-φ: its z comes from the 40 mrad stereo and is the coarse coordinate.

### A6. Remaining reconstruction-level residual: Δw

| | EW median Δw | Colored median Δw |
|---|---|---|
| Paper Fig. 5 | 0.045 cm | 0.089 cm |
| Ours (every model; truth-level too) | ~0.10 cm | ~0.43 cm |

Δw is incompatible in every model. It is **not** a kinematics or Λ-convention issue: the paper's own Fig. 6 d_cm contours, inverted through Eq. 1, give a mean (γ−1) of 0.305 (EW, 800 GeV) and 0.180 (colored, 1800 GeV); ours is 0.29–0.30 and 0.16–0.17 (`tables/paper_fig6_dcm_extracted.json`). The source of the paper's narrower Δw is **unresolved**. It does not prevent the ε_reco agreement above.

### A7. Corrected implementation (diagnostic; frozen code untouched)

- `scripts/corrected_detector_response.py` (R2 / R3 SCT response) and `scripts/02_forensic_pipeline.py`.
- Tested on the 1000 and 2000 samples (A5) and on independent seeds (Part C table).

---

## PART B — Trigger setting search

The screen was pre-registered (`notes/PREREGISTERED_TRIGGER_SCREEN.md`): one setting at a time, identical for EW and colored. Every run card, seed, banner, Pythia settings file and log is in `partB_provenance/`.

The shower driver was validated event by event against both frozen showers (EW 1045/186, colored 873/207). Generation used fresh MG5 3.7.3 template copies with a clean rebuild under the GCC 16.2 toolchain (a compiler mix initially segfaulted and was fixed before any result).

| Config | EW ε_trig | COL ε_trig | COL p vs 0.24 | Joint? |
|---|---|---|---|---|
| B0 frozen | 0.178 | 0.237 | 0.87 | ✗ |
| G0 new seed (control) | 0.170 | 0.218 | 0.13 | ✗ |
| S1–S3 qCut 30/60/90 | 0.166/0.174/0.163 | 0.233/0.227/0.217 | — | ✗ |
| S4 shower-kT MLM | 0.148 | 0.203 | 0.020 | ✗ |
| S5 LHE production scales off | 0.148 | 0.226 | 0.35 | ✗ |
| S6 tune 4C / S7 A14 | 0.164 / 0.162 | 0.265 / 0.227 | — | ✗ |
| S8/S9 pTmaxMatch 1/2 | identical to B0 (setting inert under LHE + MLM) | | | ✗ |
| G1 xqcut 15 / G2 xqcut 60 | 0.176 / 0.140 | 0.256 / 0.196 | — / 0.0004 | ✗ |
| G3 cteq6l1 | 0.152 | 0.189 | 0.0003 | ✗ |
| G4 HT/2 scale | 0.166 | 0.206 | 0.022 | ✗ |
| G5/G6 scalefact 0.5/2 | 0.182 / 0.149 | 0.221 / 0.219 | — | ✗ |
| G7 14 TeV | 0.170 | 0.283 | 0.005 | ✗ |
| D1 up to 2 jets (contradicts paper) | 0.151 | 0.239 | 1.0 | ✗ |
| D2 0 jets, no matching (contradicts paper) | 0.130 | 0.200 | ≈0 | ✗ |
| (earlier) MG5 2.3.3 + Pythia 8.212 | 0.167 | — | — | ✗ |

Findings:
- 0.10 is outside every EW Wilson 95% interval; the minimum is 0.130 [0.116, 0.145], from a paper-contradicting configuration.
- Every setting that lowers EW lowers colored too. EW/colored ratio: 0.60–0.84 here; the paper's is 0.42.
- No configuration was promising, so no confirmation sample was warranted.
- Rejected denominators, as before: trigger/generated matches EW (0.09) but breaks colored (0.10 vs 0.24).

**Verdict: no defensible generator setting reproduces both trigger values.** The EW trigger efficiency depends on a paper-undocumented setup that cannot be recovered from the paper.

---

## PART C — Fiducial (both geometry models, kept separate)

No trigger-compatible generation exists, so the fiducial test uses the frozen-setting generation, on both the existing samples and the independent seeds. The cone and finite-z are never combined: combining them is not in the paper, and its extra losses are all IBL-only vertex-offset artefacts.

| Model | EW existing (project z0 stream, `07_fiducial_models.py`) | EW indep. (`08`) | COL existing (project stream) | COL indep. (`08`) |
|---|---|---|---|---|
| A: project \|η\|<1.8 cone | 134/275 = 0.487 ✗ | 89/187 = 0.476 ✗ | 32/95 = 0.337 ✓ | 18/50 = 0.360 ✓ |
| **B: finite ATLAS barrel** | 95/275 = 0.345 (p=0.019) | 58/187 = 0.310 ✓ | 28/95 = 0.295 ✓ | 14/50 = 0.280 ✓ |

Only B reproduces both benchmarks; EW-existing is marginal in the pooled sample, while each EW sample alone is compatible.

Caveat: the paper's EW triggered population is evidently different (ε_trig 0.10), so its fiducial denominator may differ from ours.

---

## Final success requirement — answer

**No single coherent configuration reproduces all six Table I values.**

The **closest defensible configuration** is "frozen generation + finite barrel (B) + SCT R-φ-only resolution (R2) + literal paper algorithm (A0)". Validated with independent MG5 seeds (9101 EW, 9201 colored), it reproduces:
- colored trigger (0.218), fiducial (0.280) and full-SR reconstruction (0.571; 8/14, p = 0.096);
- EW fiducial (0.310) and full-SR reconstruction (0.776; 45/58, p = 0.38);

with each paper value inside the Wilson 95% interval.

The **one** value it cannot reproduce is the EW trigger (0.170 vs 0.10). The **paper-undocumented setting preventing exact reproduction** is the EW generator/trigger setup:
- none of 19 one-at-a-time variations reaches it;
- nor does the version-matched historical toolchain.

Two further caveats:
1. R2 vs R3 is not settled by the paper's figures. R3 gives EW/COL reco 0.90/0.59, compatible with neither.
2. The Δw width residual (A6) is unexplained.

## Recommendation

**Option 3: maintain the baseline and the paper-matched calibrated model separately.** Do not resume the old Figure 6 as the paper reproduction.

1. **Old Figure 6 (option 1) is not paper-faithful.** It uses R0, which the paper's own Fig. 5 excludes. Its ε_reco (~0.1–0.2 vs 0.35–0.72) would bias every Figure 6 contour by a factor ~3–5. It remains a valid *literal-text baseline*: the paper's sentence applied to the standard SCT z accuracy.
2. **Restart as "verified corrected" (option 2) is not yet justified.** The R0 exclusion is verified, but the replacement (R2 vs R3) and the geometry (B) are inferences rather than paper-documented facts, and the EW trigger remains unreproduced.
3. **What to run, as a separate, labelled paper-matched model:**
   - B + R2 + A0, with R3 and geometry A as systematics.
   - It reuses the 13 completed Figure 6 generation points, since the trigger stage is unchanged; only the downstream propagation and reconstruction need to run.
   - The existing checkpoints store per-event summaries but no hits, so they cannot be reprocessed into the new model.
   - The EW trigger normalisation should be carried as an explicit, documented ×0.10/0.177 discrepancy, not silently rescaled.

## File index

- `notes/PREREGISTERED_VARIANTS.md`, `notes/PREREGISTERED_TRIGGER_SCREEN.md`: written before evaluation.
- `paper_figures/`: paper Fig. 5/6 PDFs and renders.
- `tables/paper_fig5_extracted.json`, `tables/paper_fig6_dcm_extracted.json`
- `scripts/00`–`08` with matching `logs/`
- `tables/truth_crossings_*`, `exact_crossings_fiducial_*`, `variant_*`, `fig5_shape_tests.csv`, `R0A0_reproduction_vs_stored.csv`
- `tables/trigger_screen_results.csv`, `fiducial_models_*`, `full_chain_*`
- `forensics/*_R0_A0_events.jsonl`: complete per-event forensic records.
- `partB_provenance/`: all Part B cards, seeds, banners, settings, logs, driver source and hash, LHE hashes.
- `SHA256_MANIFEST.txt`
