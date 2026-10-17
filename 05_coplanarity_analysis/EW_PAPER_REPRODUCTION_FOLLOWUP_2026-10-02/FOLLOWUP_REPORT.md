# EW Paper-Reproduction Follow-up — ε_reco definition, finite barrel, version-matched trigger pilot

Date: 2026-10-02. Machine: DESKTOP-OD6H911.

Scope: the three questions were closed in the order requested. Figure 6 was **not** resumed. No checkpoint, frozen sample or existing report was modified, and nothing was committed or pushed. At the end of the session these were re-verified unchanged:

- Figure 6 checkpoint SHA `aa59eaa4…`
- EW1000 LHE `75999899…`
- EW2000 LHE `d900abbf…`
- EW2000 HepMC `a703b339…`

The only new generation was a bounded MG5 2.3.3 sample (500-event pilot plus one 2000-event sample) in the isolated directory `/home/rafia/hep_tools/EW_VERSION_PILOT_2026-10-02/`.

| Question | Verdict |
|---|---|
| 1. Table I ε_reco | **B: the complete Sec. IV signal-region selection among trigger+fiducial events.** Supported by direct text and by the structure of Eq. (12) → Fig. 6. |
| 2. Finite barrel | **Not documented by the paper; unresolved.** Finite z lengths are the standard ATLAS geometry and the literal reading of "only included the barrel", but are not shown to be the authors' implementation. The paper's own "\|η\|≲1.8" does not match an all-8-finite-layer acceptance (≈1.17). Not adopted. |
| 3. Version-matched pilot | **Generator-version differences do NOT explain the EW trigger discrepancy.** MG5 2.3.3 + Pythia 8.212 gives 214/1279 = 0.167 (p = 1.2×10⁻¹³ vs 0.10; Fisher vs frozen p = 0.52). |
| Figure 6 | **Recommendation: keep both geometry models as separate systematic studies, with the existing Figure 6 run as the baseline. Gate the resume on one further audit, the Δs / hit-multiplicity loss (§1.4).** That loss, not geometry or generator version, is now the largest unexplained factor in the total efficiency. |

---

## 1. Reconstruction-efficiency definition

### 1.1 Sources

- arXiv source `https://arxiv.org/src/1708.02243` re-downloaded: identical to v2 (`quirks_prd_v2.tex`, SHA in `paper_source/SHA256SUMS.txt`).
- v1 source (`quirks_arxiv.tex`) also fetched. The Results section and Table I are **identical in v1 and v2**; only the Fig. 5 caption wording changed. Both versions contain the commented-out earlier table (DY ε_trig 0.03).

### 1.2 Every sentence linking plane finding, Sec. IV cuts, Eq. 12 and Table I

