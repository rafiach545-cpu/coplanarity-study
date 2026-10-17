# Response to the review of the v4 report (2026-10-05)

New events were generated only for the pre-registered trigger combinations (MG5 + Pythia, 2000 events per benchmark). Everything else reprocessed existing events. Report: `PROFESSOR_REPORT_2026-10-04_v5.pdf`.

## 1. Can electron material effects explain the paper's conversion Δs without SCT z smearing? (`scripts/P16_conversion_material.py`)

**Setup.**
- Exact helix between layers.
- At each layer: deterministic bremsstrahlung E → E·e^(−t), as in the simulation the paper cites (arXiv:1612.00850 App. A: Bethe-Bloch + bremsstrahlung, **no multiple scattering**), and optionally Highland multiple scattering.
- t per layer scanned at 1%, 3%, 5% X₀. These are assumptions: the cited radiation lengths (Andreazza 2009) are not available here.
- Validation: with t = 0 the result equals P9d event by event (Δs within 1×10⁻⁵ cm).

**Result** (conversion only, no SCT z smearing; `tables/conversion_material_summary.csv`):
- Plane Δs median: 2 µm → 16 / 33 / 42 µm with bremsstrahlung + scattering at 1 / 3 / 5% X₀.
- Events passing hit multiplicity: median 50–67 µm, 96–100% below the cut.
- Paper: ≈ 280 µm and 3.6% below the cut. **Material effects do not explain it.**

**Decisive test: no SCT z smearing + μ = 50 pile-up** (`scripts/P10f_overlay_eta_noz.py`, same photons and seeds as P10e):

| | Plane | Hit multiplicity | Signal region |
|---|---|---|---|
| Events | 6041 | 559 (6.1%) | **375 (4.1%)** |

- For the hit-multiplicity population: Δs median 81 µm, 67% below the cut.
- **Paper:** 0.67% reach the cut, median ≈ 280 µm, 3.6% below. No smearing therefore gives 9× too many conversions reaching the cut and ≈ 0.4 fb in the signal region (paper σ), against the paper's ≈ 0.002 fb.
- **SCT z 1.16 mm + pile-up:** 2.1% reach the cut, median 209 µm, 0/193 below the cut.
- **Conclusion:** the signal panel of the paper's Fig. 5 favours no SCT z smearing, while the conversion panel favours ≈ 1 mm. No single setting reproduces both in our simulation.

## 2. Population of the paper's Fig. 5

- The Δs axis is dσ/d log Δs in fb per bin (`paper_figures/Deltat.png`). The Δw panel is unit-normalised.
- Conversions are overlaid with pile-up (paper Sec. III D), so the comparable population is conversion + pile-up after plane + hit multiplicity.
- The paper's conversion histogram totals 0.067 fb, i.e. 0.67% of σ × P_conv ≈ 10 fb, with 0.0024 fb (3.6%) below the cut.
- The earlier 3.6% vs 3.7% comparison used all conversion-only planes. That was the wrong population, and it has been replaced.

## 3. Trigger framing

- **Lead statement:** the lowest EW ε_trig in any setting or combination is 0.126 [0.110, 0.145] (C4). It does not reach 0.10, whatever colored does, so the statement holds for per-sample settings too.
- **The EW/colored ratio** is secondary evidence; it assumes common settings for both samples.
- **Open, ask the authors:** a misprint, a different denominator, or an unstated EW-specific cut. The trigger search stops here.

## 4. PDF actually used in the combinations

- The compiled `Source/run_card.inc` has `PDLABEL = 'cteq6l1'` for C1 and C5, for both EW and colored.
- `scalefact = 2` is confirmed by SCALUP: the median event scale is 2× that of G2.
- The "NNPDF23_lo (247000)" line in the EW MG logs comes from the systematics step after generation, not from generation.
- C1 EW σ equals G2 σ because cteq6l1 (+9%) and scale ×2 (−10%) roughly cancel.
- **The combination results stand.**
