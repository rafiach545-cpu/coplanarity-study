#!/usr/bin/env python3
"""07 test T06 (2026-11-16): SCT resolution settings of decision D4 (sim/detsim07.py, atlas elements).
(a) A580 response: std(r-phi residual) = 17 um and std(long residual) = 580 um within 2% (barrel: long = z; disk: long = R), Z1160: 34 / 1160 um,
    Z0: 34 / 0 um; means within 3 sigma / sqrt(N); 40 000 random hits per element type and setting.
(b) Z0 and Z1160 responses are bit for bit the pre-D4 formulas (re-implemented below from the 2026-11-15 code), barrel and disk.
(c) resmear: every pair of settings (from -> to) gives exactly the direct response of the target setting with the same normals (max |dx|, |dy|,
    |dz| < 1e-12 cm; the disk Z0 <-> Z1160 path recovers phi with atan2, 7e-15 cm as in T03 (c)); Z0 <-> Z1160 is bit for bit the pre-D4 resmear.
(d) the new keys (rphi_true, g_rphi, res_rphi_um, rphi_factor) survive overlay() for barrel and disk SCT hits.
The C01 regression (Z0 / Z1160 rows of the production runs reproduced exactly) is T06 part (e), run separately: T06e_c01_regression.sh.
Prints T06_PASS / T06_FAIL."""
import os, sys, math, itertools, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = f"{HERE}/.."; sys.path.insert(0, f"{ROOT}/sim")
import detsim07 as D
rng = np.random.default_rng(1116); AT = D.build("atlas"); ok = {}
sb = [e for e in AT if e["kind"] == "barrel" and not e["is_pixel"]][0]; sd = [e for e in AT if e["kind"] == "disk" and not e["is_pixel"]][0]
assert sb["res_rphi_um"] == 34.0 and sd["res_rphi_um"] == 34.0
EXPECT = {"Z0": (34.0, 0.0), "Z1160": (34.0, 1160.0), "A580": (17.0, 580.0)}


def point(e):
    if e["kind"] == "barrel":
        ph = rng.uniform(-math.pi, math.pi); z = rng.uniform(-e["half_cm"], e["half_cm"]); return e["r_cm"] * math.cos(ph), e["r_cm"] * math.sin(ph), z
    r = rng.uniform(e["rmin_cm"], e["rmax_cm"]); ph = rng.uniform(-math.pi, math.pi); return r * math.cos(ph), r * math.sin(ph), e["z_cm"]


def residuals(e, x, y, z, h):
    if e["kind"] == "barrel":
        R = e["r_cm"]; dph = (math.atan2(h["y"], h["x"]) - math.atan2(y, x) + math.pi) % (2 * math.pi) - math.pi; return R * dph, h["z"] - z
    r = math.hypot(x, y); dph = (math.atan2(h["y"], h["x"]) - math.atan2(y, x) + math.pi) % (2 * math.pi) - math.pi
    return r * dph, math.hypot(h["x"], h["y"]) - r


def old_response(e, x, y, z, g1, g2, sct):                       # pre-D4 code (2026-11-15), SCT only
    sl = {"Z0": 0.0, "Z1160": 0.1160}[sct]; phi = math.atan2(y, x)
    if e["kind"] == "barrel":
        R = e["r_cm"]; rh = R * phi + e["res_rphi_um"] * 1e-4 * g1; ph = rh / R; return R * math.cos(ph), R * math.sin(ph), z + sl * g2
    r = math.hypot(x, y); rh = r + sl * g2; ph = phi + e["res_rphi_um"] * 1e-4 * g1 / r; return rh * math.cos(ph), rh * math.sin(ph), e["z_cm"]


def old_resmear(h, sct):                                           # pre-D4 resmear (2026-11-15), SCT only
    sig = {"Z0": 0.0, "Z1160": 0.1160}[sct] * h["g_long"]
    if h["kind"] == "barrel": return h["x"], h["y"], h["long_true"] + sig
    ph = math.atan2(h["y"], h["x"]); r = h["long_true"] + sig; return r * math.cos(ph), r * math.sin(ph), h["z"]


# (a), (b)
N = 40000; ok["a"] = ok["b"] = True; store = {}
for e in (sb, sd):
    pts = [point(e) for _ in range(N)]; g = rng.standard_normal((N, 2)); store[e["name"]] = (pts, g)
    for sct, (sr, sl) in EXPECT.items():
        res = np.array([residuals(e, *p, D.respond(e, *p, 1.0, "t", g[k, 0], g[k, 1], sct)) for k, p in enumerate(pts)]) * 1e4
        s_r, s_l = res.std(axis=0); m_r, m_l = res.mean(axis=0)
        good = abs(s_r / sr - 1) < 0.02 and (abs(s_l / sl - 1) < 0.02 if sl > 0 else s_l < 1e-6) and abs(m_r) < 3 * sr / math.sqrt(N) \
               and abs(m_l) < 3 * max(sl, 1e-9) / math.sqrt(N)
        ok["a"] &= good
        print(f"(a) {e['kind']:6s} {sct:5s}: std r-phi {s_r:7.2f} um (expect {sr:g}), std long {s_l:8.2f} um (expect {sl:g}); means {m_r:+.2f} / {m_l:+.2f} um"
              f" -> {'ok' if good else 'FAIL'}")
        if sct in ("Z0", "Z1160"):
            same = all((lambda h, o: h["x"] == o[0] and h["y"] == o[1] and h["z"] == o[2])(D.respond(e, *p, 1.0, "t", g[k, 0], g[k, 1], sct),
                                                                                        old_response(e, *p, g[k, 0], g[k, 1], sct)) for k, p in enumerate(pts[:5000]))
            ok["b"] &= same; print(f"(b) {e['kind']:6s} {sct:5s}: identical to the pre-D4 formula (5000 hits): {same}")
# (c)
ok["c"] = True
for e in (sb, sd):
    pts, g = store[e["name"]]
    for a_, b_ in itertools.permutations(EXPECT, 2):
        src = [D.respond(e, *p, 1.0, "t", g[k, 0], g[k, 1], a_) for k, p in enumerate(pts[:5000])]
        dst = [D.respond(e, *p, 1.0, "t", g[k, 0], g[k, 1], b_) for k, p in enumerate(pts[:5000])]
        rs = D.resmear(src, b_); d = max(max(abs(u["x"] - v["x"]), abs(u["y"] - v["y"]), abs(u["z"] - v["z"])) for u, v in zip(rs, dst))
        good = d < 1e-12
        if {a_, b_} == {"Z0", "Z1160"}: good &= all(u["x"] == o[0] and u["y"] == o[1] and u["z"] == o[2] for u, o in zip(rs, (old_resmear(h, b_) for h in src)))
        ok["c"] &= good; print(f"(c) {e['kind']:6s} resmear {a_:5s} -> {b_:5s}: max diff to direct {d:.1e} cm -> {'ok' if good else 'FAIL'}")
# (d)
hb = D.respond(sb, *point(sb), 1.0, "a", 0.3, -0.2, "A580"); hd = D.respond(sd, *point(sd), 1.0, "b", 0.1, 0.5, "A580")
m, _ = D.overlay([hb, hd], []); keys = ("rphi_true", "g_rphi", "res_rphi_um", "rphi_factor")
ok["d"] = len(m) == 2 and all(all(k in h for k in keys) for h in m) and all(h["rphi_factor"] == 0.5 for h in m)
print(f"(d) keys survive overlay (barrel + disk SCT): {ok['d']}")
print("T06:", ok); print("T06_PASS" if all(ok.values()) else "T06_FAIL")
