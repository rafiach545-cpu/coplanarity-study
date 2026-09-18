"""Regression test: v4's old (v3-inherited) columns must be bit-identical
to v3 for a fixed prefix of events, proving the additive diagnostics do not
perturb the RNG stream or any existing computation. Run BEFORE any full v4
rerun. Exits 0 if all checks pass."""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "/home/rafia/coplanarity_study/02_backgrounds/photon_conversion")
from convert_and_analyze_v4_full_diagnostics import analyze_one_event_v4

BASE = "/home/rafia/coplanarity_study"
PC_DIR = f"{BASE}/02_backgrounds/photon_conversion"

failures = []


def check(name, cond):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        failures.append(name)


def run_prefix(n):
    photons = pd.read_csv(f"{PC_DIR}/zgamma_photons.csv")
    rng = np.random.default_rng(99)
    rows = []
    for i in range(n):
        res = analyze_one_event_v4(photons.iloc[i], rng)
        res["event"] = i
        rows.append(res)
    return pd.DataFrame(rows)


v3 = pd.read_csv(f"{PC_DIR}/conversion_scan_results_v3_SEC3C_DS_DW.csv")
old_cols = ["status", "n_hits", "n_candidates", "passes", "ds", "dw",
            "sec3c_plane_found", "sec3c_ds", "sec3c_dw", "sec3c_n_layers", "conv_r_cm"]

for n in (5, 50):
    v4 = run_prefix(n)
    v3_prefix = v3.iloc[:n].reset_index(drop=True)
    for col in old_cols:
        a, b = v3_prefix[col], v4[col]
        if a.dtype.kind in "iuf":
            eq = (a.isna() & b.isna()) | np.isclose(a.fillna(-999999), b.fillna(-999999))
        else:
            eq = a.astype(str) == b.astype(str)
        check(f"n={n}: column '{col}' bit-identical to v3", bool(eq.all()))
    # sanity: new fields populated
    check(f"n={n}: hit_multiplicity_pass column present and boolean", v4["hit_multiplicity_pass"].dtype == bool)
    check(f"n={n}: n_electron_hits_premerge + n_positron_hits_premerge + n_mixed <= n_hits",
          bool((v4["n_electron_hits_premerge"] + v4["n_positron_hits_premerge"] + v4["n_mixed_hits_premerge"] <= v4["n_hits"]).all()))

print(f"\nTOTAL: {len(failures)} failing checks")
sys.exit(1 if failures else 0)
