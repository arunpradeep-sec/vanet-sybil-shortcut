"""
Persistent-phantom augmentation (E9): does teaching the attack MECHANISM close the transfer gap?

NextGen phantoms are each heard once, so a NextGen-trained detector learns "no history = Sybil" and misses
Extension's GridSybil phantoms, which keep plausible trajectories. Here we add SYNTHETIC persistent phantoms to the
training data only, built from the training dataset's own genuine traffic (never from the test dataset):
for a fraction of genuine "host" vehicles, 2-5 phantom pseudonyms travel with the host at a fixed grid offset
(half of them) or a slowly oscillating offset (the other half), with the host's speed, heading and timing plus noise.
Phantoms keep their pseudonym for the whole trace, so receivers hear them many times.

P1  NextGen Train (+ phantoms) -> Extension (all four Sybil types) and -> NextGen official Test
P2  Extension 1416, three non-Grid Sybil types (+ phantoms) -> unseen GridSybil 0709 (compare E8)
Baseline = the same receivers without phantoms, so both arms see identical genuine and Sybil traffic.

Usage (venv, sybil_pipeline folder):
  python phantom.py --stage prep          # read raw zips (capped receivers), add phantoms, compute features (~1-2 h)
  python phantom.py --stage eval          # 5 seeds, HGB, writes results_phantom/ (~1 h)
  python phantom.py --stage prep --quick  # small smoke test, then: python phantom.py --stage eval --quick
"""
import argparse, glob, os, re, shutil, sys, tempfile, time, zipfile
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_veremi as cv
import experiments as E
from sklearn.ensemble import HistGradientBoostingClassifier

HERE = os.path.dirname(os.path.abspath(__file__))
P2_TRAIN = ['DataReplaySybil_1416', 'DoSRandomSybil_1416', 'DoSDisruptiveSybil_1416']


# ------------------------------------------------------------------------------ phantoms
def augment(df, frac, rng, style='mixed'):
    """Add persistent phantom pseudonyms around a fraction of genuine host vehicles (all receivers that hear a host
    also hear its phantoms, with the same pseudonyms and offsets)."""
    df = df.copy(); df['pseudo'] = df.pseudo.astype(str)
    gen = df[df.label == 0]
    per_sender = gen.groupby('sender').size()
    all_genuine = df.groupby('sender').label.max() == 0
    cand = per_sender.index[(per_sender >= 5) & all_genuine.reindex(per_sender.index).values]
    hosts = rng.choice(np.array(cand), int(round(frac * len(cand))), replace=False) if len(cand) else []
    grid = [(dl, dlat) for dl in (-12, -6, 6, 12) for dlat in (-3.5, 0.0, 3.5)]
    out = []
    for h in hosts:
        H = gen[gen.sender == h]
        th = np.radians(H.hed.values); fx, fy = np.sin(th), np.cos(th); rx_, ry_ = np.cos(th), -np.sin(th)
        t = H.rcvTime.values
        for j in range(int(rng.integers(2, 6))):
            if style == 'grid' or (style == 'mixed' and j % 2 == 0):   # fixed grid slot next to the host
                dl, dlat = grid[rng.integers(len(grid))]
                dl = np.full(len(H), float(dl)); dlat = np.full(len(H), float(dlat))
            else:                                                  # slowly oscillating offset, 5-25 m away
                r0, a0 = rng.uniform(5, 25), rng.uniform(0, 2 * np.pi)
                A, T, ph = rng.uniform(1, 4), rng.uniform(30, 120), rng.uniform(0, 2 * np.pi)
                osc = A * np.sin(2 * np.pi * t / T + ph)
                dl = r0 * np.cos(a0) + osc; dlat = r0 * np.sin(a0) + 0.3 * osc
            n = len(H)
            P = pd.DataFrame({
                'receiver': H.receiver.values, 'sender': H.sender.values, 'pseudo': f'ph_{h}_{j}',
                'rcvTime': t + rng.uniform(0.001, 0.02, n),
                'x': H.x.values + dl * fx + dlat * rx_ + rng.normal(0, 0.3, n),
                'y': H.y.values + dl * fy + dlat * ry_ + rng.normal(0, 0.3, n),
                'spd': np.clip(H.spd.values * (1 + rng.normal(0, 0.02, n)), 0, None), 'acc': H.acc.values,
                'hed': (H.hed.values + rng.normal(0, 1.0, n)) % 360,
                'pos_noise': H.pos_noise.values, 'spd_noise': H.spd_noise.values,
                'rx': H.rx.values, 'ry': H.ry.values, 'label': 1, 'attack': 'synthPhantom'})
            out.append(P)
    aug = pd.concat([df] + out, ignore_index=True) if out else df
    return aug, len(hosts)


