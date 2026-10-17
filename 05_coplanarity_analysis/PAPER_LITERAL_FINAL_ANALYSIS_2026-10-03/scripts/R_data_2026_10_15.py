#!/usr/bin/env python3
"""Single data source for the 2026-10-15 report and its figures (no number is typed by hand in the report).
Every value is read from the analysis outputs and checked with assertions against the counts used before (report of 2026-10-09, D-log).
Uncertainty: simple binomial sigma = sqrt(e (1 - e) / n) for an efficiency e = k / n with its own denominator n (approximate, statistical only);
for a ratio of MadGraph cross sections the integration errors are propagated; for a product of conditional efficiencies (Eq. 12) the relative
uncertainties are added in quadrature (each factor is a binomial on a disjoint selection stage)."""
import os, json, glob, re
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); L_ = os.path.abspath(f"{HERE}/.."); T = f"{L_}/tables"; FIG = f"{L_}/FINAL_FIGURES"; LOG = f"{L_}/logs"
EV = "/home/rafia/coplanarity_study/05_coplanarity_analysis/quirk_2000_event_fresh_regeneration_v1"; IN = f"{L_}/inputs_D41"
TR = lambda s: s.astype(str) == "True"

def sig(k, n):
    e = k / n; return e, float(np.sqrt(e * (1 - e) / n))

def fmt(k, n, d=3):
    e, s = sig(k, n); return f"{e:.{d}f} ± {s:.{d}f}"

SAM = {"COL2000": dict(tag="colored_1800GeV_L2keV", name="Colored", mq=1800, lam=2, paper=dict(trig=.24, fid=.28, reco=.35)),
       "EW2000": dict(tag="EW_800GeV_L4keV", name="EW", mq=800, lam=4, paper=dict(trig=.10, fid=.28, reco=.72))}
PAPER_L = {"EW2000": {1: .11, 2: .41, 3: .65, 4: .72, 5: .74}, "COL2000": {1: .083, 2: .35, 3: .59, 5: .74, 10: .58}}

def production():
    GEN = {s: json.load(open(f"{EV}/generation/{v['tag']}/generation_stats.json")) for s, v in SAM.items()}
    MAT = {s: pd.read_csv(f"{EV}/events/{v['tag']}/matched_events_full.csv") for s, v in SAM.items()}
    A = pd.read_csv(f"{T}/all_crossings_per_event.csv")
    PE = pd.read_csv(f"{T}/acceptance_longitudinal_per_event.csv"); PE = PE[(PE.geom == "B") & (PE.sct == "Z0") & (PE.bs == "CV")]
    CNT = {}
    for s in SAM:
        M = MAT[s]; trig = TR(M.trigger_proxy_pass); assert int(trig.sum()) == int((M.quirk_pair_pt_gev > 200).sum())
        Tg = M[trig]; charged = int(((Tg.charge1.abs() > 0.5) & (Tg.charge2.abs() > 0.5)).sum())
        a0 = A[(A["sample"] == s) & (A["mode"] == "FIRST") & (A.sct == "Z0")]
        tech = PE[(PE["sample"] == s) & (PE.why == "technical_exception")]; assert len(a0) + len(tech) == charged and not TR(tech.fid).any()
        c = dict(gen=GEN[s]["N_requested"], matched=len(M), trig=int(trig.sum()), charged=charged, fid=int(TR(a0.fid).sum()), tech=len(tech),
                 xs_matched_fb=GEN[s]["matched_xsec_pb"] * 1e3, xs_matched_err_fb=GEN[s]["matched_xsec_err_pb"] * 1e3)
        for mode in ("FIRST", "ALL"):
            for sct in ("Z1160", "Z580", "Z0"):
                x = A[(A["sample"] == s) & (A["mode"] == mode) & (A.sct == sct) & TR(A.fid)]; assert len(x) == c["fid"]
                c[(mode, sct)] = dict(plane=int(TR(x.plane).sum()), mult=int((TR(x.plane) & TR(x.mult)).sum()), sr=int(TR(x.final).sum()),
                                      ds_med_um=float(x[TR(x.plane) & TR(x.mult)].ds.median() * 1e4), dw_med_cm=float(x[TR(x.plane) & TR(x.mult)].dw.median()))
        x = A[(A["sample"] == s) & (A["mode"] == "ALL") & (A.sct == "Z0") & TR(A.fid)]
        c["multi_cross"] = int((x.max_hits_per_layer > 2).sum())
        CNT[s] = c
    # checks against the 2026-10-09 report and D-log (D18, D35)
    assert (CNT["COL2000"]["trig"], CNT["COL2000"]["matched"], CNT["EW2000"]["trig"], CNT["EW2000"]["matched"]) == (207, 873, 186, 1045)
    assert (CNT["COL2000"]["fid"], CNT["COL2000"]["charged"], CNT["EW2000"]["fid"], CNT["EW2000"]["charged"]) == (22, 68, 62, 186)
    assert [CNT[s][("FIRST", z)]["sr"] for s in SAM for z in ("Z0", "Z580", "Z1160")] == [8, 3, 1, 50, 14, 10]
    return CNT