| # | Location | Verbatim (v2 source) | Points to |
|---|---|---|---|
| S1 | Sec. III C, algorithm step 3 | "Event Selection: Gather all the reconstructed lists, apply the final cut Δw < 1 cm. If there are more than one plane identified, keep the one with the smallest Δs." | Defines *a reconstructed plane* (plane finding). |
| S2 | Sec. III C, after the algorithm | "…after the plane-finding algorithm has identified a set of candidate plains, the main discriminating variables of our analysis are – (Δs)² – (Δw)² – Number of hits found" | Plane finding is *followed* by selection on Δs, Δw, N_hits. |
| S3 | Sec. III C | "…the selection cuts on these variables can be easily modified to accommodate better signal acceptance… A tighter selection will generally boost computational efficiency at a cost of reduced signal efficiency, which is what has been chosen in this work." | Signal efficiency is reduced by the *selection cuts on Δs, Δw, N_hits*. |
| S4 | Sec. IV | "Our signal region is then defined by the following cuts: 1. At least one plane reconstructed under the tracking algorithm; 2. All but one layer must contain 2 hits, the remaining layer must contain at least 1 hit; 3. Δw < 1.0 cm and Δs < 0.01 cm" | Sec. IV signal region (SR). |
| **S5** | Sec. IV, **immediately after S4** | "For a quirk signal, as long as the length scale of oscillation m_Q/Λ² is smaller than ∼1 cm, and if the quirks pass through all 8-layers, **the reconstruction efficiency for these cuts** can be as high as ∼73%." | **"Reconstruction efficiency" is attached explicitly to "these cuts", i.e. the three SR cuts.** "pass through all 8 layers" = the fiducial condition. |
| S6 | Sec. IV, Fig. 5 discussion | "Fig 5 shows the Δs and Δw distribution for background and our benchmark signal **before the final cut on those variables** are imposed." Caption: "A signal selection cut Δs < 0.01 cm is indicated." | Δs < 0.01 cm is a *signal selection* cut that applies to the benchmark signal. |
| S7 | Eq. (12) | "We factorize the **total signal efficiency** into … ε = ε_trig × ε_fid × ε_reco." | ε is the total signal efficiency. |
| S8 | Sec. IV | "The reconstruction efficiency is defined as the efficiency of our algorithm in finding quirks which satisfy both the trigger and fiducial requirements." | Denominator = trigger ∧ fiducial. "Our algorithm … finding quirks" is ambiguous on its own (see below). |
| S9 | Sec. IV | "We see that the peak ε_reco can be as high as ∼70%, while ε_reco drops at lower Λ, where the iterative algorithm may fail to capture enough hits largely due to a stringent Δw requirements. At high Λ, ε_reco drops as well since the separation is small enough for the hits to start merging, at which point a plane cannot be found." | "Fail to capture enough hits" is the language of SR cut 2 (hit multiplicity). "∼70%" restates S5's ∼73%. |
| S10 | Table I caption | "For Λ≳5 keV, ε_reco deteriorates as pairs of hits start merging into a single pixel." | Merged hit pairs reduce per-layer hit counts, i.e. they fail SR cut 2. Under definition A they would matter only if no plane were found at all. |
| S11 | Fig. 6 caption and text | "Contours of having 3 (5) events … assuming negligible irreducible backgrounds"; "The 3 events bound corresponds to 2-σ exclusion given no background." | The expected signal count = σ·L·ε. A background-free count only makes sense for events **inside the signal region**, so ε must include the SR cuts. |

### 1.3 Verdict: **B**

Table I ε_reco = fraction of trigger ∧ fiducial events passing the **complete Sec. IV signal-region selection**.

- **Direct textual evidence:** S5 attaches "reconstruction efficiency" to "these cuts" (the SR cuts listed in S4) and quotes the same peak value (∼73%) that S9 and Table I report (0.72–0.74).
- **Structural evidence:** S7 and S11 make ε the total efficiency used for a background-free event count, which is defined only after the SR cuts.
- **Consistency:** S9 and S10 explain the Λ dependence with hit capture and merging, which act through cut 2.
- **Evidence for A:** only S8's phrase "efficiency of our algorithm in finding quirks". Read with S5 it is a description of the denominator, not a narrower numerator. No sentence ties Table I to plane finding alone.
- This conclusion does **not** rest on numerical agreement. Numerically, A agrees with the paper (0.80 vs 0.72) and B does not (0.15/0.22 vs 0.72). The textual verdict goes *against* the number that matches.

This reverses the project's earlier labelling (commit 09bedd7, `analyze_ew_quirk.py`; `table1_extraction_v1/denominator_definitions.csv`), which chose A. Those files were **not** edited.

### 1.4 Conditional cutflow after fiducial (both EW samples)

Script: `scripts/01_post_fiducial_cutflow.py`. Tables: `tables/post_fiducial_cutflow_sequential.csv`, `post_fiducial_failure_attribution.csv`, `post_fiducial_per_event.csv`.

The plane-fit code (`coplanarity_fit.py`) is unchanged since 2026-09-15, before both result files were produced, so both samples used identical selection logic. Closure was asserted for every event: stored final = plane ∧ multiplicity ∧ Δw ∧ Δs.

