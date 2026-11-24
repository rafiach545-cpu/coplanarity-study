# Eq. 3 inside Geant4: design (2026-11-24)

Goal: one Geant4 chain for every stage. The quirk equation of motion is selectable:

- **`/quirk/model eq3`** (nominal): Eq. 3 of arXiv:1708.02243, integrated with the same error-controlled DOP853 as `03_trajectory_sim/quirk_trajectory_dop853.py` (rtol 1e-10, atol 1 nm and 1e-10 GeV).
- **`/quirk/model athena`** (systematic): the existing QuirkPheno string-vector model, unchanged.

SM particles, material, the field and the hits stay in Geant4. The code goes into `hep_tools/QuirkPheno_fix` (our patched copy). QuirkPheno itself is not changed.

## How QuirkPheno moves a quirk now

The code was read for this design. The relevant files are in `quirkcore/src`.

1. The two quirks are two Geant4 tracks. They are tracked in turn: one is suspended, the other resumes.
   - `QuirkWatcher.cc:73-83`: a track is suspended when its string has no vector left (`!HasNextStringVector()`).
   - `QuirkPhysics.cc:112-117`: the stacks for suspended tracks.
2. Each step, `QuirkTransportation::AlongStepGPIL` (`QuirkTransportation.cc`) does the following:
   - builds a `QuirkHyperbolaStepper`, a fake `G4MagIntegratorStepper` that replays precomputed exact segments;
   - wraps it in a `G4ChordFinder` / `G4MagInt_Driver`;
   - calls `G4PropagatorInField::ComputeStep`, so Geant4's own chord and intersection code finds the volume boundaries on the replayed path;
   - `GetMaxLength()` is how far the replay is known.
3. The coupling between the quirks is retarded, through string vectors moving at the speed of light (`QuirkInfracolorForce`). That is the Athena model.

## Eq. 3 in the same slots

Eq. 3 couples the two quirks at **equal lab time**. So the pair is integrated jointly, and each Geant4 track replays its half.

| Piece | What it does |
|---|---|
| `QuirkEq3Pair` (new, per thread, owned like `QuirkStringStore`) | The 12-component pair state, a C++ port of our numba DOP853 (same coefficients and controller; `quirk_dop853_coefficients.npz` = scipy's), the same right-hand side as `quirk_trajectory_numba._rhs`, B from the Geant4 field at each stage point. It integrates the pair over a **time slice** [t_k, t_k + Δ] and keeps the dense output of the slice. |
| `QuirkEq3Stepper` (new, like `QuirkHyperbolaStepper`) | It replays this quirk's dense output as a function of path length s; s(t) comes from the dense speed and is monotonic. State layout as now (x, p, Ekin, t, s). `yerr = 0`, `GetMaxLength()` = the path length up to the end of the slice. |
| `QuirkTransportation` | It builds `QuirkEq3Stepper` instead of `QuirkHyperbolaStepper` when the model is eq3. Everything else is unchanged, including the boundary finding, which is Geant4's. |
| `QuirkWatcher` | Model eq3: suspend when the track has reached the end of the current slice. The partner is resumed and tracked to the same slice end. When both are there, the next slice is integrated from the two **actual** Geant4 states. |
| `QuirkMessenger` | Commands `/quirk/model eq3|athena`, `/quirk/eq3/rtol`, `/quirk/eq3/slice` (Δ in ns). |

### Material (Stage 2)

Geant4 changes a quirk's momentum (energy loss) and direction (multiple scattering) at its own step ends. Two rules handle this:

1. A slice always starts from the two actual Geant4 states.
2. Inside a slice, if the track that is moving deviates from its replayed state beyond a tolerance, the pair is re-integrated from that track's time. Its actual state and the partner's state from the slice solution at that time are used.

The partner of the first track replays a solution that did not know about that track's later material kicks inside the slice. The error is of order Δ times the effect of the kick. Δ is a parameter; convergence in Δ is a test (Δ, Δ/2, Δ/4).

**Without material nothing deviates.** Then the Geant4 chain is exactly our DOP853 Eq. 3, up to rtol and the slice restarts. That is what the equivalence test (step 7) checks.

## Tests, in order

1. Unit tests:
   - C++ DOP853 vs numba DOP853 on the G09 cases (exact helix, exact 1D string, conservation at B = 0, the 4 G08 events), agreement at the 1e-10 level;
   - slice independence (Δ = 1, 0.1, 0.01 ns) without material.
2. G10 again with `g4_eq3`: G4(eq3) vs DOP853 must be ≪ 1 µm at every Λ.
3. Equivalence test (G4_FLOW step 7), material off:
   - the same 1k events through G4(eq3) and the DOP853 chain;
   - hits in-plane and out-of-plane, fiducial and SR decisions per event: 0 flips expected.
   - If it passes, the DOP853 regen results count as the Stage 1 results.
4. Then full events (step 6), material (Stage 2), and the Δ convergence with material.

## Size

About 600–900 lines of C++ (DOP853 with dense output about 300; pair store and slices about 200; stepper about 150; messenger and watcher hooks about 100), plus the tests.

This is laptop work. Only the 1k-event equivalence test and the production go to the server.
