# Actual vs. intended Phase 5 execution order

**Intended order** (as stated at launch): colored mass points (600-2400 GeV)
first, then EW mass points (100-1000 GeV), per the informal description
given alongside the launch report.

**Actual order observed** (from `ACTUAL_PHASE5_EXECUTION_ORDER.csv`, built
from real log/checkpoint timestamps, not the intended list): EW points ran
first (100, 200, 400 GeV... continuing through all 6 EW points), then
colored.

## Root cause

`mass_points_from_grid()` in `run_phase5_production.py` builds the ordered
point list via:
```python
mp_df = df.drop_duplicates(subset=["channel","mass_gev"])[...].sort_values(["channel","mass_gev"])
```
`sort_values(["channel", ...])` sorts alphabetically by the `channel`
string. `"EW"` (uppercase E, ASCII 69) sorts before `"colored"` (lowercase
c, ASCII 99) in a plain string sort — so EW points were scheduled first,
opposite to the informally-stated intent, which was never actually encoded
in the sort key.

## Why this does not affect correctness

- **Seeds:** each point's `generation_seed` and `downstream_seed_base` come
  from the pre-built, already-committed `tables/figure6_grid91_full.csv` /
  `metadata/SEED_REGISTRY.csv`, keyed by (channel, mass, Λ) — independent of
  execution order.
- **Point identity:** each mass point's run directory, param_card mass
  value, and run_card seed are set from that same per-point data, not from
  position in a loop.
- **Outputs:** every point's generation output is validated independently
  (matched count, exit code, DONE marker) before being marked complete;
  nothing about a point's own generation depends on which point ran before
  it.

Confirmed via `ACTUAL_PHASE5_EXECUTION_ORDER.csv`: real seeds, masses, and
output paths for the first 3 completed points match the seed registry
exactly (EW 100→seed 9500, EW 200→seed 9501, as tabulated in
`SEED_REGISTRY.csv`).

**No code change was made to the ordering while the run is active** —
changing sort behavior would require touching the running driver process,
which is explicitly protected while healthy. This is documented as a
disclosed, harmless deviation from the informally-stated intent, not a
physics or provenance defect.
