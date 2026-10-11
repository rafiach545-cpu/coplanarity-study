#!/usr/bin/env python3
"""
Extract the paper's Fig. 6 d_cm contours (dotted blue paths, colour (0.275,0.51,0.706)) from
DY_limits.pdf / colored_limits.pdf and invert Eq. (1),
  d_cm = 2 cm (gamma-1) (mQ/100 GeV) (keV/Lambda)^2,
to obtain the paper's own average (gamma-1) as a function of mQ.
Axis calibration from the PDF tick labels: x linear; y log (10..1000 eV) below the break,
linear (1000..30000 eV) above it.
"""
import json, math, os
import numpy as np
import fitz
HERE = os.path.dirname(os.path.abspath(__file__))
F = f"{HERE}/../paper_figures"
D_VALUES_CM = [1e4, 1e2, 1.0, 0.1, 0.01]          # 100 m, 1 m, 1 cm, 1 mm, 100 um (bottom -> top)
def lam_eV(y):
    if y >= 282.95:                                  # log section: 10^1 @378.85, 10^3 @282.95
        return 10 ** (1 + (378.85 - y) / 47.95)
    if y >= 225.25:                                  # 1000 @282.95 .. 10000 @225.25
        return 1000 + (282.95 - y) / (282.95 - 225.25) * 9000
    return 10000 + (225.25 - y) / 66.1 * 10000       # 10000 @225.25, 20000 @159.15, 30000 @93.05
out = {}
for f, x2m, masses in (("DY_limits.pdf", lambda x: (x - 115.2) / 84.0 * 250, [400, 600, 800, 1000]),
                       ("colored_limits.pdf", lambda x: 500 + (x - 115.2) / 100.8 * 500, [1200, 1500, 1800, 2100])):
    p = fitz.open(f"{F}/{f}")[0]
    paths = [d for d in p.get_drawings() if tuple(round(c, 3) for c in (d.get("color") or ())) == (0.275, 0.51, 0.706)]
    paths.sort(key=lambda d: -max(it[1].y for it in d["items"] if it[0] == "l"))
    res = {}
    for dval, d in zip(D_VALUES_CM, paths):
        pts = [(it[1].x, it[1].y) for it in d["items"] if it[0] == "l"] + [(d["items"][-1][2].x, d["items"][-1][2].y)]
        xs = np.array([x2m(x) for x, _ in pts]); ys = np.array([y for _, y in pts]); o = np.argsort(xs)
        for m in masses:
            y = float(np.interp(m, xs[o], ys[o])); L = lam_eV(y) / 1000.0
            g1 = dval * L * L / (2.0 * m / 100.0)
            res.setdefault(str(m), []).append(dict(d_cm=dval, Lambda_keV=L, gamma_minus_1=g1))
    out[f] = res
    for m, v in res.items():
        print(f, "mQ", m, " ".join(f"d={e['d_cm']:g}cm:L={e['Lambda_keV']:.3g}keV,g-1={e['gamma_minus_1']:.3f}" for e in v))
json.dump(out, open(f"{HERE}/../tables/paper_fig6_dcm_extracted.json", "w"), indent=1)
