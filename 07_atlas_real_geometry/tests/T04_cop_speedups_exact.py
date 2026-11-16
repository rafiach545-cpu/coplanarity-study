#!/usr/bin/env python3
"""07 test T04 (2026-11-15): the speed-ups in sim/cop07.seeding_and_iterative_fit (vectorised seed pairs, Weyl/KD-tree seed pre-filter with
batched seed fit, vectorised iterative-fit eligibility) must give EXACTLY the candidates of the plain loop version (a line-by-line copy of
coplanarity_fit.seeding_and_iterative_fit with the generalised seed-pair cut, kept below as REFERENCE): same number of candidates, same hits in
the same order, same station labels, Delta_s and Delta_w equal.
Events: atlas configuration, Z(nunu)+gamma conversions at the beam pipe + pile-up (backgrounds/C01 setup), mu = 20 (events 0-11) and
mu = 50 (events 0-3), SCT Z0 and Z1160. Prints T04_PASS / T04_FAIL."""
import os, sys, math, time, argparse, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = f"{HERE}/.."; sys.path.insert(0, f"{ROOT}/sim"); sys.path.insert(0, f"{ROOT}/backgrounds")
sys.argv = [sys.argv[0]]
import C01_conversion_bkg as C, detsim07 as D, cop07, coplanarity_fit as cf


def REFERENCE(hbl, dlong, ds_seed=0.05, dw_seed=1.0, ds_iter=0.05, dw_iter=1.0, growth=3.0, dphi_max=0.1, dlong_max=2.0):
    p8 = [(a, b) for i, a in enumerate(hbl.get(8, [])) for b in hbl.get(8, [])[i + 1:] if cop07._dphi(a, b) < dphi_max and dlong[8](a, b) < dlong_max]
    p7 = [(a, b) for i, a in enumerate(hbl.get(7, [])) for b in hbl.get(7, [])[i + 1:] if cop07._dphi(a, b) < dphi_max and dlong[7](a, b) < dlong_max]
    cands = []
    for q8 in p8:
        for q7 in p7:
            sh = list(q8) + list(q7); fit = cf.fit_plane(np.array(sh))
            if fit["delta_s"] >= ds_seed or fit["delta_w"] >= dw_seed: continue
            if not np.all(np.array(sh) @ fit["n3"] > 0): continue
            cands.append({"hits": sh, "layers": [8, 8, 7, 7], "fit": fit})
    final = []
    for c in cands:
        cur, curl = list(c["hits"]), list(c["layers"])
        for k in range(6, 0, -1):
            fit = cf.fit_plane(np.array(cur)); el = []
            for h in hbl.get(k, []):
                hv = np.array(h)
                if np.dot(hv, fit["n3"]) <= 0 or abs(np.dot(hv, fit["n1"])) >= ds_iter or abs(np.dot(hv, fit["n2"])) >= dw_iter: continue
                el.append((abs(np.dot(hv, fit["n1"])), h))
            el.sort(key=lambda t: t[0])
            for _, h in el:
                tf = cf.fit_plane(np.array(cur + [h]))
                if tf["delta_s"] <= growth * fit["delta_s"] and tf["delta_w"] <= growth * fit["delta_w"]:
                    cur = cur + [h]; curl.append(k); fit = tf
        final.append({"hits": cur, "layers": curl, "fit": cf.fit_plane(np.array(cur))})
    return final


a = argparse.Namespace(geom="atlas", mu=20.0, material=True, sct="both", first=0, workers=1, tag=""); C._init(a)
kind_of = {e["name"]: e["kind"] for e in C.ELS}; ok, n_cmp, n_cand, t_new, t_ref = True, 0, 0, 0.0, 0.0
for mu, events in ((20.0, range(12)), (50.0, range(4))):
    for i in events:
        r = C.PH.iloc[i]; rng = np.random.default_rng(np.random.SeedSequence([99, 1708, i])); z0 = rng.normal(0.0, 4.5)
        regs = C.regions_atlas(r, z0)
        if not regs: continue
        nm, cp, pk, e_conv, L = regs[0]
        c1, c2 = np.random.SeedSequence([C.PU_SEED, i]).spawn(2)
        pu, st = D.pileup_hits(C.ELS, C.POOL, mu, np.random.default_rng(c1), np.random.default_rng(c2), "Z0", eta_max_reco=2.5)
        raw = C.pair_hits(np.array(cp, float), np.array([r.px, r.py, r.pz]), i, None, C.ELS, "Z0"); m0, _ = D.overlay(raw, pu)
        for sct in ("Z0", "Z1160"):
            m = m0 if sct == "Z0" else D.resmear(m0, sct)
            t = time.time(); new, hbl = cop07.reconstruct(m, (0.0, 0.0, z0), C.ELS, kind_of); t_new += time.time() - t
            # the same station grouping and pair cut functions, plain loops
            kind = {}
            for h in m:
                kind[(h["x"], h["y"], h["z"] - z0)] = kind_of[h["layer"]]
            def dl(p, q):
                dz = abs(p[2] - q[2]); dr = abs(math.hypot(p[0], p[1]) - math.hypot(q[0], q[1]))
                kp, kq = kind[p], kind[q]
                return dz if kp == kq == "barrel" else (dr if kp == kq == "disk" else max(dz, dr))
            t = time.time(); ref = REFERENCE(hbl, {k: dl for k in range(1, 9)}); t_ref += time.time() - t
            same = len(new) == len(ref) and all(x["hits"] == y["hits"] and x["layers"] == y["layers"] and x["fit"]["delta_s"] == y["fit"]["delta_s"]
                                                and x["fit"]["delta_w"] == y["fit"]["delta_w"] for x, y in zip(new, ref))
            ok &= same; n_cmp += 1; n_cand += len(ref)
            if not same: print(f"   DIFFERENT: mu {mu} event {i} {sct}: new {len(new)} candidates, reference {len(ref)}")
        print(f"   mu {mu:g} event {i}: hits {len(m0)}, candidates {len(ref)}; time new {t_new:.1f} s, reference {t_ref:.1f} s (cumulative)", flush=True)
print(f"T04: {n_cmp} reconstructions compared, {n_cand} reference candidates; identical: {ok}; time new {t_new:.1f} s vs reference {t_ref:.1f} s")
print("T04_PASS" if ok and n_cand > 0 else "T04_FAIL")
