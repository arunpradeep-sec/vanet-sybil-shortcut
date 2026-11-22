"""
Q1 experiment suite on harmonised VeReMi Extension + NextGen features (output of convert_veremi.py).

E1  within-Extension, per density: 5-fold StratifiedGroupKFold by true sender
E2  cross-density (Extension): train 0709 -> test 1416, and 1416 -> 0709
E3  NextGen official split: train Train, threshold on Validation, test on Test (separate geographic area)
E4  cross-dataset: Extension -> NextGen Test, NextGen Train -> Extension
E5  rule baseline in every setting: "first message ever heard from this pseudonym = Sybil"
E6  feature-group ablation (group alone / all minus group), HGB, on E1 (3 folds, both densities) and E3

Thresholds always come from validation data of the TRAINING side (never from the test set).
Usage: python experiments.py --feat-dir ../features [--ext-n 120000 --ng-train-n 150000 ...] [--only E1,E3]
"""
import argparse, glob, os, time
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (precision_score, recall_score, f1_score, roc_auc_score, matthews_corrcoef,
                             confusion_matrix, roc_curve, precision_recall_curve)

KIN = ['spd', 'acc', 'pos_noise', 'spd_noise', 'dist_rcv']
HIST = ['beacon_dt', 'pos_jump', 'pos_pred_err', 'spd_change_rate', 'hed_motion_err', 'msg_idx', 'pseudo_age',
        'is_new_pseudo', 'first_seen_dist']
NEIGH = ['n_pseudo_1s', 'n_near5', 'n_near20', 'min_dist_other', 'new_pseudo_5s', 'new_pseudo_frac_5s', 'n_similar_spd_near']
ALL = KIN + HIST + NEIGH
GROUPS = {'kinematic': KIN, 'history': HIST, 'neighbourhood': NEIGH}
ROWS = []
SEED = 0  # set with --seed; shifts every random choice (sampling, splits, models)


# ------------------------------------------------------------------------------ data
def load(path, n, rng):
    d = pd.read_pickle(path)
    if n and len(d) > n:
        d = d.iloc[np.sort(rng.choice(len(d), n, replace=False))]
    d = d[['sender', 'label', 'attack'] + ALL].copy()
    d['subset'] = os.path.basename(path).replace('.pkl.gz', '')
    return d.reset_index(drop=True)


def load_all(a):
    rng = np.random.default_rng(SEED)
    ext = pd.concat([load(p, a.ext_n, rng) for p in sorted(glob.glob(os.path.join(a.feat_dir, 'ext_*.pkl.gz')))], ignore_index=True)
    ext['density'] = ext.subset.str[-4:]
    ng = {}
    for split, n in [('Train', a.ng_train_n), ('Validation', a.ng_val_n), ('Test', a.ng_test_n)]:
        ng[split] = pd.concat([load(p, n, rng) for p in sorted(glob.glob(os.path.join(a.feat_dir, f'ng_*_{split}.pkl.gz')))], ignore_index=True)
        ng[split]['scenario'] = ng[split].subset.str.replace('ng_InTAS_', '').str.replace(f'_{split}', '')
    for d in [ext] + list(ng.values()):
        d['sender'] = d.sender.astype('category').cat.codes
    print(f"Extension {len(ext)} msgs ({ext.label.mean()*100:.1f}% Sybil); NextGen train {len(ng['Train'])}, "
          f"val {len(ng['Validation'])}, test {len(ng['Test'])}", flush=True)
    return ext, ng


# ------------------------------------------------------------------------------ models / metrics
def make(name, seed):
    if name == 'HGB':
        return HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, random_state=seed + 1000 * SEED)
    return RandomForestClassifier(100, min_samples_leaf=2, max_samples=0.3, n_jobs=-1, random_state=seed + 1000 * SEED)


def f1_thr(y, p):
    pr, rc, th = precision_recall_curve(y, p); f1 = 2 * pr * rc / np.maximum(pr + rc, 1e-12)
    return float(th[int(np.argmax(f1[:-1]))])


def thr_at_fpr(y, p, fpr=0.01):
    return float(np.quantile(p[y == 0], 1 - fpr))


