# Figure 4 verification (v2) — 2026-09-21

## Numbers CONFIRMED, provenance CONFIRMED STALE

`fig4_data_v2.json` gives Δs=0.019210 cm (**0.0192cm**) and Δw=0.547927 cm
(**0.548cm**) — matches the expected project-representative values exactly.

**However**, cross-checked against both current authoritative signal
cutflow CSVs (`colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv`,
`ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv`) — **no row in either
file matches this Δs or Δw value.** Neither JSON nor its companion
`.pkl` file store an event ID or benchmark label.

**Conclusion: `fig4_data_v2.json`/`fig4_best_candidate_v2.pkl` are
CONFIRMED OBSOLETE** — both were committed in commit `b8f017f`, titled
*"Baseline snapshot before trajectory/Stage-2 corrections,"* i.e. they
predate the vertex-relative-fit correction and other pipeline fixes
applied later in this project. This is consistent with the specific
mismatch found: Δs/Δw values from a pre-fix pipeline do not reproduce
under the current, corrected reconstruction.

**No authoritative, current-pipeline Figure 4 plot exists in the
repository at this time.** No PNG for Figure 4 was found anywhere.

**Status: OBSOLETE — regeneration required.** Not regenerated in this
task (would require re-deriving a specific event's hit-level (x,y,z) per
layer from the current v3 CSVs, which only store aggregate per-layer hit
*counts*, not coordinates — recovering coordinates needs a targeted
single-event replay, analogous to the Event 2555 forensic method,
authorized under this task's "small deterministic representative-event
calculation" allowance but not completed here due to time constraints).

## Recommended next action
Pick one N_plane event from the current authoritative colored or EW
cutflow (e.g. one with 8/8 layer coverage, for a clean illustrative
display), replay it deterministically (same pattern as the Event 2555
forensic script) to recover its per-hit (x,y,z), and regenerate Figure 4
projected onto the (n3,n2) plane, matching the paper's own Fig.4 style.
