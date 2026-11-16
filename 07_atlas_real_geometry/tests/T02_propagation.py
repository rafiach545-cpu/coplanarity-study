#!/usr/bin/env python3
"""07 test T02 (2026-11-15): propagation in sim/detsim07.py against independent / Stage 2 code.
(a) first_crossings (pile-up response), stage2 elements, vs 02_backgrounds/pileup/helix_propagation.find_helix_layer_crossings + the Stage 2
    acceptance (|z| < half) and 25 ns cut: same set of layers with hits, positions and times, 20 000 random pions.
(b) propagate_stage2 vs P17_conversion_ref34.track34 (Stage 2 electrons), material on and off, 4000 random conversion electrons:
    identical crossing sequence, positions, times.
(c) general propagate (atlas elements, barrel + disks, no material) vs an independent Boris pusher (step 0.005 cm) sampled and intersected with
    geometry/atlas_run2_geometry.trajectory_crossings (mm): same elements in the same order, positions within 0.01 cm, 300 random tracks.
(d) material on a disk: E after one SCT-disk crossing at normal incidence = E exp(-x0) - 0.28 MeV/mm * x0 * 93.7 mm.
Prints T02_PASS / T02_FAIL."""
import os, sys, math, importlib.util, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = f"{HERE}/.."; sys.path.insert(0, f"{ROOT}/sim"); sys.path.insert(0, f"{ROOT}/geometry")
import detsim07 as D, atlas_run2_geometry as G
from helix_propagation import find_helix_layer_crossings
spec = importlib.util.spec_from_file_location("p17", f"{D.SCR}/P17_conversion_ref34.py"); P17 = importlib.util.module_from_spec(spec); spec.loader.exec_module(P17)
rng = np.random.default_rng(20261115); S2 = D.build("stage2"); AT = D.build("atlas"); ok = {}

# (a)
bad, maxd, maxt, n_hits = 0, 0.0, 0.0, 0
for _ in range(20000):
    pt = 10 ** rng.uniform(-1, 1.3); eta = rng.uniform(-3, 3); ph = rng.uniform(-math.pi, math.pi); q = rng.choice([-1.0, 1.0])
    p = np.array([pt * math.cos(ph), pt * math.sin(ph), pt * math.sinh(eta)]); v = np.array([0.0, 0.0, rng.normal(0, 4.5)])
    mine = {k: c for k, c in D.first_crossings(v, p, q, 0.13957, S2, D.RC_STAGE2_PU).items() if c[1] <= D.TCUT}
    ref = find_helix_layer_crossings(v, p, 0.13957, q, 2.0, [e["r_cm"] for e in S2]); theirs = {}
    for e in S2:
        r = ref.get(e["r_cm"])
        if r is None or r[1] is None or r[1] > 25.0 or abs(r[0][2]) >= e["half_cm"]: continue
        theirs[e["name"]] = r
    if set(mine) != set(theirs): bad += 1; continue
    for k in mine:
        maxd = max(maxd, float(np.max(np.abs(mine[k][0] - theirs[k][0])))); maxt = max(maxt, abs(mine[k][1] - theirs[k][1])); n_hits += 1
ok["a"] = bad == 0 and maxd < 1e-8 and maxt < 1e-8
print(f"(a) pile-up first crossings (Stage 2 constant) vs find_helix_layer_crossings: {n_hits} hits, layer-set mismatches {bad}, max |dx| {maxd:.1e} cm, max |dt| {maxt:.1e} ns")

# (b)
bad, maxd, n_cr = 0, 0.0, 0
for _ in range(4000):
    E = 10 ** rng.uniform(-0.6, 2); eta = rng.uniform(-2, 2); ph = rng.uniform(-math.pi, math.pi); th = 2 * math.atan(math.exp(-eta))
    z0 = rng.normal(0, 4.5); cp = np.array([2.35 * math.cos(ph), 2.35 * math.sin(ph), z0 + 2.35 / math.tan(th)])
    p = E * np.array([math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)])
    for q in (-1.0, 1.0):
        for mat in (False, True):
            a = D.propagate_stage2(cp, p, q, D.ME, S2, material=mat); b = P17.track34(cp, p, q, mat)
            if [c[0]["name"] for c in a] != [c[0]["name"] for c in b]: bad += 1; continue
            for ca, cb in zip(a, b):
                maxd = max(maxd, abs(ca[1] - cb[1]), abs(ca[2] - cb[2]), abs(ca[3] - cb[3]), abs(ca[4] - cb[4])); n_cr += 1
ok["b"] = bad == 0 and maxd < 1e-6
print(f"(b) electrons vs Stage 2 track34 (material on/off): {n_cr} crossings, sequence mismatches {bad}, max |d(x,y,z,t)| {maxd:.1e}")

