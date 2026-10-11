#!/usr/bin/env python3
"""
Task 3: why do fiducial events fail the Sec. IV hit-multiplicity requirement?

Events: every trigger AND fiducial (finite barrel, geometry B) event of the six samples in
TABLE_I_FINAL_REPRODUCTION_2026-10-02 (same job list, same per-event seeds -> identical hits).
Algorithm: the instrumented copy of the paper's Sec. III C algorithm (forensic pipeline
`instrumented`, asserted identical to the project's coplanarity_fit for alg A0).
For each event and SCT model (Z0 = no z smearing, Z1160 = 2 x 580 um) the failing layers of the
SELECTED candidate are classified, in this priority order:
  merged       : < 2 merged hits exist in that layer (true pixel merging; acceptance is complete
                 for fiducial events by construction, all 16 crossings accepted)
  window_n1    : a hit existed but |x.n1| >= 0.05 cm at that step (association window, out of plane)
  window_n2    : a hit existed but |x.n2| >= 1 cm (association window, in-plane width)
  direction    : x.n3 <= 0
  growth_rule  : eligible hit rejected by the x3 Delta_s / Delta_w growth rule after refit
  near_threshold flag: the deciding quantity within 1% of its threshold (numerical tolerance)
Event-level tests:
  other_candidate_passes : some other Delta_w<1 candidate satisfies multiplicity (ranking/selection)
  truth_hits_pass        : the same algorithm on unsmeared, unquantised, unmerged crossings passes
"""
import importlib.util, json, math, os, sys, multiprocessing as mp
from collections import Counter
import numpy as np, pandas as pd

BASE = "/home/rafia/coplanarity_study"
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
FIN = f"{BASE}/05_coplanarity_analysis/TABLE_I_FINAL_REPRODUCTION_2026-10-02"
FOR = f"{BASE}/05_coplanarity_analysis/PAPER_TABLE_I_REPRODUCTION_FORENSICS_2026-10-02"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m


fc = load("fc", f"{FIN}/scripts/02_final_full_chain.py")
fp = load("fp", f"{FOR}/scripts/02_forensic_pipeline.py")
HALF = fc.HALF


def hits_for(cr, g, z0, model, truth=False):
    import trajectory_to_hits as tth
    raw = []
    for q, L, x, y, z, t in cr:
        lay = tth.LAYERS[L - 1]
        if truth:
            raw.append(dict(layer=lay["name"], layer_r_cm=lay["r_cm"], quirk_index=q, t_ns=t, x=x, y=y, z=z,
                            is_pixel=False, idx_rphi=None, idx_z=None)); continue
        rphi = lay["r_cm"] * math.atan2(y, x)
        if lay["is_pixel"]:
            rh, zh, ir, iz = tth.quantize_pixel(rphi, z, lay["eff_res_rphi_um"], lay["eff_res_z_um"])
        else:
            g1, g2 = g[q - 1, L - 5]; sr = lay["eff_res_rphi_um"] * 1e-4
            sz = {"Z0": 0.0, "Z1160": lay["eff_res_z_um"] * 1e-4}[model]
            rh, zh, ir, iz = rphi + sr * g1, z + sz * g2, None, None
        ph = rh / lay["r_cm"]
        raw.append(dict(layer=lay["name"], layer_r_cm=lay["r_cm"], quirk_index=q, t_ns=t, x=lay["r_cm"] * math.cos(ph),
                        y=lay["r_cm"] * math.sin(ph), z=zh, is_pixel=lay["is_pixel"], idx_rphi=ir, idx_z=iz))
    merged = raw if truth else tth.merge_neighboring_pixel_hits(raw)
    idx = {Ly["name"]: i for i, Ly in enumerate(tth.LAYERS, 1)}
    hbl = {k: [] for k in range(1, 9)}
    for h in merged:
        hbl[idx[h["layer"]]].append((h["x"], h["y"], h["z"] - z0))
    return hbl


