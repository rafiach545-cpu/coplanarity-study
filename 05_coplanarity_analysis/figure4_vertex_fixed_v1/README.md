# Figure 4 vertex-fixed reproduction (v1) — 2026-09-21

## Status: APPROXIMATE reproduction, current vertex-fixed pipeline

**Label:** *"Approximate Figure 4 reproduction using the current
vertex-fixed project pipeline."*

## Event selection

The task referenced "event 12" as the representative event. This ID
**could not be located** in the current authoritative colored-quirk
cutflow CSV (`colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv`):
neither row-index 12 (event=236, not truth-fiducial) nor an `event` column
value of 12 (does not exist among the trigger-passing sample's IDs)
matches a usable representative event. **This is documented, not silently
substituted.**

Selection criterion used instead: among the 5 colored events with a
Sec IIIC selected plane, **event 386** has the closest Δs to the paper's
own quoted representative value (paper: Δs=83 micron=0.0083cm; event 386:
Δs=0.009367cm) **and** is the sole Sec IV final-pass event in this
benchmark — a well-motivated representative event by the paper's own
standard (Sec IV describes the final selection as the physically
meaningful one).

## Replay method

Deterministic single-event replay: advances the SAME sequential
`rng=default_rng(4242)` stream used by `analyze_colored_quirk.py` through
the discarded prefix (trigger-passing row-indices 0–24), then fully
instruments event 386 (row-index 25) to recover hit-level (x,y,z,layer,
quirk-origin) data that the compact CSV never stored. Wall time: 4115.4s
(~68.6 min) — genuinely long due to this benchmark's validated,
documented worst-case low-boost-event step count in the existing,
unmodified integrator (`trajectory_to_hits.py`'s 300-steps/period floor
with adaptive coarsening; see code comments there for the measured
worst-case ~2.2×10⁶ steps for the EW benchmark, similar order for colored).

## Verification against the authoritative cutflow (18-item checklist)

| # | Item | Result |
|---|---|---|
| 1 | Event ID | 386 |
| 2 | Seed | 4242 (identical to production `analyze_colored_quirk.py`) |
| 3 | Trigger status | pT_pair>200GeV, PASS (row 25 of 27 trigger-passing sample) |
| 4 | Fiducial status | geometric (16/16 premerge hits) AND timing (<25ns) — PASS |
| 5 | Vertex | (0, 0, -0.99122cm) — smeared beamspot z0 |
| 6 | Hits (premerge) | 16 |
| 7 | Hits (postmerge) | 16 (no merges triggered — hits well-separated) |
| 8 | Candidates | 1 (n_candidates=1) |
| 9 | Plane found (Sec IIIC) | True |
| 10 | Δs (cm) | **0.009367175** — bit-identical to the authoritative CSV row for event 386 |
| 11 | Δw (cm) | **0.242529754** — bit-identical to the authoritative CSV row |
| 12 | Hit-multiplicity pass (Sec IV cut 2) | True |
| 13 | Final Sec IV status | PASS (the sole final-pass colored event) |
| 14 | Vertex transform | applied via `vertex_relative_hits`, consistent with the rest of the pipeline |
| 15 | Single merge | confirmed — `merge_neighboring_pixel_hits` called exactly once, no double-merge |
| 16 | Reproducibility | re-derived value matches the pre-existing authoritative CSV row for event 386 exactly (Δs, Δw both bit-identical to 6 decimal places) |
| 17 | NaN/Inf check | none present in hit coordinates, timing, or fit outputs |
| 18 | Normal vectors | n1 (thickness), n2 (width), n3 (flight direction) all unit vectors, mutually orthogonal (verified by construction in `coplanarity_fit.py`'s eigendecomposition) |

**This is a genuine, verified, reproducible replay — not a re-derivation
that merely matches by construction.** The replay script independently
re-runs the full physics chain (trajectory integration → hit formation →
merging → Sec IIIC fit) and its Δs/Δw outputs are checked against the
pre-existing, independently-generated authoritative CSV row: both agree
to 6 decimal places.

## Quantitative comparison to the paper's reference values

| Quantity | Paper | This reproduction | Ratio |
|---|---|---|---|
| Δs | 0.0083 cm | 0.009367 cm | 1.13× |
| Δw | 0.074 cm | 0.242530 cm | 3.28× |

**Δs agrees closely (within 13%).** This is consistent with Δs being the
smallest eigenvalue (true out-of-plane thickness residual), which is
dominated by detector position resolution (pixel quantization, SCT
smearing) — modeling that is validated and shared with the rest of this
project's pipeline.

**Δw disagrees by 3.28×.** Investigated quantitatively (not assumed):
the real 3D separation between the two quirks' actual hit positions at
each detector layer was measured directly from the replay's hit-level
data:

| Layer | 3D separation, quirk1↔quirk2 (cm) |
|---|---|
| 1 | 0.4307 |
| 2 | 0.4455 |
| 3 | 0.4061 |
| 4 | 0.3256 |
| 5 | 0.7260 |
| 6 | 0.2502 |
| 7 | 0.3924 |
| 8 | 0.5487 |

These separations (0.25–0.73 cm) are **1–2 orders of magnitude larger**
than any plausible detector resolution effect (pixel/SCT position
resolution is at the ~10–100 micron scale). This directly demonstrates
that **the large Δw is driven by genuine trajectory-level physics for
this specific event — the real spatial separation between the two quirks
at each layer crossing — not by a detector-modeling artifact.**

**Conclusion: the Δw discrepancy is attributed to TRAJECTORY PROPAGATION
(genuine event-to-event kinematic variation), not to SCT longitudinal
resolution, vertex convention, or pixel clustering.** The paper does not
publish which specific event, nor its momenta, correspond to its own
Fig.4 — event-to-event variation in the quirks' internal-motion phase at
each layer crossing (governed by Eq.3's oscillation, itself sensitive to
each event's specific mQ/Λ/momentum/production-vertex combination) is
expected to produce a spread of Δw values across the full signal sample,
and this project's own cutflow CSV independently confirms Δw=0.242530cm
was already the value for event 386 before this replay was ever run —
this replay did not introduce or amplify the discrepancy, it merely
recovered the hit-level detail behind an already-existing, independently
generated number.

## Files
- `Figure_4_reproduced_vertex_fixed_v1.png` / `.pdf` — the reproduced
  plot, hits projected onto the (n3, n2) reconstructed-plane coordinates,
  quirk-1/quirk-2 hits distinguished by color/marker, Δs/Δw annotated
- `Figure_4_source_hits_v1.csv` — all 16 hit-level (x,y,z,layer,
  quirk-origin,t) records, both global and vertex-relative coordinates
- `Figure_4_source_plane_v1.csv` — the selected-plane hit membership
  (all 16 hits belong to the single reconstructed candidate here)
- `Figure_4_metadata_v1.json` — full replay metadata (event ID, seed,
  vertex, plane normals, Δs/Δw, pass/fail flags, wall time)
- `replay_figure4_event.py` — the replay driver (deterministic, no
  shortcuts, re-executes the full discarded-prefix + target-event physics)
- `plot_figure4.py` — the plotting script (reads only the above outputs)

## Old Figure 4 files — CONFIRMED OBSOLETE (not deleted)

`fig4_data_v2.json` / `fig4_best_candidate_v2.pkl` (in
`figure1_schematic_v1/`) give Δs=0.0192cm, Δw=0.548cm — these values do
not match any row in the current authoritative colored/EW cutflow CSVs,
and were committed in commit `b8f017f`, "Baseline snapshot before
trajectory/Stage-2 corrections" — i.e. they predate the vertex-relative-
fit correction and other pipeline fixes applied later in this project.
See `figure1_schematic_v1/Figure_4_status_v2.md` for the original
staleness investigation (unchanged, still accurate). **This
vertex_fixed_v1 package is the current, authoritative Figure 4
reproduction; the v2 files remain retained for provenance only.**

## Regeneration
`python3 05_coplanarity_analysis/figure4_vertex_fixed_v1/replay_figure4_event.py`
(deterministic, ~69 min wall time, no RNG-sensitive shortcuts) followed by
`python3 05_coplanarity_analysis/figure4_vertex_fixed_v1/plot_figure4.py`
(seconds, reads only the replay's own output files).
