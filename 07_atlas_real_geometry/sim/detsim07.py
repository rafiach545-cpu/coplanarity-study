#!/usr/bin/env python3
"""07 detector simulation (2026-11-15): charged-particle propagation, hit response and pile-up overlay for the ATLAS Run 2 silicon geometry
(barrel layers + pixel disks + SCT rings, geometry/atlas_run2_id_geometry.csv), with material from geometry/atlas_run2_id_material.csv.

Two configurations (CFG):
  "stage2"  barrel only: the 8 Stage 1/2 layers with their names (L1_IBL ... L8_SCT_B6), Ref. [27] lengths, the Stage 1/2 material table
            (05_.../tables/material_X0_per_layer_ref27.csv). Used ONLY to validate this module against the Stage 2 code (tests T02-T05).
  "atlas"   barrel + end-caps, 07 material (IBL 1.88% R2; pixel 10.7%/3 R3; SCT 2.96% R3; SCT disk 3.75% R3; pixel disk = pixel barrel, INFERRED).
Common modelling (unchanged from Stages 1-2 unless stated): uniform B = 2 T along z; infinitely thin elements; effective resolution as
arXiv:1708.02243 Sec. III A (pixel: quantised to the pitch; SCT: Gaussian 2 x 17 um = 34 um in r-phi, long direction sigma_long = 0 (Z0) or
1160 um (Z1160); added in D4: A580 = ATLAS intrinsic 17 um / 580 um); pixel neighbour merging; 25 ns time-of-flight cut per hit.
End-cap response (new): pixel disks quantised in r (pitch 400 um) and in r-phi (50 um at the quantised r); SCT rings Gaussian in r-phi (34 um)
and in r (sigma_long), z = the ring's |z|. Disk pixel merging: neighbouring (r, r-phi) indices, mean r, circular mean phi.
Electron material effects (as Stage 2 P17_conversion_ref34.track34 = Ref. [34] App. A): after each hit, bremsstrahlung E -> E exp(-t_eff) and
most-probable ionisation 0.28 MeV per mm Si-equivalent, t_eff = t / |cos(incidence)| (barrel: radial normal, disk: z normal); stop below 10% of the
mass in kinetic energy; no multiple scattering.
Units: cm, GeV, ns."""
import os, sys, math, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = f"{HERE}/.."; BASE = "/home/rafia/coplanarity_study"
SCR = f"{BASE}/05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/scripts"
for p in (SCR, f"{BASE}/04_detector_sim", f"{BASE}/05_coplanarity_analysis", f"{BASE}/02_backgrounds/pileup", f"{BASE}/02_backgrounds/photon_conversion"):
    if p not in sys.path: sys.path.insert(0, p)
import atlas_geometry as ag                                            # noqa: E402  (Stage 1/2 layer definitions)
from trajectory_to_hits import quantize_pixel, merge_neighboring_pixel_hits   # noqa: E402
from pileup_hits import overlay_and_merge, BEAMSPOT_SIGMA_Z_CM          # noqa: E402
from track_suppression import suppress_tracks                           # noqa: E402
from tracking_efficiency import BASELINE_SELECTION                      # noqa: E402

CL = 29.9792458; ME = 0.000511; B_T = 2.0; TCUT = 25.0
SI_X0_MM, DEDX_MP_GEV_PER_MM = 93.7, 0.28e-3                            # as P17_conversion_ref34 (Ref. [34] App. A)
STAGE2_HALF = {"L1_IBL": 33.015, "L2_PixelB0": 40.05, "L3_PixelB1": 40.05, "L4_PixelB2": 40.05,
               "L5_SCT_B3": 74.9, "L6_SCT_B4": 74.9, "L7_SCT_B5": 74.9, "L8_SCT_B6": 74.9}
# SCT settings (D4): r-phi sigma = res_rphi_um (34 um = 2 x 17, R10 Sec. III A) x SCT_RPHI_FACTOR; long direction (barrel z, disk R) = SCT_LONG_CM.
#   Z0: 34 um / 0 (upper bound); Z1160: 34 um / 1160 um (Knapen, 2 x intrinsic); A580: 17 um / 580 um (ATLAS intrinsic, R3 Table 4.1, R1 Table 1).
SCT_LONG_CM = {"Z0": 0.0, "Z1160": 0.1160, "A580": 0.0580}
SCT_RPHI_FACTOR = {"Z0": 1.0, "Z1160": 1.0, "A580": 0.5}
ATLAS_NAME = {"IBL": "L1_IBL", "PIX1": "L2_PixelB0", "PIX2": "L3_PixelB1", "PIX3": "L4_PixelB2",
              "SCT1": "L5_SCT_B3", "SCT2": "L6_SCT_B4", "SCT3": "L7_SCT_B5", "SCT4": "L8_SCT_B6"}   # barrel names kept = Stage 2 names


