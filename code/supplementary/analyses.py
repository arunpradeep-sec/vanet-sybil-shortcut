import numpy as np, pandas as pd, json, time, sys, warnings
warnings.filterwarnings('ignore')
from sklearn.ensemble import HistGradientBoostingClassifier as HGB, RandomForestClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import *
from scipy.stats import ks_2samp, wasserstein_distance, spearmanr
sys.path.insert(0,'/home/claude/scripts')
from experiments import KIN,HIST,NEIGH,ALL
O='/home/claude/an/out/'; import os; os.makedirs(O,exist_ok=True)
S=pd.read_pickle('/home/claude/an/sample.pkl'); B=pd.read_pickle('/home/claude/an/blocks.pkl')
S['ds']=np.where(S.subset.str.startswith('ext'),'ext','ng'); S['split']=np.where(S.ds=='ext',S.subset.str[-4:],S.subset.str.split('_').str[-1])
S['g']=S.sender.astype('category').cat.codes
ext=S[S.ds=='ext'].reset_index(drop=True); E0=ext[ext.split=='0709'].reset_index(drop=True); E1=ext[ext.split=='1416'].reset_index(drop=True)
NT,NV,NX=[S[(S.ds=='ng')&(S.split==k)].reset_index(drop=True) for k in ['Train','Validation','Test']]
rng=np.random.default_rng(0)
def gsplit(D,frac=0.2,seed=0):
    return next(GroupShuffleSplit(1,test_size=frac,random_state=seed).split(D,groups=D.g))
def f1thr(y,p):
    pr,rc,th=precision_recall_curve(y,p); f=2*pr*rc/np.maximum(pr+rc,1e-12); return float(th[np.argmax(f[:-1])])
def mets(y,p,t):
    yh=p>=t; fp,tp=((yh)&(y==0)).sum(),((yh)&(y==1)).sum(); fpr,tpr,_=roc_curve(y,p)
    return dict(f1=f1_score(y,yh),mcc=matthews_corrcoef(y,yh),auc=roc_auc_score(y,p),ap=average_precision_score(y,p),
      tpr1=float(np.interp(0.01,fpr,tpr)),prec=precision_score(y,yh,zero_division=0),rec=recall_score(y,yh),fpr=fp/max((y==0).sum(),1),brier=brier_score_loss(y,p))
def hgb(it=300,lr=0.1,seed=0): return HGB(max_iter=it,learning_rate=lr,random_state=seed)
# settings: (name, train df, val df, test df)
tr0,va0=gsplit(E0); E0tr,E0va=E0.iloc[tr0],E0.iloc[va0]
a,b=gsplit(E0tr.reset_index(drop=True)); 
E0trr=E0tr.reset_index(drop=True); E0trA,E0trV=E0trr.iloc[a],E0trr.iloc[b]
extr=ext.reset_index(drop=True); a2,b2=gsplit(extr); EXtr,EXva=extr.iloc[a2],extr.iloc[b2]
SET={'E1':(E0trA,E0trV,E0va),'E2':(E0trA,E0trV,E1),'E3':(NT,NV,NX),'E4a':(EXtr,EXva,NX),'E4b':(NT,NV,ext)}
R={}
def run(name,model=None,feats=ALL,ntr=None,seed=0):
    tr,va,te=SET[name]
    if ntr and ntr<len(tr): tr=tr.iloc[np.random.default_rng(seed).choice(len(tr),ntr,replace=False)]
    m=(model or hgb(seed=seed)).fit(tr[feats].values,tr.label.values)
    pv=m.predict_proba(va[feats].values)[:,1]; pt=m.predict_proba(te[feats].values)[:,1]
    return m,pv,pt,f1thr(va.label.values,pv)
