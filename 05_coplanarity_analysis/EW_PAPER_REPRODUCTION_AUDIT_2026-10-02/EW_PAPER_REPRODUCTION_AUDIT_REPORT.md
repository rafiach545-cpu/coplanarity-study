# EW Quirk Paper-Reproduction Audit — arXiv:1708.02243v2

Date: 2026-10-02. Machine: DESKTOP-OD6H911. Benchmark: EW (Drell-Yan) quirk, mQ = 800 GeV, Λ = 4 keV.
Paper Table I: ε_trig = 0.10, ε_fid = 0.28, ε_reco(Λ=4 keV) = 0.72.

This is a fresh, independent audit. No cuts or generator settings were tuned. No new events were generated. No frozen raw sample, Figure 6 file, existing report or checkpoint was modified. Nothing was committed or pushed. All outputs are in this directory.

---

## FINAL VERDICT: **MIXED CAUSES**

| Quantity | Project | Paper | Per-quantity verdict | Evidence strength |
|---|---|---|---|---|
| **ε_fid** | 40/89 = 0.449; 94/186 = 0.505 | 0.28 | **VERIFIED IMPLEMENTATION DIFFERENCE (partial).** See note below. | The difference is verified in code and its effect replayed event by event, with exact reproduction of the stored flags (89/89, 186/186). That the paper used a finite barrel is an inference. |
| **ε_trig** | 89/511 = 0.174; 186/1045 = 0.178 | 0.10 | **PAPER SETTING UNDOCUMENTED / UNRESOLVED.** No verified implementation difference found. Not a statistical fluctuation (p = 2.8×10⁻⁷ and 1.8×10⁻¹⁴). | The definition matches the paper's text exactly. The same pipeline and definition reproduce the paper's colored value of 0.24. |

Note on ε_fid: the project models the barrel as an **origin-measured |η|<1.8 cone on infinite cylinders**. The paper builds its detector from the cited ATLAS reference, whose barrel layers have finite length. With finite ATLAS barrel half-lengths, the fiducial efficiency falls to 33/89 = 0.371 and 62/186 = 0.333 (pooled 95/275 = 0.345). That closes about 70% of the pooled gap. The residual is not significant per sample (p = 0.059, 0.12) and marginal pooled (p = 0.019).

Nothing in this audit makes the project's numbers "consistent" by tuning. The finite-barrel numbers come from the detector specification the paper cites, applied to unchanged events. They are a demonstrated sensitivity, not an adopted change.

---

## 1. Paper re-read (primary sources)

Sources are archived in `paper_source/` with SHA-256 sums: the v2 PDF (10 pages, "arXiv:1708.02243v2 [hep-ph] 13 Nov 2017"), the arXiv LaTeX source `quirks_prd_v2.tex`, the `.bbl`, and the PDF text extraction. The text below was read from the LaTeX source and cross-checked against the rendered PDF.

