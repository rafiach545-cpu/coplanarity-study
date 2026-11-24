#!/usr/bin/env python3
"""regen_dop853: write MORNING_REPORT.md from whatever exists (also after a crash: every section is guarded).
Usage: report.py <regen_dop853 dir> <exit code> <start epoch> <reason text>"""
import os, sys, time, glob, shutil, traceback
RD = os.path.abspath(sys.argv[1]); RC = sys.argv[2]; T0 = float(sys.argv[3]); WHY = sys.argv[4] if len(sys.argv) > 4 else ""
OUT = f"{RD}/out"; REP = f"{RD}/MORNING_REPORT.md"; L = []
if os.path.exists(REP): REP = f"{RD}/MORNING_REPORT_{int(time.time())}.md"          # never overwrite


def sec(title, fn):
    L.append(f"\n## {title}\n")
    try: fn()
    except Exception as e: L.append(f"(section not available: {type(e).__name__}: {str(e)[:200]})")


def md(df, cols=None):
    import pandas as pd
    d = df[cols] if cols else df
    if not len(d): return "(none)"
    h = "| " + " | ".join(map(str, d.columns)) + " |\n|" + "---|" * len(d.columns) + "\n"
    return h + "\n".join("| " + " | ".join("" if (isinstance(v, float) and v != v) else (f"{v:g}" if isinstance(v, float) else str(v)) for v in r) + " |" for r in d.itertuples(index=False))


now = time.time()
L.append("# regen_dop853: morning report\n")
L.append(f"- Finished: {time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime(now))}; exit code {RC}{' (' + WHY + ')' if WHY else ''}")
L.append(f"- Wall time: {(now - T0) / 3600:.2f} h")
L.append(f"- Mode: {'DRY RUN (2 events per point, step 0 + one point of C)' if os.environ.get('DRYRUN') == '1' else 'full'}")


def s0():
    f = f"{OUT}/STEP0.txt"; L.append(open(f).read().strip() if os.path.exists(f) else "Step 0 did not finish (no STEP0.txt).")
sec("Step 0: reproduction of the laptop reference", s0)


def head():
    import pandas as pd
    f = f"{OUT}/reach/headline_A580_mu50.csv"
    if not os.path.exists(f): L.append("Not computed (step C missing or reach step not reached)."); return
    H = pd.read_csv(f); out = []
    for r in H.itertuples():
        fmt = lambda c: f"{r.__getattribute__(f'new_{c}'):.0f} [{r.__getattribute__(f'new_{c}_lo'):.0f}–{r.__getattribute__(f'new_{c}_hi'):.0f}]" if r.__getattribute__(f"new_{c}") == r.__getattribute__(f"new_{c}") else "n/a"
        ch = lambda c: f"{r.__getattribute__(f'change_{c}'):+.0f}" if r.__getattribute__(f"change_{c}") == r.__getattribute__(f"change_{c}") else "n/a"
        out.append(dict(channel=r.channel, geometry=r.geometry, **{"old excl/disc": f"{r.old_exclusion:.0f} / {r.old_discovery:.0f}",
                    "new excl/disc [±1σ]": f"{fmt('exclusion')} / {fmt('discovery')}", "change excl/disc": f"{ch('exclusion')} / {ch('discovery')}",
                    "tolerance": f"±{r.tolerance_GeV} GeV", "verdict": r.verdict}))
    L.append("13.6 TeV, 332 fb⁻¹, A580, μ = 50, converted-photon background (central b), reach in GeV:\n"); L.append(md(pd.DataFrame(out)))
    n = f"{OUT}/reach/REACH_NOTES.txt"
    if os.path.exists(n): L.append("\nNotes:\n\n" + "\n".join(f"- {x}" for x in open(n).read().splitlines()[:30]))
sec("Headline: reach old vs new", head)


def bench():
    import pandas as pd
    B = pd.read_csv(f"{OUT}/reach/benchmarks.csv"); L.append(md(B))
sec("Benchmarks (A580): n_fid, k, eps_reco old / new", bench)


def bkg():
    import pandas as pd
    R = pd.read_csv(f"{OUT}/reach/reach_old_and_new_332fb.csv"); x = R[(R.sct == "A580") & (R.mu == 50) & (R.contour == "exclusion")][["version", "setup", "channel", "N_bkg", "n_bkg_mc"]]
    L.append("The converted-photon background contains no quirk, so it is not re-simulated; the reach uses 07 tables/X08_background_used.csv unchanged.\n")
    L.append(md(x.drop_duplicates(["version", "setup"])[["version", "setup", "N_bkg", "n_bkg_mc"]]))
sec("Background at μ = 50 (A580), old / new", bkg)


def status():
    import pandas as pd
    S = pd.read_csv(f"{OUT}/status.tsv", sep="\t")
    L.append(md(S.groupby(["step", "status"]).size().reset_index(name="jobs")))
    m = S[S.status != "ok"]
    if len(m): L.append("\nJobs not ok:\n\n" + md(m[["job", "step", "status", "tries"]]))
    S["core_h"] = (S.end - S.start) * S.workers / 3600.0; L.append(f"\nCore-hours (wall x workers, upper bound): {S.core_h.sum():.1f}")
sec("Status of the steps (C, A, B, D)", status)


def flags():
    import pandas as pd
    C = pd.read_csv(f"{OUT}/CHECKS.csv"); L.append(md(C.groupby(["step", "nfid_check", "k_check"]).size().reset_index(name="points")))
    F = C[(C.nfid_check == "FLAG") | (C.k_check == "FLAG")]
    L.append(f"\nAll FLAGs ({len(F)}):\n\n" + md(F))
sec("Sanity checks and FLAGs", flags)


def disk():
    du = 0
    for dp, dn, fn in os.walk(RD):
        for f in fn:
            try: du += os.path.getsize(os.path.join(dp, f))
            except OSError: pass
    t, u, fr = shutil.disk_usage(RD); L.append(f"regen_dop853 uses {du / 1e9:.2f} GB; filesystem free {fr / 1e9:.0f} GB of {t / 1e9:.0f} GB ({100 * fr / t:.0f} %).")
sec("Disk", disk)


def files():
    L.append("New result files (out/reach/): " + ", ".join(sorted(os.path.basename(f) for f in glob.glob(f"{OUT}/reach/*"))))
    L.append("Logs: logs/; per-job status: out/status.tsv; checks: out/CHECKS.csv; code checksums: out/CODE_MD5.txt.")
sec("Files", files)
open(REP, "w").write("\n".join(L) + "\n"); print("report written:", REP)
