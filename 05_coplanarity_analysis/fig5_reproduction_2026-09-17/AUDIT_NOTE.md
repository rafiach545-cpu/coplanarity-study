# Fig. 5 reproduction — source/audit note (2026-09-17)

Existing-data-only reproduction. No new simulation was run. No detector/cut/bin/weight
values were tuned to improve agreement with the paper.

## Source spec (from fresh re-read of paper.txt lines 480-739, Sec IIIC/IIID/IV, Fig 5 caption)

- Left panel: `dσ/dlogΔs` (fb/bin) — absolute cross-section normalized.
- Right panel: `(1/σ)dσ/dlogΔw` — unit-area (shape only) normalized.
- 4 curves per panel, NOT combined: Colored Quirk (1.8 TeV, Λ=2 keV), EW Quirk (800 GeV,
  Λ=4 keV), Pile-up, Converted γ.
- Population: Sec IIIC Event Selection output (Δw<1 cm plane found) — i.e. the paper-defined
  ε_reco population (Sec IV, p.7) — BEFORE Sec IV's stricter final cuts (hit multiplicity +
  Δs<0.01 cm) are applied. Text: "before the final cut on those variables are imposed."
- Δs<0.01 cm marked as a vertical reference line, left panel only.
- Pile-up curve uses a reweighting scheme (events allowed 1 hit/layer, reweighted by the
  efficiency of passing the stricter ≥2-hit requirement) not described for converted-γ; this
  scheme is not reproducible from currently recorded pipeline outputs.

## Files audited and verdict

| File | Verdict | Reason |
|---|---|---|
| `colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv` | USABLE | `ds`/`dw` populated for the Sec IIIC plane-found population (`truth_fiducial & ds.notna()`), matches paper population exactly. N=5. |
| `ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv` | USABLE | Same population definition. N=32. |
| `conversion_scan_results_v2_VERTEX_FIXED.csv` | **UNUSABLE — confirmed data gap** | `ds`/`dw` are NaN for all 9139 rows (2982 have `n_candidates>=1` but the plane-fit diagnostic was never recorded by `convert_and_analyze.py`). Cannot fabricate a curve. |
| `sweep_mu_2026-09-16/audit_mu50_4of8_events_reproduced.csv` | USABLE, biased | N=59, real `winner_delta_s/winner_delta_w`. Filtered to `has_4_of_8_plane==True` (≥4-layer winning candidates) — a sub-sample of the true Sec IIIC winner population, since seeding only needs 2 layers. mu=50 matches the paper's own quoted `<μ>=50` anchor value, so this is the correct μ to display, not an arbitrary choice. |
| `sweep_mu_2026-09-16/audit_mu5_event2006_reproduced.csv` | Not used as a curve | N=1 event, insufficient for a distribution; recorded here for completeness only (Δs=see JSON, Δw=see JSON), not plotted. |

## Approximations / deviations from the paper (stated explicitly, not hidden)

1. **Normalization**: paper's left panel is absolute (fb/bin); we lack a measured production
   cross-section for the colored-quirk benchmark and pile-up has no natural per-event
   cross-section, so both panels here are unit-normalized (shape only). This is a genuine
   deviation from the paper's left-panel convention, stated, not tuned.
2. **Pile-up curve is the biased ≥4-layer subsample**, not the full Sec IIIC winner
   population, and does NOT use the paper's 1-hit-reweighting scheme.
3. **Converted-photon curve is absent**, not approximated — flagged in the legend/caption
   rather than fabricated.
4. **Statistics are small** (N=5, 32, 59) — histograms are coarse; individual event Δs/Δw
   values are retained in the JSON artifact for transparency rather than being smoothed away.

## Backward trace (one example)

Colored-quirk Δs median bin (~0.012 cm): traced to
`colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv` row with `truth_fiducial=True`,
`ds` column → populated by `analyze_colored_quirk.py::analyze_one()` via
`select_reconstructed_plane()`'s fallback diagnostic (the Sec IIIC Event-Selection winning
candidate's `delta_s`, computed from `coplanarity_fit.py`'s Eq. 10/11 eigen-decomposition
on real detector-smeared hit coordinates) — confirmed NOT the Sec IV
`passes_signal_region`/`sec_iv_final_pass_rate` quantity. No εreco-labeling contamination.

## Numerical diagnostics

See accompanying `fig5_data_v3_2026-09-17.json` for full per-event arrays. Summary
(median, p16, p84, min, max, frac<0.01cm [Δs] or frac<1.0cm [Δw]):

- Colored Δs: median=0.01186, p16=0.01007, p84=0.01998, min=0.00937, max=0.02644, frac<0.01=0.20
- Colored Δw: median=0.23282, p16=0.22444, p84=0.31450, min=0.21917, max=0.44246, frac<1.0=1.00
- EW Δs: median=0.01742, p16=0.00896, p84=0.02779, min=0.00252, max=0.03192, frac<0.01=0.1875
- EW Δw: median=0.09086, p16=0.05122, p84=0.19913, min=0.03869, max=0.31508, frac<1.0=1.00
- Pileup(mu50,>=4L) Δs: median=0.03002, p16=0.02079, p84=0.03585, min=0.01174, max=0.04675, frac<0.01=0.00
- Pileup(mu50,>=4L) Δw: median=0.73196, p16=0.56898, p84=0.83698, min=0.45442, max=0.92496, frac<1.0=1.00

## Paper vs reproduction — qualitative feature comparison

| Feature | Paper | Reproduction | Match? |
|---|---|---|---|
| Signal Δs peaks well below 0.01–0.03 cm scale, left of pile-up | Yes | EW/colored medians ~0.012–0.017 cm, pileup median 0.030 cm — signal is left of pileup | MATCH (qualitative separation) |
| Pile-up Δs essentially all above 0.01cm cut | Implied by paper's claimed background rejection | frac<0.01cm = 0.00 exactly | MATCH |
| Converted-γ shown as separate curve, often overlapping pile-up in Δs | Yes | Not plotted — data gap | NOT REPRODUCIBLE FROM AVAILABLE DATA |
| Absolute fb/bin scale on left panel | Yes | Unit-normalized only | ASSUMPTION/APPROXIMATION (documented) |
| Smooth curves, high statistics | Yes (thousands of events implied) | N=5/32/59, coarse step histograms | STATISTICAL LIMITATION, not a physics discrepancy |
| Δw signal distributions clustered well below 1cm, background closer to 1cm | Yes | EW/colored Δw medians 0.09–0.23cm, pileup median 0.73cm | MATCH (qualitative ordering) |

Discrepancy classification used: (1) MATCH, (2) STATISTICAL LIMITATION (small existing N),
(3) ASSUMPTION/APPROXIMATION (normalization convention), (4) NOT REPRODUCIBLE FROM AVAILABLE
DATA (converted-γ, pile-up reweighting), (5) NOT YET CHECKED, (6) GENUINE PHYSICS DISCREPANCY
— none of the checked features fall into category (6).