| Item | Paper text (verbatim where quoted) | Status |
|---|---|---|
| Sec. III A, generation | "We generate signal samples of vector-like fermions with up to 1 jet using MadGraph5_aMC@NLO [24,25], which is subsequently matched using Pythia8 [21, 26]. For electroweak production the quirks are taken to have unit charge and are produced in Drell-Yan…" | Paper-confirmed: ≤1 extra jet, MG5 + Pythia8 matching, unit charge, DY. |
| Generator versions | `%MG5 v2.3.3` and `%Pythia 8.212` appear **only as LaTeX comments** directly above Sec. III A. They are absent from the rendered PDF (0 occurrences). | Authors' source, not published text. |
| √s, PDF, tune, xqcut/qCut, matching scheme, μR/μF, generator-level cuts | **Not stated anywhere** in text, footnotes, captions or appendix. | **Undocumented.** |
| Sec. III A, detector | "We hereby use the parameters of the various detector elements as specified in [27]" ([27] = ATL-PHYS-PUB-2009-002, *Expected Performance of the ATLAS Inner Detector*, Aug 2008). "…we only included the barrel of the pixel and SCT detectors in our simulations, which effectively restricts the fiducial range to \|η\|≲1.8." "…a uniform, gaussian smearing with width 45 mm to the z-coordinates of all the hits…" | Paper-confirmed. The \|η\|≲1.8 is described as a **consequence** of barrel-only geometry, not as an explicit cut. |
| Sec. III B, trigger | "we therefore impose a p_T > 200 GeV cut on the center mass momentum of the quirk/anti-quirk system." | Paper-confirmed definition. No denominator, generator level, or strict/non-strict boundary is stated. |
| Sec. III C | 8 layers "following the ATLAS pixel layers and SCT"; primary vertex "located at the origin" for the fit | Paper-confirmed. |
| Sec. IV, ε_fid | "The fiducial efficiency parametrizes the likelihood that each quirk intersect with each layer at least once, in events passing the trigger. We also include a 25 ns timing cut…" | Paper-confirmed: denominator = trigger-passing events. |
| Sec. IV, ε_reco | "…efficiency of our algorithm in finding quirks which satisfy both the trigger and fiducial requirements." Earlier in Sec. IV, after listing the three signal-region cuts: "…the reconstruction efficiency for **these cuts** can be as high as ∼73%." | Denominator = trigger ∧ fiducial. The numerator wording links ~73% to the full signal-region cuts (see §9). |
| Eq. (12) | ε = ε_trig × ε_fid × ε_reco | Confirmed as Eq. (12) in the rendered PDF. |
| Table I and caption | DY: ε_trig 0.10, ε_fid 0.28, ε_reco 0.11/0.41/0.65/0.72/0.74 for Λ = 1–5 keV. "ε_trig and ε_fid are independent of Λ, the latter with the exception of small edge effects." | Confirmed (PDF + source). |
| **Earlier draft of Table I** (commented out in the source) | DY ε_trig = **0.03**, QCD ε_trig = **0.21**, ε_fid 0.27–0.28 | The authors revised DY ε_trig by a factor of 3.3 between drafts with no stated reason. This is evidence that the EW trigger number was not stable in the authors' own workflow; it says nothing about the final settings. |
| Appendix A | dE/dx only; no generation details. | — |

## 2. Raw recount (event-level; no cached summaries)

`scripts/01_raw_event_recount.py` parses `unweighted_events.lhe.gz` and `tag_1_pythia8_events.hepmc.gz` directly. It uses only the standard library, and maps each HepMC event to its LHE event via the status-23 quirk momenta. `scripts/04_counts_and_statistics.py` joins the project's per-event fiducial/plane/final CSVs to the raw trigger set and **asserts set equality** (closure).

| Stage | EW 1000 | EW 2000 | Source |
|---|---|---|---|
| generated (LHE events) | **1000** | **2000** | LHE |
| matched (HepMC events after Pythia MLM veto; each has exactly 2 final-state quirks) | **511** | **1045** | HepMC |
| trigger: final status-1 quirk-pair pT > 200 GeV | **89** | **186** | HepMC |
| fiducial | **40** | **94** | per-event CSV (closure OK) |
| fiducial ∧ plane | **32** | **75** | per-event CSV |
| fiducial ∧ final Sec. IV | **6** | **21** | per-event CSV |
| plane found in any trigger event (**stale 84/94 numerator**) | 32 | 84 | 9 of the 84 are **non-fiducial** events, so 84/94 mixes populations. **Rejected.** 75/94 is used. |
| technical exceptions counted as non-fiducial | 0 | 2 (rows 103, 175) | see §5 |

Raw file hashes (SHA-256): EW1000 LHE `75999899…e04e`, HepMC `d94c83d6…769a`; EW2000 LHE `d900abbf…6b5`, HepMC `a703b339…29d3`. Full values are in `tables/raw_recount_summary.json`.

Denominators were verified exactly as specified: matching = matched/generated; trigger = trigger/matched; fiducial = fiducial/trigger; plane = (fid ∧ plane)/fid; Sec. IV = (fid ∧ final)/fid.