def score(exp, setting, model, feats, y, p, thr, thr1, by=None, seconds=0.0):
    yh = (p >= thr).astype(int); tn, fp, fn, tp = confusion_matrix(y, yh, labels=[0, 1]).ravel()
    fpr_c, tpr_c, _ = roc_curve(y, p) if len(set(y)) > 1 else ([0, 1], [0, 1], None)
    r = dict(exp=exp, setting=setting, model=model, feats=feats, n=len(y), sybil_share=y.mean(),
             prec=precision_score(y, yh, zero_division=0), rec=recall_score(y, yh, zero_division=0),
             f1=f1_score(y, yh, zero_division=0), fpr=fp / max(fp + tn, 1), mcc=matthews_corrcoef(y, yh),
             auc=roc_auc_score(y, p) if len(set(y)) > 1 else np.nan,
             tpr_at_1fpr=float(np.interp(0.01, fpr_c, tpr_c)),
             fpr_at_val_thr1=float(((p >= thr1) & (y == 0)).sum() / max((y == 0).sum(), 1)),
             tpr_at_val_thr1=float(((p >= thr1) & (y == 1)).sum() / max((y == 1).sum(), 1)), seconds=seconds)
    if by is not None:  # recall per attack type / scenario at the F1 threshold
        for k in sorted(set(by[y == 1])):
            s = (by == k) & (y == 1); r[f'rec_{k}'] = yh[s].mean()
    ROWS.append(r)
    print(f"  {exp:3s} {setting:28s} {model:5s} {feats:22s} F1={r['f1']*100:6.2f} P={r['prec']*100:6.2f} R={r['rec']*100:6.2f} "
          f"FPR={r['fpr']*100:5.2f} AUC={r['auc']*100:6.2f} TPR@1%={r['tpr_at_1fpr']*100:6.2f} "
          f"(val-thr: FPR={r['fpr_at_val_thr1']*100:5.2f} TPR={r['tpr_at_val_thr1']*100:6.2f}) {seconds:.0f}s", flush=True)
    return r


def fit_eval(exp, setting, model, feats, Xtr, ytr, Xva, yva, Xte, yte, by=None, seed=0):
    t0 = time.time(); m = make(model, seed).fit(Xtr, ytr)
    pv, pt = m.predict_proba(Xva)[:, 1], m.predict_proba(Xte)[:, 1]
    return score(exp, setting, model, feats, yte, pt, f1_thr(yva, pv), thr_at_fpr(yva, pv), by, time.time() - t0), m


def rule_eval(exp, setting, D, by=None):
    p = (D.is_new_pseudo.values > 0.5).astype(float)
    return score(exp, setting, 'rule', 'is_new_pseudo', D.label.values, p, 0.5, 0.5, by)


def inner_val(D, seed):
    cv = StratifiedGroupKFold(6, shuffle=True, random_state=seed + 1000 * SEED)
    tr, va = min(cv.split(D, D.label, D.sender), key=lambda s: abs(D.label.values[s[1]].mean() - D.label.mean()))
    return tr, va


# ------------------------------------------------------------------------------ experiments
def e1(ext, models, folds=5, feats=ALL, fname='all', exp='E1'):
    for dens in ['0709', '1416']:
        D = ext[ext.density == dens].reset_index(drop=True)
        cv = StratifiedGroupKFold(5, shuffle=True, random_state=42 + SEED)
        for k, (tr, te) in enumerate(cv.split(D, D.label, D.sender)):
            if k >= folds:
                break
            Dtr = D.iloc[tr].reset_index(drop=True); itr, iva = inner_val(Dtr, k)
            for m in models:
                fit_eval(exp, f'Ext {dens} fold{k}', m, fname, Dtr.iloc[itr][feats].values, Dtr.label.values[itr],
                         Dtr.iloc[iva][feats].values, Dtr.label.values[iva], D.iloc[te][feats].values, D.label.values[te],
                         D.attack.values[te], seed=k)
            if exp == 'E1':
                rule_eval('E5', f'Ext {dens} fold{k}', D.iloc[te], D.attack.values[te])


