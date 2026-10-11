#!/usr/bin/env python3
"""
Shared figure helpers (Phase 11).

Every figure lives in FINAL_FIGURES/<name>/ with:
  <name>.png / .pdf / .svg, <name>_source.csv (the ONLY data the plot reads), caption.md,
  provenance.json (source paths + SHA-256, selection criteria, script SHA-256), and a copy of the plotting script.
Workflow enforced by `figure(...)`: build the source table -> write CSV -> re-read CSV -> plot from the re-read copy.
Palette: reference instance of the dataviz skill (fixed categorical order; light surface). The skill's palette
validator (node) is not installed on this machine -> not run; every series also carries a line-style/marker
(secondary encoding) so identity never depends on colour alone.
"""
import hashlib, json, os, shutil, inspect
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "FINAL_FIGURES")
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
STYLES = ["-", "--", "-.", ":", (0, (5, 1)), (0, (3, 1, 1, 1)), (0, (1, 1)), (0, (5, 5))]
MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*"]
INK, INK2, MUTED, SURFACE = "#0b0b0b", "#52514e", "#898781", "#fcfcfb"
plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                     "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "font.size": 10, "legend.frameon": False, "lines.linewidth": 2})


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def figure(name, source_df, plot_fn, caption, sources, selection, script_path):
    d = os.path.join(ROOT, name); os.makedirs(d, exist_ok=True)
    csv = os.path.join(d, f"{name}_source.csv")
    source_df.to_csv(csv, index=False)
    data = pd.read_csv(csv)                               # the plot reads ONLY the written source CSV
    fig = plot_fn(data)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(os.path.join(d, f"{name}.{ext}"), dpi=200 if ext == "png" else None, bbox_inches="tight")
    plt.close(fig)
    open(os.path.join(d, "caption.md"), "w").write(caption.strip() + "\n")
    shutil.copy(script_path, os.path.join(d, os.path.basename(script_path)))
    prov = dict(figure=name, source_csv=os.path.basename(csv), source_csv_sha256=sha(csv),
                plot_reads_only_source_csv=True, selection=selection,
                upstream_sources={p: (sha(p) if os.path.isfile(p) else "directory/not-a-file") for p in sources},
                script=os.path.basename(script_path), script_sha256=sha(script_path),
                palette="dataviz reference palette (fixed order); validator not run (node unavailable); secondary encoding used")
    json.dump(prov, open(os.path.join(d, "provenance.json"), "w"), indent=1)
    return d