Event IDs are HepMC event indices.

| Step (sequential) | EW1000 | lost (event IDs) | EW2000 | lost (event IDs) |
|---|---|---|---|---|
| fiducial | 40 | — | 94 | — |
| ≥1 raw seed candidate | 32 | 72 90 136 198 248 280 373 417 | 75 | 37 79 133 214 284 290 371 373 456 496 528 598 627 671 849 923 925 932 1029 |
| **plane found** (Sec. III C selection, Δw<1) | **32 (0.800)** | none | **75 (0.798)** | none |
| hit multiplicity (SR cut 2) | 16 (0.400) | 3 13 15 84 149 186 208 279 320 339 341 355 368 386 405 500 | 48 (0.511) | 40 219 276 328 337 376 383 384 424 469 511 558 564 619 634 638 714 740 745 747 787 808 839 880 908 945 997 |
| Δw < 1 cm (SR cut 3a) | 16 | none (max Δw 0.32 / 0.42 cm) | 48 | none |
| Δs < 0.01 cm (SR cut 3b) | 6 (0.150) | 32 61 110 121 182 256 266 340 394 499 | 21 (0.223) | 70 182 205 361 403 427 570 572 632 662 674 717 730 731 785 799 805 831 874 883 921 956 967 971 986 1000 1016 |
| **final Sec. IV** | **6 (0.150)** | — | **21 (0.223)** | — |

The EW1000 "plane" count of 32 equals both the `seed_found` column (any raw candidate) and the Sec. III C-selected plane. Every raw candidate already had Δw < 1 cm.

**Which requirement causes 0.80 → 0.15/0.22?** Order-independent attribution among plane-found events:

| Among plane-found | EW1000 (32) | EW2000 (75) |
|---|---|---|
| fail Δs only | 10 | 27 |
| fail multiplicity only | 0 | 5 (328 376 469 839 880) |
| fail both | 16 | 22 |
| pass all | 6 | 21 |
| **pass Δs < 0.01 cm** | **6/32 = 19%** | **26/75 = 35%** |
| pass multiplicity | 16/32 = 50% | 48/75 = 64% |

- **Δs < 0.01 cm is the dominant loss.**
  - The median Δs of plane-found events is 0.017 cm (EW1000) and 0.015 cm (EW2000), above the cut.
- **Hit multiplicity is the second loss.**
  - Most multiplicity failures are *not* due to missing detector hits.
  - EW2000: in 22 of 27 failures, ≥2 post-merge hits existed in ≥7 layers, but the selected candidate did not collect them. The missing layers are mostly SCT 5–6 (`tables/EW2000_multiplicity_failure_diagnostic.csv`).
  - EW1000: all 16 failures had 16 post-merge hits.
- **Δw never removes an event.**

**Open item (not resolved here):** if B is the correct definition, the project's ε_reco(Λ=4 keV) is 0.15–0.22 against the paper's 0.72. That is a factor 3–5, larger than either the trigger or the fiducial discrepancy. Both dominant losses are plausibly sensitive to the hit-resolution and fit-window model, e.g.:

- SCT z smearing σ = 2 × 580 µm = 1.16 mm, entering a 100 µm Δs cut;
- the |x·n1| < 0.05 cm iterative window and the ×3 growth rule.

This is a hypothesis to test on existing events. It is **not** demonstrated.

## 2. Finite-barrel geometry

### 2.1 Evidence, separated by kind

