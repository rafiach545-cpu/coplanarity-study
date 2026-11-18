#!/usr/bin/env python3
"""07 signal step G01 (2026-11-16): eps_fid and eps_reco of the 13.6 TeV quirk samples through the 07 detector (sim/detsim07.py, sim/cop07.py).
Same events, integrator and seeds as Stage 2 (06_publication/S2_.../S2_03_propagate.py -> 05_.../F6_02_grid.py, loaded unchanged):
  trigger events of inputs/<tag>_events.csv (colored: both quirk-hadrons charged); per event i: z0 and the 8 x 2 SCT barrel normals from
  SeedSequence([6, mass, i]) (F6_02 job); per Lambda the F6_02 integrator call (B = 2 T, max_layer_r_cm 60, numba, XONLY).
New (07):
  - crossings with every element of the configuration (geom stage2 = the 8 barrel layers; atlas = barrel + pixel disks + SCT rings):
    the FIRST crossing of each element's surface (barrel: cylinder r = R, sign change of r - R as in P18.all_crossings; disk: plane z = z_d),
    linear interpolation exactly as P18; a hit if inside the element (barrel |z| < half; disk r_min <= r <= r_max) and t < 25 ns;
  - SCT normals: barrel layers use the Stage 2 draws g[(q, L)]; disk SCT elements use SeedSequence([7, mass, i]) (2 x n_disk_sct x 2, element order);
  - response detsim07.respond for the SCT settings Z0, Z1160, A580 (D4) from the same normals; merge detsim07.overlay(raw, []) (no pile-up on
    the signal, as R10 and Stages 1-2);
  - fiducial (D1 item 3): every quirk's hits (true positions) cover the 8 stations (cop07._stations) and the line PV -> its station-8 hit has
    |eta| < 2.5 (R14 acceptance; taken on the hits, not on the initial momentum, because a quirk's initial direction can differ from where
    the pair goes). With geom stage2 the eta condition is always true (station 8 at r = 51.4 cm, |z - z0| < 95 cm: |eta| < 1.4) and the rule
    is exactly the F6_02 one (all 16 first crossings inside the lengths, t < 25 ns), checked by T07;
  - reconstruction cop07.analyse (paper algorithm on stations; final = plane, multiplicity at_least_2, Delta_s < 0.01 cm, Delta_w < 1 cm).
Also stored: fid_stage2 (the F6_02 barrel rule on the same trajectory) and per setting whether the winner plane uses an end-cap element.
Usage: G01_signal_07.py <geom stage2|atlas> <tag> <band mid|low|high_a> [--nmax N] [--workers K] [--input CSV] [--out DIR]
Per-event seeds use the event_id column when the input has one (large samples, L02: 100000 + index), else the row index (Stage 2).
Env COPLANARITY_BASE: the repository root (default /home/rafia/coplanarity_study).
Output: runs/<geom>/G01_<tag>_<band>.jsonl (one line per event: list of rows per Lambda; append-only, resumable)."""
import os, sys, json, time, math, argparse, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = f"{HERE}/.."; sys.path.insert(0, f"{ROOT}/sim")
BASE = os.environ.get("COPLANARITY_BASE", "/home/rafia/coplanarity_study")   # env var for running on another machine (2026-11-16, as P4)
S2 = f"{BASE}/06_publication/S2_13p6TeV_run3_knapen_noPU_cop"
REP = f"{BASE}/05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/scripts"
NS, CM = 6.582119569e-16, 1.973269804e-14                                # as P18_all_crossings
SETTINGS = ("Z0", "Z1160", "A580")
ap = argparse.ArgumentParser(); ap.add_argument("geom", choices=["stage2", "atlas"]); ap.add_argument("tag"); ap.add_argument("band", choices=["mid", "low", "high_a"])
ap.add_argument("--nmax", type=int, default=0); ap.add_argument("--workers", type=int, default=4)
ap.add_argument("--input", default="", help="events csv (default: the Stage 2 file inputs/<tag>_events.csv)")
ap.add_argument("--out", default="", help="output directory (default: runs/<geom>)"); A = ap.parse_args()
os.environ["FAST"] = "1"; os.environ["XONLY"] = "1"; os.environ["BAND"] = A.band; os.environ.pop("LAMS", None)
_argv = sys.argv; sys.argv = [f"{REP}/F6_02_grid.py", A.tag]
spec = importlib.util.spec_from_file_location("f6grid", f"{REP}/F6_02_grid.py"); F = importlib.util.module_from_spec(spec); sys.modules["f6grid"] = F
spec.loader.exec_module(F); sys.argv = _argv
import detsim07 as D, cop07                                              # noqa: E402
ELS = D.build(A.geom); DISK_SCT = [k for k, e in enumerate(ELS) if e["kind"] == "disk" and not e["is_pixel"]]
BARREL_L = {e["name"]: L for L, e in enumerate([e for e in ELS if e["kind"] == "barrel"], 1)}   # barrel element -> Stage 2 layer 1-8
assert list(BARREL_L) == [L["name"] for L in D.ag.LAYERS]   # = tth.LAYERS order of P18 (Stage 2 layer index)


