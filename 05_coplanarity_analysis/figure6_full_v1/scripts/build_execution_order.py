"""
Builds/updates ACTUAL_PHASE5_EXECUTION_ORDER.csv from real driver/log state
(not the intended point list). Safe to rerun at any time -- read-only with
respect to the live production driver and its run directories.
"""
import os
import re
import json
import hashlib
import glob

HEP_RUNS = "/home/rafia/hep_tools/figure6_full_v1_runs"
OUT = "/home/rafia/coplanarity_study/05_coplanarity_analysis/figure6_full_v1/metadata/ACTUAL_PHASE5_EXECUTION_ORDER.csv"


def sha256_of(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    rows = []
    dirs = sorted(glob.glob(f"{HEP_RUNS}/*"), key=lambda p: os.path.getmtime(p))
    for i, d in enumerate(dirs):
        tag = os.path.basename(d)
        stats_path = f"{d}/metadata/generation_stats.json"
        done_marker = f"{d}/checkpoints_DONE_generation.txt"
        run_dir = f"{d}/Events/run_fig6"
        log_candidates = sorted(glob.glob(f"{d}/gen_run_fig6_attempt*.log"))
        log_path = log_candidates[-1] if log_candidates else None
        attempt_num = None
        if log_path:
            m = re.search(r"attempt(\d+)", log_path)
            attempt_num = int(m.group(1)) if m else None

        if os.path.exists(stats_path):
            stats = json.load(open(stats_path))
            channel, mass, seed = stats["channel"], stats["mass_gev"], stats["seed"]
            wall_s, exit_code = stats["wall_s"], stats["exit_code"]
            status = "DONE"
        else:
            m = re.match(r"(EW|colored)_(\d+)gev", tag)
            channel, mass = (m.group(1), int(m.group(2))) if m else ("?", None)
            seed, wall_s, exit_code = None, None, None
            status = "IN_PROGRESS" if os.path.isdir(run_dir) or log_path else "UNKNOWN"

        start_ts = None
        if log_path and os.path.exists(log_path):
            start_ts = os.path.getctime(log_path)
        completion_ts = os.path.getmtime(done_marker) if os.path.exists(done_marker) else None

        lhe = f"{d}/Events/run_fig6/unweighted_events.lhe.gz"
        hepmc = f"{d}/Events/run_fig6/tag_1_pythia8_events.hepmc.gz"

        rows.append({
            "execution_index": i,
            "channel": channel, "mass_GeV": mass, "generation_seed": seed,
            "run_name": "run_fig6", "attempt_number": attempt_num,
            "start_timestamp": start_ts, "completion_timestamp": completion_ts,
            "wall_seconds": wall_s, "exit_code": exit_code,
            "authoritative_output_path": run_dir if os.path.isdir(run_dir) else None,
            "log_path": log_path,
            "LHE_path": lhe if os.path.exists(lhe) else None,
            "HepMC_path": hepmc if os.path.exists(hepmc) else None,
            "SHA256": sha256_of(hepmc) if os.path.exists(hepmc) else None,
            "DONE_marker_path": done_marker,
            "DONE_marker_valid": os.path.exists(done_marker),
            "status": status,
            "notes": "" if status == "DONE" else "generation not yet complete at time of this snapshot",
        })

    import csv
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
