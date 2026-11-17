#!/usr/bin/env python3
"""07 X07 (2026-11-17): size of the multiple-scattering displacement of the quirks, which the simulation does not include (both geometries).
For every event selected at Lambda = 4 keV (server runs; group "barrel" = selected in Ideal and ATLAS, group "ATLAS-only" = selected only in ATLAS):
  - path: straight line from (0, 0, 0) along the pair direction eta_pair (the hits follow the pair, X04), crossing the beam pipe (r = 2.35 cm,
    x/X0 = 0.227 %, R6) and every ATLAS element (sim/detsim07.build('atlas'): barrel inside |z| < half length, disk inside rmin..rmax) with its x/X0;
    effective thickness t = (x/X0) / |sin theta| for a barrel layer and (x/X0) / |cos theta| for a disk;
  - Highland (PDG 2024, R7, Eq. 34.15): theta0 = 13.6 MeV / (beta c p) * z * sqrt(t) * (1 + 0.038 ln(t z^2 / beta^2)), z = 1;
  - projected (out-of-plane) displacement at the k-th silicon measurement: sigma_k = sqrt( sum_{i before k} theta0_i^2 (s_k - s_i)^2 ), s = path length;
    reported at the 8th measurement (station 8, the largest) and as the RMS over the 8 measurements;
  - momentum: (a) each quirk's initial lab momentum (inputs_large); (b) conservative lower bound p_min = m * beta*gamma(pair): the lab momentum of a quirk
    momentarily at rest in the pair frame (turning point of the string oscillation), beta_min = beta(pair).
Compared with the pixel / SCT r-phi resolution (~10-17 um intrinsic, R3) and the Delta_s < 0.01 cm = 100 um cut of the selection.
Writes tables/X07_multiple_scattering_events.csv and tables/X07_multiple_scattering_summary.csv."""
import os, sys, json, math, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(f"{HERE}/.."); sys.path.insert(0, f"{R}/sim")
import detsim07 as D
ELS = D.build("atlas"); M = pd.read_csv(f"{R}/geometry/atlas_run2_id_material.csv").set_index("component")
BP_R, BP_X0 = 2.35, float(M.loc["beam_pipe_Be_wall", "x_over_X0_normal_incidence"]); LAM = 4.0
def crossings(eta):
    th = 2 * math.atan(math.exp(-abs(eta))); st, ct = math.sin(th), math.cos(th); out = [(BP_R / st, BP_X0 / st, False)]
    for e in ELS:
        if e["kind"] == "barrel":
            s = e["r_cm"] / st
            if abs(s * ct) < e["half_cm"]: out.append((s, e["x0"] / st, True))
        elif e["z_cm"] > 0 and ct > 1e-9:
            s = e["z_cm"] / ct; r = s * st
            if e["rmin_cm"] <= r <= e["rmax_cm"]: out.append((s, e["x0"] / ct, True))
    return sorted(out)
def disp(eta, p, beta):
    cr = crossings(eta); th0 = [0.0136 / (beta * p) * math.sqrt(t) * (1 + 0.038 * math.log(t / beta ** 2)) for _, t, _ in cr]
    meas = [k for k, c in enumerate(cr) if c[2]][:8]; sig = []
    for k in meas:
        sig.append(math.sqrt(sum(th0[i] ** 2 * (cr[k][0] - cr[i][0]) ** 2 for i in range(k))) * 1e4)   # cm -> um
    return (sig[-1] if sig else np.nan), (math.sqrt(np.mean(np.square(sig))) if sig else np.nan), len(meas), sum(t for _, t, _ in cr[: (meas[-1] + 1 if meas else 0)])
def load(d, tag):
    out = {}
    for l in open(f"{R}/signal/runs/{d}/G01_{tag}_mid.jsonl"):
        for r in json.loads(l):
            if abs(r["lambda_keV"] - LAM) < 1e-9: out[r["event"]] = r
    return out
C = pd.read_csv(f"{R}/signal/inputs_large/counts.csv"); rows = []
for c in C.itertuples():
    tag = f"{c.channel}_{c.mass_gev}gev"
    if not os.path.exists(f"{R}/signal/runs/large_atlas/G01_{tag}_mid.jsonl"): continue
    A, I = load("large_atlas", tag), load("large_ideal", tag); ev = pd.read_csv(f"{R}/signal/inputs_large/{tag}_events.csv").set_index("event_id")
    for e, r in A.items():
        if not r.get("Z0_final"): continue
        grp = "barrel (selected in Ideal and ATLAS)" if I[e].get("Z0_final") else "ATLAS-only"
        x = ev.loc[e]; P = np.array([x.px1 + x.px2, x.py1 + x.py2, x.pz1 + x.pz2]); Ep = x.E1 + x.E2
        eta = math.asinh(P[2] / math.hypot(P[0], P[1])); bg_pair = np.linalg.norm(P) / math.sqrt(max(Ep ** 2 - P @ P, 1e-9)); b_pair = np.linalg.norm(P) / Ep
        for q in (1, 2):
            p = math.sqrt(x[f"px{q}"] ** 2 + x[f"py{q}"] ** 2 + x[f"pz{q}"] ** 2); beta = p / x[f"E{q}"]
            s8a, rmsa, nm, tsum = disp(eta, p, beta); s8b, rmsb, _, _ = disp(eta, c.mass_gev * bg_pair, b_pair)
            rows.append(dict(channel=c.channel, mass_gev=c.mass_gev, event=e, quirk=q, group=grp, abs_eta_pair=abs(eta), p_gev=p, beta=beta,
                             n_meas=nm, sum_t_X0=tsum, sigma_st8_um=s8a, sigma_rms_um=rmsa, p_min_gev=c.mass_gev * bg_pair, beta_min=b_pair,
                             sigma_st8_um_pmin=s8b, sigma_rms_um_pmin=rmsb))
E = pd.DataFrame(rows); E.to_csv(f"{R}/tables/X07_multiple_scattering_events.csv", index=False)
def summ(x):
    d = {"n_quirks": len(x), "median_|eta|": x.abs_eta_pair.median(), "median_sum_x/X0_to_st8": x.sum_t_X0.median()}
    for col, nm in (("sigma_st8_um", "st8"), ("sigma_st8_um_pmin", "st8_pmin")):
        v = x[col].dropna(); d.update({f"{nm}_median_um": v.median(), f"{nm}_p90_um": v.quantile(0.9), f"{nm}_max_um": v.max(),
                                        f"{nm}_frac>10um": (v > 10).mean(), f"{nm}_frac>100um": (v > 100).mean()})
    return pd.Series(d)
S = E.groupby(["channel", "group"]).apply(summ, include_groups=False).reset_index()
S2 = E.groupby(["channel", "mass_gev", "group"]).apply(summ, include_groups=False).reset_index()
pd.concat([S.assign(mass_gev="all"), S2]).to_csv(f"{R}/tables/X07_multiple_scattering_summary.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.float_format", lambda v: f"{v:.3g}")
print(S.to_string(index=False)); print(S2[S2.mass_gev.isin([100, 400, 1000, 600, 1500, 2400])].to_string(index=False))