| Class | Evidence |
|---|---|
| **Directly documented paper implementation** | (a) "We hereby use the parameters of the various detector elements as specified in [27]" ([27] = ATL-PHYS-PUB-2009-002). (b) "For simplicity, we only included the barrel of the pixel and SCT detectors in our simulations, which effectively restricts the fiducial range to \|η\|≲1.8." (c) Fiducial = "each quirk intersect with each layer at least once" + 25 ns. (d) "Inclusion of the endcaps should increase ε_fid." (e) Pile-up: "…as long as the track is within the η-range of the barrel." **No barrel half-length, z extent, or explicit η cut appears anywhere in v1 or v2.** The \|η\|≲1.8 is phrased as a *consequence* ("effectively restricts"), never as an applied cut. |
| **Authors' related simulation** (arXiv:1612.00850, App. A, cited for the pile-up detector) | "We take the resolution and geometry of each component from the ATLAS technical design report"; it models "IBL, one layer in the barrel; pixel detector … 3 layers in the barrel; SCT … layers in the barrel **and 2×9 discs in the endcaps**". A barrel+endcap layout implies finite-length barrels in **that** simulator. The quirk paper's **signal** simulation is described separately ("a simplified model of the ATLAS inner detector") and says it excludes endcaps. |
| **Standard ATLAS geometry** (primary sources, archived) | ATLAS JINST 3 S08003, Table 1.2 / Fig. 4.1: pixel sensitive barrel 50.5 < R < 122.5 mm, **\|z\| < 400.5 mm** ("active barrel length is 801 mm"); SCT sensitive barrel 299 < R < 514 mm, **\|z\| < 749 mm**. IBL: active \|z\| < 330.15 mm (arXiv:1803.00844). Ref [27] itself could not be read (CERN CDS bot-blocks all requests); it is a 2008 note and predates the IBL. |
| **Project inference** | That the paper's signal simulation used finite z lengths. Supporting: the literal reading of "barrel", the "effectively" wording, the endcap remark (d), and the authors' other simulator. Against: the paper's own number. An all-8-layer finite barrel implies \|η\| ≲ 1.17, not 1.8 (table below). |

### 2.2 Layer-by-layer table

`scripts/02_barrel_geometry_table.py` → `tables/barrel_layer_acceptance_table.csv`

| Layer | r (cm) | Half-length (cm), source | η edge, vertex at 0 | η edge, vertex at +2σ_z (9 cm) | Project implementation | Project cone ≡ \|z\| < | Binding if both applied |
|---|---|---|---|---|---|---|---|
| 1 IBL | 3.325 | 33.0 (1803.00844) | 2.99 | 2.68 | infinite cylinder + \|η_origin\|<1.8 | 9.8 | cone (tighter) |
| 2 Pixel B-layer | 5.05 | 40.05 (JINST) | 2.77 | 2.52 | same | 14.9 | cone |
| 3 Pixel L1 | 8.85 | 40.05 | 2.22 | 1.97 | same | 26.0 | cone |
| 4 Pixel L2 | 12.25 | 40.05 | 1.90 | 1.66 | same | 36.0 | cone |
| 5 SCT B3 | 29.9 | 74.9 (JINST) | 1.65 | 1.53 | same | 88.0 | finite z |
| 6 SCT B4 | 37.1 | 74.9 | 1.45 | 1.34 | same | 109.2 | finite z |
| 7 SCT B5 | 44.3 | 74.9 | 1.30 | 1.19 | same | 130.3 | finite z |
| 8 SCT B6 | 51.4 | 74.9 | 1.17 | 1.07 | same | 151.2 | finite z |

The "≲1.8" in the paper sits between the pixel-L2 edge (1.90) and the SCT-B3 edge (1.65). It does not correspond to requiring all 8 layers of a finite barrel.

### 2.3 Does applying finite-z together with \|η\|<1.8 double-count?

Not in the sense of counting the same loss twice: the two constraints bind at **different layers**. The cone binds at layers 1–4, the finite z at layers 5–8. Applying both is the intersection, which is **stricter than either and stricter than any physical barrel**.

Re-using the previous audit's replay crossings, adding the cone on top of the finite barrel removes 3 / 2 / 3 events (EW1000 / EW2000 / colored). **All of them fail only at the IBL (layer 1)**, with vertex offsets of 5.6–9.8 cm, and lie inside every physical layer (`tables/cone_on_top_of_finite_barrel_extra_losses.csv`).

