"""
Shortcut-robustness experiment (E7). Does removing or neutralising the "no history = Sybil" shortcut
restore cross-dataset transfer, and what does it cost in-domain?

Variants
  all            all 21 features (reference)
  drop_age       without is_new_pseudo, msg_idx, pseudo_age
  drop_history   without all 9 pseudonym-history features
  mask25/mask50  history-masking augmentation: in TRAINING ONLY, 25% / 50% of genuine messages get their
                 history features replaced by first-message values (no previous message), so that missing
                 history no longer identifies a Sybil. Validation and test data are never modified.
  mixed          train on Extension + NextGen together (reference upper bound, not a transfer setting)

Directions: NG -> Ext, Ext -> NG, and in-domain Ext (0709 -> 1416) and NG (official split).
Usage: python shortcut.py --feat-dir ../features
"""
import argparse, os, sys, time
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import experiments as E

AGE = ['is_new_pseudo', 'msg_idx', 'pseudo_age']
MISSING = {'beacon_dt': -1, 'pos_jump': -1, 'pos_pred_err': -1, 'spd_change_rate': -1, 'hed_motion_err': -1,
           'msg_idx': 0, 'pseudo_age': 0, 'is_new_pseudo': 1}


def mask_history(D, frac, seed):
    """Copy of D where a random `frac` of GENUINE rows look like the first message of a pseudonym."""
    D = D.copy(); r = np.random.default_rng(seed + 1000 * E.SEED)
    idx = np.flatnonzero((D.label.values == 0) & (r.random(len(D)) < frac))
    for c, v in MISSING.items():
        D.iloc[idx, D.columns.get_loc(c)] = v
    D.iloc[idx, D.columns.get_loc('first_seen_dist')] = D.dist_rcv.values[idx]
    return D


def run(setting, variant, Tr, Va, Te, by, seed=0):
    feats = {'drop_age': [c for c in E.ALL if c not in AGE],
             'drop_history': [c for c in E.ALL if c not in E.HIST]}.get(variant, E.ALL)
    if variant.startswith('mask'):
        Tr = mask_history(Tr, int(variant[4:]) / 100, seed)
    E.fit_eval('E7', setting, 'HGB', variant, Tr[feats].values, Tr.label.values, Va[feats].values, Va.label.values,
               Te[feats].values, Te.label.values, by, seed=seed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--feat-dir', default='../features'); ap.add_argument('--out', default='results_q1')
    ap.add_argument('--ext-n', type=int, default=120000); ap.add_argument('--ng-train-n', type=int, default=150000)
    ap.add_argument('--ng-val-n', type=int, default=50000); ap.add_argument('--ng-test-n', type=int, default=200000)
    ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); E.SEED = a.seed
    ext, ng = E.load_all(a)
    itr, iva = E.inner_val(ext, 0); ExtTr, ExtVa = ext.iloc[itr].reset_index(drop=True), ext.iloc[iva].reset_index(drop=True)
    S = ext[ext.density == '0709'].reset_index(drop=True); T = ext[ext.density == '1416'].reset_index(drop=True)
    s_tr, s_va = E.inner_val(S, 0); STr, SVa = S.iloc[s_tr].reset_index(drop=True), S.iloc[s_va].reset_index(drop=True)
    variants = ['all', 'drop_age', 'drop_history', 'mask25', 'mask50']
    for v in variants:
        print(f'\n--- {v} ---', flush=True)
        run('NG train -> Ext', v, ng['Train'], ng['Validation'], ext, ext.attack.values)
        run('Ext -> NG test', v, ExtTr, ExtVa, ng['Test'], ng['Test'].scenario.values)
        run('in-domain Ext 0709 -> 1416', v, STr, SVa, T, T.attack.values)
        run('in-domain NG official', v, ng['Train'], ng['Validation'], ng['Test'], ng['Test'].scenario.values)
    # mixed-source reference: train on both, test on each held-out side
    print('\n--- mixed ---', flush=True)
    Mtr = pd.concat([STr, ng['Train']], ignore_index=True); Mva = pd.concat([SVa, ng['Validation']], ignore_index=True)
    run('mixed -> Ext 1416', 'mixed', Mtr, Mva, T, T.attack.values)
    run('mixed -> NG test', 'mixed', Mtr, Mva, ng['Test'], ng['Test'].scenario.values)

    R = pd.DataFrame(E.ROWS); R.to_csv(os.path.join(a.out, 'shortcut_results.csv'), index=False)
    cols = ['f1', 'prec', 'rec', 'fpr', 'auc', 'tpr_at_1fpr', 'fpr_at_val_thr1', 'tpr_at_val_thr1']
    rc = [c for c in R.columns if c.startswith('rec_')]
    print('\n' + (R.set_index(['setting', 'feats'])[cols] * 100).round(2).to_string())
    print('\n' + (R.set_index(['setting', 'feats'])[rc] * 100).round(1).dropna(axis=1, how='all').to_string())


if __name__ == '__main__':
    main()
