# Final results (mean ± std over seeds, %)

## E1–E5 main results

| exp | setting_g | model | f1 | mcc | auc | tpr_at_1fpr | fpr_at_val_thr1 | tpr_at_val_thr1 | prec | rec | fpr | seeds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | Ext 0709 | HGB | 93.82 ± 0.03 | 88.90 ± 0.06 | 98.68 ± 0.01 | 83.50 ± 0.18 | 0.99 ± 0.03 | 83.22 ± 0.42 | 95.33 ± 0.11 | 92.37 ± 0.07 | 3.74 ± 0.09 | 5 |
| E1 | Ext 0709 | RF | 93.79 ± 0.02 | 88.85 ± 0.02 | 98.59 ± 0.01 | 82.55 ± 0.14 | 0.98 ± 0.04 | 82.17 ± 0.60 | 95.43 ± 0.07 | 92.20 ± 0.08 | 3.65 ± 0.06 | 5 |
| E5 | Ext 0709 | rule | 69.61 ± 0.03 | 56.72 ± 0.04 | 75.76 ± 0.02 | 10.70 ± 0.04 | 5.32 ± 0.02 | 56.83 ± 0.02 | 89.84 ± 0.05 | 56.83 ± 0.02 | 5.32 ± 0.02 | 5 |
| E1 | Ext 1416 | HGB | 93.69 ± 0.01 | 88.27 ± 0.06 | 98.55 ± 0.02 | 83.78 ± 0.19 | 0.94 ± 0.10 | 82.61 ± 1.40 | 95.61 ± 0.29 | 91.85 ± 0.26 | 3.81 ± 0.27 | 5 |
| E1 | Ext 1416 | RF | 93.75 ± 0.03 | 88.38 ± 0.05 | 98.56 ± 0.02 | 83.61 ± 0.20 | 0.94 ± 0.09 | 82.06 ± 1.71 | 95.65 ± 0.14 | 91.92 ± 0.13 | 3.78 ± 0.13 | 5 |
| E5 | Ext 1416 | rule | 65.21 ± 0.02 | 52.49 ± 0.03 | 73.17 ± 0.01 | 11.47 ± 0.06 | 4.43 ± 0.02 | 50.78 ± 0.02 | 91.17 ± 0.05 | 50.78 ± 0.02 | 4.43 ± 0.02 | 5 |
| E2 | Ext 0709 -> 1416 | HGB | 93.61 ± 0.09 | 88.33 ± 0.11 | 98.59 ± 0.01 | 83.54 ± 0.13 | 0.83 ± 0.10 | 81.71 ± 1.04 | 96.64 ± 0.19 | 90.76 ± 0.33 | 2.85 ± 0.18 | 5 |
| E2 | Ext 0709 -> 1416 | RF | 93.59 ± 0.06 | 88.21 ± 0.05 | 98.44 ± 0.01 | 82.58 ± 0.16 | 0.81 ± 0.10 | 80.20 ± 1.30 | 96.21 ± 0.26 | 91.10 ± 0.34 | 3.24 ± 0.24 | 5 |
| E5 | Ext 0709 -> 1416 | rule | 65.23 ± 0.02 | 52.50 ± 0.03 | 73.17 ± 0.01 | 11.46 ± 0.06 | 4.43 ± 0.02 | 50.78 ± 0.02 | 91.18 ± 0.04 | 50.78 ± 0.02 | 4.43 ± 0.02 | 5 |
| E2 | Ext 1416 -> 0709 | HGB | 93.50 ± 0.14 | 88.16 ± 0.31 | 98.54 ± 0.01 | 82.24 ± 0.17 | 1.65 ± 0.28 | 86.63 ± 1.58 | 93.84 ± 0.80 | 93.17 ± 0.52 | 5.07 ± 0.72 | 5 |
| E2 | Ext 1416 -> 0709 | RF | 93.53 ± 0.10 | 88.26 ± 0.23 | 98.48 ± 0.01 | 80.27 ± 0.21 | 1.73 ± 0.23 | 86.18 ± 1.51 | 94.13 ± 0.58 | 92.95 ± 0.38 | 4.80 ± 0.51 | 5 |
| E5 | Ext 1416 -> 0709 | rule | 69.62 ± 0.02 | 56.72 ± 0.04 | 75.76 ± 0.02 | 10.69 ± 0.04 | 5.32 ± 0.02 | 56.83 ± 0.02 | 89.84 ± 0.05 | 56.83 ± 0.02 | 5.32 ± 0.02 | 5 |
| E3 | NG official split | HGB | 99.40 ± 0.02 | 98.82 ± 0.05 | 99.93 ± 0.07 | 99.79 ± 0.04 | 1.06 ± 0.06 | 99.82 ± 0.02 | 99.08 ± 0.04 | 99.72 ± 0.05 | 0.90 ± 0.04 | 5 |
| E3 | NG official split | RF | 99.40 ± 0.01 | 98.82 ± 0.02 | 99.97 ± 0.00 | 99.74 ± 0.01 | 0.91 ± 0.03 | 99.69 ± 0.02 | 99.17 ± 0.06 | 99.63 ± 0.04 | 0.81 ± 0.06 | 5 |
| E5 | NG official split | rule | 98.58 ± 0.01 | 97.21 ± 0.02 | 98.61 ± 0.01 | 35.89 ± 0.24 | 2.79 ± 0.02 | 100.00 ± 0.00 | 97.21 ± 0.02 | 100.00 ± 0.00 | 2.79 ± 0.02 | 5 |
| E4 | Ext -> NG test | HGB | 96.83 ± 0.40 | 93.70 ± 0.78 | 98.69 ± 0.13 | 44.55 ± 4.19 | 1.60 ± 0.22 | 68.60 ± 5.43 | 95.11 ± 0.90 | 98.61 ± 0.54 | 4.93 ± 0.97 | 5 |
| E4 | NG train -> Ext | HGB | 45.75 ± 1.60 | 39.05 ± 1.09 | 74.23 ± 5.19 | 16.59 ± 0.49 | 2.58 ± 0.11 | 34.36 ± 2.04 | 92.16 ± 0.18 | 30.44 ± 1.41 | 2.24 ± 0.11 | 5 |
| E4 | Ext -> NG test | RF | 96.11 ± 1.46 | 92.29 ± 2.92 | 98.78 ± 0.13 | 49.70 ± 4.07 | 0.64 ± 0.25 | 30.34 ± 12.81 | 93.04 ± 2.71 | 99.43 ± 0.07 | 7.29 ± 3.08 | 5 |
| E4 | NG train -> Ext | RF | 36.34 ± 1.98 | 32.77 ± 1.20 | 77.03 ± 1.00 | 15.73 ± 0.22 | 2.02 ± 0.08 | 25.74 ± 0.64 | 91.82 ± 0.17 | 22.67 ± 1.56 | 1.75 ± 0.15 | 5 |
| E5 | NG -> Ext (rule on Ext) | rule | 67.43 ± 0.02 | 54.54 ± 0.02 | 74.43 ± 0.01 | 11.01 ± 0.02 | 4.88 ± 0.01 | 53.73 ± 0.02 | 90.49 ± 0.02 | 53.73 ± 0.02 | 4.88 ± 0.01 | 5 |


