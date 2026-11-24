#!/usr/bin/env python3
"""09 / step G07 (2026-11-22): impact of the Eq. 3 integration step on the Stage 1 · Run 2 · Ideal signal (8-layer, B = 2 T, 13 TeV).
Same events, vertices and SCT draws as the Stage 1 grid (05 .../scripts/F6_02_grid.py, fig6/inputs/<tag>_events.csv): the grid's own job()
is used unchanged, only the integrator is replaced by a wrapper that runs the same RK4 (quirk_trajectory_numba._rhs, same arithmetic order)
with dt / F, F = 1, 4, 16, where dt is the production step (300 steps per period after coarsening, config/reconstruction.yaml).
Memory: the wrapper integrates in segments and keeps only the trajectory points that bracket a layer crossing (plus the end points), so
all_crossings() finds exactly the same crossings; it stops at t = 25.05 ns (no hit at t >= 25 ns is used: fiducial needs every first
crossing at t < 25 ns, and reco drops later crossings). Check: F = 1 must reproduce the grid's logged fid / plane / final / ds / dw.
sigma_z: Z1160 (Knapen) and Z580 (ATLAS-like SCT z on the ideal geometry).
F = D10 / D11 (2026-11-22): the error-controlled DOP853 (03_trajectory_sim/quirk_trajectory_dop853.py) at rtol 1e-10 / 1e-11 instead of RK4;
then the RK4 step ceiling of simulate_quirk_hits is not applied (MIN_STEPS_PER_PERIOD = 1 only sizes the unused dt).
Usage: G07_dt_impact.py <tag> <lambdas keV, comma> <F> [--shard i/n]  -> out_G01/G07/<tag>_L<lam>_F<F>[_s<i>].jsonl (append, resumes)
Run in env g4. Workers: NWORKERS (default 3)."""
import os, sys, json, time, math, argparse, importlib.util, multiprocessing as mp, numpy as np, pandas as pd
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.environ.get("COPLANARITY_BASE", os.path.dirname(os.path.dirname(HERE)))
G6 = f"{BASE}/05_coplanarity_analysis/PAPER_LITERAL_FINAL_ANALYSIS_2026-10-03/scripts"
sys.path[:0] = [f"{BASE}/03_trajectory_sim"]
from quirk_trajectory_numba import _rhs, TESLA_TO_GEV2      # noqa: E402
from quirk_trajectory import _validate_integration_inputs   # noqa: E402
OUT = f"{HERE}/out_G01/G07"; os.makedirs(OUT, exist_ok=True)
SCTS = ("Z1160", "Z580")
T_STOP_NS = 25.05; NS = 6.582119569e-16; CM = 1.973269804e-14; SEG = 500_000


@njit(cache=True)
def _seg(state, t, mass, q1, q2, Lambda2, Bz, dt, n, t_max):
    """n RK4 steps from (state, t), same arithmetic as quirk_trajectory_numba._integrate (last step to t_max if reached)."""
    ts = np.zeros(n + 1); X = np.zeros((n + 1, 6)); ts[0] = t; X[0, 0:3] = state[0:3]; X[0, 3:6] = state[6:9]
    k1 = np.empty(12); k2 = np.empty(12); k3 = np.empty(12); k4 = np.empty(12); tmp = np.empty(12); m = 0
    for i in range(1, n + 1):
        if t >= t_max: break
        step = dt if t + dt < t_max else (t_max - t)
        _rhs(state, mass, q1, q2, Lambda2, Bz, k1)
        for j in range(12): tmp[j] = state[j] + 0.5 * step * k1[j]
        _rhs(tmp, mass, q1, q2, Lambda2, Bz, k2)
        for j in range(12): tmp[j] = state[j] + 0.5 * step * k2[j]
        _rhs(tmp, mass, q1, q2, Lambda2, Bz, k3)
        for j in range(12): tmp[j] = state[j] + step * k3[j]
        _rhs(tmp, mass, q1, q2, Lambda2, Bz, k4)
        for j in range(12): state[j] = state[j] + (step / 6.0) * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j])
        t += step; ts[i] = t; X[i, 0:3] = state[0:3]; X[i, 3:6] = state[6:9]; m = i
    return ts[:m + 1], X[:m + 1], t


FACTOR = 1; RADII = None; STATS = {}


