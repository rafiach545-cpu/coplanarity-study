# Fresh Independent 2000+2000 Event Quirk Regeneration — Final Report

Strictly independent of all prior project numerical results (see
`PAPER_REQUIREMENTS.md` Independence Log for the two disclosed, permitted
exceptions: frozen process-card templates and validated physics code reuse).

## Configuration [DIRECTLY STORED]

| | Colored | EW |
|---|---|---|
| mQ | 1800 GeV | 800 GeV |
| Λ | 2 keV | 4 keV |
| Production | QCD-only | Drell-Yan |
| N_requested | 2000 | 2000 |
| Generation seed | 8001 | 8002 |
| Downstream seed base | 60001 | 60002 |

Full config: `CONFIGURATION_FROZEN.json`. Seeds confirmed fresh (never used
by any prior sample or Figure 6 production): `SEED_REGISTRY.csv`.

## Generation [DIRECTLY STORED]

| | Colored | EW |
|---|---|---|
| N_matched | 873 (43.65%) | 1045 (52.25%) |
| Matched xsec | see `generation/*/generation_stats.json` | same |
| Wall time | 463.4s | 1035.7s |
| Exit code | 0 | 0 |

## Charge/trigger accounting (colored kept strictly separate per instruction)
[DIRECTLY STORED + INDEPENDENTLY RECOMPUTED]

```
N_matched=873, N_both_neutral=178, N_one_charged=421, N_both_charged=274
N_trigger_of_full_matched=207 (eps=0.2371)
N_trigger_AND_charge_filtered=68
N_trigger_of_charge_filtered=68/274 (eps=0.2482)
joint_trigger_and_charge_survival_prob=68/873=0.0779
```

The joint probability (0.078) is explicitly NOT labeled "trigger
efficiency" anywhere in this task's output — it is a separate, correctly
named quantity, per instruction.

EW: N_matched=1045, N_trigger_of_full_matched=186 (eps=0.1780). No charge
filter applies to EW (fixed unit charge).

## Reconstruction quantities, kept separate [DIRECTLY STORED]

| | Colored (N_fid=25) | EW (N_fid=94) |
|---|---|---|
| N_plane (Sec IIIC) | 20 | 84 |
| N_hit_multiplicity | 9 | 48 |
| N_final (Sec IV) | 4 | 21 |
| **ε_reco = N_plane/N_fid** | **20/25 = 0.800** | **84/94 = 0.894** |
| Sec IV final-pass rate = N_final/N_fid | 4/25 = 0.160 | 21/94 = 0.223 |

Both quantities reported without conflation, per instruction.

## Paper Table I comparison — full statistical tests
[INDEPENDENTLY RECOMPUTED + PAPER COMPARISON]

Full table: `statistics/paper_comparison_table.csv`. Wilson 95%,
Clopper-Pearson 95%, and exact two-sided binomial p-values computed for
every quantity, not just point estimates.

| Sample | Quantity | Project | Paper | Wilson 95% | p-value | Verdict |
|---|---|---|---|---|---|---|
| colored | ε_trig (full-matched) | 0.2371 | 0.24 | [0.210,0.266] | 0.874 | CONSISTENT |
| colored | ε_trig (charge-conditional) | 0.2482 | 0.24 | [0.201,0.303] | 0.777 | CONSISTENT |
| colored | ε_fid | 0.3676 | 0.28 | [0.263,0.486] | 0.136 | CONSISTENT |
| colored | ε_reco (paper-defined) | 0.8000 | 0.35 | [0.609,0.911] | **<0.0001** | **INCONSISTENT** |
| EW | ε_trig (full-matched) | 0.1780 | 0.10 | [0.156,0.202] | **<0.0001** | **INCONSISTENT** |
| EW | ε_fid | 0.5054 | 0.28 | [0.434,0.576] | **<0.0001** | **INCONSISTENT** |
| EW | ε_reco (paper-defined) | 0.8936 | 0.72 | [0.815,0.941] | **0.0001** | **INCONSISTENT** |

**This differs from earlier, much-smaller-N project measurements**, which
reported the colored ε_reco gap as "statistically inconclusive" (N_fid=7)
and the EW quantities as consistent or "tension" without a firm verdict
(N_fid=40). At this task's larger, independent statistics (N_fid=25 and 94
respectively), the same directional gaps are now **statistically
significant** — larger samples resolved prior ambiguity, and not
uniformly in the paper's favor. This is reported factually; no cut,
definition, or methodology was altered after seeing these results (verified
by construction — all cuts were fixed in `PAPER_REQUIREMENTS.md` before
generation began).

## Data quality [DIRECTLY STORED]

- NaN: 0 (both samples). Inf: 0 (both samples). Duplicate events: 0 (both).
- Technical exceptions (caught, non-fatal, logged): 2/25 colored, 2/94 EW —
  same physics-driven step-count edge case documented during Figure 6
  production, not a new bug.
- Full per-event data (raw+merged hit counts, per-layer counts, seed/
  candidate counts, Δs/Δw, every Sec IIIC/IV flag, first-failure reason,
  wall time, status): `reconstruction/*/per_event_results.csv`.

## Runtime

Colored downstream: 2843s total (25 events → 68 propagated, wall ≈13min
driver time incl. generation). EW downstream: 31067s total (186 events),
driver total elapsed ≈4h. Both sequential, one fully complete before the
next began, no memory/resource pressure observed.

## Failure-reason breakdown [DIRECTLY STORED]

Colored (of 68 propagated): fiducial=41, no_plane=13, mult=5,
signal_region=4, final_pass=3, technical=2 (sums to 68 ✓).
EW (of 186 propagated): fiducial=90, mult=27, signal_region=27,
final_pass=21, no_plane=19, technical=2 (sums to 186 ✓).

## What can and cannot be claimed

**Can claim:** with real, larger-than-before independent statistics, the
colored channel's trigger and fiducial efficiencies are now confirmed
consistent with the paper; its reconstruction efficiency is now confirmed
**statistically inconsistent** (not merely "small-N noise"). The EW
channel's trigger, fiducial, AND reconstruction efficiencies are all now
confirmed statistically inconsistent with the paper at this sample size.

**Cannot claim:** a specific root cause for the EW/colored ε_reco and
EW ε_trig/ε_fid gaps — this task deliberately did not investigate
modeling differences (out of scope; see the earlier, separate colored-only
audit for that kind of analysis, not consulted or reused here per the
independence requirement). This is a fresh numerical measurement only.

## Files

See `SHA256_MANIFEST.txt` for every output file's hash.
