#!/usr/bin/env python3
"""Fig. 4 (paper style) with a fixed, non-cherry-picked selection: for COL2000 and EW2000, among events that pass the full
signal region in the current primary setup (Ref. [27] lengths, every layer crossing within 25 ns, no SCT z smearing,
>= 2 hits in 7 layers), take the event with the MEDIAN Delta_s. Hits are rebuilt with the P18 code path; the rebuilt Delta_s
must equal tables/all_crossings_per_event.csv. Panels: all hits in the plane's (n3, n2) coordinates with the detector layers
drawn as ellipses (as in the paper), and a zoom of |n2| < 1 cm with the +-Delta_w band (Delta_w = sqrt(lambda_2), paper Eq. 11)."""
import os, sys, math, importlib.util, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fig_utils as fu
T = f"{HERE}/../tables"; S = os.path.abspath(__file__)
spec = importlib.util.spec_from_file_location("p18", f"{HERE}/P18_all_crossings.py"); p18 = importlib.util.module_from_spec(spec); spec.loader.exec_module(p18)
p4 = p18.p4; p4._init()
A = pd.read_csv(f"{T}/all_crossings_per_event.csv"); TR = lambda s: s.astype(str) == "True"
def build(s):
    x = A[(A["sample"] == s) & (A["mode"] == "ALL") & (A.sct == "Z0") & TR(A.fid) & TR(A.final)].sort_values("ds").reset_index(drop=True)
    r = x.iloc[len(x) // 2]; key = int(r.key)
    ev = p4.fp.load_sample(s).set_index("key").loc[key]; cr0 = pd.read_csv(f"{p4.FOR}/tables/truth_crossings_{s}.csv").query("key == @key").sort_values(["quirk", "layer"])
    ex = pd.read_csv(f"{T}/signal_exact_crossings_all_trigger_events.csv").query("sample == @s and key == @key").sort_values(["quirk", "layer"])
    z0, g = p4.fp.stream_draws(np.random.default_rng(int(ev.seed)), cr0, ex.copy()); m = p4.momenta(s).iloc[key]; mq, lam = p4.PAR["EW" if s.startswith("EW") else "COL"]
    _, traj = p4.tth.simulate_quirk_hits((m.px1, m.py1, m.pz1, m.E1), (m.px2, m.py2, m.pz2, m.E2), mass_gev=mq, Lambda_gev=lam, B_tesla=2.0, charge1=float(m.charge1), charge2=float(m.charge2),
                                         rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=60.0)
    cr = p18.all_crossings(traj); tth, cf = p4.tth, p4.cf; rng = np.random.default_rng(np.random.SeedSequence([18, p18.SID[s], key])); raw = []
    for c in cr:
        if c["t_ns"] >= 25.0 or abs(c["z_lab"]) >= p4.HALF[c["layer"]]: continue
        lay = tth.LAYERS[c["layer"] - 1]; rphi = lay["r_cm"] * math.atan2(c["y"], c["x"])
        if lay["is_pixel"]: rh, zh, ir, iz = tth.quantize_pixel(rphi, c["z_lab"], lay["eff_res_rphi_um"], lay["eff_res_z_um"])
        else:
            g1, g2 = g[(c["quirk"], c["layer"])] if (c["order"] == 0 and (c["quirk"], c["layer"]) in g) else rng.standard_normal(2); rh, zh, ir, iz = rphi + 34e-4 * g1, c["z_lab"], None, None
        ph = rh / lay["r_cm"]; raw.append(dict(layer=lay["name"], layer_r_cm=lay["r_cm"], quirk_index=c["quirk"], t_ns=c["t_ns"], x=lay["r_cm"] * math.cos(ph), y=lay["r_cm"] * math.sin(ph), z=zh,
                                               is_pixel=lay["is_pixel"], idx_rphi=ir, idx_z=iz))
    merged = tth.merge_neighboring_pixel_hits(raw); idx = {Ly["name"]: i for i, Ly in enumerate(tth.LAYERS, 1)}; hbl = {k: [] for k in range(1, 9)}
    for h in merged: hbl[idx[h["layer"]]].append(tuple(cf.vertex_relative_hits([(h["x"], h["y"], h["z"])], np.array([0.0, 0.0, z0]))[0]))
    cands = cf.seeding_and_iterative_fit(hbl); sel = min([c for c in cands if c["fit"]["delta_w"] < 1.0], key=lambda c: c["fit"]["delta_s"])
    assert abs(sel["fit"]["delta_s"] - r.ds) < 1e-9, (s, sel["fit"]["delta_s"], r.ds)
    n1, n2, n3 = (np.array(sel["fit"][k]) for k in ("n1", "n2", "n3")); ss = {tuple(np.round(h, 10)) for h in sel["hits"]}; rows = []
    for L, pts in hbl.items():
        for p in pts:
            p = np.array(p); rows.append(dict(sample=s, key=key, event_id=int(r.event_id), layer=L, n2_cm=p @ n2, n3_cm=p @ n3, in_plane=tuple(np.round(p, 10)) in ss,
                                              ds_cm=sel["fit"]["delta_s"], dw_cm=sel["fit"]["delta_w"], n_sr_events=len(x), rank=len(x) // 2 + 1))
    # layer ellipses in the (n3, n2) plane: points of the cylinder r = R intersected with the fitted plane through the vertex
    for L, lay in enumerate(tth.LAYERS, 1):
        u = np.cross(n1, [0, 0, 1.0]); u = u / np.linalg.norm(u) if np.linalg.norm(u) > 1e-9 else np.array([1.0, 0, 0])
        th = np.linspace(0, 2 * np.pi, 400); R = lay["r_cm"]
        # parametrise plane points q = a*n3 + b*n2 with transverse radius R: solve per angle in the plane
        for t_ in th:
            dvec = math.cos(t_) * n3 + math.sin(t_) * n2; tr = math.hypot(dvec[0], dvec[1])
            if tr < 1e-9: continue
            q = dvec * R / tr
            if abs(q[2] + z0) < p4.HALF[L] * 1.2 and q @ n3 > 0: rows.append(dict(sample=s, key=key, layer=L, ellipse=True, n2_cm=q @ n2, n3_cm=q @ n3))
    return pd.DataFrame(rows)
def plot(d):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(11, 7.4), gridspec_kw=dict(width_ratios=[1.25, 1]))
    for i, s in enumerate(["COL2000", "EW2000"]):
        g = d[(d["sample"] == s) & (d.ellipse != True)]; e = d[(d["sample"] == s) & (d.ellipse == True)]; dw, ds = g.dw_cm.iloc[0], g.ds_cm.iloc[0]
        ax = axes[i, 0]
        for L, ee in e.groupby("layer"): ax.plot(ee.n3_cm, ee.n2_cm, ".", ms=0.6, color=fu.MUTED)
        ax.scatter(g.n3_cm, g.n2_cm, marker="x", s=30, color=fu.SERIES[1] if s.startswith("EW") else fu.SERIES[0], label="hits", zorder=3)
        ax.set_xlabel("n₃ (cm)"); ax.set_ylabel("n₂ (cm)"); ax.set_xlim(0, 60); ax.set_ylim(-30, 30); ax.set_aspect("equal")
        lab = "colored 1.8 TeV, Λ = 2 keV" if s == "COL2000" else "EW 800 GeV, Λ = 4 keV"
        ax.set_title(f"{lab}: {s} event {int(g.event_id.iloc[0])} (median Δs of {int(g.n_sr_events.iloc[0])} signal-region events)", fontsize=8.5)
        bx = axes[i, 1]; bx.axhspan(-dw, dw, color=fu.SERIES[2], alpha=0.18, lw=0, label=f"±Δw = ±{dw:.3f} cm")
        bx.scatter(g.n3_cm, g.n2_cm, marker="x", s=36, color=fu.SERIES[1] if s.startswith("EW") else fu.SERIES[0], label=f"hits (Δs = {ds*1e4:.0f} µm)")
        bx.set_ylim(-1, 1); bx.set_xlim(0, 60); bx.set_xlabel("n₃ (cm)"); bx.set_ylabel("n₂ (cm)"); bx.set_title("zoom, |n₂| < 1 cm", fontsize=9); bx.legend(fontsize=7, loc="upper left")
    fig.tight_layout(); return fig
src = pd.concat([build("COL2000"), build("EW2000")])
fu.figure("F25_fig4_median_events", src, plot, "Figure 4 style. Selection rule (fixed): for COL2000 and EW2000, the event with the median Δs among all events passing the full "
          "signal region in the current primary setup (Ref. [27] lengths, every layer crossing within 25 ns, no SCT smearing along the beam). Left: all hits in the "
          "plane's (n₃, n₂) coordinates with the detector layers as ellipses (grey). Right: zoom with the ±Δw band (Δw = √λ₂, paper Eq. 11).",
          [f"{T}/all_crossings_per_event.csv"], "median Delta_s among signal-region events", S)
print(src[src.ellipse != True].groupby("sample")[["key", "event_id", "ds_cm", "dw_cm", "n_sr_events", "rank"]].first())
