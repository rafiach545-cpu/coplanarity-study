"""
Post-hoc generation-statistics enrichment (Section E). Parses each
already-completed mass point's saved banner/cards/logs -- never touches the
live production driver. Safe to rerun at any time.
"""
import os
import re
import glob
import gzip
import json
import hashlib

HEP_RUNS = "/home/rafia/hep_tools/figure6_full_v1_runs"
OUT_DIR = "/home/rafia/coplanarity_study/05_coplanarity_analysis/figure6_full_v1/TABLES"
META_DIR = "/home/rafia/coplanarity_study/05_coplanarity_analysis/figure6_full_v1/METADATA"


def sha256_of(path):
    if not path or not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_run_card(path):
    text = open(path).read()
    def grab(pattern, cast=float):
        m = re.search(pattern, text)
        return cast(m.group(1)) if m else None
    return {
        "lpp1": grab(r"(\d+)\s*=\s*lpp1", int), "lpp2": grab(r"(\d+)\s*=\s*lpp2", int),
        "ebeam1_gev": grab(r"([\d.]+)\s*=\s*ebeam1"), "ebeam2_gev": grab(r"([\d.]+)\s*=\s*ebeam2"),
        "pdf_set": (re.search(r"(\S+)\s*=\s*pdlabel1", text) or [None, None])[1] if re.search(r"(\S+)\s*=\s*pdlabel1", text) else None,
        "lhaid": grab(r"(\d+)\s*=\s*lhaid", int),
        "ickkw": grab(r"(\d+)\s*=\s*ickkw", int),
        "xqcut": grab(r"([\d.]+)\s*=\s*xqcut"),
    }


def parse_pythia_cmd(path):
    if not os.path.exists(path):
        return {}
    text = open(path).read()
    m = re.search(r"JetMatching:qCut\s*=\s*([\d.]+)", text)
    qcut = float(m.group(1)) if m else None
    m2 = re.search(r"JetMatching:nJetMax\s*=\s*(\d+)", text)
    njetmax = int(m2.group(1)) if m2 else None
    return {"qCut": qcut, "nJetMax": njetmax}


def parse_banner_versions(path):
    if not os.path.exists(path):
        return {}
    text = open(path).read()
    mg = re.search(r"VERSION\s+([\d.]+)", text)
    py8 = re.search(r"<pythia8_git_hash>", text)  # presence check only, version parsed separately below
    return {"madgraph_version": mg.group(1) if mg else None}


def parse_pythia_log_version(path):
    if not os.path.exists(path):
        return None
    text = open(path).read()
    m = re.search(r"PYTHIA\s+version\s+([\d.]+)", text, re.IGNORECASE)
    if not m:
        m = re.search(r"Pythia\s+([\d.]+)\s*:\s*Program\s+is\s+starting", text, re.IGNORECASE)
    return m.group(1) if m else None


def count_lhe_events_and_weights(lhe_path):
    """Returns (n_events, sum_w, sum_w2, n_negative_weight)."""
    if not os.path.exists(lhe_path):
        return None, None, None, None
    n, sw, sw2, nneg = 0, 0.0, 0.0, 0
    with gzip.open(lhe_path, "rt") as f:
        in_event = False
        first_line_of_event = False
        for line in f:
            if line.strip() == "<event>":
                in_event = True
                first_line_of_event = True
                continue
            if in_event and first_line_of_event:
                parts = line.split()
                if len(parts) >= 3:
                    w = float(parts[2])
                    n += 1
                    sw += w
                    sw2 += w * w
                    if w < 0:
                        nneg += 1
                first_line_of_event = False
            if line.strip() == "</event>":
                in_event = False
    return n, sw, sw2, nneg