## 3. Trigger audit

### 3.1 Definition check (all verified from raw HepMC)

- **Status codes.** The quirks appear as status 23 (hard process), 44 (shower-recoil copies) and 1 (final). The trigger uses **status 1**. The last status-44 copy agrees with status 1 to within 6.7 GeV in pair pT.
- **Units.** `U GEV MM` in both files.
- **Boundary.** Strict `>200` and `≥200` give identical counts (89, 186). Exactly one event lies within 1 GeV of threshold (200.03 GeV, EW2000, passes).
- **Event selection.** The HepMC files contain only events that survived the MLM veto, all with 2 final quirks. No weighting: every LHE event has the same weight (unweighted LO), so counting is correct.
- **Pre- vs post-shower** (sensitivity only; the paper does not say which level):

| Variant (denominator = matched) | EW 1000 | EW 2000 | vs paper 0.10 |
|---|---|---|---|
| T0 final status-1 pair pT > 200 (**project = paper text**) | 89/511 = 0.174 | 186/1045 = 0.178 | p = 2.8e-7 / 1.8e-14 |
| T2 hard-process (status-23, pre-shower) pair pT > 200 | 64/511 = 0.125 | 121/1045 = 0.116 | p = 0.065 / 0.089 |
| T4 visible-recoil proxy, \|η\|<4.9 (MET-like) | 90/511 = 0.176 | 187/1045 = 0.179 | — |

T2 is closer to 0.10, but it uses the quirk momenta *before* ISR recoil, which is unphysical as a trigger quantity. Nothing in the paper indicates that choice. It is reported as a sensitivity and **not** claimed as the cause.

### 3.2 Generator configuration (project vs paper)

| Setting | Project (both samples, identical cards; only seed and nevents differ) | Paper |
|---|---|---|
| Hard process | `p p > qe+ qe- @0` + `p p > qe+ qe- j @1`, 4-flavour p/j | "up to 1 jet": **consistent** |
| Matching | MLM, `ickkw=1`, `xqcut=30`, `ptj=20` (auto), Pythia `JetMatching:qCut=45`, `nJetMax=1`, `scheme=1`, `setMad=off`, `doShowerKt=off` | matching via Pythia8: values **undocumented** |
| PDF | `nn23lo1` (lhaid 230000) | undocumented |
| μR/μF | dynamical, `dynamical_scale_choice=-1` (CKKW clustering), `scalefact=1` | undocumented |
| √s | 13 TeV (`ebeam 6500`) | **undocumented.** 13 TeV is an inference from the Run-2 trigger discussion. |
| Generator-level cuts on quirks | none (`pt_min_pdg={}`, `eta_max_pdg={}`) | none stated |
| Versions | MG5_aMC 3.7.3; Pythia 8.317 (default `Tune:pp=14`, Monash) | LaTeX comments only: MG5 2.3.3, Pythia 8.212 |
| Matching health | 0 JetMatching errors/warnings in either log | — |

**Matching efficiency by LHE multiplicity** (raw): 0-jet 232/497 (EW1000), 471/1012 (EW2000); 1-jet 278/503, 571/988.

**Origin of trigger events:** 89/89 (EW1000) and 184/185 mapped (EW2000) come from the **1-jet matrix-element sample**. The pT > 200 GeV tail is therefore set by the 1-jet ME. The merging parameters act mainly on the relative 0-jet/1-jet normalisation of the matched sample. Moving 17.7% to 10% would need a ~44% relative change in the 1-jet share of the matched sample. That has **not been demonstrated** for any setting.

### 3.3 Cross-checks that constrain explanations

