# Unresolved Differences: Literal Reproduction vs arXiv:1708.02243v2

> **v2 CORRECTION (2026-10-03):** the classification in this document is superseded where it conflicts with `CORRECTION_ACCEPTANCE_AND_LONGITUDINAL_2026-10-03.md`. The paper-stated acceptance (barrel only, |η| ≲ 1.8, no finite-z boundary) is now PRIMARY. The finite barrel of Ref. [27] (called "literal" below) is an INFERRED sensitivity. SCT z 1160 µm is INFERRED, not stated; no SCT z smearing is UNDOCUMENTED. Primary denominators: COL2000 25, EW2000 94. See `FINAL_EXECUTIVE_REPORT.md` (v2) and `PROFESSOR_REPORT_2026-10-03_v2.pdf`.

Each item gives the paper statement, the literal implementation, the observed difference, its classification, and why it cannot be closed from documented information. Machine-readable version: `tables/unresolved_setting_matrix.csv`.

Classification keys:
- **IMPL-ERROR:** our implementation contradicts a stated requirement.
- **UNDOCUMENTED:** the paper does not give the setting.
- **PAPER-INTERNAL:** the paper's text and its own figures disagree.
- **STAT:** statistical limitation.
- **MODEL-SYST:** a documented simplification.

## U1. EW trigger efficiency: 0.174–0.178 (ours) vs 0.10 (paper)
- **Paper:** pT(QQ̄) > 200 GeV; Table I ε_trig = 0.10 (EW), 0.24 (colored). Generator: MG5 + Pythia8, ≤ 1 jet, MLM matching (Sec. III A). The TeX comments list MG5 v2.3.3 and Pythia 8.212.
- **Ours:**
  - EW1000: 89/511; EW2000: 186/1045. Wilson 95% intervals exclude 0.10 (p = 2.8e-7 and 1.8e-14).
  - The colored trigger reproduces in both samples (101/419 and 207/873).
  - The independent fresh-seed vector-like confirmation agrees: EW 352/2069 = 0.170 (Wilson 95% [0.155, 0.187]); colored 997/4331 = 0.230 (`TABLE_I_FINAL_INDEPENDENT_VALIDATION_2026-10-03/INDEPENDENT_VALIDATION_REPORT.md`).
- **What has been ruled out:** more than 24 one-at-a-time variations (`EW_PAPER_REPRODUCTION_FOLLOWUP_2026-10-02/`, `PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/` Part B):
  - generator versions (2.3.3/8.212 pilot);
  - xqcut/qCut, PDF, scale choices;
  - hard-process vs final-state pair pT;
  - jet-pT vs pair-pT trigger, MET definitions;
  - the vector-like vs chiral Z coupling.
  - No documented setting gives 0.10, and the EW/colored ratio stays 0.60–0.84 (paper 0.42).
- **Class:** UNDOCUMENTED. The paper's matching parameters, PDF, scale and any additional generator-level requirement are not stated. A hard-process-only pT(QQ̄) gives EW 64/511 = 0.125 and 121/1045 = 0.116, closer to the paper but not a reading the text supports. It is not adopted.

## U2. SCT z resolution: literal 1160 µm vs the paper's own Fig. 5 / Fig. 4
- **Paper:** "the SCT hit positions are smeared by twice the intrinsic accuracy." Ref. [27] gives 17 µm (R-φ) and 580 µm (z), so the literal reading is 34 µm / 1160 µm.
- **Conflict:**
  - With z = 1160 µm our signal Δs median is ≈ 150 µm. The paper's Fig. 5 medians are ≈ 28 µm (EW) and 35 µm (colored), with ≈ 90% of events below 0.01 cm; its Fig. 4 event has Δs = 83 µm.
  - KS p ≈ 0 against the digitised Fig. 5.
  - The paper's histograms are consistent only with z ≲ 34 µm (or none).
- **Consequence:** this one setting moves EW reconstruction from 0.06–0.16 (literal) to 0.81–0.92 (z ∈ {0, 34} µm), and colored from 0.05–0.17 to 0.36–0.83.
- **Class:** PAPER-INTERNAL plus UNDOCUMENTED. The text-literal value is authoritative here. The paper's figures prove its simulation did something else, which it does not describe. **No 100% reproduction is possible.**

