#!/bin/bash
# Supplementary analyses (Sections 4.5 and 7.12-7.17) on the FULL feature files.
# Run from the sybil_pipeline folder, inside the venv:   caffeinate -i bash run_supp.sh
set -e
cd "$(dirname "$0")"
export FEAT=../features OUT=results_supp
mkdir -p $OUT
start=$(date +%s)
echo "=== 1/4 sampling feature files $(date +%H:%M)";  python build_sample.py > $OUT/log_sample.txt 2>&1
echo "=== 2/4 shift, curves, learning, tuning $(date +%H:%M)"; python analyses.py > $OUT/log_analyses.txt 2>&1
echo "=== 3/4 learners, delay, noise $(date +%H:%M)"; python zoo_delay.py > $OUT/log_zoo.txt 2>&1
echo "=== 4/4 delay per attack type $(date +%H:%M)"; python delay2.py > $OUT/log_delay2.txt 2>&1
rm -f $OUT/sample.pkl $OUT/blocks.pkl
echo "Done in $(( ($(date +%s) - start) / 60 )) minutes. Results in sybil_pipeline/$OUT"
