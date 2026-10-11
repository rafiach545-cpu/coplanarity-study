#!/usr/bin/env python3
"""
Digitise the paper's Fig. 4 (figures/display.pdf, arXiv source) sample event from its vector paths.
Crosses ('x' markers = two crossing line segments, width 2.0) inside the inset give the hit coordinates
(n3, n2) in cm, using the inset tick labels printed in the PDF (n3: 0..80, n2: -1..1).
Digitisation uncertainty: half the marker-centre spread between the two segment midpoints, plus
the axis-fit residual.
Test: Delta_w(definition) = sqrt( sum_a (x_a.n2)^2 / (N-1) )  [paper Eqs. 10-11, second eigenvalue]
compared with the caption value 0.074 cm.
"""
import json, math, re, os
import numpy as np, fitz
HERE = os.path.dirname(os.path.abspath(__file__))
p = fitz.open(f"{HERE}/../paper_figures/display.pdf")[0]
labels = []
for b in p.get_text("dict")["blocks"]:
    for l in b.get("lines", []):
        t = "".join(s["text"] for s in l["spans"]).strip().replace("−", "-")
        x0, y0, x1, y1 = l["bbox"]; labels.append((t, (x0 + x1) / 2, (y0 + y1) / 2, l["bbox"]))
# inset tick labels: n3 '0'..'80' along the inset top; n2 '-1.0'..'1.0' at the inset right
inset_x = [(float(t), cx) for t, cx, cy, bb in labels if re.fullmatch(r"\d0|0", t) and cy < 260 and cy > 180]
inset_y = [(float(t), cy) for t, cx, cy, bb in labels if re.fullmatch(r"-?\d\.\d", t)]
fx = np.polyfit([c for _, c in inset_x], [v for v, _ in inset_x], 1)
fy = np.polyfit([c for _, c in inset_y], [v for v, _ in inset_y], 1)
res_x = np.std(np.polyval(fx, [c for _, c in inset_x]) - [v for v, _ in inset_x])
res_y = np.std(np.polyval(fy, [c for _, c in inset_y]) - [v for v, _ in inset_y])
xmin, xmax = min(c for _, c in inset_x) - 5, max(c for _, c in inset_x) + 5
ymin, ymax = min(c for _, c in inset_y) - 5, max(c for _, c in inset_y) + 5
hits = []
for d in p.get_drawings():
    if not d.get("width") or abs(d["width"] - 2.0) > 0.01 or len(d["items"]) != 2:
        continue
    pts = [(it[1].x + it[2].x) / 2 for it in d["items"]], [(it[1].y + it[2].y) / 2 for it in d["items"]]
    cx, cy = np.mean(pts[0]), np.mean(pts[1])
    if xmin <= cx <= xmax and ymin <= cy <= ymax:
        hits.append((float(np.polyval(fx, cx)), float(np.polyval(fy, cy))))
hits = sorted(hits)
n2 = np.array([h[1] for h in hits]); n3 = np.array([h[0] for h in hits])
N = len(hits)
dw_rms_nm1 = math.sqrt(np.sum(n2 ** 2) / (N - 1))
out = dict(N_hits=N, hits_n3_n2_cm=hits, axis_fit_residual=dict(n3_cm=float(res_x), n2_cm=float(res_y)),
           n2_scale_cm_per_pt=float(abs(fy[0])),
           delta_w_sqrt_sum_over_Nminus1=dw_rms_nm1, delta_w_rms_over_N=math.sqrt(np.mean(n2 ** 2)),
           half_range=float((n2.max() - n2.min()) / 2), max_abs=float(np.abs(n2).max()),
           mean_abs=float(np.mean(np.abs(n2))), caption_delta_w_cm=0.074)
json.dump(out, open(f"{HERE}/../tables/paper_fig4_event_digitised.json", "w"), indent=1)
for k, v in out.items():
    print(k, v if not isinstance(v, list) else [(round(a, 2), round(b, 3)) for a, b in v])

# ---- second calibration: the red "+-Delta_w" band (fill colour (0.98,0.502,0.447)) is drawn at
# n2 = +-0.074 cm by construction; its pixel edges fix the n2 scale and zero independently of the
# tick labels.
bands = []
for d in p.get_drawings():
    f = tuple(round(c, 3) for c in (d.get("fill") or ()))
    if f == (0.98, 0.502, 0.447):
        ys = [pt.y for it in d["items"] for pt in it[1:] if hasattr(pt, "y")] or [d["rect"].y0, d["rect"].y1]
        xs = [pt.x for it in d["items"] for pt in it[1:] if hasattr(pt, "x")] or [d["rect"].x0, d["rect"].x1]
        bands.append((min(xs), max(xs), min(ys), max(ys)))
band = [b for b in bands if 260 < (b[2] + b[3]) / 2 < 300][0]   # inset band (y-centre ~277 pt); main-plot band is ~160 pt
y_top, y_bot = band[2], band[3]
scale = 2 * 0.074 / (y_bot - y_top)                     # cm per pt
y0 = (y_top + y_bot) / 2
hits2 = []
for d in p.get_drawings():
    if not d.get("width") or abs(d["width"] - 2.0) > 0.01 or len(d["items"]) != 2:
        continue
    cx = np.mean([(it[1].x + it[2].x) / 2 for it in d["items"]]); cy = np.mean([(it[1].y + it[2].y) / 2 for it in d["items"]])
    if xmin <= cx <= xmax and ymin <= cy <= ymax:
        hits2.append((float(np.polyval(fx, cx)), float(-(cy - y0) * scale)))
hits2 = sorted(hits2)
m2 = np.array([h[1] for h in hits2])
res = dict(band_pt=band, scale_cm_per_pt=scale, tick_scale_cm_per_pt=float(abs(fy[0])),
           hits_n3_n2_cm_bandcal=hits2,
           delta_w_sqrt_sum_over_Nminus1=math.sqrt(np.sum(m2 ** 2) / (len(m2) - 1)),
           mean_n2=float(m2.mean()), half_range=float((m2.max() - m2.min()) / 2))
json.dump(res, open(f"{HERE}/../tables/paper_fig4_event_digitised_bandcal.json", "w"), indent=1)
print("\nBAND CALIBRATION")
for k, v in res.items():
    print(k, v if not isinstance(v, list) else [(round(a, 2), round(b, 3)) for a, b in v])
