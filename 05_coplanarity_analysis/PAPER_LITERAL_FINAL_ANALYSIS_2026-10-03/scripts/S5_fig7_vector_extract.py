#!/usr/bin/env python3
"""Paper Fig. 7 (arXiv:1708.02243v2 Appendix A, figures/dEdx.pdf and figures/betagamma.pdf) -> step histograms from the vector paths.
dEdx: x linear (ticks 0..100, MeV cm^2/g), y log (ticks 1e-3..1e-1); betagamma: x log (1e-4..1e1), y log (1e-4..1e0). Calibration from the tick labels
(centre of each label -> nearest tick mark). Colours: the legend line next to each label gives the sample (EW 800 GeV / colored 1800 GeV, both Lambda = 2 keV).
Output: tables/paper_fig7_vector.json, tables/paper_fig7_curves.csv (x, y of each step-path vertex)."""
import os, json, numpy as np, pandas as pd, fitz
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"; FIG = f"{HERE}/../paper_source_arXiv_1708.02243/v2_Nov2017/figures"
def pts(d):
    out = []
    for it in d["items"]:
        if it[0] == "l": out += [it[1], it[2]]
        elif it[0] == "c": out += [it[1], it[4]]
    xy = []
    for p in out:
        if not xy or abs(p.x - xy[-1][0]) > 1e-6 or abs(p.y - xy[-1][1]) > 1e-6: xy.append((p.x, p.y))
    return np.array(xy)
def num(t):
    t = t.replace("−", "-")
    if t.startswith("10") and len(t) > 2: return 10.0 ** float(t[2:])
    return float(t)
out, rows = {}, []
for name, f, xlog in (("dEdx", "dEdx.pdf", False), ("betagamma", "betagamma.pdf", True)):
    page = fitz.open(f"{FIG}/{f}")[0]; words = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = "".join(s["text"] for s in l["spans"]).strip(); words.append((t, l["bbox"]))
    ticks = [pts(d) for d in page.get_drawings() if d.get("color") == (0.0, 0.0, 0.0) and len(d["items"]) == 1 and d["items"][0][0] == "l"]
    ticks = [t for t in ticks if len(t) == 2]
    xt = [t[0, 0] for t in ticks if abs(t[0, 0] - t[1, 0]) < 1e-3]; yt = [t[0, 1] for t in ticks if abs(t[0, 1] - t[1, 1]) < 1e-3]
    xs, ys = [], []
    for t, bb in words:
        try: v = num(t)
        except ValueError: continue
        if bb[1] > 400: xs.append((v, min(xt, key=lambda q: abs(q - (bb[0] + bb[2]) / 2))))
        elif bb[0] < 112: ys.append((v, min(yt, key=lambda q: abs(q - (bb[1] + bb[3]) / 2))))
    ax = np.polyfit([p for _, p in xs], [np.log10(v) if xlog else v for v, _ in xs], 1); ay = np.polyfit([p for _, p in ys], [np.log10(v) for v, _ in ys], 1)
    conv = lambda a: ((10 ** np.polyval(ax, a[:, 0])) if xlog else np.polyval(ax, a[:, 0]), 10 ** np.polyval(ay, a[:, 1]))
    dr = page.get_drawings(); cl = lambda c: tuple(round(v, 2) for v in (c or ()))
    leg = {t: bb for t, bb in words if t.startswith("mQ")}
    curves = {}
    for rgb in ((0.98, 0.5, 0.45), (0.5, 0.0, 0.5)):
        cs = [d for d in dr if cl(d.get("color")) == rgb]
        big = max(cs, key=lambda d: len(d["items"])); small = min(cs, key=lambda d: len(d["items"]))   # histogram and its legend line
        ly = (small["rect"].y0 + small["rect"].y1) / 2; lab = min(leg, key=lambda t: abs((leg[t][1] + leg[t][3]) / 2 - ly))
        key = "EW_800GeV_2keV" if "EW" in lab else "colored_1800GeV_2keV"; x, y = conv(pts(big)); curves[key] = dict(x=list(map(float, x)), y=list(map(float, y)), rgb=rgb)
        rows += [dict(panel=name, sample=key, point=i, x=a, y=b) for i, (a, b) in enumerate(zip(x, y))]
    out[name] = dict(x_ticks=xs, y_ticks=ys, curves=curves)
    for k, c in curves.items(): print(f"{name:10s} {k:22s} n={len(c['x']):3d} x {min(c['x']):.3g}-{max(c['x']):.3g} y {min(c['y']):.3g}-{max(c['y']):.3g}")
json.dump(out, open(f"{T}/paper_fig7_vector.json", "w"), indent=1); pd.DataFrame(rows).to_csv(f"{T}/paper_fig7_curves.csv", index=False)