# ------------------------------------------------------------------------------ raw readers (features switched off)
def ng_inner_no_test(outer_path, tmpdir):
    with zipfile.ZipFile(outer_path) as outer:
        for info in outer.infolist():
            name = info.filename.replace('\\', '/')
            if not name.lower().endswith('.zip') or info.file_size < 2000 or '/Test/' in name:
                continue
            tmp = os.path.join(tmpdir, 'inner.zip')
            with outer.open(info) as src, open(tmp, 'wb') as dst:
                shutil.copyfileobj(src, dst, 16 << 20)
            with zipfile.ZipFile(tmp) as inner:
                yield info.filename, inner
            os.remove(tmp)


def read_raw(reader, path, tmp, max_receivers, rng, inner=None):
    f, w = cv.features, cv.with_inner_zips
    cv.features = lambda df: df
    if inner is not None:
        cv.with_inner_zips = inner
    try:
        return reader(path, tmp, max_receivers, rng)
    finally:
        cv.features, cv.with_inner_zips = f, w


def suffix(fr, style):
    return f'aug{fr:g}' + ('' if style == 'mixed' else f'_{style}')


def save_variants(raw, name, out, fracs, rng, style='mixed'):
    raw = raw.sort_values(['receiver', 'rcvTime']).reset_index(drop=True)
    base = os.path.join(out, f'{name}_base.pkl.gz')
    if not os.path.exists(base):
        t0 = time.time(); cv.features(raw.assign(pseudo=raw.pseudo.astype(str))).to_pickle(base, compression='gzip')
        print(f'    {name}_base: {len(raw)} messages, {raw.label.mean()*100:.1f}% Sybil ({time.time()-t0:.0f}s)', flush=True)
    for fr in fracs:
        aug, nh = augment(raw, fr, rng, style); t0 = time.time()
        F = cv.features(aug); F.to_pickle(os.path.join(out, f'{name}_{suffix(fr, style)}.pkl.gz'), compression='gzip')
        print(f'    {name}_{suffix(fr, style)}: {nh} hosts, +{len(aug)-len(raw)} phantom messages, '
              f'{F.label.mean()*100:.1f}% Sybil ({time.time()-t0:.0f}s)', flush=True)


def prep(a):
    os.makedirs(a.out_feat, exist_ok=True); rng = np.random.default_rng(7)
    fracs = [float(x) for x in a.fracs.split(',')]
    tmp = tempfile.mkdtemp(dir=a.out_feat)
    try:
        for p in sorted(glob.glob(os.path.join(a.ng_dir, '*trafficCongestionSybil.zip'))):
            if a.quick and 'highway_2' not in p:
                continue
            print(f'\n{os.path.basename(p)}', flush=True)
            for k, raw in read_raw(cv.read_nextgen, p, tmp, a.max_receivers, rng, ng_inner_no_test).items():
                save_variants(raw, f'ng_{k}', a.out_feat, fracs, rng, a.style)
        for s in P2_TRAIN:
            if a.quick and s != 'DataReplaySybil_1416':
                continue
            p = os.path.join(a.ext_dir, f'{s}.zip'); print(f'\n{os.path.basename(p)}', flush=True)
            for k, raw in read_raw(cv.read_extension, p, tmp, a.max_receivers, rng).items():
                save_variants(raw, f'ext_{k}', a.out_feat, fracs, rng, a.style)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------------------------ evaluation
def fit(tr, va, seed):
    m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, random_state=seed).fit(tr[E.ALL].values, tr.label.values)
    pv = m.predict_proba(va[E.ALL].values)[:, 1]
    return m, E.f1_thr(va.label.values, pv), E.thr_at_fpr(va.label.values, pv)


def test(exp, setting, variant, m, thr, thr1, T, by):
    p = m.predict_proba(T[E.ALL].values)[:, 1]
    r = E.score(exp, setting, variant, 'all', T.label.values, p, thr, thr1, by)
    g = T.label.values == 0; first = g & (T.is_new_pseudo.values > 0.5); hist = g & ~first
    r['fa_first_msg'] = float((p[first] >= thr1).mean()) if first.any() else np.nan
    r['fa_with_history'] = float((p[hist] >= thr1).mean()) if hist.any() else np.nan


def load_glob(pattern, n, rng):
    fs = sorted(glob.glob(pattern))
    if not fs:
        raise SystemExit(f'no files match {pattern}')
    d = pd.concat([E.load(f, n, rng) for f in fs], ignore_index=True)
    d['sender'] = d.sender.astype('category').cat.codes
    return d


