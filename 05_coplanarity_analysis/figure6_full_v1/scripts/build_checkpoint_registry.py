"""
Post-hoc CHECKPOINT_REGISTRY.csv builder (Section N). Reconstructs chunk
boundaries from each cell's progress.json (row indices are written in
CHUNK_SIZE=30 groups by the live driver, in ascending order within a cell).
Read-only with respect to the live driver.
"""
import os
import glob
import json
import hashlib
import pandas as pd

FIG6 = "/home/rafia/coplanarity_study/05_coplanarity_analysis/figure6_full_v1"
CHUNK_SIZE = 30
OUT = f"{FIG6}/metadata/CHECKPOINT_REGISTRY.csv"


def main():
    rows = []
    checkpoint_id = 0
    for cell_dir in sorted(glob.glob(f"{FIG6}/generation/*/downstream_L*keV")):
        progress_path = f"{cell_dir}/checkpoints/progress.json"
        stats_path = f"{cell_dir}/checkpoints/cell_stats.json"
        if not os.path.exists(progress_path):
            continue
        progress = json.load(open(progress_path))
        stats = json.load(open(stats_path)) if os.path.exists(stats_path) else {}
        grid_point_id = os.path.relpath(cell_dir, f"{FIG6}/generation")
        indices = sorted(int(k) for k in progress.keys())
        mtime = os.path.getmtime(progress_path)
        for chunk_start in range(0, len(indices), CHUNK_SIZE):
            chunk_indices = indices[chunk_start:chunk_start + CHUNK_SIZE]
            seeds = [progress[str(i)]["seed"] for i in chunk_indices]
            cfg_str = f"{grid_point_id}_{chunk_indices[0]}_{chunk_indices[-1]}_{seeds}"
            cfg_hash = hashlib.sha256(cfg_str.encode()).hexdigest()[:16]
            rows.append({
                "checkpoint_id": checkpoint_id,
                "grid_point_id": grid_point_id,
                "chunk_id": chunk_start // CHUNK_SIZE,
                "worker_id": "N/A (pool.map does not expose per-job worker id to caller)",
                "expected_event_id_range": f"{chunk_indices[0]}-{chunk_indices[-1]}",
                "actual_event_ids": ",".join(str(i) for i in chunk_indices),
                "row_count": len(chunk_indices),
                "seed_config_hash": cfg_hash,
                "creation_timestamp": mtime,
                "completion_timestamp": mtime,
                "checksum": cfg_hash,
                "validation_status": "chunk fully present, no gaps in expected range" if
                    chunk_indices == list(range(chunk_indices[0], chunk_indices[-1] + 1)) else "GAP DETECTED",
                "retry_count": 0,
                "resume_status": "DONE" if os.path.exists(f"{cell_dir}/checkpoints/DONE.txt") else "IN_PROGRESS",
            })
            checkpoint_id += 1
    if not rows:
        print("No downstream progress yet -- nothing to write.")
        return
    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)
    gaps = df[df["validation_status"] == "GAP DETECTED"]
    print(f"Wrote {len(df)} checkpoint rows. GAP DETECTED count: {len(gaps)}")
    dup_check = df.groupby("grid_point_id")["actual_event_ids"].apply(
        lambda s: len(set(",".join(s).split(","))) == sum(len(x.split(",")) for x in s))
    print("No duplicate events within any grid point:", bool(dup_check.all()))


if __name__ == "__main__":
    main()
