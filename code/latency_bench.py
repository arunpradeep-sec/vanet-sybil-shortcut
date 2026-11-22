"""
On-board latency benchmark for the receiver-side Sybil detector. Runs on a Raspberry Pi (or any machine)
with only numpy and scikit-learn installed.

It replays a recorded stream of received beacons (stream.npz, made by latency_prep.py on the Mac), computes
the 21 features ONLINE, one message at a time, exactly as an on-board unit would, and times:
  1. feature extraction per message (all messages of the stream),
  2. model inference per message, batch size 1 (HGB and RF, a random subset of messages),
  3. batch inference throughput (1,000 messages per call),
  4. end-to-end per message = features + HGB.
Everything is timed on ONE CPU core. It also checks that the online features equal the offline features used
in the paper, and records model size, peak memory and CPU temperature/throttling.

Usage (inside the latency_kit folder):
  python3 latency_bench.py                # full run, ~10-20 min on a Raspberry Pi 4B
  python3 latency_bench.py --quick        # 2-minute check
Output: latency_<hostname>.json and a printed summary.
"""
import argparse, json, math, os, pickle, platform, resource, socket, subprocess, sys, time
from collections import deque
import numpy as np

FEATS = ['spd', 'acc', 'pos_noise', 'spd_noise', 'dist_rcv', 'beacon_dt', 'pos_jump', 'pos_pred_err',
         'spd_change_rate', 'hed_motion_err', 'msg_idx', 'pseudo_age', 'is_new_pseudo', 'first_seen_dist',
         'n_pseudo_1s', 'n_near5', 'n_near20', 'min_dist_other', 'new_pseudo_5s', 'new_pseudo_frac_5s',
         'n_similar_spd_near']


# ------------------------------------------------------------------------------ online feature extractor
class Receiver:
    """State kept by one receiving vehicle. update() takes one received beacon and returns its 21 features."""

    def __init__(self):
        self.ps = {}                                   # pseudonym -> [t, x, y, spd, hed, count, first_t, first_dist]
        self.w1, self.c1 = deque(), {}                 # messages of the last 1 s, pseudonym counts in it
        self.w5, self.c5, self.new5 = deque(), {}, 0   # messages of the last 5 s, pseudonym counts, new-pseudonym count

    @staticmethod
    def _evict(w, c, tmin):
        removed_new = 0
        while w and w[0][0] < tmin:
            e = w.popleft(); k = c[e[1]] - 1
            if k:
                c[e[1]] = k
            else:
                del c[e[1]]
            removed_new += e[5]
        return removed_new

    def update(self, t, p, x, y, spd, acc, hed, pos_noise, spd_noise, rx, ry):
        dist = math.hypot(x - rx, y - ry)
        s = self.ps.get(p)
        if s is None:
            is_new, idx, age, first_dist = 1, 0, 0.0, dist
            bdt = jump = pred = rate = herr = -1.0
            self.ps[p] = [t, x, y, spd, hed, 1, t, dist]
        else:
            pt, px, py, pspd, phed, cnt, ft, first_dist = s
            is_new, idx, age = 0, cnt, t - ft
            dt, dx, dy = t - pt, x - px, y - py
            jump = math.hypot(dx, dy)
            if dt > 0:
                bdt = dt; ph = math.radians(phed)
                pred = math.hypot(dx - pspd * math.sin(ph) * dt, dy - pspd * math.cos(ph) * dt)
                rate = abs(spd - pspd) / dt
            else:                                      # offline: division by zero -> missing -> -1
                bdt = dt; pred = jump; rate = -1.0
            if jump > 1.0:
                bearing = math.degrees(math.atan2(dx, dy)) % 360
                herr = abs((hed - bearing + 180) % 360 - 180)
            else:
                herr = -1.0
            s[0], s[1], s[2], s[3], s[4], s[5] = t, x, y, spd, hed, cnt + 1
        # sliding windows
        e = (t, p, x, y, spd, is_new)
        for w, c in ((self.w1, self.c1), (self.w5, self.c5)):
            w.append(e); c[p] = c.get(p, 0) + 1
        self._evict(self.w1, self.c1, t - 1.0)
        self.new5 += is_new
        self.new5 -= self._evict(self.w5, self.c5, t - 5.0)
        # neighbourhood over the last 1 s
        mind, n5, n20, nsim, others = 1000.0, 0, 0, 0, False
        for (tj, pj, xj, yj, vj, _) in self.w1:
            if pj == p:
                continue
            others = True
            d = math.hypot(xj - x, yj - y)
            if d < mind:
                mind = d
            if d < 20:
                n20 += 1
                if d < 5:
                    n5 += 1
                if abs(vj - spd) < 0.5:
                    nsim += 1
        if not others:
            mind = 1000.0
        return (spd, acc, pos_noise, spd_noise, dist, bdt, jump, pred, rate, herr, idx, age, is_new, first_dist,
                len(self.c1), n5, n20, mind, self.new5, self.new5 / max(1, len(self.c5)), nsim)


