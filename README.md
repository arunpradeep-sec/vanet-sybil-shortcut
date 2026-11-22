# Shortcut learning and attack-coverage gaps in VANET Sybil detection

Code and result tables for the paper

> N. C. Velayudhan, A. Pradeep, M. Madanan, *Shortcut Learning and Attack-Coverage Gaps in VANET Sybil Detection:
> A Cross-Dataset Study on VeReMi Extension and VeReMi NextGen* (submitted to *Vehicular Communications*).

The study converts the Sybil subsets of **VeReMi Extension** and **VeReMi NextGen** to one receiver-side message schema,
describes every received beacon with the same 21 features, and evaluates tree ensembles under eight protocols:
in-domain, cross-density, NextGen official split, cross-dataset, a one-line new-pseudonym rule, feature-group ablation,
shortcut fixes and leave-one-Sybil-type-out. It adds an LSTM sequence baseline and an on-board latency benchmark
(Raspberry Pi 4B).

## Folder layout

```
repo/
  code/              all scripts (run them from this folder)
  results/           the result tables reported in the paper
  VeReMi_Extension/  put the downloaded Extension Sybil zips here   (not in git)
  VeReMi_NextGen/    put the downloaded NextGen Sybil zips here     (not in git)
  features/          written by convert_veremi.py                   (not in git)
```

Datasets: see the VeReMi project page, https://veremi-dataset.github.io/. Needed are the eight Extension archives
`{GridSybil,DataReplaySybil,DoSRandomSybil,DoSDisruptiveSybil}_{0709,1416}.zip` and the four NextGen archives
`InTAS_{urban,highway}_{2,7}_trafficCongestionSybil.zip`. The zips are read directly; nothing needs unpacking.

## Setup

Python 3.11 or newer.

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

PyTorch is needed only for `lstm_baseline.py`.

## Reproducing the paper

All commands are run from `code/`.

| Step | Command | Produces | Time (Apple M2) |
| --- | --- | --- | --- |
| 1. Features | `python convert_veremi.py` | `../features/*.pkl.gz` (44.3 M messages) | several hours |
| 2. Main experiments E1-E8, 5 seeds | `bash run_final.sh` | `results_final/final_tables.md`, `final_*.csv` | about 3 h |
| 3. LSTM baseline, 3 seeds | `python lstm_baseline.py` | `results_lstm/` | about 20 min |
| 4. Latency kit | `python latency_prep.py` | `../latency_kit/` | about 10 min |
| 5. Latency benchmark | `python3 latency_bench.py` (inside `latency_kit/`, on the target device) | `latency_<host>.json` | 15-20 min on a Pi 4B |

Quick checks: `python convert_veremi.py --test` converts only the two smallest subsets; `python lstm_baseline.py --quick`
and `python3 latency_bench.py --quick` run in a few minutes.

On the Raspberry Pi only `numpy` and `scikit-learn` are needed (`pip install numpy scikit-learn`; on 32-bit
Raspberry Pi OS also `sudo apt install libopenblas0`).

## Scripts

| Script | Purpose |
| --- | --- |
| `convert_veremi.py` | Reads both datasets from their zips, harmonises them and computes the 21 features per received message |
| `experiments.py` | E1 in-domain, E2 cross-density, E3 NextGen official split, E4 cross-dataset, E5 rule baseline, E6 ablation |
| `shortcut.py` | E7 shortcut fixes: drop pseudonym-age or history features, history masking, mixed training |
| `loto.py` | E8 leave-one-Sybil-type-out within Extension |
| `evidence.py` | Permutation importance, false alarms on genuine first messages, ROC curves |
| `aggregate.py` | Mean +- standard deviation over seeds; writes the final tables |
| `run_final.sh` | Runs all of the above for seeds 0-4 |
| `lstm_baseline.py` | LSTM over each pseudonym's last 8 messages against HGB on identical samples |
| `latency_prep.py`, `latency_bench.py` | Online feature extraction and per-message inference timing on one CPU core |

## Results in `results/`

* `main/final_tables.md` - every table of Section 7 (mean +- s.d. over 5 seeds); `final_*.csv` - the same as CSV
* `lstm/` - LSTM against HGB (Table 13)
* `latency/` - Raspberry Pi 4B and Apple M2 timing (Table 14)
* `feature_manifest.csv` - messages, Sybil share, receivers and senders per converted subset

## Licence

Code: MIT (see `LICENSE`). The VeReMi datasets keep their own licences.
