"""
Proposed transfer-robust detector (Section 7.x): three fixed ingredients, chosen before looking at any target result.
  (1) synthetic persistent phantoms in the training data (aug0.1 files from phantom.py),
  (2) a physical-consistency feature set: the 21 features minus the seven identity-novelty counters,
  (3) per-pseudonym majority voting over each receiver's message stream.
Ablation: B = all features, no phantoms (baseline) | A = all + phantoms | F = physical, no phantoms | R = physical + phantoms.
Tests use complete message streams of randomly drawn receivers, so message-level and pseudonym-level results come
from the same test data. 5 seeds.
Usage (venv, sybil_pipeline folder):  python robust.py      (writes results_robust/)
"""
import glob, os, sys, time, gc, argparse
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from experiments import KIN, HIST, NEIGH, ALL, f1_thr
from sklearn.ensemble import HistGradientBoostingClassifier as HGB
from sklearn.metrics import f1_score, matthews_corrcoef, roc_auc_score, roc_curve
NOVELTY = ['msg_idx', 'pseudo_age', 'is_new_pseudo', 'first_seen_dist', 'n_pseudo_1s', 'new_pseudo_5s', 'new_pseudo_frac_5s']
PHYS = [f for f in ALL if f not in NOVELTY]                      # 14 features
COLS = ['receiver', 'pseudo', 'label', 'attack'] + ALL
ap = argparse.ArgumentParser()
ap.add_argument('--feat', default='../features'); ap.add_argument('--pfeat', default='../features_phantom')
ap.add_argument('--out', default='results_robust'); ap.add_argument('--seeds', default='0,1,2,3,4')
ap.add_argument('--train-n', type=int, default=300000); ap.add_argument('--ext-rcv', type=int, default=30)
ap.add_argument('--ng-rcv', type=int, default=20); ap.add_argument('--quick', action='store_true')
a = ap.parse_args(); SEEDS = [int(s) for s in a.seeds.split(',')]
if a.quick: a.train_n, a.ext_rcv, a.ng_rcv = 20000, 5, 5
os.makedirs(a.out, exist_ok=True)

def read(p):
    d = pd.read_pickle(p); d = d[[c for c in COLS if c in d.columns]].copy(); d['pseudo'] = d.pseudo.astype(str)
    d['subset'] = os.path.basename(p).replace('.pkl.gz', ''); return d

