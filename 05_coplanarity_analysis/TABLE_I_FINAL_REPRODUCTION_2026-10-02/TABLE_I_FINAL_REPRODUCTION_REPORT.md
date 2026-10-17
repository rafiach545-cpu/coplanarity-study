# Table I Efficiency Reproduction — Final Report (for approval)

Paper: S. Knapen, H. K. Lou, M. Papucci, J. Setford, "Tracking down Quirks at the Large Hadron Collider", arXiv:1708.02243v2.
Date: 2026-10-02. Machine: DESKTOP-OD6H911.
Scope: Table I only. **Figure 6 was not touched.** Nothing was deleted, overwritten, committed or pushed.

---

## 1. Final configuration

| Stage | Final choice | Status |
|---|---|---|
| Hard process | `p p > Q Q̄` + `p p > Q Q̄ j` (up to 1 jet); EW: unit-charge vector-like fermion, Drell-Yan; colored: QCD only, 1800 GeV | **paper** |
| Generator / shower | MadGraph5_aMC@NLO + Pythia8 MLM matching (MG5 3.7.3, Pythia 8.317) | paper (tools); versions inferred |
| Matching settings | xqcut 30 GeV, qCut 45 GeV, nJetMax 1, MLM scheme 1, NN23LO1 PDF, CKKW dynamical scale, 13 TeV | **undocumented in the paper**; project values (frozen) |
| Λ, mass | EW: m_Q 800 GeV, Λ 4 keV; colored: m_Q 1800 GeV, Λ 2 keV | **paper** |
| Trigger | pT of the quirk/anti-quirk centre-of-mass system > 200 GeV; denominator = matched events | **paper** (definition); denominator inferred |
| Colored charge requirement | both quirk-hadrons with non-zero electric charge (applied after trigger, before fiducial) | **paper** wording; placement inferred |
| Trajectories | Nambu-Goto straight-string EOM + Lorentz force, uniform B = 2 T, first outward crossing per layer | **paper** |
| Detector | 8 barrel layers (IBL, 3 pixel, 4 SCT), Run-2 radii | paper ("8 layers"); radii from ATLAS documents |
| Fiducial geometry | finite ATLAS barrel half-lengths (IBL 33.0 cm, pixel 40.05 cm, SCT 74.9 cm); all 16 crossings; max hit time < 25 ns | paper says "only included the barrel"; lengths from ATLAS JINST 3 S08003 / arXiv:1803.00844 (**inferred**) |
| Beam spot | Gaussian z shift, σ = 45 mm | **paper** |
| Pixel response | hit at the centre of the hit pixel (50×400 µm; IBL 50×250 µm); neighbouring pixels merged | **paper** |
| SCT response | **corrected**: Gaussian R-φ smearing σ_Rφ = 2 × 17 µm = 34 µm; z not smeared (§4) | paper (2 × intrinsic accuracy) + ATLAS JINST (17 µm); z treatment **inferred** from paper Fig. 5 |
| Reconstruction | Sec. III C algorithm exactly as written (project `coplanarity_fit.py`, unmodified) | **paper** |
| ε_reco | full Sec. IV signal region (plane, hit multiplicity, Δw < 1 cm, Δs < 0.01 cm) / (trigger ∧ fiducial) | **paper** (§5) |

## 2. Statistical method

- **Primary interval:** Wilson score 95%, a binomial interval with good coverage at small N. Clopper–Pearson exact 95% is also reported.
- **Consistency test:** exact two-sided binomial p-value against the published value.
- **"Paper inside 95% CI"** refers to the Wilson interval.
- **Primary result** (declared before tabulation): all available samples pooled per benchmark, with no sample selection.
  - EW = EW1000 + EW2000 (frozen) + G0_EW (independent MG5 seed 9101).
  - Colored = COL1000 + COL2000 (frozen) + G0_COL (independent MG5 seed 9201).

## 3. Comparison with Table I

### 3.1 Primary result (pooled)

