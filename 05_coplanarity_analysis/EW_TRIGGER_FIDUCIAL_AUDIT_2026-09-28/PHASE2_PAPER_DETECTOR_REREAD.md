# Phase 2 — Paper and Detector Reference Reread

Read directly this session: Sec. III A (signal simulation), Sec. III B
(trigger), Sec. III C (plane-finding), Sec. IV (fiducial/reconstruction
efficiencies, Eq. 12), Table I, Figs. 2-5 captions (already read and
recorded across this session's prior phases; re-confirmed here). The
detector reference itself, ATL-PHYS-PUB-2009-002 / ATL-COM-PHYS-2008-105,
is a CERN internal/public note **not present in this project's cached
paper extraction or local files** — it could not be directly read in
this audit; every claim referencing it is marked UNRESOLVED or INFERENCE
accordingly, never asserted as verified against its actual numbers.

## Answers, with evidence labels

**1. Where does the paper state barrel-only restricts acceptance to
|η|≲1.8?**
Sec. III A, p.4 (paper.txt lines 409-411), exact quote:
> "For simplicity, we only included the barrel of the pixel and SCT
> detectors in our simulations, which effectively restricts the
> fiducial range to |η| ≲ 1.8."
**[DIRECT PAPER EVIDENCE]**

**2. Does the paper impose a direct crossing-point η cut, finite layer z
boundaries, or only describe an effective barrel acceptance?**
The paper's own wording ("effectively restricts... ≲1.8") describes this
as a **consequence** of including only barrel detector elements (which
are physically finite-length cylinders per ref [27]'s specifications),
not as an independently-imposed analysis cut with its own citation or
formula. The paper never writes an equation or explicit rule "reject any
hit with |η|>1.8" — the 1.8 figure is presented as an approximate,
descriptive summary of what finite barrel geometry implies.
**[DIRECT PAPER EVIDENCE for the wording; INFERENCE that this describes
a finite-z geometric truncation rather than a literal η-cut, since the
paper's own simulation code is not available to confirm directly]**

**3. Does the project apply both finite-z and η acceptance?**
No. Confirmed by direct code search (`grep` across
`atlas_geometry.py` and `trajectory_to_hits.py` for `z_max`, `Z_MAX`,
`half_length`, `z_boundary`, `ZMAX`, `barrel_z`, `z_extent`): **zero
matches**. The project applies **only** a per-hit constant-|η| cut
(`FIDUCIAL_ETA_MAX = 1.8`, evaluated via
`eta_from_theta(arctan2(r, z))` at each individual layer crossing) — no
separate finite-z boundary exists anywhere in the code.
**[PROJECT IMPLEMENTATION — verified directly, not inferred]**

**4. If both existed, would they double-count acceptance?**
Not applicable — only one mechanism exists (§3), so there is no
double-counting in the code as written. However, this raises a more
important, previously-unexamined question (§ next):

## A geometrically demonstrated modeling difference (new this phase)

A **constant-|η|<1.8 cone** and a **finite-length barrel cylinder** (the
literal, physical description implied by "we only included the barrel...
of the pixel and SCT detectors," each of which is a real, finite-length
cylindrical detector element per ref [27]) are **not the same
acceptance shape**, and diverge substantially at small radius. Direct
calculation (this audit): for an illustrative barrel half-length
(80 cm — **not independently verified against ref [27]'s actual
number, used only to demonstrate the qualitative/quantitative shape of
the effect**), the *implied* η acceptance at each layer radius would be:

| Layer | r (cm) | η-cut project uses | η-bound implied by an illustrative fixed 80cm half-length barrel |
|---|---|---|---|
| L1 IBL | 3.33 | 1.8 | 3.87 |
| L2 | 5.05 | 1.8 | 3.46 |
| L3 | 8.85 | 1.8 | 2.90 |
| L4 | 12.25 | 1.8 | 2.58 |
| L5 SCT | 29.9 | 1.8 | 1.71 |
| L6 | 37.1 | 1.8 | 1.51 |
| L7 | 44.3 | 1.8 | 1.35 |
| L8 | 51.4 | 1.8 | 1.23 |

A true finite-length cylinder is **looser** than a constant-η cone at
small radius (inner layers) and **tighter** at large radius (outer
layers) — the opposite radial dependence. **This is directly relevant**:
all 30 classified "eta-drift barrel loss" events (Phase 1) were rejected
at crossing-point |η| in the range 1.86–3.04 — values that would fall
**within** the illustrative finite-length barrel's acceptance at the
inner layers (up to 3.87 at L1) shown above.
**[INFERENCE, explicitly hedged]**: this does **not** prove the paper's
own simulation used a finite-length-cylinder geometry rather than a
constant-η cut — ref [27]'s exact dimensions were not available to
confirm this directly, and the paper's own code is not published. It
demonstrates only that **if** the paper's actual implementation modeled
real finite-length barrel elements (the literal reading of its own
sentence) rather than a hard constant-η cut (the project's
implementation), a materially different, generally *looser* acceptance
at inner layers would result — which would be a candidate contributor to
the fiducial-efficiency gap, quantitatively unverified here.

**5. Verification of layer radii, longitudinal dimensions, timing
definition, beamspot treatment, hit acceptance:**
- **8 layer radii**: 3.325, 5.05, 8.85, 12.25 (pixel/IBL), 29.9, 37.1,
  44.3, 51.4 cm (SCT) — matches standard public ATLAS Run-2 values,
  consistent with ref [27]'s subject matter (previously verified in this
  project's `PAPER_REQUIREMENTS.md` row 6; re-confirmed, not
  re-independently-derived this session). **[PROJECT IMPLEMENTATION,
  DETECTOR-REFERENCE EVIDENCE by consistency, not independently
  re-checked against ref [27]'s primary text this session]**
- **Longitudinal dimensions (finite z half-lengths)**: **not
  implemented at all** in the project (§3) — **[UNRESOLVED]** whether
  ref [27] specifies these and whether the paper used them.
- **Timing definition**: paper states "the quirks must reach the muon
  chamber in less than 25 ns" (Sec III B, motivating context) and
  "we also include a 25 ns timing cut" (Sec IV, applied to the fiducial
  definition). The project applies this to the **last (outermost)
  tracker-layer crossing time**, not the literal muon-chamber arrival
  time — **[PROJECT APPROXIMATION]**, previously flagged in
  `paper_vs_project_requirements.csv`, unchanged this session.
- **Beamspot treatment**: paper: "gaussian smearing with width 45 mm to
  the z-coordinates" (Sec III A). Project: `BEAMSPOT_SIGMA_Z_CM = 4.5`
  (cm) = 45 mm, applied once per event as a shared vertex z-offset for
  both quirks, matches exactly. **[PROJECT IMPLEMENTATION, verified
  matching DIRECT PAPER EVIDENCE]**
- **Hit acceptance**: per-hit, per-layer, constant |η|<1.8 (§3) — no
  further acceptance logic. **[PROJECT IMPLEMENTATION]**

**6. Summary of evidence labels used above**: DIRECT PAPER EVIDENCE (2
instances), PROJECT IMPLEMENTATION (4 instances), PROJECT APPROXIMATION
(1 instance), INFERENCE (2 instances, both explicitly hedged), UNRESOLVED
(1 instance — finite-z dimensions vs ref [27]). No conclusion is forced
where the paper does not provide enough information — the finite-z
question is left explicitly UNRESOLVED, not guessed.