## U3. Δw definition: Eq. 11 √λ₂ vs the paper's Fig. 4 band
- Digitising the paper's own Fig. 4 band against the plotted hits gives quoted Δw = 0.5 × √λ₂ (ratio 2.00).
- Fig. 5 cross-check (`FINAL_FIGURES/F05_*`):
  - EW2000 literal plane + multiplicity: median √λ₂ = 0.092 cm vs digitised paper median 0.045 cm. **Ratio 2.07**, consistent with the factor 2.
  - Our EW median Δw barely depends on the SCT z resolution (0.092–0.101 cm across 0–1160 µm).
  - Pile-up and conversion ratios are 1.38 and 1.21, but those populations are defined differently (the paper's pile-up is the relaxed 1-hit-per-layer set). Colored (N = 4) is not informative.
- Using W2 (½√λ₂) changes **no** count in any sample, because the Δw < 1 cm cut never binds after the multiplicity cut.
- **Class:** PAPER-INTERNAL. It has no effect on Table I.

## U4. Fiducial acceptance: "|η| ≲ 1.8" vs finite barrel
- **Paper:** barrel only, "effectively restricts the fiducial range to |η| ≲ 1.8".
- **Ref. [27]:** pixel |z| < 400.5 mm, SCT |z| < 749 mm. Requiring all 8 layers gives |η| ≲ 1.17 at the outer SCT, not 1.8.
- **Fiducial results:**
  - Literal finite barrel: EW 0.333–0.371, colored 0.222–0.324. Paper 0.28 is inside every Wilson 95% interval.
  - η-cone (project): EW 0.45–0.51, which is incompatible.
- **Class:** PAPER-INTERNAL (the 1.8 wording). The literal geometry reproduces Table I fiducial, so this does not limit the result.

## U5. EW model Z coupling (implementation error, fixed in the confirmation sample)
- The frozen EW UFO uses SM-electron chiral Z couplings; the paper requires a vector-like (1,1)₁ fermion.
- The effect is σ −24%. It is trigger-neutral: the vector-like model confirmation gives the same trigger within errors.
- **Class:** IMPL-ERROR, no effect on any Table I efficiency within statistics. It **does** affect absolute signal yields (Figure 6, out of scope).

## U6. Pile-up 4/8-layer rate: ≈ 0.7% (literal) vs ≈ 1e-3 (paper)
- **Paper:** 125k minimum-bias pool; the detector simulation of arXiv:1612.00850 App. A (energy loss, bremsstrahlung, endcaps); tracking-efficiency removal.
- **Ours:** 20k pool; helix in the 8-layer barrel; no energy loss, bremsstrahlung or endcaps.
- **Rates:**
  - 4/8 rate: literal ~0.7%, frozen 1.18%.
  - 8/8 relaxed control: compatible with 6e-5.
  - Full signal region: 0 events, consistent with the paper's statement of no background.
- **Class:** MODEL-SYST plus UNDOCUMENTED. The 4/8 definition ("a plane") does not say whether it uses seeds or full candidates. Final numbers are in `PILEUP_BACKGROUND_RESULTS.md`.

## U7. Conversion background cross-section: 0.231 pb (project) vs ~1 pb (paper)
- **Paper:** Z(νν)γ+j, MET > 200 GeV, pT(γ) > 0.5 GeV, σ ~ 1 pb. A ~1% beam-pipe conversion gives ~10 fb.
- **Ours:** σ = 0.2310512 pb (MG5 run with the paper's cuts). A factor ≈ 4.3 is unexplained; the generator cuts beyond those stated are undocumented.
- **Handling:** yields are given separately for (A) project σ, (B) the paper's 1 pb, (C) conversion probability, and (D) detector/SR efficiency. **σ is never forced to 1 pb.**
- **Class:** UNDOCUMENTED.

## U8. Conversion probability 1%
- PDG 2016 Figs. 33.16/33.17 require the beam-pipe material and thickness, which the paper does not state. 1% is DERIVED from the paper's own "~1 pb → ~10 fb".
- **Class:** DERIVED DIRECTLY (from the paper's own numbers).

## U9. Paper sample sizes and uncertainties
- No raw counts or uncertainties are published. Fig. 5 histogram quantisation implies about 1075 (EW) and 525 (colored) reconstructed events.
- All p-values treat the paper's central value as exact. The two-sample comparison using the inferred N is in `tables/paper_project_comparison.csv`.
- **Class:** STAT.

## U10. Smaller inferred items
- **IBL radius and length:** not in the paper or ref. [27]; INFERRED from paper Fig. 4 hit spacing.
- **Location of the 25 ns cut:** INFERRED (tracker crossings).
- **Neighbour-merging adjacency:** INFERRED (8-neighbour, transitive, centroid).
- **Gaussian form of the SCT smearing:** INFERRED.
- **Generator values** (xqcut 30, qCut 45, nJetMax 1, NN23LO1, 13 TeV): UNDOCUMENTED in the paper; frozen sample values are used.
- **Colored R-hadron charge model:** both hadrons need non-zero charge (paper-stated); the hadronisation fractions are Pythia defaults (UNDOCUMENTED).
