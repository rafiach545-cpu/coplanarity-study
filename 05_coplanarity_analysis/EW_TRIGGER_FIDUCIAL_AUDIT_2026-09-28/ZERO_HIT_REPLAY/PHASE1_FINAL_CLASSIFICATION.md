# Phase 1 — Final Classification of All 31 Zero-Hit Target Events

**150s bounded run** (original): 17/31 succeeded, 14 timed out.
**600s extended follow-up** (this session, retried ONLY the 14 timeouts,
results kept in separate files
`instrumented_replay_summary_EXTENDED_600s.csv` /
`layer_crossing_detail_EXTENDED_600s.csv`, never overwriting the
original 150s files): 13/14 succeeded, 1 (event 165) still timed out.

**Combined final tally, all 31 targets:**

| Classification | Count |
|---|---|
| Eta-drift barrel loss (physical, verified: all 16 crossings geometrically found, all 16 rejected solely by the \|η\|<1.8 cut, zero root-finding/numerical failures, replay reproduces stored zero-hit decision exactly) | **30** |
| Timing failure | 0 |
| Numerical failure | 0 |
| Other physical loss | 0 |
| Timeout / non-reproducible | 0 |
| Unresolved (timed out at both 150s and 600s) | **1** (event_idx 165) |

Full per-event table: `tables/FINAL_31_EVENT_CLASSIFICATION.csv`, with a
`budget_used` column distinguishing which of the two runs resolved each
event (150s vs 600s-after-150s-timeout vs still-unresolved), per
instruction to keep the two budgets separately traceable.

Event 165's mechanism is **not** inferred from the other 30 — it remains
genuinely unresolved, listed honestly. No further budget increase was
attempted this round.

**Verification against stored data**: `reproduced_zero_hit=True` for all
30 successfully classified events (checked in both the 150s and 600s
result sets) — the replay reproduces the originally stored zero-hit
decision in every completed case, satisfying the "verify before
interpreting" requirement for all 30.