def evaluate(a, seed):
    E.SEED = seed; rng = np.random.default_rng(seed)
    variants = ['base'] + [suffix(float(x), a.style) for x in a.fracs.split(',')]
    pf, ff = a.out_feat, a.feat_dir
    ext_te = load_glob(os.path.join(ff, 'ext_*.pkl.gz'), a.ext_n, rng)
    ng_te = load_glob(os.path.join(ff, 'ng_*_Test.pkl.gz'), a.ng_test_n, rng)
    ng_te['scenario'] = ng_te.subset.str.replace('ng_InTAS_', '').str.replace('_Test', '')
    grid_te = ext_te[ext_te.subset == 'ext_GridSybil_0709'].reset_index(drop=True)
    seen_te = ext_te[ext_te.subset.isin([f'ext_{s.replace("1416", "0709")}' for s in P2_TRAIN])].reset_index(drop=True)
    for v in variants:                                             # P1: NextGen train -> Extension / NextGen test
        tr = load_glob(os.path.join(pf, f'ng_*_Train_{v}.pkl.gz'), a.train_n, rng)
        va = load_glob(os.path.join(pf, f'ng_*_Validation_{v}.pkl.gz'), a.train_n // 3, rng)
        m, thr, thr1 = fit(tr, va, seed)
        test('P1', 'NG train -> Ext', v, m, thr, thr1, ext_te, ext_te.attack.values)
        test('P1', 'NG train -> NG test', v, m, thr, thr1, ng_te, ng_te.scenario.values)
    for v in variants:                                             # P2: Extension 1416 non-Grid -> GridSybil 0709
        D = load_glob(os.path.join(pf, f'ext_*_1416_{v}.pkl.gz'), a.train_n, rng)
        itr, iva = E.inner_val(D, 0)
        m, thr, thr1 = fit(D.iloc[itr], D.iloc[iva], seed)
        test('P2', 'GridSybil 1416->0709 unseen', v, m, thr, thr1, grid_te, grid_te.attack.values)
        test('P2', '3 seen types 1416->0709', v, m, thr, thr1, seen_te, seen_te.attack.values)


def summarise(out):
    R = pd.read_csv(os.path.join(out, 'phantom_results.csv'))
    cols = [c for c in ['f1', 'mcc', 'auc', 'tpr_at_1fpr', 'rec_GridSybil', 'rec_DataReplaySybil', 'rec_DoSRandomSybil',
                        'rec_DoSDisruptiveSybil', 'fa_first_msg', 'fa_with_history', 'fpr_at_val_thr1'] if c in R]
    g = R.groupby(['exp', 'setting', 'model'], sort=False)[cols]
    S = (g.mean() * 100).round(2).map('{:.2f}'.format) + ' ± ' + (g.std().fillna(0) * 100).round(2).map('{:.2f}'.format)
    S.index = S.index.set_names(['exp', 'setting', 'variant'])
    S.to_csv(os.path.join(out, 'phantom_summary.csv'))
    with pd.option_context('display.width', 250, 'display.max_columns', 20):
        print('\n' + S.to_string())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', choices=['prep', 'eval'], required=True)
    ap.add_argument('--ext-dir', default=os.path.join(HERE, '..', 'VeReMi_Extension'))
    ap.add_argument('--ng-dir', default=os.path.join(HERE, '..', 'VeReMi_NextGen'))
    ap.add_argument('--feat-dir', default=os.path.join(HERE, '..', 'features'))
    ap.add_argument('--out-feat', default=os.path.join(HERE, '..', 'features_phantom'))
    ap.add_argument('--out', default='results_phantom')
    ap.add_argument('--fracs', default='0.05,0.1,0.2')
    ap.add_argument('--max-receivers', type=int, default=300)
    ap.add_argument('--style', choices=['mixed', 'grid', 'drift'], default='mixed',
                    help='phantom offsets: mixed (default), grid only, or drifting only')
    ap.add_argument('--seeds', default='0,1,2,3,4')
    ap.add_argument('--train-n', type=int, default=300000)
    ap.add_argument('--ext-n', type=int, default=200000); ap.add_argument('--ng-test-n', type=int, default=300000)
    ap.add_argument('--quick', action='store_true')
    a = ap.parse_args()
    if a.quick:
        a.max_receivers, a.fracs, a.seeds, a.train_n, a.ext_n, a.ng_test_n = 40, '0.1', '0', 30000, 20000, 20000
        a.out_feat += '_quick'; a.out += '_quick'
    t0 = time.time()
    if a.stage == 'prep':
        prep(a)
    else:
        os.makedirs(a.out, exist_ok=True); f = os.path.join(a.out, 'phantom_results.csv'); parts = []
        for s in [int(x) for x in a.seeds.split(',')]:
            E.ROWS.clear(); print(f'\n=== seed {s}', flush=True); evaluate(a, s)
            R = pd.DataFrame(E.ROWS); R['seed'] = s; parts.append(R)
            pd.concat(parts, ignore_index=True).to_csv(f, index=False)   # rewritten after every seed
        summarise(a.out)
    print(f'\nDone in {(time.time() - t0) / 60:.0f} min')


if __name__ == '__main__':
    main()
