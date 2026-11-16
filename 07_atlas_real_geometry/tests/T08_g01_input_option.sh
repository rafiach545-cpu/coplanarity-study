#!/bin/bash
# 07 test T08 (2026-11-16): the G01 changes for the large samples (G02) leave the results unchanged.
#  (a) default call after the path change (COPLANARITY_BASE, --input/--out options): G01 stage2 --nmax 20 on EW_800gev mid and colored_1200gev low
#      gives rows identical (every field except t_s) to the first 20 events of the production files runs/stage2/G01_<tag>_<band>.jsonl (T07 PASS);
#  (b) --input = the Stage 2 csv with an added column event_id = row index: identical to (a) (event_id path of the seeds = index path);
#  (c) event_id = 100000 + index (as L02): the seeds change, so at least one row differs (the option is really used).
# Prints T08_PASS / T08_FAIL.
set -u
cd "$(dirname "$0")/.."; Q=/home/rafia/venvs/f6fast/bin/python; W=tests/T08_work; rm -rf "${W:?}"; mkdir -p "$W"
S2=/home/rafia/coplanarity_study/06_publication/S2_13p6TeV_run3_knapen_noPU_cop/inputs
ok=1
for tb in "EW_800gev mid" "colored_1800gev mid"; do
  set -- $tb; T=$1; B=$2
  $Q - "$S2/${T}_events.csv" "$W" "$T" <<'EOF'
import sys, pandas as pd
f, w, t = sys.argv[1:4]; ev = pd.read_csv(f); sel = ev.trigger_proxy_pass.astype(str) == "True"     # G01 selection (Stage 2 index = after it)
if t.startswith("colored"): sel &= (ev.charge1.abs() > 0.5) & (ev.charge2.abs() > 0.5)
ids = [-1] * len(ev); k = 0
for j in range(len(ev)):
    if sel[j]: ids[j] = k; k += 1
lines = open(f).read().splitlines(); assert len(lines) == len(ev) + 1      # raw text kept: a pandas rewrite changes the last float digit
for name, off in (("idx", 0), ("off", 100000)):
    with open(f"{w}/{t}_{name}.csv", "w") as o:
        o.write("event_id," + lines[0] + "\n")
        for j, l in enumerate(lines[1:]): o.write(f"{ids[j] + off if ids[j] >= 0 else -1},{l}\n")
EOF
  $Q signal/G01_signal_07.py stage2 $T $B --nmax 20 --workers 4 --out "$W/a" > "$W/a_$T.log" 2>&1
  $Q signal/G01_signal_07.py stage2 $T $B --nmax 20 --workers 4 --out "$W/b" --input "$W/${T}_idx.csv" > "$W/b_$T.log" 2>&1
  $Q signal/G01_signal_07.py stage2 $T $B --nmax 20 --workers 4 --out "$W/c" --input "$W/${T}_off.csv" > "$W/c_$T.log" 2>&1
  $Q - "signal/runs/stage2/G01_${T}_${B}.jsonl" "$W/a/G01_${T}_${B}_n20.jsonl" "$W/b/G01_${T}_${B}_n20.jsonl" "$W/c/G01_${T}_${B}_n20.jsonl" <<'EOF' || ok=0
import sys, json, math
def load(f):
    d = {}
    for l in open(f):
        if l.strip():
            r = json.loads(l); d[r[0]["event"]] = [{k: v for k, v in x.items() if k != "t_s"} for x in r]
    return d
def same(x, y): return json.dumps(x, sort_keys=True) == json.dumps(y, sort_keys=True)
P, a, b, c = (load(f) for f in sys.argv[1:5])
ra = len(a) == 20 and all(same(a[e], P[e]) for e in a)
rb = len(b) == 20 and all(same(b[e], a[e]) for e in a)
cc = {e - 100000: v for e, v in c.items()}
rc = len(c) == 20 and min(c) >= 100000 and any(not same([{k: v for k, v in x.items() if k != "event"} for x in cc[e]], [{k: v for k, v in x.items() if k != "event"} for x in a[e]]) for e in a)
nf = sum(x["fid"] for e in a for x in a[e])
print(f"{sys.argv[2].split('/')[-1]}: (a) identical to production {ra}, (b) event_id=index identical {rb}, (c) offset seeds differ {rc}; fiducial rows {nf}")
sys.exit(0 if ra and rb and rc else 1)
EOF
done
[ $ok = 1 ] && echo T08_PASS || echo T08_FAIL