def per_seed_samples(paths, n_total):          # one pass over the files, a training sample per seed
    out = {s: [] for s in SEEDS}; n_each = max(1, n_total // max(1, len(paths)))
    for p in paths:
        d = read(p)
        for s in SEEDS:
            rng = np.random.default_rng(1000 + s)
            out[s].append(d.iloc[np.sort(rng.choice(len(d), min(n_each, len(d)), replace=False))])
        del d; gc.collect()
    return {s: pd.concat(v, ignore_index=True) for s, v in out.items()}

def per_seed_blocks(paths, k):                  # complete streams of k random receivers per file, per seed
    out = {s: [] for s in SEEDS}
    for p in paths:
        d = read(p); rc = d.receiver.unique()
        for s in SEEDS:
            pick = np.random.default_rng(2000 + s).choice(rc, min(k, len(rc)), replace=False)
            out[s].append(d[d.receiver.isin(pick)])
        del d; gc.collect()
    return {s: pd.concat(v, ignore_index=True) for s, v in out.items()}

def split_val(D, seed):
    rng = np.random.default_rng(seed)
    rc = D.receiver.unique(); va = set(rng.choice(rc, max(1, len(rc) // 6), replace=False))
    m = D.receiver.isin(va).values; return D[~m], D[m]

def fit(tr, va, feats, seed):
    m = HGB(max_iter=300, learning_rate=0.1, random_state=seed).fit(tr[feats].values, tr.label.values)
    return m, f1_thr(va.label.values, m.predict_proba(va[feats].values)[:, 1])

def evaluate(exp, setting, variant, seed, m, thr, feats, T):
    p = m.predict_proba(T[feats].values)[:, 1]; y = T.label.values; yh = p >= thr
    fpr, tpr, _ = roc_curve(y, p)
    r = dict(exp=exp, setting=setting, variant=variant, seed=seed, n=len(T), f1=f1_score(y, yh), mcc=matthews_corrcoef(y, yh),
             auc=roc_auc_score(y, p), tpr1=float(np.interp(0.01, fpr, tpr)), fpr=float(yh[y == 0].mean()), rec=float(yh[y == 1].mean()))
    for t in sorted(set(T.attack[T.label == 1])): r[f'rec_{t}'] = float(yh[(T.attack == t).values & (y == 1)].mean())
    G = pd.DataFrame(dict(r=T.receiver.values, ps=T.pseudo.values, lab=y, a=yh, att=T.attack.values)).groupby(['r', 'ps'])
    P = pd.DataFrame(dict(lab=G.lab.max(), maj=G.a.mean() >= 0.5, anyal=G.a.max(), att=G.att.first()))
    r['ps_tpr_majority'] = float(P.maj[P.lab == 1].mean()); r['ps_fpr_majority'] = float(P.maj[P.lab == 0].mean())
    r['ps_tpr_any'] = float(P.anyal[P.lab == 1].mean()); r['ps_fpr_any'] = float(P.anyal[P.lab == 0].mean())
    for t in sorted(set(P.att[P.lab == 1])): r[f'ps_tpr_{t}'] = float(P.maj[(P.att == t) & (P.lab == 1)].mean())
    ROWS.append(r); print(f"  {exp} {setting:26s} {variant} seed{seed} MCC={r['mcc']*100:5.1f} TPR@1={r['tpr1']*100:5.1f} "
                          f"ps-TPR={r['ps_tpr_majority']*100:5.1f} ps-FPR={r['ps_fpr_majority']*100:5.1f}", flush=True)

t0 = time.time(); ROWS = []
F, PF = a.feat, a.pfeat
q = (lambda L: L[:2]) if a.quick else (lambda L: L)
ext_files = q(sorted(glob.glob(f'{F}/ext_*.pkl.gz'))); ng_test = q(sorted(glob.glob(f'{F}/ng_*_Test.pkl.gz')))
print('loading test streams', flush=True)
EXT = per_seed_blocks(ext_files, a.ext_rcv); NGT = per_seed_blocks(ng_test, a.ng_rcv)
print('loading training data', flush=True)
TR = {}
for v in ['base', 'aug0.1']:
    TR[('ng', v, 'tr')] = per_seed_samples(q(sorted(glob.glob(f'{PF}/ng_*_Train_{v}.pkl.gz'))), a.train_n)
    TR[('ng', v, 'va')] = per_seed_samples(q(sorted(glob.glob(f'{PF}/ng_*_Validation_{v}.pkl.gz'))), a.train_n // 3)
    TR[('ext', v)] = per_seed_samples(q(sorted(glob.glob(f'{PF}/ext_*_1416_{v}.pkl.gz'))), a.train_n)
TR['extall'] = per_seed_samples(ext_files, a.train_n)
print(f'loaded in {time.time()-t0:.0f}s', flush=True)
VAR = {'B': ('base', ALL), 'A': ('aug0.1', ALL), 'F': ('base', PHYS), 'R': ('aug0.1', PHYS)}
for s in SEEDS:
    ext, ngt = EXT[s], NGT[s]
    grid0709 = ext[ext.subset == 'ext_GridSybil_0709']; seen0709 = ext[ext.subset.isin(['ext_DataReplaySybil_0709', 'ext_DoSRandomSybil_0709', 'ext_DoSDisruptiveSybil_0709'])]
    for k, (v, feats) in VAR.items():
        m, thr = fit(TR[('ng', v, 'tr')][s], TR[('ng', v, 'va')][s], feats, s)
        evaluate('P1', 'NG -> Ext (all types)', k, s, m, thr, feats, ext)
        evaluate('P1', 'NG -> NG test', k, s, m, thr, feats, ngt)
        tr, va = split_val(TR[('ext', v)][s], s); m, thr = fit(tr, va, feats, s)
        if len(grid0709): evaluate('P2', 'Ext non-Grid -> Grid 0709', k, s, m, thr, feats, grid0709)
        if len(seen0709): evaluate('P2', 'Ext non-Grid -> seen 0709', k, s, m, thr, feats, seen0709)
    for k, feats in [('B', ALL), ('F', PHYS)]:                     # E4a direction: phantoms not needed
        tr, va = split_val(TR['extall'][s], s); m, thr = fit(tr, va, feats, s)
        evaluate('E4a', 'Ext -> NG test', k, s, m, thr, feats, ngt)
    pd.DataFrame(ROWS).to_csv(f'{a.out}/robust_results.csv', index=False)
R = pd.DataFrame(ROWS); num = R.select_dtypes('number').columns.drop(['seed', 'n'])
S = R.groupby(['exp', 'setting', 'variant'], sort=False)[num].agg(['mean', 'std']) * 100
S.round(2).to_csv(f'{a.out}/robust_summary.csv')
print((R.groupby(['exp', 'setting', 'variant'], sort=False)[['mcc', 'tpr1', 'ps_tpr_majority', 'ps_fpr_majority']].mean() * 100).round(1).to_string())
print(f'Done in {(time.time()-t0)/60:.0f} min')
