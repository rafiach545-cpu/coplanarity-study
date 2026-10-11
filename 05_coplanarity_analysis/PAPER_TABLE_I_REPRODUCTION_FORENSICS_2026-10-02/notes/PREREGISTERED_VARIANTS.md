# Pre-registered diagnostic variants (written BEFORE any variant was evaluated)

Date: 2026-10-02.

Variants are fixed here before results are seen, so the choice cannot be made by matching Table I.

## Paper text being interpreted (arXiv:1708.02243v2, Sec. III A, verbatim)

> "The intersections of the trajectories with a simplified model of the ATLAS inner detector are calculated, and the center of each pixel hit is used as the input for our analysis. We hereby use the parameters of the various detector elements as specified in [27]. Specifically, for the pixel detector we use the pixel size rather than the resolution and for the silicon microstrip tracker (SCT) we conservatively assume a resolution of twice the intrinsic accuracy quoted in [27]. Hits in neightboring pixels, according to the above definitions, are merged to a single hit…"

Primary detector source (ATLAS JINST 3 S08003, Table 4.1 and §1): the pixel is 50×400 µm², with intrinsic accuracy 10 µm (R-φ) × 115 µm (z). The SCT barrel intrinsic accuracy per module is 17 µm (R-φ) × 580 µm (z), with z "aris[ing] from the 40 mrad stereo angle". Ref [27] itself is unreadable (CDS bot block).

## Resolution readings (each is a defensible reading of the text above; no free parameters)

| ID | Pixel response | SCT response | Basis |
|---|---|---|---|
| R0 | quantize to pixel centre (50×400 µm) | Gaussian σ = 34 µm (R-φ), 1160 µm (z) | **current project**; "center of each pixel hit", 2× intrinsic in both coordinates |
| R1 | Gaussian σ = pitch (50, 400 µm) | as R0 | "use the pixel size rather than the resolution" read as σ = size |
| R2 | quantize (as R0) | Gaussian σ = 34 µm in R-φ only; z not smeared | SCT strips measure R-φ; the "resolution" is the R-φ accuracy (cf. arXiv:2007.07624 Table 1: "for SCT … only the resolution along r–φ is given") |
| R3 | quantize (as R0) | Gaussian σ = 34 µm in R-φ **and** z | a single quoted "resolution" number applied isotropically |
| R4 | Gaussian σ = pitch/√12 (14.4, 115.5 µm) | as R0 | Gaussian equivalent of digital quantization (tests the √12 question) |

Units: the project converts µm → cm with ×1e-4, and that conversion is verified as correct.

## Algorithm readings (Sec. III C)

| ID | Rule | Basis |
|---|---|---|
| A0 | current project (factor-3 growth vs the **current** list; smallest-\|x·n1\| first; candidates kept independently; selection Δw<1 → smallest Δs) | literal text |
| A1 | factor-3 growth measured vs the **seed** Δs, Δw | alternative reading of "do not increase by a factor of 3" |
| A2 | selection: among Δw<1 candidates, prefer the one with most layers covered, then smallest Δs | diagnostic only: **not** paper text (paper says smallest Δs) |

## Selection criterion (fixed in advance)

1. A resolution reading is preferred only if it reproduces the paper's own Fig. 5 signal Δs and Δw shapes (extracted from the vector PDF) for **both** EW and colored.
2. Table I ε_reco is then a **prediction**, not a fit target.
3. Any variant that improves EW but worsens colored relative to Table I is rejected.
4. A2 is reported but cannot be adopted, because it contradicts the paper's text.