def e2(ext, models):
    for src, dst in [('0709', '1416'), ('1416', '0709')]:
        S = ext[ext.density == src].reset_index(drop=True); T = ext[ext.density == dst].reset_index(drop=True)
        itr, iva = inner_val(S, 0)
        for m in models:
            fit_eval('E2', f'Ext {src} -> {dst}', m, 'all', S.iloc[itr][ALL].values, S.label.values[itr],
                     S.iloc[iva][ALL].values, S.label.values[iva], T[ALL].values, T.label.values, T.attack.values)
        rule_eval('E5', f'Ext {src} -> {dst}', T, T.attack.values)


def e3(ng, models, feats=ALL, fname='all', exp='E3'):
    tr, va, te = ng['Train'], ng['Validation'], ng['Test']
    for m in models:
        _, model = fit_eval(exp, 'NG official split', m, fname, tr[feats].values, tr.label.values, va[feats].values,
                            va.label.values, te[feats].values, te.label.values, te.scenario.values)
    if exp == 'E3':
        rule_eval('E5', 'NG official split', te, te.scenario.values)


def e4(ext, ng, models):
    itr, iva = inner_val(ext, 0); te = ng['Test']
    for m in models:
        fit_eval('E4', 'Ext -> NG test', m, 'all', ext.iloc[itr][ALL].values, ext.label.values[itr],
                 ext.iloc[iva][ALL].values, ext.label.values[iva], te[ALL].values, te.label.values, te.scenario.values)
        fit_eval('E4', 'NG train -> Ext', m, 'all', ng['Train'][ALL].values, ng['Train'].label.values,
                 ng['Validation'][ALL].values, ng['Validation'].label.values, ext[ALL].values, ext.label.values, ext.attack.values)
    rule_eval('E5', 'NG -> Ext (rule on Ext)', ext, ext.attack.values)


def e6(ext, ng):
    for g, cols in GROUPS.items():
        for fname, feats in [(f'only {g}', cols), (f'all minus {g}', [c for c in ALL if c not in cols])]:
            e1(ext, ['HGB'], folds=3, feats=feats, fname=fname, exp='E6')
            e3(ng, ['HGB'], feats=feats, fname=fname, exp='E6')
    e1(ext, ['HGB'], folds=3, feats=['is_new_pseudo'] + NEIGH, fname='new_pseudo + neighbourhood', exp='E6')
    e3(ng, ['HGB'], feats=['is_new_pseudo'] + NEIGH, fname='new_pseudo + neighbourhood', exp='E6')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--feat-dir', default='../features')
    ap.add_argument('--out', default='results_q1')
    ap.add_argument('--ext-n', type=int, default=120000)
    ap.add_argument('--ng-train-n', type=int, default=150000)
    ap.add_argument('--ng-val-n', type=int, default=50000)
    ap.add_argument('--ng-test-n', type=int, default=200000)
    ap.add_argument('--models', default='HGB,RF')
    ap.add_argument('--only', default='E1,E2,E3,E4,E6')
    ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    global SEED; SEED = a.seed
    ext, ng = load_all(a); models = a.models.split(','); todo = a.only.split(',')
    for name, fn in [('E1', lambda: e1(ext, models)), ('E2', lambda: e2(ext, models)), ('E3', lambda: e3(ng, models)),
                     ('E4', lambda: e4(ext, ng, models)), ('E6', lambda: e6(ext, ng))]:
        if name in todo:
            print(f'\n=== {name} ===', flush=True); fn()
            pd.DataFrame(ROWS).to_csv(os.path.join(a.out, 'all_results.csv'), index=False)
    R = pd.DataFrame(ROWS)
    R['setting_g'] = R.setting.str.replace(r' fold\d', '', regex=True)
    cols = ['f1', 'prec', 'rec', 'fpr', 'auc', 'tpr_at_1fpr', 'fpr_at_val_thr1', 'tpr_at_val_thr1']
    S = R.groupby(['exp', 'setting_g', 'model', 'feats'], sort=False)[cols].agg(['mean', 'std']) * 100
    S.round(2).to_csv(os.path.join(a.out, 'summary.csv'))
    print('\n' + (R.groupby(['exp', 'setting_g', 'model', 'feats'], sort=False)[cols].mean() * 100).round(2).to_string())


if __name__ == '__main__':
    main()