## Recall per Sybil type / scenario

| exp | setting_g | model | rec_DataReplaySybil | rec_DoSDisruptiveSybil | rec_DoSRandomSybil | rec_GridSybil | rec_highway_2 | rec_highway_7 | rec_urban_2 | rec_urban_7 | seeds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | Ext 0709 | HGB | 96.12 ± 0.15 | 98.18 ± 0.09 | 99.79 ± 0.04 | 80.80 ± 0.09 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 5 |
| E1 | Ext 0709 | RF | 96.18 ± 0.11 | 98.46 ± 0.08 | 99.96 ± 0.01 | 79.94 ± 0.14 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 5 |
| E5 | Ext 0709 | rule | 67.38 ± 0.07 | 88.87 ± 0.10 | 88.89 ± 0.11 | 4.55 ± 0.08 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 5 |
| E1 | Ext 1416 | HGB | 95.98 ± 0.39 | 98.70 ± 0.14 | 99.55 ± 0.10 | 79.26 ± 0.45 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 5 |
| E1 | Ext 1416 | RF | 96.43 ± 0.16 | 98.91 ± 0.09 | 99.95 ± 0.01 | 78.80 ± 0.30 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 5 |
| E5 | Ext 1416 | rule | 60.06 ± 0.11 | 79.88 ± 0.10 | 79.81 ± 0.06 | 3.88 ± 0.04 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 5 |
| E2 | Ext 0709 -> 1416 | HGB | 93.59 ± 0.70 | 96.65 ± 0.39 | 99.84 ± 0.02 | 78.48 ± 0.33 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 5 |
| E2 | Ext 0709 -> 1416 | RF | 94.41 ± 0.64 | 97.65 ± 0.32 | 99.93 ± 0.01 | 78.29 ± 0.47 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 5 |
| E5 | Ext 0709 -> 1416 | rule | 60.04 ± 0.07 | 79.84 ± 0.08 | 79.83 ± 0.09 | 3.88 ± 0.04 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 5 |
| E2 | Ext 1416 -> 0709 | HGB | 97.64 ± 0.53 | 99.12 ± 0.28 | 99.86 ± 0.06 | 81.72 ± 1.07 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 5 |
| E2 | Ext 1416 -> 0709 | RF | 97.66 ± 0.34 | 99.10 ± 0.21 | 99.97 ± 0.01 | 80.98 ± 0.79 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 5 |
| E5 | Ext 1416 -> 0709 | rule | 67.40 ± 0.07 | 88.85 ± 0.10 | 88.87 ± 0.11 | 4.55 ± 0.08 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 5 |
| E3 | NG official split | HGB | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 99.32 ± 0.09 | 99.84 ± 0.05 | 99.68 ± 0.04 | 99.71 ± 0.07 | 5 |
| E3 | NG official split | RF | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 98.69 ± 0.12 | 99.85 ± 0.03 | 99.43 ± 0.04 | 99.75 ± 0.05 | 5 |
| E5 | NG official split | rule | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 100.00 ± 0.00 | 100.00 ± 0.00 | 100.00 ± 0.00 | 100.00 ± 0.00 | 5 |
| E4 | Ext -> NG test | HGB | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 97.58 ± 0.21 | 98.75 ± 0.85 | 97.92 ± 0.21 | 99.30 ± 0.62 | 5 |
| E4 | NG train -> Ext | HGB | 47.76 ± 1.05 | 57.21 ± 1.16 | 30.03 ± 4.04 | 2.80 ± 0.61 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 5 |
| E4 | Ext -> NG test | RF | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 98.56 ± 0.19 | 99.83 ± 0.04 | 98.77 ± 0.19 | 99.77 ± 0.06 | 5 |
| E4 | NG train -> Ext | RF | 40.41 ± 2.09 | 48.31 ± 1.92 | 13.18 ± 2.91 | 2.34 ± 0.11 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 5 |
| E5 | NG -> Ext (rule on Ext) | rule | 63.61 ± 0.07 | 84.25 ± 0.08 | 84.26 ± 0.09 | 4.21 ± 0.02 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | nan ± 0.00 | 5 |


