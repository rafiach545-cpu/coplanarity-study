# Colored-quirk statistics feasibility (v1) — 2026-09-21

## Question
The colored ε_reco is based on only 7 fiducial events (5 reconstructed
planes, 1 final pass) — is this fixable without a new large production?

## Verified facts (from stored data, no rerun)

- **Raw matched sample**: `01_signal_generation/quirk_pair_momenta_1800gev_2kev.csv`
  — 419 rows (420 lines incl. header). This is confirmed to be the
  **complete** MLM-matched output; no larger or partially-unused raw
  sample exists anywhere in the repository (checked via `find`).
- **Charge-filtered subsample**: `..._v2_CHARGED.csv` — 125 rows.
  125/419 = 29.83%, consistent with the paper's own stated estimate
  (page 2: "the probability for those final states to have ±1 charges is
  roughly 30% as estimated using Pythia8").
- **Trigger-passing**: 27/125 (already the full charge-filtered sample —
  every one of the 125 charge-filtered events has already been evaluated
  against the trigger cut, since that cut only needs the stored momenta,
  no simulation).
- **Runtime per event**: from `docs/colored_quirk_v3_run.log`, the full
  27-trigger-passing-event run (trajectory integration + detector
  response + reconstruction) took 818s total ≈ **30.3s/trigger-passing
  event**. Only trigger-passing events are ever simulated (Stage 3's cut
  is applied before Stage 1/2, per `CUTS_AND_PIPELINE.md`), so this
  per-event cost scales with N_trigger, not N_matched.

## Conclusion: no unused sample exists

**There is no reservoir of unprocessed colored-quirk events to draw on.**
All 419 matched events, all 125 charge-filtered events, and all 27
trigger-passing events have already been fully processed through the
pipeline. Increasing the fiducial-event count requires generating
**brand-new MadGraph5_aMC@NLO + Pythia8 matched events** — a new
production run, not a reuse of existing stored data.

Per this task's explicit instruction ("If an existing unused sample
permits a safe run below six hours, run it... Otherwise provide the exact
future command and projected runtime"), and since no such unused sample
exists, **no run is launched in this task.**

## Projected requirement for a useful statistics upgrade (not executed)

To move from N_fiducial=7 to, e.g., N_fiducial≈50 (roughly the scale
needed for a Wilson 95% CI width comparable to the EW benchmark's
current N=40 fiducial sample):

1. Required trigger-passing events: 50 × (27/7) ≈ 193
2. Required charge-filtered matched events (at ε_trig=0.216): 193/0.216 ≈ 894
3. Required raw matched events (at 29.8% charge fraction): 894/0.298 ≈ 3000
   — roughly **7.2× the current matched sample size** (419 → ~3000)

## Runtime and resource estimate

- **Physics pipeline (trajectory+detector+reconstruction) only**, for the
  ~193 new trigger-passing events: 193 × 30.3s ≈ 5850s ≈ **1.6 hours**
  (within a 6-hour budget on its own).
- **MadGraph5_aMC@NLO + Pythia8 generation** of ~3000 matched events: **no
  historical timing exists in this repository** for the original
  generation step (only its OUTPUT momenta CSV was preserved, not a
  run_card, banner, or generation-time log) — this cost is genuinely
  unknown and cannot be safely estimated from stored data. LHC signal
  generation at this scale (custom UFO model, MLM matching with +1 jet)
  is typically the dominant cost of such a pipeline, often exceeding the
  downstream physics-pipeline time by a large factor, so treat this as
  the primary unbounded risk, not the reconstruction step.
- **Disk**: current 419-event sample is small (single CSV, tens of KB);
  a 3000-event sample would remain small in raw-momenta form (no
  full-event HepMC is retained in this project's pipeline), so disk is
  not expected to be a constraint.

## Verdict

**NOT SAFE TO AUTO-LAUNCH.** A colored-statistics upgrade requires new
MadGraph/Pythia8 generation whose runtime is unknown and unbounded from
this project's own stored history — this is exactly the category of
action this task explicitly withholds blanket authorization for ("Do not
automatically launch a large production"). No run was started.

## Exact future command (for explicit authorization in a future task)

```
# Stage 0: generate ~3000 new matched colored-quirk events
# (exact MadGraph5_aMC@NLO run_card/UFO model setup not preserved in this
#  repo -- would need to be reconstructed/re-verified against the existing
#  419-event sample's own generation settings before running, since no
#  run_card was archived)
<MadGraph5_aMC@NLO generation of p p > Q Qbar [+1 jet], MLM-matched,
 mQ=1800 GeV, Lambda=2 keV, ~3000 events>
  -> 01_signal_generation/quirk_pair_momenta_1800gev_2kev_v3_EXTENDED.csv (NEW FILE, does not overwrite v2)

# Stage 1: charge filter (reuse existing extract/filter logic unchanged)
python3 01_signal_generation/extract_quirk_momenta.py --input <new_raw> \
  --output quirk_pair_momenta_1800gev_2kev_v3_EXTENDED_CHARGED.csv

# Stage 2: full pipeline (reuse analyze_colored_quirk.py unchanged, but
# point it at the new CHARGED file; run with checkpointing since the
# expected trigger-passing count is ~193, projected 1.6h)
python3 05_coplanarity_analysis/analyze_colored_quirk.py \
  --input quirk_pair_momenta_1800gev_2kev_v3_EXTENDED_CHARGED.csv \
  --output colored_quirk_1800gev_2kev_cutflow_v4_EXTENDED_STATS.csv \
  --checkpoint-every 5
```

Projected total wall time: **1.6h (physics pipeline) + UNKNOWN (MadGraph
generation, likely the dominant cost)**. Recommend benchmarking the
MadGraph generation step alone, at small scale (e.g. 100 events), before
committing to the full ~3000-event run, in a dedicated future task with
explicit authorization.
