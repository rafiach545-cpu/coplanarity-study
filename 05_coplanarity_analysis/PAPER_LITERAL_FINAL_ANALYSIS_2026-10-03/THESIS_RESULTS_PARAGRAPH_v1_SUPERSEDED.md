# Thesis paragraph — Results of the reproduction

We reproduced the signal efficiencies of Table I in Knapen et al. (arXiv:1708.02243) using only settings stated in the paper or in its detector reference (the ATLAS Inner Detector performance note, ref. [27]). Each of the four independent signal samples is analysed separately.

**Coloured benchmark** (m_Q = 1800 GeV, Λ = 2 keV): we obtain trigger efficiencies of 101/419 = 0.241 and 207/873 = 0.237 and fiducial efficiencies of 6/27 = 0.22 and 22/68 = 0.32. Both agree with the paper's 0.24 and 0.28 within Wilson 95% intervals.

**Electroweak benchmark** (m_Q = 800 GeV, Λ = 4 keV): the fiducial efficiencies, 33/89 = 0.37 and 62/186 = 0.33, are consistent with 0.28. Agreement requires the finite barrel lengths of the reference detector rather than a pseudorapidity cut. The electroweak trigger efficiency, however, is 0.174–0.178, significantly above the paper's 0.10 (p < 10⁻⁶). It remained at 0.13–0.19 under 36 documented variations of the event generation.

**Reconstruction.** The efficiency for the full signal region (a reconstructed plane; two hits in seven layers and at least one in the eighth; Δw < 1 cm; Δs < 0.01 cm) depends almost entirely on the SCT hit resolution along the beam axis. With the resolution the paper's text specifies (twice the 580 µm intrinsic accuracy), we find 2/33 = 0.06 and 10/62 = 0.16 for the electroweak benchmark, and 1/6 and 1/22 = 0.05 for the coloured benchmark. The paper quotes 0.72 and 0.35. An independent sample generated with fresh seeds and a configuration fixed in advance confirms these values (0.14 and 0.06). The paper's own Δs distributions (its Fig. 5) are, however, only compatible with a resolution of at most a few tens of µm. Without beam-axis smearing, the same events give 0.81–0.82 (electroweak) and 0.36–0.83 (coloured). Since the paper does not document this choice, we report the literal result as our reproduction and the alternative as a systematic envelope.

**Backgrounds.** No background event passes the signal region:
- 0 of 5000 pile-up events at ⟨μ⟩ = 50;
- 0 of 9139 photon conversions;
- 0 of 9139 conversions overlaid with pile-up.

These correspond to 95% upper limits of 6.0×10⁻⁴ and 3.3×10⁻⁴ per event, or fewer than 0.21 conversion events at 300 fb⁻¹ with our Z(νν)γ+jet cross-section, in line with the paper's conclusion. Planes with at least one hit in all eight layers occur at a rate of 2×10⁻⁴, compatible with the paper's 6×10⁻⁵. Planes with hits in at least four layers occur at 6.6×10⁻³, about six times more often than the paper reports.

We also find that the detector model without beam-axis smearing, which brings the signal efficiencies toward Table I, admits 22 of 9139 photon conversions into the signal region (about 1.5 events at 300 fb⁻¹). A calibrated model of this kind therefore cannot be adopted without re-examining the background.
