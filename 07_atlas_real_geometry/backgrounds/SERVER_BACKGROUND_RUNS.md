# Background runs on the server: exact commands (2026-11-17)

## What the chain needs

**Code (in git).** All of it is tested by T12, which reproduces the production rows exactly with the default options (`logs/T12_c01_server_options.log`):
- `07_atlas_real_geometry/backgrounds/C01_conversion_bkg.py` and `S01_conversion_summary.py`;
- `07/sim/` (`detsim07.py`, `cop07.py`);
- `02_backgrounds/pileup/` and `02_backgrounds/photon_conversion/`;
- `04_detector_sim/`, `05_coplanarity_analysis/coplanarity_fit.py`.

**Paths.** All paths come from `COPLANARITY_BASE`, the repository root.

**New options (2026-11-17)**

| Script | Option | Effect |
|---|---|---|
| C01 | `--photons CSV` | photon sample to use |
| C01 | `--pool CSV` | minimum-bias pool to use (.csv, .csv.gz, .csv.xz) |
| C01 | `--pileup-only` | no photon pair; pile-up hits only |
| S01 | `--xsec FILE` | cross-section file with keys `sigma_generated_pb`, `n_events_after_MET`, and optional `n_generated` (default 10000) |

**Inputs**

| Input | Where | In git |
|---|---|---|
| 9 130 Z(νν̄)γ photons (production) | `06_publication/S2_13p6TeV_run3_knapen_noPU_cop/inputs/zgamma_13p6TeV/zgamma_photons.csv` | yes |
| Zγ cross section (production) | `06_.../inputs/zgamma_xsec_13p6TeV.txt` | yes |
| 100k Zγ photons (made in step a) | `07/backgrounds/inputs_zgamma_large/zgamma_photons_large.csv` and `zgamma_xsec_large.txt` | after step (a) |
| Minimum-bias pool, 20 000 events, 13.6 TeV, seed 20260916 (252 MB) | `06_.../inputs/minbias_pool_20000_13p6TeV.csv`, sha256 `52b465f520867cc0ee1597cca242a6f687717295d28df4cf02dd04246aa6126b` | no (too large): copy `~/minbias_pool_20000_13p6TeV.csv.gz` (99 MB) or regenerate (below) |

**Python.** The hep env (Pythia8 8.312, numpy, pandas), e.g. the conda-pack `~/hep_env.tar.gz` unpacked on the server.

On the server, set once per shell:

```bash
export COPLANARITY_BASE=$HOME/coplanarity_study          # repository root on the server
export HEP=$HOME/hep_env                                  # unpacked hep env (conda-pack)
export PYTHIA8DATA=$HEP/share/Pythia8/xmldoc
P=$HEP/bin/python
S2=$COPLANARITY_BASE/06_publication/S2_13p6TeV_run3_knapen_noPU_cop
cd $COPLANARITY_BASE/07_atlas_real_geometry/backgrounds
mkdir -p ../logs
```

**Getting the minimum-bias pool**, one of:

```bash
# (1) copy the laptop pool and unpack it
gunzip -c ~/minbias_pool_20000_13p6TeV.csv.gz > $S2/inputs/minbias_pool_20000_13p6TeV.csv
# (2) regenerate it with the same seed (about 2 min); accept it only if the sha256 matches
$P $S2/S2_07_minbias_pool.py 20000 13600 $S2/inputs/minbias_pool_20000_13p6TeV.csv
sha256sum $S2/inputs/minbias_pool_20000_13p6TeV.csv      # must be 52b465f5...126b, else use (1)
```

Runs on the laptop have shown that floating-point results can differ between machines (RESULTS §9). If (2) does not reproduce the checksum, use (1).

**Observed on the server (2026-11-17).** Option (2) gave sha256 `94e81e1f…`, not `52b465f5…`: same seed and code, different machine floating point inside Pythia. The pool test (c) shows the two pools are statistically equivalent (RESULTS §7). Runs that use this default pool are valid, but they do not use the exact laptop pool. Use (1) whenever a run must match the laptop production row by row.

## Runtime estimates

The estimates use the measured laptop cost per photon per worker, assuming one server core is about as fast as one laptop core (uncertainty about ×2 either way). 100k generated events give about 91 300 photons after MET > 200 GeV.

