#!/usr/bin/env python3
"""Figure 4-style displays of background events, rebuilt through the EXACT production code paths
(P9_literal_conversion.literal_event / P10_literal_overlay.event, with the analysis function wrapped to capture hits;
each rebuild is asserted to reproduce the stored Delta_s / decision).
Selection rules (stated, deterministic, applied to the stored literal tables):
  (a) conversion only, LITERAL : final Sec. IV event if any; else among literal planes the one with the most winner
      hits, ties -> smallest Delta_s.
  (b) conversion only, SYS_Z0 (calibrated, NOT literal; diagnostic): first SYS_Z0 event passing Sec. IV.
  (c) conversion + pile-up, LITERAL : final event if any; else plane+multiplicity event if any; else the literal plane
      with the most conversion-origin winner hits, ties -> smallest Delta_s.
Panels: transverse x-y view (all hits; conversion e+- hits coloured; selected-plane hits ringed) and the selected
plane's (n3, n2) view (|n2| < 2 cm)."""
import os, sys, glob, importlib.util, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
def load(n):
    s = importlib.util.spec_from_file_location(n, f"{HERE}/{n}.py"); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
TR = lambda s: s.astype(str) == "True"
LOG = f"{HERE}/../logs"


def capture_p9(i, config):
    p9 = load("P9_literal_conversion"); p9._init(); cap = {}
    orig = p9.analyse; names = iter(p9.CONFIGS)
    def wrap(hits, origin):
        nm = next(names); r = orig(hits, origin)
        if nm == config: cap.update(hits=hits, origin=origin, res=r)
        return r
    p9.analyse = wrap; p9.literal_event(i)
    # recompute the selected plane for the display (same functions as analyse)
    o = cap["origin"]; hbl = {k: [] for k in range(1, 9)}; src = {}
    for h in cap["hits"]:
        pt = (h["x"] - o[0], h["y"] - o[1], h["z"] - o[2]); hbl[p9.IDX[h["layer"]]].append(pt); src[pt] = {"0": "conv e⁻", "1": "conv e⁺"}.get(str(h["quirk_index"]), "conv e⁺e⁻ merged pixel hit")
    w = p9.select_reconstructed_plane(p9.seeding_and_iterative_fit(hbl))
    return cap["res"], w, src


def capture_p10(i):
    p10 = load("P10_literal_overlay"); p10._init(); cap = {}
    orig = p10.reco
    def wrap(merged, origin):
        r = orig(merged, origin)
        if "res" not in cap: cap.update(merged=merged, origin=origin, res=r[0], w=r[1][0])
        return r
    p10.reco = wrap; p10.event(i)
    o = cap["origin"]; src = {}
    for h in cap["merged"]:
        s = [str(x) for x in h.get("source_quirk_indices", [h["quirk_index"]])]
        src[(h["x"] - o[0], h["y"] - o[1], h["z"] - o[2])] = "mixed" if (any(x.startswith("conv") for x in s) and any(x.startswith("pu") for x in s)) else ("conv" if any(x.startswith("conv") for x in s) else "pile-up")
    return cap["res"], cap["w"], src


def rows(tag, ev, res, w, src, why):
    win = {tuple(np.round(p, 10)) for p in w["hits"]} if w else set()
    n1, n2, n3 = (np.array(w["fit"][k]) for k in ("n1", "n2", "n3")) if w else (np.zeros(3),) * 3
    out = []
    for pt, s in src.items():
        p = np.array(pt)
        out.append(dict(panel=tag, event=ev, x_cm=p[0], y_cm=p[1], z_rel_cm=p[2], origin=s, in_selected_plane=tuple(np.round(p, 10)) in win,
                        n1_cm=p @ n1, n2_cm=p @ n2, n3_cm=p @ n3, ds_cm=res["ds"], dw_cm=res["dw"], plane=res["plane"], mult=res["mult"], final=res["final"], selection=why))
    return out