def _stage2_material():
    m = pd.read_csv(f"{BASE}/05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/tables/material_X0_per_layer_ref27.csv"); X = {}
    for r in m.itertuples():
        for nm in (r.layer_names if isinstance(r.layer_names, str) else "").split(): X[nm] = float(r.per_layer_X0_normal_incidence)
    return X


def build(cfg):
    """List of element dicts (cm). Barrel: kind 'barrel', r_cm, half_cm. Disk: kind 'disk', z_cm, rmin_cm, rmax_cm. Plus det, pitch, x0."""
    els = []
    if cfg == "stage2":
        X = _stage2_material()
        for L in ag.LAYERS:
            els.append(dict(name=L["name"], kind="barrel", det="pixel" if L["is_pixel"] else "sct", is_pixel=L["is_pixel"], r_cm=L["r_cm"],
                            half_cm=STAGE2_HALF[L["name"]], pitch_rphi_um=L["eff_res_rphi_um"], pitch_long_um=L["eff_res_z_um"],
                            res_rphi_um=L["eff_res_rphi_um"], x0=X[L["name"]], layer_r_cm=L["r_cm"]))
        return els
    assert cfg == "atlas"
    g = pd.read_csv(f"{ROOT}/geometry/atlas_run2_id_geometry.csv"); M = pd.read_csv(f"{ROOT}/geometry/atlas_run2_id_material.csv").set_index("component")
    X = lambda c: float(M.loc[c, "x_over_X0_normal_incidence"])
    pix_l, sct_l, sct_d, ibl = X("pixel_barrel_3layers_total") / 3, X("sct_barrel_layer"), X("sct_endcap_disk"), X("IBL_staves")
    pitch = {"IBL": (50, 250)}; L2 = {L["name"]: L for L in ag.LAYERS}
    for r in g[g.region == "barrel"].itertuples():
        nm = ATLAS_NAME[r.name]; pix = r.element == "pixel"; L = L2[nm]
        els.append(dict(name=nm, kind="barrel", det=r.element, is_pixel=pix, r_cm=r.r_mm / 10, half_cm=r.half_z_mm / 10,
                        pitch_rphi_um=L["eff_res_rphi_um"], pitch_long_um=L["eff_res_z_um"], res_rphi_um=L["eff_res_rphi_um"],
                        x0=ibl if r.name == "IBL" else (pix_l if pix else sct_l), layer_r_cm=r.r_mm / 10))
    for r in g[g.region.isin(["endcap", "endcap_ring"])].itertuples():
        pix = r.element == "pixel"; dz = float(r.ring_dz_mm) if pd.notna(r.ring_dz_mm) else 0.0
        # SCT disk material (3.75% per disk, R3) is assigned per ring crossing; a crossing of two overlapping rings of one disk counts it twice
        # (overestimate in the ring-overlap band only; documented).
        for side in (1, -1):
            els.append(dict(name=f"{r.name}_{'A' if side > 0 else 'C'}", kind="disk", det=r.element, is_pixel=pix, z_cm=side * (r.z_mm + dz) / 10,
                            rmin_cm=r.r_min_mm / 10, rmax_cm=r.r_max_mm / 10, pitch_rphi_um=50 if pix else None, pitch_long_um=400 if pix else None,
                            res_rphi_um=50 if pix else 34.0, x0=pix_l if pix else sct_d, layer_r_cm=None))
    return els


# ---------------------------------------------------------------- helix (uniform Bz), same convention as P16_conversion_material.next_crossing
RC_EXACT = 100.0 / (0.299792458 * B_T)                                  # cm per GeV of pT: R[m] = pT / (0.299792458 B[T])
RC_STAGE2_PU = 1.973269804e-14 / (0.30282212 * B_T * 1.9535e-16)        # the constant of helix_propagation.py (Stage 1/2 pile-up), 1.2e-5 larger


