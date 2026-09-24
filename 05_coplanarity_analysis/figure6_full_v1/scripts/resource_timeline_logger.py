"""
Lightweight, read-only resource-timeline logger. Polls every POLL_S seconds
(not aggressive), appends one row to PHASE5_RESOURCE_TIMELINE.csv. Does not
touch, signal, or import the production driver -- reads only /proc, df,
free, and the driver's own status.json.
"""
import os
import time
import json
import csv
import subprocess

FIG6 = "/home/rafia/coplanarity_study/05_coplanarity_analysis/figure6_full_v1"
STATUS_PATH = f"{FIG6}/RUNTIME/status.json"
OUT_PATH = f"{FIG6}/RUNTIME/PHASE5_RESOURCE_TIMELINE.csv"
PID_PATH = f"{FIG6}/RUNTIME/production.pid"
POLL_S = 120
FIELDS = ["timestamp_utc", "driver_pid", "driver_alive", "n_children",
          "stage", "current_point_or_cell", "progress",
          "elapsed_h", "rolling_s_per_event",
          "driver_rss_mb", "children_rss_mb_total",
          "free_ram_gb", "free_disk_gb",
          "generation_dir_size_mb", "fig6_output_size_mb"]


def read_pid():
    try:
        return int(open(PID_PATH).read().strip())
    except Exception:
        return None


def proc_alive(pid):
    return pid is not None and os.path.exists(f"/proc/{pid}")


def rss_mb(pid):
    try:
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024
    except Exception:
        return None
    return None


def children_of(pid):
    try:
        out = subprocess.run(["ps", "--ppid", str(pid), "-o", "pid="],
                              capture_output=True, text=True).stdout
        return [int(x) for x in out.split()]
    except Exception:
        return []


def du_mb(path):
    try:
        out = subprocess.run(["du", "-sm", path], capture_output=True, text=True).stdout
        return int(out.split()[0])
    except Exception:
        return None


def free_gb():
    out = subprocess.run(["df", "--output=avail", "-BG", "/home/rafia"],
                          capture_output=True, text=True).stdout
    lines = out.strip().split("\n")
    return int(lines[-1].replace("G", "")) if len(lines) > 1 else None


def free_ram_gb():
    out = subprocess.run(["free", "-g"], capture_output=True, text=True).stdout
    for line in out.split("\n"):
        if line.startswith("Mem:"):
            return int(line.split()[6]) if len(line.split()) > 6 else int(line.split()[3])
    return None


def main():
    new_file = not os.path.exists(OUT_PATH)
    with open(OUT_PATH, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        while True:
            pid = read_pid()
            alive = proc_alive(pid)
            children = children_of(pid) if alive else []
            status = {}
            if os.path.exists(STATUS_PATH):
                try:
                    status = json.load(open(STATUS_PATH))
                except Exception:
                    pass
            row = {
                "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "driver_pid": pid, "driver_alive": alive, "n_children": len(children),
                "stage": status.get("stage"),
                "current_point_or_cell": status.get("current_point") or status.get("current_cell"),
                "progress": status.get("generation_progress") or status.get("cell_progress"),
                "elapsed_h": status.get("elapsed_h"),
                "rolling_s_per_event": status.get("rolling_s_per_event"),
                "driver_rss_mb": rss_mb(pid) if alive else None,
                "children_rss_mb_total": sum(filter(None, [rss_mb(c) for c in children])) if children else 0,
                "free_ram_gb": free_ram_gb(),
                "free_disk_gb": free_gb(),
                "generation_dir_size_mb": du_mb("/home/rafia/hep_tools/figure6_full_v1_runs"),
                "fig6_output_size_mb": du_mb(FIG6),
            }
            w.writerow(row)
            f.flush()
            if status.get("stage") == "COMPLETE":
                break
            if not alive:
                # driver died -- this row captures the dead state; stop rather than spin forever
                break
            time.sleep(POLL_S)


if __name__ == "__main__":
    main()
