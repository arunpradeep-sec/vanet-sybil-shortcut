"""
E8: leave-one-Sybil-type-out (LOTO) on VeReMi Extension.

For each held-out Sybil type H and each density pair (A -> B, A != B):
  seen      train on all 4 types at density A           -> test H at density B   (reference: H was seen)
  unseen    train on the other 3 types at density A     -> test H at density B   (H never seen)
  unseen+NG train on the other 3 types at A + NextGen Train -> test H at B       (does extra diversity help?)
Training and test always come from different simulations (different densities), which also avoids the
shared genuine traffic of the two DoS Sybil subsets. Thresholds come from a sender-grouped validation split
of the training data. The 'first message from a pseudonym' rule is reported for every test set.
Usage: python loto.py --feat-dir ../features
"""
import argparse, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import experiments as E

TYPES = ['GridSybil', 'DataReplaySybil', 'DoSRandomSybil', 'DoSDisruptiveSybil']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--feat-dir', default='../features'); ap.add_argument('--out', default='results_q1')
    ap.add_argument('--ext-n', type=int, default=120000); ap.add_argument('--ng-train-n', type=int, default=150000)
    ap.add_argument('--ng-val-n', type=int, default=50000); ap.add_argument('--ng-test-n', type=int, default=20000)
    ap.add_argument('--models', default='HGB,RF')
    ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); E.SEED = a.seed
    ext, ng = E.load_all(a)
    ext['type'] = ext.subset.str.replace('ext_', '').str[:-5]
    for H in TYPES:
        for A, B in [('0709', '1416'), ('1416', '0709')]:
            Te = ext[(ext.type == H) & (ext.density == B)].reset_index(drop=True)
            print(f'\n--- held out {H}, train {A} -> test {B} ---', flush=True)
            for mode in ['seen', 'unseen', 'unseen+NG']:
                Tr = ext[(ext.density == A) & ((ext.type != H) | (mode == 'seen'))].reset_index(drop=True)
                itr, iva = E.inner_val(Tr, 0)
                Xtr, Xva = Tr.iloc[itr], Tr.iloc[iva]
                if mode == 'unseen+NG':
                    Xtr = pd.concat([Xtr, ng['Train']], ignore_index=True); Xva = pd.concat([Xva, ng['Validation']], ignore_index=True)
                for m in a.models.split(','):
                    E.fit_eval('E8', f'{H} {A}->{B}', m, mode, Xtr[E.ALL].values, Xtr.label.values,
                               Xva[E.ALL].values, Xva.label.values, Te[E.ALL].values, Te.label.values)
            E.rule_eval('E8', f'{H} {A}->{B}', Te)
    R = pd.DataFrame(E.ROWS); R.to_csv(os.path.join(a.out, 'loto_results.csv'), index=False)
    R['held_out'] = R.setting.str.split(' ').str[0]
    cols = ['f1', 'rec', 'fpr', 'auc', 'tpr_at_1fpr', 'fpr_at_val_thr1', 'tpr_at_val_thr1']
    S = (R.groupby(['held_out', 'model', 'feats'], sort=False)[cols].mean() * 100).round(2)
    S.to_csv(os.path.join(a.out, 'loto_summary.csv')); print('\n' + S.to_string())
    print('\nMean over held-out types:\n' + (R.groupby(['model', 'feats'], sort=False)[cols].mean() * 100).round(2).to_string())


if __name__ == '__main__':
    main()
