"""
ATLAS Run-2 Inner Detector barrel geometry, 8 layers, cross-checked directly
against source PDFs (pypdf text extraction, 2026-09-14):

SOURCE ATTRIBUTION (do not assume every number below comes from one table --
verified field-by-field against the actual documents, not carried over from
an earlier, less careful pass):

  - Beam-pipe inner radius (2.35 cm): arXiv:1803.00844 (ATLAS IBL production/
    integration paper), Sec. 2.1 / Fig. 3 ("R23.5 - Inner beam-pipe"),
    explicitly "a new beam pipe of reduced inner radius of 23.5mm." Sec. 7
    describes installing that same beam pipe but does not restate the number
    there -- the number itself is in Sec. 2.1, not Sec. 7.

  - Layer radii, pixel/SCT pitches, and r-phi intrinsic resolutions: VERIFIED
    EXACTLY against Table 1 of arXiv:2007.07624 ("Alignment of the ATLAS
    Inner Detector in Run-2"): IBL 33.25mm (50/250um pitch, 10/60um res
    r-phi/z), Pixel 50.5/88.5/122.5mm (50/400um pitch, 10/115um res r-phi/z),
    SCT 299/371/443/514mm (80um pitch, 17um res r-phi). Table 1's own caption
    states explicitly: "for SCT and TRT only the resolution along r-phi is
    given" -- it does NOT provide an SCT z-resolution at all.

  - SCT z-resolution (580um intrinsic, before the paper's own doubling) is
    THEREFORE NOT FROM Table 1 of arXiv:2007.07624, despite an earlier
    version of this file's docstring and DEVIATIONS_LOG.md item 1 implying
    it was. It is very likely from the original detector-performance
    reference the Knapen et al. paper itself cites (ref [27],
    ATL-PHYS-PUB-2009-002, which is NOT one of the 3 references available for
    this re-check) -- this specific number is UNVERIFIED against the 3
    sources checked here and is flagged, not silently re-attributed to the
    wrong document. The value is left unchanged since no verified
    replacement is available.

  - Effective-resolution prescription (pixel: use pitch as effective
    resolution; SCT: double the intrinsic accuracy) comes from Sec. III A of
    arXiv:1708.02243 (Knapen, Lou, Papucci, Setford), NOT from either ATLAS
    reference -- it is that paper's own simplified modelling choice, applied
    on top of the Run-2 geometry numbers above.

Layer numbering follows the paper's convention: layer 1 = innermost (IBL),
layer 8 = outermost (SCT B6).
"""

import numpy as np

HBARC_GEV_CM = 1.973269804e-14  # 1 GeV^-1 = this many cm

# Beam pipe inner radius (photon-conversion material location, Stage 6b).
# Source: arXiv:1803.00844, Sec. 2.1 / Fig. 3 -- see module docstring.
BEAMPIPE_RADIUS_CM = 2.35  # 23.5 mm

# Each layer: (name, radius_cm, pitch_rphi_um, pitch_z_um,
#              intrinsic_res_rphi_um, intrinsic_res_z_um, is_pixel)
# Radii/pitches/r-phi resolutions: Table 1 of arXiv:2007.07624 (verified
# exactly). SCT z-resolution (580um): NOT in that table -- see module
# docstring for the attribution caveat.
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
         res_rphi_um=17, res_z_um=580, is_pixel=False),  # res_z_um: see caveat above
    dict(name="L6_SCT_B4", r_cm=37.1,  pitch_rphi_um=80, pitch_z_um=None,
         res_rphi_um=17, res_z_um=580, is_pixel=False),  # res_z_um: see caveat above
    dict(name="L7_SCT_B5", r_cm=44.3,  pitch_rphi_um=80, pitch_z_um=None,
         res_rphi_um=17, res_z_um=580, is_pixel=False),  # res_z_um: see caveat above
    dict(name="L8_SCT_B6", r_cm=51.4,  pitch_rphi_um=80, pitch_z_um=None,
         res_rphi_um=17, res_z_um=580, is_pixel=False),  # res_z_um: see caveat above
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
    """
    Pseudorapidity from polar angle theta (radians), measured from the
    NOMINAL detector origin (0,0,0) -- see trajectory_to_hits.py's own eta
    calculation for why this is the origin-relative, "fixed hardware
    acceptance" definition and not a per-event-vertex-relative one.

    Numerically safe near theta=0 and theta=pi: tan(theta/2) -> 0 or -> inf
    at those exact endpoints, which would give eta = +-inf. No real hit sits
    at exactly r=0 (theta=0 or pi means the hit is ON the beam axis, which no
    finite-radius detector layer crossing can produce), so clipping theta
    slightly away from the endpoints only avoids a spurious inf/nan for
    degenerate/test inputs, without affecting any physical hit's eta value.
    """
    eps = 1e-12
    theta_safe = np.clip(theta, eps, np.pi - eps)
    return -np.log(np.tan(theta_safe / 2.0))


def layer_radii_cm():
    return np.array([layer["r_cm"] for layer in LAYERS])
