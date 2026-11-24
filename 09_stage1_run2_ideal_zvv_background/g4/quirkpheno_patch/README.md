# QuirkPheno patch (09, 2026-11-24)

`quirkpheno_09_vs_d91cb27.patch` holds every change of `hep_tools/QuirkPheno_fix` against QuirkPheno commit d91cb27 (github.com/tvami/QuirkPheno, Apache-2.0). Upstream QuirkPheno is not changed, and nothing is pushed there.

## Apply

```bash
git clone https://github.com/tvami/QuirkPheno.git QuirkPheno_fix && cd QuirkPheno_fix && git checkout d91cb27
git apply /path/to/quirkpheno_09_vs_d91cb27.patch
cmake -S . -B build -DCMAKE_PREFIX_PATH=$CONDA_PREFIX && cmake --build build -j8      # env g4
```

Verified on 2026-11-24: the patch applies cleanly on a fresh clone at d91cb27, and the result equals the QuirkPheno_fix sources.

## Contents

1. **Step-error fixes and options of G05 (2026-11-22)**:
   - `/quirk/secondOrderField` (second-order placement of the field kick);
   - `/qsim/field/deltaIntersection` and `deltaChord`;
   - delta chord passed to the quirk chord finder.

   These are used for the Athena runs (G05, G06, G08, G10–G13).
2. **Eq. 3 model (`/quirk/model eq3`), work in progress, NOT validated:**
   - `QuirkEq3Dop853`: C++ DOP853, bitwise identical to the numba module on all 176 G09 calls (G14);
   - `QuirkEq3Pair`: pair integration in time slices;
   - `QuirkEq3Stepper`: replay for G4PropagatorInField;
   - hooks in QuirkTransportation, QuirkWatcher, QuirkMessenger and QuirkPhysics;
   - the commands `/quirk/eq3Rtol` and `/quirk/eq3Slice`;
   - debug counters printed with `QUIRK_EQ3_DEBUG=1`.

   The default model is athena: without `/quirk/model eq3` the behaviour is that of item 1.

## Open problem in the eq3 model (G15, G16)

The solver, the replay (step points within 2 µm) and the path-length map (relative error 6e-14) are correct.

`QuirkEq3Stepper::DistChord()` returns 0. As a result:
- Geant4 locates boundaries on chords of a whole slice (17 mm at 0.1 ns);
- the first layer crossings of an oscillating quirk are missed;
- a later crossing is recorded instead (12–13 mm away), or none at all (L6 and L7 in G01 event 0, 4 keV).

Planned fix: a true `DistChord` from the dense output together with a fine `deltaChord`. Cross-check: a cap on the step length.

Until then, do not use the eq3 model for results.
