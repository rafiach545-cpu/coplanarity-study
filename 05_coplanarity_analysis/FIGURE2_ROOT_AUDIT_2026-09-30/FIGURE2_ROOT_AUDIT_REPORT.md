# Figure 2 Root Audit Report — Event 65, Colored 1800 GeV / 2 keV Benchmark

Audit date: 2026-09-30
Scope: read-mostly forensic verification of the existing Figure 2
(`05_coplanarity_analysis/FINAL_FIGURES_2000_EVENT_2026-09-30/`), reproducing
arXiv:1708.02243v2 ("Tracking down Quirks at the LHC"), Figure 2 (p.4).
This audit is read-mostly: it did not modify, overwrite, or delete any
existing Figure 2 file. All new files live under
`05_coplanarity_analysis/FIGURE2_ROOT_AUDIT_2026-09-30/`.

Paper text/equations quoted below were fetched live from the ar5iv HTML
rendering of arXiv:1708.02243 (no local cached paper text file was found in
the repository at audit time — `paper.txt`, referenced by
`docs/COLORED_QUIRK_PAPER_EVIDENCE_v1.md`, is not currently present under any
path in the repo or its git history's added-file list). This is flagged
explicitly as a judgment call: the equations and caption below are DIRECT
PAPER EVIDENCE from the paper's own arXiv HTML rendering, not from the
project's prior paraphrase.

---

## Phase 1 — Source file provenance

See `SOURCE_FILE_PROVENANCE.csv` / `.md` for the full table (path, size,
mtime, SHA-256, classification) of 11 files: the two original Figure-2
scripts, the original source CSV/metadata/PNG, the two stored-event CSVs
(`per_event_results.csv`, `trigger_passing_events.csv`), the trajectory
integrator (`quirk_trajectory_optimized_v2.py`), the baseline integrator/unit
utilities (`quirk_trajectory.py`), the detector-hit code
(`trajectory_to_hits.py`), and geometry constants (`atlas_geometry.py`). No
LHE/HepMC files were copied (paths/hashes only, and none were needed — the
per-quirk four-momenta are already flattened into `trigger_passing_events.csv`).

`EVENT65_ORIGINAL_INPUT_ROW.csv` contains the exact, unaltered row 65 of
`trigger_passing_events.csv` (all 32 original columns preserved).

## Phase 2 — Event identity and initial kinematics

Confirmed end-to-end: sample = Colored, mQ = 1800 GeV, Λ = 2 keV, B = 2 T,
`event_idx=65`, `seed=2123515583` (`EVENT65_INITIAL_KINEMATICS.csv`).

- `per_event_results.csv["event_idx"]` is exactly `0..67` sequential and
  equal to `row_index`, so `trig.iloc[65]` (positional) and
  `recon[event_idx==65]` (label) address the same underlying event —
  verified programmatically, not assumed.
- Four-momenta consumed by the integrator are read straight from
  `trigger_passing_events.csv` row 65 with no transformation before being
  passed to `simulate_quirk_hits` — confirmed by re-reading the row inside
  this audit's own script and diffing against what the original replay
  script would have read (identical values, same file, same row index).
- Supplied vs on-shell energy (mass=1800 GeV exactly, as used by the
  integrator): quirk 1: supplied E=2067.271653 GeV vs on-shell
  2066.814412 GeV (rel. diff 2.21e-4); quirk 2: supplied E=2077.693749 GeV
  vs on-shell 2076.756478 GeV (rel. diff 4.51e-4). Both are the small,
  expected on-shell/off-shell rounding already handled explicitly by
  `check_onshell_energy()` in `trajectory_to_hits.py` (a printed warning,
  not an error) — not a new finding, but independently reconfirmed here.
- Pair four-momentum: `(px,py,pz)=(86.45,-1118.53,683.11)` GeV,
  `E=4144.97` GeV (supplied) / `4143.57` GeV (on-shell); pair
  `pT=1121.87` GeV; invariant mass 3931.35 GeV (supplied) / 3929.88 GeV
  (on-shell).
- CM-frame boost: `beta_cm = 0.316991`, `gamma_cm = 1.054376`.
- Internal (CM-frame) quirk speed/boost, computed the same way the
  integrator itself computes it for period-sizing: `v_int = 0.401045`,
  `gamma_int = 1.091633`.

## Phase 3 — Code-level definition of L, verified algebraically and numerically

The plotted quantity is **|L|**, the Euclidean norm of the 3-vector

```
L_vec = (x1 - x2) × [0.5*(p1 - p2)]     (all in natural units, GeV^-1 × GeV = dimensionless = units of ħ)
```

computed in `replay_figure2_colored_event65.py` and stored as `L_hbar =
np.linalg.norm(Lvec, axis=1)`. `make_figure2.py` plots `df["L_hbar"]/1e12`
directly — no sign, no single component.

**Independent, from-scratch verification** (this audit's
`generate_audit_csvs.py`, a genuinely separate code path, not a copy of the
project's shortcut formula): computed `r1 = x1 − R_cm`, `r2 = x2 − R_cm`
(per-particle positions relative to the pair's arithmetic-mean CM position,
`R_cm = 0.5*(x1+x2)`), then `L1 = r1×p1`, `L2 = r2×p2` (full lab-frame
momenta, not halved), and `L_total = L1+L2`. Algebraically this reduces to
exactly `0.5*(x1-x2)×(p1-p2)` — the orchestrating session's algebra was
correct. Numerically, over all 25,654 integrated steps of the regenerated
trajectory, `|L_total|` (independent formula) vs `|Lvec|` (project formula)
agree with **max relative difference 5.58e-9** (max absolute difference
1092 out of values ~1e13, i.e. floating-point-level agreement, not a
coincidence of similar magnitude). **This confirms the project's L formula
is not a factor-of-2 (or any other) bug** — it is an algebraically exact
shortcut for `L1+L2` about the pair CM.

Both quirks are included (L1 and L2 both computed and summed); CM-relative
positions are used (not lab-frame positions relative to the origin);
lab-frame (not internal/boosted) momenta are used for each particle, which
is the correct convention for "orbital angular momentum of the pair about
its own CM, as measured in the lab frame" — the physically relevant quantity
for how much rotation the trajectory itself acquires (the quantity paper
Eq. 6–9 is estimating), which is the correct target quantity, not e.g. the
CM-frame-boosted relative angular momentum.

## Phase 4 — Unit-conversion audit and the ~52×10¹² vs ~1×10¹² ħ gap

**Units.** `x1`, `x2` (from `integrate_trajectory_fast_v2`) are natural-unit
positions (GeV⁻¹); `p1`, `p2` are GeV momenta. In natural units (ħ=c=1),
`position[GeV⁻¹] × momentum[GeV]` is dimensionless and *already* the value
of `L/ħ` — no ħc factor is needed or applied at the L-computation step, and
none should be. The `CM_PER_NATURAL = 1.973269804e-14` (= ħc in GeV·cm)
conversion is applied ONLY to `x1`,`x2` for the *r_cm* and *d_cm* (position)
outputs — confirmed by direct inspection: `rel_x_natural = traj["x1"] -
traj["x2"]` (natural units) is what enters the cross product for L, not
`x1_cm`/`x2_cm`. This is exactly as the script's own comment states, and is
correct: converting positions to cm before the cross product would have
silently introduced a spurious ħc factor into `L_hbar`. **No unit error
found.**

**Reconciling the d amplitude (cross-check of trajectory correctness).**
Paper Eq. 4 gives the CM-frame *per-quirk* oscillation amplitude
`d_cm,max = (mQ/Λ²)(γ−1)`. For this event's own internal γ=1.091633:
`d_cm,max = (1800/(2e-6)²)×0.091633 GeV⁻¹ = 4.123e13 GeV⁻¹ = 0.8135 cm`.
The regenerated trajectory's actual maximum **total** separation
`|x1−x2|` (this audit's `d_cm` column) is **1.62733 cm — exactly 2×
0.8135 cm** (ratio 2.001). This is the expected relationship (paper's own
Eq. 5 explicitly writes the torque using "`2d`" for the same reason: `d` in
the paper's Eq. 1/4 is the *per-quirk* distance from the pair CM, and the
project's plotted `d_cm` is the *full* two-quirk separation). This 2.00×
match is strong, independent confirmation that the trajectory integrator
correctly reproduces paper Eq. 4's own exact analytic solution for this
event's kinematics — not a coincidence, and not consistent with any
length-scale bug.

**The L-scale gap, quantified event-by-event (not hand-waved):**

| Quantity | Value (this event) |
|---|---|
| v (internal CM-frame quirk speed) | 0.401045 |
| v_cm (pair boost) | 0.316991 |
| γ (internal) | 1.091633 |
| γ_cm | 1.054376 |
| mQ | 1800 GeV (=1.8 TeV, matches benchmark exactly) |
| Λ | 2×10⁻⁶ GeV (=2 keV, matches benchmark exactly) |
| B | 2 T (matches benchmark exactly) |
| Eq. 7 numeric estimate, **L ~ 10¹² ħ (v_cm·v³/0.1)(2keV/Λ)⁴(mQ/1.8TeV)²(B/2T)** | **2.045×10¹¹ ħ** (0.20×10¹²) |
| Eq. 6 estimate (natural units, B converted to GeV² via TESLA_TO_GEV2) | 3.212×10¹¹ ħ (same order as Eq.7, consistent) |
| Numerical trajectory max \|L\|, full integrated range | 5.290×10¹³ ħ (52.9×10¹²) |
| Numerical trajectory max \|L\|, displayed r≤22cm range | 5.222×10¹³ ħ (52.2×10¹²) |
| **Ratio: numeric max / Eq. 7 (single-oscillation estimate)** | **≈259×** |

Because mQ, Λ, B for this event are *exactly* the paper's own benchmark
values, the `(2keV/Λ)⁴(mQ/1.8TeV)²(B/2T)` factors are all identically 1 —
they are not responsible for the gap. The only event-specific input to
Eq. 7 is `v_cm·v³/0.1 = 0.317×0.401³/0.1 = 0.205`, i.e. **this event's own
kinematics predict a factor ~5× *smaller* L than the paper's illustrative
"~10¹²ħ" headline figure**, not larger — so the 52×10¹² we observe is not
explained by "faster/more-boosted than the paper's own example" kinematics;
if anything the naive Eq. 7 scaling points the other way.

Two hypotheses were tested quantitatively, not asserted:

1. **Approximation vs. exact, single-period vs. accumulated.** Eq. 6 is
   explicitly derived as "L picked up during **a single oscillation**" —
   not a cumulative total. The event's own oscillation period is
   `period_est = 3.940×10¹⁴ GeV⁻¹`; the displayed range (r≤22cm) spans
   `t=3.306×10¹⁵ GeV⁻¹`, i.e. **8.39 periods elapsed**. Multiplying Eq. 7's
   per-period estimate by 8.39 periods gives 1.72×10¹² ħ — closing the gap
   from 259× down to **≈30×**, but not to O(1).
2. **Does |L| grow linearly with elapsed periods (coherent accumulation)?**
   No: over the *full* integrated trajectory (49.3 periods elapsed to the
   point of maximum |L|), the numerical maximum (5.290×10¹³) is only 1.3%
   larger than the value already reached within the first 8.39 periods
   (5.222×10¹³). If accumulation were linear in period count, 49 periods
   should give ~6× more than 8 periods; it does not. **|L| plateaus/
   oscillates near this same order of magnitude after only a few periods,
   it does not keep growing.** This means "N periods × per-period pickup"
   is at best a partial, not complete, explanation of the gap.

**Conclusion on the gap:** the residual ≈30–260× discrepancy between the
paper's Eq. 6–7 (an explicit order-of-magnitude "∼" heuristic — a single
average torque × one period, using a "typical" displacement 2d rather than
a genuine time integral of the torque over the actual, relativistic,
magnetic-force-coupled trajectory) and the exact numerically-integrated
maximum |L| is **not accounted for by unit errors, factor-of-2 coordinate
conventions, or simple period-counting alone** (all of those were checked
and ruled out or only partially explanatory above). It is attributable to
Eq. 6–7 being a rough scaling estimate that the paper itself denotes with
"∼", not a precise closed-form prediction of a specific event's numerical
trajectory maximum — both the paper and this project agree the number is
"large compared to ħ" (10¹¹–10¹³ range on both sides, many orders of
magnitude above 1), which is the qualitative claim Eq. 6–9 is actually used
to support (annihilation suppression / coplanarity preservation), not an
exact numerical prediction to be matched to a few percent. This audit does
**not** claim the ≈30–260× gap is fully quantitatively resolved to O(1); it
reports the exact factor and the two most plausible contributing effects
tested, and states plainly that a residual factor remains unexplained by
anything found here.

## Phase 5 — Full timeseries export and monotonicity

`EVENT65_FULL_TIMESERIES.csv` (2,518 rows, r≤22cm displayed range) contains,
per accepted RK4 step: step index, `t_gev_inv`, `r_cm`, `x1`/`x2`
(natural-unit components), `p1`/`p2` components, `d_cm`, `Lx/Ly/Lz_hbar`
(signed components), and both the original-formula and independent-formula
`|L|`. **`r_cm` is monotonically non-decreasing over the entire displayed
range (0 decreasing steps out of 2517 intervals)** — L and d come from the
identical row/timestep (no interpolation, no row-shifting, no re-sorting):
the data were generated in native integration order and never sorted by r,
so there is no possibility of a false phase relationship from re-sorting.

## Phase 6 — Zeros/extrema and the eight direct questions

`EVENT65_L_ZERO_AND_EXTREMA_TABLE.csv`: 16 signed-L_z zero-crossings, 31
|L| local extrema (15 minima + 16 maxima), 15 d local extrema, over the
displayed range.

1. **Signed or |L|?** |L| (a vector norm) — confirmed directly from the
   code (`np.linalg.norm(Lvec, axis=1)`), not inferred from the shape.
2. **Why does the curve stay non-negative?** Because it is mathematically a
   norm; it cannot be negative by construction, independent of any physics.
3. **Why ~2× as many oscillations as d?** Confirmed quantitatively: 31 |L|
   extrema vs 15 d extrema in the same window (ratio 2.07). Mechanistically
   verified in the minima list: |L| has a **local minimum at every turning
   point of d — both at d's maxima (~1.62cm, |L|≈3.6×10¹¹) AND at d's
   minima (~0.001–0.006cm, |L|≈0.6–1.4×10¹¹)** — i.e. two |L| minima per
   one full d-oscillation period, exactly the observed 2:1 ratio.
4. **Does |L| fold +/- half-cycles together?** Yes: the signed z-component
   `Lz` changes sign 16 times (≈8 full periods) while |L| (necessarily
   non-negative) shows a corresponding but doubled-frequency ripple —
   consistent with |L| folding the ± half-cycles of the underlying signed
   motion into equal-magnitude humps.
5. **At every genuine signed-Lz zero, is d large or small?** Mixed, not
   one-sided: across the 16 crossings, `d_cm` ranges from ≈0 up to ≈1.627cm
   (mean 0.81, std 0.84) — crossings occur at BOTH ends of d's oscillation,
   not preferentially at one.
6. **At every displayed \|L\| minimum, is d large or small?** Both — the 15
   minima split into two interleaved families: one at d≈1.62cm (near d's
   own maximum) with |L|≈3.6×10¹¹, and one at d≈0.001–0.006cm (near d's own
   minimum) with |L|≈0.6–1.4×10¹¹ — i.e. |L| dips at *both* of d's turning
   points, not only one.
7. **Are any apparent zeros a plotting-resolution artifact?** The only
   exact `|L|=0` point in the whole displayed dataset occurs at the very
   first integrated step (`t=0`), where both quirks are still coincident
   at the production vertex by construction (`x1=x2` ⇒ `r1_rel=r2_rel=0`
   ⇒ `L1=L2=0` trivially) — not a genuine mid-trajectory physical zero and
   not a plotting/resolution artifact either; it is the exact, expected
   value at the initial condition. All later local minima (question 6) are
   nonzero (≥5.9×10¹⁰ ħ), consistent with the paper's own caption that L
   stays large in units of ħ once the trajectory begins.
8. **Genuine physical disagreement, or wrong quantity compared?** No
   evidence of a wrong-quantity comparison: the project plots the same kind
   of object the paper's Fig. 2 caption describes (an angular momentum
   curve that oscillates and a separation curve that "does not vanish
   except at r=0"), and this audit's own data shows exactly that
   qualitative behavior (near-zero-but-nonzero `d` dips, always-oscillating
   never-exactly-zero-after-t=0 `|L|`). The unresolved ≈30–260× magnitude
   gap (Phase 4) is about the paper's own crude analytic estimate (Eq.
   6–7) vs. an exact numerical integration for one specific MC event — it
   is not evidence that the project computed a different physical quantity
   than the paper's Fig. 2 itself plots.

## Phase 7 — Paper Eq. 5–9 / Figure 2 comparison table

Fetched directly from the arXiv HTML rendering of 1708.02243 (DIRECT PAPER
EVIDENCE, quoted verbatim where feasible):

> Eq. 5: **τ ∼ 2d × (eE_cm) = 2eγ_cm d × (v_cm × B)**
> Eq. 6: **L ∼ |τ|Δt ∼ e·v_cm·γ_cm·v·γ(γ−1)·mQ²B/Λ⁴**
> Eq. 7: **L ∼ 10¹²ħ (v_cm v³/0.1)(2keV/Λ)⁴(mQ/1.8TeV)²(B/2T)**
> Eq. 8: **Δφ ∼ |τ|Δt²/I ∼ e·v_cm·γ_cm·γ²v²/[(γ−1)²]·B/Λ²**
> Eq. 9: **Δφ ∼ 10⁻⁵(v_cm/v²)(B/2T)(2keV/Λ)²**
> Figure 2 caption: "Angular momentum L and the relative distance between
> the quirks d, as a function of the radial distance of the center of mass
> to the interaction point for a representative event, with B=2T. The
> displacement d varies several orders of magnitude over the quirk
> trajectories, but despite the appearance on this figure, it does not
> vanish except at the origin (r=0)."

| Quantity | Paper statement/value | Project value (event 65) | Ratio/diff | Source | Status |
|---|---|---|---|---|---|
| B field | 2 T, uniform, along z | 2 T | exact match | `EVENT65_INITIAL_KINEMATICS.csv` | DIRECT PAPER EVIDENCE, VERIFIED |
| mQ | 1.8 TeV (benchmark used in Eq.7) | 1800 GeV exactly | exact match | same | VERIFIED |
| Λ | 2 keV (benchmark used in Eq.7) | 2×10⁻⁶ GeV exactly | exact match | same | VERIFIED |
| L definition | Not given in closed form for Fig.2 itself (Eq.6 is only an order-of-magnitude estimate for the *pickup rate*, not the plotted curve's defining formula) | \|L1+L2\| about pair CM, lab-frame momenta | INFERENCE (paper does not publish Fig.2's exact underlying formula) | `EVENT65_FULL_TIMESERIES.csv`, Phase 3 | UNRESOLVED — plausible/standard convention, not directly verifiable against paper text |
| d definition | "relative distance between the quirks" (full separation, paper's own Fig.2 curve) | \|x1−x2\| (full separation) | Confirmed self-consistent via Eq.4 amplitude check (2.00× per-quirk amplitude, Phase 4) | Phase 4 | VERIFIED (self-consistency argument, not a direct paper-value match — paper does not publish its own event's numeric d) |
| L numerical scale (illustrative, Eq.7) | ∼10¹² ħ (order-of-magnitude, paper's OWN benchmark kinematics, not necessarily event 65's) | max \|L\| ≈ 5.2–5.3×10¹³ ħ | ≈30–260× larger (event-specific Eq.7: 2.05×10¹¹) | Phase 4 | UNRESOLVED (order-of-magnitude qualitative agreement — both "≫1" — but exact factor not closed) |
| d numerical scale | "varies several orders of magnitude," "does not vanish except at r=0" | ranges from ≈0.0006 cm to 1.627 cm over displayed range (>3 orders of magnitude); never exactly 0 after t=0 | Qualitatively matches | Phase 5/6 | VERIFIED (qualitative shape) |
| Radial display range | Paper's Fig.2 x-axis range not numerically stated in the fetched text (only that it spans "the quirk trajectories") | 0–22 cm (project's own declared, documented choice, not paper-derived) | N/A | `FIGURE_2_2000event_colored_event65_source.csv`-generating script comment | INFERENCE / project's own documented choice |
| Oscillation period/count | Not numerically stated for Fig.2 in the fetched text | ≈8.39 periods across displayed range; 16 signed-L zero-crossings, 31 \|L\| extrema, 15 d extrema | N/A | Phase 6 | Cannot be compared — paper does not publish this number |
| Phase relation L vs d | Not explicitly stated numerically | \|L\| has a local minimum at BOTH of d's turning points (2:1 frequency ratio) | N/A | Phase 6 | INFERENCE from project data only — paper text does not give this relationship explicitly |
| Physical conclusion (annihilation suppressed, coplanarity preserved) | Explicitly stated: L≫ħ suppresses annihilation; Δφ (Eq.9) is tiny (∼10⁻⁵) so coplanarity is preserved | \|L\| ranges 10¹⁰–10¹³ ħ (≫1 throughout after t=0); this audit did not independently recompute Δφ (out of scope — no plane-rotation code was touched) | Qualitatively consistent (L≫ħ in both) | Phase 6 | PARTIALLY VERIFIED — L≫ħ claim supported; Δφ/coplanarity claim not independently re-derived in this audit |

**Overstatement guard:** this project's Figure 2 is explicitly labeled (in
its own metadata and figure caption) as "a representative project event —
NOT a claimed exact reproduction of the paper's own (unpublished)
representative event." The paper does not publish event 65's (or any
specific event's) exact four-momenta, so no row-by-row numerical agreement
with the paper's own Fig. 2 curve is possible or claimed anywhere in this
audit. Only qualitative shape (oscillating L, non-vanishing-but-varying d,
"≫ħ" scale) and the paper's own closed-form estimates (Eq. 4, Eq. 6/7) were
available for quantitative cross-checking, and both were checked explicitly
above.

