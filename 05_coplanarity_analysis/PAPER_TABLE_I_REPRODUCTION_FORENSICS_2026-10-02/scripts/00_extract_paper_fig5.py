#!/usr/bin/env python3
"""
Extract the signal histograms of the paper's Fig. 5 (arXiv:1708.02243v2 source,
figures/Deltat.pdf and figures/Deltaw.pdf) directly from the vector paths.

Axis calibration uses the tick labels printed in the PDF itself (text positions of
'10^-3', '10^-2', '10^-1' on x; '10^-4'...'10^0' on y), so no manual digitisation.
Each coloured step path (width 3.0) is one histogram. Bin edges and heights are
recovered from the path vertices.
"""
import json
import math
import os
import re
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = f"{HERE}/../paper_figures"
COLORS = {(0.5, 0.0, 0.5): "Colored Quirk", (1.0, 0.0, 0.0): "EW Quirk",
          (0.0, 0.5, 0.0): "Pileup", (0.0, 0.0, 1.0): "Converted gamma"}


def ticks(page):
    """Return x-tick and y-tick (value, coordinate) pairs from tick-label text."""
    words = page.get_text("dict")
    xs, ys = [], []
    for b in words["blocks"]:
        for l in b.get("lines", []):
            txt = "".join(s["text"] for s in l["spans"]).replace("−", "-")
            m = re.fullmatch(r"10(-?\d)", txt.replace(" ", ""))
            if not m:
                continue
            e = int(m.group(1))
            x0, y0, x1, y1 = l["bbox"]
            xs.append((e, (x0 + x1) / 2, y0, y1))
    return xs


def main():
    out = {}
    for fname, var in (("Deltat.pdf", "delta_s_cm"), ("Deltaw.pdf", "delta_w_cm")):
        page = fitz.open(f"{FIG}/{fname}")[0]
        labels = ticks(page)
        # x-axis labels lie lowest on the page (largest y); y-axis labels are left-most
        ymax = max(t[3] for t in labels)
        xlab = sorted([t for t in labels if abs(t[3] - ymax) < 5], key=lambda t: t[1])
        ylab = [t for t in labels if t not in xlab]
        ylab = sorted(ylab, key=lambda t: -(t[2] + t[3]) / 2)
        # linear fit log10(value) vs coordinate
        def fit(pairs):
            n = len(pairs)
            mx = sum(p for p, _ in pairs) / n
            my = sum(v for _, v in pairs) / n
            sxx = sum((p - mx) ** 2 for p, _ in pairs)
            sxy = sum((p - mx) * (v - my) for p, v in pairs)
            a = sxy / sxx
            return lambda c: a * (c - mx) + my
        fx = fit([(t[1], t[0]) for t in xlab])
        fy = fit([((t[2] + t[3]) / 2, t[0]) for t in ylab])
        hists = {}
        for dr in page.get_drawings():
            col = tuple(round(c, 2) for c in (dr.get("color") or ()))
            if col not in COLORS or not dr.get("width") or dr["width"] < 2.9 or len(dr["items"]) < 5:
                continue
            pts = []
            for it in dr["items"]:
                if it[0] == "l":
                    pts += [it[1], it[2]]
            # step path: horizontal segments give bins
            bins = []
            for it in dr["items"]:
                if it[0] != "l":
                    continue
                p, q = it[1], it[2]
                if abs(p.y - q.y) < 1e-6 and abs(p.x - q.x) > 1e-3:
                    lo, hi = sorted([p.x, q.x])
                    bins.append(dict(lo=10 ** fx(lo), hi=10 ** fx(hi), height=10 ** fy(p.y), y_pt=p.y))
            hists[COLORS[col]] = sorted(bins, key=lambda b: b["lo"])
        out[var] = dict(x_ticks=[(t[0], t[1]) for t in xlab], y_ticks=[(t[0], (t[2] + t[3]) / 2) for t in ylab],
                        histograms=hists, plot_rect=[page.rect.x0, page.rect.y0, page.rect.x1, page.rect.y1])
    json.dump(out, open(f"{HERE}/../tables/paper_fig5_extracted.json", "w"), indent=1)
    for var, d in out.items():
        print("==", var, "xticks", [(e, round(c, 1)) for e, c in d["x_ticks"]], "yticks", [(e, round(c, 1)) for e, c in d["y_ticks"]])
        for name in ("EW Quirk", "Colored Quirk"):
            h = d["histograms"].get(name, [])
            tot = sum(b["height"] for b in h)
            cut = 0.01 if var == "delta_s_cm" else 1.0
            below = sum(b["height"] for b in h if b["hi"] <= cut * 1.0001)
            med_acc, med = 0, None
            for b in h:
                med_acc += b["height"]
                if med is None and med_acc >= tot / 2:
                    med = math.sqrt(b["lo"] * b["hi"])
            print(f"  {name}: {len(h)} bins, sum={tot:.4e} fb, frac(<{cut})={below / tot:.3f}, median bin centre={med:.4g}")
            print("   ", [(f"{b['lo']:.3g}-{b['hi']:.3g}", f"{b['height']:.3g}") for b in h])


if __name__ == "__main__":
    main()
