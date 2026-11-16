#!/usr/bin/env python3
"""07 test T03 (2026-11-15): end-cap hit response and the station COP on end-cap tracks (sim/detsim07.py, sim/cop07.py, atlas elements).
(a) pixel disk quantisation: |r_hit - r| <= 200 um (pitch 400 / 2) and |r phi_hit - r phi| <= 25 um (+ the r-quantisation effect on r-phi, bound
    50/2 um + r_phi * 200 um / r), 50 000 random points.
(b) SCT disk smearing with sigma_long = 1160 um: std(r_hit - r) = 1160 um and std(r dphi) = 34 um within 2%, mean within 3 sigma/sqrt(N).
(c) resmear: Z1160 -> Z0 gives back the true long coordinate exactly; Z0 -> Z1160 equals a direct Z1160 response with the same normals.
(d) disk pixel merging: two hits in neighbouring pixels merge into one with merged_count 2; hits 2 pixels apart stay separate.
(e) station COP on synthetic planes: two stiff (pT = 1 TeV) opposite-charge tracks from the PV, 1 cm apart in theta at the 8th station
    (inside the paper's 2 cm seed cut; same phi), eta 0-2.4, at |eta| = 1.4,
    1.9, 2.3 (barrel/disk mixtures and pure disks), SCT r-phi smearing 34 um (Z0; without any smearing the 4-hit seed has Delta_s = 0 and
    the paper's growth rule 'Delta_s may grow by at most 3x' rejects every further hit; a phi separation puts the r-phi smearing inside the
    plane, the same problem). Whenever both tracks cross the same first 4 pixel + 4 SCT elements, cop07 must select a plane with 2 hits on
    pass the final selection (Sec. IV: 2 hits on all but one station). Pairs whose two tracks cross different elements (barrel/disk boundaries, an element
    just missed) are counted separately: there the paper's seed-pair cut can fail (an acceptance effect, to be measured on the signal).
(f) station list on the barrel equals the 8 barrel layers for |eta| < 1.0 (z0 = 0) - consistency with Stages 1-2.
Prints T03_PASS / T03_FAIL."""
import os, sys, math, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = f"{HERE}/.."; sys.path.insert(0, f"{ROOT}/sim")
import detsim07 as D, cop07
rng = np.random.default_rng(1115); AT = D.build("atlas"); ok = {}
pd_ = [e for e in AT if e["kind"] == "disk" and e["is_pixel"]][0]; sd = [e for e in AT if e["kind"] == "disk" and not e["is_pixel"]][0]
# (a)
w = 0.0; wr = 0.0
for _ in range(50000):
    r = rng.uniform(pd_["rmin_cm"], pd_["rmax_cm"]); ph = rng.uniform(-math.pi, math.pi)
    h = D.respond(pd_, r * math.cos(ph), r * math.sin(ph), pd_["z_cm"], 1.0, "t", 0, 0, "Z0"); rh = math.hypot(h["x"], h["y"]); phh = math.atan2(h["y"], h["x"])
    rref = 0.5 * (pd_["rmin_cm"] + pd_["rmax_cm"])
    wr = max(wr, abs(rh - r)); dphi = (phh - ph + math.pi) % (2 * math.pi) - math.pi; w = max(w, abs(r * dphi) / (r / rref))
ok["a"] = wr <= 0.02 + 1e-12 and w <= 0.0025 + 1e-9
print(f"(a) pixel disk: max |dr| = {wr * 1e4:.1f} um (<= 200), max r-phi error scaled to r_ref = {w * 1e4:.1f} um (<= 25; angular pitch 50 um / r_ref)")
# (b)
N = 100000; dr, drp = np.empty(N), np.empty(N)
for k in range(N):
    r = rng.uniform(sd["rmin_cm"], sd["rmax_cm"]); ph = rng.uniform(-math.pi, math.pi); g = rng.standard_normal(2)
    h = D.respond(sd, r * math.cos(ph), r * math.sin(ph), sd["z_cm"], 1.0, "t", g[0], g[1], "Z1160")
    dr[k] = math.hypot(h["x"], h["y"]) - r; drp[k] = r * ((math.atan2(h["y"], h["x"]) - ph + math.pi) % (2 * math.pi) - math.pi)
s1, s2 = dr.std() * 1e4, drp.std() * 1e4
ok["b"] = abs(s1 / 1160 - 1) < 0.02 and abs(s2 / 34 - 1) < 0.02 and abs(dr.mean()) < 3 * dr.std() / math.sqrt(N) and abs(drp.mean()) < 3 * drp.std() / math.sqrt(N)
print(f"(b) SCT disk: std(dr) = {s1:.1f} um (1160), std(r dphi) = {s2:.2f} um (34), means {dr.mean() * 1e4:.2f} / {drp.mean() * 1e4:.3f} um")
# (c)
hs = []
for e in (sd, [x for x in AT if x["kind"] == "barrel" and not x["is_pixel"]][0]):
    for _ in range(200):
        g = rng.standard_normal(2)
        if e["kind"] == "disk": r = rng.uniform(e["rmin_cm"], e["rmax_cm"]); ph = rng.uniform(-3, 3); x, y, z = r * math.cos(ph), r * math.sin(ph), e["z_cm"]
        else: ph = rng.uniform(-3, 3); x, y, z = e["r_cm"] * math.cos(ph), e["r_cm"] * math.sin(ph), rng.uniform(-50, 50)
        hs.append((e, x, y, z, g, D.respond(e, x, y, z, 1.0, "t", g[0], g[1], "Z1160"), D.respond(e, x, y, z, 1.0, "t", g[0], g[1], "Z0")))