# (c)
def boris_batch(X0, P0, Q, m, ds=0.01, smax=760.0):
    """Independent integrator, vectorised over tracks: rotation of p about z by k ds / |p| per path step ds (exact for uniform Bz; Boris
    form), straight step of length ds along the updated direction. Returns arrays (n_steps, n_tracks) x, y, z (cm) and t (n_steps, n_tracks)."""
    n = int(smax / ds); pm = np.linalg.norm(P0, axis=1); v = pm / np.sqrt(pm ** 2 + m ** 2)
    k = 0.299792458 * D.B_T / 100.0 * Q; tz = k * ds / pm * 0.5; sz = 2 * tz / (1 + tz * tz)   # Boris t = q B ds / (2 p): dp/ds = q (u x B)
    X = np.empty((n, len(Q), 3)); X[0] = X0; pp = np.array(P0, float)
    for i in range(1, n):
        prx = pp[:, 0] + pp[:, 1] * tz; pry = pp[:, 1] - pp[:, 0] * tz
        pp = np.stack([pp[:, 0] + pry * sz, pp[:, 1] - prx * sz, pp[:, 2]], axis=1)
        X[i] = X[i - 1] + pp / pm[:, None] * ds
    t = (np.arange(n) * ds)[:, None] / (D.CL * v)[None, :]
    return X, t
NT = 300; PT = 10 ** rng.uniform(-0.3, 1.5, NT); ETA = rng.uniform(-2.8, 2.8, NT); PH = rng.uniform(-math.pi, math.pi, NT); Q = rng.choice([-1.0, 1.0], NT)
P0 = np.stack([PT * np.cos(PH), PT * np.sin(PH), PT * np.sinh(ETA)], axis=1); X0 = np.stack([np.zeros(NT), np.zeros(NT), rng.normal(0, 4.5, NT)], axis=1)
XB, TB = boris_batch(X0, P0, Q, 0.13957)
bad, maxd, ncr, nd = 0, 0.0, 0, 0
for j in range(NT):
    mine = D.propagate(X0[j], P0[j], Q[j], 0.13957, AT, material=False)
    ref = [c for c in G.trajectory_crossings(XB[:, j, 0] * 10, XB[:, j, 1] * 10, XB[:, j, 2] * 10, TB[:, j]) if c[4] <= D.TCUT]
    nm_ref = [(c[0]["name"] if c[0]["kind"] == "disk" else D.ATLAS_NAME[c[0]["name"]]) for c in ref]
    if [c[0]["name"] for c in mine] != nm_ref: bad += 1; print("   mismatch", [c[0]["name"] for c in mine], nm_ref); continue
    for a, b in zip(mine, ref):
        maxd = max(maxd, abs(a[1] - b[1] / 10), abs(a[2] - b[2] / 10), abs(a[3] - b[3] / 10)); ncr += 1; nd += a[0]["kind"] == "disk"
ok["c"] = bad == 0 and maxd < 0.01
print(f"(c) propagate (barrel + disks) vs vectorised Boris + trajectory_crossings: {ncr} crossings ({nd} on disks), mismatches {bad}, max |dx| {maxd:.1e} cm")

# (d)
e = [x for x in AT if x["name"] == "SCTD1_outer_A"][0]; E0 = 5.0; pz = math.sqrt(E0 ** 2 - D.ME ** 2)
x = np.array([50.0, 0.0, 0.0]); pp = np.array([0.0, 1e-6, pz]); out = D.propagate(x, pp, -1.0, D.ME, [e, dict(e, name="probe", z_cm=e["z_cm"] + 1.0, x0=0.0)], material=True)
# energy after the first disk: read from the momentum change via a second, material-free probe disk 1 cm behind it
ok["d"] = len(out) == 2
Eexp = E0 * math.exp(-e["x0"]) - D.DEDX_MP_GEV_PER_MM * e["x0"] * D.SI_X0_MM
h = D._helix(x, pp, -1.0); a = (e["z_cm"] - x[2]) * h[0] / (h[1] * pp[2]); pos, pn = D._pos(x, pp, h, a)
pm = math.sqrt(pn @ pn); Eb = math.sqrt(pm * pm + D.ME ** 2); te = e["x0"] / (abs(pn[2]) / pm); Ea = Eb * math.exp(-te) - D.DEDX_MP_GEV_PER_MM * te * D.SI_X0_MM
ok["d"] = ok["d"] and abs(Ea - Eexp) < 1e-9
print(f"(d) SCT disk material at normal incidence: E after = {Ea:.6f} GeV, expected {Eexp:.6f} GeV (x/X0 = {e['x0']})")
print("T02_PASS" if all(ok.values()) else f"T02_FAIL {ok}")
