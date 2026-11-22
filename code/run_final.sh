#!/bin/bash
# Final multi-seed run for the manuscript. Run from the sybil_pipeline folder, inside the venv:
#   caffeinate -i bash run_final.sh
# (caffeinate keeps the Mac awake). Expects FULL feature files in ../features
# (run "python convert_veremi.py" first, WITHOUT --max-receivers).
# Settings: SEEDS and the sample sizes below. Logs go to results_final/logs.
set -e
cd "$(dirname "$0")"
FEAT=../features
OUT=results_final
SEEDS="0 1 2 3 4"
SIZES="--ext-n 300000 --ng-train-n 300000 --ng-val-n 100000 --ng-test-n 500000"
mkdir -p "$OUT/logs"
start=$(date +%s)
for s in $SEEDS; do
  D="$OUT/seed$s"; mkdir -p "$D"
  echo "=== seed $s: E1-E4 $(date +%H:%M)"
  python experiments.py --feat-dir "$FEAT" --out "$D" $SIZES --seed "$s" --only E1,E2,E3,E4 > "$OUT/logs/experiments_seed$s.log" 2>&1
  echo "=== seed $s: E7 shortcut fixes $(date +%H:%M)"
  python shortcut.py --feat-dir "$FEAT" --out "$D" $SIZES --seed "$s" > "$OUT/logs/shortcut_seed$s.log" 2>&1
  echo "=== seed $s: E8 leave-one-type-out $(date +%H:%M)"
  python loto.py --feat-dir "$FEAT" --out "$D" $SIZES --ng-test-n 50000 --seed "$s" > "$OUT/logs/loto_seed$s.log" 2>&1
done
echo "=== seed 0: E6 ablation $(date +%H:%M)"
python experiments.py --feat-dir "$FEAT" --out "$OUT/seed0_e6" $SIZES --seed 0 --only E6 --models HGB > "$OUT/logs/ablation_seed0.log" 2>&1
cp "$OUT/seed0_e6/all_results.csv" "$OUT/seed0_e6_results.csv"
python - <<'PY'
import pandas as pd
a = pd.read_csv('results_final/seed0/all_results.csv'); b = pd.read_csv('results_final/seed0_e6_results.csv')
pd.concat([a, b[b.exp == 'E6']], ignore_index=True).to_csv('results_final/seed0/all_results.csv', index=False)
PY
echo "=== seed 0: feature reliance evidence $(date +%H:%M)"
python evidence.py --feat-dir "$FEAT" --out "$OUT/seed0" $SIZES --seed 0 > "$OUT/logs/evidence_seed0.log" 2>&1
echo "=== aggregating $(date +%H:%M)"
python aggregate.py --root "$OUT" > "$OUT/logs/aggregate.log" 2>&1
echo "Done in $(( ($(date +%s) - start) / 60 )) minutes. Results: $OUT/final_tables.md"
