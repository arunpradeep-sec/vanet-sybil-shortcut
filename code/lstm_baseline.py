"""
Sequence-model baseline: does an LSTM over each pseudonym's recent message history generalise better than
gradient boosting on per-message features? Both models are trained and tested on IDENTICAL samples.

Input per message: the last W messages heard from the same pseudonym by the same receiver (oldest first),
each described by the 21 harmonised features + a 'real message' flag; missing history is zero-padded.
HGB sees only the current message's 21 features, as in the main experiments.

Experiments (same protocol as experiments.py / loto.py):
  L2  Extension cross-density (0709 -> 1416, 1416 -> 0709); also gives the 'seen' reference for L8
  L3  NextGen official split
  L4  cross-dataset (Extension -> NextGen test, NextGen train -> Extension)
  L8  leave-one-Sybil-type-out: train 3 Extension types at density A, test the 4th at density B
Thresholds come from validation data of the training side. Seeds change sample, splits and initialisation.

Usage (venv, sybil_pipeline folder):
  python lstm_baseline.py --quick            # ~10 min smoke test
  caffeinate -i python lstm_baseline.py      # full run (default 3 seeds), writes results_lstm/
"""
import argparse, glob, os, sys, time
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import experiments as E
from sklearn.ensemble import HistGradientBoostingClassifier

F = len(E.ALL)
TYPES = ['GridSybil', 'DataReplaySybil', 'DoSRandomSybil', 'DoSDisruptiveSybil']


# ------------------------------------------------------------------------------ data
def signed_log(a):
    return np.sign(a) * np.log1p(np.abs(a))


def load_windows(path, n, rng, W):
    """Sample n messages from one feature file and gather each one's last W messages from the same pseudonym."""
    d = pd.read_pickle(path)
    N = len(d)
    X = signed_log(d[E.ALL].values.astype(np.float32))
    rec = pd.factorize(d.receiver.values)[0]; ps = pd.factorize(d.pseudo.astype(str).values)[0]
    order = np.lexsort((d.rcvTime.values, ps, rec))
    r, p = rec[order], ps[order]
    new = np.ones(N, bool); new[1:] = (r[1:] != r[:-1]) | (p[1:] != p[:-1])
    pos = np.arange(N) - np.maximum.accumulate(np.where(new, np.arange(N), 0))
    sel = np.sort(rng.choice(N, min(n, N), replace=False))      # positions in sorted order
    win = np.zeros((len(sel), W, F + 1), np.float32)
    for l in range(W):
        ok = pos[sel] >= l
        src = order[sel[ok] - l]
        win[ok, W - 1 - l, :F] = X[src]; win[ok, W - 1 - l, F] = 1.0
    rows = order[sel]
    meta = pd.DataFrame({'sender': d.sender.values[rows], 'label': d.label.values[rows].astype(int),
                         'attack': d.attack.values[rows]})
    meta['subset'] = os.path.basename(path).replace('.pkl.gz', '')
    del d, X
    return win, meta


def load_all(a, seed):
    rng = np.random.default_rng(seed); parts = {}
    for p in sorted(glob.glob(os.path.join(a.feat_dir, 'ext_*.pkl.gz'))):
        parts.setdefault('ext', []).append(load_windows(p, a.ext_n, rng, a.window))
    for split, n in [('Train', a.ng_train_n), ('Validation', a.ng_val_n), ('Test', a.ng_test_n)]:
        for p in sorted(glob.glob(os.path.join(a.feat_dir, f'ng_*_{split}.pkl.gz'))):
            parts.setdefault(split, []).append(load_windows(p, n, rng, a.window))
    out = {}
    for k, v in parts.items():
        W_ = np.concatenate([w for w, _ in v]); M = pd.concat([m for _, m in v], ignore_index=True)
        M['sender'] = M.sender.astype('category').cat.codes
        if k == 'ext':
            M['density'] = M.subset.str[-4:]; M['type'] = M.subset.str.replace('ext_', '').str[:-5]
        else:
            M['scenario'] = M.subset.str.replace('ng_InTAS_', '').str.replace(f'_{k}', '')
        out[k] = (W_, M)
        print(f'  {k}: {len(M)} sequences, {M.label.mean()*100:.1f}% Sybil, '
              f'{(W_[:, :-1, F].sum(1) == 0).mean()*100:.1f}% without history', flush=True)
    return out


def standardise(train_win, *wins):
    """z-score each feature on the training set's real rows; padding rows stay zero."""
    real = train_win[:, :, F] > 0
    mu = train_win[:, :, :F][real].mean(0); sd = train_win[:, :, :F][real].std(0) + 1e-6
    res = []
    for w in (train_win,) + wins:
        z = w.copy(); m = z[:, :, F:F + 1]
        z[:, :, :F] = (z[:, :, :F] - mu) / sd * m
        res.append(z)
    return res