That extra loss is an artefact: an origin-measured η cone combined with a smeared vertex. Nothing in the paper describes applying both. The "both" variant (C, 0.327 pooled EW in the previous audit) is therefore **not a defensible model of the paper**.

### 2.4 Verdict

- **Unresolved by the paper.**
- Finite barrel (B: pooled EW 0.345) remains a physically motivated, ATLAS-documented alternative.
- The project's cone (A: 0.487) is a defensible reading of the paper's \|η\|≲1.8 sentence taken literally, but it is unphysical at the inner layers once the vertex is smeared.
- Neither is shown to be the authors' implementation. The finite-barrel number is **not** adopted as authoritative.

## 3. Version-matched EW trigger pilot

### 3.1 Toolchain (obtained and built faithfully)

| Item | Source | Integrity / build |
|---|---|---|
| MG5_aMC **2.3.3** (2015-10-25) | launchpad.net/mg5amcnlo/lts/2.3.x | MD5 `217ab0f3…6064` matches Launchpad; SHA-256 `ad33a264…bb57` |
| Pythia **8.212** | pythia.org/releases/pythia82/pythia8212.tgz (official archive) | SHA-256 `5631cf82…b898`; `Pythia:versionNumber` 8.212; built with GCC 16.2, 0 errors |
| Python 2.7.15 (MG5 2.3.3 is Python-2 only) | new isolated conda env `mg5_233_py27` | no other env touched |
| Quirk UFO | unmodified copy of the project model | imports under Python 2 (47 particles) |

**Two build accommodations for modern gfortran**, recorded in `pilot_provenance/mg5_233_cards/make_opts.used`:

- `-fallow-argument-mismatch`: MG5 2.3.3's `dsample.f` passes a 5th argument that the callee ignores.
- `-std=legacy`: legacy array-passing idiom in `genps.f`.

Both downgrade compile errors to warnings, as 2015-era compilers did. **No source line was changed.**

**Physics validation of the historical build:** σ_LO = (4.553 ± 0.022)×10⁻⁴ pb (MG5 2.3.3) vs 4.542 and 4.574×10⁻⁴ pb (3.7.3, same cards). Agreement within uncertainty.

### 3.2 Cards (identical physics; one generator change)

- **Process card:** identical to the project's (`p p > qe+ qe- @0` + `j @1`, 4-flavour p/j). MG5 2.3.3 produced the same three subprocesses.
- **Parameter card:** identical masses and widths. `aS` set to the frozen 0.13; MG5 does not use it with a PDF set.
- **Run card:** every key common to both versions is identical (nn23lo1, dynamical_scale_choice −1, ickkw 1, xqcut 30, ptj 20, etaj 5, maxjetflavor 4, 6.5 TeV beams). 2.3.3-only keys keep their template defaults and don't act on this process (drjj = mmjj = 0, no lepton or photon objects).
- **Seeds:**
  - pilot effective seed **24**: MG5 2.3.3 consumed the set seed 8002 during the first, compile-failed launch and reset it, as its code does; recorded in the banner.
  - production seed **8003**, set explicitly and confirmed in the banner and log.
- **Shower settings:** the 16 changed settings of the frozen EW2000 run verbatim (qCut 45, nJetMax 1, scheme 1, setMad off, coneRadius 1, etaJetMax 1000, nQmatch 4, …), Pythia default seed and tune.
- **Shower driver:** a standalone LHE→Pythia8+`JetMatchingMadgraph` program (`pilot_provenance/driver/quirk_mlm_shower.cc`), the same structure as MG5's PY8 interface and Pythia's main89.
  - **Validation: with Pythia 8.317 on the frozen EW2000 LHE it reproduces the frozen HepMC event by event.** 1045/1045 matched events, max \|ΔpT_pair\| = 4×10⁻⁹ GeV, trigger 186/186.
- Trigger computed identically everywhere: final status-1 quirk-pair pT > 200 GeV (strict), denominator = matched events.

### 3.3 Version-interaction artefact found (reported, excluded)

