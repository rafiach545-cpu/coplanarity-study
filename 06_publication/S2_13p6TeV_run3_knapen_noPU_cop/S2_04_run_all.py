#!/usr/bin/env python3
"""Stage 2, step 4: runs S2_03_propagate.py for all 13 mass points and the three Lambda bands of the reproduction (low 0.1-0.7, mid 1-10, high_a 15-25 keV).
All points are propagated, including colored 2400 GeV (skipped at 13 TeV because N_max < 3). Lanes: low + mid with 4 processes in parallel, then high_a with 2
(one 15-25 keV trajectory needs up to 2.4 GB). A process that exits non-zero is restarted (up to 6 attempts; it resumes from its checkpoint).
Memory watchdog as in the reproduction (logs/F6_mem_watchdog.sh): if MemAvailable < 700 MB, the largest S2_03 process is killed and its lane restarts it.
Usage: S2_04_run_all.py. Logs: logs/S2_04_<tag>_<band>.log, logs/S2_04_run_all.log."""
import os, time, subprocess, threading, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); PY = "/home/rafia/venvs/f6fast/bin/python"
C = pd.read_csv(f"{HERE}/inputs/counts.csv")
TAGS = [f"{r.channel}_{r.mass_gev}gev" for r in C.sort_values("n_trigger_both_charged", ascending=False).itertuples()]
stop = False
def log(m): print(f"{time.strftime('%FT%T')} {m}", flush=True)
def watchdog():
    while not stop:
        av = int(next(l for l in open("/proc/meminfo") if l.startswith("MemAvailable")).split()[1])
        if av < 716800:
            ps = subprocess.run(["ps", "-eo", "pid,rss,args", "--sort=-rss"], capture_output=True, text=True).stdout.splitlines()[1:]
            p = next((l.split()[0] for l in ps if "S2_03_propagate.py" in l), None)
            if p: os.kill(int(p), 9); log(f"watchdog: MemAvailable {av} kB -> killed {p}"); time.sleep(5)
        time.sleep(1)
def task(tag, band):
    for a in range(1, 7):
        with open(f"{HERE}/logs/S2_04_{tag}_{band}.log", "a") as f:
            rc = subprocess.run([PY, f"{HERE}/S2_03_propagate.py", tag], env={**os.environ, "BAND": band}, stdout=f, stderr=subprocess.STDOUT).returncode
        log(f"{tag} {band} attempt {a} exit {rc}")
        if rc == 0: return True
        time.sleep(20)
    return False
def lanes(jobs, n):
    q = list(jobs); lk = threading.Lock(); bad = []
    def lane():
        while True:
            with lk:
                if not q: return
                j = q.pop(0)
            if not task(*j): bad.append(j)
    ts = [threading.Thread(target=lane) for _ in range(n)]; [t.start() for t in ts]; [t.join() for t in ts]; return bad
threading.Thread(target=watchdog, daemon=True).start()
bad = lanes([(t, b) for b in ("mid", "low") for t in TAGS], 4) + lanes([(t, "high_a") for t in TAGS], 2)
stop = True; log(f"FAILED {bad}" if bad else "PROPAGATION_EXIT=0")
