#!/usr/bin/env python3
"""Recompute the FROZEN (pre-literal) converted-photon cutflows from the stored per-event CSVs, with event IDs.
conversion-only : 02_backgrounds/photon_conversion/conversion_scan_results_v4_FULL_DIAGNOSTICS.csv
conversion+PU50 : 02_backgrounds/photon_conversion/conversion_with_pileup_mu50_v1.csv
Read-only on the frozen files. Output: tables/frozen_background_cutflows.csv (stage, N, weighted pb, IDs)."""
import os, hashlib, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); PC = f"{HERE}/../../../02_backgrounds/photon_conversion"
rows = []
def sha(f): return hashlib.sha256(open(f, "rb").read()).hexdigest()
def flow(name, f, stages):
    d = pd.read_csv(f); assert d.event.is_unique; prev = pd.Series(True, index=d.index)
    rows.append(dict(cutflow=name, stage="generated (MET>200, photon pT>0.5)", n=len(d), weight_pb=d.weight_pb.sum(), ids="all", source=os.path.basename(f), sha256=sha(f)))
    for st, m in stages(d):
        m = prev & m; assert (m <= prev).all(); prev = m
        rows.append(dict(cutflow=name, stage=st, n=int(m.sum()), weight_pb=d.weight_pb[m].sum(),
                         ids=" ".join(map(str, d.event[m])) if m.sum() <= 300 else f"({int(m.sum())} ids, see CSV mask)", source=os.path.basename(f), sha256=sha(f)))
T = lambda s: s.astype(str) == "True"
flow("frozen_conversion_only_v4", f"{PC}/conversion_scan_results_v4_FULL_DIAGNOSTICS.csv", lambda d: [
    ("Sec. III C plane", T(d.sec3c_plane_found)), ("hit multiplicity 7x2+1", T(d.hit_multiplicity_pass)),
    ("dw < 1 cm", d.sec3c_dw < 1), ("ds < 0.01 cm (final)", d.sec3c_ds < 0.01)])
flow("frozen_conversion_plus_pileup_mu50_v1", f"{PC}/conversion_with_pileup_mu50_v1.csv", lambda d: [
    ("Sec. III C plane", T(d.sec3c_plane_found)), ("hit multiplicity 7x2+1", T(d.hit_multiplicity_pass)),
    ("dw < 1 cm", d.sec3c_dw < 1), ("ds < 0.01 cm", T(d.delta_s_pass_0p01)), ("final Sec. IV (stored flag)", T(d.final_sec_iv_pass))])
out = pd.DataFrame(rows); out.to_csv(f"{HERE}/../tables/frozen_background_cutflows.csv", index=False)
print(out[["cutflow", "stage", "n", "weight_pb"]].to_string()); print(out[out.n <= 5][["cutflow", "stage", "ids"]].to_string())
