# NLO Compilation Failure — Root Cause Diagnosis

Scope: diagnose (not silently fix) why the pre-existing NLO attempt at
`/home/rafia/hep_tools/zgamma_nlo_test/` (found already on disk, dated
2026-09-14, before this audit) never produced a cross section. The
original failed attempt was **not modified or rerun** — only inspected
and reasoned about.

## Symptom (previously reported)

`run_01_tag_1_debug.log`: compiling the physics process directory
`P0_dxd_za` fails at the final link step of `test_soft_col_limits`:
```
undefined reference to `fastjet::Error::Error(std::__cxx11::basic_string<...>const&)'
```

## Root cause (newly identified this session)

This is **not** a problem with the physics process code. It traces back
to MG5's own bundled dependency, FastJet, which was **never successfully
built** in the first place:

- `/home/rafia/hep_tools/MG5_aMC_v3_7_3/HEPTools/fastjet/` contains only
  a `fastjet_install.log` — no `lib/libfastjet.so` exists at all
  (confirmed directly: `find ... -iname "libfastjet*"` returns nothing,
  `fastjet-config` binary is absent).
- Reading `fastjet_install.log` in full: FastJet 3.4.2's own build
  **failed at its own shared-library link step**:
  ```
  /home/rafia/miniforge3/envs/hep/bin/x86_64-conda-linux-gnu-ld:
    .../crtbeginS.o: in function 'deregister_tm_clones':
    crtstuff.c:(.text+0xa): undefined reference to `__TMC_END__'
  ... relocation R_X86_64_PC32 against undefined hidden symbol
      `__TMC_END__' can not be used when making a shared object
  collect2: error: ld returned 1 exit status
  make[1]: *** [Makefile:541: libfastjet.la] Error 1
  ```
  This is a known class of incompatibility between newer conda-forge GCC
  versions (this environment: GCC 16.2.0 via
  `/home/rafia/miniforge3/envs/hep`) and older autotools/libtool-
  generated shared-library link commands that pass `-nostdlib` and
  expect the compiler driver to supply matching `crtbegin`/`crtend`
  objects with transactional-memory (`__TMC_END__`) support resolved.
  It is a **toolchain incompatibility bug, not a FastJet or MadGraph
  physics-code bug**.
- Despite this failure, MG5's own installer script printed "Finished
  fastjet installation" and proceeded anyway — **it did not check the
  build's exit status**. This left a broken/absent FastJet install that
  every subsequent NLO compile (which links against FastJet C++ code via
  `fastjetfortran_madfks_full.cc`) was doomed to fail against, exactly as
  observed in the original symptom above.
- Additionally (independently) noted: the original NLO attempt's
  `run_card.dat` never set the `misset` (MET) cut at all — so even a
  successful FastJet build and compile would not, as configured, have
  produced a directly paper-comparable number without a further card fix.

## Why this was not repaired in this session

- **No alternative compiler exists on this machine.** `which gcc g++`
  finds nothing; only `gcc-14-base`/`libgcc-s1` metadata packages are
  installed at the system level (no actual system GCC binary). The
  conda `hep` environment's GCC 16.2.0 is the only compiler available
  anywhere on this machine, and it is the one with the incompatibility.
- A real fix would require either (a) installing a working system-level
  C/C++ toolchain (`apt install build-essential` or similar) — a
  system-wide package-management change, not something confined to a
  disposable build directory, and one that could affect the existing
  conda `hep` environment's other builds — or (b) patching FastJet's
  build flags (e.g. dropping `-nostdlib`, adding `-fno-lto`, or forcing
  a different `crtbegin`/`crtend` pair) inside a disposable rebuild,
  which is a nontrivial, open-ended autotools/libtool debugging exercise
  with real risk of producing a subtly miscompiled library if rushed.
- Per the explicit constraint to repair only inside a disposable
  directory or this audit folder and to never modify the authoritative
  MadGraph/conda installation, and given no safe disposable-only fix was
  identified within this session's scope, this is reported as a genuine
  blocker requiring an explicit decision, not silently worked around.

## Classification

**UNRESOLVED — blocked by a pre-existing, independently-caused toolchain
bug** (conda-forge GCC 16.2 + libtool shared-library linking), not by
anything wrong in this project's physics code, cards, or process
definition. The original failed attempt is preserved unmodified at
`/home/rafia/hep_tools/zgamma_nlo_test/`.

## What would be needed to actually resolve it (for an explicit decision, not acted on here)

1. Install a working system C/C++ toolchain independent of the conda
   `hep` environment's GCC 16.2 (e.g. via `apt install build-essential`,
   requires sudo — a system-level change outside this audit's authorized
   scope), OR
2. Rebuild FastJet 3.4.2 in a disposable directory with modified
   configure/link flags to work around the `__TMC_END__` issue (e.g.
   `--disable-shared` to build a static library instead, which sidesteps
   the shared-library link path entirely — this is the most promising
   disposable-only option and could be attempted if authorized), then
   point a fresh, disposable NLO process directory's link step at that
   static library.
