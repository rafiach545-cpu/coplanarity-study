# Phase 1 — Cleanup summary

Inventory of all Figure-6-related files found across the repo (7 files):
`PRE_CLEANUP_FILE_INVENTORY.csv`.

**Result: no SUPERSEDED, FAILED_PARTIAL, ZERO_BYTE_TEMPORARY, DUPLICATE, or
UNKNOWN Figure 6 artifacts were found.** All 7 existing Figure-6-related
files are either:
- **REQUIRED INPUT** (the prior grid proposal, requirement matrix, and
  runtime-estimate JSONs — used as inputs to this task's Phase 0/2/3, kept
  read-only),
- **AUTHORITATIVE** (the frozen consolidated-report figure, untouched), or
- **COMPLETED PILOT** (the committed three-point pilot report).

Consequently:
- `ARCHIVE_OBSOLETE/ARCHIVE_REASONS.csv` is empty (header only) — nothing
  needed archiving.
- `PERMANENT_DELETE_MANIFEST.csv` is empty (header only) — nothing met the
  permanent-deletion criteria (uncommitted + zero-byte/truncated +
  unreferenced + reproducible + confirmed unrelated to authoritative
  results).
- `POST_CLEANUP_FILE_INVENTORY.csv` is identical to the pre-cleanup
  inventory (no files moved or deleted).

Note: the repo's working tree also contains several pre-existing
`*.csv.checkpoint` files under `02_backgrounds/photon_conversion/` and
`05_coplanarity_analysis/sweep_mu_2026-09-16/`. These predate this task,
belong to the already-frozen pile-up/converted-photon background studies
(Figures 1-5 scope), and are explicitly out of scope for this Figure-6-only
cleanup — left untouched, not classified, not archived.

**One correction identified during Phase 0 (paper reread), carried into
Phase 2/3:** the existing grid proposal's EW mass list includes 1200 GeV,
outside the paper's own Fig. 6 EW-panel axis range (0-1000 GeV). This is a
grid-definition fix, not a cleanup action, and is applied in Phase 2/3
rather than here.
