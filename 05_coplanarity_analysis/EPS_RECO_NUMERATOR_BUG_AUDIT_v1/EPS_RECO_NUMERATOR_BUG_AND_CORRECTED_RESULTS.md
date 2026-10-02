# ε_reco Numerator Bug — Found by Re-Deriving Directly from the Raw 2000-Event Files

**Read-only investigation**, triggered by "see the 2000 events files and find
out the consistency in results and uncertainty." No existing file in
`quirk_2000_event_fresh_regeneration_v1/` was modified. No new simulation
was run. This document reports a genuine computational bug found in the
*previously reported* ε_reco numbers for both samples, and gives the
corrected values.

## Summary

Independently recomputing every efficiency directly from
`reconstruction/*/per_event_results.csv` (not trusting the cached
summary JSON/CSV files) surfaced a real bug in how `N_plane` (the
numerator of ε_reco) was computed by `run_fresh_regeneration.py`. Once
corrected, **2 of the 4 previously-reported "inconsistent with paper"
results become consistent** — this is a genuine correction found by
scrutinizing the data, not a search for agreement; it happened to move
the picture toward better paper agreement, but the analysis was run the
same way regardless of which direction it would point.

## 1. The bug, precisely

`run_fresh_regeneration.py` line 375:
```python
n_plane = int(recon_df["sec3c_plane_found"].sum())
```
This sums `sec3c_plane_found` over **all** processed events in
`recon_df` — but `recon_df` contains every trigger-passing event that
was propagated downstream, not just the fiducial-passing ones. The
plane-finding algorithm (`seeding_and_iterative_fit`) is run
**unconditionally** on every event's hits (confirmed by reading
`analyze_event()`, lines 266–299 of the same file) — it has no awareness
of the truth-level fiducial flag, and can find a spurious coplanar
"plane" using the (typically sparser) hit pattern of a non-fiducial
event too.

The paper's own definition (Sec. IV, Eq. 12 context, p.7, direct quote):
> "The reconstruction efficiency is defined as the efficiency of our
> algorithm in finding quirks **which satisfy both the trigger and
> fiducial requirements**."

This is a conditional efficiency: P(plane found | trigger AND fiducial).
For that, the numerator must be a **subset** of the fiducial-passing
population — i.e. `N_plane` must count only fiducial events for which a
plane was also found, not the raw total of "any event, fiducial or not,
with a plane found." The code computed the latter.

**Verified directly**, from the raw per-event CSV (not assumed):

| Sample | "plane found" (unconditioned, buggy) | "plane found AND fiducial" (correct) | Difference |
|---|---|---|---|
| Colored | 20 | 12 | 8 spurious planes came from non-fiducial events |
| EW | 84 | 75 | 9 spurious planes came from non-fiducial events |

This is not a rare edge case — it affects 8/20 (40%) of the colored
sample's "planes found" and 9/84 (11%) of the EW sample's.

## 2. Why this happened (root cause, not just the symptom)

The plane-finding algorithm operates purely on reconstructed hit
geometry; it has no way to know a given event failed the truth-level
"both quirks hit all 8 layers within 25 ns" requirement. A non-fiducial
event can still have enough hits, arranged coplanarly by chance or by
partial trajectory overlap, to pass the Sec. III C seeding/growth
algorithm. The original code's `n_plane` line summed this raw success
count across the whole propagated sample instead of restricting to the
fiducial subset before dividing by `n_fid` — a numerator/denominator
population mismatch. The same unconditioned-sum pattern was used for
`n_mult` and `n_final` too (lines 376–377), so those were checked as well
(§3): their impact turned out to be smaller because the stricter
downstream cuts (hit multiplicity; Δs<0.01cm, Δw<1cm) happen to reject
nearly all of the spurious non-fiducial "planes" on their own.

**This same bug was present in every earlier pass of this project's own
audits** — the `statistics/efficiency_denominator_audit.csv` file from
the earlier "forensic audit before commit" task shows the identical
buggy numbers (20/25 and 84/94), meaning that audit also failed to catch
this despite explicitly aiming to recompute everything from raw
per-event data. It re-derived N_fid, N_mult, N_final consistency checks
correctly, but did not re-derive N_plane with the fiducial condition
applied — an oversight in that audit's own scope, not a new error
introduced now.

## 3. Corrected numbers, full cascade, both samples

