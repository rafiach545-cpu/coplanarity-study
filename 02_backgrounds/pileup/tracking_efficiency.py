"""
Phase 3: track reconstruction efficiency lookup, digitized from ATL-PHYS-
PUB-2015-051 Figure 1(b) (docs/reference/atl_phys_pub_2015_051/, Task A).

BASELINE SCENARIO (per user decision): "Loose" -- ref[33] itself calls this
"the default track requirements applied during 'inside-out' track
reconstruction" (Sec 3, p.4), matching the quirk paper's generic "was this
track reconstructed" concern better than the fake-optimized "Tight Primary"
selection. This is a DOCUMENTED, JUSTIFIED CHOICE, not something either
paper states explicitly -- the quirk paper never names a selection.

"Tight Primary" is retained as a SEPARATE, explicitly-labeled systematic-
variation scenario. The two curves are NEVER averaged or blended.

INTERPOLATION: piecewise-linear between digitized bin centers (the only
information available from a digitized graphical source -- no functional
form is given by either paper).

BOUNDARY TREATMENT (verified, not invented -- see Task C's decision table):
  - pT < lowest digitized point (~0.455 GeV, close to Loose/Tight's own
    pT>400MeV reconstruction threshold): efficiency = 0. This is NOT an
    extrapolation -- both Loose and Tight Primary selections REQUIRE
    pT>400MeV to be reconstructed at all (ATL-PHYS-PUB-2015-051 Sec 3), so
    a track below that threshold cannot be reconstructed BY DEFINITION,
    independent of any curve shape.
  - pT > highest digitized point (~4.5 GeV): held FLAT at the last
    digitized value. This IS a documented ASSUMPTION (not verified beyond
    the digitized range), though it is consistent with the paper's own
    prose claim of a "~90%/~85% plateau ... above pT>=5 GeV" (p.5) -- the
    digitized curve's own last points (0.896 Loose, 0.853 Tight at
    pT=4.5 GeV) are already close to those quoted plateau values.

NO systematic uncertainty band is available from this digitization (Task A
did not digitize the uncertainty bands) -- ε(pT) returned here is a central
value only.
"""
import csv
import bisect

DIGITIZED_CSV = "/home/rafia/coplanarity_study/docs/reference/atl_phys_pub_2015_051/fig1b_digitized.csv"
BASELINE_SELECTION = "Loose"
SYSTEMATIC_SELECTION = "TightPrimary"


def _load_curve(selection):
    pts = []
    with open(DIGITIZED_CSV) as f:
        for row in csv.DictReader(f):
            if row["selection"] == selection:
                pts.append((float(row["pT_GeV"]), float(row["efficiency"])))
    pts.sort()
    return pts


_CURVES = {
    BASELINE_SELECTION: _load_curve(BASELINE_SELECTION),
    SYSTEMATIC_SELECTION: _load_curve(SYSTEMATIC_SELECTION),
}


def track_efficiency(pt_gev, selection=BASELINE_SELECTION):
    """
    Returns the central-value track reconstruction efficiency at pt_gev
    (truth pT, GeV) for the given selection ("Loose" or "TightPrimary").
    See module docstring for exact boundary treatment.
    """
    if selection not in _CURVES:
        raise ValueError(f"selection must be one of {list(_CURVES)}, got {selection!r}")
    pts = _CURVES[selection]
    pt_lo, pt_hi = pts[0][0], pts[-1][0]

    if pt_gev < pt_lo:
        return 0.0  # definitional: below the pT>400MeV reconstruction threshold
    if pt_gev >= pt_hi:
        return pts[-1][1]  # documented plateau assumption

    xs = [p[0] for p in pts]
    i = bisect.bisect_right(xs, pt_gev) - 1
    x0, y0 = pts[i]
    x1, y1 = pts[i + 1]
    frac = (pt_gev - x0) / (x1 - x0)
    return y0 + frac * (y1 - y0)


BANDS_CSV = "/home/rafia/coplanarity_study/docs/reference/atl_phys_pub_2015_051/fig1b_digitized_with_bands_v2.csv"


def _load_band_curve(selection, column):
    pts = []
    with open(BANDS_CSV) as f:
        for row in csv.DictReader(f):
            if row["selection"] == selection and row[column] not in ("", "None"):
                pts.append((float(row["pT_GeV"]), float(row[column])))
    pts.sort()
    return pts


_VARIANT_CURVES = {
    ("Loose", "lower"): _load_band_curve("Loose", "lower_efficiency"),
    ("Loose", "upper"): _load_band_curve("Loose", "upper_efficiency"),
    ("TightPrimary", "lower"): _load_band_curve("TightPrimary", "lower_efficiency"),
    ("TightPrimary", "upper"): _load_band_curve("TightPrimary", "upper_efficiency"),
}


def _interp(pts, pt_gev):
    pt_lo, pt_hi = pts[0][0], pts[-1][0]
    if pt_gev < pt_lo:
        return 0.0
    if pt_gev >= pt_hi:
        return pts[-1][1]
    xs = [p[0] for p in pts]
    i = bisect.bisect_right(xs, pt_gev) - 1
    x0, y0 = pts[i]
    x1, y1 = pts[i + 1]
    frac = (pt_gev - x0) / (x1 - x0)
    return y0 + frac * (y1 - y0)


def track_efficiency_variant(pt_gev, selection=BASELINE_SELECTION, variant="central"):
    """
    PURELY ADDITIVE extension for the Fig 1(b) systematic-sensitivity test
    (2026-09-17) -- does NOT alter track_efficiency()'s existing behavior,
    used unchanged by the already-completed 5-mu sweep.

    variant: "central" (identical to track_efficiency()), "lower" (total-
    systematic lower envelope), or "upper" (total-systematic upper
    envelope), from fig1b_digitized_with_bands_v2.csv (Task A/systematics
    audit, 2026-09-17). Same boundary treatment (0 below threshold, flat
    plateau above) applies to all three variants.
    """
    if variant == "central":
        return track_efficiency(pt_gev, selection=selection)
    key = (selection, variant)
    if key not in _VARIANT_CURVES:
        raise ValueError(f"no band curve for {key}")
    return _interp(_VARIANT_CURVES[key], pt_gev)


if __name__ == "__main__":
    for pt in [0.2, 0.4, 0.455, 0.7, 1.0, 2.0, 4.5, 6.0, 10.0]:
        eL = track_efficiency(pt, "Loose")
        eT = track_efficiency(pt, "TightPrimary")
        print(f"pT={pt:5.2f} GeV: Loose={eL:.4f}  TightPrimary={eT:.4f}")
    print()
    print("Variant check (Loose):")
    for pt in [0.5, 1.0, 2.0, 4.5]:
        c = track_efficiency_variant(pt, "Loose", "central")
        lo = track_efficiency_variant(pt, "Loose", "lower")
        hi = track_efficiency_variant(pt, "Loose", "upper")
        print(f"pT={pt:.2f}: central={c:.4f} lower={lo:.4f} upper={hi:.4f}")
