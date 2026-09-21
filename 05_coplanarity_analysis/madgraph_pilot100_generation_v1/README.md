# Bounded real-generation benchmark (v1) — 2026-09-21

## Status: BLOCKED — environment lacks a build toolchain (`make`)

## What was attempted

Per the task, a bounded ~100-event real-generation pilot was attempted for
both benchmarks, using the recovered original process directories as
immutable templates:

1. `rsync -a --exclude='Events/run_01'` copied the entire original EW
   process directory (`/home/rafia/hep_tools/quirk_ew_800gev_4kev/`) to a
   new, separate location (`/home/rafia/hep_tools/pilot100_runs/
   quirk_ew_800gev_4kev_pilot100v1/`) — **the original directory and its
   `Events/run_01` were never touched** (verified: `ls Events/` on the
   original still shows only `run_01` after this operation).
2. Verified the copy's `run_card.dat` matched the original run's actual
   settings exactly (diffed against the banner's embedded run_card for
   `ickkw`, `xqcut`, `ptj`, `etaj`, `pdlabel1`, `lhaid`, `ebeam` — zero
   differences) before editing anything.
3. Edited ONLY `nevents` (1000→100) and `iseed` (0/auto→**9101**, distinct
   from the original run's actual used seed, 21) in the copy's
   `run_card.dat`. `param_card.dat` (masses, charges, color reps) left
   byte-identical to the original.
4. Ran `/usr/bin/time -v ./bin/generate_events -f` inside the copy.

## What happened

The run failed after 6.63s wall time (4.19s user, 0.50s system, exit
status reported as 0 by `time` since the MadGraph shell itself exits
cleanly after catching the error — **the underlying generation did NOT
succeed**, confirmed by reading the actual command output, not just the
wrapper's exit code):

```
compile Source Directory
Error detected in "generate_events -f"
str : Impossible to compile .../Source directory
    Trying to launch make command returns:
        [Errno 2] No such file or directory: 'make'
    In general this means that your computer is not able to compile.
```

**Root cause verified directly** (not assumed): `which make gcc gfortran
g++ cc f77` returns nothing; `dpkg -l | grep -iE "gfortran|make "` shows
neither installed. This WSL environment has no C/Fortran build toolchain
at all. This is NOT a bug in the recovered cards, NOT a corruption of the
copied process directory (the precompiled `SubProcesses/*/madevent`
binaries were confirmed present and intact in the copy, 2.2MB, correct
permissions), and NOT something introduced by this task's copy operation
— `generate_events` unconditionally attempts a Source-directory
recompile-check as part of its normal startup sequence, regardless of
whether anything actually needs rebuilding.

## Why no workaround was attempted

- **Installing build-essential/gfortran** would require `sudo apt-get
  install`, a system-level package installation with a footprint beyond
  this task's own working directory — an environment-modifying action
  requiring explicit user authorization, not something to do unilaterally
  mid-task.
- **Patching MadGraph's internal Python** (`bin/internal/misc.py`) to
  skip the compile-check would modify the shared MadGraph installation
  itself (used by the original, still-preserved samples too) — too risky
  and out of scope for a "bounded benchmark."
- **Manually driving the precompiled `madevent` binaries directly**,
  bypassing MadGraph's own `generate_events` workflow entirely, would
  require independently reimplementing MadGraph's own survey/refine/
  combine orchestration logic outside its tested interface — high risk of
  a subtly wrong result that looks superficially plausible, which this
  project's entire methodology explicitly avoids.

Given all three options carry real risk or require authorization this
task didn't grant, the correct action was to **stop and report**, exactly
as the standing project convention requires for any blocker.

## Colored benchmark: not attempted

Since the blocker is a property of the environment (no `make` anywhere on
the system), not of the EW process directory specifically, attempting the
identical procedure for colored would fail identically and add no new
information. Per the task's own "do not launch a larger production"
framing, this was not run — re-confirming an already-diagnosed
environment-level blocker a second time would waste, not conserve,
resources.

## Partial data preserved (NOT authoritative — no new physics content)

- `logs/EW_pilot100_generate_events_attempt.log` — full `/usr/bin/time -v` output
- `logs/EW_pilot100_debug.log` — MadGraph's own debug traceback
- `metadata/EW_pilot100_run_card_ATTEMPTED.dat` — the edited run_card (nevents=100, iseed=9101), for reuse once a compiler is available
- The copied process directory itself remains at
  `/home/rafia/hep_tools/pilot100_runs/quirk_ew_800gev_4kev_pilot100v1/`
  (outside git, ready to resume immediately once `make`+`gfortran` are
  installed — no need to re-copy or re-edit cards)

## What CAN be computed from already-existing real data (not fabricated, not a substitute for the requested pilot)

The original 1000-event runs' own file modification timestamps give a
genuine (if partial) empirical timing data point for the shower+matching
stage only (LHE already existed; this measures Pythia8 shower+MLM-matching
wall time, not the MadGraph parton-level generation time, which has no
recorded start timestamp anywhere):

| Benchmark | Shower+matching wall time (1000 LHE events) | Per-LHE-event |
|---|---|---|
| EW | 28.196s | 0.0282s/event |
| Colored | 13.808s | 0.0138s/event |

**This is NOT a substitute for items 1-6 of the requested runtime
projection** (generation time per event, time per accepted matched event,
projected larger-sample/Figure-6 runtime) — those require the MadGraph
parton-level generation stage's timing, which this blocker prevented from
being measured. Only the shower+matching component has a real number;
the parton-level generation component remains genuinely unmeasured, and
projecting Figure 6 costs from an incomplete pipeline timing would be
exactly the kind of unfounded extrapolation this project avoids.

## Comparison with recovered original samples

**Not performed.** No new sample was generated (blocked before any events
existed), so there is nothing to compare. The existing
`madgraph_pilot_v1/` package's "comparison" (0.0 GeV exact match) remains
the only comparison data available, and it is explicitly a data-integrity
check against the SAME original files, not an independent new-sample
comparison, as already documented there.

## Exact next recommended action

1. **Explicit authorization request**: install a Fortran/C build
   toolchain (`sudo apt-get install -y build-essential gfortran`) — this
   is a system-level change and needs the user's explicit go-ahead before
   being run.
2. Once available, resume immediately from the already-prepared copy at
   `/home/rafia/hep_tools/pilot100_runs/quirk_ew_800gev_4kev_pilot100v1/`
   (cards already edited, nevents=100, iseed=9101) — no re-copying or
   re-editing needed, just re-run `./bin/generate_events -f`.
3. Prepare the equivalent colored copy (`quirk_signal_1800gev_2kev`,
   nevents=100, a distinct new seed e.g. 9102) the same way, sequentially
   after EW completes.
4. Only then compute the full runtime-projection items 1-6 from real
   measured numbers.

## Validation

- [x] Original `Events/run_01` for both benchmarks confirmed untouched (directory listing check before/after)
- [x] Root cause independently verified (`which`/`dpkg` checks), not assumed
- [x] Failure logged in full, not silently skipped
- [x] No workaround attempted without authorization
- [x] No fabricated timing/comparison numbers for the un-run pilot