def lambda_scan():
    L0 = pd.read_csv(f"{T}/lambda_scan_summary.csv"); L1 = pd.read_csv(f"{T}/lambda_scan_z1160_summary.csv")
    LS = pd.concat([L0[L0["sample"].isin(list(SAM)) & (L0.sct == "Z0")], L1]); return LS

def backgrounds():
    def ov(d):
        o = pd.concat(pd.read_csv(f) for f in glob.glob(f"{LOG}/{d}/chunk_*.csv")); o = o[o.config == "LITERAL"]; assert o.event.nunique() == 9139
        return dict(n=9139, plane=int(TR(o.plane).sum()), mult=int((TR(o.plane) & TR(o.mult)).sum()), sr=int((TR(o.plane) & TR(o.mult) & TR(o.final)).sum()))
    def pu(d):
        p = pd.concat(pd.read_csv(f) for f in glob.glob(f"{LOG}/{d}/chunk_*.csv")); assert p.event_i.nunique() == 5000; sel = TR(p.sec3c_plane_found) & (p.sec3c_dw < 1)
        return dict(n=5000, r4=int((sel & (p.sec3c_n_layers >= 4)).sum()), r8=int((sel & (p.sec3c_n_layers >= 8)).sum()), sr=int(TR(p.final_sec_iv_pass).sum()))
    BG = dict(conv580=ov("P10_chunks_B_Z580_REF34"), conv1160=ov("P10_chunks_LITERAL"), conv0=ov("P10_chunks_B_Z0_REF34"),
              pu580=pu("P21_chunks_REF34_Z580"), pu1160=pu("P8_chunks_LITERAL"), puinel=pu("P22_chunks_MB_INEL_MONASH"))
    assert (BG["conv580"]["sr"], BG["conv1160"]["sr"], BG["conv0"]["sr"], BG["pu580"]["sr"], BG["pu580"]["r4"], BG["pu580"]["r8"]) == (0, 0, 146, 0, 33, 1)
    return BG

def ul95(n): return 1 - 0.05 ** (1 / n)

def lo_trigger():
    """sigma(B)/sigma(A) from the MG5 logs (inputs_D41): 3.7.3 in one log (EW A, EW B, COL A, COL B), 2.3.3 in four logs."""
    xs = [tuple(map(float, m)) for m in re.findall(r"Cross-section :\s+([0-9.eE+-]+) \+- ([0-9.eE+-]+) pb", open(f"{IN}/mg5_373_run.log").read())]
    assert len(xs) == 4; out = {}
    for ver, vals in (("3.7.3", xs), ("2.3.3", [tuple(map(float, re.findall(r"Cross-section :\s+([0-9.eE+-]+) \+- ([0-9.eE+-]+) pb", open(f"{IN}/{d}_gen.log").read())[-1]))
                                                for d in ("EW_A_233", "EW_B_233", "COL_A_233", "COL_B_233")])):
        for b, (a, bb) in (("EW", (vals[0], vals[1])), ("COL", (vals[2], vals[3]))):
            r = bb[0] / a[0]; out[(ver, b)] = dict(sA=a, sB=bb, r=r, dr=r * np.hypot(a[1] / a[0], bb[1] / bb[0]))
    return out

def d41(tag="mg5_373_lo"):
    """EW sample B (pp -> qe+ qe- j, ptj 200, LO): contiguous finished events of the append-only checkpoint."""
    f = f"{LOG}/D41_{tag}_events.jsonl"
    if not os.path.exists(f): return None
    rows = [r for l in open(f) for r in json.loads(l)]; d = pd.DataFrame(rows); ev = sorted(d.event.unique())
    n = next((i for i, e in enumerate(ev) if e != i), len(ev))
    if tag == "mg5_373_lo" and os.environ.get("D41_NMAX"): n = min(n, int(os.environ["D41_NMAX"]))   # one snapshot for the report and its figures
    d = d[d.event < n]
    out = dict(n=n, err=int((d.error.astype(str) != "").sum()))
    for lam in (1, 2, 3, 4, 5):
        x = d[d.lambda_keV == lam]; fid = x[x.fid.astype(bool)]; fin = fid[fid.final.astype(bool)]
        out[lam] = dict(fid=len(fid), sr=len(fin), plane=int(fid.plane.astype(bool).sum()), ds_med_um=float(fin.ds.median() * 1e4) if len(fin) else np.nan,
                        dw_med_cm=float(fid[fid.plane.astype(bool)].dw.median()) if len(fid) else np.nan)
    return out

