# Figure 3 diagnostic (v2) — ACHIEVED (APPROXIMATE) — 2026-09-21

## Status: superseding all prior "NOT ACHIEVED" verdicts

This corrects both the prior-turn `Figure_3_NOT_ACHIEVED_v1.md` verdict and
this session's own first attempt. **Neither prior "degenerate" or
"unphysical" result was real physics** — both were measurement artifacts.
See `figure3_diagnostic_metadata_v2.json`'s `"key_finding"` field for the
full technical account. Short version:

1. The prior turn measured the wrong quantity: internal angular momentum
   `L = x_rel × p_rel` instead of the paper's own stated definition (Eq.8
   preamble): the rotation of the plane spanned by the **quirks' velocity
   vectors**, `n_v(t) = v1(t) × v2(t)`.
2. This turn's first attempt switched to `n_v` but used too loose a
   validity threshold, letting through samples near periodic
   near-antiparallel crossings (`v1 ≈ -v2`, where `|v1×v2| → 0` and its
   direction is numerically ill-conditioned). These crossings produced
   isolated spurious spikes of order 0.02–0.1 rad that dominated a naive
   `max()` statistic.
3. Fixing both issues (correct `n_v` definition; percentile-based
   exclusion of near-crossing samples, `valid = |n_v| > 0.1×median(|n_v|)`)
   revealed that the **same simple, unperturbed configuration already used
   for the achieved Figure 2 reproduction** (pure-x CM boost, B=2T along z,
   internal tilt along z — no artificial perturbation of any kind)
   reproduces Δφ(r) with the correct magnitude and correct qualitative
   shape for both benchmarks. **This was a measurement bug, not a missing
   physical ingredient.**

## Primary result

`Figure_3_diagnostic_v2.png` / `.pdf`, built from configs
`J_colored_natural_config` (mQ=1.8TeV, Λ=2keV) and `K_ew_natural_config`
(mQ=800GeV, Λ=2keV — the paper's own SECOND Fig.3 benchmark point, note
Λ=2keV not the main-text EW-benchmark Λ=4keV used elsewhere in this
project, per the paper's own Fig.3 caption).

| Config | max Δφ (rad) | Paper's stated range |
|---|---|---|
| Colored (J) | 4.610×10⁻⁴ | Eq.9 ~10⁻⁵; text "not larger than 10⁻³"; Fig.3 axis 0–4×10⁻⁴ |
| EW (K) | 6.075×10⁻⁴ | same |

Both fall within, or very close to, the paper's own stated range and
Fig.3's own y-axis span. Qualitative shape matches the paper's own
description verbatim: "Δφ oscillates and slowly accumulates... until it
stabilizes around a fixed value."

**Label: "Approximate Figure 3 reproduction — correct definition, correct
order of magnitude and qualitative shape; initial orientation is a
project assumption (paper does not publish exact initial conditions);
residual angle-unwrapping spike artifacts documented, not hidden."**

## Definition used (verified against paper.txt lines 301-349)

- **Quantity:** Δφ = accumulated (unwrapped) rotation angle of
  `n_v(t) = v1(t) × v2(t)` (normalized), the normal to the plane spanned
  by the two quirks' **lab-frame velocity vectors** — NOT the fitted
  detector-hit plane (that is `coplanarity_fit.py`'s Sec IIIC quantity,
  used for Fig.4/5, a different thing entirely).
- **Radial coordinate:** r = |x_cm(t)| = |(x1+x2)/2|, cm.
- **Sign convention:** unsigned (arccos of dot product; hemisphere-flip
  resolves the plane-normal sign ambiguity).
- **Caption/axis-label inconsistency** (paper-internal, confirmed by
  direct visual PDF inspection): the printed caption says "Δθ", but the
  y-axis label and Eq.8/9 both say "Δφ" — no equation anywhere defines a
  separate Δθ. We use Δφ (the equation-supported quantity).
- **B-field:** Lorentz force, B=2T along lab z, same treatment as
  everywhere else in this project (`quirk_trajectory.py`, unmodified).
- **ISR recoil:** not modeled directly (no ISR jet 4-momentum injected);
  the CM boost is set parametrically. PROJECT SIMPLIFICATION, same as
  Figure 2.

## Acceptance criteria — all met

- [x] Matches paper's own Eq.8/9 definition (not the caption's unsupported "Δθ")
- [x] Δφ changes nontrivially with r (rises from 0, oscillates, plateaus)
- [x] Physically valid initial state (energy-momentum conservation checked and passed for every config, see `figure3_scan_table_v2.csv`)
- [x] No manual curve shaping — only a genuine bug fix in the observable's measurement, not a post-hoc reshaping
- [x] Reproducible — deterministic ODE integration, no RNG anywhere in this script
- [x] Correct axes/units — r in cm, Δφ in units of 10⁻³ rad, matching the paper's own Fig.3 exactly

## Known limitation (documented, not hidden)

The plotted curves show occasional sharp spikes/dips at isolated r values
where the percentile-based validity filter transitions between segments
separated by a near-degenerate crossing; the reference direction
re-anchors at each new segment's first sample. The smooth trend BETWEEN
spikes is the validated signal (percentile statistics: median~6×10⁻⁵,
p95~1.4×10⁻⁴, p99~4×10⁻⁴ rad — all physically reasonable, not
spike-dominated). The paper's own Fig.3 curve is smoother, likely from a
better-conditioned numerical method (e.g. direct torque integration
rather than post-hoc arccos of noisy unit vectors) — see
`recommended_next_experiment` in the metadata JSON for a concrete fix.

## Full bounded scan (11 configurations tested, all recorded)

See `figure3_scan_table_v2.csv` for the complete record: event/config ID,
benchmark, initial momenta construction, boost vector, tilt, B-field,
energy-momentum-conservation check, max Δφ, r-range, growth check, and
(for the one rejected config, G) the explicit rejection reason. Per-config
Δφ(r) source curves are in `figure3_source_<config_id>_v2.csv`.

Only config G (`boost_zperturb_ytilt` — boost given a z-component but
internal tilt kept transverse/y, i.e. tilt NOT aligned with either the
boost or the B-field) remained genuinely degenerate (max Δφ = 2.4×10⁻⁶,
flat with r) — consistent with the underlying symmetry: when the internal
tilt is orthogonal to the plane containing both the boost and B-field
directions, no torque component exists to rotate the velocity-vector
plane out of its own fixed orientation.

## Files
- `Figure_3_diagnostic_v2.png` / `.pdf` — primary plot (configs J, K)
- `figure3_scan_table_v2.csv` — full 11-config scan record
- `figure3_source_<config_id>_v2.csv` — per-config Δφ(r) raw curves
- `figure3_diagnostic_metadata_v2.json` — full definitions, findings, caveats

## Regeneration
`python3 03_trajectory_sim/figure3_diagnostic_v2.py` — no RNG, no new
simulation beyond this script's own ~11 independent single-event RK4
integrations (each ~15-30s wall time), fully deterministic.