| Test | Result | Implication |
|---|---|---|
| Fisher EW1000 vs EW2000 (trigger) | p = 0.89 | Stable between independent seeds. |
| Pooled trigger | 275/1556 = 0.177, Wilson95 [0.159, 0.196], p = 2.9e-20 vs 0.10 | **Not a statistical fluctuation.** |
| **Colored benchmark** (mQ = 1800, raw independent parse, same definition, denominator = matched) | 101/419 = **0.241**; 207/873 = **0.237** | Matches paper 0.24 (p = 0.95, 0.87). The definition and denominator convention reproduce the paper where the generator setup is less in doubt. |
| "Generated-events denominator" hypothesis | EW: 89/1000 = 0.089, 186/2000 = 0.093 (compatible with 0.10). Colored: 0.101, 0.104 (vs paper 0.24, p ≈ 1e-29). | **No single denominator convention reproduces both paper values.** The EW match is numerically compatible but inconsistent with the colored row, so it is **not** a demonstrated cause. |

**Conclusion on trigger: UNRESOLVED.** The project's trigger implementation matches the paper's text. The discrepancy is EW-specific, statistically overwhelming and seed-stable. None of the undocumented settings (√s, PDF, merging scales, versions, tune) is pinned by the paper, so none can be shown to be the cause from existing events.

## 4. Fiducial audit

### 4.1 Implementation (code-verified)

`04_detector_sim/trajectory_to_hits.py` + `atlas_geometry.py`:

- 8 barrel layers at r = 3.325, 5.05, 8.85, 12.25, 29.9, 37.1, 44.3, 51.4 cm, modelled as **infinite cylinders**. A crossing is the first outward crossing of each radius, found by linear interpolation on the integrated trajectory.
- A hit is kept only if **\|η\| < 1.8**, with η computed from the **nominal origin** at the crossing point (`FIDUCIAL_ETA_MAX = 1.8`, line 389). **There is no finite-z boundary.**
- Vertex: z0 ~ N(0, 4.5 cm), drawn once per event and shared by both quirks.
- Fiducial = 16 pre-merge hits (2 quirks × 8 layers) **and** max hit time < 25 ns.
- Event-level `n_premerge == 16` equals the paper's "each quirk intersects each layer at least once" under the first-crossing-only rule. Re-crossings are never counted, so loopers are not excluded by the `== 16` test.

### 4.2 Replay on existing events (`scripts/02_fiducial_replay.py`)

Method:

- The project's own unmodified propagator is used (`simulate_quirk_hits` + `integrate_trajectory_fast_v2`), called with vertex z0 = 0. The equation of motion with uniform B along z is exactly invariant under z translation, so true crossings = z0 = 0 crossings + z0.
- The project's z0 is recovered exactly:
  - EW2000: from the stored per-event seed.
  - EW1000: by replaying the single sequential `default_rng(4242)` stream (1 draw for z0, then 2 draws per accepted SCT hit).

Validation: the reproduced baseline equals the stored `truth_fiducial` on **89/89 (EW1000), 186/186 (EW2000) and 68/68 (colored 2000)** events.

Acceptance variants evaluated on identical crossings (denominator = trigger):

| Variant | EW 1000 | EW 2000 | EW pooled | Colored 2000 (cross-check) |
|---|---|---|---|---|
| A: project baseline (origin-η < 1.8 cone, 25 ns) | 40/89 = 0.449 | 94/186 = 0.505 | 134/275 = 0.487 (p = 4e-13) | 25/68 = 0.368 |
| **B: finite ATLAS barrel** \|z\|<33.0 (IBL) / 40.05 (pixel) / 74.9 (SCT) cm, 25 ns | **33/89 = 0.371** (p = 0.059) | **62/186 = 0.333** (p = 0.12) | **95/275 = 0.345** (Wilson95 [0.292, 0.403], p = 0.019) | 22/68 = 0.324 (p = 0.42) |
| B2: as B, SCT half-length 80 cm | 34/89 = 0.382 | 64/186 = 0.344 | — | 22/68 |
| B0: as B, no vertex smearing | 33/89 | 64/186 | — | 21/68 |
| C: η<1.8 cone **and** finite barrel | 30/89 = 0.337 | 60/186 = 0.323 | 90/275 = 0.327 (p = 0.093) | 19/68 = 0.279 |
| A0: project cone, no vertex smearing | 51/89 = 0.573 | 107/186 = 0.575 | — | 29/68 = 0.426 |
| Geometric only (cone, no timing) | 41/89 | 95/186 | — | 28/68 |