def fig2():
    D = f"{T}/fig2_final"; pl = pd.read_csv(f"{D}/fig2_paper_L.csv"); pdd = pd.read_csv(f"{D}/fig2_paper_d.csv")
    ours = {k: pd.read_csv(f"{D}/fig2_ours_{k}.csv") for k in ("constructed", "key8")}
    def minima(x, y):
        i = np.where((y[1:-1] < y[:-2]) & (y[1:-1] <= y[2:]))[0] + 1; res = []
        for k in i:
            x0, x1, x2 = x[k - 1:k + 2]; y0, y1, y2 = y[k - 1:k + 2]; den = (x0 - x1) * (x0 - x2) * (x1 - x2)
            A = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / den; B = (x2 ** 2 * (y0 - y1) + x1 ** 2 * (y2 - y0) + x0 ** 2 * (y1 - y2)) / den; C = y1 - A * x1 ** 2 - B * x1
            xv = -B / (2 * A) if A > 0 else x1; res.append((xv, A * xv ** 2 + B * xv + C if A > 0 else y1))
        return res
    def summary(rL, L, rd, d):
        s = rd <= 5.0; dm = [m for m in minima(rd[s], d[s]) if 0.05 < m[0] < 5]
        lz = [m for m in minima(rL[rL <= 5.0], L[rL <= 5.0]) if m[1] < 0.05 * L.max() and 0.05 < m[0] < 5]
        lz = [m for i, m in enumerate(lz) if i == 0 or m[0] - lz[i - 1][0] > 0.05]
        return dict(dmax=float(d[s].max()), spacing=float(np.mean(np.diff([m[0] for m in dm]))), Lpk=float(L[rL <= 5].max()),
                    Lapp=[float(np.interp(r, rL, L)) for r, _ in dm], rapp=[float(r) for r, _ in dm], lz=[float(r) for r, _ in lz])
    S = {"paper": summary(pl.r_cm.values, pl.L_1e12_hbar.values, pdd.r_cm.values, pdd.d_cm.values)}
    for k, x in ours.items(): S[k] = summary(x.r_cm.values, x.L_1e12_hbar.values, x.r_cm.values, x.d_cm.values)
    # signed change of L per half-oscillation (sign flipped at each |L| zero)
    P = S["paper"]; sg = lambda r: (-1) ** sum(z < r for z in P["lz"]); v = [0.0] + [sg(r) * l for r, l in zip(P["rapp"], P["Lapp"])]; S["paper"]["dL_half"] = list(np.diff(v))
    assert abs(S["constructed"]["Lpk"] - 0.643) < 0.002 and abs(S["key8"]["Lpk"] - 0.862) < 0.002 and abs(S["paper"]["Lapp"][1] - 0.194) < 0.002
    return S, pl, pdd, ours

def checks():
    """Numbers of the Fig. 2 / annihilation / width / step-size investigations, read from their output files."""
    o = {}
    t = open(f"{T}/D17_fig2_torque_decomposition.txt").read()
    m = re.findall(r"\(B\) initial CM frame.*?\n.*?\n((?:\s+\d.*\n){4})", t)
    rows = [list(map(float, l.split()[2:7])) for l in m[0].strip().splitlines()]          # dL EM string frame sum (constructed event)
    o["torque_constructed"] = rows
    t = open(f"{T}/D18_fig2_B0_string_test.txt").read(); o["B0_turning"] = [float(v) for v in re.findall(r"max (0\.8\d+)", t)]
    t = open(f"{T}/D22_fig2_L_residual_annihilation.txt").read()
    o["L_residual"] = [(int(a), float(b), float(c)) for a, b, c in re.findall(r"^\s*(\d+) steps/period.*?\| ([+-][0-9.e+]+) hbar.*?\| [+-][0-9.e+]+ hbar.*?\| ([+-][0-9.e+]+) hbar", t, re.M)]
    o["annih_A"] = pd.read_csv(f"{T}/D27_annihilation_A.csv")
    o["toyB"] = open(f"{T}/D27_annihilation_B.txt").read(); o["toyC"] = open(f"{T}/D28_quantum_toy_checks.txt").read()
    o["D29"] = pd.read_csv(f"{T}/D29_li_pei_formulas.csv"); o["D32"] = pd.read_csv(f"{T}/D32_cm_time_string_reco.csv")
    o["D14"] = pd.read_csv(f"{T}/D14_step_convergence.csv"); o["D26"] = pd.read_csv(f"{T}/D26_stepwise_cutflow.csv")
    o["P24"] = pd.read_csv(f"{T}/fig5_author_population.csv")
    return o

if __name__ == "__main__":
    C = production(); print({s: {k: v for k, v in c.items() if not isinstance(k, tuple)} for s, c in C.items()})
    print(backgrounds()); print(lo_trigger()); D = d41(); print({k: D[k] for k in D}); S = fig2()[0]; print(S); ch = checks(); print(ch["torque_constructed"], ch["B0_turning"], ch["L_residual"])