## Precision at lower prevalence (from mean FPR/TPR)

| exp | setting_g | model | fpr_at_val_thr1 | tpr_at_val_thr1 | precision@5% | precision@1% | precision@0.1% |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | Ext 0709 | HGB | 0.99 | 83.22 | 81.61 | 46.0 | 7.78 |
| E1 | Ext 0709 | RF | 0.98 | 82.17 | 81.46 | 45.74 | 7.71 |
| E5 | Ext 0709 | rule | 5.32 | 56.83 | 36.01 | 9.75 | 1.06 |
| E1 | Ext 1416 | HGB | 0.94 | 82.61 | 82.23 | 47.04 | 8.09 |
| E1 | Ext 1416 | RF | 0.94 | 82.06 | 82.2 | 46.99 | 8.08 |
| E5 | Ext 1416 | rule | 4.43 | 50.78 | 37.63 | 10.38 | 1.13 |
| E2 | Ext 0709 -> 1416 | HGB | 0.83 | 81.71 | 83.79 | 49.8 | 8.95 |
| E2 | Ext 0709 -> 1416 | RF | 0.81 | 80.2 | 83.84 | 49.89 | 8.98 |
| E5 | Ext 0709 -> 1416 | rule | 4.43 | 50.78 | 37.63 | 10.38 | 1.13 |
| E2 | Ext 1416 -> 0709 | HGB | 1.65 | 86.63 | 73.44 | 34.67 | 5.0 |
| E2 | Ext 1416 -> 0709 | RF | 1.73 | 86.18 | 72.42 | 33.51 | 4.76 |
| E5 | Ext 1416 -> 0709 | rule | 5.32 | 56.83 | 36.01 | 9.75 | 1.06 |
| E3 | NG official split | HGB | 1.06 | 99.82 | 83.18 | 48.7 | 8.6 |
| E3 | NG official split | RF | 0.91 | 99.69 | 85.25 | 52.59 | 9.91 |
| E5 | NG official split | rule | 2.79 | 100.0 | 65.38 | 26.61 | 3.47 |
| E4 | Ext -> NG test | HGB | 1.6 | 68.6 | 69.24 | 30.16 | 4.1 |
| E4 | NG train -> Ext | HGB | 2.58 | 34.36 | 41.18 | 11.84 | 1.31 |
| E4 | Ext -> NG test | RF | 0.64 | 30.34 | 71.37 | 32.36 | 4.53 |
| E4 | NG train -> Ext | RF | 2.02 | 25.74 | 40.09 | 11.38 | 1.26 |
| E5 | NG -> Ext (rule on Ext) | rule | 4.88 | 53.73 | 36.68 | 10.01 | 1.09 |