def _helix(x, p, q, rc=RC_EXACT):
    pT = math.hypot(p[0], p[1]); Rc = pT * rc; s = -q; ux, uy = p[0] / pT, p[1] / pT
    C = (x[0] - Rc * uy / s, x[1] + Rc * ux / s); v0 = (Rc * uy / s, -Rc * ux / s)      # centre and centre->start vector
    return pT, Rc, s, ux, uy, C, v0


def _pos(x, p, h, a):
    pT, Rc, s, ux, uy, C, v0 = h; sa, ca = math.sin(s * a), math.cos(s * a)
    X = x[0] + Rc * (ux * sa - uy * (1 - ca)) / s; Y = x[1] + Rc * (ux * (1 - ca) + uy * sa) / s; Z = x[2] + Rc * a * p[2] / pT
    th = s * a; pn = np.array([pT * (ux * math.cos(th) - uy * math.sin(th)), pT * (ux * math.sin(th) + uy * math.cos(th)), p[2]])
    return np.array([X, Y, Z]), pn


def _cyl_angles(h, rho, amax, eps=1e-9):
    """All turning angles a in (eps, amax] at which the helix circle meets radius rho (ascending)."""
    pT, Rc, s, ux, uy, C, v0 = h; d = math.hypot(*C)
    if d < 1e-12: return []
    c = (rho * rho - d * d - Rc * Rc) / (2 * Rc * d)
    if c < -1 or c > 1: return []
    phC, phv0 = math.atan2(C[1], C[0]), math.atan2(v0[1], v0[0]); da = math.acos(c); out = []
    for phv in (phC + da, phC - da):
        a = ((phv - phv0) * s) % (2 * math.pi)
        while a <= amax:
            if a > eps: out.append(a)
            a += 2 * math.pi
    return sorted(out)


def next_crossing(x, p, q, els, last=None, amax=None):
    """Earliest element crossing along the helix from x (excluding an immediate re-crossing of `last`). Returns (el, pos, p_new, path_cm) or None."""
    h = _helix(x, p, q); pT, Rc = h[0], h[1]; k = math.sqrt(1 + (p[2] / pT) ** 2)
    amax = amax if amax is not None else (TCUT * CL * 1.0001) / (Rc * k)              # path cannot exceed c * 25 ns
    best = None
    for e in els:
        if e["kind"] == "barrel":
            for a in _cyl_angles(h, e["r_cm"], amax):
                if e is last and a < 1e-7: continue
                if best is not None and a >= best[0]: break
                pos, pn = _pos(x, p, h, a)
                if abs(pos[2]) < e["half_cm"]: best = (a, e, pos, pn); break
        else:
            if p[2] == 0: continue
            a = (e["z_cm"] - x[2]) * pT / (Rc * p[2])
            if a <= 1e-9 or a > amax or (best is not None and a >= best[0]) or (e is last and a < 1e-7): continue
            pos, pn = _pos(x, p, h, a); r = math.hypot(pos[0], pos[1])
            if e["rmin_cm"] <= r <= e["rmax_cm"]: best = (a, e, pos, pn)
    if best is None: return None
    a, e, pos, pn = best
    return e, pos, pn, Rc * a * k


def propagate(x0, p0, q, m, els, material=True, max_hits=60):
    """Sequential crossings of a charged particle: [(el, x, y, z, t_ns)], with the electron material effects after each hit if material."""
    out, x, p, tns, last = [], np.array(x0, float), np.array(p0, float), 0.0, None
    for _ in range(max_hits):
        r = next_crossing(x, p, q, els, last)
        if r is None: break
        e, x, pn, path = r; pm = math.sqrt(pn @ pn); E = math.sqrt(pm * pm + m * m); tns += path / (CL * pm / E)
        if tns > TCUT: break
        out.append((e, x[0], x[1], x[2], tns)); p = pn; last = e
        if material:
            nrm = np.array([x[0], x[1], 0.0]) / math.hypot(x[0], x[1]) if e["kind"] == "barrel" else np.array([0.0, 0.0, 1.0])
            cosi = max(abs(p @ nrm) / pm, 1e-3); te = e["x0"] / cosi
            Ek = E * math.exp(-te) - DEDX_MP_GEV_PER_MM * te * SI_X0_MM
            if Ek - m < 0.1 * m: break
            p = p * math.sqrt(max(Ek * Ek - m * m, 0.0)) / pm
    return out


