#!/bin/bash
# Extra experiments for the revision-proofing step. Run from the sybil_pipeline folder, inside the venv:
#   caffeinate -i bash run_extra.sh
# 1) supplementary analyses repeated for seeds 0-4 (results_supp/seed0 ... seed4)
# 2) proposed transfer-robust detector, 5 seeds (results_robust/)
# 3) adaptive attacker with warm-up, 5 seeds (results_adaptive/)
set -e
cd "$(dirname "$0")"
export FEAT=../features
start=$(date +%s)
for S in 0 1 2 3 4; do
  export SEED=$S OUT=results_supp/seed$S; mkdir -p $OUT
  echo "=== seed $S: sampling $(date +%H:%M)"; python build_sample.py > $OUT/log_sample.txt 2>&1
  echo "=== seed $S: analyses $(date +%H:%M)"; python analyses.py > $OUT/log_analyses.txt 2>&1
  echo "=== seed $S: learners, delay, noise $(date +%H:%M)"; python zoo_delay.py > $OUT/log_zoo.txt 2>&1
  echo "=== seed $S: delay per type $(date +%H:%M)"; python delay2.py > $OUT/log_delay2.txt 2>&1
  rm -f $OUT/sample.pkl $OUT/blocks.pkl $OUT/A11_pseudo_*.csv
done
unset SEED OUT
echo "=== robust detector $(date +%H:%M)"; python robust.py > results_robust_log.txt 2>&1
echo "=== adaptive attacker $(date +%H:%M)"; python adaptive.py > results_adaptive_log.txt 2>&1
echo "Done in $(( ($(date +%s) - start) / 60 )) minutes."