## Phase 8 — Independent regeneration (single process, `nice -n 19`)

Regenerated event 65's full trajectory from its stored four-momenta + stored
seed using the unmodified `simulate_quirk_hits`/`integrate_trajectory_fast_v2`
code, single Python process, no multiprocessing, `nice -n 19` throughout
(confirmed via `ps`; Figure 6 workers were running concurrently and were not
touched). Row counts matched exactly (2,518 vs. 2,518). Point-by-point
comparison against the original `FIGURE_2_2000event_colored_event65_source.csv`:

| Column | Max abs diff | Max rel diff | Bit-identical? |
|---|---|---|---|
| r_cm | 3.55×10⁻¹⁵ | 2.41×10⁻¹⁶ | No, but floating-point-equivalent (machine epsilon) |
| L_hbar | 7.81×10⁻³ (out of values ~10¹³) | 2.49×10⁻¹⁶ | No, but floating-point-equivalent |
| d_cm | 2.22×10⁻¹⁶ | 2.48×10⁻¹⁴ | No, but floating-point-equivalent |

All differences are at the level of double-precision floating-point
non-associativity (relative differences ~1e-14–1e-16), not a real numerical
discrepancy — **the regeneration reproduces the original Figure 2 source
data to full floating-point precision.** No divergent timestep was found
(the "first_divergent_row" search at a 1e-9 absolute threshold found none).

