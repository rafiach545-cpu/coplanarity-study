#!/usr/bin/env python3
"""Fig. 4 (paper style) for the two SCT z settings of the report: 1.16 mm (paper text: twice the 580 um of Ref. [27]) and no smearing.
Fixed selection rule (no hand-picking): for COL2000 and EW2000, among events passing the full signal region with one hit per quirk per layer
(first crossing), Ref. [27] lengths, the event with the median Delta_s. Hits rebuilt with the P18 code path; the rebuilt Delta_s must equal
tables/all_crossings_per_event.csv. Left: all hits in the plane's (n3, n2) coordinates with the layers drawn as ellipses (as in the paper);
right: zoom |n2| < 1 cm with the +-Delta_w band (Delta_w = sqrt(lambda_2), Eq. 11). Output: FINAL_FIGURES/F29_fig4_<setting>/"""
import os, sys, math, importlib.util, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; S = os.path.abspath(__file__)
spec = importlib.util.spec_from_file_location("p18", f"{HERE}/P18_all_crossings.py"); p18 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p18)
p4 = p18.p4; p4._init()
A = pd.read_csv(f"{T}/all_crossings_per_event.csv"); TR = lambda s: s.astype(str) == "True"
def build(s, sct):
    x = A[(A["sample"] == s) & (A["mode"] == "FIRST") & (A.sct == sct) & TR(A.fid) & TR(A.final)].sort_values("ds").reset_index(drop=True)
    r = x.iloc[len(x) // 2]; key = int(r.key)
    ev = p4.fp.load_sample(s).set_index("key").loc[key]; cr0 = pd.read_csv(f"{p4.FOR}/tables/truth_crossings_{s}.csv").query("key == @key").sort_values(["quirk", "layer"])
    ex = pd.read_csv(f"{T}/signal_exact_crossings_all_trigger_events.csv").query("sample == @s and key == @key").sort_values(["quirk", "layer"])
    z0, g = p4.fp.stream_draws(np.random.default_rng(int(ev.seed)), cr0, ex.copy()); m = p4.momenta(s).iloc[key]; mq, lam = p4.PAR["EW" if s.startswith("EW") else "COL"]
    _, traj = p4.tth.simulate_quirk_hits((m.px1, m.py1, m.pz1, m.E1), (m.px2, m.py2, m.pz2, m.E2), mass_gev=mq, Lambda_gev=lam, B_tesla=2.0, charge1=float(m.charge1), charge2=float(m.charge2),
                                         rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
    tth, cf = p4.tth, p4.cf; raw = []
    for c in p18.all_crossings(traj):
        if c["order"] > 0 or c["t_ns"] >= 25.0 or abs(c["z_lab"]) >= p4.HALF[c["layer"]]: continue
        lay = tth.LAYERS[c["layer"] - 1]; rphi = lay["r_cm"] * math.atan2(c["y"], c["x"])
        if lay["is_pixel"]: rh, zh, ir, iz = tth.quantize_pixel(rphi, c["z_lab"], lay["eff_res_rphi_um"], lay["eff_res_z_um"])
        else:
            g1, g2 = g[(c["quirk"], c["layer"])]; rh, zh, ir, iz = rphi + 34e-4 * g1, c["z_lab"] + p4.SZ[sct] * g2, None, None
        ph = rh / lay["r_cm"]; raw.append(dict(layer=lay["name"], layer_r_cm=lay["r_cm"], quirk_index=c["quirk"], t_ns=c["t_ns"], x=lay["r_cm"] * math.cos(ph), y=lay["r_cm"] * math.sin(ph), z=zh,
                                               is_pixel=lay["is_pixel"], idx_rphi=ir, idx_z=iz))
    idx = {Ly["name"]: i for i, Ly in enumerate(tth.LAYERS, 1)}; hbl = {k: [] for k in range(1, 9)}
    for h in tth.merge_neighboring_pixel_hits(raw): hbl[idx[h["layer"]]].append(tuple(cf.vertex_relative_hits([(h["x"], h["y"], h["z"])], np.array([0.0, 0.0, z0]))[0]))
    sel = min([c for c in cf.seeding_and_iterative_fit(hbl) if c["fit"]["delta_w"] < 1.0], key=lambda c: c["fit"]["delta_s"])
    assert abs(sel["fit"]["delta_s"] - r.ds) < 1e-9, (s, sct, sel["fit"]["delta_s"], r.ds)
    n1, n2, n3 = (np.array(sel["fit"][k]) for k in ("n1", "n2", "n3")); rows = []
    for L, pts in hbl.items():
        for p in pts:
            p = np.array(p); rows.append(dict(sample=s, sct=sct, key=key, event_id=int(r.event_id), layer=L, n2_cm=p @ n2, n3_cm=p @ n3, ds_cm=sel["fit"]["delta_s"], dw_cm=sel["fit"]["delta_w"],
                                              n_sr_events=len(x), rank=len(x) // 2 + 1, ellipse=False))
    for L, lay in enumerate(tth.LAYERS, 1):
        for t_ in np.linspace(0, 2 * np.pi, 400):
            dv = math.cos(t_) * n3 + math.sin(t_) * n2; tr = math.hypot(dv[0], dv[1])
            if tr < 1e-9: continue
            q = dv * lay["r_cm"] / tr
            if q @ n3 > 0: rows.append(dict(sample=s, sct=sct, key=key, layer=L, ellipse=True, n2_cm=q @ n2, n3_cm=q @ n3))
    return pd.DataFrame(rows)
LAB = {"Z1160": "SCT z 1.16 mm", "Z0": "no SCT z smearing"}
for sct in ("Z1160", "Z0"):
    src = pd.concat([build("COL2000", sct), build("EW2000", sct)])
    def plot(d, sct=sct):
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(2, 2, figsize=(11, 7.2), gridspec_kw=dict(width_ratios=[1.25, 1]))
        for i, s in enumerate(["COL2000", "EW2000"]):
            g = d[(d["sample"] == s) & (d.ellipse != True)]; e = d[(d["sample"] == s) & (d.ellipse == True)]; dw, ds = g.dw_cm.iloc[0], g.ds_cm.iloc[0]; col = fu.SERIES[1] if s.startswith("EW") else fu.SERIES[0]
            ax = axes[i, 0]
            for L, ee in e.groupby("layer"): ax.plot(ee.n3_cm, ee.n2_cm, ".", ms=0.6, color=fu.MUTED)
            ax.scatter(g.n3_cm, g.n2_cm, marker="x", s=30, color=col, zorder=3)
            ax.set_xlabel("n₃ (cm)"); ax.set_ylabel("n₂ (cm)"); ax.set_xlim(-20, 80); ax.set_ylim(-30, 25); ax.set_aspect("equal")
            lab = "colored 1.8 TeV, Λ = 2 keV" if s == "COL2000" else "EW 800 GeV, Λ = 4 keV"
            ax.set_title(f"{lab}: event {int(g.event_id.iloc[0])} (median Δs, {int(g['rank'].iloc[0])} of {int(g.n_sr_events.iloc[0])})", fontsize=8.5)
            bx = axes[i, 1]; bx.axhspan(-dw, dw, color=fu.SERIES[2], alpha=0.18, lw=0, label=f"±Δw = ±{dw:.3f} cm")
            bx.scatter(g.n3_cm, g.n2_cm, marker="x", s=36, color=col, label=f"hits, Δs = {ds*1e4:.0f} µm")
            bx.set_ylim(-1, 1); bx.set_xlim(0, 80); bx.set_xlabel("n₃ (cm)"); bx.set_ylabel("n₂ (cm)"); bx.set_title("zoom, |n₂| < 1 cm", fontsize=9); bx.legend(fontsize=7, loc="upper left")
        fig.suptitle(LAB[sct], fontsize=10); fig.tight_layout(); return fig
    fu.figure(f"F29_fig4_{sct}", src, plot, f"Figure 4 style, {LAB[sct]}. Selection rule: for COL2000 and EW2000, the event with the median Δs among events passing the full signal region "
              "(one hit per quirk per layer, Ref. [27] lengths). Left: all hits in the plane's (n₃, n₂) coordinates, layers as ellipses (grey). Right: zoom with the ±Δw band (Δw = √λ₂, Eq. 11).",
              [f"{T}/all_crossings_per_event.csv"], "median Delta_s among signal-region events", S)
    print(sct, src[src.ellipse != True].groupby("sample")[["event_id", "ds_cm", "dw_cm", "n_sr_events", "rank"]].first().to_string())