def replay(S, limit=None):
    """Run the extractor over the stream; return features (N x 21) and per-message times in ns."""
    n = len(S['t']) if limit is None else min(limit, len(S['t']))
    cols = [S[k].tolist() for k in ('rec', 'pseudo', 't', 'x', 'y', 'spd', 'acc', 'hed', 'pos_noise', 'spd_noise', 'rx', 'ry')]
    out = np.empty((n, len(FEATS)), np.float64); ns = np.empty(n, np.int64)
    cur, R = None, None; clock = time.perf_counter_ns
    for i in range(n):
        r = cols[0][i]
        if r != cur:
            cur, R = r, Receiver()
        a = clock()
        f = R.update(cols[2][i], cols[1][i], cols[3][i], cols[4][i], cols[5][i], cols[6][i], cols[7][i],
                     cols[8][i], cols[9][i], cols[10][i], cols[11][i])
        ns[i] = clock() - a
        out[i] = f
    return out, ns


class LeanHGB:
    """The fitted HGB trees as flat NumPy arrays: all trees are walked together, one level per step.
    Same output as predict_proba (features have no missing values), without scikit-learn's per-call checks."""

    def __init__(self, hgb):
        feat, thr, left, right, leaf, val, roots, off = [], [], [], [], [], [], [], 0
        for (tree,) in hgb._predictors:
            nd = tree.nodes; roots.append(off)
            feat.append(nd['feature_idx']); thr.append(nd['num_threshold'])
            left.append(nd['left'] + off); right.append(nd['right'] + off)
            leaf.append(nd['is_leaf'].astype(bool)); val.append(nd['value']); off += len(nd)
        cat = lambda v: np.concatenate(v)
        self.feat, self.thr, self.left, self.right = cat(feat).astype(np.intp), cat(thr), cat(left).astype(np.intp), cat(right).astype(np.intp)
        self.leaf, self.val, self.roots = cat(leaf), cat(val), np.array(roots, np.intp)
        self.base = float(np.ravel(hgb._baseline_prediction)[0])
        self.depth = int(max(t[0].nodes['depth'].max() for t in hgb._predictors))
        self.n_trees, self.n_nodes = len(roots), off

    def predict_one(self, x):
        idx = self.roots
        for _ in range(self.depth):
            go = x[self.feat[idx]] <= self.thr[idx]
            nxt = np.where(go, self.left[idx], self.right[idx])
            idx = np.where(self.leaf[idx], idx, nxt)
        return 1.0 / (1.0 + math.exp(-(self.base + self.val[idx].sum())))


# ------------------------------------------------------------------------------ helpers
def stats_us(ns):
    us = np.asarray(ns) / 1000.0
    return {k: round(float(v), 2) for k, v in
            dict(mean=us.mean(), median=np.median(us), p95=np.percentile(us, 95), p99=np.percentile(us, 99),
                 max=us.max()).items()}


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return ''


def temp_c():
    try:
        return round(int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1000, 1)
    except Exception:
        return None


def platform_info():
    cpu = sh("grep -m1 -E 'Model|model name' /proc/cpuinfo | cut -d: -f2") or sh('sysctl -n machdep.cpu.brand_string')
    board = sh('cat /proc/device-tree/model 2>/dev/null | tr -d "\\0"')
    import sklearn
    return dict(host=socket.gethostname(), board=board, cpu=cpu, machine=platform.machine(), cores=os.cpu_count(),
                python=platform.python_version(), numpy=np.__version__, sklearn=sklearn.__version__,
                os=platform.platform())


def time_single(predict, X, idx):
    ns = np.empty(len(idx), np.int64); clock = time.perf_counter_ns
    for j, i in enumerate(idx):
        row = X[i:i + 1]; a = clock(); predict(row); ns[j] = clock() - a
    return ns


