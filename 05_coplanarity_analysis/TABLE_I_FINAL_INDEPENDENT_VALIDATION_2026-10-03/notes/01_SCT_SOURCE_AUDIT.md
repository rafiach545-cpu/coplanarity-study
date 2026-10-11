# Task 1 — SCT smearing: what the sources actually determine

## Direct sources (verbatim)

**Paper** (arXiv:1708.02243v2, Sec. III A; identical in v1):

> "The intersections of the trajectories with a simplified model of the ATLAS inner detector are calculated, and the center of each pixel hit is used as the input for our analysis. We hereby use the parameters of the various detector elements as specified in [27]. Specifically, for the pixel detector we use the pixel size rather than the resolution and for the silicon microstrip tracker (SCT) we conservatively assume a resolution of twice the intrinsic accuracy quoted in [27]."

Sec. III C: "A single hit is then defined by its position three-vector".

**Ref. [27]** = ATL-PHYS-PUB-2009-002, "The Expected Performance of the ATLAS Inner Detector". CDS is bot-blocked, but the same text was published as the chapter "TRACKING – THE EXPECTED PERFORMANCE OF THE INNER DETECTOR" of the ATLAS CSC book, arXiv:0901.0512 (PDF pages 40–43). It is extracted verbatim to `ref27_CSC_ID_chapter_pages40-43.txt`; PDF SHA-256 is in `csc_pdf_sha256.txt`.

> "For the SCT, eight strip layers (four space points) are crossed by each track. In the barrel region, this detector uses small-angle (40 mrad) stereo strips to measure both coordinates, with one set of strips in each layer parallel to the beam direction, measuring R−φ. Each side of a detector module consists of two 6.4 cm long, daisy-chained sensors with a strip pitch of 80 µm. … The intrinsic accuracies per module in the barrel are 17 µm (R−φ) and 580 µm (z) …"

Table "Intrinsic accuracy": "SCT Barrel 17 (R-φ) 580 (z)¹", with footnote "¹ Arises from the 40 mrad stereo angle".

The same chapter's table of active dimensions gives the pixel sensitive barrel as "0 < |z| < 400.5" mm and the SCT sensitive barrel as "0 < |z| < 749" mm. This is the source for the finite-barrel geometry, now taken directly from ref. [27].

## Answers

| Question | Answer | Source |
|---|---|---|
| Which SCT coordinates does the paper smear? | The paper says only "a resolution of twice the intrinsic accuracy". It does not name coordinates. Ref. [27] quotes the intrinsic accuracy in **both** R-φ (17 µm) and z (580 µm), and states that the SCT measures **both coordinates** via the stereo strips. | paper + ref. [27] |
| Is 17 µm a pitch, an intrinsic accuracy or a Gaussian sigma? | **Intrinsic accuracy** (single-module resolution). The pitch is 80 µm. Ref. [27] uses no word "sigma"; treating the accuracy as a Gaussian σ is the conventional reading (an inference). | ref. [27] |
| Why 34 µm? | The paper's "twice the intrinsic accuracy": 2 × 17 µm. | paper + ref. [27] |
| SCT z: (a) not smeared | Not stated in the paper. Contradicts the literal text, because ref. [27] quotes a z accuracy. | — |
| (b) 34 µm | Not stated; would require applying the R-φ number to z. | — |
| (c) ≈ 580 µm | The intrinsic z accuracy, but without the paper's factor 2; inconsistent with "twice". | ref. [27] |
| **(d) 1.16 mm** | **The literal reading:** 2 × 580 µm. This was the original project implementation. | **paper + ref. [27]** |
| (e) strip / line, not a 3D point | **Excluded by the paper:** "A single hit is then defined by its position three-vector". | paper Sec. III C |

## Conflict with the paper's own figures

The literal reading (d) is **inconsistent with the paper's published Fig. 5**.
- The signal Δs median is about 28 µm (EW) and 35 µm (colored), with about 90% below 0.01 cm.
- Under (d), our median is about 150 µm and only about 30% are below 0.01 cm (KS p ≈ 0 for both benchmarks).
- The paper's Fig. 4 event has Δs = 83 µm, which is also hard to obtain with 1.16 mm z noise on 8 of 16 hits, given |n₁·ẑ| ~ 0.45.

**The paper therefore does not determine the SCT z treatment**: its text (d) and its figures (≈ a or b) disagree.

## Decision (made before looking at any new efficiency)

All defensible alternatives are carried as a **systematic envelope**:

| Label | SCT R-φ | SCT z | Status |
|---|---|---|---|
| Z0 | 34 µm | none | **calibrated** (selected previously knowing Table I): **not paper-proven** |
| Z34 | 34 µm | 34 µm | figure-compatible alternative |
| Z580 | 34 µm | 580 µm | intrinsic z accuracy without the factor 2 |
| Z1160 | 34 µm | 1160 µm | **paper-text literal** (original baseline) |

- Pixel response is the same for all: pixel-centre quantization, "the center of each pixel hit" (paper), with neighbouring-pixel merging.
- Fig. 5 compatibility is reported for each, as evidence, without selecting by Table I.
