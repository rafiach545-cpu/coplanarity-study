#!/usr/bin/env python3
"""
CANDIDATE corrected detector response (diagnostic branch; frozen project code is NOT edited).

Finding (Part A): the project's SCT response smears z with sigma = 2 x 580 um = 1.16 mm.
Truth-level plane thickness is ~1e-3 cm; with |n1.z| ~ 0.45 typical, 1.16 mm of z noise
inflates Delta_s to a median ~0.015 cm, so 70% of plane-found signal fails Delta_s < 0.01 cm,
and the factor-3 growth rule rejects SCT hits (21/22 of the EW2000 "hits available"
multiplicity failures). The paper's own Fig. 5 signal Delta_s (median ~28-35 um, ~90% below
0.01 cm) is incompatible with that response (KS p ~ 0 for both benchmarks).

Paper-consistent readings (pre-registered, notes/PREREGISTERED_VARIANTS.md):
  R2  SCT smeared in R-phi only (sigma = 2 x 17 um); z unsmeared
  R3  SCT smeared isotropically with sigma = 2 x 17 um
Pixels unchanged (quantised to pixel centre; R4 test shows Gaussian pitch/sqrt12 is equivalent).

This module exposes `sct_sigma_cm(model, layer)` and `respond(...)` so the corrected response
can be applied to any truth crossing list exactly as scripts/02_forensic_pipeline.py does.
"""
import math

SCT_RPHI_INTRINSIC_UM = 17.0      # ATLAS JINST 3 S08003, Table 4.1 (per module)
SCT_Z_INTRINSIC_UM = 580.0        # idem, "arises from the 40 mrad stereo angle"
PAPER_FACTOR = 2.0                # arXiv:1708.02243 Sec. III A: "twice the intrinsic accuracy"


def sct_sigma_cm(model):
    """Return (sigma_rphi_cm, sigma_z_cm) for the SCT under a given reading."""
    s_r = PAPER_FACTOR * SCT_RPHI_INTRINSIC_UM * 1e-4
    if model == "R0":                       # current project
        return s_r, PAPER_FACTOR * SCT_Z_INTRINSIC_UM * 1e-4
    if model == "R2":
        return s_r, 0.0
    if model == "R3":
        return s_r, s_r
    raise ValueError(model)


def respond_sct(rphi_cm, z_cm, g_rphi, g_z, model):
    """Apply the SCT response with standard-normal draws g_rphi, g_z (shared random numbers)."""
    s_r, s_z = sct_sigma_cm(model)
    return rphi_cm + s_r * g_rphi, z_cm + s_z * g_z