T0=time.time()
# ---------- A1 single-feature AUC + shift
rows=[]
for f in ALL:
    r=dict(feature=f,group='KIN' if f in KIN else 'HIST' if f in HIST else 'NEIGH')
    for ds,D in [('ext',ext),('ng',pd.concat([NT,NV,NX]))]:
        r[f'auc_{ds}']=roc_auc_score(D.label,D[f])
    ng=pd.concat([NT,NV,NX])
    for lab,nm in [(0,'gen'),(1,'syb')]:
        x=ext[ext.label==lab][f].values; z=ng[ng.label==lab][f].values
        r[f'ks_{nm}']=ks_2samp(x,z).statistic
    rows.append(r)
pd.DataFrame(rows).to_csv(O+'A1_feature_auc_shift.csv',index=False); print('A1',time.time()-T0,flush=True)
# violin sample
vs=[]
for ds,D in [('Extension',ext),('NextGen',pd.concat([NT,NV,NX]))]:
    for lab in [0,1]:
        d=D[D.label==lab].sample(4000,random_state=0)[ALL].copy(); d['ds']=ds; d['label']=lab; vs.append(d)
pd.concat(vs).to_csv(O+'A1_violin_sample.csv.gz',index=False)
# ---------- A2 domain classifier
ng=pd.concat([NT,NV,NX]); rows=[]
for lab,nm in [(0,'genuine'),(1,'Sybil'),(None,'all')]:
    X1=ext if lab is None else ext[ext.label==lab]; X2=ng if lab is None else ng[ng.label==lab]
    n=min(len(X1),len(X2),60000); D=pd.concat([X1.sample(n,random_state=0).assign(dom=0),X2.sample(n,random_state=0).assign(dom=1)]).reset_index(drop=True)
    for gname,feats in [('all',ALL),('KIN',KIN),('HIST',HIST),('NEIGH',NEIGH)]:
        a,b=gsplit(D,0.3); m=hgb().fit(D.iloc[a][feats].values,D.dom.values[a]); p=m.predict_proba(D.iloc[b][feats].values)[:,1]
        rows.append(dict(subset=nm,features=gname,auc=roc_auc_score(D.dom.values[b],p)))
pd.DataFrame(rows).to_csv(O+'A2_domain_clf.csv',index=False); print('A2',time.time()-T0,flush=True)
# ---------- A3 correlations
for ds,D in [('ext',ext),('ng',ng)]:
    pd.DataFrame(spearmanr(D[ALL].sample(50000,random_state=0).values).statistic,index=ALL,columns=ALL).to_csv(O+f'A3_spearman_{ds}.csv')
# ---------- A12 PCA
from sklearn.decomposition import PCA
P=pd.concat([ext.sample(6000,random_state=1).assign(ds='Extension'),ng.sample(6000,random_state=1).assign(ds='NextGen')])
Z=StandardScaler().fit_transform(np.sign(P[ALL].values)*np.log1p(np.abs(P[ALL].values))); pca=PCA(2).fit(Z); c=pca.transform(Z)
pd.DataFrame(dict(pc1=c[:,0],pc2=c[:,1],ds=P.ds.values,label=P.label.values)).to_csv(O+'A12_pca.csv',index=False)
json.dump(dict(evr=pca.explained_variance_ratio_.tolist()),open(O+'A12_pca.json','w'))
# ---------- main predictions for curves
preds={}
for k in SET:
    m,pv,pt,t=run(k); y=SET[k][2].label.values; preds[k]=(y,pt,t,m)
    R[k]=mets(y,pt,t); print(k,R[k],flush=True)
