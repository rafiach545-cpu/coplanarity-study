# Signal Table I Results — Literal Reproduction (Phases 3–7)

> **v2 CORRECTION (2026-10-03):** the classification in this document is superseded where it conflicts with `CORRECTION_ACCEPTANCE_AND_LONGITUDINAL_2026-10-03.md`. The paper-stated acceptance (barrel only, |η| ≲ 1.8, no finite-z boundary) is now PRIMARY. The finite barrel of Ref. [27] (called "literal" below) is an INFERRED sensitivity. SCT z 1160 µm is INFERRED, not stated; no SCT z smearing is UNDOCUMENTED. Primary denominators: COL2000 25, EW2000 94. See `FINAL_EXECUTIVE_REPORT.md` (v2) and `PROFESSOR_REPORT_2026-10-03_v2.pdf`.

**Benchmarks** (paper Table I):
- EW: m_Q = 800 GeV, Λ = 4 keV. Paper: trigger 0.10, fiducial 0.28, reconstruction 0.72.
- Colored: m_Q = 1800 GeV, Λ = 2 keV. Paper: trigger 0.24, fiducial 0.28, reconstruction 0.35.

**The paper publishes no raw counts and no uncertainties.** Exact paper-versus-project significance therefore cannot be fully determined. The p-values below test our counts against the paper's *quoted central value* treated as exact. A sample-size-aware two-sample comparison, with the paper's sample sizes inferred from its Fig. 5 histograms, is in `tables/paper_project_comparison.csv`.

## Literal configuration

Only PAPER-STATED, REFERENCE-STATED or unavoidable DERIVED-DIRECTLY settings, plus unavoidable UNDOCUMENTED generator values taken from the frozen samples:
- **Frozen samples:** EW1000, EW2000, COL1000, COL2000, each reported separately.
- **Trigger:** pT of the quirk-pair CM system > 200 GeV (strict, final state), out of matched events. Raw recount in `tables/P3_raw_trigger_recount.json`.
- **Colored charge requirement:** both R-hadrons with non-zero charge.
- **Fiducial:** finite ATLAS barrel from ref. [27], no η cut; all 16 first crossings; max t < 25 ns; common 45 mm beam-spot shift.
- **Hit model:** pixel-centre hits; **SCT σ = 34 µm (R-φ) and 1160 µm (z)**; neighbouring-pixel merging.
- **Algorithm:** literal Sec. III C; Δw = √λ₂ (Eq. 11).
- **ε_reco:** full Sec. IV signal region / (trigger ∧ fiducial).

## Phase 4 exact-replay validation (before any variant)

Every trigger event was re-propagated with its stored vertex and stored random stream; `tables/signal_replay_vs_stored.csv`.

| Sample | Fiducial decisions | Plane | Final | Δs exact (1e-9) |
|---|---|---|---|---|
| EW1000 | 89/89 | 40/40 | 40/40 | 40/40 |
| EW2000 | 186/186 | 92/94 | 94/94 | 75/94 |
| COL1000 | 27/27 | 7/7 | 7/7 | 7/7 |
| COL2000 | 68/68 | 25/25 | 25/25 | 25/25 |

- The EW2000 differences are cross-machine floating-point effects: the project's own code run on this machine gives our values. They change no final count.
- SCT random-draw counts: 0 mismatches.
- 0 extra random draws were needed for the literal geometry.

## Phase 3 raw trigger recount (independent stdlib parse of the frozen LHE/HepMC)

| Sample | Generated | Showered | Matched | Trigger (final) | Post-shower pre-hadronisation | Hard process (status 23) |
|---|---|---|---|---|---|---|
| EW1000 | 1000 | 1000 | 511 | 89 | 89 | 64 |
| EW2000 | 2000 | 2000 | 1045 | 186 | 186 | 121 |
| COL1000 | 1000 | 1000 | 419 | 101 | 101 | 67 |
| COL2000 | 2000 | 2000 | 873 | 207 | 210 | 138 |

