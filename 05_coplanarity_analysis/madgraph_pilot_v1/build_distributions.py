"""
Builds distribution source CSVs and plots from the event tables. Also
builds the "comparison with existing samples" -- honestly framed: since
this pilot extracts from the SAME original LHE/HepMC files as the existing
authoritative CSVs (not a freshly-generated independent sample), the
comparison is a DATA-INTEGRITY / reproducibility check (must show perfect
agreement by construction), not an independent statistical validation.
This is stated explicitly, not glossed over.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "/home/rafia/coplanarity_study/05_coplanarity_analysis/madgraph_pilot_v1"
REPO = "/home/rafia/coplanarity_study"

BENCH = {
    "EW": f"{REPO}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv",
    "colored": f"{REPO}/01_signal_generation/quirk_pair_momenta_1800gev_2kev.csv",
}

for name, existing_path in BENCH.items():
    hepmc = pd.read_csv(f"{BASE}/event_tables/{name}_hepmc_events.csv")
    lhe = pd.read_csv(f"{BASE}/event_tables/{name}_lhe_events.csv")
    existing = pd.read_csv(existing_path)

    # --- distributions: quirk1 pT/eta/phi, quirk2 pT/eta/phi, pair pT/mass ---
    dist_vars = ["pt1_gev", "eta1", "phi1", "pt2_gev", "eta2", "phi2",
                 "quirk_pair_pt_gev", "quirk_pair_mass_gev", "weight"]
    fig, axes = plt.subplots(3, 3, figsize=(14, 12))
    for ax, var in zip(axes.flat, dist_vars):
        ax.hist(hepmc[var].dropna(), bins=30, histtype="step")
        ax.set_xlabel(var)
        ax.set_ylabel("events")
    fig.suptitle(f"{name}: generator-level distributions (matched sample, N={len(hepmc)})")
    fig.tight_layout()
    fig.savefig(f"{BASE}/figures/{name}_distributions.png", dpi=130)
    plt.close(fig)

    for var in dist_vars:
        counts, edges = np.histogram(hepmc[var].dropna(), bins=30)
        pd.DataFrame({"bin_lo": edges[:-1], "bin_hi": edges[1:], "count": counts}).to_csv(
            f"{BASE}/distributions/{name}_{var}_source.csv", index=False)

    # --- LHE-level jet-parton pT (process @1 only), matching-scale diagnostics ---
    fig, ax = plt.subplots(figsize=(7, 5))
    jet_pt = lhe.loc[lhe["n_jet_partons_lhe"] > 0, "jet_parton_pt_gev"]
    ax.hist(jet_pt, bins=30, histtype="step", label=f"N(events w/ jet parton)={len(jet_pt)}/{len(lhe)}")
    ax.set_xlabel("LHE jet-parton pT (GeV)")
    ax.set_ylabel("events")
    ax.set_title(f"{name}: parton-level jet pT (process @1 events only)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"{BASE}/figures/{name}_jet_parton_pt.png", dpi=130)
    plt.close(fig)
    counts, edges = np.histogram(jet_pt, bins=30)
    pd.DataFrame({"bin_lo": edges[:-1], "bin_hi": edges[1:], "count": counts}).to_csv(
        f"{BASE}/distributions/{name}_jet_parton_pt_source.csv", index=False)

    # --- matching accept/reject: process_id split (proxy for @0 vs @1) ---
    proc_counts = lhe["process_id"].value_counts().sort_index()
    proc_counts.to_csv(f"{BASE}/distributions/{name}_lhe_process_id_counts.csv")

    # --- comparison with existing authoritative sample (data-integrity check) ---
    n_common = min(len(hepmc), len(existing))
    pt_diff = np.abs(hepmc["quirk_pair_pt_gev"].values[:n_common] - existing["pT_pair"].values[:n_common])
    comparison = {
        "benchmark": name,
        "n_pilot_matched": len(hepmc),
        "n_existing_matched": len(existing),
        "n_common_compared": n_common,
        "max_abs_pT_pair_diff_gev": float(pt_diff.max()),
        "mean_abs_pT_pair_diff_gev": float(pt_diff.mean()),
        "note": "Pilot extracts from the SAME original LHE/HepMC files as the "
                "existing authoritative sample (not an independently generated "
                "new sample) -- this is a DATA-INTEGRITY/reproducibility check, "
                "expected to show exact (0.0) agreement by construction, NOT an "
                "independent statistical cross-check of two different MC runs.",
    }
    pd.DataFrame([comparison]).to_csv(f"{BASE}/distributions/{name}_comparison_with_existing.csv", index=False)
    print(f"{name}: max |pT_pair diff| vs existing = {pt_diff.max():.6e} GeV (n_common={n_common})")

print("Saved all distribution CSVs and figures")