def main():
    cv = pd.concat(pd.read_csv(f) for f in sorted(glob.glob(f"{LOG}/P9_chunks_LITERAL/chunk_*.csv")))
    for c in ("plane", "mult", "final"): cv[c] = TR(cv[c])
    lc = cv[(cv.config == "LITERAL") & cv.plane].copy(); lc["nw"] = lc.winner_layers.str.count(r"\d+")
    if lc.final.any(): a = lc[lc.final].iloc[0]; whya = "literal conversion-only event passing Sec. IV"
    else: a = lc.sort_values(["nw", "ds"], ascending=[False, True]).iloc[0]; whya = "no literal conversion-only event passes Sec. IV; literal plane with most winner hits (ties: smallest Δs)"
    b = cv[(cv.config == "SYS_Z0") & cv.final].sort_values("event").iloc[0]; whyb = "first SYS_Z0 (calibrated, NOT literal) conversion-only event passing Sec. IV"
    ov = pd.concat(pd.read_csv(f) for f in sorted(glob.glob(f"{LOG}/P10_chunks_LITERAL/chunk_*.csv")))
    for c in ("plane", "mult", "final"): ov[c] = TR(ov[c])
    lo = ov[(ov.config == "LITERAL") & ov.plane]
    if lo.final.any(): c_ = lo[lo.final].sort_values("event").iloc[0]; whyc = "literal overlay event passing Sec. IV"
    elif lo.mult.any(): c_ = lo[lo.mult].sort_values("ds").iloc[0]; whyc = "no literal overlay final event; plane+multiplicity event with smallest Δs"
    else: c_ = lo.sort_values(["winner_conv_hits", "ds"], ascending=[False, True]).iloc[0]; whyc = "no literal overlay final/multiplicity event; plane with most conversion-origin winner hits (ties: smallest Δs)"
    whyc += f" [{ov.event.nunique()} of 9139 overlay events processed]"
    out = []
    for tag, ev, cfg, why in [("conversion only — LITERAL", int(a.event), "LITERAL", whya), ("conversion only — SYS_Z0 (calibrated)", int(b.event), "SYS_Z0", whyb)]:
        res, w, src = capture_p9(ev, cfg); ref = cv[(cv.config == cfg) & (cv.event == ev)].iloc[0]
        assert abs(res["ds"] - ref.ds) < 1e-12 and res["final"] == ref.final, (tag, ev)
        out += rows(tag, ev, res, w, src, why)
    res, w, src = capture_p10(int(c_.event)); assert abs(res["ds"] - c_.ds) < 1e-12 and res["final"] == c_.final
    out += rows("conversion + pile-up (μ=50) — LITERAL", int(c_.event), res, w, src, whyc)
    df = pd.DataFrame(out)

    def plot(d):
        import matplotlib.pyplot as plt
        tags = list(dict.fromkeys(d.panel)); fig, axes = plt.subplots(len(tags), 2, figsize=(10, 4.2 * len(tags)))
        col = {"conv e⁻": fu.SERIES[0], "conv e⁺": fu.SERIES[1], "conv e⁺e⁻ merged pixel hit": fu.SERIES[6], "conv": fu.SERIES[0], "mixed": fu.SERIES[4], "pile-up": "#c9c8c2"}
        RADII = [3.325, 5.05, 8.85, 12.25, 29.9, 37.1, 44.3, 51.4]
        for k, t in enumerate(tags):
            g = d[d.panel == t]; ax, bx = axes[k]
            for o, gg in g.groupby("origin"):
                ax.scatter(gg.x_cm, gg.y_cm, s=2 if o == "pile-up" else 14, color=col.get(o, fu.INK2), label=o, zorder=1 if o == "pile-up" else 3, lw=0)
            sp = g[g.in_selected_plane]
            ax.scatter(sp.x_cm, sp.y_cm, s=60, facecolors="none", edgecolors=fu.INK, lw=1, label="selected plane hits", zorder=4)
            for rr in RADII: ax.add_patch(plt.Circle((0, 0), rr, fill=False, color="#e6e5e0", lw=0.6, zorder=0))
            ax.set_xlim(-56, 56); ax.set_ylim(-56, 56)
            ax.set_aspect("equal"); ax.set_xlabel("x (cm)"); ax.set_ylabel("y (cm)"); ax.legend(fontsize=6, loc="upper left", markerscale=1.5)
            ax.set_title(f"{t}: event {g.event.iloc[0]} (transverse view)", fontsize=8)
            near = g[(g.n2_cm.abs() < 2) & g.plane]
            for o, gg in near.groupby("origin"):
                bx.scatter(gg.n3_cm, gg.n2_cm, s=4 if o == "pile-up" else 18, marker="x" if o != "pile-up" else ".", color=col.get(o, fu.INK2), label=o)
            if g.plane.iloc[0]:
                bx.axhspan(-g.dw_cm.iloc[0], g.dw_cm.iloc[0], color=fu.SERIES[2], alpha=0.15, lw=0, label="±Δw (√λ₂)")
            bx.set_ylim(-2, 2); bx.set_xlabel("n₃ (cm)"); bx.set_ylabel("n₂ (cm)"); bx.legend(fontsize=6, loc="upper right")
            bx.set_title(f"plane view: Δs = {g.ds_cm.iloc[0]*1e4:.0f} µm, Δw = {g.dw_cm.iloc[0]:.3f} cm, mult = {g.mult.iloc[0]}, SR = {g.final.iloc[0]}", fontsize=8)
        fig.tight_layout(); return fig
    fu.figure("F10_background_event_displays", df, plot,
              "Figure 4-style displays of background events rebuilt through the exact production code paths (rebuild asserted to reproduce the "
              "stored Δs and decision). Rows: (a) converted photon, LITERAL; (b) converted photon, SYS_Z0 (SCT z not smeared — calibrated, NOT "
              "literal), one of the 22 events that pass the signal region only in that setting; (c) converted photon + μ=50 pile-up, LITERAL. "
              "Selection rules are stated per row in the source CSV ('selection' column). Left: transverse view (barrel layer radii drawn), conversion e± hits coloured (pixel hits shared by e⁺ and e⁻ after neighbouring-pixel merging in purple), "
              "pile-up grey, selected-plane hits ringed. Right: selected plane's (n₃, n₂) coordinates, |n₂| < 2 cm.",
              [f"{LOG}/P9_chunks_LITERAL", f"{LOG}/P10_chunks_LITERAL"], "see selection column", os.path.abspath(__file__))
    print(df.groupby("panel")[["event", "ds_cm", "dw_cm", "mult", "final", "selection"]].first().to_string())


if __name__ == "__main__":
    main()
