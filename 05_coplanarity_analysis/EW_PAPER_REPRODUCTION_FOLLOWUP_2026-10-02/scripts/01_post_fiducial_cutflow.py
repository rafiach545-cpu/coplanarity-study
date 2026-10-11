#!/usr/bin/env python3
"""
Conditional cutflow AFTER the fiducial requirement, for both EW samples,
from the project's stored per-event results (read-only).

Project semantics (05_coplanarity_analysis/coplanarity_fit.py, unchanged since
2026-09-15, i.e. before both result files were produced):
  candidates      = seeding_and_iterative_fit(hits)      (Sec III C steps 1-2)
  selected plane  = select_reconstructed_plane(candidates): keep candidates with
                    dw < 1 cm, choose smallest ds         (Sec III C step 3)
  final Sec IV    = selected plane AND hit multiplicity AND ds < 0.01 cm
                    (dw < 1 cm is already guaranteed by the selection)

Stored columns:
  EW2000 per_event_results.csv: n_candidates, sec3c_plane_found, sec3c_ds_cm,
        sec3c_dw_cm, hit_multiplicity_pass (of the selected plane), final_sec_iv_pass
  EW1000 ew_quirk_..._v3_VERTEX_FIXED.csv: n_candidates, seed_found (= n_candidates>0),
        ds/dw (of the selected plane, NaN if none), best_candidate_passes_hit_multiplicity
        (of the selected plane), passes_signal_region
Sequential order requested: plane found -> hit multiplicity -> dw -> ds -> final.
"""
import json
import os
import numpy as np
import pandas as pd

B = "/home/rafia/coplanarity_study/05_coplanarity_analysis"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tables")


def load():
    d = f"{B}/quirk_2000_event_fresh_regeneration_v1"
    te = pd.read_csv(f"{d}/events/EW_800GeV_L4keV/trigger_passing_events.csv")
    te["row_index"] = np.arange(len(te))
    pe = pd.read_csv(f"{d}/reconstruction/EW_800GeV_L4keV/per_event_results.csv")
    e2 = te[["row_index", "hepmc_event_idx"]].merge(pe, on="row_index", validate="1:1")
    e2 = pd.DataFrame(dict(
        sample="EW2000", event_id=e2.hepmc_event_idx.astype(int), row_index=e2.row_index,
        fiducial=e2.truth_fiducial.astype(bool), n_candidates=e2.n_candidates,
        plane_found=e2.sec3c_plane_found.astype(bool), ds=e2.sec3c_ds_cm, dw=e2.sec3c_dw_cm,
        mult=e2.hit_multiplicity_pass.astype(bool), final=e2.final_sec_iv_pass.astype(bool)))
    e1 = pd.read_csv(f"{B}/ew_quirk_800gev_4kev_cutflow_v3_VERTEX_FIXED.csv")
    e1 = pd.DataFrame(dict(
        sample="EW1000", event_id=e1.event.astype(int), row_index=np.arange(len(e1)),
        fiducial=e1.truth_fiducial.astype(bool), n_candidates=e1.n_candidates,
        plane_found=e1.dw.notna() & (e1.dw < 1.0), ds=e1.ds, dw=e1.dw,
        mult=e1.best_candidate_passes_hit_multiplicity.fillna(False).astype(bool),
        final=e1.passes_signal_region.astype(bool),
        seed_found_column=e1.seed_found.astype(bool)))
    return e1, e2


def cutflow(e):
    f = e[e.fiducial].copy()
    f["dw_pass"] = f.dw < 1.0
    f["ds_pass"] = f.ds < 0.01
    steps = [("fiducial", np.ones(len(f), bool)),
             ("raw_candidate_exists (n_candidates>0)", (f.n_candidates.fillna(0) > 0).to_numpy()),
             ("plane_found (Sec IIIC selected, dw<1)", f.plane_found.to_numpy()),
             ("hit_multiplicity", f.mult.to_numpy()),
             ("delta_w < 1 cm", f.dw_pass.to_numpy()),
             ("delta_s < 0.01 cm", f.ds_pass.to_numpy()),
             ("final_SecIV (stored flag)", f.final.to_numpy())]
    rows, alive = [], np.ones(len(f), bool)
    n_fid = len(f)
    prev = n_fid
    for name, m in steps:
        new = alive & m
        lost = f.event_id.to_numpy()[alive & ~m]
        rows.append(dict(sample=e["sample"].iloc[0], step=name, n_pass=int(new.sum()), n_fid=n_fid,
                         frac_of_fid=new.sum() / n_fid, lost_here=int(prev - new.sum()),
                         lost_event_ids=" ".join(map(str, sorted(lost)))))
        alive, prev = new, int(new.sum())
    # closure: recomputed sequential final must equal stored final
    recomputed = f.plane_found & f.mult & f.dw_pass & f.ds_pass
    assert (recomputed == f.final).all(), "closure failure: stored final != plane&mult&dw&ds"
    # non-sequential attribution among plane-found events
    p = f[f.plane_found]
    attrib = dict(
        sample=e["sample"].iloc[0], n_fid=n_fid, n_plane=len(p),
        fail_ds_only=int((~p.ds_pass & p.mult).sum()),
        fail_mult_only=int((p.ds_pass & ~p.mult).sum()),
        fail_both=int((~p.ds_pass & ~p.mult).sum()),
        pass_all=int((p.ds_pass & p.mult).sum()),
        ds_pass_given_plane=int(p.ds_pass.sum()), mult_pass_given_plane=int(p.mult.sum()),
        ids_fail_ds_only=" ".join(map(str, sorted(p.event_id[~p.ds_pass & p.mult]))),
        ids_fail_mult_only=" ".join(map(str, sorted(p.event_id[p.ds_pass & ~p.mult]))),
        ids_fail_both=" ".join(map(str, sorted(p.event_id[~p.ds_pass & ~p.mult]))),
        ds_quantiles_plane=[float(x) for x in p.ds.quantile([0.1, 0.25, 0.5, 0.75, 0.9])],
        dw_max_plane=float(p.dw.max()))
    return pd.DataFrame(rows), attrib, f


def main():
    e1, e2 = load()
    allrows, attribs, per = [], [], []
    for e in (e1, e2):
        r, a, f = cutflow(e)
        allrows.append(r)
        attribs.append(a)
        per.append(f)
    note = {}
    f1 = per[0]
    note["EW1000_seed_found_vs_selected_plane_among_fid"] = dict(
        seed_found=int(f1.seed_found_column.sum()), selected_plane=int(f1.plane_found.sum()))
    df = pd.concat(allrows)
    df.to_csv(f"{OUT}/post_fiducial_cutflow_sequential.csv", index=False)
    pd.DataFrame(attribs).to_csv(f"{OUT}/post_fiducial_failure_attribution.csv", index=False)
    pd.concat(per).to_csv(f"{OUT}/post_fiducial_per_event.csv", index=False)
    json.dump(note, open(f"{OUT}/post_fiducial_notes.json", "w"), indent=2)
    pd.set_option("display.width", 250, "display.max_colwidth", 200)
    print(df.to_string(index=False))
    print(json.dumps(attribs, indent=2))
    print(note)


if __name__ == "__main__":
    main()