p-values are exact two-sided binomial vs 0.28. Variant C is shown for completeness only; the paper does not describe applying both.

**Mechanism** (`logs/05_transition_matrix.log`):

- **Kept by the cone, rejected by the real barrel (EW: 10 + 34 events):** pairs at \|η_pair\| = 1.21–1.85. Their outer-SCT crossings lie at \|z\| = 77–149 cm, beyond the 74.9 cm SCT barrel. A \|η\|<1.8 cone at r = 51.4 cm admits \|z\| up to ≈151 cm, about twice the real SCT barrel. Requiring all 8 real barrel layers implies an effective \|η_pair\| ≲ 1.2.
- **Rejected by the cone, kept by the real barrel (EW: 3 + 2 events):** central pairs with \|z0\| = 5.6–8.5 cm. Measured from the origin, their IBL/pixel crossings exceed \|η\| = 1.8, although they lie well inside the 33–40 cm inner barrels. This is an artefact of combining an origin-measured cone with a smeared vertex. It is also why vertex smearing alone moves the cone result by 11–13 events (A0 vs A), but moves the finite-barrel result by at most 2.
- The crossing-point η follows the **pair** direction, not the individual quirk's production η: the median of max\|η_cross\| − \|η_pair\| is 0.05 (EW1000, EW2000). Bound quirks travel together, so production-level single-quirk η is the wrong acceptance proxy.
- Timing (25 ns) removes 1 event per EW sample. That is consistent with the paper's "slight drop".
- Numerical limits and root finding: all 16 crossings exist for every replayed event except the one technical exception. There was no root-finding failure. Integration limits are sized on transverse β to reach r = 60 cm × 3.

### 4.3 Provenance of the barrel half-lengths

- **IBL:** active \|z\| < 330.15 mm, verified in arXiv:1803.00844 (IBL layout table).
- **Pixel barrel \|z\| < 400.5 mm and SCT barrel \|z\| < 749 mm:** standard ATLAS Inner Detector values (ATLAS detector paper, JINST 3 S08003). **Not re-read from ref [27] in this session:** CERN CDS returned a bot-check page to every request. Corroboration: arXiv:1704.07983 states the ID barrel has "full coverage for \|η\| ≲ 1.5" and SCT barrel strips 126 mm long. The SCT sensitivity at 80 cm (B2) changes the result by 1–2 events.
- **Ref [27] dates from 2008 and predates the IBL**, so how the paper modelled its innermost layer is unknown. The inner-layer choice barely matters for the finite-barrel result: the binding constraint is the outer SCT.

### 4.4 Is the paper's \|η\|≲1.8 compatible with a finite barrel?

Only partly. A literal all-8-real-layers requirement gives an effective \|η_pair\| ≲ 1.2, not 1.8. The paper's phrase may summarise the pixel-barrel extent or be loose. **Whether the authors used finite barrels is therefore an inference.** What is verified is:

- (i) the project departs from the finite-length geometry that the cited reference specifies;
- (ii) the size of that departure on unchanged events;
- (iii) the direction is the same for both benchmarks: EW 0.487 → 0.345, colored 0.368 → 0.324, paper 0.28 for both.

**Residual after B:** pooled EW 0.345 vs 0.28, p = 0.019. Per sample, p = 0.059 and 0.12. The fiducial efficiency is conditional on the trigger-selected population, and that population itself disagrees with the paper (§3), so a residual of this size cannot be attributed further.

## 5. Eta audit integration

