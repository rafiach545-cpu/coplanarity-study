#!/usr/bin/env python3
"""
Task 4: trigger efficiency by initial-state partonic channel and by ME jet multiplicity, EW vs colored,
using the driver-v3 showers (frozen shower settings) of the six LHE samples. Each matched event is
mapped back to its LHE event through the hard-process (status 23) quirk momenta.
Also: hard-process (pre-shower) vs final-state (post-shower / post-hadronisation for colored)
pair pT trigger.
"""
import math, os
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"
W = "/home/rafia/hep_tools/TABLE_I_TRIGGER_SEARCH_2026-10-02"
LHE = {"EW1000": "EW_frozen1000_mg373", "EW2000": "EW_frozen2000_mg373", "G0_EW": "G0_newseed_EW",
       "COL1000": "COL_frozen1000_mg373", "COL2000": "COL_frozen2000_mg373", "G0_COL": "G0_newseed_COL"}
QIDS = {9000011, 1000006}


def read_lhe(path):
    ev, cur, inside = [], None, False
    for line in open(path):
        s = line.strip()
        if s.startswith("<event"):
            inside, cur = True, []; continue
        if s.startswith("</event"):
            inside = False; n = int(cur[0].split()[0]); P = [l.split() for l in cur[1:1 + n]]
            ini = sorted(int(p[0]) for p in P if int(p[1]) == -1)
            q = [p for p in P if abs(int(p[0])) in QIDS]
            jets = [p for p in P if int(p[1]) == 1 and abs(int(p[0])) not in QIDS]
            def lab(i):
                a = abs(i); return "g" if a == 21 else ("q" if i > 0 else "qbar")
            chan = "+".join(sorted(lab(i) for i in ini)) + (" -> QQ" + ("+" + "+".join(lab(int(j[0])) for j in jets) if jets else ""))
            ev.append(dict(n_jets=len(jets), channel=chan,
                           key=tuple(sorted((round(float(x[6]), 2), round(float(x[8]), 2)) for x in q))))
            continue
        if inside and s and not s.startswith("<"):
            cur.append(s)
    return pd.DataFrame(ev)


def wil(k, n, z=1.959964):
    if n == 0: return (np.nan, np.nan)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z / d * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)); return c - h, c + h


rows = []
for s, l in LHE.items():
    L = read_lhe(f"{W}/inputs/{l}.lhe"); key = {k: i for i, k in enumerate(L.key)}
    e = pd.read_csv(f"{W}/runs/V3OBS/{s}/events.csv")
    e["lhe"] = [key.get(tuple(sorted([(round(a, 2), round(b, 2)), (round(c, 2), round(d, 2))]))) for a, b, c, d in zip(e.h_px1, e.h_pz1, e.h_px2, e.h_pz2)]
    e = e.join(L[["n_jets", "channel"]], on="lhe")
    e["sample"] = s; e["bench"] = "EW" if "EW" in s else "COL"
    rows.append(e)
d = pd.concat(rows)
print("unmapped:", d.lhe.isna().groupby(d["sample"]).sum().to_dict())
out = []
for (b, by), g in [((b, "n_jets"), x) for b, x in d.groupby("bench")] + [((b, "channel"), x) for b, x in d.groupby("bench")]:
    for v, gg in g.groupby(by):
        n = len(gg); k = int((gg.pair_pt_final > 200).sum()); kh = int((gg.pair_pt_hard > 200).sum()); lo, hi = wil(k, n)
        out.append(dict(bench=b, split=by, value=v, N_matched=n, frac_of_matched=n / len(g), N_trig=k, eff_trig=k / n,
                        ci95_lo=lo, ci95_hi=hi, frac_of_triggers=k / max(int((g.pair_pt_final > 200).sum()), 1),
                        eff_trig_hard_status23=kh / n))
    n = len(g); k = int((g.pair_pt_final > 200).sum()); kh = int((g.pair_pt_hard > 200).sum())
    if by == "n_jets":
        out.append(dict(bench=b, split="ALL", value="all", N_matched=n, frac_of_matched=1.0, N_trig=k, eff_trig=k / n,
                        ci95_lo=wil(k, n)[0], ci95_hi=wil(k, n)[1], frac_of_triggers=1.0, eff_trig_hard_status23=kh / n))
o = pd.DataFrame(out); o.to_csv(f"{T}/trigger_by_channel_and_multiplicity.csv", index=False)
pd.set_option("display.width", 220); print(o.round(4).to_string(index=False))
EOF_ = None
