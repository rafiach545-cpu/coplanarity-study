# Figure 6 of arXiv:1708.02243v2: reproduction settings and checks

Status: 18 October 2026. Computed for Λ = 0.1–25 keV at every mass point that can reach 3 events. The 15–25 keV band was added overnight on 18 October. Λ > 25 keV and Λ < 100 eV are not computed.

Figure: `FINAL_FIGURES/F6_fig6/F6_fig6.png` (and .pdf). Numbers: `fig6/F6_N_grid.csv` (every grid point: k, n, ε, N with ±1σ), `fig6/F6_reach.csv`, `fig6/F6_failure_bound.csv`, `fig6/F6_ew_lo_ratio.csv`.

## What the paper says

These quotes are from the v2 source, `quirks_prd_v2.tex`.

- **The plotted quantity.** "Contours of having 3 (5) events in the m_Q vs Λ plane for an integrated luminosity of 300 fb⁻¹". Also: "The 3 events bound corresponds to 2-σ exclusion given no background. Discovery is defined by 5 events."
- **Backgrounds.** Sec. IV: "assuming negligible irreducible backgrounds". No background enters Fig. 6.
- **Efficiency.** ε = ε_trig × ε_fid × ε_reco (Eq. 12). The trigger is p_T(QQ̄) > 200 GeV. ε_fid requires all 8 layers and t < 25 ns. ε_reco is the signal region of Sec. IV.
- **Colored charge.** Sec. II: "the probability for those final states to have ±1 charges is roughly 30%". The paper does not say whether Fig. 6 includes this factor.
- **Cross section.** "MadGraph5_aMC@NLO … up to 1 jet … matched using Pythia8". The paper gives no σ values.
- **Overlays.** HSCP and monojet limits come from Farina et al., supplied privately. The d_cm lines come from Eq. 1.
- **Reach.** Abstract: "string tension between 100 eV and 30 keV, … colored (electroweak charged) quirks as heavy as 1600 (650) GeV may be discovered".
- **Validity.** Sec. II: the straight-string approximation holds for "Λ ≫ 100 eV".

## Implementation