def propagate_stage2(x0, p0, q, m, els, material=True):
    """Exact replica of the Stage 2 electron propagation (P17_conversion_ref34.track34): the elements are visited in list order and for each
    the first OUTWARD crossing of its radius within one turn is taken, with no active-length condition (acceptance is applied later to the
    hit, as in Stage 2); material after every crossing; stop if a radius is not reached, t > 25 ns or E_kin < 10% m."""
    out, x, p, tns = [], np.array(x0, float), np.array(p0, float), 0.0
    for e in els:
        h = _helix(x, p, q); aa = _cyl_angles(h, e["r_cm"], 2 * math.pi)
        if not aa: break
        a = aa[0]; pT, Rc = h[0], h[1]; pos, pn = _pos(x, p, h, a); path = Rc * a * math.sqrt(1 + (p[2] / pT) ** 2)
        if math.hypot(x[0], x[1]) < e["r_cm"] and not _outward(h, a): break
        x = pos; pm = math.sqrt(pn @ pn); E = math.sqrt(pm * pm + m * m); tns += path / (CL * pm / E)
        if tns > TCUT: break
        out.append((e, x[0], x[1], x[2], tns)); p = pn
        if material:
            rhat = np.array([x[0], x[1], 0.0]) / math.hypot(x[0], x[1]); cosi = max(abs(p @ rhat) / pm, 1e-3); te = e["x0"] / cosi
            Ek = E * math.exp(-te) - DEDX_MP_GEV_PER_MM * te * SI_X0_MM
            if Ek - m < 0.1 * m: break
            p = p * math.sqrt(max(Ek * Ek - m * m, 0.0)) / pm
    return out


def _outward(h, a):
    """True if the radius increases at turning angle a (d r^2 / da > 0)."""
    pT, Rc, s, ux, uy, C, v0 = h; ang = math.atan2(v0[1], v0[0]) + s * a
    vx, vy = Rc * math.cos(ang), Rc * math.sin(ang); X, Y = C[0] + vx, C[1] + vy
    return (X * (-vy) + Y * vx) * s > 0


def first_crossings(x0, p0, q, m, els, rc=RC_EXACT):
    """Pile-up response (as Stage 2 pileup_particle_hits, no material): for every element its FIRST crossing (barrel: first meeting of the
    radius inside |z| < half, which from the vertex is outward; disk: the single z crossing inside [rmin, rmax]). Returns {name: (pos, t_ns)}."""
    p = np.array(p0, float); pT = math.hypot(p[0], p[1]); res = {}
    if q == 0 or pT < 1e-9: return res
    h = _helix(x0, p, q, rc); Rc = h[1]; k = math.sqrt(1 + (p[2] / pT) ** 2); pm = math.sqrt(p @ p); v = pm / math.sqrt(pm * pm + m * m)
    for e in els:
        if e["kind"] == "barrel":
            aa = _cyl_angles(h, e["r_cm"], 4 * math.pi)
            if not aa: continue
            a = aa[0]; pos, _ = _pos(x0, p, h, a)                   # first meeting of the radius (Stage 2: no |z| retry on later turns)
            if abs(pos[2]) >= e["half_cm"]: continue                # active length (Stage 2: literal_detector.accepted, geometry B)
        else:
            if p[2] == 0: continue
            a = (e["z_cm"] - x0[2]) * pT / (Rc * p[2])
            if a <= 1e-9: continue
            pos, _ = _pos(x0, p, h, a)
            if not (e["rmin_cm"] <= math.hypot(pos[0], pos[1]) <= e["rmax_cm"]): continue
        res[e["name"]] = (pos, Rc * a * k / (CL * v))
    return res


