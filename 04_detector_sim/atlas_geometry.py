"""
ATLAS Run-2 Inner Detector barrel geometry, 8 layers, "Method B" as specified
in the user-provided reference (Table 1 of ATLAS Collaboration, "Alignment
of the ATLAS Inner Detector in Run-2," arXiv:2007.07624), cross-checked
against the resolution/pitch treatment prescribed in Sec. III A of
arXiv:1708.02243 (Knapen, Lou, Papucci, Setford).

Layer numbering follows the paper's convention: layer 1 = innermost (IBL),
layer 8 = outermost (SCT B6).
"""

import numpy as np

HBARC_GEV_CM = 1.973269804e-14  # 1 GeV^-1 = this many cm

# Beam pipe inner radius (photon-conversion material location, Stage 6b)
BEAMPIPE_RADIUS_CM = 2.35  # 23.5 mm

# Each layer: (name, radius_cm, pitch_rphi_um, pitch_z_um,
#              intrinsic_res_rphi_um, intrinsic_res_z_um, is_pixel)
LAYERS = [
    dict(name="L1_IBL",    r_cm=3.325, pitch_rphi_um=50, pitch_z_um=250,
         res_rphi_um=10, res_z_um=60, is_pixel=True),
    dict(name="L2_PixelB0", r_cm=5.05,  pitch_rphi_um=50, pitch_z_um=400,
         res_rphi_um=10, res_z_um=115, is_pixel=True),
    dict(name="L3_PixelB1", r_cm=8.85,  pitch_rphi_um=50, pitch_z_um=400,
         res_rphi_um=10, res_z_um=115, is_pixel=True),
    dict(name="L4_PixelB2", r_cm=12.25, pitch_rphi_um=50, pitch_z_um=400,
         res_rphi_um=10, res_z_um=115, is_pixel=True),
    dict(name="L5_SCT_B3", r_cm=29.9,  pitch_rphi_um=80, pitch_z_um=None,
         res_rphi_um=17, res_z_um=580, is_pixel=False),
    dict(name="L6_SCT_B4", r_cm=37.1,  pitch_rphi_um=80, pitch_z_um=None,
         res_rphi_um=17, res_z_um=580, is_pixel=False),
    dict(name="L7_SCT_B5", r_cm=44.3,  pitch_rphi_um=80, pitch_z_um=None,
         res_rphi_um=17, res_z_um=580, is_pixel=False),
    dict(name="L8_SCT_B6", r_cm=51.4,  pitch_rphi_um=80, pitch_z_um=None,
         res_rphi_um=17, res_z_um=580, is_pixel=False),
]

# Paper's prescription (Sec III A): for PIXEL layers, use the pixel SIZE
# (pitch) directly as the effective hit resolution -- NOT the intrinsic
# single-hit resolution. For SCT layers, use 2x the intrinsic accuracy.
for layer in LAYERS:
    if layer["is_pixel"]:
        layer["eff_res_rphi_um"] = layer["pitch_rphi_um"]
        layer["eff_res_z_um"] = layer["pitch_z_um"]
    else:
        layer["eff_res_rphi_um"] = 2.0 * layer["res_rphi_um"]
        layer["eff_res_z_um"] = 2.0 * layer["res_z_um"]

FIDUCIAL_ETA_MAX = 1.8  # barrel-only acceptance (paper Sec III A)
BEAMSPOT_SIGMA_Z_CM = 4.5  # 45 mm longitudinal beamspot smearing (paper value)


def eta_from_theta(theta):
    return -np.log(np.tan(theta / 2.0))


def layer_radii_cm():
    return np.array([layer["r_cm"] for layer in LAYERS])