## E6 ablation

| setting_g | feats | f1 | mcc | auc | tpr_at_1fpr | seeds |
| --- | --- | --- | --- | --- | --- | --- |
| Ext 0709 | only kinematic | 76.97 ± 0.00 | 62.60 ± 0.00 | 84.94 ± 0.00 | 55.44 ± 0.00 | 1 |
| Ext 1416 | only kinematic | 77.98 ± 0.00 | 63.47 ± 0.00 | 85.38 ± 0.00 | 56.71 ± 0.00 | 1 |
| NG official split | only kinematic | 65.75 ± 0.00 | 0.65 ± 0.00 | 51.03 ± 0.00 | 1.91 ± 0.00 | 1 |
| Ext 0709 | all minus kinematic | 93.31 ± 0.00 | 87.86 ± 0.00 | 98.55 ± 0.00 | 78.20 ± 0.00 | 1 |
| Ext 1416 | all minus kinematic | 93.70 ± 0.00 | 88.15 ± 0.00 | 98.67 ± 0.00 | 81.68 ± 0.00 | 1 |
| NG official split | all minus kinematic | 98.93 ± 0.00 | 97.90 ± 0.00 | 99.96 ± 0.00 | 99.34 ± 0.00 | 1 |
| Ext 0709 | only history | 91.38 ± 0.00 | 84.38 ± 0.00 | 95.57 ± 0.00 | 65.63 ± 0.00 | 1 |
| Ext 1416 | only history | 91.42 ± 0.00 | 83.98 ± 0.00 | 95.26 ± 0.00 | 66.07 ± 0.00 | 1 |
| NG official split | only history | 98.58 ± 0.00 | 97.20 ± 0.00 | 99.43 ± 0.00 | 86.77 ± 0.00 | 1 |
| Ext 0709 | all minus history | 82.93 ± 0.00 | 71.95 ± 0.00 | 90.65 ± 0.00 | 67.79 ± 0.00 | 1 |
| Ext 1416 | all minus history | 84.59 ± 0.00 | 73.12 ± 0.00 | 92.23 ± 0.00 | 68.80 ± 0.00 | 1 |
| NG official split | all minus history | 87.23 ± 0.00 | 74.98 ± 0.00 | 95.59 ± 0.00 | 69.39 ± 0.00 | 1 |
| Ext 0709 | only neighbourhood | 73.37 ± 0.00 | 51.27 ± 0.00 | 83.48 ± 0.00 | 34.40 ± 0.00 | 1 |
| Ext 1416 | only neighbourhood | 75.56 ± 0.00 | 52.87 ± 0.00 | 84.87 ± 0.00 | 34.40 ± 0.00 | 1 |
| NG official split | only neighbourhood | 84.42 ± 0.00 | 69.72 ± 0.00 | 94.22 ± 0.00 | 66.96 ± 0.00 | 1 |
| Ext 0709 | all minus neighbourhood | 92.09 ± 0.00 | 85.75 ± 0.00 | 95.84 ± 0.00 | 73.65 ± 0.00 | 1 |
| Ext 1416 | all minus neighbourhood | 91.76 ± 0.00 | 84.81 ± 0.00 | 95.33 ± 0.00 | 74.71 ± 0.00 | 1 |
| NG official split | all minus neighbourhood | 98.54 ± 0.00 | 97.12 ± 0.00 | 99.40 ± 0.00 | 85.61 ± 0.00 | 1 |
| Ext 0709 | new_pseudo + neighbourhood | 85.08 ± 0.00 | 72.95 ± 0.00 | 93.64 ± 0.00 | 45.79 ± 0.00 | 1 |
| Ext 1416 | new_pseudo + neighbourhood | 85.38 ± 0.00 | 72.35 ± 0.00 | 93.47 ± 0.00 | 47.45 ± 0.00 | 1 |
| NG official split | new_pseudo + neighbourhood | 99.26 ± 0.00 | 98.55 ± 0.00 | 99.90 ± 0.00 | 99.58 ± 0.00 | 1 |


