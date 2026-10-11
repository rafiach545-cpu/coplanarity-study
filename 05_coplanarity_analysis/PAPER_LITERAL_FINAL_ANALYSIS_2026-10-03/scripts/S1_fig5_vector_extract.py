#!/usr/bin/env python3
"""Exact paper Fig. 5 histograms from the VECTOR source figures in the arXiv source tarball (figures/Deltat.pdf = Delta_s,
figures/Deltaw.pdf = Delta_w; arXiv:1708.02243 src, identical to v2). Axes calibrated from the tick-label positions (log10 axes);
each coloured step polyline -> bins (lo, hi, height); colour -> population from the legend.
Usage: S1_fig5_vector_extract.py <figures_dir> <out_json>"""
import sys, json, math, re, collections, numpy as np, pymupdf
def val(t):
    t = t.replace("−", "-"); m = re.fullmatch(r"10(-?\d+)", t)
    if m: return 10.0 ** int(m.group(1))
    return {"100": 1.0}.get(t)
def extract(path):
    p = pymupdf.open(path)[0]; W = p.get_text("words"); dr = p.get_drawings()
    nums = [(w, v) for w in W if (v := val(w[4])) is not None]
    # x tick labels share the lowest common baseline; y tick labels share a common right edge on the left
    xmin = min(w[0] for w, _ in nums); ybot = max(w[3] for w, _ in nums)
    yt = [((w[1] + w[3]) / 2, v) for w, v in nums if w[0] - xmin < 15]                    # left column = y-axis labels
    xt = [((w[0] + w[2]) / 2, v) for w, v in nums if w[0] - xmin >= 15 and ybot - w[3] < 15]   # bottom row = x-axis labels
    ax = np.polyfit([a for a, _ in xt], [math.log10(v) for _, v in xt], 1); ay = np.polyfit([a for a, _ in yt], [math.log10(v) for _, v in yt], 1)
    X = lambda u: 10 ** np.polyval(ax, u); Y = lambda u: 10 ** np.polyval(ay, u)
    legend = {}; labels = [w for w in W if w[4] in ("Colored", "EW", "Pileup", "Converted")]
    names = {"Colored": "Colored Quirk", "EW": "EW Quirk", "Pileup": "Pileup", "Converted": "Converted gamma"}
    hist = {}
    for d in dr:
        col = tuple(round(c, 3) for c in (d["color"] or ()))
        if not col or col == (0.0, 0.0, 0.0) or (d.get("width") or 0) < 2.5: continue
        if d["items"][0][0] == "re":  # legend swatch -> the legend word just right of it on the same row
            r = d["items"][0][1]; w = min(labels, key=lambda w: abs((w[1] + w[3]) / 2 - (r.y0 + r.y1) / 2) + abs(w[0] - r.x1)); legend[col] = names[w[4]]; continue
        pts = []
        for it in d["items"]:
            if it[0] == "l": pts += [(it[1].x, it[1].y), (it[2].x, it[2].y)]
        bins = []
        for (x0, y0), (x1, y1) in zip(pts[::2], pts[1::2]):
            if abs(y0 - y1) < 1e-6 and abs(x1 - x0) > 1e-6:
                lo, hi = sorted((x0, x1)); bins.append(dict(lo=float(X(lo)), hi=float(X(hi)), height=float(Y(y0))))
        hist[col] = sorted(bins, key=lambda b: b["lo"])
    out = {legend[c]: b for c, b in hist.items()}
    resid = dict(x=float(np.std([np.polyval(ax, a) - math.log10(v) for a, v in xt])), y=float(np.std([np.polyval(ay, a) - math.log10(v) for a, v in yt])))
    return dict(histograms=out, x_ticks=[v for _, v in xt], y_ticks=[v for _, v in yt], calibration_residual_dex=resid)
if __name__ == "__main__":
    fd, o = sys.argv[1], sys.argv[2]
    res = {"delta_s_cm": extract(f"{fd}/Deltat.pdf"), "delta_w_cm": extract(f"{fd}/Deltaw.pdf"),
           "source": "arXiv:1708.02243 source tarball figures/Deltat.pdf, figures/Deltaw.pdf (vector)"}
    json.dump(res, open(o, "w"), indent=1)
    for k in ("delta_s_cm", "delta_w_cm"):
        r = res[k]; print(k, "calib residual (dex)", r["calibration_residual_dex"], "ticks x", r["x_ticks"], "y", r["y_ticks"])
        for n, b in r["histograms"].items():
            h = np.array([x["height"] for x in b]); lo = np.array([x["lo"] for x in b]); hi = np.array([x["hi"] for x in b])
            frac = h / h.sum(); c = np.cumsum(frac); i = np.searchsorted(c, 0.5)
            print(f"   {n:16s} bins {len(b):2d} width(dex) {np.median(np.log10(hi/lo)):.3f} range {lo.min():.2e}-{hi.max():.2e} sum {h.sum():.3g} median-bin {math.sqrt(lo[i]*hi[i]):.3g}")
