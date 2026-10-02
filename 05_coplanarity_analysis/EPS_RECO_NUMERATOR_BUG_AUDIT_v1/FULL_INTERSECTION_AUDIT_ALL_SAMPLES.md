# Full Event-ID Intersection Audit — ε_reco Numerator, All Four Samples

**Read-only.** No frozen file modified (`quirk_2000_event_fresh_regeneration_v1/`
and the original 1000-event cutflow CSVs at repo root are untouched). No
new simulation run. This supersedes nothing — it extends
`EPS_RECO_NUMERATOR_BUG_AND_CORRECTED_RESULTS.md` with explicit
event-level intersection counts for all 7 requested quantities, for both
the 2000-event fresh regeneration and the original 1000-event samples,
and keeps `eps_plane_conditional` and `eps_secIV_conditional` as two
separate, explicitly-labeled quantities per instruction.

## Data sources (exact files read)

| Sample | File | Rows (excl. header) |
|---|---|---|
| Colored, 2000-event fresh regen | `quirk_2000_event_fresh_regeneration_v1/reconstruction/colored_1800GeV_L2keV/per_event_results.csv` | 68 |
| EW, 2000-event fresh regen | `quirk_2000_event_fresh_regeneration_v1/reconstruction/EW_800GeV_L4keV/per_event_results.csv` | 186 |
| Colored, original 1000-event | `05_coplanarity_analysis/colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv` | 27 |
| EW, original 1000-event | `05_coplanarity_analysis/ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv` | 89 |

The original-sample row counts (27, 89) match the trigger-passing counts
already on record in `final_freeze_v1/master_cutflow_table.csv`
(`N_trigger=27` colored, `N_trigger=89` EW) — confirms these are the
correct, complete trigger-passing subsets, not a truncated file.

Column mapping between the two code generations (different column
names, same physical meaning):

| Quantity | 2000-event column | 1000-event column |
|---|---|---|
| Fiducial flag | `truth_fiducial` | `truth_fiducial` |
| Plane found (Sec III C) | `sec3c_plane_found` | `seed_found` |
| Hit-multiplicity pass | `hit_multiplicity_pass` | `best_candidate_passes_hit_multiplicity` |
| Sec IV final pass | `final_sec_iv_pass` | `passes_signal_region` |

## The 7 requested counts, all four samples

### Colored, 2000-event fresh regeneration
1. N_fiducial = **25**
2. N_plane_total (unconditioned) = **20**
3. N(fiducial AND plane) = **12**
4. N_hit_multiplicity_total (unconditioned) = **9**
5. N(fiducial AND plane AND hit_multiplicity) = **7**
6. N_final_total (unconditioned) = **4**
7. N(fiducial AND final SecIV) = **3**

### EW, 2000-event fresh regeneration
1. N_fiducial = **94**
2. N_plane_total (unconditioned) = **84**
3. N(fiducial AND plane) = **75**
4. N_hit_multiplicity_total (unconditioned) = **48**
5. N(fiducial AND plane AND hit_multiplicity) = **48**
6. N_final_total (unconditioned) = **21**
7. N(fiducial AND final SecIV) = **21**

### Colored, original 1000-event sample
1. N_fiducial = **7**
2. N_plane_total (unconditioned) = **5**
3. N(fiducial AND plane) = **5**
4. N_hit_multiplicity_total (unconditioned) = **3**
5. N(fiducial AND plane AND hit_multiplicity) = **3**
6. N_final_total (unconditioned) = **1**
7. N(fiducial AND final SecIV) = **1**

### EW, original 1000-event sample
1. N_fiducial = **40**
2. N_plane_total (unconditioned) = **32**
3. N(fiducial AND plane) = **32**
4. N_hit_multiplicity_total (unconditioned) = **16**
5. N(fiducial AND plane AND hit_multiplicity) = **16**
6. N_final_total (unconditioned) = **6**
7. N(fiducial AND final SecIV) = **6**

**Observation: for both 1000-event samples, item 2 equals item 3 exactly
(and item 4 equals item 5, item 6 equals item 7) — the unconditioned and
fiducial-conditioned counts are identical.** For both 2000-event samples,
item 2 exceeds item 3 (20 vs 12 colored; 84 vs 75 EW) — the bug is
present only in the newer regeneration.

## Why the original 1000-event samples do NOT have this bug (structural, not coincidental)

Traced directly in `analyze_colored_quirk.py` (the script that produced
the original 1000-event cutflow CSVs): line 86, `if not truth_fiducial:`
is followed by an early return that sets `seed_found = False` **without
ever calling** the seeding/plane-finding algorithm. Non-fiducial events
in the original pipeline never had the algorithm run on them at all —
so `seed_found` (and everything downstream of it) is structurally
guaranteed to be `False` for every non-fiducial event, making the
unconditioned sum and the fiducial-conditioned sum identical by
construction. This is confirmed directly by the exact match in every
one of the three unconditioned-vs-conditioned pairs above (5=5, 3=3,
1=1 for colored; 32=32, 16=16, 6=6 for EW) — not asserted, verified.

