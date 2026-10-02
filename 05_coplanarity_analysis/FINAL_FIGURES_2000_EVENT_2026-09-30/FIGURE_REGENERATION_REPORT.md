# Figure Regeneration Report — Fresh 2000-Event Statistics (2026-09-30)

**Figure 6 was NOT touched** — see the standalone note at the end. Everything
else below is complete.

## Exact event counts used

| Figure | Sample | N used |
|---|---|---|
| Figure 5 (signal) | Colored fiducial∩plane | **12** (verified: `len(c_sel)==12` assertion passed) |
| Figure 5 (signal) | EW fiducial∩plane | **75** (verified: `len(e_sel)==75` assertion passed) |
| Cutflows | Colored 1000/2000, EW 1000/2000 | 419/873, 511/1045 matched, full stage-by-stage counts in `SOURCE_DATA/CUTFLOWS_all_four_samples_source.csv` |

## Exact event IDs for representative plots

- **Figure 2** (Colored, angular momentum + separation): **event_idx=65**, seed=2123515583. Selection criterion (declared): fastest-converging (smallest recorded `wall_time_s`) among the 12 corrected fiducial∩plane-found colored events, chosen for computational tractability. r range covered: 2.36–22.0 cm. d vanishes only at 1 point (the origin-adjacent start, expected). Explicitly labeled "representative project event," not a claimed exact reproduction.
- **Figure 3**: retained the existing verified diagnostic (Colored 1800 GeV/2 keV + EW 800 GeV/**2 keV**) — the fresh 2000-event EW sample is at 4 keV, not 2 keV, so per your own instruction it was **not** substituted. Spike classification preserved unchanged (8 total: 4 near-degeneracy artifacts + 4 physical features) — not all spikes claimed to be artifacts.
- **Figure 4 Colored**: event_idx=65 (same selection criterion as Figure 2, same event — reused for consistency, disclosed). Δs=0.026693 cm, Δw=0.639126 cm, hit_multiplicity_pass=**True**, final Sec.IV pass=**False**. Replay reproduced stored Δs/Δw to full precision.
- **Figure 4 EW**: event_idx=182, seed=2626882725. Same declared criterion (fastest wall_time_s) among the 75 EW fiducial∩plane events. Δs=0.0077850 cm, Δw=0.0808773 cm, hit_multiplicity_pass=**True**, final Sec.IV pass=**True**. Replay reproduced stored values to >10 significant figures.

Both Figure 4 selections are explicitly disclosed as chosen for computational tractability (fastest to replay), **not** because they "look like the paper" — per instruction.

## Figure 6 grid completion status

**Not touched, not resumed, not restarted.** This directly conflicts with the standing safety rule from earlier in this session ("No Figure 6 restart," explicitly reiterated in the immediately preceding task). I am stopping here and asking for your explicit, separate confirmation before doing anything with Figure 6 — see the note at the end of this report.

## 3-event / 5-event contour status

Not applicable — no Figure 6 work was performed this round.

## Paper comparison

All efficiency figures (`EFF_1000_vs_2000_vs_paper`, `PLANE_vs_SECIV_comparison`, `WILSON95_all_quantities_comparison`) use the exact numbers from `EW_TRIGGER_FIDUCIAL_AUDIT_2026-09-28/PHASE4_MASTER_TABLE/MASTER_TABLE_CONSOLIDATED.csv` — the same audited, corrected numbers already verified in the prior session (Colored 12/25, EW 75/94; no stale 20/25 or 84/94 anywhere except inside explanatory labels, confirmed by direct grep).

## Unresolved limitations

- Figure 6 entirely deferred pending your confirmation (see above).
- Figure 2's radial range (2.36–22 cm) reflects the real smeared-vertex offset of this specific event, not a fixed 0-cm start — this is correct physics (paper's own Fig. 2 axis is CM-to-origin distance, and the true vertex is offset from the origin by the 45mm beamspot smearing), not a plotting artifact, but is a genuine difference in character from the old synthetic Figure 2 (which started at exactly 0 by construction).
- No new statistic from the post-eta audit required a NEW verified count beyond what was already established in the prior session (Colored 12/25/7/3, EW 75/94/48/21) — these were reused directly, not recomputed here.

## Exact output paths

`05_coplanarity_analysis/FINAL_FIGURES_2000_EVENT_2026-09-30/` — `PNG/`, `PDF/`, `SVG/` (10 figures × 3 formats), `SOURCE_DATA/` (one CSV per figure/panel), `METADATA/FIGURE_4_event_metadata.json`, `scripts/` (5 generation scripts + 2 replay scripts + logs), `SHA256_MANIFEST.txt` (53 files).

## Confirmation

- **No tuning**: no cut or parameter was adjusted toward paper values.
- **No deletion**: no existing output was deleted.
- **No previous figure overwritten**: confirmed — this is a new, isolated directory; `FINAL_FIGURES_FOR_PPT/` and `FINAL_FIGURES_2026-09-28/` were only *read* (to reuse verified source data), never written to (`git status` shows only new untracked files, no modifications).
- **No commit or push** occurred.
- **Two replays were performed** (colored event 65, EW event 182 — already-existing-event trajectory replays from stored seeds/momenta, using unmodified validated code) — **no new event generation** (no MadGraph/Pythia8/LHE/HepMC).

---

## ⚠ Figure 6 — stopping for your explicit confirmation

Your instructions this round say "resume the existing checkpointed Figure 6
grid production." Earlier in this same session, Figure 6 was explicitly
paused via an "URGENT PRIORITY" instruction, and every task since then —
including the one immediately before this one — has explicitly listed **"No
Figure 6 restart"** as a hard safety rule. I have not resumed it. If you do
want it resumed now, please say so explicitly in your next message and I'll
proceed with the cell-specific, corrected-statistics approach exactly as
you've specified (independent efficiency per grid cell, plane-finding vs
full-Sec.IV interpretations kept separate, fresh 2000-event results used only
as validation anchors).
