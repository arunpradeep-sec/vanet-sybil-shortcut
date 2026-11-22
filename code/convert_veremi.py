"""
Convert VeReMi Extension and VeReMi NextGen Sybil subsets into one harmonised, receiver-side feature table
per subset. Reads straight from the downloaded zips (nested zips are copied one at a time to a temporary
file and deleted again), so nothing needs to be unzipped by hand.

Usage (in the venv, from the sybil_pipeline folder):
  python convert_veremi.py --test                 # quick check on the two smallest subsets
  python convert_veremi.py                        # everything
  python convert_veremi.py --max-receivers 400    # subsample receivers if memory runs short

Output: ../features/<dataset>_<subset>[_<split>].pkl.gz  and  ../features/manifest.csv

Harmonised schema (both datasets):
  heading in compass degrees (0 = north, clockwise), speed and |acceleration| as scalars,
  positional noise magnitude, speed noise magnitude, times in seconds.
  label = 1 for a Sybil message (Extension: sender's attack code 16-19; NextGen: attacker == 1).
"""
import argparse, glob, io, json, os, re, shutil, sys, tempfile, time, zipfile
import numpy as np, pandas as pd

EXT_SYBIL = {16: 'GridSybil', 17: 'DataReplaySybil', 18: 'DoSRandomSybil', 19: 'DoSDisruptiveSybil'}
FEATS = ['spd', 'acc', 'pos_noise', 'spd_noise', 'dist_rcv', 'beacon_dt', 'pos_jump', 'pos_pred_err',
         'spd_change_rate', 'hed_motion_err', 'msg_idx', 'pseudo_age', 'is_new_pseudo', 'first_seen_dist',
         'n_pseudo_1s', 'n_near5', 'n_near20', 'min_dist_other', 'new_pseudo_5s', 'new_pseudo_frac_5s',
         'n_similar_spd_near']
COLS = ['receiver', 'sender', 'pseudo', 'rcvTime', 'x', 'y', 'spd', 'acc', 'hed', 'pos_noise', 'spd_noise',
        'rx', 'ry', 'label', 'attack']


def basename(n):
    return re.split(r'[\\/]', n)[-1]


def with_inner_zips(outer_path, tmpdir):
    """Yield (inner_name, ZipFile) for every zip nested inside outer_path, one at a time."""
    with zipfile.ZipFile(outer_path) as outer:
        for info in outer.infolist():
            if not info.filename.lower().endswith('.zip') or info.file_size < 2000:
                continue
            tmp = os.path.join(tmpdir, 'inner.zip')
            with outer.open(info) as src, open(tmp, 'wb') as dst:
                shutil.copyfileobj(src, dst, 16 << 20)
            with zipfile.ZipFile(tmp) as inner:
                yield info.filename, inner
            os.remove(tmp)


def compass(hx, hy):
    return np.degrees(np.arctan2(hx, hy)) % 360


# ------------------------------------------------------------------------------------------ readers
def read_extension(path, tmpdir, max_receivers, rng):
    subset = os.path.basename(path)[:-4]
    frames = []
    for run, (iname, inner) in enumerate(with_inner_zips(path, tmpdir)):
        names = [n for n in inner.namelist() if 'traceJSON-' in basename(n)]
        attack = {}
        for n in names:
            p = basename(n).split('-'); attack[int(p[1])] = int(p[3][1:])
        if max_receivers and len(names) > max_receivers:
            names = list(rng.choice(names, max_receivers, replace=False))
        R = {c: [] for c in COLS}
        for n in names:
            rcv = int(basename(n).split('-')[1]); own_t, own_x, own_y = [], [], []; msgs = []
            for line in inner.read(n).decode().splitlines():
                o = json.loads(line)
                if o['type'] == 2:
                    own_t.append(o['rcvTime']); own_x.append(o['pos'][0]); own_y.append(o['pos'][1])
                elif o['type'] == 3:
                    msgs.append(o)
            if not msgs or not own_t:
                continue
            own_t = np.array(own_t); idx = np.clip(np.searchsorted(own_t, [m['rcvTime'] for m in msgs], 'right') - 1, 0, None)
            for m, k in zip(msgs, idx):
                code = attack.get(m['sender'], 0)
                R['receiver'].append(f'{subset}_{run}_{rcv}'); R['sender'].append(f'{subset}_{run}_{m["sender"]}')
                R['pseudo'].append(m['senderPseudo']); R['rcvTime'].append(m['rcvTime'])
                R['x'].append(m['pos'][0]); R['y'].append(m['pos'][1])
                R['spd'].append(float(np.hypot(*m['spd'][:2]))); R['acc'].append(float(np.hypot(*m['acl'][:2])))
                R['hed'].append(float(compass(m['hed'][0], m['hed'][1])))
                R['pos_noise'].append(float(np.hypot(*m['pos_noise'][:2]))); R['spd_noise'].append(float(np.hypot(*m['spd_noise'][:2])))
                R['rx'].append(own_x[k]); R['ry'].append(own_y[k])
                R['label'].append(int(code in EXT_SYBIL)); R['attack'].append(EXT_SYBIL.get(code, 'genuine' if code == 0 else f'A{code}'))
        if R['rcvTime']:
            frames.append(features(pd.DataFrame(R)))   # per run: keeps peak memory low
        print(f'    {basename(iname)}: {len(R["rcvTime"])} messages', flush=True)
    return {subset: pd.concat(frames, ignore_index=True)} if frames else {}