By contrast, `run_fresh_regeneration.py`'s `analyze_event()` calls
`seeding_and_iterative_fit()` **unconditionally on every event**
(confirmed by direct code read, lines 266–299), regardless of
`truth_fiducial` — allowing spurious "planes" to be found in
non-fiducial events, which the original code's design prevented outright.

**Conclusion: the original 1000+1000 samples are NOT affected by this
bug.** Their previously-reported ε_reco-type numbers (5/7=0.714 colored,
32/40=0.800 EW, as recorded in `final_freeze_v1/master_cutflow_table.csv`)
are correct as computed — no correction needed for those files.

## Two separately-named conditional efficiencies, all four samples, vs Table I

Per instruction, these are kept as two distinct quantities — see
"Definition ambiguity" below before treating either as *the* paper
ε_reco.

| Sample | eps_plane_conditional = N(fid∩plane)/N_fid | Wilson 95% CI | vs paper | p-value | eps_secIV_conditional = N(fid∩final)/N_fid | Wilson 95% CI | vs paper | p-value |
|---|---|---|---|---|---|---|---|---|
| Colored 2000 | 12/25 = 0.4800 | [0.300, 0.665] | 0.35 | 0.208 | 3/25 = 0.1200 | [0.042, 0.300] | 0.35 | 0.019 |
| EW 2000 | 75/94 = 0.7979 | [0.706, 0.867] | 0.72 | 0.107 | 21/94 = 0.2234 | [0.151, 0.318] | 0.72 | 2.4e-23 |
| Colored 1000 | 5/7 = 0.7143 | [0.359, 0.918] | 0.35 | 0.056 | 1/7 = 0.1429 | [0.026, 0.513] | 0.35 | 0.434 |
| EW 1000 | 32/40 = 0.8000 | [0.652, 0.895] | 0.72 | 0.295 | 6/40 = 0.1500 | [0.071, 0.291] | 0.72 | 9.1e-14 |

## Definition ambiguity — explicitly disclosed, not resolved here

The paper (Sec. IV, p.7) defines: "The reconstruction efficiency is
defined as the efficiency of our algorithm **in finding quirks** which
satisfy both the trigger and fiducial requirements." This phrase is
compatible with two different readings, and the paper does not
disambiguate further:

- **Reading A → `eps_plane_conditional`**: "finding quirks" = the
  Sec. III C seeding/iterative-fit algorithm successfully identifies
  *a* coplanar hit-plane candidate at all. This is the most literal
  reading of "finding" as a geometric/algorithmic act, and is what this
  project's `PAPER_REQUIREMENTS.md` (row 19) previously adopted as "the
  paper-defined ε_reco."
- **Reading B → `eps_secIV_conditional`**: "finding quirks" = the full
  event is ultimately accepted into the Sec. IV signal region (plane
  found AND hit-multiplicity pass AND the tight Δs<0.01cm/Δw<1cm cuts) —
  i.e., the algorithm's end-to-end success at fully reconstructing and
  selecting the quirk, not merely proposing a candidate plane.

**Both readings are defensible from the text alone.** Under Reading A,
all four samples' ε_reco-type numbers are now statistically consistent
with Table I (all p>0.05: colored-2000 p=0.208, EW-2000 p=0.107,
colored-1000 p=0.056, EW-1000 p=0.295). Under Reading B, all four are
strongly inconsistent (colored-2000 p=0.019, EW-2000 and EW-1000 both
p≪0.0001, colored-1000 the only borderline case at p=0.434 — but note
its N_fid=7 is very small, so this one non-rejection carries little
statistical weight). **This audit does not declare which reading the
paper intended** — that determination would require either explicit
paper text this project does not have, or contacting the paper's
authors; it is reported here as an open, disclosed ambiguity per
instruction, not resolved by assumption.

## What remains unresolved / not done

- Frozen files are NOT corrected in place, per instruction. If/when
  authorized, the fix is a one-line change in
  `run_fresh_regeneration.py`'s `build_statistics()`: replace
  `n_plane = int(recon_df["sec3c_plane_found"].sum())` with
  `n_plane = int((recon_df["truth_fiducial"] & recon_df["sec3c_plane_found"]).sum())`
  (and equivalently condition `n_mult`/`n_final` on the full AND-chain,
  though as shown above their impact is smaller).
- Which of `eps_plane_conditional` / `eps_secIV_conditional` is the
  "correct" comparison to Table I remains an open, disclosed question.