| Benchmark | Quantity | N_pass | N_total | Our efficiency | 95% CI (Wilson) | Paper | Paper inside 95% CI? | Notes |
|---|---|---|---|---|---|---|---|---|
| EW | trigger | 462 | 2657 | 0.174 | [0.160, 0.189] | 0.10 | **no** (p = 3e-31) | pair pT > 200 / matched; no defensible setting found that reaches 0.10 (§6) |
| EW | fiducial | 152 | 462 | 0.329 | [0.288, 0.373] | 0.28 | **no, marginal** (p = 0.022) | each sample alone contains 0.28 (0.371, 0.328, 0.310); see §8 |
| EW | reconstruction | 114 | 152 | 0.750 | [0.676, 0.812] | 0.72 | **yes** (p = 0.47) | full Sec. IV SR / (trigger ∧ fiducial) |
| Colored | trigger | 494 | 2147 | 0.230 | [0.213, 0.248] | 0.24 | **yes** (p = 0.29) | before charge requirement |
| Colored | fiducial | 41 | 146 | 0.281 | [0.214, 0.359] | 0.28 | **yes** (p = 1.0) | denominator = trigger ∧ both R-hadrons charged |
| Colored | reconstruction | 21 | 41 | 0.512 | [0.365, 0.657] | 0.35 | **no, marginal** (p = 0.034) | small N; per sample 5/6, 7/21, 9/14 |

### 3.2 Per sample (Wilson 95% and Clopper–Pearson 95%)

| Benchmark | Sample | Quantity | N_pass | N_total | Eff. | Wilson 95% | CP 95% | Paper | Inside (Wilson)? | p |
|---|---|---|---|---|---|---|---|---|---|---|
| EW | EW1000 | trigger | 89 | 511 | 0.174 | [0.144, 0.209] | [0.142, 0.210] | 0.10 | no | 2.8e-07 |
| EW | EW1000 | fiducial | 33 | 89 | 0.371 | [0.278, 0.475] | [0.271, 0.480] | 0.28 | YES | 0.059 |
| EW | EW1000 | reconstruction | 28 | 33 | 0.848 | [0.691, 0.933] | [0.681, 0.949] | 0.72 | YES | 0.12 |
| EW | EW2000 | trigger | 186 | 1045 | 0.178 | [0.156, 0.202] | [0.155, 0.203] | 0.10 | no | 1.8e-14 |
| EW | EW2000 | fiducial | 61 | 186 | 0.328 | [0.265, 0.398] | [0.261, 0.400] | 0.28 | YES | 0.16 |
| EW | EW2000 | reconstruction | 41 | 61 | 0.672 | [0.547, 0.777] | [0.540, 0.787] | 0.72 | YES | 0.4 |
| EW | G0_EW | trigger | 187 | 1101 | 0.170 | [0.149, 0.193] | [0.148, 0.193] | 0.10 | no | 1.3e-12 |
| EW | G0_EW | fiducial | 58 | 187 | 0.310 | [0.248, 0.380] | [0.245, 0.382] | 0.28 | YES | 0.37 |
| EW | G0_EW | reconstruction | 45 | 58 | 0.776 | [0.653, 0.864] | [0.647, 0.875] | 0.72 | YES | 0.38 |
| Colored | COL1000 | trigger | 101 | 419 | 0.241 | [0.203, 0.284] | [0.201, 0.285] | 0.24 | YES | 0.95 |
| Colored | COL1000 | fiducial | 6 | 27 | 0.222 | [0.106, 0.408] | [0.086, 0.423] | 0.28 | YES | 0.67 |
| Colored | COL1000 | reconstruction | 5 | 6 | 0.833 | [0.436, 0.970] | [0.359, 0.996] | 0.35 | no | 0.022 |
| Colored | COL2000 | trigger | 207 | 873 | 0.237 | [0.210, 0.266] | [0.209, 0.267] | 0.24 | YES | 0.87 |
| Colored | COL2000 | fiducial | 21 | 68 | 0.309 | [0.212, 0.426] | [0.202, 0.433] | 0.28 | YES | 0.59 |
| Colored | COL2000 | reconstruction | 7 | 21 | 0.333 | [0.172, 0.546] | [0.146, 0.570] | 0.35 | YES | 1 |
| Colored | G0_COL | trigger | 186 | 855 | 0.218 | [0.191, 0.246] | [0.190, 0.247] | 0.24 | YES | 0.13 |
| Colored | G0_COL | fiducial | 14 | 51 | 0.275 | [0.171, 0.409] | [0.159, 0.417] | 0.28 | YES | 1 |
| Colored | G0_COL | reconstruction | 9 | 14 | 0.643 | [0.388, 0.837] | [0.351, 0.872] | 0.35 | no | 0.045 |

Technical propagation exceptions (step-ceiling RuntimeError) stay in the trigger denominators and count as non-fiducial, as in the project: EW2000 1, G0_EW 1, COL2000 2.

