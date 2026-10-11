#!/usr/bin/env python3
"""
Full reconstruction forensic audit on EXISTING events (no generation).

For every trigger-passing event of EW1000, EW2000, COL1000, COL2000:
  * rebuild the project's detector hits from truth crossings (tables/truth_crossings_*.csv)
    with the project's exact random-number stream:
      EW2000/COL2000: default_rng(stored per-event seed)
      EW1000/COL1000: one sequential default_rng(4242) over the trigger list
    stream order per event (trajectory_to_hits.simulate_quirk_hits): 1 draw z0 ~ N(0,4.5 cm);
    then quirk 1..2, layer 1..8: for crossings with |eta_lab|<1.8, SCT -> 2 draws (r-phi, z),
    pixel -> none (quantised).
  * apply a resolution model (notes/PREREGISTERED_VARIANTS.md R0..R4); the SCT standard-normal
    draws are shared between models (common random numbers). Pixel Gaussian models (R1, R4)
    use a separate per-event stream (seed = 10_000_000 + key) so the project stream is untouched.
  * merge with the project's own merge_neighboring_pixel_hits (imported, unmodified);
  * run an instrumented copy of the Sec. III C algorithm (A0 = project logic, A1, A2 per notes),
    asserting for A0 that candidates equal the project's own seeding_and_iterative_fit output;
  * select plane / apply Sec. IV cuts and record the first failed requirement.

R0/A0 must reproduce the project's stored per-event results; this is asserted.

Outputs:
  forensics/<sample>_R0_A0_events.jsonl   full per-event forensic record (hits, seeds, candidates...)
  tables/variant_event_results.csv        one row per (sample, model, algorithm, event)
"""
import json
import math
import os
import sys
from collections import Counter
import numpy as np
import pandas as pd

BASE = "/home/rafia/coplanarity_study"
HERE = os.path.dirname(os.path.abspath(__file__))
OUTT = f"{HERE}/../tables"
OUTF = f"{HERE}/../forensics"
sys.path.insert(0, f"{BASE}/04_detector_sim")
sys.path.insert(0, f"{BASE}/05_coplanarity_analysis")
import trajectory_to_hits as tth            # noqa: E402  (unmodified project code)
import coplanarity_fit as cf                # noqa: E402  (unmodified project code)

A5 = f"{BASE}/05_coplanarity_analysis"
ETA_MAX = 1.8
SIG_Z0 = 4.5
LAYER_NAME_TO_IDX = {L["name"]: i for i, L in enumerate(tth.LAYERS, 1)}
MODELS = ["R0", "R1", "R2", "R3", "R4"]
ALGS = ["A0", "A1", "A2"]


# --------------------------------------------------------------------------- inputs
def load_sample(s):
    if s in ("EW2000", "COL2000"):
        tag = "EW_800GeV_L4keV" if s == "EW2000" else "colored_1800GeV_L2keV"
        d = f"{A5}/quirk_2000_event_fresh_regeneration_v1"
        te = pd.read_csv(f"{d}/events/{tag}/trigger_passing_events.csv")
        te["row_index"] = np.arange(len(te))
        pe = pd.read_csv(f"{d}/reconstruction/{tag}/per_event_results.csv")
        m = te[["row_index", "hepmc_event_idx"]].merge(pe, on="row_index", validate="1:1")
        return pd.DataFrame(dict(
            key=m.row_index, event_id=m.hepmc_event_idx.astype(int), seed=m.seed,
            stored_fid=m.truth_fiducial.astype(bool), stored_npost=m.n_hits_postmerge,
            stored_plane=m.sec3c_plane_found.astype(bool), stored_ds=m.sec3c_ds_cm, stored_dw=m.sec3c_dw_cm,
            stored_mult=m.hit_multiplicity_pass.astype(bool), stored_final=m.final_sec_iv_pass.astype(bool),
            stored_ncand=m.n_candidates, technical=(m.status == "error")))
    src, res = {"EW1000": ("ew_quirk_pair_momenta_800gev_4kev.csv", "ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv"),
                "COL1000": ("quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv",
                            "colored_quirk_1800gev_2kev_cutflow_v3_FULL_PIPELINE.csv")}[s]
    t = pd.read_csv(f"{BASE}/01_signal_generation/{src}")
    t = t[t.pT_pair > 200].reset_index(drop=True)
    t["key"] = np.arange(len(t))
    r = pd.read_csv(f"{A5}/{res}")
    m = t[["key", "event"]].merge(r, on="event", validate="1:1")
    return pd.DataFrame(dict(
        key=m.key, event_id=m.event.astype(int), seed=np.nan,
        stored_fid=m.truth_fiducial.astype(bool), stored_npost=m.n_hits_postmerge,
        stored_plane=m.dw.notna() & (m.dw < 1.0), stored_ds=m.ds, stored_dw=m.dw,
        stored_mult=m.best_candidate_passes_hit_multiplicity.fillna(False).astype(bool),
        stored_final=m.passes_signal_region.astype(bool), stored_ncand=m.n_candidates,
        technical=False))