# ------------------------------------------------------------------------------ models
def device():
    import torch
    if torch.backends.mps.is_available():
        return torch.device('mps')
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def make_lstm(hidden):
    import torch, torch.nn as nn

    class Net(nn.Module):
        def __init__(s):
            super().__init__()
            s.lstm = nn.LSTM(F + 1, hidden, batch_first=True)
            s.head = nn.Sequential(nn.Linear(hidden + F + 1, 64), nn.ReLU(), nn.Dropout(0.1), nn.Linear(64, 1))
        def forward(s, x):
            _, (h, _) = s.lstm(x)
            return s.head(torch.cat([h[-1], x[:, -1, :]], 1)).squeeze(1)
    return Net()


def predict(net, X, dev, bs=8192):
    import torch
    net.eval(); out = []
    with torch.no_grad():
        for i in range(0, len(X), bs):
            out.append(torch.sigmoid(net(torch.from_numpy(X[i:i + bs]).to(dev))).float().cpu().numpy())
    return np.concatenate(out)


def fit_lstm(Xtr, ytr, Xva, yva, a, seed):
    import torch
    from sklearn.metrics import roc_auc_score
    torch.manual_seed(seed); np.random.seed(seed); dev = device()
    net = make_lstm(a.hidden).to(dev)
    opt = torch.optim.AdamW(net.parameters(), lr=a.lr, weight_decay=1e-4)
    pw = torch.tensor(float((1 - ytr.mean()) / max(ytr.mean(), 1e-6)), device=dev)
    lossf = torch.nn.BCEWithLogitsLoss(pos_weight=pw)
    Xt, yt = torch.from_numpy(Xtr), torch.from_numpy(ytr.astype(np.float32))
    best, best_state = -1, None
    for ep in range(a.epochs):
        net.train(); perm = torch.randperm(len(Xt))
        for i in range(0, len(Xt), a.batch):
            idx = perm[i:i + a.batch]
            opt.zero_grad(); lossf(net(Xt[idx].to(dev)), yt[idx].to(dev)).backward(); opt.step()
        auc = roc_auc_score(yva, predict(net, Xva, dev))
        if auc > best:
            best = auc; best_state = {k: v.detach().clone() for k, v in net.state_dict().items()}
    net.load_state_dict(best_state)
    return lambda X: predict(net, X, dev)


def fit_hgb(Xtr, ytr, seed):
    m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, random_state=seed).fit(Xtr[:, -1, :F], ytr)
    return lambda X: m.predict_proba(X[:, -1, :F])[:, 1]


# ------------------------------------------------------------------------------ evaluation
def run(exp, setting, Wtr, Mtr, Wva, Mva, tests, a, seed):
    """tests: list of (setting name, W, M, by) evaluated with the same fitted model."""
    Ztr, Zva, *Zte = standardise(Wtr, Wva, *[w for _, w, _, _ in tests])
    for model in a.models.split(','):
        t0 = time.time()
        if model == 'LSTM':
            if a.no_torch:
                continue
            f = fit_lstm(Ztr, Mtr.label.values, Zva, Mva.label.values, a, seed)
        else:
            f = fit_hgb(Ztr, Mtr.label.values, seed)
        pv = f(Zva); thr, thr1 = E.f1_thr(Mva.label.values, pv), E.thr_at_fpr(Mva.label.values, pv)
        for (name, _, M, by), Z in zip(tests, Zte):
            E.score(exp, name, model, 'sequence' if model == 'LSTM' else 'message', M.label.values, f(Z), thr, thr1,
                    by, time.time() - t0)


def split_val(M, seed):
    E.SEED = seed
    return E.inner_val(M.reset_index(drop=True), 0)