| Run | Cost per photon (s × worker) | Source |
|---|---|---|
| ATLAS, μ = 0 | ≈ 0.5–1 (estimate) | — |
| ATLAS, μ = 20 | 2.1 | `C01_chain.log` |
| ATLAS, μ = 50 | 11.8 | A580, `C01_chain_A580.log` |
| Ideal (stage2), μ = 0 | 0.02 | `C01_chain_stage2_A580.log` |
| Ideal (stage2), μ = 20 | 0.50 | same |
| Ideal (stage2), μ = 50 | 2.1 | same |

**Memory.** Each worker loads the pool (a few hundred MB). 40 workers need about 20–40 GB. With 160 cores, four 40-worker jobs can run at the same time.

## (a) Zγ 100k generation and photon extraction (laptop)

10 independent MG5 runs of 10 000 events. Each uses the production cards of 06 S2 (13.6 TeV) and changes only iseed (271000 + chunk). Photons are extracted with the Stage 2 extractor.

- Chunk 0 was run as a test on 2026-11-17: 5.0 min, σ = 0.2513 pb (production 0.2521 pb), 9 128 photons after MET (production 9 130).
- The script resumes and skips chunk 0.
- **Done 2026-11-17:** 10 chunks, 100 000 generated, 90 980 photons after MET, σ = 0.25074 pb (event-weighted mean; chunk spread 0.2493–0.2527 pb), `logs/Z01_zgamma_large.log`.

```bash
cd ~/coplanarity_study/07_atlas_real_geometry
/home/rafia/miniconda3/envs/hep/bin/python backgrounds/Z01_zgamma_large.py 10 0 > logs/Z01_zgamma_large.log 2>&1   # about 45 min (9 chunks x 5 min)
tail -2 logs/Z01_zgamma_large.log                       # Z01: ... generated 100000, photons after MET ~91 300 ... Z01_EXIT=0
git add backgrounds/inputs_zgamma_large/zgamma_photons_large.csv backgrounds/inputs_zgamma_large/zgamma_xsec_large.txt \
        backgrounds/inputs_zgamma_large/chunks.csv logs/Z01_zgamma_large.log
git commit -m "07: Z(nunu)gamma 100k photons (Z01)" && git push
```

## (b) C01 A580 for Ideal and ATLAS, μ = 0 / 20 / 50, 100k photons (server)

```bash
git pull
PH=inputs_zgamma_large/zgamma_photons_large.csv
for mu in 0 20 50; do
  setsid nohup $P C01_conversion_bkg.py atlas  $mu --sct A580 --photons $PH --tag A580_100k --workers 40 > ../logs/C01_atlas_A580_100k_mu$mu.log  2>&1 < /dev/null &
done
# the Ideal runs are cheap: run them one after another in one job
setsid nohup bash -c "for mu in 0 20 50; do $P C01_conversion_bkg.py stage2 \$mu --sct A580 --photons $PH --tag A580_100k --workers 40; done" \
      > ../logs/C01_stage2_A580_100k.log 2>&1 < /dev/null &
# when all show C01_EXIT=0:
X=inputs_zgamma_large/zgamma_xsec_large.txt
$P S01_conversion_summary.py --xsec $X runs/C01_atlas_A580_100k_mu0  runs/C01_atlas_A580_100k_mu20  runs/C01_atlas_A580_100k_mu50
$P S01_conversion_summary.py --xsec $X runs/C01_stage2_A580_100k_mu0 runs/C01_stage2_A580_100k_mu20 runs/C01_stage2_A580_100k_mu50
git add runs/C01_*_A580_100k_mu* ../tables/S01_C01_*_A580_100k_mu*.csv ../logs/C01_*A580_100k*.log
git commit -m "07: C01 A580 with 100k Zgamma photons, Ideal and ATLAS, mu 0/20/50" && git push
```

| Job (40 workers) | Estimated time |
|---|---|
| ATLAS A580, μ = 0 | 0.3–0.6 h |
| ATLAS A580, μ = 20 | ≈ 1.3 h |
| ATLAS A580, μ = 50 | **≈ 7.5 h** (the longest job) |
| Ideal A580, μ = 0 + 20 + 50 together | < 1 min + ≈ 20 min + ≈ 1.3 h |

