# Pile-up-Only Background (μ = 50) — Literal Reproduction (Phase 8)

> **v2 CORRECTION (2026-10-03):** the classification in this document is superseded where it conflicts with `CORRECTION_ACCEPTANCE_AND_LONGITUDINAL_2026-10-03.md`. The paper-stated acceptance (barrel only, |η| ≲ 1.8, no finite-z boundary) is now PRIMARY. The finite barrel of Ref. [27] (called "literal" below) is an INFERRED sensitivity. SCT z 1160 µm is INFERRED, not stated; no SCT z smearing is UNDOCUMENTED. Primary denominators: COL2000 25, EW2000 94. See `FINAL_EXECUTIVE_REPORT.md` (v2) and `PROFESSOR_REPORT_2026-10-03_v2.pdf`.

## Paper statements (arXiv:1708.02243v2, verbatim)

From Sec. III D and IV:
- "only ∼10⁻³ of all background events contain a plane with at least one hit in 4 out of 8 layers. The number rapidly drops to 6×10⁻⁵, for events with a plane that contains at least one hit in each layer. Still the majority of these planes have only one hit in most of the layers."
- "the pileup backgrounds are derived by taking the distribution from events that are allowed to have 1-hit per layer, weighted by the overall efficiency of passing the more stringent requirement in point 2."
- "Even though Fig. 5 suggests a few background events after the final selection cut of Δs < 0.01 cm, we suspect that they can easily be removed …"

## Literal configuration

- **Pile-up:** ⟨μ⟩ = 50 (Poisson). Each interaction is drawn from the 20 000-event minimum-bias ancestry pool, with its own vertex z ~ N(0, 45 mm).
- **Tracks:** exact helix in 2 T; ATLAS tracking-efficiency track removal (ATL-PHYS-PUB-2015-051).
- **Detector:** finite barrel (ref. [27]), pixel-centre hits, SCT 34/1160 µm, neighbouring-pixel merging.
- **Reconstruction:** literal Sec. III C reconstruction relative to the primary vertex.
- **Seeds:** per event, `SeedSequence([90210777, 50, i]).spawn(2)`. Chunk files: `logs/P8_chunks_LITERAL/`.
- **Validation:** with the frozen code path (VALIDATE mode) the first 200 events reproduce the stored project sweep exactly (200/200; Δs difference 0).
- **Sample:** 5000 events, all completed (`P8_EXIT=0`).

**Mean hits per layer (literal):** L1 1680, L2 1549, L3 1217, L4 1026, L5 828, L6 693, L7 583, L8 494, for a total ≈ 8070 per event. This matches the paper's "O(1000) unassociated pile-up hits per layer". Source: `tables/pileup_layer_multiplicity.csv`.

## Cutflow (`tables/pileup_cutflow.csv`)

Upper limits are one-sided Clopper–Pearson 95% upper limits on the per-event probability.

| Stage | LITERAL k/5000 | rate | Upper limit / Wilson 95% | Paper | p (exact) | FROZEN project sweep k/5000 |
|---|---|---|---|---|---|---|
| plane with ≥ 1 hit in ≥ 4/8 layers | 33 | 6.6e-3 | W95 [4.7e-3, 9.3e-3] | ~1e-3 | 1e-16 | 59 (1.2e-2) |
| plane with ≥ 1 hit in 8/8 layers (relaxed control) | 1 | 2.0e-4 | W95 [3.5e-5, 1.1e-3] | 6e-5 | 0.26 (compatible) | 0 |
| Sec. III C plane | 109 | 2.2e-2 | — | — | — | 172 |
| hit multiplicity (7 × 2 + 1) | 0 | 0 | UL 6.0e-4 | — | — | 0 |
| Δw < 1 cm | 0 | 0 | UL 6.0e-4 | — | — | 0 |
| Δs < 0.01 cm (final Sec. IV) | **0** | 0 | **UL 6.0e-4** | "a few" events in Fig. 5 | — | 0 |

The frozen sweep's stored "Δs pass = 7" is *non-sequential*: Δs < 0.01 without the multiplicity cut. In the sequential cutflow it is 0.

**Relaxed-control estimate (the paper's method):**
- The only literal 8/8 event is event 800: 11 hits, Δs = 0.032 cm, Δw = 0.62 cm. It **fails** Δs < 0.01.
- So the relaxed distribution has 0 events in the signal region, and P(8/8 ∧ Δs ∧ Δw) < 6.0e-4 (95% CL).
- Multiplying by the multiplicity efficiency (0/1 observed; not measurable here) only lowers it.
- Of the 109 literal planes, 8 have Δs < 0.01 and Δw < 1, but all 8 fail the multiplicity cut. Literal planes have a median of 3 layers and 5 hits, which confirms "the majority of these planes have only one hit in most of the layers".

## Verdict (pile-up)

- **Compatible:**
  - the 8/8 relaxed-control rate (2e-4 vs 6e-5, p = 0.26);
  - the conclusion that no pile-up event passes the full signal region (0/5000; UL 6.0e-4 per event).
- **Differs:** the 4/8 rate, 6.6e-3 against ~1e-3, about 6.6× higher. The frozen project geometry gives 1.2e-2.
- **Likely causes** (MODEL-SYST; see `UNRESOLVED_DIFFERENCES.md` U6):
  - our detector omits the 1612.00850 App. A energy loss, bremsstrahlung and endcap material, which remove low-pT tracks;
  - the 20k pool vs 125k minimum-bias events;
  - "a plane" is undefined: seed vs fitted candidate.
- **Statistical limitation:** 5000 events cannot probe the paper's 6e-5 level with power. The expected count at 6e-5 is 0.3, so the 1 observed event is consistent with it.
- **No absolute luminosity yield is given for pile-up alone.** It needs the number of triggered (MET-type) events per bunch crossing that the overlay sits on, and the paper does not state it. Per-triggered-event probabilities and upper limits are given instead.