## Phase 9 — Cache-only independent plot

`plot_figure2_cache_only.py` imports only `pandas` and `matplotlib`; it
reads `EVENT65_ROOT_RECOMPUTED_VALUES.csv` and nothing from
`03_trajectory_sim/` or `04_detector_sim/`. Colors preserved exactly:
angular-momentum curve `#1f3d7a`, separation curve `darkorange`. Output:
`FIGURE2_EVENT65_ROOT_VERIFIED.png/.pdf/.svg`, all labeled event_idx=65,
Colored 1800 GeV/2 keV, with the same "representative event, not the
paper's exact event" disclaimer. The existing final Figure 2 files under
`FINAL_FIGURES_2000_EVENT_2026-09-30/` were not touched.

## One flagged documentation discrepancy (judgment call, not a numerical bug)

`FIGURE_2_2000event_metadata.json`'s selection criterion states "the 12
corrected fiducial-AND-plane-found colored events." This audit independently
counted the events in `per_event_results.csv` satisfying
`geometric_fiducial==True AND sec3c_plane_found==True`: there are **15**,
not 12. Event 65 (seed 2123515583, wall_time_s=12.817092) is unambiguously
the fastest-converging event in either count (next-fastest is event 43 at
18.36s), so **the actual event selected is unaffected** by this discrepancy
— it is a stale/imprecise count in the metadata's prose description, not a
selection error. Flagged here as a minor label-interpretation issue rather
than silently corrected or ignored.