- **31 targeted zero-hit EW2000 events** (from `EW_TRIGGER_FIDUCIAL_AUDIT_2026-09-28/ZERO_HIT_REPLAY`): this replay completed all 31. All 31 have 16 geometric crossings, with crossing \|η\| = 1.95–3.08, tracking \|η_pair\| = 1.79–3.05. **All 31 fail under both A and B.**
- **Event 165** (row 165, HepMC event 951), previously unresolved after a 600 s timeout: **resolved here.** All 16 crossings are at \|η\| ≈ 3.0 (η_pair = −3.02, \|z\| up to 513 cm), and it also fails timing (max t = 25.51 ns). Same mechanism as the other 30. It completed in seconds because this replay skips hit digitisation and fitting.
- **No numerical or root-finding failure demonstrated.** The two EW2000 technical exceptions are step-ceiling `RuntimeError`s in `simulate_quirk_hits`:
  - Row 175 (η_pair ≈ −2.3) also fails in this replay.
  - Row 103 (event 655) propagates here (crossing \|η\| = 2.1) and is non-fiducial under every variant.
  - Neither changes any count.
- **As required: the eta audit alone does not explain the discrepancy.** These 31 events are genuinely outside every barrel acceptance considered. The gap-relevant events are the separate 44 (EW1000 + EW2000) "cone-only" events at \|η_pair\| 1.2–1.85 described in §4.2.

## 6. Statistics (task 7)

Columns: binomial SE = √(p(1−p)/n). Wilson intervals at 68.27% and 95%. Clopper–Pearson at 95%. Exact two-sided binomial p-value vs the paper (scipy `binomtest`). Full table: `tables/efficiency_statistics.csv`.

| Sample | Efficiency | k/n | p̂ | SE | Wilson 68% | Wilson 95% | CP 95% | Paper | p (exact) |
|---|---|---|---|---|---|---|---|---|---|
| EW1000 | matching | 511/1000 | 0.5110 | 0.0158 | [0.4952, 0.5268] | [0.4800, 0.5419] | [0.4795, 0.5424] | — | — |
| EW1000 | trigger | 89/511 | 0.1742 | 0.0168 | [0.1580, 0.1916] | [0.1437, 0.2094] | [0.1423, 0.2099] | 0.10 | 2.76e-07 |
| EW1000 | fiducial | 40/89 | 0.4494 | 0.0527 | [0.3976, 0.5024] | [0.3503, 0.5527] | [0.3438, 0.5586] | 0.28 | 8.17e-04 |
| EW1000 | plane \| fid | 32/40 | 0.8000 | 0.0632 | [0.7298, 0.8556] | [0.6524, 0.8950] | [0.6435, 0.9095] | 0.72 | 2.95e-01 |
| EW1000 | Sec. IV \| fid | 6/40 | 0.1500 | 0.0565 | [0.1021, 0.2150] | [0.0706, 0.2907] | [0.0571, 0.2984] | 0.72 | 9.14e-14 |
| EW2000 | matching | 1045/2000 | 0.5225 | 0.0112 | [0.5113, 0.5337] | [0.5006, 0.5443] | [0.5003, 0.5446] | — | — |
| EW2000 | trigger | 186/1045 | 0.1780 | 0.0118 | [0.1665, 0.1901] | [0.1560, 0.2023] | [0.1553, 0.2026] | 0.10 | 1.79e-14 |
| EW2000 | fiducial | 94/186 | 0.5054 | 0.0367 | [0.4688, 0.5419] | [0.4341, 0.5764] | [0.4313, 0.5793] | 0.28 | 1.26e-10 |
| EW2000 | plane \| fid | **75/94** | 0.7979 | 0.0414 | [0.7534, 0.8361] | [0.7057, 0.8666] | [0.7025, 0.8737] | 0.72 | 1.07e-01 |
| EW2000 | Sec. IV \| fid | 21/94 | 0.2234 | 0.0430 | [0.1835, 0.2692] | [0.1510, 0.3175] | [0.1439, 0.3210] | 0.72 | 2.37e-23 |

Fisher exact test, EW1000 vs EW2000 (`tables/fisher_stability_1000_vs_2000.csv`):

