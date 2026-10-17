# PPT-ready Summary — Literal Reproduction of Knapen et al., Table I

## Slide 1 — Approach
- Only settings stated in the paper or in its detector reference [27]; **no tuning to Table I**
- 4 independent signal samples, each reported separately (no pooling)
- Every number is k/n with Wilson 95% intervals; the paper publishes no counts

## Slide 2 — Table I: literal result (figure: `FINAL_FIGURES/F06_table_I_comparison`)

| | Paper | Our 1st sample | Our 2nd sample | |
|---|---|---|---|---|
| Colored ε_trig | 0.24 | 0.241 (101/419) | 0.237 (207/873) | ✅ |
| Colored ε_fid | 0.28 | 0.22 (6/27) | 0.32 (22/68) | ✅ |
| Colored ε_reco | 0.35 | 0.17 (1/6) | 0.05 (1/22) | ❌ |
| EW ε_trig | 0.10 | 0.174 (89/511) | 0.178 (186/1045) | ❌ |
| EW ε_fid | 0.28 | 0.37 (33/89) | 0.33 (62/186) | ✅ |
| EW ε_reco | 0.72 | 0.06 (2/33) | 0.16 (10/62) | ❌ |

## Slide 3 — Why reconstruction fails (figure: `F08_diag_sct_z_envelope`, `F05_fig5_ds_dw_normalised`)
- The paper's text gives an SCT z resolution of 2 × 580 µm = **1.16 mm**
- The paper's own Fig. 5 Δs (median ≈ 30 µm) is only possible with ≲ 34 µm or no smearing
- The same events give EW ε_reco **0.06–0.16 (literal)** vs **0.81–0.92 (no / small smearing)**
- → The paper's text and figures disagree, and the paper does not document what it used

## Slide 4 — EW trigger (figure: `F09_diag_ew_trigger`)
- 36 one-at-a-time generator variations: EW ε_trig = 0.13–0.19, never 0.10
- Colored 0.24 reproduces → the EW/colored ratio of 0.42 cannot be reached
- Unresolved: undocumented generator settings

## Slide 5 — Backgrounds (figures: `F11_background_cutflow_and_yields`, `F10_background_event_displays`)
- Pile-up μ = 50: **0/5000** in the signal region; 8/8-layer planes 2e-4 (paper 6e-5) ✅; 4/8-layer planes 6.6e-3 (paper 1e-3) ❌
- Photon conversions: **0/9139**; conversion + pile-up: **0/9139** → < 0.21 events at 300 fb⁻¹ (95% CL)
- ⚠ The "no SCT z smearing" detector that matches Table I lets **22/9139 conversions** into the signal region (~1.5–7 events at 300 fb⁻¹)

## Slide 6 — Bottom line
- Trigger (colored) and fiducial: **reproduced**
- EW trigger and reconstruction: **not reproduced** with the literal settings
- A 100% reproduction is **impossible** from published information (SCT z resolution, generator settings and raw counts undocumented)
- A calibrated configuration can be shown only if labelled "calibrated", together with its conversion background