# ------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kit', default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument('--single', type=int, default=2000, help='messages timed with batch-1 inference per model')
    ap.add_argument('--batch-rows', type=int, default=20000)
    ap.add_argument('--quick', action='store_true')
    a = ap.parse_args()
    from threadpoolctl import threadpool_limits
    from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
    info = platform_info(); res = dict(platform=info, temp_start_c=temp_c(), throttled_start=sh('vcgencmd get_throttled'))
    print(json.dumps(info, indent=1), flush=True)
    S = dict(np.load(os.path.join(a.kit, 'stream.npz'))); Tn = np.load(os.path.join(a.kit, 'train.npz'))
    limit = 30000 if a.quick else None
    n_single = 300 if a.quick else a.single
    Xtr, ytr = Tn['X'], Tn['y']
    if a.quick:
        Xtr, ytr = Xtr[:40000], ytr[:40000]

    # 1. models (training is not timed as on-board cost)
    print(f'\nTraining HGB and RF on {len(ytr)} Extension messages ...', flush=True)
    t0 = time.time()
    hgb = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1, random_state=0).fit(Xtr, ytr)
    t1 = time.time()
    rf = RandomForestClassifier(n_estimators=100, min_samples_leaf=2, max_samples=0.3, n_jobs=-1, random_state=0).fit(Xtr, ytr)
    rf.set_params(n_jobs=1)
    t2 = time.time()
    res['train_seconds'] = dict(HGB=round(t1 - t0, 1), RF=round(t2 - t1, 1))
    res['model_bytes'] = dict(HGB=len(pickle.dumps(hgb)), RF=len(pickle.dumps(rf)))
    print(f'  done: HGB {t1-t0:.0f}s, RF {t2-t1:.0f}s; sizes HGB {res["model_bytes"]["HGB"]/1e6:.2f} MB, '
          f'RF {res["model_bytes"]["RF"]/1e6:.1f} MB', flush=True)

    with threadpool_limits(1):
        # 2. online features
        print(f'\nReplaying {limit or len(S["t"])} received beacons through the online extractor ...', flush=True)
        replay(S, 2000)                                            # warm-up
        F, fns = replay(S, limit)
        res['features_us'] = stats_us(fns); res['messages'] = len(fns)
        off = S['feats'][:len(F)].astype(np.float64)
        close = np.isclose(F, off, rtol=1e-4, atol=1e-3)
        res['feature_match'] = dict(all_features_equal_pct=round(float(close.all(1).mean() * 100), 3),
                                    per_feature_mismatch_pct={f: round(float((~close[:, j]).mean() * 100), 3)
                                                              for j, f in enumerate(FEATS) if (~close[:, j]).any()})
        print(f'  feature extraction: {res["features_us"]} us; online = offline for '
              f'{res["feature_match"]["all_features_equal_pct"]}% of messages', flush=True)

        # 3. single-message inference
        rng = np.random.default_rng(0); idx = rng.choice(len(F), min(n_single, len(F)), replace=False)
        Xs = F.astype(np.float32)
        res['single_us'] = {}
        for name, m in (('HGB', hgb), ('RF', rf)):
            time_single(m.predict_proba, Xs, idx[:50])             # warm-up
            ns = time_single(m.predict_proba, Xs, idx)
            res['single_us'][name] = stats_us(ns)
            print(f'  {name} batch-1 inference: {res["single_us"][name]} us', flush=True)
            if name == 'HGB':
                e2e = fns[idx] + ns

        lean = LeanHGB(hgb)
        chk = np.array([lean.predict_one(Xs[i]) for i in idx[:500]])
        res['lean_HGB_max_abs_diff'] = float(np.abs(chk - hgb.predict_proba(Xs[idx[:500]])[:, 1]).max())
        res['lean_HGB'] = dict(trees=lean.n_trees, nodes=lean.n_nodes, max_depth=lean.depth)
        time_single(lambda r: lean.predict_one(r[0]), Xs, idx[:50])
        ns_lean = time_single(lambda r: lean.predict_one(r[0]), Xs, idx)
        res['single_us']['HGB_lean'] = stats_us(ns_lean)
        e2e_lean = fns[idx] + ns_lean
        print(f'  lean HGB batch-1 inference ({lean.n_trees} trees): {res["single_us"]["HGB_lean"]} us, '
              f'max difference to scikit-learn {res["lean_HGB_max_abs_diff"]:.1e}', flush=True)

        # 4. batch throughput
        B = Xs[:min(a.batch_rows, len(Xs))]; res['batch_msgs_per_s'] = {}
        for name, m in (('HGB', hgb), ('RF', rf)):
            a0 = time.perf_counter()
            for i in range(0, len(B), 1000):
                m.predict_proba(B[i:i + 1000])
            res['batch_msgs_per_s'][name] = round(len(B) / (time.perf_counter() - a0))
            print(f'  {name} batch-1000 throughput: {res["batch_msgs_per_s"][name]} messages/s', flush=True)

    # 5. end-to-end and load
    res['end_to_end_HGB_us'] = stats_us(e2e)
    res['end_to_end_HGB_lean_us'] = stats_us(e2e_lean)
    res['capacity_msgs_per_s_one_core_lean'] = round(1e6 / res['end_to_end_HGB_lean_us']['mean'])
    res['capacity_msgs_per_s_one_core'] = round(1e6 / res['end_to_end_HGB_us']['mean'])
    t, rec = S['t'][:len(F)], S['rec'][:len(F)]
    sec = np.floor(t).astype(np.int64); key = rec.astype(np.int64) * 10**7 + sec
    _, cnt = np.unique(key, return_counts=True)
    res['observed_load_msgs_per_s'] = dict(median=int(np.median(cnt)), p99=int(np.percentile(cnt, 99)), max=int(cnt.max()))
    res['mean_neighbour_msgs_in_1s'] = round(float(F[:, FEATS.index('n_pseudo_1s')].mean()), 1)
    res['cpu_utilisation_at_peak_pct'] = round(res['observed_load_msgs_per_s']['max'] * res['end_to_end_HGB_us']['mean'] / 1e4, 2)
    p = hgb.predict(Xs); y = S['label'][:len(F)]
    tp = int(((p == 1) & (y == 1)).sum()); res['stream_F1_sanity'] = round(200 * tp / max(1, int(p.sum() + y.sum())), 2)
    res['peak_rss_mb'] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 if sys.platform != 'darwin' else 1024**2), 1)
    res['temp_end_c'] = temp_c(); res['throttled_end'] = sh('vcgencmd get_throttled')

    print('\n================ SUMMARY ================')
    print(f'{info["board"] or info["cpu"]} | Python {info["python"]} | scikit-learn {info["sklearn"]} | one core')
    print(f'{"stage":32s}{"mean":>9s}{"median":>9s}{"p99":>9s}{"max":>10s}   (microseconds)')
    for lab, s_ in [('feature extraction', res['features_us']), ('HGB inference (batch 1)', res['single_us']['HGB']),
                    ('lean HGB inference (batch 1)', res['single_us']['HGB_lean']),
                    ('RF inference (batch 1)', res['single_us']['RF']), ('end-to-end, features + HGB', res['end_to_end_HGB_us']),
                    ('end-to-end, features + lean HGB', res['end_to_end_HGB_lean_us'])]:
        print(f'{lab:32s}{s_["mean"]:9.1f}{s_["median"]:9.1f}{s_["p99"]:9.1f}{s_["max"]:10.1f}')
    print(f'capacity on one core: {res["capacity_msgs_per_s_one_core"]} messages/s; observed load per receiver: '
          f'median {res["observed_load_msgs_per_s"]["median"]}, max {res["observed_load_msgs_per_s"]["max"]} messages/s '
          f'-> {res["cpu_utilisation_at_peak_pct"]}% of one core at peak')
    print(f'with lean HGB: capacity {res["capacity_msgs_per_s_one_core_lean"]} messages/s -> '
          f'{round(res["observed_load_msgs_per_s"]["max"] * res["end_to_end_HGB_lean_us"]["mean"] / 1e4, 2)}% of one core at peak')
    print(f'batch-1000 throughput: HGB {res["batch_msgs_per_s"]["HGB"]}, RF {res["batch_msgs_per_s"]["RF"]} messages/s')
    print(f'model size: HGB {res["model_bytes"]["HGB"]/1e6:.2f} MB, RF {res["model_bytes"]["RF"]/1e6:.1f} MB; '
          f'peak memory {res["peak_rss_mb"]} MB; CPU {res["temp_start_c"]} -> {res["temp_end_c"]} C, '
          f'throttled: {res["throttled_end"] or "n/a"}')
    print(f'online features equal offline features for {res["feature_match"]["all_features_equal_pct"]}% of messages')
    out = os.path.join(a.kit, f'latency_{info["host"]}{"_quick" if a.quick else ""}.json')
    json.dump(res, open(out, 'w'), indent=1)
    print(f'\nSaved {out}')


if __name__ == '__main__':
    main()
