# Figure 7 — NOT REPRODUCIBLE (confirmed blocker)

**Caption** (App. A, p.9): "Differential distribution of dE/dx (left) and
βγ (right) for two signal benchmark points with Λ=2keV in our simulation
of the ATLAS pixel detector."

## Required inputs
- Bethe-Bloch dE/dx formula (mean energy loss vs βγ)
- Silicon path-length per hit (detector-material geometry)
- Pixel-detector material budget / thickness map
- Most-probable-value (MPV) treatment (paper explicitly uses MPV as fn of
  βγ, from PDG ref [35], not the mean)

## Repository search performed
`grep -rli "dE/dx\|dEdx\|bethe.bloch\|beta_gamma\|betagamma"` across all
`.py` files — **zero real implementations found** (a few incidental
substring matches in unrelated pileup files, verified not to be dE/dx
code). No material-budget map, no energy-loss table, no path-length-in-
silicon code, no calorimeter/TRT response code anywhere in the repository.

## Verdict
**BLOCKED — missing physics, not a data-processing gap.** Implementing a
full Bethe-Bloch + material-budget model was explicitly listed as
requiring "an evidence and runtime gate" before implementation, and this
task did not authorize it. No formula-level shortcut was attempted since
even a "lightweight" dE/dx reproduction requires, at minimum, a validated
silicon path-length calculation per hit and an MPV-vs-βγ curve digitized
from PDG ref [35] — neither exists in this project.

## Recommended next action (not started)
A dedicated future task, explicitly scoped and time-gated, to: (1)
digitize the PDG MPV-dE/dx-vs-βγ curve (ref [35], figs 33.16/33.17-style
material already used elsewhere in this project for conversion
probability, so the reference is known); (2) compute per-hit path length
through each detector layer's silicon thickness (already have layer
geometry in `atlas_geometry.py`); (3) apply the MPV formula per hit; (4)
histogram over the existing signal samples' hits. This is feasible in
principle but was not attempted here per the explicit no-new-detector-
material-model-without-a-gate instruction.
