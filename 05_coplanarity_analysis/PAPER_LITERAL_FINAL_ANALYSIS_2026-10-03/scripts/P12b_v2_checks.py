#!/usr/bin/env python3
"""v2 checks: primary denominators, every v2 count recomputed from the per-event audit file, finite-barrel EW2000 = 62,
conversion A counts from per-event file, frozen signal/background hashes unchanged, no Figure 6 process."""
import os, json, hashlib, subprocess, re, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); T = f"{HERE}/../tables"; REPO = os.path.abspath(f"{HERE}/../../..")
R = []; TR = lambda s: s.astype(str) == "True"
def chk(n, ok, ev): R.append(dict(check=n, result="PASS" if ok else "FAIL", evidence=str(ev))); print("PASS" if ok else "FAIL", n, "|", ev)
pe = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); M = pd.read_csv(f"{T}/acceptance_longitudinal_matrix.csv")
bad = 0
for (s, g, z, b), x in pe.groupby(["sample", "geom", "sct", "bs"]):
    m = M[(M["sample"] == s) & (M.acceptance == g) & (M.sct_z == z) & (M.beamspot == b)].iloc[0]; f = x[TR(x.fid)]
    bad += int((len(f), int(TR(f.plane).sum()), int(TR(f.mult).sum()), int(TR(f.final).sum())) != (m.fiducial, m.plane, m.mult, m.final))
chk("matrix counts recomputed from per-event file (72 configs)", bad == 0, f"{bad} mismatches")
V = pd.read_csv(f"{T}/v2_primary_table_I.csv")
den = {s: int(V[(V["sample"] == s) & (V.quantity == "fiducial")].k.iloc[0]) for s in ["COL1000", "COL2000", "EW1000", "EW2000"]}
chk("primary fiducial numerators = 7, 25, 40, 94", den == {"COL1000": 7, "COL2000": 25, "EW1000": 40, "EW2000": 94}, den)
rd = V[V.quantity == "reconstruction"].groupby("sample").n.unique().to_dict()
chk("primary reco denominators equal primary fiducial counts", all(list(v) == [den[k]] for k, v in rd.items()), rd)
S = pd.read_csv(f"{T}/v2_finite_barrel_sensitivity.csv")
chk("finite-barrel EW2000 fiducial = 62 (not 61), final 10", int(S[(S["sample"] == "EW2000") & (S.quantity == "fiducial")].k.iloc[0]) == 62 and int(S[(S["sample"] == "EW2000") & (S.treatment.str.startswith("SCT z 1160"))].k.iloc[0]) == 10, "EW2000 B")
cp = pd.read_csv(f"{T}/conversion_acceptance_A_per_event.csv"); cf = pd.read_csv(f"{T}/conversion_acceptance_A_cutflow.csv")
ok = all(int((TR(g.plane) & TR(g.mult) & TR(g.final)).sum()) == int(cf[(cf.config == c) & (cf.stage == "final Sec. IV")].k.iloc[0]) for c, g in cp.groupby("config"))
chk("conversion acceptance-A finals recomputed from per-event file", ok, cf[cf.stage == "final Sec. IV"][["config", "k"]].values.tolist())
chk("conversion acceptance-A covers 9139 photons x 3 configs", len(cp) == 3 * 9139 and cp.groupby("config").event.nunique().eq(9139).all(), len(cp))
p3 = json.load(open(f"{T}/P3_raw_trigger_recount.json")); fh = []
for k, v in p3.items():
    if isinstance(v, dict) and "lhe" in v:
        for a in ("lhe", "hepmc"):
            if hashlib.sha256(open(v[a], "rb").read()).hexdigest() != v[f"{a}_sha256"]: fh.append(k + a)
chk("frozen signal LHE/HepMC unchanged", not fh, fh or "8 identical")
gd = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True).stdout.strip()
chk("no tracked file modified", gd == "", gd or "clean")
ps = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True).stdout
chk("no Figure 6 process", not [l for l in ps.splitlines() if re.search("run_phase5_production|figure6", l) and "P12b" not in l], "none")
f6 = f"{REPO}/05_coplanarity_analysis/figure6_full_v1/generation/EW_400GeV/downstream_L10keV/checkpoints/progress.json"
chk("Figure 6 checkpoint hash unchanged", hashlib.sha256(open(f6, "rb").read()).hexdigest().startswith("aa59eaa418c8339f"), "aa59eaa4…")
chk("v1 professor PDF still present (not overwritten)", os.path.exists(f"{HERE}/../PROFESSOR_REPORT_2026-10-03.pdf") and os.path.exists(f"{HERE}/../PROFESSOR_REPORT_2026-10-03_v2.pdf"), "v1 + v2")
pd.DataFrame(R).to_csv(f"{T}/P12b_v2_validation_results.csv", index=False)
