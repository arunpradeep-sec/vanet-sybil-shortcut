"""
Combine multi-seed results into mean ± std tables for the manuscript.
Expects results_final/seed<k>/{all_results.csv, shortcut_results.csv, loto_results.csv} (k = 0..4)
and optionally results_final/seed0/{importance_*.csv, first_message_false_alarms.csv} from evidence.py.
Within-dataset folds are averaged first, so std is across seeds.
Usage: python aggregate.py --root results_final
Writes: results_final/final_tables.md and final_*.csv
"""
import argparse, glob, os, re
import numpy as np, pandas as pd

M = ['f1', 'mcc', 'auc', 'tpr_at_1fpr', 'fpr_at_val_thr1', 'tpr_at_val_thr1', 'prec', 'rec', 'fpr']


def md_table(df, index=True):
    """Markdown table without the optional 'tabulate' package."""
    d = df.reset_index() if index else df.copy()
    cols = [str(c) for c in d.columns]
    lines = ['| ' + ' | '.join(cols) + ' |', '| ' + ' | '.join('---' for _ in cols) + ' |']
    for row in d.itertuples(index=False):
        lines.append('| ' + ' | '.join(str(v) for v in row) + ' |')
    return '\n'.join(lines)


def collect(root, name):
    out = []
    for d in sorted(glob.glob(os.path.join(root, 'seed*'))):
        f = os.path.join(d, name)
        if os.path.exists(f):
            x = pd.read_csv(f); x['seed'] = int(re.findall(r'\d+', os.path.basename(d))[0]); out.append(x)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def ms(df, keys, cols):
    """mean over folds within seed, then mean ± std over seeds (in %)."""
    per_seed = df.groupby(keys + ['seed'], sort=False)[cols].mean()
    g = per_seed.groupby(level=list(range(len(keys))), sort=False)
    mean, std, n = g.mean() * 100, g.std().fillna(0) * 100, g.size()
    txt = mean.round(2).map('{:.2f}'.format) + ' ± ' + std.round(2).map('{:.2f}'.format)
    txt['seeds'] = n
    return txt, mean, std


def prec_at(t, f, pi):
    d = t * pi + f * (1 - pi)
    return np.where(d > 0, t * pi / d, np.nan)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--root', default='results_final'); a = ap.parse_args()
    md = ['# Final results (mean ± std over seeds, %)\n']

    A = collect(a.root, 'all_results.csv')
    if len(A):
        A['setting_g'] = A.setting.str.replace(r' fold\d', '', regex=True)
        cols = [c for c in M if c in A]
        T, mean, _ = ms(A[A.exp.isin(['E1', 'E2', 'E3', 'E4', 'E5'])], ['exp', 'setting_g', 'model'], cols)
        T.to_csv(os.path.join(a.root, 'final_main.csv')); md += ['## E1–E5 main results\n', md_table(T), '\n']
        rc = [c for c in A.columns if c.startswith('rec_')]
        R, _, _ = ms(A[A.exp.isin(['E1', 'E2', 'E3', 'E4', 'E5'])], ['exp', 'setting_g', 'model'], rc)
        R = R.loc[:, (R != 'nan ± 0.00').any()]
        R.to_csv(os.path.join(a.root, 'final_per_type_recall.csv')); md += ['## Recall per Sybil type / scenario\n', md_table(R), '\n']
        P = mean[['fpr_at_val_thr1', 'tpr_at_val_thr1']].copy() / 100
        for pi in [0.05, 0.01, 0.001]:
            P[f'precision@{pi*100:g}%'] = prec_at(P.tpr_at_val_thr1.values, P.fpr_at_val_thr1.values, pi) * 100
        P[['fpr_at_val_thr1', 'tpr_at_val_thr1']] *= 100
        P.round(2).to_csv(os.path.join(a.root, 'final_prevalence.csv')); md += ['## Precision at lower prevalence (from mean FPR/TPR)\n', md_table(P.round(2)), '\n']
        if (A.exp == 'E6').any():
            T6, _, _ = ms(A[A.exp == 'E6'], ['setting_g', 'feats'], ['f1', 'mcc', 'auc', 'tpr_at_1fpr'])
            T6.to_csv(os.path.join(a.root, 'final_ablation.csv')); md += ['## E6 ablation\n', md_table(T6), '\n']

    S = collect(a.root, 'shortcut_results.csv')
    if len(S):
        cols = ['f1', 'mcc', 'auc', 'tpr_at_1fpr'] + (['rec_GridSybil'] if 'rec_GridSybil' in S else [])
        T7, _, _ = ms(S, ['setting', 'feats'], cols)
        T7.to_csv(os.path.join(a.root, 'final_shortcut.csv')); md += ['## E7 shortcut fixes\n', md_table(T7), '\n']

    L = collect(a.root, 'loto_results.csv')
    if len(L):
        L['held_out'] = L.setting.str.split(' ').str[0]
        T8, _, _ = ms(L, ['held_out', 'model', 'feats'], ['f1', 'mcc', 'tpr_at_1fpr'])
        T8a, _, _ = ms(L, ['model', 'feats'], ['f1', 'mcc', 'tpr_at_1fpr'])
        T8.to_csv(os.path.join(a.root, 'final_loto.csv')); T8a.to_csv(os.path.join(a.root, 'final_loto_mean.csv'))
        md += ['## E8 leave-one-type-out, per held-out type\n', md_table(T8), '\n', '## E8 mean over types\n', md_table(T8a), '\n']
        ps = L[L.model == 'HGB'].groupby(['seed', 'feats']).f1.mean().unstack()
        if {'seen', 'unseen'} <= set(ps.columns):
            d = (ps['unseen'] - ps['seen']) * 100
            md += [f'Seen − unseen F1 gap (HGB) per seed: {", ".join(f"{-v:.1f}" for v in d)} points; '
                   f'unseen lower in {(d < 0).sum()} of {len(d)} seeds.\n']

    for f in ['importance_groups.csv', 'first_message_false_alarms.csv']:
        X = collect(a.root, f)
        if len(X):
            md += [f'## {f} (seed 0)\n', md_table(X[X.seed == X.seed.min()].round(4), index=False), '\n']

    open(os.path.join(a.root, 'final_tables.md'), 'w').write('\n'.join(md))
    print('\n'.join(md)); print(f'\nWritten to {os.path.abspath(a.root)}/final_tables.md')


if __name__ == '__main__':
    main()
