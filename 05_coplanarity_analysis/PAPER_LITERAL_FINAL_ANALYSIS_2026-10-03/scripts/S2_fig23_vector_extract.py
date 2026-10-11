#!/usr/bin/env python3
"""Paper Fig. 2 (figures/angular_momentum.pdf: L blue, d green dashed) and Fig. 3 (figures/steps.pdf: colored purple, EW red) curves from the
VECTOR source figures in the arXiv:1708.02243 source tarball. Linear axes calibrated from tick-label centres (x: bottom row; left y: left
column; right y: right column). Usage: S2_fig23_vector_extract.py <figures_dir> <out_json>"""
import sys, json, numpy as np, pymupdf
def num(t):
    try: return float(t.replace("−", "-"))
    except ValueError: return None
def axes(p):
    W = [(w, v) for w in p.get_text("words") if (v := num(w[4])) is not None]
    xs = [w[0] for w, _ in W]; xmin, xmax = min(xs), max(xs); ybot = max(w[3] for w, _ in W)
    left = [((w[1] + w[3]) / 2, v) for w, v in W if w[0] - xmin < 12]
    right = [((w[1] + w[3]) / 2, v) for w, v in W if xmax - w[0] < 12 and xmax - xmin > 300]
    bottom = [((w[0] + w[2]) / 2, v) for w, v in W if ybot - w[3] < 8 and w[0] - xmin >= 12]
    fit = lambda pts: np.polyfit([a for a, _ in pts], [v for _, v in pts], 1)
    return fit(bottom), fit(left), (fit(right) if len(right) >= 2 else None), dict(bottom=[v for _, v in bottom], left=[v for _, v in left], right=[v for _, v in right])
def curves(path, names, right_for=()):
    p = pymupdf.open(path)[0]; ax, ay, ar, ticks = axes(p); out = {}
    for d in p.get_drawings():
        col = tuple(round(c, 3) for c in (d["color"] or ()))
        if col not in names or len(d["items"]) < 4: continue
        pts = [(it[1].x, it[1].y) for it in d["items"] if it[0] == "l"] + [(d["items"][-1][2].x, d["items"][-1][2].y)]
        X = np.polyval(ax, [q[0] for q in pts]); Y = np.polyval(ar if names[col] in right_for else ay, [q[1] for q in pts])
        out[names[col]] = dict(x=X.tolist(), y=Y.tolist())
    return dict(curves=out, ticks=ticks)
if __name__ == "__main__":
    fd, o = sys.argv[1], sys.argv[2]
    res = {"fig2": curves(f"{fd}/angular_momentum.pdf", {(0.0, 0.0, 1.0): "L_1e12_hbar", (0.0, 0.502, 0.0): "d_cm"}, right_for=("d_cm",)),
           "fig3": curves(f"{fd}/steps.pdf", {(0.502, 0.0, 0.502): "colored_1800GeV_2keV", (1.0, 0.0, 0.0): "EW_800GeV_2keV"}),
           "source": "arXiv:1708.02243 source tarball figures/angular_momentum.pdf, figures/steps.pdf (vector)"}
    json.dump(res, open(o, "w"), indent=1)
    for f in ("fig2", "fig3"):
        print(f, res[f]["ticks"])
        for n, c in res[f]["curves"].items():
            x, y = np.array(c["x"]), np.array(c["y"]); print(f"   {n}: {len(x)} pts, x {x.min():.2f}-{x.max():.2f}, y {y.min():.4g}-{y.max():.4g}, y at max x {y[np.argmax(x)]:.4g}")