def classify(hbl, cf):
    log = {}
    cands = fp.instrumented(hbl, "A0", log)
    ref = cf.seeding_and_iterative_fit(hbl)
    assert len(ref) == len(cands) and all(r["hits"] == c["hits"] for r, c in zip(ref, cands))
    surv = [c for c in cands if c["fit"]["delta_w"] < 1.0]
    sel = min(surv, key=lambda c: c["fit"]["delta_s"]) if surv else None
    if sel is None:
        return dict(plane=False, mult=False, reasons={}, other_pass=False, n_cands=len(cands))
    mult = cf.check_hit_multiplicity(sel["layers"])
    cnt = Counter(sel["layers"])
    reasons, near = {}, False
    if not mult:
        for L in range(1, 9):
            if cnt.get(L, 0) >= 2:
                continue
            avail = len(hbl.get(L, []))
            if avail < 2:
                reasons[L] = "merged"; continue
            steps = [s for s in sel["steps"] if s["layer"] == L and s["action"] != "added"]
            why = []
            for s in steps:
                if s["action"] == "not_eligible":
                    why.append({"|x.n1|>=0.05": "window_n1", "|x.n2|>=1": "window_n2", "x.n3<=0": "direction"}[s["reason"]])
                    if s["reason"] == "|x.n1|>=0.05" and abs(abs(s["x_n1"]) - 0.05) < 0.0005:
                        near = True
                else:
                    why.append("growth_rule")
                    if abs(s["trial_ds"] - 3 * s["ref_ds"]) < 0.01 * 3 * s["ref_ds"] or abs(s["trial_dw"] - 3 * s["ref_dw"]) < 0.01 * 3 * s["ref_dw"]:
                        near = True
            reasons[L] = why[0] if why else "seed_layer"
    other = any(cf.check_hit_multiplicity(c["layers"]) for c in surv if c is not sel)
    return dict(plane=True, mult=bool(mult), reasons=reasons, other_pass=bool(other), near=near, n_cands=len(cands))


def work(a):
    fc._init()
    import coplanarity_fit as cf
    meta, res = fc.propagate(a)
    if res is None:
        return None
    cr, g = res
    if not all(c is not None for c in cr):
        return None
    if not (all(abs(c[4]) < HALF[c[1]] for c in cr) and max(c[5] for c in cr) < 25.0):
        return None                                          # not fiducial in geometry B
    out = dict(sid=meta["sid"], key=meta["key"], bench=meta["bench"])
    for model in ("Z0", "Z1160"):
        r = classify(hits_for(cr, g, meta["z0"], model), cf)
        out.update({f"{model}_{k}": (json.dumps(v) if isinstance(v, dict) else v) for k, v in r.items()})
    t = classify(hits_for(cr, g, meta["z0"], "Z0", truth=True), cf)
    out.update(truth_plane=t["plane"], truth_mult=t["mult"], truth_reasons=json.dumps(t["reasons"]))
    return out


def main():
    J, trig, info = fc.jobs()
    with mp.Pool(10) as pool:
        rows = [r for r in pool.imap_unordered(work, J, chunksize=2) if r]
    d = pd.DataFrame(rows); d.to_csv(f"{T}/multiplicity_forensics_per_event.csv", index=False)
    summ = []
    for b in ("EW", "COL"):
        x = d[d.bench == b]
        for m in ("Z0", "Z1160"):
            pl = x[x[f"{m}_plane"] == True]; fail = pl[pl[f"{m}_mult"] == False]
            lay = Counter(); ev = Counter()
            for r in fail[f"{m}_reasons"]:
                rr = json.loads(r); lay.update(rr.values())
                ev[("merged-only" if set(rr.values()) == {"merged"} else "+".join(sorted(set(rr.values()))))] += 1
            summ.append(dict(bench=b, sct=m, n_fid=len(x), n_plane=len(pl), n_mult_fail=len(fail),
                             failing_layer_reasons=dict(lay), event_reason_combos=dict(ev),
                             other_candidate_would_pass=int(fail[f"{m}_other_pass"].sum()),
                             near_threshold_events=int(fail[f"{m}_near"].fillna(False).sum()),
                             truth_hits_pass_mult_among_fails=int(fail.truth_mult.sum())))
        summ.append(dict(bench=b, sct="TRUTH hits (no quantisation/smearing/merging)", n_fid=len(x),
                         n_plane=int(x.truth_plane.sum()), n_mult_fail=int((x.truth_plane & ~x.truth_mult).sum()),
                         failing_layer_reasons=dict(Counter(v for r in x[x.truth_plane & ~x.truth_mult].truth_reasons for v in json.loads(r).values()))))
    s = pd.DataFrame(summ); s.to_csv(f"{T}/multiplicity_forensics_summary.csv", index=False)
    pd.set_option("display.width", 250, "display.max_colwidth", 120); print(s.to_string(index=False))


if __name__ == "__main__":
    main()