def read_nextgen(path, tmpdir, max_receivers, rng):
    scen = os.path.basename(path)[:-4].replace('_trafficCongestionSybil', '')
    out = {}
    for iname, inner in with_inner_zips(path, tmpdir):
        split = [s for s in ('Train', 'Validation', 'Test') if f'/{s}/' in iname.replace('\\', '/')][0]
        names = [n for n in inner.namelist() if n.endswith('.json')]
        if max_receivers and len(names) > max_receivers:
            names = list(rng.choice(names, max_receivers, replace=False))
        R = {c: [] for c in COLS}
        for n in names:
            rcv = basename(n)[:-5]
            for m in json.loads(inner.read(n)):
                s, r = m['sender'], m['receiver']
                sx, sy, _ = map(float, s['pos'].split(',')); rx, ry, _ = map(float, r['pos'].split(','))
                nx, ny, _ = map(float, s['pos_noise'].split(','))
                R['receiver'].append(f'{scen}_{split}_{rcv}'); R['sender'].append(f'{scen}_{split}_{m["sender_id"]}')
                R['pseudo'].append(m['sender_alias']); R['rcvTime'].append(m['rcvTime'] / 1e9)
                R['x'].append(sx); R['y'].append(sy); R['spd'].append(float(s['spd'])); R['acc'].append(abs(float(s['acl'])))
                R['hed'].append(float(s['hed']) % 360); R['pos_noise'].append(float(np.hypot(nx, ny)))
                R['spd_noise'].append(abs(float(s['spd_noise']))); R['rx'].append(rx); R['ry'].append(ry)
                R['label'].append(int(m['attacker'])); R['attack'].append('trafficCongestionSybil' if m['attacker'] else 'genuine')
        out[f'{scen}_{split}'] = features(pd.DataFrame(R))
        print(f'    {split}: {len(R["rcvTime"])} messages', flush=True)
    return out