## E7 shortcut fixes

| setting | feats | f1 | mcc | auc | tpr_at_1fpr | rec_GridSybil | seeds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NG train -> Ext | all | 45.75 ± 1.60 | 39.05 ± 1.09 | 74.23 ± 5.19 | 16.59 ± 0.49 | 2.80 ± 0.61 | 5 |
| Ext -> NG test | all | 96.83 ± 0.40 | 93.70 ± 0.78 | 98.69 ± 0.13 | 44.55 ± 4.19 | nan ± 0.00 | 5 |
| in-domain Ext 0709 -> 1416 | all | 93.61 ± 0.09 | 88.33 ± 0.11 | 98.59 ± 0.01 | 83.54 ± 0.13 | 78.48 ± 0.33 | 5 |
| in-domain NG official | all | 99.40 ± 0.02 | 98.82 ± 0.05 | 99.93 ± 0.07 | 99.79 ± 0.04 | nan ± 0.00 | 5 |
| NG train -> Ext | drop_age | 46.48 ± 1.49 | 39.55 ± 0.96 | 74.63 ± 5.06 | 16.64 ± 0.37 | 2.55 ± 0.19 | 5 |
| Ext -> NG test | drop_age | 96.95 ± 0.47 | 93.96 ± 0.93 | 98.73 ± 0.13 | 45.82 ± 3.83 | nan ± 0.00 | 5 |
| in-domain Ext 0709 -> 1416 | drop_age | 93.52 ± 0.08 | 88.18 ± 0.10 | 98.48 ± 0.01 | 83.42 ± 0.13 | 78.38 ± 0.31 | 5 |
| in-domain NG official | drop_age | 99.35 ± 0.14 | 98.72 ± 0.28 | 99.83 ± 0.28 | 99.61 ± 0.42 | nan ± 0.00 | 5 |
| NG train -> Ext | drop_history | 25.72 ± 2.23 | 9.37 ± 1.19 | 57.03 ± 0.70 | 2.52 ± 0.10 | 7.07 ± 0.69 | 5 |
| Ext -> NG test | drop_history | 44.78 ± 4.29 | 15.36 ± 1.07 | 63.59 ± 0.82 | 1.09 ± 0.12 | nan ± 0.00 | 5 |
| in-domain Ext 0709 -> 1416 | drop_history | 83.75 ± 0.08 | 72.32 ± 0.16 | 91.29 ± 0.06 | 68.34 ± 0.39 | 80.72 ± 0.33 | 5 |
| in-domain NG official | drop_history | 87.17 ± 0.05 | 75.08 ± 0.30 | 95.51 ± 0.04 | 69.05 ± 0.45 | nan ± 0.00 | 5 |
| NG train -> Ext | mask25 | 59.60 ± 1.95 | 49.83 ± 1.58 | 67.36 ± 3.49 | 22.63 ± 1.45 | 2.40 ± 0.06 | 5 |
| Ext -> NG test | mask25 | 83.47 ± 2.10 | 69.79 ± 3.07 | 93.36 ± 1.30 | 7.65 ± 4.71 | nan ± 0.00 | 5 |
| in-domain Ext 0709 -> 1416 | mask25 | 91.88 ± 0.07 | 84.72 ± 0.08 | 98.14 ± 0.02 | 78.11 ± 0.18 | 85.10 ± 0.46 | 5 |
| in-domain NG official | mask25 | 99.17 ± 0.04 | 98.37 ± 0.07 | 99.91 ± 0.01 | 99.22 ± 0.11 | nan ± 0.00 | 5 |
| NG train -> Ext | mask50 | 59.97 ± 0.73 | 50.06 ± 0.64 | 69.18 ± 4.71 | 23.53 ± 1.46 | 2.45 ± 0.11 | 5 |
| Ext -> NG test | mask50 | 80.29 ± 1.96 | 60.76 ± 3.37 | 85.27 ± 0.98 | 1.58 ± 1.77 | nan ± 0.00 | 5 |
| in-domain Ext 0709 -> 1416 | mask50 | 89.82 ± 0.05 | 80.24 ± 0.06 | 97.37 ± 0.03 | 76.79 ± 0.11 | 92.26 ± 0.43 | 5 |
| in-domain NG official | mask50 | 99.14 ± 0.03 | 98.31 ± 0.05 | 99.90 ± 0.02 | 99.09 ± 0.09 | nan ± 0.00 | 5 |
| mixed -> Ext 1416 | mixed | 93.48 ± 0.06 | 88.15 ± 0.08 | 98.55 ± 0.02 | 82.78 ± 0.15 | 77.67 ± 0.24 | 5 |
| mixed -> NG test | mixed | 98.46 ± 1.30 | 96.96 ± 2.56 | 98.33 ± 2.43 | 61.07 ± 52.79 | nan ± 0.00 | 5 |