| Item | This work |
|---|---|
| Event samples | figure6_full_v1 generation (unchanged): MG5 3.7.3 + Pythia8, MLM matched (xqcut 30), nn23lo1, 2000 events per mass. Colored 600–2400 GeV, EW 100–1000 GeV |
| N, colored | 300 fb⁻¹ × σ_matched × ε_trig × f_ch × (k/n). ε_trig = N(p_T(QQ̄) > 200)/N(matched). f_ch = fraction of triggered events with both quirk-hadrons charged (abs(q) > 0.5, as in Table I). A second line drops f_ch |
| N, EW | 300 fb⁻¹ × σ_matched × ε_trig × (k/n), ε_trig = N(p_T(QQ̄) > 200)/N(matched) of the same matched + shower sample (since 2026-10-19; the paper's described method, so all efficiencies come from one sample). Alternative (sensitivity only): the LO ratio σ_B/σ_A (A: pp → QQ̄; B: pp → QQ̄ + j with p_T(j) > 200 GeV, ickkw 0), which reproduces Table I's 0.096 at 800 GeV but is not stated in the paper; it is 0.54–0.75 × the matched count |
| k/n | n = propagated events (trigger; colored: both charged). k = events in the signal region. k/n = ε_fid × ε_reco |
| Pipeline | Same as Table I (P18/P20). Production integrator with 300 steps per period, B = 2 T, first crossing, Ref. [27] lengths, t < 25 ns, plane search and signal region as in the paper |
| SCT z | Both settings with the same random draws: 1.16 mm (paper text; the same-smearing background is 0/9139) and none (reproduces Table I; the same-smearing background is 146/9139) |
| Λ grid | 0.1, 0.2, 0.3, 0.5, 0.7, 1, 2, 3, 4, 5, 7, 10, 15, 20, 25 keV. The 15–25 keV points use the numba positions-only integrator, which is bitwise identical to the production integrator (validation: 396 rows, 0 differences) |
| Points not propagated | Colored 2400 (N_max 0.9 without f_ch): N < 3 even with ε_fid = ε_reco = 1. Colored 2100: with f_ch N_max = 1.15 < 3; it is run only for the line without f_ch |
| Contour | log10 N interpolated linearly in m_Q and in the paper's Λ display coordinate (log below 1 keV, linear above), only between grid points with a measured N (k ≥ 1) or a bound. Points with k = 0 have no measured N, so no contour passes through them. They are marked: grey ✕ means the 95% UL on N is below 3; red ✕ means it is not resolved (UL ≥ 3) |
| Paper curves | Extracted from the vector figures (`scripts/S4_fig6_vector_extract.py`). The y calibration is checked to be continuous at 1000 eV |

## Checks

| Check | Result |
|---|---|
| EW LO ratio at 800 GeV vs Table I (0.096) | 0.0961 ± 0.0006 |
| Colored 1800 GeV, independent sample vs Table I production | ε_trig 227/854 = 0.27 vs 0.24. f_ch 0.33 vs 0.33. σ 0.319 vs 0.329 fb. ε_fid 20/75 vs 22/68. ε_reco (no smearing) 3/19, 11/20, 16/20, 17/20, 9/20 at 1, 2, 3, 5, 10 keV vs 2, 8, 17, 20, 14 /22. All within ~1.5σ |
| Integration failures, colored 1800 GeV | 5, all in 4 events that are not fiducial at any Λ, so no bias |
| Paper y-axis calibration | The log and linear pieces meet at 1000.0 eV in both panels |
| EW 800 GeV, independent sample vs Table I production (no SCT z) | ε_reco 5/46, 28/47, 37/48, 42/48, 35/47 (0.11, 0.60, 0.77, 0.88, 0.74) at 1–5 keV vs 0.19, 0.65, 0.67, 0.81, 0.68. ε_fid 0.32 vs 0.33. Paper: 0.11, 0.41, 0.65, 0.72, 0.74; ε_fid 0.28 |
| Duplicates in the checkpoints | none (every file: unique events = propagated events) |
| Integration failures on events that are fiducial at another Λ | at most 1–2 per (mass, Λ). Near the contour nose (colored 1500–1800, EW 600–800) the effect on k is 0–4%, below the statistical error (`fig6/F6_failure_bound.csv`) |
| Interpolation artefact (found and fixed) | The first version set k = 0 points to an arbitrary small N, which drew boundaries that no data support. Now no contour passes through k = 0 points |

## Result: maximum mass reach (300 fb⁻¹; brackets = N at the Wilson 68% bounds of k/n)

| | Exclusion, 3 events | Discovery, 5 events |
|---|---|---|
| Paper, Fig. 6 | colored 1793, EW 762 GeV | colored 1707, EW 688 GeV |
| Paper, abstract | – | colored 1600, EW 650 GeV |
| No SCT z smearing, with the charge factor | colored 1702 (1651–1747), EW 792 (766–815) | colored 1591 (1538–1639), EW 701 (681–722) |
| No SCT z smearing, without the charge factor | colored 1893 (1859–1929) | colored 1820 (1784–1852) |
| SCT z 1.16 mm (same for signal and background), with the charge factor | colored 1497 (1438–1558), EW 524 (482–567) | colored 1424 (1368–1482), EW 473 (440–514) |
| SCT z 1.16 mm, without the charge factor | colored 1655 (1592–1724) | colored 1586 (1527–1651) |

All maxima are at Λ = 4–5 keV (SCT z 1.16 mm, EW: 7 keV), as in the paper (4–5 keV).

## What is not covered

- **Λ > 25 keV.** The integrator has a ceiling of 20 million steps. At 30–35 keV it removes 5–56% of the events that are fiducial at 10 keV, which would bias the efficiency strongly low (`fig6/F6_high_step_ceiling_scan.csv`). A larger ceiling needs about 5–7 GB per process. The paper's contours reach about 31–35 keV.
- **Λ < 100 eV and m_Q below the sample range** (colored < 600 GeV, EW < 100 GeV).
- **Low-Λ edges (≲ 0.7 keV).** 0 of 40–150 events pass there, and at the lightest masses the 95% UL on N is still ≥ 3. Resolving these edges needs larger samples.
- **Cross-section normalisation.** The paper gives no σ. We use our matched σ for both channels, with no K-factor and no tuning.

## Normalisation sensitivity (no new simulation; `scripts/F6_05_sensitivity.py`, `fig6/F6_reach_sensitivity.csv`, `FINAL_FIGURES/F6_kfactor/`)

Every grid N is multiplied by a common factor and the contours are redrawn. This is a sensitivity study, not a fit. Signal has no SCT z smearing; the charge factor is included.

| Variant | Colored exclusion / discovery (GeV) | EW exclusion / discovery (GeV) |
|---|---|---|
| Paper, Fig. 6 | 1793 / 1707 | 762 / 688 |
| K = 1 (our LO σ) | 1702 / 1591 | 792 / 701 |
| K = 1.2 (EW) | – | 824 / 730 |
| K = 1.4 (EW) | – | 850 / 759 |
| K = 1.5 (colored) | 1789 / 1679 | – |
| K = 1.8 (colored) | 1817 / 1718 | – |
| K = 2 ("N_Q = 2" read as ×2 on σ) | 1831 / 1741 | 910 / 824 |
| EW ε_trig = LO ratio instead of the matched count (×0.54–0.75 per mass; reproduces Table I's 0.10) | – | 712 / 643 |
| EW fully LO: LO-ratio trigger and ε_fid, ε_reco from the LO sample at 800 GeV (report Section 2.3) | – | 717 / 648 |
| Annihilation, worst case (α = 0.05, survival from D27 at the benchmark masses, applied to all masses) | 1672 / 1560 | 758 / 671 |

Colored: an overall factor of about 1.5–1.7 on the signal puts our maxima on the paper's curves; the paper gives no σ, so its source cannot be identified. EW (paper's method): our maxima are already +4% / +2% from the paper's, so a factor > 1 overshoots. A factor 2 overshoots both channels.
(Before 2026-10-19 the EW main line used the LO ratio: 712 / 643 GeV, now the "LO ratio" row.)

Main-figure changes (2026-10-17):
- Title wording.
- Maxima with ±1σ written in each panel.
- Notes on the normalisation: LO, no K-factor, N_Q not applied, EW ε_trig = LO ratio.
- Notes on the red ✕ regions, Λ > 10 keV and the annihilation worst case.

## 15–25 keV band (18 October 2026; checks in `fig6/F6_high_a_checks.csv`)

| Check | Result |
|---|---|
| Completeness | All 11 points complete (unique events = propagated events). No duplicates. Both lanes exited with code 0. The memory watchdog never had to act |
| Step-ceiling failures among the events fiducial at 10 keV | 0–1 at 15–20 keV; 0–3 at 25 keV (≤ 13%, EW 100 GeV). Most failures are in events that are never fiducial |
| Effect on the maxima | None. The maxima stay at 3–5 keV: colored 1702 / 1591 and EW 712 / 643 GeV (EW with the LO-ratio trigger used until 2026-10-19) (exclusion / discovery, no SCT z smearing, with the charge factor) |
| Shape | Without SCT z smearing, the upper part of our contours follows the paper's up to 20–25 keV (EW reaches about 400 GeV at 20–22 keV; colored reaches about 1250–1450 GeV at 20 keV). With 1.16 mm the contours close at about 10–15 keV |
| Physics trend | ε_reco falls above 10 keV, as the paper says, because hits merge. Example, EW 800 GeV with no SCT z smearing: k = 21, 12, 7 at 15, 20, 25 keV |

## EW trigger changed to the paper's method (19 October 2026)

| Item | Result |
|---|---|
| Change | EW ε_trig = N(p_T(QQ̄) > 200)/N(matched) of the matched + shower sample (before: LO ratio). ε_fid, ε_reco unchanged (same sample). Colored unchanged |
| Reason | The paper describes one sample (“0 + 1 jet ... matched using Pythia8”) and a p_T(QQ̄) > 200 GeV trigger; it does not state an LO ratio. Taking the trigger from LO and ε_fid, ε_reco from the matched sample mixed two samples |
| EW 1000 GeV | N_max = 300 × 0.0645 fb × 190/988 = 3.72 ≥ 3, so it is now propagated (190 events, all 15 Λ). Best point 4 keV: k = 45, N = 0.88 < 3; it does not move the contour (EW 800 max N = 2.88 at 4 keV). Integration failures: 1–4 per Λ up to 15 keV, 15 at 20 keV and 43 at 25 keV (step ceiling), where N < 0.2 anyway |
| Masses outside the grid | Not needed: EW 1000 N ≤ 0.88 (×2 → 1.8); colored 2400 N_max 0.9 even with ε_fid = ε_reco = 1 |
| Result (no SCT z smearing) | EW 792 / 701 GeV (paper 762 / 688): +4% / +2%. With the LO ratio: 712 / 643 (-7% / -7%) |
| Code checks added | F6_03 stops if a checkpoint has fewer events than propagated (a partial file had given a wrong test value). counts.csv n_trigger_both_charged now uses abs(q) > 0.5 like F6_02/F6_03 (was abs(q) = 1; informational column only, the figure was already right) |
