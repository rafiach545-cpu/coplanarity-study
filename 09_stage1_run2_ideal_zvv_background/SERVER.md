# 09 on the server

Written 2026-11-20. From now on, heavy runs go to the server: B08 at 25 keV, W(ℓν)+jets, tt̄ and the large Z(νν̄) background.

## What the pipeline needs

| Piece | Used by | Version | Install |
|---|---|---|---|
| MG5_aMC | B01 | 3.7.3 (git tag `v3.7.3`) | git clone (below) |
| Pythia8 + HepMC2 + MG5aMC_PY8_interface | B01 (shower through MG5) | Pythia **8.317**, HepMC **2.06.09** (as on the laptop) | MG5 `install pythia8` |
| conda env `mg5` | B01 | Python 3.11, numpy, pandas, six, C/C++/Fortran compilers, make, rsync, curl | `env/mg5_environment.yml` |
| conda env `g4` | B03, B05, B07, B08, B09, g4/ | Python 3.13; numpy, pandas, numba, uproot; pythia8 = 8.312 (its Python module gives the particle charges); Geant4 11.4.1, HepMC3, CMake | `env/g4_lock_linux64.txt` (exact laptop packages) or `env/g4_environment.yml` |
| Geant4 / QuirkPheno | only `g4/` (validation, not the B chain) | Geant4 11.4.1, QuirkPheno d91cb27 | optional, see `/home/rafia/hep_tools/g4_setup/README.md` |

Checked on the laptop (2026-11-20): B03 run in env `g4` reproduces all 38 result columns of the laptop B03 run (env `hep`) exactly, on 30 events.

All paths come from `paths09.py`, and each can be overridden: `COPLANARITY_BASE` (repository root), `HEP_TOOLS` (MG5 and run folders), and `ZVV_RUNS`, `WLNU_RUNS`, `SIGNAL_10K_RUNS`, `B05_HEPMC`, `QUIRKPHENO`.

## (a) Installation (once)

```bash
cd $HOME
git clone https://github.com/rafiach545-cpu/coplanarity-study.git coplanarity_study
cd coplanarity_study && git checkout transfer-2026-10-02
export COPLANARITY_BASE=$HOME/coplanarity_study HEP_TOOLS=$HOME/hep_tools      # put these two lines in ~/.bashrc
D=$COPLANARITY_BASE/09_stage1_run2_ideal_zvv_background

conda env create -f $D/env/mg5_environment.yml
conda create -n g4 --file $D/env/g4_lock_linux64.txt      # or: conda env create -f $D/env/g4_environment.yml

mkdir -p $HEP_TOOLS && cd $HEP_TOOLS
git clone --depth 1 --branch v3.7.3 https://github.com/mg5amcnlo/mg5amcnlo.git MG5_aMC_v3_7_3
conda activate mg5 && cd MG5_aMC_v3_7_3
sed -i 's/^#\? *auto_update *=.*/auto_update = 0/' input/mg5_configuration.txt
printf 'install pythia8\n' > /tmp/inst.mg5 && ./bin/mg5_aMC /tmp/inst.mg5   # downloads and builds Pythia 8.317, HepMC 2.06.09 and the interface
HEPTools/pythia8/bin/pythia8-config --version                             # must print 8.317
```

`install pythia8` needs HTTPS access to launchpad.net and pythia.org. If the server allows only git and conda, copy two things from the laptop with `scp` or `rsync`:
- `/home/rafia/hep_tools/MG5_aMC_v3.7.3.tar.gz`;
- the `HEPTools/HEPToolsInstallers` folder, then run `install pythia8 --local`.

Smoke test, the Z(νν̄) pilot (1000 events). It also builds the MG5 process template, so run it before any parallel jobs:

```bash
cd $D && conda activate mg5
python B01_generate_zvv.py 1 0 --nev 1000 --cores 8
```

σ must agree with the laptop pilot, 9.97 pb, within about 1 %.

