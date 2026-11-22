"""
Prepare the latency kit for the Raspberry Pi (run on the Mac, in the venv, from sybil_pipeline).

Writes ../latency_kit/ with:
  stream.npz        raw received beacons of a few receivers from one dense VeReMi Extension run, in arrival
                    order, plus the offline features of convert_veremi.py for a correctness check
  train.npz         21-feature training sample from the other Extension receivers
  latency_bench.py  the benchmark itself (needs only numpy and scikit-learn)

Usage:
  python latency_prep.py                           # densest archive (GridSybil_0709), first run, up to 200,000 beacons
  python latency_prep.py --zip DoSRandomSybil_1416 --max-msgs 100000
"""
import argparse, glob, itertools, os, shutil, sys, tempfile
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_veremi as cv

here = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('--ext-dir', default=os.path.join(here, '..', 'VeReMi_Extension'))
ap.add_argument('--feat-dir', default=os.path.join(here, '..', 'features'))
ap.add_argument('--out', default=os.path.join(here, '..', 'latency_kit'))
ap.add_argument('--zip', default='GridSybil_0709')
ap.add_argument('--receivers', type=int, default=40)
ap.add_argument('--max-msgs', type=int, default=200000)
ap.add_argument('--train-per-file', type=int, default=25000)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)

# ---- 1. raw stream from the first simulation run of one archive
path = [p for p in sorted(glob.glob(os.path.join(a.ext_dir, '*Sybil_*.zip'))) if a.zip in os.path.basename(p)][0]
print(f'Reading {a.receivers} receivers of the first run in {os.path.basename(path)} ...', flush=True)
orig_feat, orig_inner = cv.features, cv.with_inner_zips
cv.features = lambda df: df
cv.with_inner_zips = lambda p, t: itertools.islice(orig_inner(p, t), 1)
tmp = tempfile.mkdtemp(dir=a.out)
try:
    raw = list(cv.read_extension(path, tmp, a.receivers, np.random.default_rng(0)).values())[0]
finally:
    cv.features, cv.with_inner_zips = orig_feat, orig_inner
    shutil.rmtree(tmp, ignore_errors=True)
raw = raw.sort_values(['receiver', 'rcvTime']).reset_index(drop=True)
sizes = raw.groupby('receiver', sort=False).size()
keep = sizes.index[np.cumsum(sizes.values) <= a.max_msgs]
if len(keep) == 0:
    keep = sizes.index[:1]
raw = raw[raw.receiver.isin(keep)].reset_index(drop=True)
off = orig_feat(raw.copy())
assert (off.rcvTime.values == raw.rcvTime.values).all() and (off.receiver.values == raw.receiver.values).all()
np.savez_compressed(os.path.join(a.out, 'stream.npz'),
                    rec=pd.factorize(raw.receiver)[0].astype(np.int32), pseudo=pd.factorize(raw.pseudo)[0].astype(np.int64),
                    t=raw.rcvTime.values.astype(np.float64),
                    **{c: raw[c].values.astype(np.float64) for c in ['x', 'y', 'spd', 'acc', 'hed', 'pos_noise', 'spd_noise', 'rx', 'ry']},
                    label=raw.label.values.astype(np.int8), feats=off[cv.FEATS].values.astype(np.float32))
print(f'  stream: {len(raw)} beacons from {raw.receiver.nunique()} receivers, {raw.label.mean()*100:.1f}% Sybil', flush=True)

# ---- 2. training sample from the other receivers
rng = np.random.default_rng(1); X, y = [], []
stream_rcv = set(raw.receiver)
for p in sorted(glob.glob(os.path.join(a.feat_dir, 'ext_*.pkl.gz'))):
    d = pd.read_pickle(p)
    d = d[~d.receiver.isin(stream_rcv)]
    d = d.iloc[rng.choice(len(d), min(a.train_per_file, len(d)), replace=False)]
    X.append(d[cv.FEATS].values.astype(np.float32)); y.append(d.label.values.astype(np.int8))
    print(f'  training sample from {os.path.basename(p)}', flush=True)
np.savez_compressed(os.path.join(a.out, 'train.npz'), X=np.concatenate(X), y=np.concatenate(y))
shutil.copy(os.path.join(here, 'latency_bench.py'), a.out)
print(f'\nKit ready in {os.path.abspath(a.out)}:')
for f in sorted(os.listdir(a.out)):
    print(f'  {f:20s} {os.path.getsize(os.path.join(a.out, f))/1e6:7.2f} MB')