## E8 leave-one-type-out, per held-out type

| held_out | model | feats | f1 | mcc | tpr_at_1fpr | seeds |
| --- | --- | --- | --- | --- | --- | --- |
| GridSybil | HGB | seen | 86.84 ± 0.05 | 70.46 ± 0.56 | 71.95 ± 0.30 | 5 |
| GridSybil | RF | seen | 86.57 ± 0.02 | 69.98 ± 0.45 | 68.62 ± 0.30 | 5 |
| GridSybil | HGB | unseen | 8.64 ± 1.73 | 7.06 ± 1.72 | 3.33 ± 0.77 | 5 |
| GridSybil | RF | unseen | 16.77 ± 1.82 | 14.05 ± 1.33 | 2.96 ± 0.35 | 5 |
| GridSybil | HGB | unseen+NG | 6.88 ± 0.41 | 6.22 ± 0.14 | 2.85 ± 0.07 | 5 |
| GridSybil | RF | unseen+NG | 7.04 ± 0.94 | 6.78 ± 0.64 | 2.62 ± 0.10 | 5 |
| GridSybil | rule | is_new_pseudo | 7.88 ± 0.04 | -0.72 ± 0.11 | 0.93 ± 0.01 | 5 |
| DataReplaySybil | HGB | seen | 94.44 ± 0.19 | 92.07 ± 0.25 | 84.72 ± 0.30 | 5 |
| DataReplaySybil | RF | seen | 94.58 ± 0.11 | 92.24 ± 0.15 | 84.13 ± 0.33 | 5 |
| DataReplaySybil | HGB | unseen | 75.91 ± 1.41 | 69.99 ± 1.33 | 50.71 ± 1.11 | 5 |
| DataReplaySybil | RF | unseen | 72.87 ± 0.52 | 66.85 ± 0.53 | 48.30 ± 0.42 | 5 |
| DataReplaySybil | HGB | unseen+NG | 74.91 ± 1.52 | 69.09 ± 1.42 | 48.61 ± 1.16 | 5 |
| DataReplaySybil | RF | unseen+NG | 70.30 ± 0.63 | 64.61 ± 0.54 | 46.55 ± 0.23 | 5 |
| DataReplaySybil | rule | is_new_pseudo | 72.85 ± 0.05 | 64.76 ± 0.06 | 13.47 ± 0.03 | 5 |
| DoSRandomSybil | HGB | seen | 97.93 ± 0.08 | 96.16 ± 0.14 | 97.96 ± 0.11 | 5 |
| DoSRandomSybil | RF | seen | 97.95 ± 0.07 | 96.20 ± 0.12 | 97.97 ± 0.18 | 5 |
| DoSRandomSybil | HGB | unseen | 96.89 ± 0.25 | 94.22 ± 0.45 | 80.31 ± 2.15 | 5 |
| DoSRandomSybil | RF | unseen | 97.62 ± 0.03 | 95.57 ± 0.06 | 79.40 ± 2.14 | 5 |
| DoSRandomSybil | HGB | unseen+NG | 96.68 ± 0.52 | 93.82 ± 0.93 | 77.97 ± 2.09 | 5 |
| DoSRandomSybil | RF | unseen+NG | 97.32 ± 0.06 | 95.02 ± 0.12 | 65.24 ± 4.18 | 5 |
| DoSRandomSybil | rule | is_new_pseudo | 88.58 ± 0.05 | 80.15 ± 0.10 | 16.62 ± 0.11 | 5 |
| DoSDisruptiveSybil | HGB | seen | 96.92 ± 0.09 | 94.27 ± 0.16 | 81.07 ± 0.27 | 5 |
| DoSDisruptiveSybil | RF | seen | 97.12 ± 0.05 | 94.64 ± 0.09 | 80.46 ± 0.38 | 5 |
| DoSDisruptiveSybil | HGB | unseen | 91.93 ± 0.59 | 86.06 ± 0.89 | 72.63 ± 0.63 | 5 |
| DoSDisruptiveSybil | RF | unseen | 93.79 ± 0.53 | 88.94 ± 0.85 | 73.11 ± 0.27 | 5 |
| DoSDisruptiveSybil | HGB | unseen+NG | 95.13 ± 0.40 | 91.14 ± 0.68 | 75.53 ± 0.65 | 5 |
| DoSDisruptiveSybil | RF | unseen+NG | 94.88 ± 0.33 | 90.72 ± 0.54 | 71.39 ± 0.51 | 5 |
| DoSDisruptiveSybil | rule | is_new_pseudo | 88.60 ± 0.05 | 80.19 ± 0.08 | 16.73 ± 0.04 | 5 |