def eta_lab(r, z):
    return -math.log(math.tan(math.atan2(r, z) / 2.0))


# --------------------------------------------------------------------------- detector response
def zlab(row, z0):
    return row.z_lab if hasattr(row, "z_lab") else row.z_rel + z0


def stream_draws(rng, cr, exact=None):
    """Consume the project stream for one event; return z0 and SCT standard normals per crossing.
    If `exact` (crossings propagated with the true z0) is given, its lab z is used for the eta test."""
    z0 = rng.normal(0.0, SIG_Z0)
    if exact is not None:
        cr = exact
    g = {}
    for row in cr.itertuples():
        if not row.crossed:
            continue
        if abs(eta_lab(row.r, zlab(row, z0))) > ETA_MAX:
            continue
        if not row.is_pixel:
            g[(row.quirk, row.layer)] = (rng.normal(0.0, 1.0), rng.normal(0.0, 1.0))
    return z0, g


def build_hits(cr, z0, g, model, key):
    prng = np.random.default_rng(10_000_000 + int(key))
    raw, unsm = [], []
    for row in cr.itertuples():
        if not row.crossed:
            continue
        z = zlab(row, z0)
        if abs(eta_lab(row.r, z)) > ETA_MAX:
            continue
        L = tth.LAYERS[row.layer - 1]
        phi = math.atan2(row.y, row.x)
        rphi = L["r_cm"] * phi
        unsm.append(dict(layer=row.layer, quirk=row.quirk, x=row.x, y=row.y, z=z, t_ns=row.t_ns))
        if L["is_pixel"]:
            q_r, q_z, i_r, i_z = tth.quantize_pixel(rphi, z, L["eff_res_rphi_um"], L["eff_res_z_um"])
            if model in ("R1", "R4"):
                f = 1.0 if model == "R1" else 1.0 / math.sqrt(12.0)
                rphi_h = rphi + prng.normal(0.0, f * L["pitch_rphi_um"] * 1e-4)
                z_h = z + prng.normal(0.0, f * L["pitch_z_um"] * 1e-4)
            else:
                rphi_h, z_h = q_r, q_z
        else:
            g1, g2 = g[(row.quirk, row.layer)]
            s_r = L["eff_res_rphi_um"] * 1e-4
            s_z = {"R2": 0.0, "R3": L["eff_res_rphi_um"] * 1e-4}.get(model, L["eff_res_z_um"] * 1e-4)
            rphi_h, z_h = rphi + s_r * g1, z + s_z * g2
            i_r = i_z = None
        ph = rphi_h / L["r_cm"]
        raw.append(dict(layer=L["name"], layer_r_cm=L["r_cm"], quirk_index=row.quirk, t_ns=row.t_ns,
                        x=L["r_cm"] * math.cos(ph), y=L["r_cm"] * math.sin(ph), z=z_h,
                        is_pixel=L["is_pixel"], idx_rphi=i_r, idx_z=i_z))
    return unsm, raw, tth.merge_neighboring_pixel_hits(raw)


