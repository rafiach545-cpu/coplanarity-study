# Event 2555 forensic audit — why it passed (v1) — 2026-09-21

Read-only forensic audit. No full simulation was rerun; only event 2555 was
targeted, via deterministic replay of the exact original seeds (the
sequential `rng_photon` stream required replaying its state through the
discarded events 0..2554 first — an unavoidable consequence of the
single-stream design, not a new simulation of those events' full pipeline).

**A bug was found and fixed during this audit, in the audit script itself
(not in the authoritative data)**: the first replay attempt fed RAW
(pre-merge) conversion hits into the μ=0 reconstruction instead of MERGED
hits (what v3/v4 actually use), producing Δs=0.005525cm — inconsistent
with v4's stored 0.005823cm. Corrected by merging `raw_conv_hits` via
`merge_neighboring_pixel_hits()` first, exactly matching v3/v4's code
path. **After the fix, the replay reproduces v4's stored row for event
2555 exactly** (Δs, Δw, layer count, hit-multiplicity flag, n_hits — all
bit-identical), confirmed below. The μ=50 branch matched the authoritative
overlay CSV on first attempt (Δs=0.0090945384209177 both).

## 1. Event identity
- Event ID: **2555** (0-indexed row position in `zgamma_photons.csv`, matching the `event` column written by both the v4 and overlay drivers).
- Master seed (photon stream): **99**, single sequential `np.random.default_rng(99)`.
- Pile-up/suppression stream: `SeedSequence([90210777, 2555]).spawn(2)`.
- Sampled pile-up multiplicity: **N_PU = 56**.
- Sampled minimum-bias pool-event IDs (56 draws, all unique): 10492, 7425, 5239, 3702, 5794, 9524, 18719, 11575, 12852, 15006, 16173, 5987, 12712, 9627, 19478, 12160, 11042, 14971, 337, 10046, 16289, 9718, 11645, 6432, 15219, 1773, 17901, 11596, 19573, 10042, **3628**, 12734, 1036, 3377, 12956, 15331, 4418, 3510, 841, 19973, 11752, 19992, 639, 9215, 12504, 10940, 16773, 14737, 15048, 4315, 14458, 7817, 763, 11000, 18158, 5432. (DETERMINISTIC REPLAY EVIDENCE.)
- Authoritative output: `02_backgrounds/photon_conversion/conversion_with_pileup_mu50_v1.csv`, sha256=`66f715e107797a9e0c88a9baaedadda7bf2fde51f7872aa3c3e81a4e4a065856` (unchanged, re-verified).
- Event 2555 appears **exactly once** (DIRECTLY STORED EVIDENCE, verified).
- `final_sec_iv_pass=True` is **directly stored**, not reconstructed after the fact.

## 2. μ=0 baseline (CORRECTED, verified bit-identical to v4)
- Photon: pT=51.86GeV (from photon_info.json), η/φ as stored.
- Conversion point: (x,y,z) stored in `event2555_photon_info.json`.
- e⁻/e⁺ four-momenta: equal 50/50 split, stored.
- Raw conversion hits: 16. **Merged (postmerge): 14** — matches v4's `n_hits=14` exactly.
- Selected-plane per-layer hit counts (merged): L8=2, L7=2, L6=2, L5=**1**, L4=2, L3=2, L2=**1**, L1=**1**.
- Δs(μ=0) = **0.0058233 cm** — confirms the previously-reported 0.00582 value.
- Δw(μ=0) = 0.315129 cm.
- Hit-multiplicity: **FAIL**. Three layers (1, 2, 5) have fewer than 2 hits — the cut allows only **one** such exception, so 3 deficient layers is a clear, non-borderline failure.
- Final Sec IV: **FAIL** (consistent with v4).
- **First failure reason: hit-multiplicity** (Δs and Δw both already pass their own thresholds at μ=0).

## 3. μ=50 overlay state (matches authoritative CSV exactly)
- N_PU=56, 6034 particles propagated, 1593 primary tracks (643 removed/reconstructed, 950 kept/failed), 177 secondary, 0 ambiguous.
- Raw pile-up hits before suppression: 12389; after suppression: 7663.
- Raw conversion hits: 16 (unchanged). Combined premerge: 7679. Postmerge: **7675** — matches the overlay CSV's `n_hits=7675` exactly.
- Mixed hard+pileup merged clusters: 0 (none of the merged clusters combined a conversion hit and a pile-up hit into the *same* pixel cluster — the pile-up hits landed close to, not on top of, the conversion hits).
- Δs(μ=50) = **0.0090945 cm** — confirms the previously-reported 0.00910 value, **< 0.01cm**.
- Δw(μ=50) = 0.478525 cm.
- Selected-plane per-layer hit counts: L8=2, L7=2, L6=2, L5=**1**, L4=3, L3=3, L2=2, L1=2.
- Hit-multiplicity: **PASS** — only layer 5 (1 hit) remains below 2, exactly the single allowed exception.
- Final Sec IV: **PASS**.

## 4. Exact pile-up hits responsible
`event2555_selected_plane_hits_with_origin.csv`, `responsible_pileup_particle.json`. **A single pile-up track** — pool event **3628**, particle index **10** (the 31st of 56 sampled interactions, tag `pu30_ev3628_p10`) — a **primary** charged pion (m=0.1396GeV, q=+1, pT=0.242GeV), whose track failed the Loose tracking-efficiency Bernoulli draw (retained in the "unassociated" pool, per ref[33]'s own definition of this background source) — contributed exactly one hit each to layers **1, 2, 3, and 4**:

| Layer | μ=0 conv hits | μ=50 hits | Pile-up hits added | Final hits | Required | μ=0 status |
|---|---|---|---|---|---|---|
| 8 | 2 | 2 | 0 | 2 | ≥2 (or the 1 exception) | ok |
| 7 | 2 | 2 | 0 | 2 | ≥2 | ok |
| 6 | 2 | 2 | 0 | 2 | ≥2 | ok |
| 5 | 1 | 1 | 0 | 1 | ≥2 | **insufficient (remains the allowed exception)** |
| 4 | 2 | 3 | 1 | 3 | ≥2 | ok (was already ok, over-satisfied) |
| 3 | 2 | 3 | 1 | 3 | ≥2 | ok (already ok, over-satisfied) |
| 2 | 1 | 2 | 1 | 2 | ≥2 | **insufficient → fixed by pile-up** |
| 1 | 1 | 2 | 1 | 2 | ≥2 | **insufficient → fixed by pile-up** |

**Missing layers at μ=0**: 1, 2, and 5 (three deficient layers, cut allows one). **Pile-up hits that fixed it**: the same single track's hits on layers 1 and 2 (layers 3, 4 also gained a hit each but were not deficient). **Layer 5 remains at 1 hit even at μ=50** — this is the one allowed exception, unchanged by pile-up.

## 5. How the reconstructed plane changed
n_candidates=1 at **both** μ=0 and μ=50 (single candidate throughout — pile-up did not create a competing candidate). Normal vector n1: cosine similarity = 0.99998, angle = **0.371°** — essentially the same plane. **Conclusion: pile-up preserved and enlarged the original conversion candidate**, it did not create a different or new plane. Δ(Δs) = Δs(μ=50) − Δs(μ=0) = **+0.003271 cm**. Δ(Δw) = +0.163396 cm. No conversion hits were lost; 4 pile-up hits were added, 3 of them on already-sufficient layers (3, 4) and 2 on the deficient layers (1, 2) — layer 3 and 4 each received exactly 1 of the 4 added hits, matching the single track's 4 total crossings (layers 1,2,3,4).

## 6. Software-artifact verification
- Raw+raw single merge: **CONFIRMED** — `overlay_and_merge(raw_conv_hits, raw_pileup_hits)` used exactly once (DIRECTLY STORED + code inspection).
- No duplicate hit IDs: CONFIRMED in the forensic replay's merged-hit tables (sequential unique IDs by construction).
- No accidental event duplication: CONFIRMED, event 2555 appears exactly once in the authoritative CSV.
- All selected-hit references resolve: CONFIRMED, every `merged_hit_id` in `selected_plane_hits` exists in `event2555_merged_hits_mu50.csv`.
- No NaN/Inf: CONFIRMED (repo-wide check, prior turn's audit + this event's specific values are all finite).
- Timing requirement: applied inside `simulate_quirk_hits` (code-level, unchanged); not separately re-verified per-hit here (UNAVAILABLE at hit level for this specific check, would require re-instrumenting timing rejection counters, not done).
- Barrel acceptance (|η|<1.8): applied inline in `simulate_quirk_hits` (code-level, confirmed unchanged); per-hit rejection count UNAVAILABLE (same limitation documented in the earlier converted-photon-only freeze).
- Vertex convention: consistently the conversion point for both μ=0 and μ=50 reconstructions (DIRECTLY STORED, `vertex_cm` reused identically).
- Mixed-cluster provenance survived merging: CONFIRMED — `source_quirk_indices` correctly distinguishes conversion (`[1]`/`[2]`/`[1,2]`) from pile-up (`["pu30_ev3628_p10"]`) hits, with 0 clusters that actually mixed both categories together for this event.
- Sec IIIC/Sec IV thresholds match source: CONFIRMED, `dw_max_cm=1.0`, `ds_max_cm=0.01` (coplanarity_fit.py:177,195, unchanged).
- Independent recomputation: **DETERMINISTIC REPLAY EVIDENCE** — after the merge-order bugfix, Δs/Δw/hit-multiplicity/final verdict at μ=0 reproduce v4's stored row exactly; at μ=50 they reproduce the authoritative overlay CSV's stored row exactly.
- Deterministic replay reproduces the same result: **CONFIRMED**, both states.

## 7. Statistics (unchanged from the prior correction — re-verified here)
k=1, n=9139. Point estimate=0.000109421. Wilson 68%=[0.0000418,0.000286], Wilson 95%=[0.0000193,0.000620], Clopper-Pearson 68%=[0.0000191,0.000360], Clopper-Pearson 95%=[0.0000028,0.000610]. Cross-checked via explicit formula and `scipy.stats.beta`; `statsmodels` unavailable in this environment (unchanged limitation, not a new finding). The 0.01 conversion weight is confirmed **not** used as a binomial count anywhere in this analysis. Raw conditional probability = 1/9139 = 0.000109421. Physical 1%-weighted equivalent = 0.01/9139 = 1.0942×10⁻⁶. **This single event does not, by itself, establish agreement with the paper** — it is one realization of a small-number process with a wide confidence interval spanning roughly two orders of magnitude.

## 8. Diagnostic figures
- `event2555_selected_plane_xy_rz.png` — transverse (x-y) and longitudinal (r-z) displays of the selected plane's hits, colored by origin (conversion=blue, pile-up=red, mixed=purple; 0 mixed clusters occurred for this event's selected hits).
- `event2555_layer_comparison.png` — per-layer hit-count bar chart, μ=0 vs μ=50, with the required-multiplicity line marked.
- Source data: `event2555_selected_plane_hits_with_origin.csv`, `layer_comparison_table.csv`, `event2555_merged_hits_mu0.csv`, `event2555_merged_hits_mu50.csv`, `event2555_raw_conversion_hits.csv`, `event2555_raw_pileup_hits.csv`.

## 9. Evidence limitations
Per-hit timing/η rejection counts are UNAVAILABLE (never separately logged by `simulate_quirk_hits`, a pre-existing limitation documented in the earlier converted-photon-only freeze, not new to this audit). All other requested quantities were recovered, either DIRECTLY STORED or via DETERMINISTIC REPLAY.

## Files changed
- `02_backgrounds/photon_conversion/forensic_replay_event_2555.py` (new)
- `05_coplanarity_analysis/event_2555_forensic_v1/*` (new: JSON summaries, CSVs, PNGs)
- `docs/event2555_forensic_audit_v1.md` (this report)
- No authoritative event CSV modified. No simulation rerun beyond the targeted, necessary event-2555 replay (and its unavoidable rng-state prefix replay).

## Test commands and exit codes
- `python3 02_backgrounds/photon_conversion/forensic_replay_event_2555.py` — exit 0 (initial replay, later identified to have the μ=0 merge-order bug).
- Inline correction script (μ=0 recomputation from saved raw hits) — exit 0, verified bit-identical to v4.
- `python3 tests/test_wilson_interval_regression.py` — exit 0 (unchanged from prior correction).

## Confirmation
No process remains running (verified via `ps aux`). No EW/colored job, pile-up sweep, or Figure 6 scan was started.