Strict > 200 and ≥ 200 give identical counts. Events within 1 GeV of threshold: EW2000 1, COL1000 2, COL2000 3.

## LITERAL results (each sample separately)

Columns: SE = binomial standard error; W68 / W95 = Wilson 68% / 95%; CP95 = Clopper–Pearson 95%; p = exact two-sided binomial p-value against the paper's quoted value.

| Sample | Quantity | k/n | % | SE | W68 | W95 | CP95 | Paper | Paper in W95? | p |
|---|---|---|---|---|---|---|---|---|---|---|
| COL1000 | trigger | 101/419 | 24.1% | 0.021 | [0.221, 0.263] | [0.203, 0.284] | [0.201, 0.285] | 0.24 | yes | 0.95 |
| COL1000 | fiducial | 6/27 | 22.2% | 0.080 | [0.153, 0.311] | [0.106, 0.408] | [0.086, 0.423] | 0.28 | yes | 0.67 |
| COL1000 | **reconstruction (full SR)** | 1/6 | 16.7% | 0.152 | [0.066, 0.363] | [0.030, 0.564] | [0.004, 0.641] | 0.35 | yes (N = 6) | 0.67 |
| COL2000 | trigger | 207/873 | 23.7% | 0.014 | [0.223, 0.252] | [0.210, 0.266] | [0.209, 0.267] | 0.24 | yes | 0.87 |
| COL2000 | fiducial | 22/68 | 32.4% | 0.057 | [0.270, 0.382] | [0.224, 0.442] | [0.215, 0.448] | 0.28 | yes | 0.42 |
| COL2000 | **reconstruction (full SR)** | 1/22 | 4.5% | 0.044 | [0.017, 0.113] | [0.008, 0.218] | [0.001, 0.228] | 0.35 | **no** | 0.0013 |
| EW1000 | trigger | 89/511 | 17.4% | 0.017 | [0.158, 0.192] | [0.144, 0.209] | [0.142, 0.210] | 0.10 | **no** | 2.8e-7 |
| EW1000 | fiducial | 33/89 | 37.1% | 0.051 | [0.321, 0.423] | [0.278, 0.475] | [0.271, 0.480] | 0.28 | yes | 0.059 |
| EW1000 | **reconstruction (full SR)** | 2/33 | 6.1% | 0.042 | [0.031, 0.116] | [0.017, 0.196] | [0.007, 0.202] | 0.72 | **no** | 2e-15 |
| EW2000 | trigger | 186/1045 | 17.8% | 0.012 | [0.166, 0.190] | [0.156, 0.202] | [0.155, 0.203] | 0.10 | **no** | 1.8e-14 |
| EW2000 | fiducial | 62/186 | 33.3% | 0.035 | [0.300, 0.369] | [0.270, 0.404] | [0.266, 0.406] | 0.28 | yes | 0.12 |
| EW2000 | **reconstruction (full SR)** | 10/62 | 16.1% | 0.047 | [0.120, 0.213] | [0.090, 0.272] | [0.080, 0.277] | 0.72 | **no** | 7.8e-20 |

**Diagnostic only (never Table I ε_reco):** plane-found / fiducial = COL1000 5/6, COL2000 9/22, EW1000 25/33, EW2000 45/62.

**Stale contaminated values: rejected.**
- The EW2000 plane numerator 84 (plane among *all* triggered events) is not used. The fiducial intersection is 75 under the frozen configuration and 45 under the literal one.
- The COL2000 plane numerator 20 is not used. The fiducial intersection is 12 under the frozen configuration and 9 under the literal one.

## Literal cutflows with lost event IDs (HepMC event indices)

Full list: `tables/signal_cutflow_with_event_ids.csv`. Closure: every stage is a subset of the previous one, with no duplicates (`tables/signal_event_closure.csv`).