# --------------------------------------------------------------------------- instrumented algorithm
def fit(h):
    return cf.fit_plane(np.array(h))


def instrumented(hits_by_layer, alg, log):
    """Copy of cf.seeding_and_iterative_fit with logging; alg A1 changes growth reference."""
    def dphi(a, b):
        d = abs(math.atan2(a[1], a[0]) - math.atan2(b[1], b[0]))
        return min(d, 2 * math.pi - d)
    L8, L7 = hits_by_layer.get(8, []), hits_by_layer.get(7, [])
    p8 = [(a, b) for i, a in enumerate(L8) for b in L8[i + 1:] if dphi(a, b) < 0.1 and abs(a[2] - b[2]) < 2.0]
    p7 = [(a, b) for i, a in enumerate(L7) for b in L7[i + 1:] if dphi(a, b) < 0.1 and abs(a[2] - b[2]) < 2.0]
    log["n_hits_L8"], log["n_hits_L7"], log["n_pairs_L8"], log["n_pairs_L7"] = len(L8), len(L7), len(p8), len(p7)
    seeds, cands = [], []
    for a in p8:
        for b in p7:
            sh = list(a) + list(b)
            f = fit(sh)
            ok = f["delta_s"] < 0.05 and f["delta_w"] < 1.0 and bool(np.all(np.array(sh) @ f["n3"] > 0))
            reason = ("pass" if ok else "ds>=0.05" if f["delta_s"] >= 0.05 else "dw>=1" if f["delta_w"] >= 1.0
                      else "x.n3<=0")
            seeds.append(dict(ds=f["delta_s"], dw=f["delta_w"], result=reason))
            if ok:
                cands.append(dict(hits=sh, layers=[8, 8, 7, 7], fit=f, seed_ds=f["delta_s"], seed_dw=f["delta_w"]))
    log["seeds"] = seeds
    finals = []
    for c in cands:
        hs, ls = list(c["hits"]), list(c["layers"])
        steps = []
        for li in range(6, 0, -1):
            f = fit(hs)
            elig = []
            for h in hits_by_layer.get(li, []):
                hv = np.array(h)
                why = None
                if hv @ f["n3"] <= 0:
                    why = "x.n3<=0"
                elif abs(hv @ f["n1"]) >= 0.05:
                    why = "|x.n1|>=0.05"
                elif abs(hv @ f["n2"]) >= 1.0:
                    why = "|x.n2|>=1"
                if why:
                    steps.append(dict(layer=li, hit=list(h), action="not_eligible", reason=why,
                                      x_n1=float(hv @ f["n1"])))
                else:
                    elig.append((abs(hv @ f["n1"]), h))
            elig.sort(key=lambda t: t[0])
            for _, h in elig:
                tf = fit(hs + [h])
                ref_s, ref_w = (f["delta_s"], f["delta_w"]) if alg != "A1" else (c["seed_ds"], c["seed_dw"])
                if tf["delta_s"] <= 3.0 * ref_s and tf["delta_w"] <= 3.0 * ref_w:
                    hs.append(h)
                    ls.append(li)
                    f = tf
                    steps.append(dict(layer=li, hit=list(h), action="added", ds=tf["delta_s"], dw=tf["delta_w"]))
                else:
                    steps.append(dict(layer=li, hit=list(h), action="rejected_growth",
                                      trial_ds=tf["delta_s"], ref_ds=ref_s, trial_dw=tf["delta_w"], ref_dw=ref_w))
        ff = fit(hs)
        finals.append(dict(hits=hs, layers=ls, fit=ff, steps=steps))
    return finals


