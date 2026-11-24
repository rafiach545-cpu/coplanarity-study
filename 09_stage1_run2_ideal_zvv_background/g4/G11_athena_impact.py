#!/usr/bin/env python3
"""09 / Geant4 step G11 (2026-11-24): size of the Athena string-model systematic on the Stage 1 · Run 2 · Ideal signal (8-layer, B = 2 T, 13 TeV).
The G07 impact subset (colored 1800 GeV and EW 800 GeV at Lambda = 2, 4, 7, 10 keV; EW 600 GeV at 4, 5 keV) with the trajectory from Geant4
(QuirkPheno_fix: Athena string-vector model; secondOrderField, DeltaIntersection 1 nm (G05), maxBoost 0.01 or 0.001) instead of Eq. 3.
Everything else is the G07 job unchanged (G07_dt_impact.py, itself the Stage 1 grid's F6_02_grid.py job): same events and trigger selection,
same z0 and SCT draws (SeedSequence([6, mass, i])), the grid's fid_of and P18 reco for Z0 / Z1160 / Z580.
Geant4: one quirksim process per (event, Lambda), g4/ideal8_vacuum.card (no material, Bz = 2 T), gun at (0, 0, z0), /qsim/maxTime 25.05 ns
(as G07's T_STOP_NS: no hit at t >= 25 ns is used). Crossing of layer L by quirk q = the ENTRY point of its first visit of the 1 um layer
(inner surface = the layer radius, as all_crossings). Quirk mapping (as G01): Geant4 p1 = the positive PDG code with charge -1 e (h_q = 0),
so grid quirk with charge -1 -> p1 / h_q 0, charge +1 -> p2 / h_q 1 (all G07 events have charges -1/+1 or +1/-1, checked).
Output out_G01/G11/<tag>_L<lams>_F<G4mb01|G4mb001>[_n<N>].jsonl, rows in the G07 format (F, fid, first, <sct>_final/_ds/_dw/...), compared by G11_table.py
with the G07 DOP853 run FD10. Usage (env g4): G11_athena_impact.py <tag> <lambdas keV> [--mb 0.01] [--nmax N]; workers NWORKERS (default 6)."""
import os, sys, json, time, argparse, subprocess, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import G07_dt_impact as G7                                                  # noqa: E402  (unchanged; only load_grid / _init are used)
import uproot                                                               # noqa: E402
BASE = G7.BASE; G6 = G7.G6
QF = os.environ.get("QUIRKPHENO_FIX", os.path.join(os.path.dirname(BASE), "hep_tools", "QuirkPheno_fix")) + "/build"
CARD = f"{HERE}/ideal8_vacuum.card"; OUT = f"{HERE}/out_G01/G11"; MB = 0.01


def _init(tag, lams, mb):
    global MB
    G7._init(tag, lams, "D10"); MB = mb                                     # grid module, MQ, SNAME, p18, p4; the integrator setting is not used here


def g4_crossings(i, lam, P1, P2, c1, c2, z0):
    g = G7.G; tag = f"{g.SNAME}_e{i:04d}_L{lam:g}_mb{MB:g}"; root = f"{OUT}/runs/{tag}.root"
    neg, pos = (P1, P2) if c1 < 0 else (P2, P1)                             # p1 = charge -1 (h_q 0), p2 = charge +1 (h_q 1)
    if not os.path.exists(root):
        L = ["/quirk/secondOrderField true", "/qsim/field/deltaIntersection 1e-6 mm", f"/quirk/maxBoost {MB}", f"/quirk/mass {g.MQ} GeV",
             f"/quirk/lambda {lam * 1000.0} eV", f"/qsim/card {CARD}", "/qsim/gen/mode gun", "/qsim/killSecondaries true", "/qsim/out/towers false",
             "/qsim/out/printEvery 1000", f"/qsim/maxTime {G7.T_STOP_NS} ns", f"/qsim/gun/p1 {neg[0]} {neg[1]} {neg[2]} GeV",
             f"/qsim/gun/p2 {pos[0]} {pos[1]} {pos[2]} GeV", f"/qsim/gun/vertex 0 0 {z0 * 10.0} mm", "/run/initialize", "/run/beamOn 1"]
        open(f"{OUT}/runs/{tag}.mac", "w").write("\n".join(L) + "\n")
        env = dict(os.environ, LD_LIBRARY_PATH=f"{QF}/quirkcore:" + os.environ.get("LD_LIBRARY_PATH", ""))
        with open(f"{OUT}/runs/{tag}.log", "w") as lg:
            subprocess.run([f"{QF}/quirksim/quirksim", "-m", f"{OUT}/runs/{tag}.mac", "-t", "1", "-s", "7", "-o", root[:-5] + "_part.root"],
                           env=env, stdout=lg, stderr=subprocess.STDOUT, check=True)
        os.replace(root[:-5] + "_part.root", root)
    T = uproot.open(root)["events"].arrays(library="np"); assert len(T["evt"]) == 1
    qmap = {0: 1 if c1 < 0 else 2, 1: 2 if c1 < 0 else 1}; cr, seen = [], set()
    for j in np.argsort(T["h_t0"][0]):
        q, l = qmap[int(T["h_q"][0][j])], int(T["h_layer"][0][j])
        if (q, l) in seen: continue
        seen.add((q, l))
        cr.append(dict(quirk=q, layer=l, order=0, x=0.1 * T["h_x0"][0][j], y=0.1 * T["h_y0"][0][j], z_lab=0.1 * T["h_z0"][0][j], t_ns=float(T["h_t0"][0][j]),
                       r=G7.G.p4.tth.LAYERS[l - 1]["r_cm"]))
    return cr