---

## FINAL VERDICT: **VERIFIED CORRECT WITH LABEL-INTERPRETATION ISSUE**

Direct evidence supporting this verdict:

- **No unit error, no coordinate/factor-of-2 bug found.** The L formula
  used by the project is algebraically and numerically (5.6×10⁻⁹ relative)
  identical to a from-scratch, independently-coded `L1+L2` about the pair
  CM using full lab-frame momenta. The natural-unit cross product needs no
  ħc factor (correctly not applied), and the display-only cm conversion is
  correctly excluded from the L calculation.
- **Independent regeneration (Phase 8) reproduces the original CSV to
  floating-point precision** (relative differences ~1e-14–1e-16), single
  process, unmodified code, confirming the pipeline is deterministic and
  reproducible from the stored seed/momenta as claimed.
- **The trajectory integrator's own output is independently cross-checked
  against paper Eq. 4's exact closed-form amplitude** (2.00× match to the
  per-quirk vs. full-separation convention), a strong internal-consistency
  check unrelated to the project's own code.
- **The plotted quantity is |L| (vector magnitude), confirmed from the
  source code**, not an ambiguous or mislabeled signed quantity; all eight
  Phase-6 diagnostic questions have direct, data-backed answers (not
  hand-waved), and none of them reveal a plotting-resolution artifact or a
  wrong-quantity comparison.