The ATLAS runs take about 8 h in total if run in parallel. Expected output size is about 80 MB for ATLAS μ = 50 and less for the others.

**Expected gain.** With 10× more photons:
- the upper limit when none pass drops from 1.29 to about 0.13 events (ATLAS) and from 0.25 to about 0.025 events (Ideal);
- the relative MC error of the A580 background drops from 58–71% to about 20%.

**After pulling, on the laptop.** R01 and X08 read the S01 tables by name. Their file names are switched to the `_100k` tables, then `reach/R00_postprocess.sh` is rerun.

**Done 2026-11-18.** Pushed by the server (commit 9bef53e0). On the laptop: R01, X08, X11 and S02 switched to the `_100k` runs (S02 and X11 use `zgamma_xsec_large.txt` for them), R00 rerun (T09, T11 pass). A580 background at 332 fb⁻¹, μ = 0 / 20 / 50: ATLAS 0 / 0.069 / 0.198, Ideal 0 / 0.092 / 0.108 events (RESULTS headline and §7).

## (c) Pool test: a new-seed 20k pool, Z0 at μ = 50 (server)

Z0 at μ = 50 has 687 passing photons, so a pool effect larger than the MC error (about 6%) would be visible. The same photons and seeds are used; only the pool changes.

```bash
mkdir -p inputs_pool_test
$P $S2/S2_07_minbias_pool.py 20000 13600 inputs_pool_test/minbias_pool_20000_13p6TeV_seed20261117.csv 20261117      # about 2 min
setsid nohup $P C01_conversion_bkg.py atlas 50 --sct Z0 --pool inputs_pool_test/minbias_pool_20000_13p6TeV_seed20261117.csv \
      --tag pooltest_seed20261117 --workers 40 > ../logs/C01_atlas_pooltest_mu50.log 2>&1 < /dev/null &                # about 45 min
# optional: a 125k pool (about 8 min to generate; each worker then holds about 6 times more memory)
$P $S2/S2_07_minbias_pool.py 125000 13600 inputs_pool_test/minbias_pool_125000_13p6TeV_seed20261118.csv 20261118
setsid nohup $P C01_conversion_bkg.py atlas 50 --sct Z0 --pool inputs_pool_test/minbias_pool_125000_13p6TeV_seed20261118.csv \
      --tag pooltest_125k --workers 40 > ../logs/C01_atlas_pooltest125k_mu50.log 2>&1 < /dev/null &                   # about 1 h
# when done:
$P S01_conversion_summary.py runs/C01_atlas_pooltest_seed20261117_mu50 runs/C01_atlas_pooltest_125k_mu50
```

**Comparison.** Production Z0 at μ = 50 is 69.2 ± 4.4 events (687 passing photons, `tables/S01_C01_atlas_mu50.csv`).
- Agreement within about ±9 events (2σ of the two MC errors combined) means the 20k pool (each event reused about 23 times at μ = 50) is adequate.
- A larger difference is a pool systematic.

**Result (2026-11-17, `compare/X09_pool_test.py`).** Test 77.3 ± 5.1 vs production 69.2 ± 4.4. The paired difference is +8.1 ± 6.5 (1.3σ), within the criterion, so the 125k pool was not run. Most of the difference is in Pixel B0 (8 → 14 passing photons, +4.7 events). It is kept as a conservative ~12% pool systematic on Z0 at μ = 50.

The pool files are inputs, not results. Do not commit them; commit only the `runs/C01_atlas_pooltest*` folders and the S01 tables.

## (d) Pile-up-only background in the ATLAS geometry (server)

**What it measures.** No photon pair is simulated; the event has only the pile-up hits around a primary vertex. Photon i provides only the seeds and z0, so the pile-up is the same as in the conversion runs. The result is the probability per bunch crossing that pile-up alone passes the COP selection.

Before this, it was measured only in the Ideal geometry: Z1160, 5 000 events, 0 passing (< 6 × 10⁻⁴ per event).

