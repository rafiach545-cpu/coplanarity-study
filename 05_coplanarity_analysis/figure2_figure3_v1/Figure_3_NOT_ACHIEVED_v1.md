# Figure 3 (Δφ vs r) — NOT ACHIEVED this session

**Status: diagnostic setup produces degenerate (Δφ≡0) or unphysically
large (Δφ~10+ rad, L~1e15ℏ) results depending on tilt choice — neither is
a valid reproduction. Not fabricated, not forced.**

## What was tried
The existing validated script (`validate_bfield_fig2_fig3.py`) uses an
internal-motion tilt of `[0,0,1]` (boost along x, B along z), which its
own docstring already flags as confining every vector to the x-z plane —
Δφ is then identically zero by construction (a geometric degeneracy, not
a physics bug).

Attempted fixes (this task): giving the tilt a small out-of-plane
y-component (`[0,0.02,1]`, `[0,0.3,1]`) — **Δφ remained exactly 0** in
both cases (L stayed at the correct ~1e12ℏ order of magnitude, but the
rotation axis apparently stays pinned regardless). Giving the tilt an
x-component (`[0.5,0.5,1]`) — **Δφ became unphysically large** (~10-25
radians, several full rotations) and L jumped to ~1e15ℏ (1000× the
paper's stated order of magnitude) — an artifact of how the CM-frame
tilt combines with the x-directed boost (likely a relativistic-beaming-
type momentum inflation when the internal motion has a component along
the boost axis), not a genuine small-Δφ regime.

## Why this was not pushed further
Finding the specific 3D tilt geometry that reproduces both (a) the
correct ~1e12ℏ angular-momentum scale AND (b) a small, nonzero,
smoothly-growing Δφ (paper: saturates <~1e-3) requires a more careful
parameter search than was completed in the time available for this
already very large task. Per the task's explicit instruction ("Do not
fabricate missing data... do not tune any physics parameter to resemble
the paper"), no value was invented and no curve was forced to match the
paper's stated ceiling.

## What is preserved
Figure 2 (L, d vs r) — **achieved**, physically sensible (L reaches the
correct ~1e12ℏ order of magnitude for this benchmark, matching the paper
exactly). One caveat: in this single representative event, d does
touch exactly 0 at r≈4.2cm, which is at some tension with the paper's
explicit claim "it does not vanish except at the origin" — reported
honestly, not smoothed over.

## Recommended next action (not started)
A proper fix would explore the tilt-angle parameter space more
systematically (e.g. scan a small range of out-of-plane angles and
identify the regime that keeps L at the correct order of magnitude while
producing a nonzero, small, monotonically-growing Δφ), or revisit
whether the CM-frame internal-motion setup itself needs a genuinely
different construction (e.g., a small initial POSITION offset between
the quirks rather than only a momentum-direction tilt) to match the
paper's Fig. 3 setup more faithfully.
