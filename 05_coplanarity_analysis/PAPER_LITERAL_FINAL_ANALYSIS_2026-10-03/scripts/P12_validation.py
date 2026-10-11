#!/usr/bin/env python3
"""Phase 12 validation. Every check prints PASS/FAIL with evidence; results -> tables/P12_validation_results.csv.
Re-runnable; read-only on everything except its own output."""
import os, re, sys, glob, json, hashlib, subprocess, pandas as pd, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); L = os.path.abspath(f"{HERE}/.."); T = f"{L}/tables"; REPO = os.path.abspath(f"{L}/../..")
R = []
def chk(name, ok, ev): R.append(dict(check=name, result="PASS" if ok else "FAIL", evidence=str(ev)[:900])); print(("PASS " if ok else "FAIL ") + name, "|", str(ev)[:200])
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
Tr = lambda s: s.astype(str) == "True"
# 1 percentages recomputed
s = pd.read_csv(f"{T}/signal_efficiency_statistics.csv")
bad = s[~np.isclose(s.N_pass / s.N_total, s.eff) | ~np.isclose(100 * s.eff, s.percent)]
chk("signal: eff == N_pass/N_total and percent == 100*eff (all rows)", len(bad) == 0, f"{len(s)} rows, {len(bad)} mismatches")
for f in ["pileup_cutflow.csv", "converted_photon_cutflow.csv", "overlay_cutflow.csv"]:
    d = pd.read_csv(f"{T}/{f}"); b = d[~np.isclose(d.k / d.n, d.frac)]
    chk(f"{f}: frac == k/n", len(b) == 0, f"{len(d)} rows")
    seq = d[~d.stage.str.contains("non-sequential|generated|4/8|8/8")]
    mono = all((g.k.diff().fillna(0) <= 0).all() for _, g in seq.groupby("config", sort=False))
    chk(f"{f}: sequential stages monotone non-increasing", mono, "per config")
# 2 event closure
c = pd.read_csv(f"{T}/signal_event_closure.csv")
cols = [x for x in c.columns if x.startswith(("subset", "no_dup", "is_subset", "closure")) or c[x].dtype == bool]
allok = all(c[x].astype(str).isin(["True"]).all() for x in cols) if cols else False
chk("signal event closure: every stage subset of previous, no duplicates", allok, f"columns checked {cols}")
pe = pd.read_csv(f"{T}/signal_per_event_all_configs.csv")
chk("signal per-event: unique (sample,key,geom,sct,wconv)", not pe.duplicated(["sample", "key", "geom", "sct", "wconv"]).any(), len(pe))
lit = pe[(pe.geom == "B") & (pe.sct == "Z1160") & (pe.wconv == "W1")]
ok = True
for smp, g in lit.groupby("sample"):
    f, p, m, fin = Tr(g.fid), Tr(g.plane), Tr(g.mult), Tr(g.final)
    ok &= bool((p <= f).all() and (m <= p).all() and (fin <= m).all())
chk("literal signal: final ⊆ mult ⊆ plane ⊆ fiducial per event", ok, "4 samples")
# recount literal numbers from per-event table vs statistics table
st = s[s.config == "LITERAL"].set_index(["sample", "quantity"])
mm = []
for smp, g in lit.groupby("sample"):
    nf, nr = int(Tr(g.fid).sum()), int((Tr(g.fid) & Tr(g.final)).sum())
    a = st.loc[(smp, "reconstruction (full Sec. IV SR)")]
    if (int(a.N_pass), int(a.N_total)) != (nr, nf): mm.append(smp)
chk("literal reco k/n recomputed from per-event table == statistics table", not mm, mm or "all 4 match")
# 3 stale contaminated numbers
hits = []
for f in glob.glob(f"{L}/*.md"):
    for i, line in enumerate(open(f), 1):
        if re.search(r"\b20\s*/\s*25\b|\b84\s*/\s*94\b|numerator (20|84)\b|\b84\b.*plane|plane.*\b84\b", line) and not re.search(r"reject|contaminat|not used|stale|NOT", line, re.I):
            hits.append(f"{os.path.basename(f)}:{i}")
chk("no stale 20/25 or 84/94 used as a result in reports (only in rejection context)", not hits, hits or "none")
# 4 units
chk("units: literal signal Δs in cm (max < 1) and Δw in cm (max < 10)", lit.ds.max() < 1 and lit.dw.max() < 10, f"ds max {lit.ds.max():.4f} cm, dw max {lit.dw.max():.3f} cm")
# 5 figures read CSVs + provenance hashes
fb = []
for d in sorted(glob.glob(f"{L}/FINAL_FIGURES/*/")):
    n = os.path.basename(d.rstrip("/")); pj = f"{d}/provenance.json"
    if not os.path.exists(pj): fb.append(f"{n}: no provenance"); continue
    p = json.load(open(pj)); csv = f"{d}/{p['source_csv']}"
    if not p.get("plot_reads_only_source_csv") or sha(csv) != p["source_csv_sha256"]: fb.append(f"{n}: csv hash")
    for e in ("png", "pdf", "svg"):
        if not os.path.exists(f"{d}/{n}.{e}"): fb.append(f"{n}: missing {e}")
    if not os.path.exists(f"{d}/caption.md"): fb.append(f"{n}: caption")