| Sample | Trigger (analysed) | Fiducial | Plane | Multiplicity | Δw | Δs | Final |
|---|---|---|---|---|---|---|---|
| COL1000 | 27 | 6 | 5 | 3 | 3 | 1 | 1 |
| COL2000 | 68 | 22 | 9 | 4 | 4 | 1 | 1 |
| EW1000 | 89 | 33 | 25 | 10 | 10 | 2 | 2 |
| EW2000 | 186 | 62 | 45 | 24 | 24 | 10 | 10 |

Events lost at the hit-multiplicity and Δs steps:
- **EW2000 multiplicity:** 219 276 328 337 376 383 424 430 469 511 528 558 564 634 638 714 745 747 839 908 945.
- **EW2000 Δs:** 70 205 361 570 730 785 799 805 874 956 967 971 1000 1016.
- **COL2000 multiplicity:** 107 141 298 430 860.
- **COL2000 Δs:** 394 564 851.

The per-event first-failure reason and the complete seed/candidate logs are in `logs/P4_literal_forensic_events.jsonl`.

## Systematic variants (same events, same hits; NOT the literal result)

Each cell is fiducial / reconstruction. Under W2 every number is identical (the Δw cut never binds).

| Sample | Geometry | SCT z 1160 (literal) | 580 | 34 | 0 (calibrated) |
|---|---|---|---|---|---|
| EW1000 | B (literal) | 0.371 / 0.061 | 0.371 / 0.152 | 0.371 / 1.000 | 0.371 / 0.818 |
| EW2000 | B | 0.333 / 0.161 | 0.333 / 0.226 | 0.333 / 0.919 | 0.333 / 0.806 |
| COL1000 | B | 0.222 / 0.167 | 0.222 / 0.333 | 0.222 / 0.833 | 0.222 / 0.833 |
| COL2000 | B | 0.324 / 0.045 | 0.324 / 0.136 | 0.324 / 0.545 | 0.324 / 0.364 |
| EW1000 | A (η-cone) | 0.449 / 0.150 | 0.449 / 0.250 | 0.449 / 0.975 | 0.449 / 0.850 |
| EW2000 | A | 0.505 / 0.223 | 0.505 / 0.309 | 0.505 / 0.926 | 0.505 / 0.809 |
| COL1000 | A | 0.259 / 0.143 | 0.259 / 0.429 | 0.259 / 0.714 | 0.259 / 0.714 |
| COL2000 | A | 0.368 / 0.120 | 0.368 / 0.200 | 0.368 / 0.560 | 0.368 / 0.440 |

- The calibrated "no SCT z smearing" model (Z0) brings EW reconstruction to 0.81–0.82 and colored to 0.36–0.83. **It is not paper-proven** and does not enter the literal result.
- An independent confirmation sample (fresh seeds, configuration locked before generation, vector-like EW model) is in `TABLE_I_FINAL_INDEPENDENT_VALIDATION_2026-10-03/`. With the literal configuration it gives reconstruction **EW 14/102 = 0.137** and **colored 6/94 = 0.064**, confirming the literal results above. Fiducial: EW 102/352 = 0.290, colored 94/333 = 0.282.

## Verdict (signal)

- **Reproduced (paper value inside our 95% interval in every sample):**
  - colored trigger;
  - EW and colored fiducial (finite-barrel geometry from ref. [27]).
- **Not reproduced:**
  - **EW trigger** (0.174–0.178 vs 0.10; no defensible setting reproduces it, see `UNRESOLVED_DIFFERENCES.md`);
  - **EW and colored reconstruction under the literal SCT reading** (0.06–0.16 vs 0.72; 0.05 vs 0.35, with the COL1000 1/6 compatible only through N = 6).
- **Root cause of the reconstruction failure:** the literal 1.16 mm SCT z resolution. The paper's own Fig. 5 shows that its simulation did not have that resolution. The paper does not document what it used instead.