def integrator(x1_0, p1_0, x2_0, p2_0, mass, charge1, charge2, Lambda_GeV, B_tesla, t_max_gev_inv, dt_gev_inv, e_charge_natural=0.30282212):
    """Drop-in for tth.integrate_trajectory: dt / FACTOR, stop at T_STOP_NS, keep only crossing brackets."""
    _validate_integration_inputs(x1_0, p1_0, x2_0, p2_0, mass, Lambda_GeV, t_max_gev_inv, dt_gev_inv)
    state = np.array([*map(float, x1_0), *map(float, p1_0), *map(float, x2_0), *map(float, p2_0)])
    dt = dt_gev_inv / FACTOR; t_end = min(t_max_gev_inv, T_STOP_NS / NS * 1.0)
    if FACTOR == 1 and t_max_gev_inv <= t_end: t_end = t_max_gev_inv                     # same last step as production
    Rn = np.array(RADII) / CM; keep_t, keep_x = [], []; t = 0.0; nsteps = 0; last = None
    while t < t_end:
        ts, X, t = _seg(state, t, float(mass), charge1 * e_charge_natural, charge2 * e_charge_natural, Lambda_GeV ** 2, B_tesla * TESLA_TO_GEV2, dt, SEG, t_end)
        if not np.all(np.isfinite(X)): raise RuntimeError("non-finite state (G07 wrapper)")
        if last is not None: ts, X = np.r_[last[0], ts[1:]], np.vstack([last[1], X[1:]])      # segment boundary: previous end point is this start
        nsteps += len(ts) - 1
        idx = {0, len(ts) - 1}
        for a in (0, 3):
            r = np.hypot(X[:, a], X[:, a + 1])
            for R in Rn:
                d = np.sign(r - R); w = np.nonzero(d[1:] != d[:-1])[0]; idx.update(w.tolist()); idx.update((w + 1).tolist())
        ii = np.array(sorted(idx)); keep_t.append(ts[ii] if not keep_t else ts[ii][1:]); keep_x.append(X[ii] if not keep_x else X[ii][1:])
        last = (ts[-1:], X[-1:])
        if len(ts) <= 1: break
    T = np.concatenate(keep_t); XX = np.vstack(keep_x)
    STATS["n_steps"] = nsteps; STATS["dt"] = dt
    return {"t_gev_inv": T, "x1": XX[:, 0:3], "p1": np.empty((0, 3)), "x2": XX[:, 3:6], "p2": np.empty((0, 3))}


def load_grid():
    import types
    src = open(f"{G6}/F6_02_grid.py").read().split('if __name__ == "__main__":')[0]
    g = types.ModuleType("f6grid"); g.__file__ = f"{G6}/F6_02_grid.py"
    return g, src


G = None


def _init(tag, lams, factor):
    global G, FACTOR, RADII
    sys.argv = ["F6_02_grid.py", tag]; os.environ["LAMS"] = ",".join(str(l) for l in lams); os.environ.pop("FAST", None)
    g, src = load_grid(); exec(compile(src, g.__file__, "exec"), g.__dict__); g._init_worker(); G = g
    FACTOR = factor; RADII = [L["r_cm"] for L in G.p4.tth.LAYERS]
    if str(factor) == "S10":                                       # the production switch in simulate_quirk_hits (env QUIRK_INTEGRATOR)
        import quirk_trajectory_dop853 as Q
        os.environ["QUIRK_INTEGRATOR"] = "dop853"; Q.RTOL = 1e-10; Q.ATOL_X = 1e-7 / Q.CM; Q.ATOL_P = 1e-10; Q.RADII_CM = None; Q.T_STOP_NS = None
        _orig = G.p4.tth.integrate_trajectory
        def _stat(*a, **k): return _orig(*a, **k)
        G.p4.tth.MIN_STEPS_PER_PERIOD = G.p4.R["steps_per_period"]
        STATS["n_steps"] = -1
    elif str(factor).startswith("D"):
        import quirk_trajectory_dop853 as Q
        rt = 10.0 ** -int(str(factor)[1:]); Q.RTOL = rt; Q.ATOL_X = 1e-7 / Q.CM * rt / 1e-10; Q.ATOL_P = 1e-10 * rt / 1e-10
        Q.RADII_CM = RADII; Q.T_STOP_NS = T_STOP_NS; Q.NCOARSE = 8; Q.NFINE = 64
        def dop(*a, **k):
            tr = Q.integrate_trajectory_dop853(*a, **k); STATS["n_steps"] = Q.STATS["n_accepted"]; return tr
        G.p4.tth.integrate_trajectory = dop; G.p4.tth.MIN_STEPS_PER_PERIOD = 1
    else:
        G.p4.tth.integrate_trajectory = integrator
    # the grid writes Z0 and Z1160; G07 needs Z1160 and Z580: same reco, other sigma_z key
    G.SCTS = SCTS


