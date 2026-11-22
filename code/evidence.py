"""
Evidence for the shortcut claim + extra analyses for the manuscript.

1. Group and feature permutation importance (drop in ROC-AUC) of an Extension-trained and a NextGen-trained HGB,
   each on its own held-out test set, and of the NextGen model on Extension.
2. False alarms on GENUINE messages that are the first heard from their pseudonym vs genuine messages with history.
3. ROC curves (downsampled) for in-domain and cross-dataset settings.
Extension is split 3-ways by true sender (train / validation / test); NextGen uses its official splits.
Usage: python evidence.py --feat-dir ../features --out results_q1
"""
import argparse, json, os, sys
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score, roc_curve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import experiments as E


def group_importance(m, D, cols_all, groups, rng, n=40000, reps=3):
    S = D.iloc[rng.choice(len(D), min(n, len(D)), replace=False)].reset_index(drop=True)
    X = S[cols_all].values.copy(); y = S.label.values
    base = roc_auc_score(y, m.predict_proba(X)[:, 1]); out = {}
    for name, cols in groups.items():
        idx = [cols_all.index(c) for c in cols]; drops = []
        for _ in range(reps):
            Xp = X.copy(); perm = rng.permutation(len(Xp)); Xp[:, idx] = X[perm][:, idx]
            drops.append(base - roc_auc_score(y, m.predict_proba(Xp)[:, 1]))
        out[name] = (float(np.mean(drops)), float(np.std(drops)))
    return base, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--feat-dir', default='../features'); ap.add_argument('--out', default='results_q1')
    ap.add_argument('--ext-n', type=int, default=120000); ap.add_argument('--ng-train-n', type=int, default=150000)
    ap.add_argument('--ng-val-n', type=int, default=50000); ap.add_argument('--ng-test-n', type=int, default=200000)
    ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); E.SEED = a.seed; rng = np.random.default_rng(a.seed)
    ext, ng = E.load_all(a)
    rest, te = E.inner_val(ext, 1); Rest = ext.iloc[rest].reset_index(drop=True); ExtTe = ext.iloc[te].reset_index(drop=True)
    tr, va = E.inner_val(Rest, 2); ExtTr, ExtVa = Rest.iloc[tr], Rest.iloc[va]
    print(f'Extension split: train {len(ExtTr)}, val {len(ExtVa)}, test {len(ExtTe)} (sender-disjoint)', flush=True)
    F = E.ALL
    mx = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, random_state=a.seed).fit(ExtTr[F].values, ExtTr.label.values)
    mn = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, random_state=a.seed).fit(ng['Train'][F].values, ng['Train'].label.values)
    thr = {'ext': E.thr_at_fpr(ExtVa.label.values, mx.predict_proba(ExtVa[F].values)[:, 1]),
           'ng': E.thr_at_fpr(ng['Validation'].label.values, mn.predict_proba(ng['Validation'][F].values)[:, 1])}

    # 1. importance
    groups = {'kinematic': E.KIN, 'history': E.HIST, 'neighbourhood': E.NEIGH, 'is_new_pseudo': ['is_new_pseudo'],
              'history except is_new_pseudo': [c for c in E.HIST if c != 'is_new_pseudo']}
    imp_rows = []
    for mname, m, Dname, D in [('Extension-trained', mx, 'Extension test', ExtTe), ('NextGen-trained', mn, 'NextGen test', ng['Test']),
                               ('NextGen-trained', mn, 'Extension test', ExtTe), ('Extension-trained', mx, 'NextGen test', ng['Test'])]:
        base, out = group_importance(m, D, F, groups, rng)
        for g, (mu, sd) in out.items():
            imp_rows.append(dict(model=mname, data=Dname, base_auc=base, group=g, auc_drop=mu, sd=sd))
        print(f'\n{mname} on {Dname}: AUC {base:.4f}; ' + ', '.join(f'{g} {mu:.4f}' for g, (mu, sd) in out.items()), flush=True)
    feat_rows = []
    for mname, m, D in [('Extension-trained', mx, ExtTe), ('NextGen-trained', mn, ng['Test'])]:
        base, out = group_importance(m, D, F, {f: [f] for f in F}, rng, n=30000, reps=2)
        for f, (mu, sd) in out.items():
            feat_rows.append(dict(model=mname, feature=f, auc_drop=mu))
    pd.DataFrame(imp_rows).to_csv(os.path.join(a.out, 'importance_groups.csv'), index=False)
    FR = pd.DataFrame(feat_rows).pivot(index='feature', columns='model', values='auc_drop').sort_values('NextGen-trained', ascending=False)
    FR.to_csv(os.path.join(a.out, 'importance_features.csv')); print('\nPer-feature AUC drop:\n' + FR.round(4).to_string(), flush=True)

    # 2. false alarms on genuine first messages (at the validation-chosen 1%-FPR threshold of each model)
    fa = []
    for mname, m, key in [('Extension-trained', mx, 'ext'), ('NextGen-trained', mn, 'ng'), ('Rule', None, None)]:
        for Dname, D in [('Extension test', ExtTe), ('NextGen test', ng['Test'])]:
            g = D[D.label == 0]; first = g.is_new_pseudo.values > 0.5
            flag = (g.is_new_pseudo.values > 0.5) if m is None else (m.predict_proba(g[F].values)[:, 1] >= thr[key])
            s = D[D.label == 1]
            det = (s.is_new_pseudo.values > 0.5) if m is None else (m.predict_proba(s[F].values)[:, 1] >= thr[key])
            fa.append(dict(model=mname, data=Dname, genuine_first_share=first.mean(), fpr_genuine_first=flag[first].mean(),
                           fpr_genuine_with_history=flag[~first].mean(), fpr_all=flag.mean(), tpr=det.mean()))
    FA = pd.DataFrame(fa); FA.to_csv(os.path.join(a.out, 'first_message_false_alarms.csv'), index=False)
    print('\nFalse alarms on genuine messages (val-chosen 1%-FPR threshold):\n' + (FA.set_index(['model', 'data']) * 100).round(2).to_string(), flush=True)

    # 3. ROC curves, downsampled on a log-spaced FPR grid
    grid = np.unique(np.r_[0, np.logspace(-4, 0, 60)]); roc = []
    for mname, m, Dname, D in [('Extension-trained', mx, 'Extension test', ExtTe), ('Extension-trained', mx, 'NextGen test', ng['Test']),
                               ('NextGen-trained', mn, 'NextGen test', ng['Test']), ('NextGen-trained', mn, 'Extension test', ExtTe)]:
        p = m.predict_proba(D[F].values)[:, 1]; f, t, _ = roc_curve(D.label.values, p)
        auc = roc_auc_score(D.label.values, p)
        for gx in grid:
            roc.append(dict(setting=f'{mname} → {Dname}', fpr=float(gx), tpr=float(np.interp(gx, f, t)), auc=auc))
    pd.DataFrame(roc).to_csv(os.path.join(a.out, 'roc_curves.csv'), index=False)
    print('\nROC AUCs: ' + str(pd.DataFrame(roc).groupby('setting').auc.first().round(4).to_dict()))


if __name__ == '__main__':
    main()
