"""
Adaptive attacker (Section 7.x): phantoms that first send k plausible beacons ("warm-up") before the attack matters.
Test phantoms = synthetic persistent phantoms injected into Extension 1416 non-Grid runs (phantom.py aug0.1 and
aug0.1_drift files), plus the real GridSybil 1416 phantoms. Detection is measured as a function of the number of
messages k a receiver has already heard from the phantom (msg_idx), and at pseudonym level after a warm-up of K messages.
Detectors (trained on data independent of the test streams):
  NG     NextGen Train, all features              NG+R   NextGen Train + phantoms, physical features (proposed)
  EXT    Extension 0709, all four Sybil types      EXT-3  Extension 0709 without GridSybil (never saw persistent phantoms)
Usage (venv, sybil_pipeline folder):  python adaptive.py     (writes results_adaptive/)
"""
import glob, os, sys, time, gc, argparse
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from experiments import ALL, f1_thr
from sklearn.ensemble import HistGradientBoostingClassifier as HGB
NOVELTY = ['msg_idx', 'pseudo_age', 'is_new_pseudo', 'first_seen_dist', 'n_pseudo_1s', 'new_pseudo_5s', 'new_pseudo_frac_5s']
PHYS = [f for f in ALL if f not in NOVELTY]
COLS = ['receiver', 'pseudo', 'label', 'attack'] + ALL
ap = argparse.ArgumentParser()
ap.add_argument('--feat', default='../features'); ap.add_argument('--pfeat', default='../features_phantom')
ap.add_argument('--out', default='results_adaptive'); ap.add_argument('--seeds', default='0,1,2,3,4')
ap.add_argument('--train-n', type=int, default=300000); ap.add_argument('--rcv', type=int, default=60)
ap.add_argument('--quick', action='store_true')
a = ap.parse_args(); SEEDS = [int(s) for s in a.seeds.split(',')]
if a.quick: a.train_n, a.rcv = 20000, 10
os.makedirs(a.out, exist_ok=True)
def read(p):
    d = pd.read_pickle(p); d = d[[c for c in COLS if c in d.columns]].copy(); d['pseudo'] = d.pseudo.astype(str)
    d['subset'] = os.path.basename(p).replace('.pkl.gz', ''); return d
