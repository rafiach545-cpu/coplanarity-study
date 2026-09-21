# Bounded real-generation benchmark (v1) — 2026-09-21

## Status: BOTH BENCHMARKS COMPLETED SUCCESSFULLY, toolchain blocker resolved

**Caveat, stated up front and throughout: 100 requested events measures
RUNTIME AND CONFIGURATION REPRODUCIBILITY, not precision physics
agreement.** N=60 (EW matched) / N=49 (colored matched) give ~13-14%
relative statistical uncertainty on any efficiency/cross-section — these
are feasibility/timing numbers, not a precision remeasurement of the
existing 1000-event authoritative samples.

## Phase 1: isolated conda toolchain (no sudo used)

```
conda create -n mg5_build_tools -y -c conda-forge make gcc_linux-64 gxx_linux-64 gfortran_linux-64
```

The `hep` environment (used for all physics analysis in this project) was
never touched. Conda-forge's compiler packages install only
target-triple-prefixed binaries (`x86_64-conda-linux-gnu-gcc`, etc.), not
plain `gcc`/`g++`/`gfortran` — three symlinks were created **inside
`mg5_build_tools`'s own `bin/` directory only** (never system-wide) to
resolve this: `gcc`, `g++`, `gfortran`, `cc` → their prefixed targets.

Full verification (versions, `which` output, `$PATH`, `$CONDA_PREFIX`,
`conda list`) saved in `toolchain/`. A minimal C program, Fortran
program, and a `Makefile` building both were compiled and executed
successfully (`toolchain/COMPILE_TEST_RESULT.txt`) before touching
MadGraph at all.

**Phase 2 (sudo fallback) was never needed** — the conda toolchain fully
resolved the blocker.

## First attempt (from the prior task) — preserved as PARTIAL_NOT_AUTHORITATIVE

The original (pre-toolchain) `generate_events` attempt failed before
producing any events (see the earlier commit `52d8315`). Its partial
files (a stray debug log, `crossx.html`, `index.html` — no actual run
directory was ever created) were moved into
`/home/rafia/hep_tools/pilot100_runs/quirk_ew_800gev_4kev_pilot100v1/
FAILED_ATTEMPT_PARTIAL_NOT_AUTHORITATIVE/` before the successful rerun,
which used a new run name (`run_pilot100`) to avoid any ambiguity.

## Results

| | EW | Colored |
|---|---|---|
| Requested LHE events | 100 | 100 |
| Generated LHE events | 100 | 100 |
| Matched (shower+MLM) events | 60 | 49 |
| Matching efficiency (this pilot) | 60% | 49% |
| Matching efficiency (original, 1000 evt) | 51.1% | 41.9% |
| Parton-level cross section | 4.410978e-4 pb | 7.498129e-4 pb |
| Matched cross section | 2.647e-4 ± 2.19e-5 pb | 3.674e-4 ± 3.75e-5 pb |
| Matched xsec vs original (1000evt) | ratio 1.13× | ratio 1.17× |
| KS test vs original (quirk-pair pT shape) | stat=0.061, **p=0.981** | stat=0.170, **p=0.138** |
| Wall time (full chain, incl. one-time compile) | 172.22s | 39.77s |
| Seed used | 9101 (original: 21) | 9102 (original: 21) |
| Exit code | 0 | 0 |

Both KS p-values are well above any conventional significance threshold
— the pilot samples' shapes are statistically indistinguishable from the
existing 1000-event authoritative samples, exactly as expected for two
independent draws from the same physical configuration.

## Validation gates: ALL PASSED

- [x] Requested/generated/showered/matched counts all internally consistent (100→100→60/49)
- [x] No NaN, no Inf in `quirk_pair_pt_gev` (either benchmark)
- [x] No duplicate `hepmc_event_idx`
- [x] All event weights finite
- [x] Original `Events/run_01` directories confirmed byte-identical (SHA-256) before and after — **originals never touched**

## Runtime projections (items 1–6, all from real measured numbers)

Full detail and caveats in `RUNTIME_PROJECTIONS.json`. Summary:

1. **Generation time/requested event** (upper bound, includes one-time compile): EW 1.72s, colored 0.40s
2. **Shower/matching time/LHE event** (cleanly separable, no compile cost): EW 0.04s, colored 0.03s
3. **Time/matched event** (upper bound): EW 2.87s, colored 0.81s
4. **Projected colored larger-sample runtime** (894 charge-filtered events target, using this pilot's real 49% matching efficiency): **6122 requested events, ≈0.68h** — previously "unknown," now bounded and small
5. **Projected Figure 6 generation-only cost**: **13 distinct mass points** (7 colored + 6 EW, NOT 91 — see item 6), 2000 events/point: **≈12.7h total** (3.16h colored + 9.57h EW)
6. **Revised full Figure 6 runtime**: generation (12.7h) + downstream trajectory/detector/reconstruction (**425h, unchanged from the Phase-7 estimate — Λ genuinely requires a separate propagation run per (mQ,Λ) combination, this saving does not apply there**) = **≈437.7h total, generation is only ~2.9% of it**. The previously-complete generation-time unknown is now resolved: it was never the dominant cost.

## Comparison methodology note

Unlike `madgraph_pilot_v1/` (which extracted from the SAME original files
and therefore showed trivial 0.0 GeV exact agreement), this package's
comparison is a **genuine independent statistical cross-check** — new
events, new seed, same configuration — making the KS-test agreement a
real, meaningful validation of configuration reproducibility.

## Directory structure
- `toolchain/` — conda build-tools verification (versions, compile test, package list)
- `EW/`, `colored/` — per-benchmark cards, logs, event tables, raw compressed LHE/HepMC, figures, metadata
- `RUNTIME_PROJECTIONS.json` — items 1–6
- `SHA256_MANIFEST.txt` — hashes of every committed file

## What was NOT done (per explicit instruction)

No Figure 6 grid launched. No larger colored-statistics production
launched. EW and colored were run strictly sequentially, never
concurrently (verified: colored's `generate_events` was only started
after EW's had fully exited with confirmed exit code 0).

## Next recommended action

With the generation-time unknown now resolved and shown to be a small
fraction of the total Figure 6 cost, the real remaining question is
whether to authorize the downstream 425h trajectory/detector/
reconstruction stage (91 mQ-Λ combinations) — that decision, and its own
checkpoint/resume design, should be a separate, explicitly authorized
future task, not an automatic next step from this one.
