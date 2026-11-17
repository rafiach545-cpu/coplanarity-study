# Pile-up as a background: factorisation plan (2026-11-17, priority, not started)

## Why

The A580 and Z0 background passes are converted photons completed by pile-up (RESULTS §7, `compare/X10_pileup_completion.py`, `tables/X10_*.csv`).
- At μ = 0, these photons are **near-misses**: their winning plane has Δw < 1 cm and Δs < 0.01 cm, but they fail the hit-multiplicity cut. Typically they have 14 hits, where 15 are needed (7 stations with 2 hits).
- At μ = 20/50, one or two pile-up hits complete the plane. All A580 passes are of this kind, and 679 of 687 Z0 passes at μ = 50.

The total background therefore has two parts:

    N_bkg = N_trig × [ P_PU                              (A: plane from pile-up alone)
                     + Σ_obj ν_nm,obj × P_c(μ, n_miss) ]  (B: near-miss object from the hard event, completed by pile-up)

- N_trig ≈ 10⁷ MET-triggered events at 332 fb⁻¹ (`BACKGROUND_CANDIDATES.md` A).
- ν_nm,obj is the number of near-miss two-track objects per triggered event (conversions, Dalitz pairs, K_S, ...), measured at μ = 0.
- P_c is the probability that pile-up completes a near-miss. It depends on μ and on the number of missing hits, n_miss.
- Below one event in total requires each part to be below about 10⁻⁷ per triggered event.

## A. Pile-up alone

The selection is applied in steps: a plane (≥ 8 stations, Δw < 1 cm) → multiplicity → Δs < 0.01 cm. The rate factorises as

    P_PU = f_plane × f_mult|plane × f_Δs|plane,mult

- **Measuring each factor.** Each factor is measured separately on the events where it is defined.
  - The T12 test (20 events, ATLAS μ = 50) gave 11 planes, so f_plane ≈ 0.5 is directly measurable.
  - With 2 × 10⁵ events, about 10⁵ planes are available. Each conditional factor is then measured down to 3 × 10⁻⁵ (95% UL with 0 seen).
  - If one of the factors is about 10⁻³, the other must reach about 2 × 10⁻⁴ for P_PU ≈ 10⁻⁷. Both are reachable.
- **Checking that the factors are independent.** Δs and multiplicity are not assumed independent. Their joint rate is compared with the product of the separate rates for looser cuts, where there are enough counts:
  - Δs < 0.02, 0.05 and 0.1 cm;
  - ≥ 5 or 6 stations with 2 hits.
  - The ratio of joint to product is used as a correction, with its spread as a systematic.
- **Tails with zero counts.** If a factor shows zero counts, its tail is extrapolated:
  - the Δs CDF is fitted for 0.02–0.2 cm with a power law, down to 0.01 cm;
  - the distribution of the number of stations with 2 hits is fitted, out to 7.
  - The UL is quoted next to the extrapolation.
- **Code change.** C01 `--pileup-only` is modified to record **every** candidate per event, not only the winner: stations with 1 and 2 hits, Δs, Δw, and hit counts. Otherwise, after the winner cut, the factors could not be measured separately.

## B. Near-miss completed by pile-up

- **P_c(μ, n_miss), by oversampling.** Each near-miss photon–region row is overlaid with K independent pile-up draws (new pile-up seeds, same photon). This uses a new C01 option `--rows FILE --overlays K`; K = 0 must reproduce production (test T13).
  - So far each near-miss has one overlay: the ATLAS A580 estimate at μ = 50 is 5/470 = 1.1% ± 0.5%.
  - With K = 100: 470 × 100 overlays give about 500 passes, so P_c is known to about 5%. P_c is also given as a function of n_miss and of the end-cap content.
- **ν_nm (μ = 0 only, cheap).**
  - For Zγ it is already known from the C01 μ = 0 runs.
  - For Z(νν̄)+jets and W+jets it needs B01–B02 and C01 at μ = 0 (`ZJETS_PLAN.md`). The expensive μ = 50 runs on jet objects (about 40 h there) are then no longer needed.
  - With P_c ≈ 1–3%, 10⁻⁷ per event needs ν_nm ≲ 3 × 10⁻⁶ – 10⁻⁵ per event.

## Cost

**Coding: about 2 days.**
- Candidate-level output for `--pileup-only`: ½ day.
- `--rows` / `--overlays` with test T13: ½ day.
- F01 analysis (factors, independence check, tail fits, combined rate with errors): 1 day.

**Server time.** Estimates use 40-worker jobs. The per-event cost is taken from the measured laptop per-photon costs, about 2.4 s × worker at μ = 20 and 11.5 s × worker at μ = 50 for ATLAS, with an uncertainty of about ×2.

| Job | Size | Time per 40-worker job |
|---|---|---|
| S0 pilot: pile-up only, ATLAS A580, μ = 50 | 2 000 events | ≈ 10 min (measures f_plane and the true cost; S1 is then resized) |
| S1 pile-up only, ATLAS, {A580, Z0} × μ = 20 | 2 × 10⁵ events each | ≈ 3.3 h each |
| S1 pile-up only, ATLAS, {A580, Z0} × μ = 50 | 2 × 10⁵ events each | **≈ 16 h each** |
| S2 oversampling, ATLAS: A580 (470 rows × 100) + Z0 (2 000 rows × 20), μ = 20 and 50 | about 87 000 rows per μ | ≈ 2.8 h together |
| S2 oversampling, Ideal A580 (122 rows × 100), μ = 20 and 50 | 12 200 rows per μ | ≈ 10 min |
| S3 near-miss rate in Z+jets (only if Z+jets is required) | 10⁵ events, μ = 0 | ≈ 1–2 h |

- **Total.** About 1 650 core-hours. On 160 cores this is **about 11 h** if the μ = 50 jobs use 80 workers each, or about 16 h with four parallel 40-worker jobs.
- **Smaller option.** If the pilot shows f_plane ≈ 0.5, 10⁵ events per setting are enough, and the total halves (≈ 6–8 h).
- **Memory.** Each worker holds the pool (a few hundred MB). 160 workers need about 40–80 GB.
- **Ideal geometry.** The same S1 for Ideal costs about 1/4 of ATLAS (the pile-up hits are barrel only). It can be added if the Ideal comparison needs it.

## Order

1. Code and T13 (laptop).
2. S0 pilot.
3. S2 oversampling (short, and it fixes P_c).
4. S1 sized from the pilot.
5. F01 combination.
6. S3 after the professor decides on Z+jets.

The result replaces the "Zγ only" caveat on the A580 background with a total that includes pile-up.
