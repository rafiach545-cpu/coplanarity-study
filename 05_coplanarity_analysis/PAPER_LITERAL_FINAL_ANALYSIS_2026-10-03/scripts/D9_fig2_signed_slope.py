#!/usr/bin/env python3
"""Model-independent test on Fig. 2 curves (2026-10-11). Signed L: |L| with its sign flipped at every zero (cusp) of |L|.
In the torque picture of Eq. 5 (dL/dt = q d x E_cm, constant CM velocity) dL/dr is proportional to d with one constant magnitude and a sign that
flips at every closest approach (each arch of d). Fit, per point away from cusps and d zeros:  dL_s/dr = (a * sigma_k + b) * d,
sigma_k = +1, -1, +1, ... for the successive arches of d. b = part of the torque that does not change sign; b/a its relative size.
Applied to the paper's curves (vector figure) and, as control, to our constructed event (tables/D8_fig2_toy_curves.csv, axis z, charge 2/3)."""
import os, json, numpy as np, pandas as pd
T = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tables")
def analyse(rL, L, rd, d, label):
    o = np.argsort(rL); rL, L = np.asarray(rL)[o], np.asarray(L)[o]; o = np.argsort(rd); rd, d = np.asarray(rd)[o], np.asarray(d)[o]
    g = np.linspace(0.02, min(rL.max(), rd.max(), 5.0) - 0.02, 2000); Lg = np.interp(g, rL, L); dg = np.interp(g, rd, d)
    lz = [g[i] for i in range(1, len(g) - 1) if Lg[i] < Lg[i - 1] and Lg[i] <= Lg[i + 1] and Lg[i] < 0.05 * Lg.max()]
    dz = [0.0] + [g[i] for i in range(1, len(g) - 1) if dg[i] < dg[i - 1] and dg[i] <= dg[i + 1] and dg[i] < 0.1 * dg.max()]
    s = np.ones_like(g)
    for z in lz: s[g > z] *= -1
    Ls = s * Lg; dLdr = np.gradient(Ls, g); arch = np.searchsorted(dz, g) - 1; sig = np.where(arch % 2 == 0, 1.0, -1.0)
    near = np.zeros_like(g, bool)
    for z in lz + dz: near |= np.abs(g - z) < 0.12
    ok = ~near & (dg > 0.3 * dg.max())
    X = np.column_stack([sig[ok] * dg[ok], dg[ok]]); (a, b), *_ = np.linalg.lstsq(X, dLdr[ok], rcond=None)
    res = dLdr[ok] - X @ [a, b]; R = dLdr[ok] / dg[ok]
    per = pd.DataFrame(dict(arch=arch[ok], ratio=R)).groupby("arch").ratio.agg(["median", "std", "size"])
    print(f"== {label}: |L| zeros at r = {np.round(lz, 2)}, d zeros at r = {np.round(dz[1:], 2)}")
    print(f"   fit dL_s/dr = (a*sigma + b)*d : a = {a:.3g}, b = {b:.3g}, b/a = {b/a:+.3f}; rms residual / |a|*<d> = {np.sqrt((res**2).mean())/abs(a)/dg[ok].mean():.3f}")
    print("   ratio (dL_s/dr)/d per arch of d (median, std, n):"); print(per.round(4).to_string())
    return dict(label=label, a=a, b=b, b_over_a=b / a)
V = json.load(open(f"{T}/paper_fig23_vector.json"))["fig2"]["curves"]
out = [analyse(V["L_1e12_hbar"]["x"], V["L_1e12_hbar"]["y"], V["d_cm"]["x"], V["d_cm"]["y"], "paper Fig. 2 (L in 1e12 hbar)")]
toy = pd.read_csv(f"{T}/D8_fig2_toy_curves.csv"); toy = toy[(toy["axis"] == "z (beam)") & np.isclose(toy.charge, 2 / 3)]
out.append(analyse(toy.r_cm, toy.L_cm_hbar / 1e12, toy.r_cm, toy.d_cm, "constructed event (control)"))
pd.DataFrame(out).to_csv(f"{T}/D9_fig2_signed_slope.csv", index=False)

# ---- addendum: control with the physical sign (L_s = signed projection, no flip where |L| only touches zero) and a model check on the paper's d
def fit_arches(r, Ls, d, label):
    g = np.linspace(0.02, min(r.max(), 5.0) - 0.02, 2000); Lg = np.interp(g, r, Ls); dg = np.interp(g, r, d); dLdr = np.gradient(Lg, g)
    dz = [0.0] + [g[i] for i in range(1, len(g) - 1) if dg[i] < dg[i - 1] and dg[i] <= dg[i + 1] and dg[i] < 0.1 * dg.max()]
    arch = np.searchsorted(dz, g) - 1; sig = np.where(arch % 2 == 0, 1.0, -1.0); near = np.zeros_like(g, bool)
    for z in dz: near |= np.abs(g - z) < 0.12
    ok = ~near & (dg > 0.3 * dg.max()); X = np.column_stack([sig[ok] * dg[ok], dg[ok]]); (a, b), *_ = np.linalg.lstsq(X, dLdr[ok], rcond=None)
    print(f"== {label}: a = {a:.4g}, b = {b:.3g}, b/a = {b/a:+.4f}"); return a, b
c = toy.sort_values("r_cm"); r = c.r_cm.values; L = c.L_cm_hbar.values / 1e12; d = c.d_cm.values
dz = [0.0] + [r[i] for i in range(1, len(r) - 1) if d[i] < d[i - 1] and d[i] <= d[i + 1] and d[i] < 0.1 * d.max()]
fit_arches(r, L, d, "constructed event, physical sign (|L| touches zero, no flip)")
# model: L_s(r) = integral of (a*sigma + b) * d dr on the paper's own d curve, with the paper fit (a, b)
pa, pb = out[0]["a"], out[0]["b"]; rd = np.array(V["d_cm"]["x"]); dd = np.array(V["d_cm"]["y"]); o = np.argsort(rd); rd, dd = rd[o], dd[o]
g = np.linspace(0, 5.0, 5001); dg = np.interp(g, rd, dd); zz = [0.0] + [g[i] for i in range(1, len(g) - 1) if dg[i] < dg[i - 1] and dg[i] <= dg[i + 1] and dg[i] < 0.1 * dg.max()]
sig = np.where((np.searchsorted(zz, g) - 1) % 2 == 0, 1.0, -1.0)
for lab, bb in (("paper fit (a, b)", pb), ("same a, b = 0", 0.0)):
    Ls = np.concatenate([[0], np.cumsum(0.5 * ((pa * sig + bb) * dg)[1:] * np.diff(g) + 0.5 * ((pa * sig + bb) * dg)[:-1] * np.diff(g))]); A = np.abs(Ls)
    pk = [f"{A[np.argmin(np.abs(g - z))]:.2f}" for z in zz[1:]]; zr = [g[i] for i in range(1, len(g) - 1) if A[i] < A[i - 1] and A[i] <= A[i + 1] and A[i] < 0.03 and g[i] > 0.1]
    print(f"   model {lab}: |L| at closest approaches = {' / '.join(pk)} ; |L| zeros at r = {np.round(zr, 2)}")
print("   paper: |L| at closest approaches = 0.65 / 0.19 / 0.52 / 0.29 ; |L| zeros at r = [1.91 2.67 4.10]")
