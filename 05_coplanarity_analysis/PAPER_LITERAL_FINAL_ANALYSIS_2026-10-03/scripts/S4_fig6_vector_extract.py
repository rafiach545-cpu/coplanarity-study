#!/usr/bin/env python3
"""Paper Fig. 6 (arXiv:1708.02243v2, figures/colored_limits.pdf and figures/DY_limits.pdf) -> curves in (m_Q [GeV], Lambda [eV]) from the vector paths.
Calibration from the tick marks next to the tick labels: x linear; y piecewise, log10 below 1000 eV (ticks 10, 100, 1000) and linear above (ticks 10000,
20000, 30000); the two pieces must meet at 1000 eV (checked). Curves identified by stroke colour / dash / fill (matplotlib defaults of the paper's plot):
exclusion = purple (0.5,0,0.5) dashed; discovery = salmon (0.98,0.5,0.45) solid; HSCP 300 fb-1 = green dashed; HSCP 12.9 fb-1 = solid green outline of the shaded area;
monojet 300 fb-1 = grey dashed; monojet 12.9 fb-1 = solid grey outline of the shaded area; d_cm = blue dotted (labels 100 um ... 100 m, assigned by vertical order).
Output: tables/paper_fig6_vector.json, tables/paper_fig6_curves.csv"""
import os, json, numpy as np, pandas as pd, fitz
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"; FIG = f"{HERE}/../paper_source_arXiv_1708.02243/v2_Nov2017/figures"
def pts(d):
    out = []
    for it in d["items"]:
        if it[0] == "l": out += [it[1], it[2]]
        elif it[0] == "c": out += [it[1], it[4]]
        elif it[0] == "re": r = it[1]; out += [r.tl, r.tr, r.br, r.bl]
    xy = []
    for p in out:
        if not xy or abs(p.x - xy[-1][0]) > 1e-6 or abs(p.y - xy[-1][1]) > 1e-6: xy.append((p.x, p.y))
    return np.array(xy)
def calib(page):
    words = {}
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = "".join(s["text"] for s in l["spans"]).strip(); words.setdefault(t, l["bbox"])
    ticks = [pts(d) for d in page.get_drawings() if d.get("color") == (0.0, 0.0, 0.0) and len(d["items"]) == 1 and d["items"][0][0] == "l"]
    ticks = [t for t in ticks if len(t) == 2]
    xt = [t for t in ticks if abs(t[0, 0] - t[1, 0]) < 1e-3]; yt = [t for t in ticks if abs(t[0, 1] - t[1, 1]) < 1e-3]
    def near_x(xc): return min((t[0, 0] for t in xt), key=lambda v: abs(v - xc))
    def near_y(yc): return min((t[0, 1] for t in yt), key=lambda v: abs(v - yc))
    xs = [(float(k), near_x((v[0] + v[2]) / 2)) for k, v in words.items() if k.isdigit() and v[1] > 400]
    ylog = [(10 ** int(k[2:]), near_y((words[k][1] + words[k][3]) / 2)) for k in ("101", "102", "103")]
    ylin = [(float(k), near_y((words[k][1] + words[k][3]) / 2)) for k in ("10000", "20000", "30000")]
    ax = np.polyfit([p for _, p in xs], [v for v, _ in xs], 1)
    al = np.polyfit([p for _, p in ylog], [np.log10(v) for v, _ in ylog], 1); bl = np.polyfit([p for _, p in ylin], [v for v, _ in ylin], 1)
    y1000 = (3 - al[1]) / al[0]; lin_at = np.polyval(bl, y1000)
    def to_val(xy):
        x = np.polyval(ax, xy[:, 0]); y = np.where(xy[:, 1] >= y1000, 10 ** np.polyval(al, xy[:, 1]), np.polyval(bl, xy[:, 1])); return x, y
    return to_val, dict(x_ticks=xs, y_log_ticks=ylog, y_lin_ticks=ylin, y_page_at_1000eV=float(y1000), linear_fit_value_at_that_y=float(lin_at))
RGB = {"exclusion": ((0.5, 0.0, 0.5), True), "discovery": ((0.98, 0.5, 0.45), False), "hscp_300": ((0.0, 0.5, 0.0), True), "monojet_300": ((0.5, 0.5, 0.5), True)}
out, rows = {}, []
for panel, f in (("colored", "colored_limits.pdf"), ("EW", "DY_limits.pdf")):
    page = fitz.open(f"{FIG}/{f}")[0]; to_val, cal = calib(page); dr = page.get_drawings(); cur = {}
    cl = lambda c: tuple(round(v, 2) for v in (c or ()))
    for name, (rgb, dashed) in RGB.items():
        c = [d for d in dr if cl(d.get("color")) == rgb and d.get("fill") is None and len(d["items"]) > 5 and (("[]" not in str(d.get("dashes"))) == dashed)]
        c = max(c, key=lambda d: len(d["items"])); cur[name] = to_val(pts(c))
    for name, rgb in (("hscp_12.9_boundary", (0.0, 0.5, 0.0)), ("monojet_12.9_boundary", (0.5, 0.5, 0.5))):   # solid outline of the shaded 12.9 fb-1 regions
        c = [d for d in dr if cl(d.get("color")) == rgb and d.get("fill") is None and "[]" in str(d.get("dashes")) and len(d["items"]) > 5]
        cur[name] = to_val(pts(max(c, key=lambda d: len(d["items"]))))
    dcm = [d for d in dr if cl(d.get("color")) == (0.27, 0.51, 0.71)]
    dcm = sorted(dcm, key=lambda d: float(np.mean(pts(d)[:, 1])))                      # top (small d_cm) first
    for lab, d in zip(("dcm_100um", "dcm_1mm", "dcm_1cm", "dcm_1m", "dcm_100m"), dcm): cur[lab] = to_val(pts(d))
    out[panel] = dict(calibration=cal, curves={k: dict(m_GeV=list(map(float, v[0])), lambda_eV=list(map(float, v[1]))) for k, v in cur.items()})
    for k, (x, y) in cur.items(): rows += [dict(panel=panel, curve=k, point=i, m_GeV=a, lambda_eV=b) for i, (a, b) in enumerate(zip(x, y))]
    print(panel, "1000 eV at page y", round(cal["y_page_at_1000eV"], 2), "-> linear piece gives", round(cal["linear_fit_value_at_that_y"], 1), "eV")
    for k, (x, y) in cur.items(): print(f"   {k:18s} n={len(x):3d}  m {x.min():7.1f}-{x.max():7.1f} GeV  Lambda {y.min():8.1f}-{y.max():8.1f} eV")
json.dump(out, open(f"{T}/paper_fig6_vector.json", "w"), indent=1); pd.DataFrame(rows).to_csv(f"{T}/paper_fig6_curves.csv", index=False)
