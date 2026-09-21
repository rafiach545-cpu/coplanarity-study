# Figure 7 dE/dx — paper-to-code specification (v1) — 2026-09-21

## What the paper actually says (verified by direct PDF extraction, this task)

Appendix A, page 9, verbatim: *"Although we did not make use of variables
relying on dE/dx measurements in our analysis, we here include a brief
discussion for completeness. In Fig. 7 we show the dE/dx and βγ
distributions for the hits in the ATLAS pixel detector for a few signal
benchmarks. For the dE/dx we use the most probable value as a function of
βγ [35]. Since this simplified treatment of the dE/dx distribution is not
accurate for very slow particles, we omitted hits with βγ < 0.1 in the
left-hand panel of Fig. 7."*

Ref [35] = Particle Data Group, "Review of Particle Physics," Chin. Phys.
C40 (2016). This is the **standard PDG dE/dx reference** — a
well-established, publicly documented formula (Bethe-Bloch / Landau-Vavilov
most-probable-value treatment), not something unique to this paper.

**Crucially: the paper itself states it did NOT use dE/dx in its actual
analysis.** Figure 7 is presented purely for completeness/illustration.
This significantly lowers the stakes of not reproducing it exactly — it
was never part of the paper's core result.

## Item-by-item specification status

| Item | Status | Detail |
|---|---|---|
| Bethe-Bloch equation | DIRECT PAPER REQUIREMENT (via cited ref [35], PDG) | Standard formula, well-documented, does not need the paper to restate it |
| Quirk electric charge | PARTIALLY SPECIFIED | EW: unit charge (paper states this explicitly, Sec III A). Colored: quirk-hadron charge is ±1 with ~30% probability, otherwise 0 (not visible) or other multiples — Fig.7's caption does not state which specific charge value was used for the colored curve |
| β,γ dependence | DIRECT PAPER REQUIREMENT | Standard Bethe-Bloch β,γ dependence; MPV-vs-βγ specifically per PDG ref [35] |
| Detector material composition | NOT SPECIFIED IN PAPER | No composition (pure silicon assumed elsewhere in this project's pixel/SCT geometry, per `CUTS_AND_PIPELINE.md`) given for Fig.7 specifically |
| Material thickness per layer | NOT SPECIFIED IN PAPER | This project's own detector geometry (`atlas_geometry.py`) has layer RADII but no silicon THICKNESS/material-budget values in radiation lengths or g/cm² |
| Path-length correction | NOT SPECIFIED IN PAPER | Needed to convert a per-hit dE/dx (MeV cm²/g, mass stopping power) into an actual energy loss per crossing — requires local incidence angle and layer thickness, neither of which is in this project's stored geometry |
| Mean vs MPV | DIRECT PAPER REQUIREMENT | Paper explicitly uses MPV (Landau-Vavilov most-probable value), NOT the naive Bethe-Bloch mean — these differ substantially at low βγ due to the long Landau tail |
| Units | DIRECT PAPER REQUIREMENT | Fig.7 y-axis: MeV·cm²/g (mass stopping power), linear scale, 0-100 range |
| Low-beta validity / cutoff | DIRECT PAPER REQUIREMENT | Paper explicitly omits hits with βγ<0.1 in the left panel, citing MPV-treatment inaccuracy there |
| Energy/momentum update from dE/dx | NOT SPECIFIED IN PAPER — PROJECT SIMPLIFICATION IF IMPLEMENTED | The paper's own quirk propagation (Eq.3) does not include an explicit dE/dx energy-loss term; Fig.7 is a POST-HOC diagnostic computed from the already-simulated trajectory, not a feedback term in the equations of motion. Integrating dE/dx as an energy-loss term into `quirk_trajectory.py` would be a project addition beyond the paper's own stated method |
| Timestep coupling | N/A | Follows from the above — no dE/dx feedback exists in the paper's propagator |
| Stopping condition | N/A | Paper does not model quirks stopping via ionization loss (they are "heavy stable charged particles," energy loss from a single tracker traversal is negligible relative to mQ~800-1800 GeV) |
| Validation references | Standard PDG tables (e.g. minimum-ionizing dE/dx in silicon ≈1.664 MeV·cm²/g at βγ≈3-3.5) — well-known, not paper-specific |

## Repository search for reusable material/dE/dx code

`grep -rli "dE/dx\|dEdx\|bethe.bloch\|beta_gamma\|betagamma\|stopping.power\|material.budget\|radiation.length"`
across all `.py` files — **zero real implementations found** (re-confirmed
this task; matches the prior turn's finding in
`figure_inventory_v2/Figure_7_NOT_REPRODUCIBLE.md`). No material-budget
map, no path-length-in-silicon code, anywhere in the repository.

## Decision: what CAN and CANNOT be built without fabrication

**CAN be built** (this task): a standalone Bethe-Bloch/MPV validation
module — the FORMULA itself is fully specified by cited reference [35]
(PDG) and does not depend on this project's unavailable detector-specific
inputs (material thickness, path length). This produces a dE/dx-vs-βγ
CURVE (mass stopping power in a given material, e.g. silicon, per unit
path length) that can be validated against known PDG reference values.

**CANNOT be built** (remains BLOCKED): integration of that curve into
this project's ACTUAL simulated hits (i.e., reproducing Fig.7's real
histograms from real simulated quirk trajectories) — this requires the
per-hit path length through each layer's silicon thickness and the
detector's material budget, neither of which exists in this project's
stored geometry (`atlas_geometry.py` has radii only, no thickness/budget).
Fabricating a plausible-looking material-budget value not sourced from
the paper or a cited reference would be exactly the kind of invented
input this task explicitly prohibits.

**Verdict for the full Figure 7 reproduction: BLOCKED — MATERIAL MODEL
NOT SPECIFIED/IMPLEMENTED.** The standalone formula-validation module
below is a genuine, bounded, non-fabricated feasibility step; it does not
constitute a Figure 7 reproduction.