## E8 mean over types

| model | feats | f1 | mcc | tpr_at_1fpr | seeds |
| --- | --- | --- | --- | --- | --- |
| HGB | seen | 94.03 ± 0.08 | 88.24 ± 0.22 | 83.93 ± 0.18 | 5 |
| RF | seen | 94.05 ± 0.05 | 88.27 ± 0.16 | 82.79 ± 0.19 | 5 |
| HGB | unseen | 68.34 ± 0.59 | 64.33 ± 0.58 | 51.75 ± 0.60 | 5 |
| RF | unseen | 70.26 ± 0.55 | 66.35 ± 0.51 | 50.94 ± 0.45 | 5 |
| HGB | unseen+NG | 68.40 ± 0.35 | 65.07 ± 0.34 | 51.24 ± 0.72 | 5 |
| RF | unseen+NG | 67.39 ± 0.32 | 64.28 ± 0.27 | 46.45 ± 1.07 | 5 |
| rule | is_new_pseudo | 64.48 ± 0.02 | 56.09 ± 0.04 | 11.94 ± 0.03 | 5 |


Seen − unseen F1 gap (HGB) per seed: 25.6, 25.2, 25.5, 26.6, 25.6 points; unseen lower in 5 of 5 seeds.

## importance_groups.csv (seed 0)