def crossings(x, t):
    """First crossing of every element surface: [(element index, x, y, z, t_ns)] for those inside the element."""
    r = np.hypot(x[:, 0], x[:, 1]); out = []
    for k, e in enumerate(ELS):
        if e["kind"] == "barrel":
            R = e["r_cm"]; d = np.sign(r - R); idx = np.where(d[1:] != d[:-1])[0]
            if not len(idx): continue
            i = idx[0]; f = (R - r[i]) / (r[i + 1] - r[i])
        else:
            Z = e["z_cm"]; d = np.sign(x[:, 2] - Z); idx = np.where(d[1:] != d[:-1])[0]
            if not len(idx): continue
            i = idx[0]; f = (Z - x[i, 2]) / (x[i + 1, 2] - x[i, 2])
        p = x[i] + f * (x[i + 1] - x[i]); tt = t[i] + f * (t[i + 1] - t[i])
        inside = abs(p[2]) < e["half_cm"] if e["kind"] == "barrel" else e["rmin_cm"] <= math.hypot(p[0], p[1]) <= e["rmax_cm"]
        out.append((k, p[0], p[1], p[2], tt, inside))
    return out


SENS_ADJ = [float(x) for x in os.environ.get("G01_SENS_ADJ", "").split(",") if x.strip()]


def station_counts(w):
    """(stations with >= 1 hit, stations with >= 2 hits) of the winning plane; multiplicity threshold T (total hits) <=> n1 == 8 and n2 >= T - 8."""
    if not w: return 0, 0
    from collections import Counter
    c = Counter(w["layers"]); return sum(1 for k in range(1, 9) if c.get(k, 0) >= 1), sum(1 for k in range(1, 9) if c.get(k, 0) >= 2)