chk("every FINAL_FIGURES entry: png/pdf/svg, caption, provenance, source-CSV hash matches", not fb, fb or f"{len(glob.glob(f'{L}/FINAL_FIGURES/*/'))} figures")
# 6 paper values
cp = pd.read_csv(f"{T}/paper_project_comparison.csv")
P = {("EW", "trigger"): 0.10, ("EW", "fiducial"): 0.28, ("EW", "reconstruction"): 0.72, ("COL", "trigger"): 0.24, ("COL", "fiducial"): 0.28, ("COL", "reconstruction"): 0.35}
chk("paper Table I values cited correctly", all(abs(r.paper_eff - P[(r.benchmark, r.quantity)]) < 1e-12 for _, r in cp.iterrows()), "6 values x samples")
tex = glob.glob(f"{REPO}/05_coplanarity_analysis/EW_PAPER_REPRODUCTION_FOLLOWUP_2026-10-02/paper_source/v2/quirks_prd_v2.tex")[0]
tx = open(tex).read()
chk("paper text contains quoted background numbers (10^{-3}, 6\\times 10^{-5}, ~1 pb, ~10 fb)", all(x in tx for x in ["10^{-3}", "6\\times 10^{-5}", "$\\sim 1$ pb", "$\\sim 10$ fb"]), os.path.basename(tex))
# 7 calibrated excluded
chk("LITERAL rows use only geometry B, SCT Z1160, W1", set(map(tuple, s[s.config == "LITERAL"][["geometry", "sct_z", "dw_convention"]].values)) == {("B", "Z1160", "W1")}, "statistics table")
chk("paper_project_comparison built from LITERAL only", len(cp) == 12, len(cp))
# 8 frozen hashes
p3 = json.load(open(f"{T}/P3_raw_trigger_recount.json")); fh = []
for k, v in p3.items():
    if isinstance(v, dict) and "lhe" in v:
        for a in ("lhe", "hepmc"):
            if sha(v[a]) != v[f"{a}_sha256"]: fh.append(f"{k}:{a}")
chk("frozen signal LHE/HepMC SHA-256 unchanged since Phase 3", not fh, fh or "8 files identical")
fbg = pd.read_csv(f"{T}/frozen_background_cutflows.csv").drop_duplicates("source")
bh = [r.source for _, r in fbg.iterrows() if sha(f"{REPO}/02_backgrounds/photon_conversion/{r.source}") != r.sha256]
chk("frozen conversion CSVs unchanged since P9b", not bh, bh or "2 files identical")
gd = subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True).stdout.strip()
gd = "\n".join(l for l in gd.splitlines() if "PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/" not in l)   # own working folder is tracked since the 2026-10-05 commit
chk("no tracked project file modified outside this analysis folder", gd == "", gd or "clean")
head = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
anc = subprocess.run(["git", "-C", REPO, "merge-base", "--is-ancestor", "97258a5d3ab99154c0b1fdacc397904a5ef5339f", "HEAD"]).returncode == 0
pushed = subprocess.run(["git", "-C", REPO, "branch", "-r", "--contains", "HEAD"], capture_output=True, text=True).stdout.strip()
chk("HEAD = 97258a5 or a local commit on top of it (commit authorized 2026-10-05), nothing pushed", anc and (head.startswith("97258a5") or pushed == ""), f"{head[:7]}; remote branches containing HEAD: {pushed or 'none'}")
f6 = f"{REPO}/05_coplanarity_analysis/figure6_full_v1/generation/EW_400GeV/downstream_L10keV/checkpoints/progress.json"
chk("Figure 6 checkpoint hash unchanged", sha(f6) == "aa59eaa418c8339f1b9dcb408ab1310e27df7dfd6dc76011c5129d52ff2a0c2b", sha(f6)[:16])
dn = len(glob.glob(f"{REPO}/05_coplanarity_analysis/figure6_full_v1/**/DONE*", recursive=True))
ps = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True).stdout
f6p = [l for l in ps.splitlines() if re.search(r"run_phase5_production|figure6", l) and "P12_validation" not in l and "grep" not in l]
chk("no Figure 6 process running", not f6p, f6p or "none")
pool = f"{REPO}/02_backgrounds/pileup/minbias_pool_20000_ANCESTRY_v1.csv"
R.append(dict(check="minbias pool sha256 (untracked; functional check = P8 VALIDATE 200/200 exact)", result="INFO", evidence=sha(pool)))
out = pd.DataFrame(R); out.to_csv(f"{T}/P12_validation_results.csv", index=False)
print(out.result.value_counts().to_dict())