# ---------------------------------------------------------------- hit response
def respond(e, x, y, z, t, tag, g_rphi, g_long, sct):
    """One raw hit dict. g_rphi, g_long: standard normals (used for SCT only)."""
    phi = math.atan2(y, x)
    if e["kind"] == "barrel":
        R = e["r_cm"]; rphi = R * phi
        if e["is_pixel"]: rh, zh, ir, iz = quantize_pixel(rphi, z, e["pitch_rphi_um"], e["pitch_long_um"])
        else: rh, zh, ir, iz = rphi + e["res_rphi_um"] * SCT_RPHI_FACTOR[sct] * 1e-4 * g_rphi, z + SCT_LONG_CM[sct] * g_long, None, None
        ph = rh / R
        return {"layer": e["name"], "layer_r_cm": R, "quirk_index": tag, "t_ns": t, "x": R * math.cos(ph), "y": R * math.sin(ph), "z": zh,
                "is_pixel": e["is_pixel"], "idx_rphi": ir, "idx_z": iz, "kind": "barrel", "long_true": z, "g_long": g_long,
                "rphi_true": rphi, "g_rphi": g_rphi, "res_rphi_um": e["res_rphi_um"], "rphi_factor": SCT_RPHI_FACTOR[sct]}
    r = math.hypot(x, y)
    if e["is_pixel"]:
        # pixel grid on a disk: radial pitch 400 um; azimuthal pitch fixed in angle, 50 um at the disk's mean radius (r_ref), so that radially
        # neighbouring pixels share the phi index (a module's r-phi pitch is constant along the module, not proportional to r). Approximation:
        # the true r-phi pitch is 50 um everywhere; here it is 50 um * r / r_ref (37-63 um on 88.8-149.6 mm).
        pr = e["pitch_long_um"] * 1e-4; dph = e["pitch_rphi_um"] * 1e-4 / (0.5 * (e["rmin_cm"] + e["rmax_cm"]))
        ir_ = int(round(r / pr)); rq = ir_ * pr; ip = int(round(phi / dph)); ph = ip * dph; rh = rq; idx = (ip, ir_)
    else:
        rh = r + SCT_LONG_CM[sct] * g_long; ph = phi + e["res_rphi_um"] * SCT_RPHI_FACTOR[sct] * 1e-4 * g_rphi / r; idx = (None, None)
    return {"layer": e["name"], "layer_r_cm": None, "quirk_index": tag, "t_ns": t, "x": rh * math.cos(ph), "y": rh * math.sin(ph), "z": e["z_cm"],
            "is_pixel": e["is_pixel"], "idx_rphi": idx[0], "idx_z": idx[1], "kind": "disk", "long_true": r, "g_long": g_long,
            "rphi_true": phi, "g_rphi": g_rphi, "res_rphi_um": e["res_rphi_um"], "rphi_factor": SCT_RPHI_FACTOR[sct]}


def resmear(hits, sct):
    """Same hits with the SCT smearing of setting `sct` (common random numbers: the stored standard normals g_long, g_rphi are reused).
    Pixel hits are unchanged. Barrel: z = z_true + sigma_long g_long; disk: r = r_true + sigma_long g_long.
    r-phi: kept as it is when the setting has the same r-phi factor (Z0 <-> Z1160, bit for bit as before D4); otherwise recomputed from the
    true r-phi exactly as respond() does (barrel rphi_true + sigma g_rphi; disk phi_true + sigma g_rphi / r_true)."""
    out = []
    for h in hits:
        if h["is_pixel"]: out.append(h); continue
        sig = SCT_LONG_CM[sct] * h["g_long"]; f = SCT_RPHI_FACTOR[sct]; same = f == h["rphi_factor"]
        if h["kind"] == "barrel":
            if same: out.append({**h, "z": h["long_true"] + sig}); continue
            R = h["layer_r_cm"]; ph = (h["rphi_true"] + h["res_rphi_um"] * f * 1e-4 * h["g_rphi"]) / R
            out.append({**h, "z": h["long_true"] + sig, "x": R * math.cos(ph), "y": R * math.sin(ph), "rphi_factor": f})
        else:
            ph = math.atan2(h["y"], h["x"]) if same else h["rphi_true"] + h["res_rphi_um"] * f * 1e-4 * h["g_rphi"] / h["long_true"]
            r = h["long_true"] + sig; out.append({**h, "x": r * math.cos(ph), "y": r * math.sin(ph), "rphi_factor": f})
    return out


