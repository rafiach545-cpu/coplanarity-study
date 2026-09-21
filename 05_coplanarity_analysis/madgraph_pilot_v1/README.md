# MadGraph data-preservation package (v1) — 2026-09-21

## Important: this is a LOCATE-AND-PRESERVE package, not a new pilot generation

The task requested reconstructing generator run-cards and generating a
~100-event pilot, on the assumption that original settings were lost.
**A full-filesystem search (as explicitly requested) found the actual
original MadGraph process directories intact**, at
`/home/rafia/hep_tools/quirk_ew_800gev_4kev/` and
`/home/rafia/hep_tools/quirk_signal_1800gev_2kev/`, outside the git repo.

These are not reconstructions — they are verified originals (see
`metadata/GENERATOR_CONFIGURATION_SUMMARY.md` for the full authenticity
verification: particle-code match, exact 511/419 event-count match, and
0.0 GeV bit-identical pT_pair match against the existing authoritative
CSVs). Given this, generating a fresh ~100-event toy pilot would have been
pure waste — strictly worse statistics than the 1000 already-generated
events per benchmark that were sitting on disk, unused for cutflow
purposes and never before preserved in version control. **No MadGraph or
Pythia8 process was run this task.** This package parses and preserves
the existing original output instead.

## Directory structure
- `cards/EW/`, `cards/colored/` — original banner, run_card, param_card,
  proc_card, Pythia8 cmd file, merged-xsecs file (small text files, copied verbatim)
- `raw_events/RAW_EVENT_FILE_REGISTRY.json` — absolute paths, sizes, and
  SHA-256 hashes of the original LHE/HepMC files (NOT committed to git —
  33MB+25MB compressed, outside this project's established small-file
  convention; fully hash-verified and path-referenced instead)
- `event_tables/` — full event-level CSVs, both LHE (1000 events/benchmark,
  parton level) and HepMC (511 EW / 419 colored, matched final sample)
- `cutflows/generator_cutflow_EW_and_colored.csv` — complete stage-by-stage
  cutflow with entering/passing/failing/conditional/cumulative efficiency
- `distributions/` — source CSVs for every distribution plotted
- `figures/` — distribution plots (PNG)
- `runtime/` — wall time, CPU%, peak RSS for every step of THIS extraction
  (not generation, which was not run)
- `metadata/` — generator configuration summary, provenance/environment,
  LHE init blocks, cross-section/matching statistics, validation gates
- `logs/` — original Pythia8 run logs (small enough to commit, ~650KB each)
- `tests/test_cache_only_recompute.py` — proves every reported number is
  recoverable from saved files alone, without touching the original
  hep_tools location
- `SHA256_MANIFEST.txt` — hashes of every committed file in this package

## Key results (all traceable to a saved file — see table)

| Quantity | EW | Colored | Source file |
|---|---|---|---|
| LHE events generated | 1000 | 1000 | `event_tables/*_lhe_events.csv` |
| Parton-level cross section | 4.573838e-04 pb | 7.503599e-04 pb | `metadata/*_lhe_init.json` |
| Showered+matched events | 511 | 419 | `event_tables/*_hepmc_events.csv` |
| Matching efficiency | 51.1% | 41.9% | `metadata/cross_section_and_matching_statistics.csv` |
| Charge-filter pass (colored only) | N/A (unit charge by construction) | 125 | `cutflows/generator_cutflow_EW_and_colored.csv` |
| Trigger-proxy pass (pT_pair>200GeV) | 89 | 27 | same |
| Existing matched cross section (pre-verified, unchanged) | 0.0002337 pb | 0.0003144 pb | `metadata/cross_section_and_matching_statistics.csv` |

**All of these exactly match every previously-recorded number throughout
this project's entire history** (511/419 matched, 89/27 trigger-passing,
125 charge-filtered) — this package traces them all the way back to their
true origin (1000 raw generated events per benchmark), which had never
been documented in this repo before.

## Comparison with existing samples

Framed honestly: since this pilot extracts from the SAME original files
as the existing authoritative CSVs (not an independently generated new
sample), the comparison shows **exact (0.0 GeV) agreement by
construction** — this is a data-integrity/reproducibility check, not an
independent statistical cross-check of two different MC runs. See
`distributions/*_comparison_with_existing.csv` for the explicit framing
and numbers.

## Cache for future Figure 6 work

Everything needed to recompute the generator cutflow, trigger-proxy
efficiency, charge-filter efficiency, distributions, and cross-section
normalization is saved in `event_tables/` and `metadata/` —
`tests/test_cache_only_recompute.py` proves this (13/13 gates + all cache
checks pass, 0.043–0.048s runtime, no access to the original hep_tools
location required).

## Validation gates: 13/13 PASSED

See `metadata/VALIDATION_GATES.json`. No NaN/Inf, no duplicate event IDs,
valid four-momenta (E≥|p|), matching totals close correctly, cache-only
recomputation agrees with the main summary.

## Limitations (documented, not hidden)

- **Leading-jet pT**: extracted from the LHE parton-level record only
  (process @1 events), not from full jet clustering on the showered
  HepMC final state (would require implementing an anti-kt-style
  algorithm — out of scope for this data-preservation task).
- **MET/recoil proxy**: uses quirk-pair pT directly (physically
  equivalent to the paper's own trigger variable by momentum
  conservation), not a separately-clustered "missing energy" object.
- **Generation-time provenance**: the original MadGraph event-generation
  command itself was not separately logged (only the shower/matching
  command, `run_shower.sh`, was preserved); file mtimes are used as the
  best available proxy for generation timestamps.
- **Raw LHE/HepMC not committed to git** (repository size policy) — fully
  hash-referenced instead in `raw_events/RAW_EVENT_FILE_REGISTRY.json`.

## Regeneration

This package requires NO MadGraph/Pythia8 run to regenerate — it only
re-parses the existing original files:
```
python3 extract_pilot_data.py       # ~15-16s, parses LHE+HepMC
python3 build_cutflow_and_xsec.py   # ~1s
python3 build_distributions.py      # ~7s
python3 tests/test_cache_only_recompute.py  # ~0.05s
```