| Efficiency | p (two-sided) |
|---|---|
| matching | 0.56 |
| trigger | 0.89 |
| fiducial | 0.44 |
| plane \| fid | 1.00 |
| Sec. IV \| fid | 0.48 |

**All stable between samples.**

## 7. Quantitative answer to task 8

| Question | Answer |
|---|---|
| Can any **verified** implementation difference move the trigger from 17.5–17.8% toward 10%? | **No.** None was found. The definition, status level, units, boundary, event selection, weights and denominator match the paper's text, and the colored row validates the convention. Undocumented-setting and denominator hypotheses are not demonstrated, and the denominator one contradicts the colored row. |
| Can any verified implementation difference move the fiducial from 45–51% toward 28%? | **Partly, yes.** Replacing the origin-η cone with the cited finite barrel gives 37.1% / 33.3% (pooled 34.5%), about 70% of the gap. Residual: p = 0.019 pooled, not significant per sample. |

## 8. New simulation (tasks 9–10)

No new events were generated. The fiducial result needed none: it is a geometry change applied to existing events.

For the trigger, the only generator information traceable to the authors is the commented `MG5 v2.3.3` / `Pythia 8.212`. It is not published text, and it does not fix PDF, merging scales, √s or tune. A controlled, version-matched pilot is described in `CONTROLLED_REPRODUCTION_PLAN.md`. It is **not launched** and needs your approval. It would test only the version hypothesis, and every other setting would remain an explicitly labelled assumption.

## 9. Out-of-scope observation (flagged, not resolved)

The paper ties "∼73%" to "**these cuts**", i.e. the three signal-region cuts (plane found, hit multiplicity, Δw<1 cm and Δs<0.01 cm). Table I's 0.72 at Λ = 4 keV is the same quantity.

- Project plane | fid = 0.80 / 0.80 agrees with 0.72 (p = 0.30, 0.11).
- Project full Sec. IV | fid = 0.15 / 0.22 disagrees strongly (p ≈ 1e-13, 1e-23).

Which project quantity is the like-for-like comparison to Table I ε_reco should be re-examined separately. This audit used 75/94 as instructed.

## 10. Recommendations (no action taken)

1. Decide explicitly whether the detector model should use finite barrel half-lengths (paper-cited geometry) or keep the \|η\|<1.8 cone. Figure 6 production is mid-run with the cone model, so a change would require recomputing completed cells. That decision is yours.
2. Keep the trigger discrepancy labelled UNRESOLVED in reports. Do not present the generated-denominator or pre-shower numbers as explanations.
3. If the version-matched pilot is approved, run it in an isolated directory with the validation gates in `CONTROLLED_REPRODUCTION_PLAN.md` before any large sample.

## File index

- `scripts/01_raw_event_recount.py`: raw LHE/HepMC parse → `tables/EW{1000,2000}_{lhe,hepmc}_events.csv`, `tables/raw_recount_summary.json`
- `scripts/02_fiducial_replay.py`: propagation replay and acceptance variants → `tables/*_layer_crossings_vertex_relative.csv`, `tables/*_fiducial_variants_per_event.csv`, `*_summary.json`, `EW2000_technical_exceptions.json`
- `scripts/03_trigger_variants_and_colored_crosscheck.py` → `tables/trigger_variants_summary.json`
- `scripts/04_counts_and_statistics.py` → `tables/stage_counts_recomputed.json`, `tables/efficiency_statistics.csv`, `tables/fisher_stability_1000_vs_2000.csv`
- `tables/descriptive_pair_eta_threshold_scan.csv`: descriptive only, not a proposed cut
- `logs/`: stdout of every script
- `paper_source/`: PDF, LaTeX source, bbl, text extraction, SHA256SUMS
- `SHA256_MANIFEST.txt`: hashes of every output

Environment: conda env `hep` (Python 3.11.16, numpy 2.4.6, scipy 1.17.1, pandas 3.0.5) on DESKTOP-OD6H911.