def job(a):
    i, P1, P2, c1, c2 = a; g = G; p18, p4 = g.p18, g.p4; p18.SID[g.SNAME] = 1000 + int(g.MQ)
    rng = np.random.default_rng(np.random.SeedSequence([6, int(g.MQ), i])); z0 = rng.normal(0.0, p4.R["beamspot_cm"])
    gg = {(q, L): rng.standard_normal(2) for q in (1, 2) for L in range(1, 9)}; out = []
    for lam in g.LAMS:
        t0 = time.time()
        try:
            _, tr = p4.tth.simulate_quirk_hits(P1, P2, mass_gev=g.MQ, Lambda_gev=lam * 1e-6, B_tesla=p4.R["B_tesla"], charge1=c1, charge2=c2,
                                               rng=np.random.default_rng(0), z0_cm=z0, max_layer_r_cm=p4.R["max_layer_r_cm"])
        except Exception as e:
            out.append(dict(event=i, lambda_keV=lam, F=FACTOR, fid=False, error=str(e)[:80], t_s=round(time.time() - t0, 2))); continue
        cr = p18.all_crossings(tr); del tr, _
        f = g.fid_of(cr); row = dict(event=i, lambda_keV=lam, F=FACTOR, fid=f, error="", n_steps=STATS.get("n_steps"), z0=z0)
        row["first"] = [[c["quirk"], c["layer"], c["x"], c["y"], c["z_lab"], c["t_ns"]] for c in cr if c["order"] == 0]
        for sct in ("Z0",) + SCTS:
            r = p18.reco(cr, z0, gg, sct, i, g.SNAME, True) if f else dict(plane=False, mult=False, final=False, ds=np.nan, dw=np.nan)
            row.update({f"{sct}_plane": r["plane"], f"{sct}_mult": r["mult"], f"{sct}_final": r["final"], f"{sct}_ds": r["ds"], f"{sct}_dw": r["dw"]})
        row["t_s"] = round(time.time() - t0, 2); out.append(row)
    return out


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("tag"); a.add_argument("lambdas"); a.add_argument("F")
    a.add_argument("--shard", default="0/1"); a.add_argument("--nmax", type=int); a.add_argument("--out", default=OUT); A = a.parse_args()
    os.makedirs(A.out, exist_ok=True)
    lams = [float(x) for x in A.lambdas.split(",")]; si, sn = map(int, A.shard.split("/"))
    _init(A.tag, lams, A.F if A.F[0] in "DS" else int(A.F))
    ev = pd.read_csv(f"{G6}/../fig6/inputs/{A.tag}_events.csv"); sel = ev.trigger_proxy_pass.astype(str) == "True"
    if A.tag.startswith("colored"): sel &= (ev.charge1.abs() > 0.5) & (ev.charge2.abs() > 0.5)
    ev = ev[sel].reset_index(drop=True)
    jobs = [(i, (r.px1, r.py1, r.pz1, r.E1), (r.px2, r.py2, r.pz2, r.E2), float(r.charge1), float(r.charge2)) for i, r in enumerate(ev.itertuples())]
    jobs = [j for j in jobs if j[0] % sn == si][:A.nmax]
    LOG = f"{A.out}/{A.tag}_L{A.lambdas.replace(',', '-')}_F{A.F}{'' if sn == 1 else f'_s{si}of{sn}'}{f'_n{A.nmax}' if A.nmax else ''}.jsonl"
    done = {json.loads(l)[0]["event"] for l in open(LOG) if l.strip()} if os.path.exists(LOG) else set()
    todo = [j for j in jobs if j[0] not in done]; print(f"{A.tag} L={lams} F={A.F}: {len(jobs)} events, {len(todo)} to run -> {LOG}", flush=True)
    NW = int(os.environ.get("NWORKERS", 3))
    with mp.Pool(NW, initializer=_init, initargs=(A.tag, lams, A.F if A.F[0] in "DS" else int(A.F))) as pool, open(LOG, "a") as fh:
        for k, rr in enumerate(pool.imap_unordered(job, todo), 1):
            fh.write(json.dumps(rr, default=lambda v: v.item() if hasattr(v, "item") else (bool(v) if isinstance(v, np.bool_) else str(v))) + "\n"); fh.flush()
            if k % 10 == 0: print(f"{k}/{len(todo)}", flush=True)
    print("G07_EXIT=0", flush=True)