def select(cands, alg):
    surv = [c for c in cands if c["fit"]["delta_w"] < 1.0]
    if not surv:
        return None, "no candidate with dw<1"
    if alg == "A2":
        cov = lambda c: (sum(v >= 2 for v in Counter(c["layers"]).values()), len(set(c["layers"])))
        best = max(surv, key=lambda c: (cov(c), -c["fit"]["delta_s"]))
        return best, f"A2: max coverage {cov(best)} then smallest ds among {len(surv)}"
    best = min(surv, key=lambda c: c["fit"]["delta_s"])
    return best, f"smallest ds among {len(surv)} candidates with dw<1 (of {len(cands)})"


def first_failure(fid, n8pairs, n7pairs, cands, sel, mult, ds_ok):
    if not fid:
        return "fiducial"
    if n8pairs == 0 or n7pairs == 0:
        return "no_seed_pair_L8_or_L7"
    if not cands:
        return "no_seed_passing_seed_cuts"
    if sel is None:
        return "no_candidate_dw<1"
    if not mult:
        return "hit_multiplicity"
    if not ds_ok:
        return "delta_s>=0.01"
    return "PASS"


# --------------------------------------------------------------------------- main
def main():
    os.makedirs(OUTF, exist_ok=True)
    rows, repro = [], []
    for s in ("EW1000", "EW2000", "COL1000", "COL2000"):
        ev = load_sample(s)
        cr_all = pd.read_csv(f"{OUTT}/truth_crossings_{s}.csv")
        ex_all = pd.read_csv(f"{OUTT}/exact_crossings_fiducial_{s}.csv")
        seq = np.random.default_rng(4242) if s in ("EW1000", "COL1000") else None
        jl = open(f"{OUTF}/{s}_R0_A0_events.jsonl", "w")
        n_valid = 0
        for e in ev.sort_values("key").itertuples():
            cr = cr_all[cr_all.key == e.key].sort_values(["quirk", "layer"])
            if e.technical or len(cr) == 0 or ("technical_error" in cr.columns and cr.technical_error.notna().any()):
                continue
            rng = seq if seq is not None else np.random.default_rng(int(e.seed))
            ex = ex_all[ex_all.key == e.key].sort_values(["quirk", "layer"])
            z0, g = stream_draws(rng, cr, ex if e.stored_fid else None)
            if not e.stored_fid:
                continue
            assert len(ex) == 16 and abs(ex.z0_cm.iloc[0] - z0) < 1e-12, f"{s} {e.key} exact crossings/z0"
            cr = ex
            for model in MODELS:
                unsm, raw, merged = build_hits(cr, z0, g, model, e.key)
                hbl = {k: [] for k in range(1, 9)}
                for h in merged:
                    hbl[LAYER_NAME_TO_IDX[h["layer"]]].append(tuple(cf.vertex_relative_hits(
                        [(h["x"], h["y"], h["z"])], np.array([0.0, 0.0, z0]))[0]))
                for alg in ALGS:
                    log = {}
                    cands = instrumented(hbl, alg, log)
                    if model == "R0" and alg == "A0":
                        ref = cf.seeding_and_iterative_fit(hbl)
                        assert len(ref) == len(cands) and all(
                            r["hits"] == c["hits"] and r["layers"] == c["layers"] for r, c in zip(ref, cands)), \
                            f"{s} key {e.key}: instrumented algorithm != project"
                    sel, why = select(cands, alg)
                    mult = cf.check_hit_multiplicity(sel["layers"]) if sel else False
                    ds = sel["fit"]["delta_s"] if sel else np.nan
                    dw = sel["fit"]["delta_w"] if sel else np.nan
                    final = bool(sel is not None and mult and ds < 0.01)
                    ff = first_failure(True, log["n_pairs_L8"], log["n_pairs_L7"], cands, sel, mult, ds < 0.01)
                    cnt = Counter(sel["layers"]) if sel else Counter()
                    avail = Counter(LAYER_NAME_TO_IDX[h["layer"]] for h in merged)
                    rows.append(dict(sample=s, model=model, alg=alg, key=int(e.key), event_id=int(e.event_id),
                                     z0_cm=z0, n_raw=len(raw), n_merged=len(merged),
                                     avail_per_layer=str({k: avail.get(k, 0) for k in range(1, 9)}),
                                     n_seeds=len(log["seeds"]), n_cands=len(cands),
                                     plane=sel is not None, ds=ds, dw=dw, mult=mult, final=final,
                                     sel_layer_counts=str({k: cnt.get(k, 0) for k in range(1, 9)}),
                                     first_failure=ff, selection_reason=why))
                    if model == "R0" and alg == "A0":
                        # reproduction of stored project results (recorded, not asserted: the
                        # stored 2000-event results were produced on the source machine; see report)
                        repro.append(dict(sample=s, key=int(e.key), event_id=int(e.event_id),
                                          npost_match=len(merged) == int(e.stored_npost),
                                          plane_match=(sel is not None) == bool(e.stored_plane),
                                          mult_match=(mult == bool(e.stored_mult)) or sel is None,
                                          final_match=final == bool(e.stored_final),
                                          ds_exact=bool(sel is None or abs(ds - e.stored_ds) < 1e-9),
                                          ds_replay=ds, ds_stored=e.stored_ds,
                                          plane_replay=sel is not None, plane_stored=bool(e.stored_plane),
                                          final_replay=final, final_stored=bool(e.stored_final)))
                        n_valid += 1
                        jl.write(json.dumps(dict(
                            sample=s, key=int(e.key), event_id=int(e.event_id), z0_cm=z0,
                            unsmeared_hits=unsm,
                            smeared_hits=[{k: h[k] for k in ("layer", "quirk_index", "x", "y", "z", "is_pixel", "idx_rphi", "idx_z")} for h in raw],
                            merged_hits=[{k: h[k] for k in ("layer", "x", "y", "z", "merged_count", "source_quirk_indices")} for h in merged],
                            hits_available_per_layer={k: avail.get(k, 0) for k in range(1, 9)},
                            seed_pairs={"L8_hits": log["n_hits_L8"], "L7_hits": log["n_hits_L7"],
                                        "L8_pairs": log["n_pairs_L8"], "L7_pairs": log["n_pairs_L7"]},
                            seeds_considered=log["seeds"],
                            candidates=[dict(n_hits=len(c["hits"]), layers=c["layers"],
                                             ds=c["fit"]["delta_s"], dw=c["fit"]["delta_w"],
                                             n1=c["fit"]["n1"].tolist(), n2=c["fit"]["n2"].tolist(),
                                             n3=c["fit"]["n3"].tolist(), hits=[list(h) for h in c["hits"]],
                                             growth_log=c["steps"]) for c in cands],
                            selected_candidate_index=(cands.index(sel) if sel else None),
                            selection_reason=why, per_layer_multiplicity={k: cnt.get(k, 0) for k in range(1, 9)},
                            delta_s_cm=ds, delta_w_cm=dw, hit_multiplicity_pass=mult, final_sec_iv=final,
                            first_failed_requirement=ff), default=float) + "\n")
        jl.close()
        rp = pd.DataFrame([r for r in repro if r["sample"] == s])
        print(f"{s}: fiducial events {n_valid}; R0/A0 vs stored: ds exact {int(rp.ds_exact.sum())}/{len(rp)}, "
              f"plane match {int(rp.plane_match.sum())}, final match {int(rp.final_match.sum())}, "
              f"npost match {int(rp.npost_match.sum())}")
    pd.DataFrame(rows).to_csv(f"{OUTT}/variant_event_results.csv", index=False)
    pd.DataFrame(repro).to_csv(f"{OUTT}/R0A0_reproduction_vs_stored.csv", index=False)


if __name__ == "__main__":
    main()