# ------------------------------------------------------------------------------------------ features
def features(df):
    df = df.sort_values(['receiver', 'rcvTime']).reset_index(drop=True)
    df['dist_rcv'] = np.hypot(df.x - df.rx, df.y - df.ry)
    g = df.groupby(['receiver', 'pseudo'], sort=False)
    dt = g.rcvTime.diff(); dx, dy = g.x.diff(), g.y.diff()
    ps, ph = g.spd.shift(), np.radians(g.hed.shift())
    df['beacon_dt'] = dt
    df['pos_jump'] = np.hypot(dx, dy)
    df['pos_pred_err'] = np.hypot(dx - ps * np.sin(ph) * dt, dy - ps * np.cos(ph) * dt)
    df['spd_change_rate'] = (df.spd - ps).abs() / dt
    bearing = np.degrees(np.arctan2(dx, dy)) % 360
    err = np.abs((df.hed - bearing + 180) % 360 - 180)
    df['hed_motion_err'] = np.where(df.pos_jump > 1.0, err, np.nan)
    df['msg_idx'] = g.cumcount()
    df['pseudo_age'] = df.rcvTime - g.rcvTime.transform('min')
    df['is_new_pseudo'] = (df.msg_idx == 0).astype(np.int8)
    df['first_seen_dist'] = g.dist_rcv.transform('first')
    nxt = g.rcvTime.shift(-1).fillna(np.inf).values

    n = len(df); out = {k: np.zeros(n, np.float32) for k in
                        ['n_pseudo_1s', 'n_near5', 'n_near20', 'min_dist_other', 'new_pseudo_5s', 'new_pseudo_frac_5s', 'n_similar_spd_near']}
    T, X, Y, V, P, NEW = (df[c].values for c in ['rcvTime', 'x', 'y', 'spd', 'pseudo', 'is_new_pseudo'])
    starts = np.r_[0, np.flatnonzero(df.receiver.values[1:] != df.receiver.values[:-1]) + 1, n]
    for a0, a1 in zip(starts[:-1], starts[1:]):
        t = T[a0:a1]; lo1 = np.searchsorted(t, t - 1.0) + a0; lo5 = np.searchsorted(t, t - 5.0) + a0
        for i in range(a0, a1):
            a = lo1[i - a0]
            out['n_pseudo_1s'][i] = (nxt[a:i + 1] > T[i]).sum()       # distinct pseudonyms heard in last 1 s
            m = P[a:i + 1] != P[i]
            if m.any():
                d = np.hypot(X[a:i + 1][m] - X[i], Y[a:i + 1][m] - Y[i])
                out['min_dist_other'][i] = d.min(); out['n_near5'][i] = (d < 5).sum(); near = d < 20
                out['n_near20'][i] = near.sum(); out['n_similar_spd_near'][i] = (np.abs(V[a:i + 1][m][near] - V[i]) < 0.5).sum()
            else:
                out['min_dist_other'][i] = 1000
            b = lo5[i - a0]; k = NEW[b:i + 1].sum(); out['new_pseudo_5s'][i] = k
            out['new_pseudo_frac_5s'][i] = k / max(1, (nxt[b:i + 1] > T[i]).sum())
    for k, v in out.items():
        df[k] = v
    for c in ['beacon_dt', 'pos_jump', 'pos_pred_err', 'spd_change_rate', 'hed_motion_err']:
        df[c] = df[c].replace([np.inf, -np.inf], np.nan)
    df[FEATS] = df[FEATS].fillna(-1).astype(np.float32)
    return df[['receiver', 'sender', 'pseudo', 'rcvTime', 'label', 'attack'] + FEATS]


# ------------------------------------------------------------------------------------------ main
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument('--ext-dir', default=os.path.join(here, '..', 'VeReMi_Extension'))
    ap.add_argument('--ng-dir', default=os.path.join(here, '..', 'VeReMi_NextGen'))
    ap.add_argument('--out', default=os.path.join(here, '..', 'features'))
    ap.add_argument('--max-receivers', type=int, default=0)
    ap.add_argument('--test', action='store_true', help='only DataReplaySybil_1416 and InTAS_highway_2')
    ap.add_argument('--only', default='', help='comma-separated substrings of zip names to process')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); rng = np.random.default_rng(0)
    jobs = [(p, read_extension, 'ext') for p in sorted(glob.glob(os.path.join(a.ext_dir, '*Sybil_*.zip')))] + \
           [(p, read_nextgen, 'ng') for p in sorted(glob.glob(os.path.join(a.ng_dir, '*trafficCongestionSybil.zip')))]
    if a.test:
        jobs = [j for j in jobs if 'DataReplaySybil_1416' in j[0] or 'highway_2' in j[0]]
    if a.only:
        jobs = [j for j in jobs if any(s in j[0] for s in a.only.split(','))]
    print(f'{len(jobs)} archives to convert -> {os.path.abspath(a.out)}')
    man_path = os.path.join(a.out, 'manifest.csv')
    manifest = pd.read_csv(man_path).to_dict('records') if os.path.exists(man_path) else []
    tmpdir = tempfile.mkdtemp(dir=a.out)
    try:
        for path, reader, tag in jobs:
            t0 = time.time(); print(f'\n{os.path.basename(path)}', flush=True)
            for name, F in reader(path, tmpdir, a.max_receivers, rng).items():
                t1 = time.time(); fn = os.path.join(a.out, f'{tag}_{name}.pkl.gz')
                F.to_pickle(fn, compression='gzip')
                manifest = [m for m in manifest if m['file'] != os.path.basename(fn)]
                manifest.append(dict(file=os.path.basename(fn), dataset=tag, subset=name, messages=len(F),
                                     sybil=int(F.label.sum()), receivers=F.receiver.nunique(), senders=F.sender.nunique(),
                                     seconds=round(time.time() - t0, 1)))
                pd.DataFrame(manifest).to_csv(man_path, index=False)
                print(f'  -> {os.path.basename(fn)}: {len(F)} messages, {int(F.label.sum())} Sybil '
                      f'({F.label.mean()*100:.1f}%)', flush=True)
                del F
            print(f'  done in {time.time()-t0:.0f}s', flush=True)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    print('\n' + pd.DataFrame(manifest).to_string(index=False))


if __name__ == '__main__':
    main()