def sample_all(paths, n):
    out = {s: [] for s in SEEDS}; n_each = max(1, n // max(1, len(paths)))
    for p in paths:
        d = read(p)
        for s in SEEDS:
            rng = np.random.default_rng(3000 + s); out[s].append(d.iloc[np.sort(rng.choice(len(d), min(n_each, len(d)), replace=False))])
        del d; gc.collect()
    return {s: pd.concat(v, ignore_index=True) for s, v in out.items()}
def blocks_all(paths, k):
    out = {s: [] for s in SEEDS}
    for p in paths:
        d = read(p); rc = d.receiver.unique()
        for s in SEEDS:
            pick = np.random.default_rng(4000 + s).choice(rc, min(k, len(rc)), replace=False); out[s].append(d[d.receiver.isin(pick)])
        del d; gc.collect()
    return {s: pd.concat(v, ignore_index=True) for s, v in out.items()}
def split_val(D, s):
    rc = D.receiver.unique(); va = set(np.random.default_rng(s).choice(rc, max(1, len(rc) // 6), replace=False))
    m = D.receiver.isin(va).values; return D[~m], D[m]
def fit(tr, va, feats, s):
    m = HGB(max_iter=300, learning_rate=0.1, random_state=s).fit(tr[feats].values, tr.label.values)
    return m, f1_thr(va.label.values, m.predict_proba(va[feats].values)[:, 1])
F, PF = a.feat, a.pfeat; q = (lambda L: L[:1]) if a.quick else (lambda L: L)
BINS = [(0, 0, '0'), (1, 1, '1'), (2, 4, '2-4'), (5, 9, '5-9'), (10, 19, '10-19'), (20, 10**9, '20+')]
ROWS, PS = [], []; t0 = time.time()
print('loading data (one pass per file)', flush=True)
EXT0709 = sample_all(q(sorted(glob.glob(f'{F}/ext_*_0709.pkl.gz'))), a.train_n)
NGB = (sample_all(q(sorted(glob.glob(f'{PF}/ng_*_Train_base.pkl.gz'))), a.train_n), sample_all(q(sorted(glob.glob(f'{PF}/ng_*_Validation_base.pkl.gz'))), a.train_n // 3))
NGA = (sample_all(q(sorted(glob.glob(f'{PF}/ng_*_Train_aug0.1.pkl.gz'))), a.train_n), sample_all(q(sorted(glob.glob(f'{PF}/ng_*_Validation_aug0.1.pkl.gz'))), a.train_n // 3))
TESTS = {'synthetic (mixed)': blocks_all(q(sorted(glob.glob(f'{PF}/ext_*_1416_aug0.1.pkl.gz'))), a.rcv),
         'synthetic (drift)': blocks_all(q(sorted(glob.glob(f'{PF}/ext_*_1416_aug0.1_drift.pkl.gz'))), a.rcv),
         'GridSybil (real)': blocks_all([f'{F}/ext_GridSybil_1416.pkl.gz'], a.rcv)}
print(f'loaded in {time.time()-t0:.0f}s', flush=True)
for s in SEEDS:
    print(f'=== seed {s}', flush=True)
    E = EXT0709[s]; e_tr, e_va = split_val(E, s)
    E3 = E[E.subset != 'ext_GridSybil_0709']; e3_tr, e3_va = split_val(E3, s)
    M = {'NG': (*fit(NGB[0][s], NGB[1][s], ALL, s), ALL),
         'NG+R': (*fit(NGA[0][s], NGA[1][s], PHYS, s), PHYS),
         'EXT': (*fit(e_tr, e_va, ALL, s), ALL), 'EXT-3': (*fit(e3_tr, e3_va, ALL, s), ALL)}
    tests = {tn: v[s] for tn, v in TESTS.items()}
    for tn, T in tests.items():
        syb = (T.attack == 'synthPhantom').values if tn.startswith('synthetic') else (T.label == 1).values
        gen = (T.label == 0).values; k = T.msg_idx.values
        for mn, (m, thr, feats) in M.items():
            al = m.predict_proba(T[feats].values)[:, 1] >= thr
            r = dict(seed=s, test=tn, model=mn, fpr=float(al[gen].mean()), fpr_first=float(al[gen & (k == 0)].mean()), fpr_hist=float(al[gen & (k > 0)].mean()))
            for lo, hi, lab in BINS:
                sel = syb & (k >= lo) & (k <= hi); r[f'rec_k{lab}'] = float(al[sel].mean()) if sel.any() else np.nan
            ROWS.append(r)
            D = pd.DataFrame(dict(r=T.receiver.values, ps=T.pseudo.values, k=k, a=al, syb=syb, gen=gen))
            for K in [0, 1, 3, 5, 10]:
                G = D[D.k >= K].groupby(['r', 'ps']); P = pd.DataFrame(dict(syb=G.syb.max(), gen=G.gen.max(), maj=G.a.mean() >= 0.5))
                PS.append(dict(seed=s, test=tn, model=mn, warmup=K, ps_tpr=float(P.maj[P.syb].mean()), ps_fpr=float(P.maj[P.gen].mean()),
                               n_syb=int(P.syb.sum())))
            print(f"  {tn:18s} {mn:6s} rec k=0 {r['rec_k0']*100:5.1f}  k=5-9 {r['rec_k5-9']*100:5.1f}  k=20+ {r['rec_k20+']*100 if r['rec_k20+']==r['rec_k20+'] else float('nan'):5.1f}  FPR {r['fpr']*100:4.1f}", flush=True)
    pd.DataFrame(ROWS).to_csv(f'{a.out}/adaptive_by_k.csv', index=False); pd.DataFrame(PS).to_csv(f'{a.out}/adaptive_pseudonym.csv', index=False)
R = pd.DataFrame(ROWS); print((R.groupby(['test', 'model']).mean(numeric_only=True).drop(columns='seed') * 100).round(1).to_string())
P = pd.DataFrame(PS); print((P.groupby(['test', 'model', 'warmup'])[['ps_tpr', 'ps_fpr']].mean() * 100).round(1).unstack('warmup').to_string())
print(f'Done in {(time.time()-t0)/60:.0f} min')