def job(a):
    i, P1, P2, c1, c2 = a; g = G7.G; p18, p4 = g.p18, g.p4; p18.SID[g.SNAME] = 1000 + int(g.MQ)
    rng = np.random.default_rng(np.random.SeedSequence([6, int(g.MQ), i])); z0 = rng.normal(0.0, p4.R["beamspot_cm"])     # as G07 job
    gg = {(q, L): rng.standard_normal(2) for q in (1, 2) for L in range(1, 9)}; out = []; F = f"G4mb{str(MB).replace('0.', '')}"
    for lam in g.LAMS:
        t0 = time.time()
        try: cr = g4_crossings(i, lam, P1, P2, c1, c2, z0)
        except Exception as e:
            out.append(dict(event=i, lambda_keV=lam, F=F, fid=False, error=str(e)[:80], t_s=round(time.time() - t0, 2))); continue
        f = g.fid_of(cr); row = dict(event=i, lambda_keV=lam, F=F, fid=f, error="", z0=z0)
        row["first"] = [[c["quirk"], c["layer"], c["x"], c["y"], c["z_lab"], c["t_ns"]] for c in cr]
        for sct in ("Z0",) + G7.SCTS:
            r = p18.reco(cr, z0, gg, sct, i, g.SNAME, True) if f else dict(plane=False, mult=False, final=False, ds=np.nan, dw=np.nan)
            row.update({f"{sct}_plane": r["plane"], f"{sct}_mult": r["mult"], f"{sct}_final": r["final"], f"{sct}_ds": r["ds"], f"{sct}_dw": r["dw"]})
        row["t_s"] = round(time.time() - t0, 2); out.append(row)
    return out


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("tag"); a.add_argument("lambdas"); a.add_argument("--mb", type=float, default=0.01)
    a.add_argument("--nmax", type=int); A = a.parse_args(); os.makedirs(f"{OUT}/runs", exist_ok=True)
    lams = [float(x) for x in A.lambdas.split(",")]
    ev = pd.read_csv(f"{G6}/../fig6/inputs/{A.tag}_events.csv"); sel = ev.trigger_proxy_pass.astype(str) == "True"
    if A.tag.startswith("colored"): sel &= (ev.charge1.abs() > 0.5) & (ev.charge2.abs() > 0.5)
    ev = ev[sel].reset_index(drop=True)                                     # as G07
    assert ((ev.charge1 * ev.charge2) == -1).all(), "Geant4 gun needs charges -1/+1"
    jobs = [(i, (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2)) for i, r in enumerate(ev.itertuples())][:A.nmax]
    F = f"G4mb{str(A.mb).replace('0.', '')}"
    LOG = f"{OUT}/{A.tag}_L{A.lambdas.replace(',', '-')}_F{F}{f'_n{A.nmax}' if A.nmax else ''}.jsonl"
    done = {json.loads(l)[0]["event"] for l in open(LOG) if l.strip()} if os.path.exists(LOG) else set()
    todo = [j for j in jobs if j[0] not in done]; print(f"{A.tag} L={lams} {F}: {len(jobs)} events, {len(todo)} to run -> {LOG}", flush=True)
    with mp.Pool(int(os.environ.get("NWORKERS", 6)), initializer=_init, initargs=(A.tag, lams, A.mb)) as pool, open(LOG, "a") as fh:
        for k, rr in enumerate(pool.imap_unordered(job, todo), 1):
            fh.write(json.dumps(rr, default=lambda v: v.item() if hasattr(v, "item") else (bool(v) if isinstance(v, np.bool_) else str(v))) + "\n"); fh.flush()
            if k % 10 == 0: print(f"{k}/{len(todo)}", flush=True)
    print("G11_EXIT=0", flush=True)