```bash
PH=inputs_zgamma_large/zgamma_photons_large.csv
for sct in A580 Z0; do for mu in 20 50; do
  setsid nohup $P C01_conversion_bkg.py atlas $mu --sct $sct --pileup-only --photons $PH --first 20000 --tag PUonly_${sct} --workers 40 \
        > ../logs/C01_atlas_PUonly_${sct}_mu$mu.log 2>&1 < /dev/null &
done; done
# when done: S01 reports pass_prob_per_event and pass_prob_UL95_if_zero (3 / n)
$P S01_conversion_summary.py runs/C01_atlas_PUonly_A580_mu20 runs/C01_atlas_PUonly_A580_mu50 runs/C01_atlas_PUonly_Z0_mu20 runs/C01_atlas_PUonly_Z0_mu50
```

| Job (40 workers, 20 000 events) | Estimated time |
|---|---|
| μ = 20 | ≈ 20 min each |
| μ = 50 | ≈ 1.6 h each |

With 0 passing events the upper limit is 1.5 × 10⁻⁴ per event. The T12 test run (20 events, μ = 50, Z0) gave 11 planes and 0 passing events.

**How to use the result.** This probability multiplies the number of triggered events. Every MET-triggered event (Z(νν̄)+jets, W+jets, Zγ; about 10⁷ at 332 fb⁻¹, `BACKGROUND_CANDIDATES.md` A) carries pile-up. Even 0 passing out of 20 000 therefore does not prove the background is below one event. Factorising the rate (plane rate × multiplicity × Δs/Δw pass fractions) would be needed; this is a step for later.

## (e) Sensitivity test: pixel-merge distance, μ = 50, 9 130 photons (server)

**What it measures.** The background with pixel merging at adjacency 0, 1 and 2, for Z0 and A580, in both geometries. Adjacency is the merge distance in pixel-index units; production uses 1 (touching pixels).
- Pixel indices are integers. A distance of 0.5 pixel (−50%) therefore merges only hits in the same pixel, which is adjacency 0. A distance of 1.5 pixels (+50%) merges exactly what adjacency 1 merges.
- So adjacency 0 (−50% and −100%) and adjacency 2 (+100%) are the variants that change anything.
- The multiplicity threshold (14 / 15 / 16) is applied afterwards by `compare/X11_merge_mult_sensitivity.py`. Test T13 checks that this after-the-fact threshold reproduces the stored `mult` on every row.

**Pool and reference.** Each variant is compared with the **server** adjacency 1 run, so that machine floating point (RESULTS §9) cancels. Use the laptop pool (option (1) above) so that the pool is also identical.

```bash
POOLL=$S2/inputs/minbias_pool_20000_13p6TeV.csv        # unpacked laptop pool, sha256 52b465f5...126b
for sct in Z0 A580; do for a in 0 1 2; do
  setsid nohup $P C01_conversion_bkg.py atlas 50 --sct $sct --merge-adj $a --pool $POOLL --tag sens_${sct}_a$a --workers 40 \
        > ../logs/C01_atlas_sens_${sct}_a${a}_mu50.log 2>&1 < /dev/null &
done; done
# Ideal (cheap): one job, run one after another
setsid nohup bash -c "for sct in Z0 A580; do for a in 0 1 2; do $P C01_conversion_bkg.py stage2 50 --sct \$sct --merge-adj \$a --pool $POOLL --tag sens_\${sct}_a\$a --workers 40; done; done" \
      > ../logs/C01_stage2_sens_mu50.log 2>&1 < /dev/null &
# when all show C01_EXIT=0:
git add runs/C01_*_sens_*_mu50 ../logs/C01_*sens*.log
git commit -m "07: C01 merge-adjacency sensitivity (0/1/2), Z0 and A580, mu = 50, ATLAS and Ideal" && git push
```

| Job (40 workers) | Estimated time |
|---|---|
| ATLAS, each of 6 runs (Z0 / A580 × adjacency 0 / 1 / 2) | ≈ 45 min (≈ 0.7 h if all six share 160 cores: about 4 at a time) |
| Ideal, 6 runs one after another | ≈ 6 × 8 min ≈ 50 min |

The whole of (e) takes about 1.5–2 h on 160 cores (uncertainty about ×2). After pulling, `compare/X11_merge_mult_sensitivity.py` adds the variants to `tables/X11_background_sensitivity.csv`.
