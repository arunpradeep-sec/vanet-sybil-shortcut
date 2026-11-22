import numpy as np, pandas as pd, json
from scipy import stats
from sklearn.metrics import roc_auc_score
B='/mnt/user-data/uploads/VANET Paper/sybil_pipeline/results_supp/seed'
def cat(f): return pd.concat([pd.read_csv(f'{B}{s}/{f}').assign(seed=s) for s in range(5)],ignore_index=True)
def pt(a,b,name):
    a,b=np.asarray(a),np.asarray(b); d=a-b; t,p=stats.ttest_rel(a,b); ci=stats.t.interval(0.95,len(d)-1,loc=d.mean(),scale=stats.sem(d))
    print(f'{name}: diff {d.mean()*100:.1f} pp, 95% CI [{ci[0]*100:.1f}, {ci[1]*100:.1f}], paired t p={p:.2g}')
Z=cat('A5_zoo.csv'); g=lambda m,s: Z[(Z.model==m)&(Z.setting==s)].sort_values('seed').mcc.values
pt(g('NB','E4b'),g('HGB','E4b'),'NB vs HGB, E4b MCC'); pt(g('HGB','E4b'),g('MLP','E4b'),'HGB vs MLP, E4b')
pt(g('HGB','E1'),g('RF','E1'),'HGB vs RF, E1'); pt(g('HGB','E1'),g('NB','E1'),'HGB vs NB, E1')
K=cat('A13_topk.csv'); k=lambda kk,s: K[(K.k==kk)&(K.setting==s)].sort_values('seed').mcc.values
pt(k(2,'E4b'),k(21,'E4b'),'top-2 vs all 21, E4b')
L=cat('A4_learning.csv'); l=lambda n: L[(L.setting=='E4b')&(L.n==n)].groupby('seed').mcc.mean().values
pt(l(500),l(100000),'500 vs 100k msgs, E4b')
R=pd.read_csv('/mnt/user-data/uploads/VANET Paper/sybil_pipeline/results_robust/robust_results.csv')
r=lambda st,v,m='mcc': R[(R.setting==st)&(R.variant==v)].sort_values('seed')[m].values
for st in ['NG -> Ext (all types)','Ext non-Grid -> Grid 0709','NG -> NG test','Ext non-Grid -> seen 0709']:
    pt(r(st,'A'),r(st,'B'),f'A vs B, {st}'); pt(r(st,'R'),r(st,'A'),f'R vs A, {st}'); pt(r(st,'F'),r(st,'B'),f'F vs B, {st}')
pt(r('Ext -> NG test','F'),r('Ext -> NG test','B'),'F vs B, E4a')
# bootstrap CIs on AUC / MCC for main settings, and DeLong-type comparison via paired bootstrap HGB vs NB AUC on E4b
rng=np.random.default_rng(0); rows=[]
for s in range(5):
    P=np.load(f'{B}{s}/preds_main.npz')
    for st in ['E1','E2','E3','E4a','E4b']:
        y,p=P[f'{st}_y'],P[f'{st}_p']; n=len(y); idx=rng.integers(0,n,(200,n)) if n<300000 else rng.integers(0,n,(100,n))
        aucs=[roc_auc_score(y[i],p[i]) for i in idx[:100]]; rows.append(dict(seed=s,setting=st,lo=np.percentile(aucs,2.5),hi=np.percentile(aucs,97.5),auc=roc_auc_score(y,p)))
C=pd.DataFrame(rows); C['half']=(C.hi-C.lo)/2; print((C.groupby('setting')[['auc','half']].mean()*100).round(3))
d=[]
for s in range(5):
    P=np.load(f'{B}{s}/preds_zoo.npz'); y=P['E4b_y']; a,b=P['E4b_HGB'],P['E4b_NB']; n=len(y); bs=[]
    for _ in range(200):
        i=rng.integers(0,n,n); bs.append(roc_auc_score(y[i],a[i])-roc_auc_score(y[i],b[i]))
    d.append(dict(seed=s,diff=roc_auc_score(y,a)-roc_auc_score(y,b),lo=np.percentile(bs,2.5),hi=np.percentile(bs,97.5),aucH=roc_auc_score(y,a),aucN=roc_auc_score(y,b)))
print(pd.DataFrame(d).round(4))
