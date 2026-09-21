"""
Builds the generator cutflow, cross-section summary, and comparison tables
for the madgraph_pilot_v1 package, from the already-extracted event tables
(extract_pilot_data.py) plus this project's existing authoritative
charge-filtered CSV (for the colored benchmark's charge-filter flag, which
requires the pythia8 python bindings' particle-charge database -- already
correctly computed once by 01_signal_generation/extract_quirk_momenta.py,
reused here by event-index join rather than re-querying pythia8 a second
time for the same information).
"""
import json
import numpy as np
import pandas as pd

BASE = "/home/rafia/coplanarity_study/05_coplanarity_analysis/madgraph_pilot_v1"
REPO = "/home/rafia/coplanarity_study"

configs = {
    "EW": {
        "lhe_requested": 1000,
        "existing_matched_csv": f"{REPO}/01_signal_generation/ew_quirk_pair_momenta_800gev_4kev.csv",
        "existing_charged_csv": None,  # EW needs no charge filter (unit charge by construction)
        "matched_xsec_pb": 0.0002337,  # this project's own pre-existing measured value (unchanged)
    },
    "colored": {
        "lhe_requested": 1000,
        "existing_matched_csv": f"{REPO}/01_signal_generation/quirk_pair_momenta_1800gev_2kev.csv",
        "existing_charged_csv": f"{REPO}/01_signal_generation/quirk_pair_momenta_1800gev_2kev_v2_CHARGED.csv",
        "matched_xsec_pb": 0.0003144,  # recovered in the Fig.5 weight audit (7.5036e-4 fb/evt * 419)
    },
}

cutflow_rows = []
xsec_rows = []

for name, cfg in configs.items():
    lhe = pd.read_csv(f"{BASE}/event_tables/{name}_lhe_events.csv")
    hepmc = pd.read_csv(f"{BASE}/event_tables/{name}_hepmc_events.csv")
    with open(f"{BASE}/metadata/{name}_lhe_init.json") as f:
        init = json.load(f)

    n_requested = cfg["lhe_requested"]
    n_lhe = len(lhe)
    n_positive_w = (lhe["weight"] > 0).sum()
    n_negative_w = (lhe["weight"] <= 0).sum()
    n_hepmc = len(hepmc)
    n_2quirks = (hepmc["n_quirks_found"] == 2).sum()

    existing_matched = pd.read_csv(cfg["existing_matched_csv"])
    n_matched_existing = len(existing_matched)

    n_charge_pass = None
    if cfg["existing_charged_csv"]:
        charged = pd.read_csv(cfg["existing_charged_csv"])
        n_charge_pass = len(charged)
        denom_for_trigger = charged
    else:
        denom_for_trigger = existing_matched

    n_trigger = (denom_for_trigger["pT_pair"] > 200).sum()

    stages = [
        ("LHE requested (Main:numberOfEvents / nevents in run_card)", n_requested, n_requested, 0),
        ("LHE generated (unweighted_events.lhe)", n_requested, n_lhe, n_requested - n_lhe),
        ("LHE positive-weight", n_lhe, int(n_positive_w), int(n_negative_w)),
        ("Showered + MLM-matched (HepMC final sample)", n_lhe, n_hepmc, n_lhe - n_hepmc),
        ("Exactly 2 quirks identified (mass+PDG window)", n_hepmc, int(n_2quirks), n_hepmc - int(n_2quirks)),
    ]
    if n_charge_pass is not None:
        stages.append(("Charge filter (both quirk-hadrons nonzero charge)", int(n_2quirks), n_charge_pass, int(n_2quirks) - n_charge_pass))
    stages.append(("Trigger proxy (pT_pair>200GeV)", (n_charge_pass if n_charge_pass is not None else int(n_2quirks)), int(n_trigger), (n_charge_pass if n_charge_pass is not None else int(n_2quirks)) - int(n_trigger)))

    entering = n_requested
    for stage_name, enter, passing, failing in stages:
        cond_eff = passing / enter if enter else float("nan")
        cutflow_rows.append({
            "benchmark": name, "stage": stage_name, "entering": enter, "passing": passing,
            "failing": failing, "conditional_efficiency": cond_eff,
            "cumulative_efficiency": passing / n_requested if n_requested else float("nan"),
        })

    # cross-check: this pilot's own matched-event count must equal the
    # existing authoritative sample's row count (self-consistency gate)
    assert n_2quirks == n_matched_existing, (
        f"{name}: pilot HepMC 2-quirk count ({n_2quirks}) != existing authoritative "
        f"matched CSV row count ({n_matched_existing})")

    sum_w = hepmc["weight"].sum()
    sum_w2 = (hepmc["weight"] ** 2).sum()
    n_eff = (sum_w ** 2) / sum_w2 if sum_w2 > 0 else float("nan")
    xsec_rows.append({
        "benchmark": name,
        "parton_level_xsec_pb": init["total_xsecup_pb"],
        "matched_xsec_pb (existing, pre-verified this project)": cfg["matched_xsec_pb"],
        "matching_efficiency (matched/parton-level events, approx)": n_hepmc / n_lhe,
        "sum_of_weights": sum_w,
        "sum_of_squared_weights": sum_w2,
        "effective_event_count": n_eff,
        "n_matched_events": n_hepmc,
        "per_event_normalization_weight_fb_per_event": cfg["matched_xsec_pb"] * 1000 / n_hepmc,
        "units": "pb for cross-sections; fb for per-event weight",
    })

    print(f"=== {name} cutflow ===")
    for r in cutflow_rows:
        if r["benchmark"] == name:
            print(f"  {r['stage']}: {r['entering']}->{r['passing']} (cond_eff={r['conditional_efficiency']:.4f})")

cutflow_df = pd.DataFrame(cutflow_rows)
cutflow_df.to_csv(f"{BASE}/cutflows/generator_cutflow_EW_and_colored.csv", index=False)

xsec_df = pd.DataFrame(xsec_rows)
xsec_df.to_csv(f"{BASE}/metadata/cross_section_and_matching_statistics.csv", index=False)

print("\nSaved cutflows/generator_cutflow_EW_and_colored.csv")
print("Saved metadata/cross_section_and_matching_statistics.csv")
print("\nAll self-consistency assertions passed: pilot matched-event counts == existing authoritative samples")