## 4. Corrected SCT smearing (implemented consistently in every final number)

Full description: `notes/SCT_SMEARING_IMPLEMENTATION.md`.

| | Pixel | SCT R-φ | SCT z |
|---|---|---|---|
| Previous (rejected) | pixel-centre quantization | σ_Rφ = 34 µm | σ_z = 1160 µm (2 × 580 µm) |
| **Final (corrected)** | pixel-centre quantization | **σ_Rφ = 34 µm** (2 × 17 µm) | **not smeared** |

Why the change:
- Planes fitted to unsmeared crossings have a median Δs of 4–13 µm.
- The paper's own Fig. 5 (signal Δs median ≈ 28 µm EW / 35 µm colored, ≈ 90% below 0.01 cm) is incompatible with σ_z = 1.16 mm (KS p ≈ 0, both benchmarks). That model produced a median Δs of 150 µm and was responsible for the 0.15–0.22 / 0.12 reconstruction efficiencies.
- The R-φ-only treatment (z unsmeared) and the isotropic 34 µm treatment are both compatible with the colored Fig. 5 distribution, and Fig. 5 cannot separate them.
- The z-unsmeared version was chosen; that choice was informed by Table I (§9).

## 5. Reconstruction efficiency definition (re-checked)

Paper text (v2 source, verbatim):
1. Sec. IV lists the signal region: "1. At least one plane reconstructed under the tracking algorithm 2. All but one layer must contain 2 hits, the remaining layer must contain at least 1 hit 3. Δw < 1.0 cm and Δs < 0.01 cm".
2. It continues: "…if the quirks pass through all 8-layers, **the reconstruction efficiency for these cuts** can be as high as ∼73%."
3. "The reconstruction efficiency is defined as the efficiency of our algorithm in finding quirks which satisfy both the trigger and fiducial requirements."
4. Eq. (12): ε = ε_trig × ε_fid × ε_reco is the **total** signal efficiency used for the background-free 3/5-event contours.

**Denominator:** trigger ∧ fiducial events. **Numerator:** events passing the complete Sec. IV signal region. Both definitions in this report use these.

With the corrected SCT treatment, plane-finding alone (152/152 EW, 34/41 colored) would overshoot the paper. The full-SR values (0.750 EW, 0.512 colored) are the like-for-like comparison.

## 6. EW trigger efficiency — first-principles audit