The pilot writes chunk 0. The laptop table `data/B01_chunks.csv` already has chunks 0–10, and the server's chunk 0 replaces the laptop's chunk-0 row. Use chunk numbers ≥ 11 for new server chunks, so the seeds (391000 + chunk) never repeat a laptop chunk.

## (b) Finishing B08: the 25 keV part

The 0.1–10 keV part runs on the laptop. The CSVs `data/B08_EW_<m>gev_L0.1-10.csv` are copied to the server with git or scp. Only Λ = 25 keV is left. It reaches the 2 × 10⁷-step ceiling and needs about 1–2 GB per worker.

B08 reads the 07 signal HepMC (13.6 TeV, 10k generated per mass, 8.1 GB in total). Take one of the two routes:

1. **Copy (same events as the laptop):**
   ```bash
   rsync -av laptop:/home/rafia/hep_tools/07_large_runs/EW_{100,400,800,1200}gev_c0? $HEP_TOOLS/07_large_runs/
   ```
2. **Regenerate (same seeds; identical events only with the same MG5 and Pythia):**
   ```bash
   COPLANARITY_BASE=... S2B_RUNS=$HEP_TOOLS/07_large_runs python $COPLANARITY_BASE/07_atlas_real_geometry/signal/G02_large_samples.py gen --points EW:100,EW:400,EW:800,EW:1200
   ```
   This needs the Stage 2 MG5 quirk template process directory. It is not in git, so copy `hep_tools/S2_13p6TeV_runs` as well.

Then:

```bash
cd $D && conda activate g4
for m in 800 400 100 1200; do
  python B08_signal_cleaning_scan.py $m --lambdas 25 --workers 8 > logs/B08_EW_${m}_L25.log 2>&1
  mv data/B08_EW_${m}gev.csv data/B08_EW_${m}gev_L25.csv
done
```

To rerun all of B08 there, use `--lambdas 0.1,1,4,10,25`. Use `--workers` up to about RAM / 2 GB.

## (c) W(ℓν)+jets (ℓ = e, μ, τ)

The sample is defined in `paths09.SAMPLES["wlnu"]`:
- `p p > ℓ⁺ ν j` and `p p > ℓ⁻ ν̄ j`;
- the same cuts as Z(νν̄): `misset` 200 GeV, `ptj` 20 GeV;
- no charged-lepton cut (`ptl` = 0, no η cut);
- seeds 392000 + chunk.

```bash
cd $D && conda activate mg5
python B01_generate_zvv.py 1 0 --nev 1000 --sample wlnu --cores 8     # pilot; also builds the template (do this first)
conda activate g4
python B03_hits_and_planes.py 0 --sample wlnu --workers 8
python B09_cleaning_variants_bkg.py 0 --sample wlnu --workers 8
# production, e.g. 100 chunks of 10k, 8 chunks at a time (MG5 2 cores + 2 workers each = about 32 cores):
seq 1 100 | xargs -P 8 -I{} env NEV=10000 MG5_CORES=2 WORKERS=2 ./server_chunk.sh wlnu {}
```

`server_chunk.sh` runs B01 → B03 → B09 for one chunk and then deletes the HepMC (`KEEP_HEPMC=1` keeps it). The outputs are `data/wlnu_B03_*`, `data/wlnu_B09_*` and `data/B01_wlnu_chunks.csv`. The same command with `zvv` and chunks ≥ 11 extends the Z(νν̄) background.

## Cost (from laptop timings, 2026-11-19/20)

Per 10k events:
- B01: about 3.3 min wall on 10 cores;
- B03: about 300 s on 8 workers;
- B09: about 450 s on 4 workers.

That is about 130 core-minutes per 10k events, so 1M events ≈ 220 core-hours.

The HepMC is about 0.8 GB per 10k and is deleted after each chunk. The CSV outputs are about 10 MB per 10k.

**Do not start the large Z(νν̄) run before the cleaning choice is final.** The B07–B09 results decide it.