Recomputed directly from `reconstruction/*/per_event_results.csv`,
requiring `truth_fiducial` (and, at each subsequent stage, all prior
stages) to hold before counting a "success":

### Colored (1800 GeV, Λ=2 keV)
| Transition | Numerator/Denominator | Value | Wilson 95% CI |
|---|---|---|---|
| trigger → fiducial | 25/68 | 0.3676 | [0.263, 0.486] |
| fiducial → plane (ε_reco) | **12/25** (was 20/25) | **0.4800** (was 0.8000) | [0.300, 0.665] |
| plane → multiplicity | 7/12 (was 9/25 mixed) | 0.5833 | [0.320, 0.807] |
| fiducial → final (Sec IV) | 3/25 (was 4/25) | 0.1200 | [0.042, 0.300] |

### EW (800 GeV, Λ=4 keV)
| Transition | Numerator/Denominator | Value | Wilson 95% CI |
|---|---|---|---|
| trigger → fiducial | 94/186 | 0.5054 | [0.434, 0.576] |
| fiducial → plane (ε_reco) | **75/94** (was 84/94) | **0.7979** (was 0.8936) | [0.706, 0.867] |
| plane → multiplicity | 48/75 (was 48/94 mixed) | 0.6400 | [0.527, 0.739] |
| fiducial → final (Sec IV) | 21/94 (unchanged) | 0.2234 | [0.151, 0.318] |

## 4. Corrected paper-comparison table with statistical uncertainty

| Sample | Quantity | Corrected value (k/n) | Paper | Wilson 95% CI | Exact binomial p | Verdict (was) | Verdict (corrected) |
|---|---|---|---|---|---|---|---|
| Colored | ε_trig | 207/873 = 0.2371 | 0.24 | [0.210, 0.266] | 0.874 | Consistent | Consistent (unchanged) |
| Colored | ε_fid | 25/68 = 0.3676 | 0.28 | [0.263, 0.486] | 0.136 | Consistent | Consistent (unchanged) |
| Colored | **ε_reco** | **12/25 = 0.4800** | 0.35 | [0.300, 0.665] | **0.208** | ~~Inconsistent~~ | **Consistent** |
| EW | ε_trig | 186/1045 = 0.1780 | 0.10 | [0.156, 0.202] | <0.0001 | Inconsistent | Inconsistent (unchanged) |
| EW | ε_fid | 94/186 = 0.5054 | 0.28 | [0.434, 0.576] | <0.0001 | Inconsistent | Inconsistent (unchanged) |
| EW | **ε_reco** | **75/94 = 0.7979** | 0.72 | [0.706, 0.867] | **0.107** | ~~Inconsistent~~ | **Consistent** |

**Net effect of the correction: previously 4 of 6 quantities were
reported inconsistent with the paper; after fixing this bug, only 2 of 6
remain inconsistent (both EW ε_trig and ε_fid — unrelated to this bug,
unaffected by it).**

## 5. What this does and does not mean

- **Does not affect** ε_trig or ε_fid for either sample — those were
  always computed correctly (their numerators were never mixed with the
  wrong population).
- **Does not affect** the cross-section audit or the converted-photon
  background work — fully separate pipeline (see
  `05_coplanarity_analysis/EFFICIENCY_DEFINITIONS_EXPLAINED_v1/`).
- **Does change the headline claim** "the colored and EW reconstruction
  efficiencies are both statistically inconsistent with the paper" —
  that claim was based on the buggy numerator. With the corrected
  numerator, **both ε_reco values are now statistically consistent with
  the paper's Table I.**
- The two still-inconsistent quantities (EW ε_trig, EW ε_fid) are
  unrelated to this bug and remain open questions, previously flagged
  and not addressed by this correction.

## 6. Not yet done (explicitly disclosed)

- This document does not modify `run_fresh_regeneration.py`,
  `statistics/efficiency_denominator_audit.csv`,
  `statistics/paper_comparison_table.csv`, or any other file in
  `quirk_2000_event_fresh_regeneration_v1/` — per the standing
  instruction that directory must not be touched. If you want the
  authoritative files corrected in place, that is a separate,
  explicitly-authorized next step, not done here.
- The `plane→mult` and other intermediate transitions were recomputed
  correctly conditioned but were not independently re-verified via a
  full event-by-event replay (that would require rerunning simulation
  code, out of scope for a read-only audit).