| model | data | base_auc | group | auc_drop | sd | seed |
| --- | --- | --- | --- | --- | --- | --- |
| Extension-trained | Extension test | 0.9865 | kinematic | 0.0277 | 0.0005 | 0 |
| Extension-trained | Extension test | 0.9865 | history | 0.3374 | 0.0021 | 0 |
| Extension-trained | Extension test | 0.9865 | neighbourhood | 0.0809 | 0.0009 | 0 |
| Extension-trained | Extension test | 0.9865 | is_new_pseudo | 0.0 | 0.0 | 0 |
| Extension-trained | Extension test | 0.9865 | history except is_new_pseudo | 0.3407 | 0.0005 | 0 |
| NextGen-trained | NextGen test | 0.9997 | kinematic | 0.0002 | 0.0 | 0 |
| NextGen-trained | NextGen test | 0.9997 | history | 0.4017 | 0.0014 | 0 |
| NextGen-trained | NextGen test | 0.9997 | neighbourhood | 0.0122 | 0.0002 | 0 |
| NextGen-trained | NextGen test | 0.9997 | is_new_pseudo | 0.0 | 0.0 | 0 |
| NextGen-trained | NextGen test | 0.9997 | history except is_new_pseudo | 0.2759 | 0.0009 | 0 |
| NextGen-trained | Extension test | 0.7773 | kinematic | 0.0008 | 0.0004 | 0 |
| NextGen-trained | Extension test | 0.7773 | history | 0.2735 | 0.0014 | 0 |
| NextGen-trained | Extension test | 0.7773 | neighbourhood | 0.0046 | 0.0006 | 0 |
| NextGen-trained | Extension test | 0.7773 | is_new_pseudo | 0.0243 | 0.0006 | 0 |
| NextGen-trained | Extension test | 0.7773 | history except is_new_pseudo | 0.1642 | 0.0019 | 0 |
| Extension-trained | NextGen test | 0.9857 | kinematic | 0.0005 | 0.0004 | 0 |
| Extension-trained | NextGen test | 0.9857 | history | 0.5054 | 0.0017 | 0 |
| Extension-trained | NextGen test | 0.9857 | neighbourhood | 0.0209 | 0.0002 | 0 |
| Extension-trained | NextGen test | 0.9857 | is_new_pseudo | -0.0 | 0.0 | 0 |
| Extension-trained | NextGen test | 0.9857 | history except is_new_pseudo | 0.5071 | 0.003 | 0 |


## first_message_false_alarms.csv (seed 0)

| model | data | genuine_first_share | fpr_genuine_first | fpr_genuine_with_history | fpr_all | tpr | seed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Extension-trained | Extension test | 0.0485 | 0.1892 | 0.0031 | 0.0121 | 0.8524 | 0 |
| Extension-trained | NextGen test | 0.0279 | 0.5208 | 0.01 | 0.0243 | 0.835 | 0 |
| NextGen-trained | Extension test | 0.0485 | 0.5023 | 0.0005 | 0.0248 | 0.3505 | 0 |
| NextGen-trained | NextGen test | 0.0279 | 0.3529 | 0.0001 | 0.0099 | 0.9982 | 0 |
| Rule | Extension test | 0.0485 | 1.0 | 0.0 | 0.0485 | 0.5423 | 0 |
| Rule | NextGen test | 0.0279 | 1.0 | 0.0 | 0.0279 | 1.0 | 0 |