def _merge_disk_pixels(hits):
    """Neighbour merging on a pixel disk: connected components of hits with |d idx_phi| <= 1 and |d idx_r| <= 1 (same element)."""
    from collections import defaultdict
    by = defaultdict(list); out = []
    for h in hits: by[h["layer"]].append(h)
    for nm, hs in by.items():
        n = len(hs); adj = [[] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if abs(hs[i]["idx_rphi"] - hs[j]["idx_rphi"]) <= 1 and abs(hs[i]["idx_z"] - hs[j]["idx_z"]) <= 1: adj[i].append(j); adj[j].append(i)
        seen = [False] * n
        for i in range(n):
            if seen[i]: continue
            st, comp = [i], []; seen[i] = True
            while st:
                k = st.pop(); comp.append(k)
                for b in adj[k]:
                    if not seen[b]: seen[b] = True; st.append(b)
            cl = [hs[k] for k in comp]; rr = np.mean([math.hypot(c["x"], c["y"]) for c in cl])
            ph = math.atan2(np.mean([c["y"] / math.hypot(c["x"], c["y"]) for c in cl]), np.mean([c["x"] / math.hypot(c["x"], c["y"]) for c in cl]))
            src = sorted(set(c["quirk_index"] for c in cl), key=str)
            out.append({**cl[0], "x": rr * math.cos(ph), "y": rr * math.sin(ph), "t_ns": min(c["t_ns"] for c in cl), "merged_count": len(cl),
                        "source_quirk_indices": src, "quirk_index": cl[0]["quirk_index"] if len(src) == 1 else None})
    return out


def overlay(raw_hard, raw_pu):
    """Single merge pass over hard + pile-up hits. Barrel hits: the frozen Stage 2 overlay_and_merge (identical call in the stage2 config);
    disk pixel hits: _merge_disk_pixels; disk SCT hits pass through (as barrel SCT)."""
    hb = [h for h in raw_hard if h.get("kind", "barrel") == "barrel"]; pb = [h for h in raw_pu if h.get("kind", "barrel") == "barrel"]
    merged, st = overlay_and_merge(hb, pb)
    disk = [h for h in raw_hard + raw_pu if h.get("kind") == "disk"]
    if disk:
        merged = merged + _merge_disk_pixels([h for h in disk if h["is_pixel"]]) + \
                 [{**h, "merged_count": 1, "source_quirk_indices": [h["quirk_index"]]} for h in disk if not h["is_pixel"]]
    return merged, st


# ---------------------------------------------------------------- pile-up (copy of pileup_hits_suppressed.sample_pileup_hits_suppressed,
# same RNG order: Poisson(mu), choice of pool events, per interaction z0, per particle the SCT normals in element order; then suppress_tracks)
def pileup_hits(els, pool_index, mu, rng_pu, rng_sup, sct, eta_max_reco=None, selection=BASELINE_SELECTION, rc=RC_EXACT):
    n_pu = rng_pu.poisson(mu); ids = np.fromiter(pool_index.keys(), dtype=np.int64); raw, kin, lab = {}, {}, {}
    if n_pu > 0 and len(ids) > 0:
        for pu_idx, ev in enumerate(rng_pu.choice(ids, size=n_pu, replace=True)):
            z0 = rng_pu.normal(0.0, BEAMSPOT_SIGMA_Z_CM); v = np.array([0.0, 0.0, z0])
            px, py, pz, m, q, labl = pool_index[ev]
            for j in range(len(px)):
                tag = f"pu{pu_idx}_ev{ev}_p{j}"; cr = first_crossings(v, (px[j], py[j], pz[j]), q[j], m[j], els, rc); hits = []
                for e in els:
                    c = cr.get(e["name"])
                    if c is None or c[1] > TCUT: continue
                    if e["is_pixel"]: hits.append(respond(e, *c[0], c[1], tag, 0.0, 0.0, sct))
                    else: g1 = rng_pu.normal(0.0, 1.0); g2 = rng_pu.normal(0.0, 1.0); hits.append(respond(e, *c[0], c[1], tag, g1, g2, sct))
                if hits:
                    raw[tag] = hits; kin[tag] = float(math.hypot(px[j], py[j]))
                    eta = math.asinh(pz[j] / max(math.hypot(px[j], py[j]), 1e-12))
                    lab[tag] = str(labl[j]) if (eta_max_reco is None or abs(eta) < eta_max_reco) else "secondary"   # outside |eta| < 2.5: never reconstructed
    un, sst = suppress_tracks(raw, kin, lab, rng_sup, selection=selection)
    return un, dict(n_pu_interactions=int(n_pu), **sst)