def one_seed(a, seed):
    print(f'\n=== seed {seed}: building sequences', flush=True)
    D = load_all(a, seed); We, Me = D['ext']
    take = lambda W, M, m: (W[m.values], M[m].reset_index(drop=True))
    # L2 (+ 'seen' reference for L8)
    for A, B in [('0709', '1416'), ('1416', '0709')]:
        Ws, Ms = take(We, Me, Me.density == A); Wt, Mt = take(We, Me, Me.density == B)
        tr, va = split_val(Ms, seed)
        tests = [(f'Ext {A} -> {B}', Wt, Mt, Mt.attack.values)]
        tests += [(f'{H} {A}->{B} seen', *take(Wt, Mt, Mt.type == H), None) for H in TYPES]
        run('L2', f'Ext {A} -> {B}', Ws[tr], Ms.iloc[tr], Ws[va], Ms.iloc[va], tests, a, seed)
    # L3
    (Wtr, Mtr), (Wva, Mva), (Wte, Mte) = D['Train'], D['Validation'], D['Test']
    run('L3', 'NG official', Wtr, Mtr, Wva, Mva, [('NG official split', Wte, Mte, Mte.scenario.values)], a, seed)
    # L4
    tr, va = split_val(Me, seed)
    run('L4', 'Ext -> NG', We[tr], Me.iloc[tr], We[va], Me.iloc[va], [('Ext -> NG test', Wte, Mte, Mte.scenario.values)], a, seed)
    run('L4', 'NG -> Ext', Wtr, Mtr, Wva, Mva, [('NG train -> Ext', We, Me, Me.attack.values)], a, seed)
    # L8 unseen
    for H in TYPES:
        for A, B in [('0709', '1416'), ('1416', '0709')]:
            Ws, Ms = take(We, Me, (Me.density == A) & (Me.type != H)); Wt, Mt = take(We, Me, (Me.density == B) & (Me.type == H))
            tr, va = split_val(Ms, seed)
            run('L8', f'{H} {A}->{B}', Ws[tr], Ms.iloc[tr], Ws[va], Ms.iloc[va], [(f'{H} {A}->{B} unseen', Wt, Mt, None)], a, seed)
    del D


def summarise(out):
    R = pd.read_csv(os.path.join(out, 'lstm_results.csv'))
    R['group'] = R.setting.str.replace(r' (0709|1416)->(0709|1416)', '', regex=True)
    cols = ['f1', 'mcc', 'auc', 'tpr_at_1fpr']
    per_seed = R.groupby(['group', 'model', 'seed'], sort=False)[cols].mean()
    g = per_seed.groupby(level=[0, 1], sort=False)
    S = (g.mean() * 100).round(2).map('{:.2f}'.format) + ' ± ' + (g.std().fillna(0) * 100).round(2).map('{:.2f}'.format)
    S.to_csv(os.path.join(out, 'lstm_summary.csv'))
    # mean over the four Sybil types for seen / unseen
    L = R[R.setting.str.contains(' seen| unseen', regex=True)].copy()
    L['mode'] = np.where(L.setting.str.endswith('unseen'), 'unseen', 'seen')
    M = L.groupby(['mode', 'model', 'seed'])[cols].mean().groupby(level=[0, 1])
    T = (M.mean() * 100).round(2).map('{:.2f}'.format) + ' ± ' + (M.std().fillna(0) * 100).round(2).map('{:.2f}'.format)
    T.to_csv(os.path.join(out, 'lstm_loto_mean.csv'))
    print('\n' + S.to_string() + '\n\nLeave-one-type-out, mean over types:\n' + T.to_string())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--feat-dir', default='../features'); ap.add_argument('--out', default='results_lstm')
    ap.add_argument('--seeds', default='0,1,2'); ap.add_argument('--models', default='LSTM,HGB')
    ap.add_argument('--window', type=int, default=8); ap.add_argument('--hidden', type=int, default=64)
    ap.add_argument('--epochs', type=int, default=5); ap.add_argument('--batch', type=int, default=1024)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--ext-n', type=int, default=100000); ap.add_argument('--ng-train-n', type=int, default=100000)
    ap.add_argument('--ng-val-n', type=int, default=30000); ap.add_argument('--ng-test-n', type=int, default=150000)
    ap.add_argument('--quick', action='store_true'); ap.add_argument('--no-torch', action='store_true', help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.quick:
        a.seeds, a.epochs, a.ext_n, a.ng_train_n, a.ng_val_n, a.ng_test_n = '0', 2, 8000, 8000, 3000, 8000
        a.out += '_quick'
    os.makedirs(a.out, exist_ok=True)
    if not a.no_torch:
        import torch; print(f'PyTorch {torch.__version__} on {device()}', flush=True)
    t0 = time.time()
    for s in [int(x) for x in a.seeds.split(',')]:
        E.ROWS.clear(); one_seed(a, s)
        R = pd.DataFrame(E.ROWS); R['seed'] = s
        f = os.path.join(a.out, 'lstm_results.csv')
        R.to_csv(f, mode='a', header=not os.path.exists(f), index=False)
        print(f'seed {s} done after {(time.time() - t0) / 60:.0f} min', flush=True)
    summarise(a.out)
    print(f'\nResults written to {os.path.abspath(a.out)}/')


if __name__ == '__main__':
    main()
