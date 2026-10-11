#!/usr/bin/env python3
"""
Figure 4-style event displays for ONE real EW event and ONE real colored event (literal configuration).
Selection: the first EW2000 / COL2000 trigger event (by key) that passes the full literal Sec. IV signal region;
if none passes, the first literal-fiducial event with a reconstructed plane (stated in the caption).
Hits are rebuilt exactly as in P4 (stored exact crossings, stored z0, the project's own SCT random draws), then
projected on the selected plane's (n3, n2) axes. Inset: zoom of n2 within +-1 cm; band = +-Delta_w (Eq. 11, sqrt(l2)).
"""
import importlib.util, os, sys, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu                                          # noqa: E402
spec = importlib.util.spec_from_file_location("p4", f"{HERE}/P4_literal_signal.py"); p4 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p4)
p4._init()
T = f"{HERE}/../tables"
FOR = p4.FOR


def build(sample):
    d = pd.read_csv(f"{T}/signal_per_event_all_configs.csv")
    x = d[(d["sample"] == sample) & (d.geom == "B") & (d.sct == "Z1160") & (d.wconv == "W1") & (d.fid == True)].sort_values("key")
    pick = x[x.final == True]
    why = "first event passing the full literal Sec. IV signal region"
    if len(pick) == 0:
        pick = x[x.plane == True]; why = "no event passes the literal SR; first literal-fiducial event with a plane"
    r = pick.iloc[0]; key = int(r.key)
    ev = p4.fp.load_sample(sample).set_index("key").loc[key]
    cr0 = pd.read_csv(f"{FOR}/tables/truth_crossings_{sample}.csv").query("key == @key").sort_values(["quirk", "layer"])
    ex = pd.read_csv(f"{T}/signal_exact_crossings_all_trigger_events.csv").query("sample == @sample and key == @key").sort_values(["quirk", "layer"])
    z0, g = p4.fp.stream_draws(np.random.default_rng(int(ev.seed)), cr0, ex)
    cr = ex.to_dict("records")
    import math
    tth, cf = p4.tth, p4.cf
    raw = []
    for c in cr:
        if abs(c["z_lab"]) >= p4.HALF[c["layer"]]:
            continue
        lay = tth.LAYERS[c["layer"] - 1]; rphi = lay["r_cm"] * math.atan2(c["y"], c["x"])
        if lay["is_pixel"]:
            rh, zh, ir, iz = tth.quantize_pixel(rphi, c["z_lab"], lay["eff_res_rphi_um"], lay["eff_res_z_um"])
        else:
            g1, g2 = g[(c["quirk"], c["layer"])]; rh, zh, ir, iz = rphi + 34e-4 * g1, c["z_lab"] + 0.116 * g2, None, None
        ph = rh / lay["r_cm"]
        raw.append(dict(layer=lay["name"], layer_r_cm=lay["r_cm"], quirk_index=c["quirk"], t_ns=c["t_ns"], x=lay["r_cm"] * math.cos(ph),
                        y=lay["r_cm"] * math.sin(ph), z=zh, is_pixel=lay["is_pixel"], idx_rphi=ir, idx_z=iz))
    merged = tth.merge_neighboring_pixel_hits(raw)
    idx = {Ly["name"]: i for i, Ly in enumerate(tth.LAYERS, 1)}
    hbl = {k: [] for k in range(1, 9)}
    for h in merged:
        hbl[idx[h["layer"]]].append((h["x"], h["y"], h["z"] - z0))
    cands = cf.seeding_and_iterative_fit(hbl); sel = cf.select_reconstructed_plane(cands)
    assert abs(sel["fit"]["delta_s"] - r.ds) < 1e-12, "display rebuild does not match the P4 literal result"
    n1, n2, n3 = sel["fit"]["n1"], sel["fit"]["n2"], sel["fit"]["n3"]
    sset = {tuple(np.round(h, 10)) for h in sel["hits"]}
    rows = []
    for L, pts in hbl.items():
        for p in pts:
            p = np.array(p)
            rows.append(dict(sample=sample, event_id=int(r.event_id), layer=L, n1_cm=p @ n1, n2_cm=p @ n2, n3_cm=p @ n3,
                             in_selected_plane=tuple(np.round(p, 10)) in sset, delta_s_cm=sel["fit"]["delta_s"],
                             delta_w_cm=sel["fit"]["delta_w"], selection=why, final_sec_iv=bool(r.final)))
    return pd.DataFrame(rows)


def main():
    import matplotlib.pyplot as plt
    src = pd.concat([build("COL2000"), build("EW2000")])

    def plot(df):
        fig, axes = plt.subplots(2, 1, figsize=(6.4, 7.6))
        for ax, (smp, g) in zip(axes, df.groupby("sample", sort=False)):
            dw, ds = g.delta_w_cm.iloc[0], g.delta_s_cm.iloc[0]
            ax.axhspan(-dw, dw, color=fu.SERIES[1], alpha=0.25, lw=0, label="±Δw (Eq. 11)")
            ax.scatter(g.n3_cm, g.n2_cm, marker="x", s=36, color=fu.INK2, label="hits (selected plane)")
            ax.set_xlabel("n₃ (cm)"); ax.set_ylabel("n₂ (cm)"); ax.set_ylim(-1.0, 1.0)
            lab = "colored 1800 GeV, Λ = 2 keV" if smp.startswith("COL") else "EW 800 GeV, Λ = 4 keV"
            ax.set_title(f"{lab} — {smp} event {g.event_id.iloc[0]}  (Δw = {dw:.3f} cm, Δs = {ds*1e4:.0f} µm, SR pass = {g.final_sec_iv.iloc[0]})", fontsize=8)
            ax.legend(fontsize=7, loc="upper right")
        fig.tight_layout(); return fig

    fu.figure("F04_signal_event_displays", src, plot,
              "Figure 4-style displays of ONE real colored event (COL2000) and ONE real EW event (EW2000) in the literal configuration "
              "(finite barrel, SCT 34/1160 µm, literal Sec. III C algorithm). Hits rebuilt exactly from stored crossings, vertex and the project's "
              "own SCT random draws, projected on the selected plane's (n₃, n₂) axes; band = ±Δw with Δw = sqrt(λ₂) (paper Eq. 11). Note: the "
              "paper's own Fig. 4 band corresponds to 0.5·sqrt(λ₂) (see UNRESOLVED_DIFFERENCES.md). The selection rule is stated per panel in the source CSV.",
              [f"{T}/signal_per_event_all_configs.csv", f"{T}/signal_exact_crossings_all_trigger_events.csv"],
              "first literal SR-passing event (else first literal-fiducial event with a plane) in COL2000 and EW2000", os.path.abspath(__file__))
    print(src.groupby("sample")[["event_id", "delta_s_cm", "delta_w_cm", "final_sec_iv"]].first(), src.selection.unique())


if __name__ == "__main__":
    main()