def job(a):
    i, P1, P2, c1, c2 = a
    rng = np.random.default_rng(np.random.SeedSequence([6, int(F.MQ), i])); z0 = rng.normal(0.0, F.p4.R["beamspot_cm"])
    g = {(q, L): rng.standard_normal(2) for q in (1, 2) for L in range(1, 9)}                       # F6_02 order
    gD = np.random.default_rng(np.random.SeedSequence([7, int(F.MQ), i])).standard_normal((2, max(len(DISK_SCT), 1), 2))
    dpos = {k: j for j, k in enumerate(DISK_SCT)}; origin = (0.0, 0.0, z0); out = []
    for lam in F.LAMS:
        t0 = time.time()
        try:
            _, tr = F.p4.tth.simulate_quirk_hits(P1, P2, mass_gev=F.MQ, Lambda_gev=lam * 1e-6, B_tesla=F.p4.R["B_tesla"], charge1=c1, charge2=c2,
                                                 rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=F.p4.R["max_layer_r_cm"])
        except Exception as ex:
            out.append(dict(event=i, lambda_keV=lam, fid=False, fid_stage2=False, error=str(ex)[:80], t_s=round(time.time() - t0, 2))); continue
        t = np.asarray(tr["t_gev_inv"]) * NS; cr = {q: crossings(np.asarray(x) * CM, t) for q, x in ((1, tr["x1"]), (2, tr["x2"]))}; del tr, _
        # Stage 2 fiducial rule on the barrel layers (F6_02 fid_of): first crossing of all 8 layers inside the length and t < 25 ns
        fid2 = all(sum(1 for c in cr[q] if ELS[c[0]]["kind"] == "barrel" and c[5] and c[4] < F.p4.R["timing_ns"]) == 8 for q in (1, 2)) \
               and all(sum(1 for c in cr[q] if ELS[c[0]]["kind"] == "barrel") == 8 for q in (1, 2))
        hits_true = {q: [c for c in cr[q] if c[5] and c[4] < F.p4.R["timing_ns"]] for q in (1, 2)}
        fid = True
        for q in (1, 2):
            st = cop07._stations([dict(x=c[1], y=c[2], z=c[3], is_pixel=ELS[c[0]]["is_pixel"]) for c in hits_true[q]], origin, ELS)
            fid &= set(range(1, 9)) <= set(st)
            if fid:
                c8 = [c for c, s_ in zip(hits_true[q], st) if s_ == 8][0]; fid &= abs(math.asinh((c8[3] - z0) / math.hypot(c8[1], c8[2]))) < 2.5
        row = dict(event=i, lambda_keV=lam, fid=bool(fid), fid_stage2=bool(fid2), error="", n_true_hits=sum(len(v) for v in hits_true.values()))
        for sct in SETTINGS:
            if not fid:
                row.update({f"{sct}_plane": False, f"{sct}_mult": False, f"{sct}_final": False, f"{sct}_ds": np.nan, f"{sct}_dw": np.nan, f"{sct}_endcap": False})
                continue
            raw = []
            for q in (1, 2):
                for k, x, y, z, tt, _in in hits_true[q]:
                    e = ELS[k]
                    if e["is_pixel"]: g1, g2 = 0.0, 0.0
                    elif e["kind"] == "barrel": g1, g2 = g[(q, BARREL_L[e["name"]])]
                    else: g1, g2 = gD[q - 1, dpos[k]]
                    raw.append(D.respond(e, x, y, z, tt, q, g1, g2, sct))
            merged, _st = D.overlay(raw, []); res, w = cop07.analyse(merged, origin, ELS)
            row.update({f"{sct}_plane": res["plane"], f"{sct}_mult": res["mult"], f"{sct}_final": res["final"], f"{sct}_ds": res["ds"],
                        f"{sct}_dw": res["dw"], f"{sct}_endcap": bool(w is not None and ("SCTD" in res["winner_stations"] or "PixD" in res["winner_stations"]))})
            for adj in SENS_ADJ:                                                       # 2026-11-17 sensitivity test (env G01_SENS_ADJ, e.g. "0,1,2"); same raw hits
                mg, _ = D.overlay(raw, [], adjacency=adj); rs, ww = cop07.analyse(mg, origin, ELS); n1, n2 = station_counts(ww)
                row.update({f"{sct}_a{adj:g}_plane": rs["plane"], f"{sct}_a{adj:g}_ds": rs["ds"], f"{sct}_a{adj:g}_dw": rs["dw"], f"{sct}_a{adj:g}_n1": n1, f"{sct}_a{adj:g}_n2": n2})
        row["t_s"] = round(time.time() - t0, 2); out.append(row)
    return out


if __name__ == "__main__":
    ev = pd.read_csv(A.input or f"{S2}/inputs/{F.TAG}_events.csv"); sel = ev.trigger_proxy_pass.astype(str) == "True"
    if F.CH == "colored": sel &= (ev.charge1.abs() > 0.5) & (ev.charge2.abs() > 0.5)
    ev = ev[sel].reset_index(drop=True)
    if A.nmax: ev = ev.iloc[:A.nmax]
    ids = ev.event_id.astype(int).tolist() if "event_id" in ev else list(range(len(ev)))   # large samples (L02): event_id = 100000 + index
    jobs = [(ids[i], (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2)) for i, r in enumerate(ev.itertuples())]
    outd = A.out or f"{HERE}/runs/{A.geom}"; os.makedirs(outd, exist_ok=True); LOG = f"{outd}/G01_{F.TAG}_{A.band}{f'_n{A.nmax}' if A.nmax else ''}.jsonl"
    done = {json.loads(l)[0]["event"] for l in open(LOG) if l.strip()} if os.path.exists(LOG) else set()
    todo = [j for j in jobs if j[0] not in done]
    print(f"G01 {A.geom} {F.TAG} band {A.band} Lambda {F.LAMS} keV: events {len(jobs)}, done {len(done)}, to run {len(todo)} -> {LOG}", flush=True)
    enc = lambda v: v.item() if hasattr(v, "item") else str(v)
    with mp.Pool(A.workers, initializer=F._init_worker) as pool, open(LOG, "a") as fh:
        for k, rr in enumerate(pool.imap(job, todo), 1):
            fh.write(json.dumps(rr, default=enc) + "\n"); fh.flush()
            if k % 10 == 0: print(f"  {k}/{len(todo)}", flush=True)
    print("G01_DONE", F.TAG, A.band, flush=True)