MG5 3.7.3's interface sets `Beams:setProductionScalesFromLHEF = on` ("S"); Pythia's default, and its own 8.212 MLM example `main89mlm.cmnd`, is `off`.

MG5 2.3.3 writes `<scales pt_clust_N>` with **N = final-state position** (`addmothers.f`: `integ = i−2`). Pythia (8.212 `LesHouches.cc` and 8.317) reads N as the **LHE line index**, which is MG5 3.x's convention. So "2.3.3 LHE + S=on" assigns the jet's clustering scale to a quirk. With Pythia 8.317 that drives 1-jet matching to 99.9% (1482/2000 matched).

This combination is invalid and excluded. S was therefore also added as its own one-at-a-time variable.

### 3.4 Results

`tables/version_pilot_variants.csv`; spectra in `tables/version_pilot_pairpt_spectra.json`. Each row is ε_trig = trigger/matched, with the exact two-sided binomial p-value vs 0.10.

| Variant (one change per step) | LHE | Pythia | S | ε_trig | Wilson 95% | p vs 0.10 | Fisher vs frozen 275/1556 |
|---|---|---|---|---|---|---|---|
| Frozen samples | 3.7.3 | 8.317 | on | 275/1556 = 0.177 | [0.159, 0.196] | 2.9e-20 | — |
| Rerun of frozen config (driver) | 3.7.3 | 8.317 | on | 280/1538 = 0.182 | — | 1.6e-22 | 0.71 |
| **Pythia version** | 3.7.3 | **8.212** | on | 268/1556 = 0.172 | — | 3.2e-18 | 0.78 |
| **S off** | 3.7.3 | 8.317 | **off** | 240/1582 = 0.152 | — | 1.2e-10 | 0.060 |
| Pythia 8.212 + S off | 3.7.3 | 8.212 | off | 257/1579 = 0.163 | — | 1.5e-14 | 0.32 |
| **ME version** (pilot + prod) | **2.3.3** | 8.317 | off | 214/1248 = 0.171 | — | 1.2e-14 | 0.73 |
| **Era-faithful: MG5 2.3.3 + Pythia 8.212** (pilot + prod) | 2.3.3 | 8.212 | off | **214/1279 = 0.167** | — | **1.2e-13** | **0.52** |
| ↳ production sample alone (seed 8003) | 2.3.3 | 8.212 | off | 179/1037 = 0.173 | [0.151, 0.197] | 8.1e-13 | 0.79 |
| ↳ 500-event pilot alone (seed 24) | 2.3.3 | 8.212 | off | 35/242 = 0.145 | [0.106, 0.195] | 0.024 | 0.24 |

One-variable effects (Fisher exact):

| Variable changed | Effect p | Notes |
|---|---|---|
| Pythia version (MG 3.7.3, S off) | 0.41 | not significant |
| ME version (Py 8.212, S off) | 0.76 | not significant |
| S setting (Py 8.317, same LHE) | 0.024 | 0.182 → 0.152 |

The S setting is the only significant change found, and even its lowest value (0.152) is incompatible with 0.10 (p = 1.2×10⁻¹⁰).

**Pair-pT spectra** (normalized, matched events). KS test vs frozen: era-faithful production p = 0.80; MG 3.7.3 + Py 8.212 S off p = 0.37; MG 3.7.3 + Py 8.317 S off p = 0.23.

| pair pT (GeV) | frozen | MG 2.3.3 + Py 8.212 S off | MG 3.7.3 + Py 8.212 S off | MG 3.7.3 + Py 8.317 S off |
|---|---|---|---|---|
| 0–25 | 0.258 | 0.257 | 0.272 | 0.270 |
| 25–50 | 0.188 | 0.181 | 0.203 | 0.208 |
| 50–75 | 0.110 | 0.138 | 0.102 | 0.106 |
| 75–100 | 0.085 | 0.079 | 0.082 | 0.079 |
| 100–150 | 0.122 | 0.101 | 0.109 | 0.106 |
| 150–200 | 0.060 | 0.070 | 0.072 | 0.084 |
| 200–300 | 0.075 | 0.072 | 0.077 | 0.065 |
| 300–400 | 0.037 | 0.037 | 0.027 | 0.022 |
| 400–600 | 0.039 | 0.037 | 0.036 | 0.045 |
| 600–1000 | 0.023 | 0.023 | 0.019 | 0.015 |
| >1000 | 0.003 | 0.004 | 0.002 | 0.001 |
| N matched | 1556 | 1037 | 1056 | 1050 |

