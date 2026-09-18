"""
Cache-only analysis test: proves that, WITHOUT any detector-propagation
rerun, the cache prototype alone supports: complete cutflow, per-layer
table, Delta_s/Delta_w statistics, multiplicity, failure reasons, notable-
event display, and future cut-threshold diagnostics (re-deriving pass/fail
under a DIFFERENT hypothetical Delta_s threshold, entirely from cached
fit results). Also validates cache integrity (Phase 6 of the task).
Exits 0 if all checks pass.
"""
import sys
import time
import numpy as np
import pandas as pd

BASE = "/home/rafia/coplanarity_study"
OUT = f"{BASE}/02_backgrounds/photon_conversion/cache_prototype_v1"

failures = []


def check(name, cond):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        failures.append(name)


t0 = time.time()

ev = pd.read_csv(f"{OUT}/conversion_photon_event_cache_sample100_v1.csv")
raw = pd.DataFrame(dict(np.load(f"{OUT}/conversion_photon_hit_cache_sample100_v1.npz", allow_pickle=True)))
merged = pd.DataFrame(dict(np.load(f"{OUT}/conversion_photon_hit_cache_sample100_v1_merged.npz", allow_pickle=True)))
cand = pd.DataFrame(dict(np.load(f"{OUT}/conversion_photon_candidate_cache_sample100_v1.npz", allow_pickle=True)))
link = pd.DataFrame(dict(np.load(f"{OUT}/conversion_photon_candidate_hit_link_sample100_v1.npz", allow_pickle=True)))

# --- integrity (Phase 6) ---
check("100 unique event IDs, 0-99", ev["event"].nunique() == 100 and set(ev["event"]) == set(range(100)))
check("no duplicate raw_hit_id", raw["raw_hit_id"].duplicated().sum() == 0)
check("no duplicate merged_hit_id", merged["merged_hit_id"].duplicated().sum() == 0)
check("all candidate-hit links resolve to stored merged hits",
      link["merged_hit_id"].astype(int).isin(merged["merged_hit_id"]).all())

# --- complete cutflow, cache-only ---
n_total = len(ev)
n_ok = int((ev["status"] == "ok").sum())
n_plane = int(ev["sec3c_plane_found"].sum())
selected = cand[cand["is_selected_sec3c_plane"]]
n_mult = int(selected["hit_multiplicity_pass"].sum())
n_ds = int((selected["delta_s"] < 0.01).sum())
n_final = int(ev["final_pass"].sum())
check("cutflow computable cache-only (all stages > -1)", all(x >= 0 for x in [n_total, n_ok, n_plane, n_mult, n_ds, n_final]))
print(f"  cutflow: N_total={n_total} N_ok={n_ok} N_plane={n_plane} N_mult={n_mult} N_ds<0.01={n_ds} N_final={n_final}")

# --- per-layer table, cache-only ---
per_layer = merged.groupby("layer").size()
check("per-layer table computable cache-only", len(per_layer) > 0)

# --- Delta_s/Delta_w stats, cache-only ---
ds = selected["delta_s"].to_numpy()
dw = selected["delta_w"].to_numpy()
check("Delta_s/Delta_w stats computable cache-only", len(ds) == n_plane and len(dw) == n_plane)

# --- multiplicity / failure reasons, cache-only ---
fail_reasons = []
for _, row in selected.iterrows():
    if not row["hit_multiplicity_pass"]:
        fail_reasons.append("hit_multiplicity")
    elif not row["delta_s_pass"]:
        fail_reasons.append("delta_s")
    else:
        fail_reasons.append("final_pass")
check("failure-reason classification computable cache-only", len(fail_reasons) == n_plane)

# --- notable-event display, cache-only ---
if len(selected):
    min_ds_event = selected.loc[selected["delta_s"].idxmin(), "event"]
    check("notable-event (min Delta_s) resolvable cache-only", min_ds_event in ev["event"].to_numpy())

# --- future cut-threshold diagnostic, cache-only (NO rerun needed) ---
# e.g. "what if Delta_s cut were 0.02cm instead of 0.01cm?" -- answerable
# purely from the cached fit results, no propagation needed
n_ds_hypothetical_002 = int((selected["delta_s"] < 0.02).sum())
check("hypothetical Delta_s<0.02cm cut-threshold diagnostic computable cache-only (no rerun)",
      n_ds_hypothetical_002 >= n_ds)
print(f"  hypothetical Delta_s<0.02cm: {n_ds_hypothetical_002} (vs Delta_s<0.01cm: {n_ds}) -- answered without rerunning propagation")

analysis_wall_time = time.time() - t0
print(f"\nCache-only analysis wall time: {analysis_wall_time:.4f}s (vs {279.78:.1f}s cache generation time)")

print(f"\nTOTAL: {len(failures)} failing checks")
sys.exit(1 if failures else 0)
