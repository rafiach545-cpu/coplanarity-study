# Figure 6 — future-work grid proposal (NOT executed)

This is a proposal only. No grid scan, interpolation, or discovery/exclusion
contour was generated or approximated in this task. This document exists to
satisfy the requirement to "demonstrate why 2 benchmark points can't support
a continuous contour" and to specify what a real future scan would need.

## Why 2 points cannot support a contour

The project has exactly 2 simulated benchmark points:
- Colored (3,1)_2/3: mQ=1.8 TeV, Lambda=2 keV
- EW (1,1)_1: mQ=800 GeV, Lambda=4 keV

Figure 6 is a **95% CL exclusion/discovery contour in the continuous
(mQ, Lambda) plane** for each quirk representation, drawn from the paper's
own reference values in Table I, which itself tabulates
epsilon_reco(mQ, Lambda) at only ~5 discrete Lambda values per mQ (and the
paper's own mQ grid, not given in the text beyond the two headline points,
is denser still based on the shape of Fig.6's curves). A contour requires
epsilon_reco (and hence total efficiency) as a **continuous, or at least
finely-gridded, function of both mQ and Lambda** — 2 points fix nothing
about the functional dependence in either dimension; they are two isolated
samples of a 2D surface with unknown curvature. Interpolating a smooth
contour through 2 points (of the ~50+ that Fig.6's smooth curves imply) would
be fabrication, not reproduction — hence not attempted.

## What a real future scan needs (grid proposal, sizes only, not run)

| Parameter | Proposed values | Count | Why |
|---|---|---|---|
| mQ (colored, (3,1)_2/3) | 600, 900, 1200, 1500, 1800, 2100, 2400 GeV | 7 | spans paper's Fig.6 colored-panel x-range |
| mQ (EW, (1,1)_1) | 200, 400, 600, 800, 1000, 1200 GeV | 6 | spans paper's Fig.6 EW-panel x-range |
| Lambda | 1, 2, 3, 4, 5, 7, 10 keV | 7 | matches Table I's own Lambda sampling |
| Events/point | >=2000 (matches this project's existing per-benchmark statistics, needed to keep Wilson-interval widths comparable to what's already used elsewhere in this project) | — | statistical-precision parity with existing results |

Grid size: 7×7 (colored) + 6×7 (EW) = 49 + 42 = **91 total (mQ, Lambda) points**,
each requiring a full signal generation -> trajectory -> detector -> Sec IIIC/IV
pipeline run at >=2000 events/point => **>=182,000 total simulated events**,
roughly 20-40x this project's largest single run to date (the mu=50
converted-photon+pileup overlay, 9139 events).

## Additional required components (not yet implemented anywhere in this project)

1. **Production cross-section sigma(mQ, Lambda) over the full grid** — the
   paper's Fig.6 requires this as an external input (a QCD or Drell-Yan
   production calculation at each mQ); Lambda does not affect production
   cross-section (only Delta_s/Delta_w/efficiency), so this reduces to a
   1D scan over mQ per representation, but is still **not implemented**:
   this project has exactly one cross-section value (EW, single point,
   from this project's own MadGraph run) and zero for colored.
2. **Luminosity-normalized discovery/exclusion prescription** — Poisson
   discovery-significance (typically Z = sqrt(2*((s+b)*ln(1+s/b) - s)) or
   equivalent, per paper's stated "5-event expected signal" discovery
   criterion) at L=300fb^-1, assuming negligible background (paper's own
   stated assumption, consistent with this project's own background
   measurements — see below).
3. **Background treatment** — paper assumes negligible irreducible
   background. This project's own pile-up-only (0/5000 at every mu tested)
   and converted-photon+pileup (1/9139) measurements are *consistent* with
   that assumption but were never required as a Fig.6 input by the paper
   itself (the paper does not cite a background MC).
4. **Checkpoint/cache infrastructure** — a 91-point, >=182,000-event scan
   at this project's established runtime-per-event scale would need the
   same checkpoint/resume infrastructure already used for the large
   pileup/conversion runs (`*.csv.checkpoint` pattern already present
   elsewhere in this repo), scaled up substantially, plus a disk-usage
   estimate before launch (per this project's own standing safety-gate
   convention).

## Runtime estimate (order-of-magnitude only)

The existing 9139-event converted-photon+pileup overlay is this project's
largest completed single run. Scaling to >=182,000 signal events (a
~20x larger sample, across 91 independent parameter points each needing
separate trajectory integration with point-specific mQ/Lambda) would
plausibly require **on the order of 10-20x the wall-clock time** of the
largest run completed in this project to date, run serially; this is a
rough order-of-magnitude estimate only, not a scheduled quote, since
per-point runtime also scales with Lambda (smaller Lambda -> larger
angular momentum -> different oscillation period -> different required
dt/step-count for numerical convergence, per this project's own
dt-convergence validation elsewhere in `03_trajectory_sim/`).

## Conclusion

**No grid scan was launched.** This proposal exists solely to satisfy the
requirement to show why 2 points can't produce a contour and to specify
what would be needed. Figure 6 remains **BLOCKED / NOT REPRODUCED**, per
`figure6_requirement_matrix.csv` in `converted_photon_with_pileup_v1/`
(unchanged, re-verified this turn, still accurate).