- **The "label-interpretation issue"**: (a) the "12 vs. 15" fiducial&plane
  candidate-count discrepancy in the metadata's prose (does not affect
  which event was actually selected); and (b) the ≈30–260× gap between the
  paper's own admittedly-order-of-magnitude Eq. 6/7 estimate and this
  event's exact numerical trajectory maximum is real, quantified, and only
  partially (not fully) explained by period-accumulation — it is reported
  honestly as an open, unresolved quantitative gap rather than claimed to
  be reconciled, and rather than being (mis)represented as either "exact
  agreement" or "a bug." Both are labeling/interpretation matters, not
  evidence of incorrect code or a physics-definition mismatch.

This audit did not find a NUMERICAL-UNIT BUG, and did not find a
PHYSICS-DEFINITION MISMATCH (the quantities plotted are standard, correctly
computed, and qualitatively match the paper's own Fig. 2 description) — but
it also does not claim VERIFIED CORRECT outright, because of the two
labeling/documentation issues above (the metadata's "12" vs. actual 15, and
the honestly-unresolved order-of-magnitude gap against Eq. 6/7 that should
not be silently glossed over in any future write-up of this figure).

---

## Confirmations

- **Figure 6 remained running and untouched throughout this audit.**
  Verified via `tmux ls` (session `figure6_resume` present throughout) and
  `ps -p 14845` (driver PID 14845, `run_phase5_production.py`, plus worker
  PIDs 15006/15007/15008, all still running at the time of this report).
  No file under `05_coplanarity_analysis/figure6_full_v1/` was read,
  touched, or modified by this audit.
- **No new MadGraph/Pythia/LHE/HepMC event generation was performed.** Only
  the already-stored four-momenta for event_idx=65 (seed 2123515583) were
  read from `trigger_passing_events.csv` and replayed through the existing,
  unmodified trajectory integrator.
- **No existing Figure 2 file was modified, overwritten, or deleted** —
  `FINAL_FIGURES_2000_EVENT_2026-09-30/` was only read from, never written
  to. All new outputs are exclusively under
  `05_coplanarity_analysis/FIGURE2_ROOT_AUDIT_2026-09-30/`.
- **Nothing was committed or pushed to git** during this audit.