back = D.resmear([t[5] for t in hs], "Z0"); fwd = D.resmear([t[6] for t in hs], "Z1160")
e0 = max(max(abs(b["x"] - t[6]["x"]), abs(b["y"] - t[6]["y"]), abs(b["z"] - t[6]["z"])) for b, t in zip(back, hs))
e1 = max(max(abs(f["x"] - t[5]["x"]), abs(f["y"] - t[5]["y"]), abs(f["z"] - t[5]["z"])) for f, t in zip(fwd, hs))
ok["c"] = e0 < 1e-12 and e1 < 1e-12
print(f"(c) resmear: Z1160 -> Z0 max diff {e0:.1e} cm, Z0 -> Z1160 max diff {e1:.1e} cm")
# (d)
r0 = 12.0; pr = 0.04
mk = lambda r, phi: D.respond(pd_, r * math.cos(phi), r * math.sin(phi), pd_["z_cm"], 1.0, "a", 0, 0, "Z0")
h1 = mk(r0, 0.3); h2 = mk(r0 + pr, 0.3); h3 = mk(r0 + 3 * pr, 0.3)
m12 = D._merge_disk_pixels([h1, h2]); m13 = D._merge_disk_pixels([h1, h3])
ok["d"] = len(m12) == 1 and m12[0]["merged_count"] == 2 and len(m13) == 2
print(f"(d) disk pixel merging: neighbours -> {len(m12)} cluster (count {m12[0]['merged_count']}), 3 pixels apart -> {len(m13)} clusters")
# (e)
from collections import Counter
same, same_ok, diff, diff_ok = 0, 0, 0, 0
for eta in np.round(np.arange(0.0, 2.45, 0.05), 2):
    hits, seq = [], []
    th0 = 2 * math.atan(math.exp(-eta)); u0 = np.array([math.cos(0.7) * math.sin(th0), math.sin(0.7) * math.sin(th0), math.cos(th0)])
    c0 = D.propagate(np.zeros(3), 1000.0 * u0 / math.sin(th0), -1.0, 0.5, AT, material=False)
    sct0 = [c for c in c0 if not c[0]["is_pixel"]][:4]
    L8 = math.sqrt(sct0[-1][1] ** 2 + sct0[-1][2] ** 2 + sct0[-1][3] ** 2) if len(sct0) == 4 else 50.0
    for body, (q, dth) in enumerate(((-1.0, 0.0), (1.0, -1.0 / L8))):                # 1 cm apart at the 8th station, in theta
        th = th0 + dth; pt = 1000.0; p = np.array([pt * math.cos(0.7), pt * math.sin(0.7), pt / math.tan(th)])
        cr = D.propagate(np.zeros(3), p, q, 0.5, AT, material=False); seq.append([c[0]["name"] for c in cr])
        for e, x, y, z, t in cr:
            g = rng.standard_normal(2); hits.append(D.respond(e, x, y, z, t, body, g[0], g[1], "Z0"))
    merged, _ = D.overlay(hits, [])
    res, wn = cop07.analyse(merged, (0.0, 0.0, 0.0), AT)
    cnt = Counter(wn["layers"]) if wn else Counter(); good = bool(res["final"])
    # the two tracks have the same first-4-pixel / first-4-SCT element sequence?
    f = lambda sq: ([n for n in sq if n.startswith(("L1", "L2", "L3", "L4", "PIXD"))][:4], [n for n in sq if n.startswith(("L5", "L6", "L7", "L8", "SCTD"))][:4])
    if f(seq[0]) == f(seq[1]) and len(f(seq[0])[0]) == 4 and len(f(seq[0])[1]) == 4:
        same += 1; same_ok += good
        if not good: print(f"   same sequence but not found: eta {eta}, {[cnt[k] for k in range(1, 9)]}, final {res['final']}")
    else: diff += 1; diff_ok += good
print(f"(e) synthetic pairs (pT 1 TeV, 1 cm apart in theta at the 8th station, SCT r-phi 34 um), eta 0-2.4: same 8-station sequence {same} -> "
      f"final selection passed: {same_ok}/{same}; different sequences (boundaries, an element just missed) {diff} -> passed {diff_ok}/{diff}")
ok["e"] = same_ok == same and same > 0
# (f)
bar = [e["name"] for e in AT if e["kind"] == "barrel"]; fs = []
for eta in np.linspace(0, 1.0, 21):
    th = 2 * math.atan(math.exp(-eta)); fs.append(cop07.station_list(np.array([math.sin(th), 0, math.cos(th)]), (0, 0, 0), AT) == bar)
ok["f"] = all(fs); print(f"(f) barrel station list for |eta| <= 1.0: {sum(fs)}/{len(fs)} equal to the 8 barrel layers")
print("T03_PASS" if all(ok.values()) else f"T03_FAIL {ok}")