def enrich_one_point(run_dir):
    tag = os.path.basename(run_dir)
    stats_path = f"{run_dir}/metadata/generation_stats.json"
    if not os.path.exists(stats_path):
        return None
    stats = json.load(open(stats_path))

    run_card = parse_run_card(f"{run_dir}/Cards/run_card.dat")
    events_dir = f"{run_dir}/Events/run_fig6"
    pycmd = parse_pythia_cmd(f"{events_dir}/tag_1_pythia8.cmd")
    banner_path = glob.glob(f"{events_dir}/*banner*.txt")
    banner_info = parse_banner_versions(banner_path[0]) if banner_path else {}
    pythia_version = parse_pythia_log_version(f"{events_dir}/tag_1_pythia8.log")

    lhe_path = f"{events_dir}/unweighted_events.lhe.gz"
    n_lhe, sum_w, sum_w2, n_neg = count_lhe_events_and_weights(lhe_path)
    n_eff = (sum_w ** 2 / sum_w2) if (sum_w2 and sum_w2 > 0) else None

    hashes = {
        "banner_sha256": sha256_of(banner_path[0]) if banner_path else None,
        "run_card_sha256": sha256_of(f"{run_dir}/Cards/run_card.dat"),
        "param_card_sha256": sha256_of(f"{run_dir}/Cards/param_card.dat"),
        "proc_card_sha256": sha256_of(f"{run_dir}/Cards/proc_card_mg5.dat"),
        "pythia_cmd_sha256": sha256_of(f"{events_dir}/tag_1_pythia8.cmd"),
        "lhe_sha256": sha256_of(lhe_path),
        "hepmc_sha256": sha256_of(f"{events_dir}/tag_1_pythia8_events.hepmc.gz"),
    }

    row = dict(stats)
    row.update({
        "N_requested": stats["n_generated"],  # what run_card actually requested
        "N_generated_LHE": n_lhe,
        "matching_efficiency": (stats["n_matched"] / n_lhe) if n_lhe else None,
        "sum_weights": sum_w, "sum_weights_squared": sum_w2,
        "effective_event_count": n_eff, "negative_weight_count": n_neg,
        "duplicate_event_count": "NOT SEPARATELY CHECKED (LHE event IDs not verified unique this pass)",
        "malformed_event_count": "NOT SEPARATELY TRACKED (MadGraph reports overall success/failure only)",
        "madgraph_version": banner_info.get("madgraph_version"),
        "pythia8_version": pythia_version,
        "pdf_set": run_card.get("pdf_set"), "lhaid": run_card.get("lhaid"),
        "collider_energy_gev": (run_card.get("ebeam1_gev") or 0) + (run_card.get("ebeam2_gev") or 0),
        "xqcut": run_card.get("xqcut"), "qCut": pycmd.get("qCut"), "nJetMax": pycmd.get("nJetMax"),
        **hashes,
    })
    return row


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(META_DIR, exist_ok=True)
    rows = []
    for run_dir in sorted(glob.glob(f"{HEP_RUNS}/*")):
        r = enrich_one_point(run_dir)
        if r:
            rows.append(r)
    if not rows:
        print("No completed generation points yet.")
        return
    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUT_DIR}/generation_statistics_13_mass_points.csv", index=False)
    print(f"Wrote {len(df)} rows to TABLES/generation_statistics_13_mass_points.csv")

    validation = {
        "n_points_enriched": len(df),
        "all_exit_code_0": bool((df["exit_code"] == 0).all()),
        "requested_vs_generated_match": bool((df["N_requested"] == df["N_generated_LHE"]).all()) if "N_generated_LHE" in df else None,
        "any_negative_weights": bool((df["negative_weight_count"].fillna(0) > 0).any()) if "negative_weight_count" in df else None,
        "matching_efficiency_range": [float(df["matching_efficiency"].min()), float(df["matching_efficiency"].max())] if "matching_efficiency" in df else None,
    }
    with open(f"{META_DIR}/generation_validation_13_mass_points.json", "w") as f:
        json.dump(validation, f, indent=2)
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