| Check | Finding |
|---|---|
| Definition (paper) | "we impose a p_T > 200 GeV cut on the center mass momentum of the quirk/anti-quirk system". The paper gives **no** jet definition, jet radius, jet threshold, η acceptance or leading-jet cut, and no generator-level cut. |
| Numerator | final-state (status 1) quirk four-momenta, vector-summed; strict > 200 GeV. Hard-process and status-44 copies were checked. Units GeV. One event within 1 GeV of threshold (200.03, passes). |
| Denominator | matched events = events surviving the Pythia MLM veto (= events written). The same convention reproduces colored 0.24 (0.230 pooled). |
| Generated / showered / matched | every LHE event is showered; MLM accepts 51–55% (EW) and 41–44% (colored); no showering failures; 0 JetMatching errors. |
| Generator-level cuts | none on quirks; jets: ptj 20 GeV (auto, from xqcut 30). |
| MET | visible MET (\|η\| < 4.9, quirks/R-hadrons and neutrinos invisible) = 0.176 EW / 0.234 COL, identical to the paper definition (0.177 / 0.235). |
| Jet-based alternatives (not in paper) | anti-kT R = 0.4 leading jet > 200 GeV (\|η\| < 4.5 or < 2.8): 0.131 EW / 0.187 COL; MET ∧ leading jet: 0.124 / 0.177. Both benchmarks fall together. |
| ISR / matching / PDF / scale / tune / √s / multiplicity | 19 one-setting variations (`PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02`, Part B): EW 0.130–0.182, never compatible with 0.10; colored 0.19–0.28. |
| Generator versions | MG5 2.3.3 + Pythia 8.212 (named only in the paper's LaTeX comments): EW 0.167. |
| EW/colored trigger ratio | ours 0.60–0.84 in every variant; paper 0.42. **No single change lowers EW without lowering colored.** |
| Denominator alternatives | trigger/generated gives EW 0.09 (≈0.10) but colored 0.10 (paper 0.24), so it is rejected. |

**Conclusion:**
- The EW trigger efficiency is inconsistent with Table I under every defensible definition and setting.
- The colored trigger is reproduced by the same definition.
- The difference must come from an EW-specific, paper-undocumented generation or trigger setup.
- The paper's own draft table, commented out in the arXiv source, had EW ε_trig = 0.03, a further sign that this number was unstable in the authors' workflow.

## 7. Detailed cutflows (final configuration)

### EW (m_Q = 800 GeV, Λ = 4 keV)

| Stage | EW1000 | EW2000 | G0_EW | Pooled |
|---|---|---|---|---|
| generated (LHE events) | 1000 | 2000 | 2000 | 5000 |
| showered (all LHE events passed to Pythia8) | 1000 | 2000 | 2000 | 5000 |
| matched (MLM-accepted) | 511 | 1045 | 1101 | 2657 |
| trigger: pair pT > 200 GeV | 89 | 186 | 187 | 462 |
| fiducial (finite barrel, 16 crossings, t < 25 ns) | 33 | 61 | 58 | 152 |
| plane found (Sec. III C) | 33 | 61 | 58 | 152 |
| hit multiplicity (SR cut 2) | 28 | 41 | 45 | 114 |
| Δw < 1 cm (SR cut 3a) | 28 | 41 | 45 | 114 |
| Δs < 0.01 cm (SR cut 3b) | 28 | 41 | 45 | 114 |
| **final signal region** | **28** | **41** | **45** | **114** |

### Colored (m_Q = 1800 GeV, Λ = 2 keV)

| Stage | COL1000 | COL2000 | G0_COL | Pooled |
|---|---|---|---|---|
| generated (LHE events) | 1000 | 2000 | 2000 | 5000 |
| showered | 1000 | 2000 | 2000 | 5000 |
| matched (MLM-accepted) | 419 | 873 | 855 | 2147 |
| trigger: pair pT > 200 GeV | 101 | 207 | 186 | 494 |
| trigger ∧ both R-hadrons charged (non-zero) | 27 | 68 | 51 | 146 |
| fiducial (finite barrel, 16 crossings, t < 25 ns) | 6 | 21 | 14 | 41 |
| plane found (Sec. III C) | 5 | 18 | 11 | 34 |
| hit multiplicity (SR cut 2) | 5 | 7 | 9 | 21 |
| Δw < 1 cm | 5 | 7 | 9 | 21 |
| Δs < 0.01 cm | 5 | 7 | 9 | 21 |
| **final signal region** | **5** | **7** | **9** | **21** |

With the corrected SCT treatment, the only remaining reconstruction loss is the per-layer **hit multiplicity** (plus plane-finding for colored). The Δs and Δw cuts remove nothing. In the paper's Fig. 5, about 8–10% of signal lies above Δs = 0.01 cm, so our Δs is now slightly *better* than the paper's.

## 8. Systematic tests (pooled; not the final configuration)

| Geometry | SCT model | EW fid | EW reco | COL fid | COL reco |
|---|---|---|---|---|---|
| A (η-cone, project) | old σ_z = 1.16 mm | 0.476 | 0.109 | 0.404 | 0.102 |
| A | **corrected** (R-φ only) | 0.476 | **0.764 ✓** | 0.404 | 0.492 |
| A | isotropic 34 µm | 0.476 | 0.886 | 0.404 | 0.593 |
| **B (finite barrel)** | old σ_z = 1.16 mm | 0.329 | 0.099 | 0.281 ✓ | 0.049 |
| **B** | **corrected (final)** | 0.329 | **0.750 ✓** | **0.281 ✓** | 0.512 |
| B | isotropic 34 µm | 0.329 | 0.901 | 0.281 ✓ | 0.610 |

✓ = paper value inside the Wilson 95% interval. The full table with N and CI is in `tables/final_systematics_geometry_resolution.csv`.

## 9. What is stated, what is inferred, what was tested, what is unresolved

**Explicitly stated in the paper:**
- process (≤ 1 jet, MG5 + Pythia8 matching);
- unit-charge Drell-Yan (EW); QCD-only (colored);
- the trigger definition (pair pT > 200 GeV);
- 2 T uniform field; the EOM; 8 barrel layers (pixel + SCT only);
- pixel size used, with the "center of each pixel hit"; SCT "twice the intrinsic accuracy";
- neighbouring-pixel merging; 45 mm beam-spot smearing;
- 25 ns timing cut in ε_fid;
- fiducial = each quirk intersects each layer;
- the complete Sec. III C algorithm and Sec. IV signal region;
- ε_reco "for these cuts" (full SR) with denominator trigger ∧ fiducial;
- colored requires non-zero-charge quirk-hadrons.

**Inferred from the paper or detector documents:**
- intrinsic accuracies (17 µm R-φ, 580 µm z; JINST Table 4.1) and Run-2 radii;
- finite barrel half-lengths;
- the matched-event denominator for ε_trig (it reproduces the colored value);
- SCT z not smeared (the only family compatible with the paper's own Fig. 5, together with the isotropic 34 µm variant);
- placement of the colored charge requirement (between trigger and fiducial);
- generator versions (LaTeX comments only).

**Our own systematic tests:**
- η-cone vs finite barrel; three SCT models;
- 19 generator/shower variations;
- MG5 2.3.3 / Pythia 8.212;
- MET and jet trigger observables;
- the trigger/generated denominator;
- independent-seed samples.

**Unresolved:**
1. **EW trigger efficiency** (0.174 vs 0.10). There is no defensible reproduction, and the paper does not document the EW generator/trigger setup that would explain it.
2. **R-φ-only vs isotropic SCT treatment.** The paper's figure does not decide it. The final choice reproduces ε_reco for EW but was selected with knowledge of Table I. The isotropic version overshoots both benchmarks.
3. **Oscillation width Δw.** Ours is 2–5× wider than the paper's Fig. 5. Kinematics (⟨γ−1⟩) agree with the paper's Fig. 6, so the cause is not identified.
4. **Pooled EW fiducial** (0.329, p = 0.022) and **pooled colored reconstruction** (0.512, p = 0.034). Both are marginal at the 95% level.
   - With six simultaneous comparisons, a Bonferroni threshold of 0.05/6 = 0.0083 would not flag either; the EW trigger (p ≈ 1e-31) remains.
   - The EW fiducial is conditional on our trigger-selected population, which differs from the paper's (ε_trig 0.174 vs 0.10).
   - The colored reconstruction rests on 41 events.
   - These two are reported as *marginal*, not as reproduced.
5. Ref. [27] (ATL-PHYS-PUB-2009-002) could not be read; values come from the ATLAS JINST paper.

## 10. Verdict per Table I value

| Value | Verdict |
|---|---|
| EW trigger 0.10 | **Not reproduced** (0.174 [0.160, 0.189]); clearly inconsistent; no defensible fix found |
| EW fiducial 0.28 | **Marginal** (0.329 [0.288, 0.373]; every individual sample consistent) |
| EW reconstruction 0.72 | **Reproduced** (0.750 [0.676, 0.812]) |
| Colored trigger 0.24 | **Reproduced** (0.230 [0.213, 0.248]) |
| Colored fiducial 0.28 | **Reproduced** (0.281 [0.214, 0.359]) |
| Colored reconstruction 0.35 | **Marginal** (0.512 [0.365, 0.657]; small N) |

**Requested next step:** your approval or corrections of this Table I configuration. Figure 6 has not been touched and will not be until you approve. No cleanup has been done; all intermediate directories are intact (listed in §11).

## 11. Provenance

- **This report's directory** (`05_coplanarity_analysis/TABLE_I_FINAL_REPRODUCTION_2026-10-02/`):
  - `scripts/01_trigger_observable_audit.py`, `scripts/02_final_full_chain.py`, `scripts/03_final_tables.py`
  - `tables/final_table_I_comparison.csv`, `final_cutflows.csv`, `final_systematics_geometry_resolution.csv`, `trigger_observable_audit.csv`, `full_chain_per_event.csv`, `full_chain_summary.csv`
  - `notes/SCT_SMEARING_IMPLEMENTATION.md`, `notes/paper_statements_verbatim.txt`
- **Isolated generation/shower workspace:** `/home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02/` (driver v3 source and binary, `runs/V3OBS/`).
- **Earlier stages, all kept:** `EW_PAPER_REPRODUCTION_AUDIT_2026-10-02/`, `EW_PAPER_REPRODUCTION_FOLLOWUP_2026-10-02/`, `PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02/`, `/home/rafia/hep_tools/EW_VERSION_PILOT_2026-10-02/`.
- **Frozen inputs, read-only:** project per-event results, frozen LHE/HepMC.
- `SHA256_MANIFEST.txt` covers every file in this directory.

Note: verbatim quotations keep the paper's own spellings ("neightboring", "candidate plains").
