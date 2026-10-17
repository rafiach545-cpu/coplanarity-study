# PPT-ready Summary — Reproduction of Knapen et al., Table I (v2)

## Slide 1 — Approach
- Every setting labelled by source: stated by the paper / stated by the reference detector note [27] / inferred / undocumented
- Main result uses the **paper-stated acceptance**: barrel only, |η| ≲ 1.8
- 4 independent signal samples, each shown separately, all with Wilson 95% intervals; the paper publishes no counts

## Slide 2 — Table I (figure `F06v2_table_I_primary`)

| | Paper | Sample 1 | Sample 2 | |
|---|---|---|---|---|
| Colored ε_trig | 0.24 | 0.241 | 0.237 | ✅ |
| Colored ε_fid | 0.28 | 7/27 = 0.26 | 25/68 = 0.37 | ✅ |
| Colored ε_reco (1.16 / 0.58 mm / none) | 0.35 | 0.14 / 0.43 / 0.71 | 0.12 / 0.20 / 0.44 | depends on SCT z |
| EW ε_trig | 0.10 | 0.174 | 0.178 | ❌ |
| EW ε_fid | 0.28 | 40/89 = 0.45 | 94/186 = 0.51 | ❌ (✅ only with the inferred finite barrel) |
| EW ε_reco (1.16 / 0.58 mm / none) | 0.72 | 0.15 / 0.25 / 0.85 | 0.22 / 0.31 / 0.81 | ❌ / ❌ / borderline |

## Slide 3 — What decides reconstruction (`F08v2_sct_z_envelope`, `F15v2_signal_ds_vs_paper`)
- The paper says it doubles “the intrinsic accuracy” of [27]; [27] gives 17 µm across and 580 µm along the beam
- The paper never says the doubling applies along the beam → 1.16 mm is our reading
- The paper's Fig. 5 (Δs ≈ 30 µm) only fits with little or no smearing along the beam, which no source supports

## Slide 4 — Beam spot (45 mm)
- One common shift per event, fitted from the vertex: planes survive (used)
- Fit from the origin, or a separate shift of every hit: almost nothing survives (0–4 events)

## Slide 5 — Backgrounds (`F13v2_pileup_by_acceptance`, `F14v2_conversion_by_acceptance`)
- Pile-up: 0/5000 in the signal region ✅; 8/8-layer rate ✅; 4/8-layer rate 6–12× the paper ❌
- Conversions: 0/9139 with SCT smearing ✅; **30/9139 without** ⚠
- Conversion + pile-up: 0/9139 (finite barrel, vertex fit); 1/9139 in an old run that fitted from the conversion point

## Slide 6 — Bottom line
- Reproduced with stated settings: colored trigger and fiducial; no background in the signal region
- Not reproduced: EW trigger, EW fiducial (stated acceptance), EW reconstruction with any sourced SCT smearing
- A full reproduction is impossible from published information: acceptance, SCT z resolution, beam-spot treatment and generator settings are not uniquely given