json.dump(R,open(O+'main_metrics.json','w'),indent=1)
# A7 threshold sweep, A8 calibration, A9 PR, A10 confusion, ROC
th=np.linspace(0.01,0.99,99); sw=[]; cal=[]; prc=[]; cm={}
for k,(y,p,t,m) in preds.items():
    for x in th:
        yh=p>=x; sw.append(dict(setting=k,thr=x,f1=f1_score(y,yh,zero_division=0),mcc=matthews_corrcoef(y,yh),prec=precision_score(y,yh,zero_division=0),rec=recall_score(y,yh),fpr=((yh)&(y==0)).sum()/(y==0).sum()))
    bins=np.linspace(0,1,11); idx=np.clip(np.digitize(p,bins)-1,0,9)
    for i in range(10):
        s=idx==i
        if s.sum()>20: cal.append(dict(setting=k,bin=i,pmean=p[s].mean(),frac=y[s].mean(),n=int(s.sum())))
    pr,rc,_=precision_recall_curve(y,p); sel=np.unique(np.linspace(0,len(pr)-1,300).astype(int))
    for i in sel: prc.append(dict(setting=k,prec=pr[i],rec=rc[i]))
    cm[k]=confusion_matrix(y,p>=t).tolist()+[[t]]
pd.DataFrame(sw).to_csv(O+'A7_threshold.csv',index=False); pd.DataFrame(cal).to_csv(O+'A8_calibration.csv',index=False)
pd.DataFrame(prc).to_csv(O+'A9_pr.csv',index=False); json.dump(cm,open(O+'A10_confusion.json','w'))
print('curves',time.time()-T0,flush=True)
# ---------- A16 feature-noise robustness
rows=[]
for k in ['E1','E3']:
    y,p,t,m=preds[k]; te=SET[k][2]
    for s in [0,0.01,0.02,0.05,0.1,0.2]:
        X=te[ALL].values.astype(float); X=X*(1+np.random.default_rng(1).normal(0,s,X.shape)); pp=m.predict_proba(X)[:,1]
        rows.append(dict(setting=k,sigma=s,**mets(y,pp,t)))
pd.DataFrame(rows).to_csv(O+'A16_noise.csv',index=False); print('A16',time.time()-T0,flush=True)
# ---------- A13 top-k features
imp=pd.read_csv('/home/claude/repo/results/main/final_ablation.csv') if False else None
from sklearn.inspection import permutation_importance
y,p,t,m=preds['E1']; te=SET['E1'][2].sample(20000,random_state=0)
pi=permutation_importance(m,te[ALL].values,te.label.values,scoring='roc_auc',n_repeats=3,random_state=0,n_jobs=1)
order=[ALL[i] for i in np.argsort(-pi.importances_mean)]
pd.DataFrame(dict(feature=ALL,imp=pi.importances_mean,sd=pi.importances_std)).to_csv(O+'A13_perm_E1.csv',index=False)
rows=[]
for kk in [1,2,3,5,8,12,16,21]:
    for s in ['E1','E2','E3','E4a','E4b']:
        _,pv,pt,tt=run(s,feats=order[:kk]); rows.append(dict(k=kk,setting=s,**mets(SET[s][2].label.values,pt,tt)))
pd.DataFrame(rows).to_csv(O+'A13_topk.csv',index=False); print('A13',time.time()-T0,flush=True)
# ---------- A4 learning curve
rows=[]
for s in ['E1','E3','E4b']:
    for n in [500,1000,2000,5000,10000,20000,50000,100000]:
        if n>len(SET[s][0]): continue
        for rep in range(3):
            _,pv,pt,tt=run(s,ntr=n,seed=rep); rows.append(dict(setting=s,n=n,rep=rep,**mets(SET[s][2].label.values,pt,tt)))
pd.DataFrame(rows).to_csv(O+'A4_learning.csv',index=False); print('A4',time.time()-T0,flush=True)
# ---------- A6 hyperparameter grid
rows=[]
for it in [50,100,300,600]:
    for lr in [0.03,0.1,0.3]:
        for s in ['E2','E3','E4a','E4b']:
            _,pv,pt,tt=run(s,model=hgb(it,lr)); rows.append(dict(it=it,lr=lr,setting=s,**mets(SET[s][2].label.values,pt,tt)))
pd.DataFrame(rows).to_csv(O+'A6_hparam.csv',index=False); print('A6',time.time()-T0,flush=True)