**Verdict: generator-version differences do not explain the EW trigger discrepancy.**

- The era-faithful toolchain reproduces the project's ε_trig (0.167 vs 0.177) and its pair-pT spectrum.
- It remains incompatible with the paper's 0.10 at p ≈ 10⁻¹³.
- The trigger discrepancy stays **UNRESOLVED / PAPER SETTING UNDOCUMENTED**.
- The colored control (plan gate 6) was not run. The version change had no effect on EW, so a neutrality check had nothing to detect, and the sample stayed bounded at 2000 events. It remains available if wanted.
- Nothing was tuned: xqcut, qCut, PDF, scales and shower settings were held at the frozen values throughout.

## 4. Recommendation for Figure 6

**Keep both geometry models as separate systematic studies, with the existing Figure 6 run (η-cone) as the baseline. Resume only after one further bounded audit of the Δs / hit-multiplicity loss.**

Reasoning:

1. **Geometry: no paper-backed reason to restart.** The finite barrel is unresolved by the paper (§2). Restarting with it would replace one undocumented choice with another. The existing per-event Figure 6 outputs are a valid cone-model baseline. A finite-barrel *fiducial* systematic can be added later by post-processing (as the previous audit did), without discarding the run.
2. **ε_reco definition: it does not invalidate the run.** The driver already stores per-event `truth_fiducial`, `sec3c_plane_found`, `hit_multiplicity_pass`, Δs, Δw and `final_sec_iv_pass`. Definition B is a change of numerator in post-processing, not of the computation.
3. **Generator version: no effect** (§3).
4. **Why still gate the resume:** under definition B the project's ε_reco is 3–5× below the paper's. That factor scales Figure 6's total efficiency directly, and it is dominated by Δs < 0.01 cm and by multiplicity failures with hits available (§1.4).
   - If that audit finds an implementation problem in the hit-resolution or fit model, every remaining and completed Figure 6 cell would need recomputation. That would be the "restart with corrected modelling" case.
   - If it finds none, resume the existing run unchanged.
   - The audit needs no new generation: the existing EW2000 triggered events and the stored seeds suffice.

## Files

- `scripts/01_post_fiducial_cutflow.py` → `tables/post_fiducial_*`
- `scripts/02_barrel_geometry_table.py` → `tables/barrel_layer_acceptance_table.csv`, `tables/cone_on_top_of_finite_barrel_extra_losses.csv`
- `scripts/03_version_pilot_analysis.py` → `tables/version_pilot_variants.csv`, `tables/version_pilot_pairpt_spectra.json`
- `tables/EW2000_multiplicity_failure_diagnostic.csv`
- `logs/`: all script outputs, including `04_pilot_key_tests.log` (pooled tests)
- `paper_source/`: arXiv src (latest = v2), v1 source, 1612.00850 source, ATLAS JINST paper, SHA256SUMS
- `pilot_provenance/`:
  - download hashes and Launchpad MD5;
  - driver source and binary hashes;
  - MG5 2.3.3 proc/run/param cards (defaults and used) and make_opts (original and used);
  - both banners;
  - every shower run's settings, log and events.csv, plus LHE SHA-256s;
  - generation logs.
- Large files (LHE copies, MG5 2.3.3 process directory, Pythia 8.212 build) stay in `/home/rafia/hep_tools/EW_VERSION_PILOT_2026-10-02/`.
- `SHA256_MANIFEST.txt`
