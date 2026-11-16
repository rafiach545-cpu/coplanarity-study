# Signal: what must be redone with the real ATLAS geometry and material (2026-11-15)

Signal yield: N = L σ ε_trig f_ch k/n (06 report). The table lists, for each factor, whether the real geometry changes it.

| Factor | Changes? | Why | Action |
|---|---|---|---|
| σ(pp → QQ̄), MG5 | **No** | Production cross section, independent of the detector | keep (Stage 1/2 values) |
| Generated events (MG5 + Pythia8, `inputs/<tag>_events.csv`) | **No** | Generator level | reuse; the S2b larger samples near the contour are still planned |
| ε_trig (pT(QQ̄) > 200 GeV, truth proxy) | **No** with the current proxy | Defined on generator momenta | keep. A real MET-trigger turn-on would be a separate change |
| f_ch (both quirk-hadrons charged, colored) | **No** at production; **yes** if charge exchange in material is added | f_ch comes from Pythia hadronisation; nuclear interactions in the material can flip the charge along the path | keep. Charge flip is a later option, or a systematic |
| Trajectory (propagation) | **Yes** | Ionisation loss dE/dx in each layer slows the quirks (βγ ≈ 0.2–0.7); the field falls from 2 T to ~0.9 T at the ID ends (R4); end-cap crossings | rerun the propagation (F6_02 equivalent) with material and geometry |
| Hits and k/n (fiducial, plane, multiplicity, final) | **Yes** | New layers (end-cap disks), timing rule (SCT 01X, R5), hit efficiency 99.74% (R5), resolutions | rerun the reconstruction |
| Fiducial rule "16 first crossings in the 8 barrel layers" | **Must be redefined** | With end-caps the 8 layers are not always the same 8 cylinders. T01: with barrel only, all 8 layers are crossed for \|η\| ≤ 1.15; with disks, ≥ 4 pixel + ≥ 4 SCT elements are crossed up to \|η\| = 2.5 | **decision for the supervisor**: count "8 silicon elements" instead of "8 barrel layers"? |
| Reach (N = 3, 5 contours, background) | **Yes** | follows from k/n and the new background | redo for 13 and 13.6 TeV |

**Short answer:**

- **Cross section:** no new cross sections and no new event generation for the signal.
- **Detector part:** everything after generation must be rerun with the new geometry and material: propagation, hits, COP, k/n and reach. Because the end-caps add acceptance at \|η\| > 1.15, k/n may increase.
- **Background:** new processes (Z(νν̄)+jets, W+jets) need new generation and new cross sections (`../backgrounds/`). The tested Z+γ background needs a new detector simulation, but not a new generation.

## Expectation written before the 07 signal run (2026-11-16)

Written before any 07 signal result, so the run can be compared with it.

- **Fiducial acceptance goes up.**
  - Stage 2 needs all 16 first crossings on the 8 barrel layers. That means \|η\| ≲ 1.2–1.4 (T01: all 8 layers for \|η\| ≤ 1.15 at z0 = 0).
  - With the disks, ≥ 4 pixel + ≥ 4 SCT elements are crossed up to \|η\| = 2.5.
  - The gain is limited by the 25 ns cut: the disks are at \|z\| up to 272 cm, and a quirk with β ≈ 0.3–0.5 needs 18–30 ns to get there. The gain should therefore be largest for light EW quirks (fast) and smaller for heavy colored ones (slow).
  - Guess: ε_fid × 1.2–1.6.
- **Reconstruction efficiency of the new events is lower than in the barrel.**
  - Pairs whose two quirks cross different elements at the barrel/end-cap boundary pass only partly (T03 (e): 5/11).
  - On the disks the coarse SCT coordinate is R, so the seed-pair cut \|Δr\| < 2 cm is used.
- **Signal yield:** k/n should rise by less than ε_fid.
- **Settings:**
  - A580 should lie between Z0 and Z1160 for both signal and background.
  - The Z0 background is 3–4 times the Stage 2 one (C01), so the Z0 gain over Z1160 in reach shrinks.
  - Z1160 keeps zero background, so its reach changes only through k/n.

## Expectation written before the large-sample generation (G02, 2026-11-16)

10 000 generated events per mass point (5 chunks × 2000, L01 unchanged, new seeds) for the 13 Stage 2 points, then G01 atlas with the three SCT settings.
- **Cross sections:** equal to Stage 2 (`counts.csv`, 2000 events) within the combined MC errors (the cards differ only in nevents and iseed).
- **Trigger-pass events** (colored: both quirk-hadrons charged) ≈ 5 × Stage 2: EW 100/200/400/600/800/1000 GeV: 235 / 470 / 675 / 795 / 870 / 960; colored 600/900/1200/1500/1800/2100/2400 GeV: 220 / 340 / 425 / 320 / 330 / 270 / 290, each within ≈ 3 binomial σ.
- **ε_fid, ε_reco** in the barrel-only rule (fid_stage2, stored by G01): equal to Stage 2 within the Stage 2 statistical errors; their errors shrink by ≈ √5.
- **CPU:** generation ≈ 1–2.5 min per chunk (65 chunks); G01 ≈ 5 s (mid), 0.2 s (low), 20 s (high_a) per event at the barrel timing, somewhat more with the end-cap elements: ≈ 45 CPU hours.
