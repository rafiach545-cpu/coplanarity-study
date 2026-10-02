# NLO Repair Attempt — Disposable Static FastJet Build

Following the root-cause diagnosis in `NLO_COMPILATION_FAILURE_DIAGNOSIS.md`
(MG5's bundled FastJet shared-library build silently failed due to a
conda-forge GCC 16.2 `__TMC_END__` linker incompatibility), a repair was
attempted entirely inside a disposable directory
(`/tmp/fastjet_disposable_build/`, NOT inside the authoritative
`MG5_aMC_v3_7_3` installation and NOT inside the original failed
`zgamma_nlo_test` directory).

## What was done

1. Downloaded FastJet 3.4.2 source directly from fastjet.fr (matching the
   exact version MG5's own installer had attempted).
2. Configured with `--disable-shared --enable-static` — this sidesteps
   the shared-library link path entirely (the `__TMC_END__` error only
   occurs when linking a `.so`; a static `.a` archive is just `ar`
   + `ranlib`, no problematic final link step).
3. Built with the same conda `hep` environment's GCC 16.2 (no alternative
   compiler exists on this machine — confirmed via `which gcc g++`).

## Result: SUCCESS

- `libfastjet.a` and its dependent static libraries (SISCone, CDFCones,
  NestedDefs plugins, fastjettools) all built cleanly, no linker errors.
- `fastjet-config --version` → `3.4.2`, confirms a working install at
  `/tmp/fastjet_disposable_build/install/`.

This confirms the diagnosis: the failure was specifically about
shared-library linking, not about compiling FastJet's source code itself
against this GCC version.

## What remains before an actual NLO cross-section can be obtained

Having a working static FastJet does not, by itself, fix the original
`zgamma_nlo_test` process directory — that directory's own compiled
SubProcesses (`P0_dxd_za` etc.) still expect to link against the
HEPTools shared FastJet (`-lgeneric -lmodel -lpdf ... ` link line
references the MG5-bundled HEPTools path). Pointing a *fresh* NLO process
directory's build at this disposable static library instead would
require either:
(a) overriding the `fastjet` path in a fresh process directory's
`Cards/me5_configuration.txt` / `Source/make_opts` to point at
`/tmp/fastjet_disposable_build/install/bin/fastjet-config` before that
directory's first compile (untested — MG5's build system may or may not
cleanly accept a static-only fastjet-config in place of its expected
shared one), or
(b) manually relinking the existing failed `P0_*` object files against
the new static library (fragile, not recommended).

## Update: the repair was completed and the NLO compile actually succeeded

Option (a) was attempted and worked. A fresh disposable NLO output
directory (`generation/nlo_pilot_attempt/`, process `p p > z a [QCD]`,
matching the original failed `zgamma_nlo_test`'s process) was generated
via `mg5_aMC`, and its `Cards/amcatnlo_configuration.txt` was edited to
point `fastjet = /tmp/fastjet_disposable_build/install/bin/fastjet-config`
(a change to this audit's own disposable output directory only, not to
the authoritative MG5 install or the original failed attempt).

Compiling this fresh directory hit the FastJet-related link step
successfully this time (no `undefined reference to fastjet::Error`
error). A second, independent, unrelated blocker then appeared:
```
./check_poles: error while loading shared libraries: libninja.so.0: cannot open shared object file: No such file or directory
```
Diagnosis: the library file **does exist**
(`/home/rafia/hep_tools/MG5_aMC_v3_7_3/HEPTools/lib/libninja.so.0`) — this
was a missing `LD_LIBRARY_PATH` entry, not a build failure. Fixed by
exporting `LD_LIBRARY_PATH` to include that HEPTools lib directory for
this audit's own subprocess invocation only (no change to any
authoritative file, no shell profile or conda-env-wide change).

With both fixes applied, the NLO compile **fully succeeded**:
```
INFO:  Result for test_ME:      Passed.
INFO:  Result for test_MC:      Passed.
INFO:  Result for check_poles:  Poles successfully cancel for 20 points over 20 (tolerance=1.0e-05)
```
for all 4 subprocess channels (P0_uux_za, P0_ddx_za, P0_uxu_za,
P0_dxd_za). **This conclusively resolves the original NLO compilation
blocker** — the root cause (broken FastJet + missing library path) is
fixed, entirely within disposable/local scope, with no modification to
the authoritative MadGraph installation.

## The resulting cross-section number is NOT directly paper-comparable

The pilot run then completed and reported:
```
Total cross section:      1.175e+03 +- 1.6e+01 pb
```
This is **~5000x larger** than the LO baseline (0.23 pb) and cannot be
interpreted as an NLO/LO K-factor. The reason: this NLO process
definition, `p p > z a [QCD]`, produces an **on-shell, undecayed Z
boson** (matching the original failed attempt's process exactly) —
unlike the LO baseline's explicit `z > vl vl~` decay chain. Consequences:
- No Z→νν branching ratio (~20%) is applied, since the Z is not decayed
  to any specific final state.
- No MET cut could be applied (MET requires neutrinos from a decayed Z;
  the NLO run_card template for this process has no `misset` parameter
  at all, confirmed by direct inspection).
- The result is therefore the **fully inclusive p p → Zγ(+jet) NLO
  cross section**, a different and much less restrictive observable
  than either the paper's ~1 pb (post Z→νν decay, post MET>200 GeV) or
  this project's 0.23 pb LO baseline (which does include both).

**A genuine, paper-comparable NLO number would require** adding the
Z→νν decay to this NLO computation — either via MadSpin's spin-correlated
decay applied to the NLO sample, or by using a process definition that
decays Z inline in a way compatible with NLO+FKS subtraction (nontrivial;
simply writing `z > vl vl~` in the `[QCD]`-order NLO generate command was
not attempted here due to time already invested in this session) — plus
reintroducing an equivalent MET cut. This was not completed.

## Classification (revised from the earlier UNRESOLVED verdict)

**NLO compilation: RESOLVED** (root cause fixed, fully reproducible,
confirmed via a clean successful compile+run). **NLO cross-section for
the paper-comparable observable: STILL NOT OBTAINED** — a different,
harder sub-problem (adding the Z→νν decay to the NLO computation) that
was not attempted. The K-factor question therefore remains open, but for
a different, now well-defined reason than before (no longer "can't even
compile," now "need to add the correct decay chain to a working NLO
setup").
