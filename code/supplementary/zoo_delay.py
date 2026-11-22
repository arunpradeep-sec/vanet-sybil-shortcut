exec(open('/home/claude/an/analyses.py').read().split('T0=time.time()')[0])
T0=time.time()
lg=FunctionTransformer(lambda X: np.sign(X)*np.log1p(np.abs(X)))
Z={'LR':lambda: make_pipeline(lg,StandardScaler(),LogisticRegression(max_iter=500)),
   'NB':lambda: make_pipeline(lg,GaussianNB()),
   'DT':lambda: DecisionTreeClassifier(min_samples_leaf=20,random_state=0),
   'kNN':lambda: make_pipeline(lg,StandardScaler(),KNeighborsClassifier(15,n_jobs=2)),
   'MLP':lambda: make_pipeline(lg,StandardScaler(),MLPClassifier((64,64),early_stopping=True,max_iter=200,random_state=0)),
   'ET':lambda: ExtraTreesClassifier(100,min_samples_leaf=2,n_jobs=2,random_state=0),
   'RF':lambda: RandomForestClassifier(100,min_samples_leaf=2,max_samples=0.3,n_jobs=2,random_state=0),
   'HGB':lambda: hgb()}
rows=[]
for s in SET:
    tr,va,te=SET[s]; tr=tr.sample(min(60000,len(tr)),random_state=0); te=te.sample(min(60000,len(te)),random_state=0)
    for nm,f in Z.items():
        t0=time.time(); m=f().fit(tr[ALL].values,tr.label.values); pv=m.predict_proba(va[ALL].values)[:,1]; pt=m.predict_proba(te[ALL].values)[:,1]
        rows.append(dict(setting=s,model=nm,sec=time.time()-t0,**mets(te.label.values,pt,f1thr(va.label.values,pv)))); print(s,nm,rows[-1]['mcc'],flush=True)
    pd.DataFrame(rows).to_csv(O+'A5_zoo.csv',index=False)
# ---------- A11 detection delay + pseudonym aggregation on receiver blocks
B['ds']=np.where(B.subset.str.startswith('ext'),'ext','ng')
blk={'E2':B[B.ds=='ext'],'E3':B[B.ds=='ng'],'E4a':B[B.ds=='ng'],'E4b':B[B.ds=='ext']}
rows=[]; agg=[]
for s,D in blk.items():
    m,pv,pt,t=run(s); D=D.sort_values(['receiver','pseudo','rcvTime']).copy(); D['p']=m.predict_proba(D[ALL].values)[:,1]; D['a']=D.p>=t
    D['k']=D.groupby(['receiver','pseudo']).cumcount()
    G=D.groupby(['receiver','pseudo'])
    first=G.apply(lambda g: g.k[g.a].min() if g.a.any() else np.inf); lab=G.label.max(); n=G.size()
    t0=G.rcvTime.min(); tf=G.apply(lambda g: g.rcvTime[g.a].min() if g.a.any() else np.inf)
    P=pd.DataFrame(dict(first=first,lab=lab,n=n,dt=tf-t0))
    for kk in [0,1,2,3,4,5,7,10,15,20,30,50]:
        rows.append(dict(setting=s,k=kk,syb=(P[P.lab==1]['first']<=kk).mean(),gen=(P[P.lab==0]['first']<=kk).mean()))
    for kk in [1,2,3,5]:  # pseudonym flagged if >= kk alarms in its stream ; and fraction of flagged messages >= 0.5
        c=G.a.sum(); fl=c>=kk
        agg.append(dict(setting=s,rule=f'>={kk} alarms',tpr=fl[lab==1].mean(),fpr=fl[lab==0].mean(),n_syb=int((lab==1).sum()),n_gen=int((lab==0).sum())))
    fr=G.a.mean()>=0.5; agg.append(dict(setting=s,rule='majority',tpr=fr[lab==1].mean(),fpr=fr[lab==0].mean(),n_syb=int((lab==1).sum()),n_gen=int((lab==0).sum())))
    P.to_csv(O+f'A11_pseudo_{s}.csv'); print(s,'delay done',time.time()-T0,flush=True)
pd.DataFrame(rows).to_csv(O+'A11_delay.csv',index=False); pd.DataFrame(agg).to_csv(O+'A11_aggregate.csv',index=False)
# ---------- A16b sensor-noise robustness (physical features only, sentinels kept)
PH=['spd','acc','pos_noise','spd_noise','dist_rcv','pos_jump','pos_pred_err','spd_change_rate','hed_motion_err','first_seen_dist','min_dist_other']
rows=[]
for s in ['E1','E2','E3','E4a']:
    m,pv,pt,t=run(s); te=SET[s][2]
    if len(te)>100000: te=te.sample(100000,random_state=0)
    y=te.label.values
    for sg in [0,0.01,0.02,0.05,0.1,0.2,0.3]:
        X=te[ALL].copy()
        for f in PH:
            x=X[f].values.astype(float); ok=(x>=0)&(x<999); x[ok]=np.abs(x[ok]*(1+np.random.default_rng(1).normal(0,sg,ok.sum()))); X[f]=x
        rows.append(dict(setting=s,sigma=sg,**mets(y,m.predict_proba(X.values)[:,1],t)))
pd.DataFrame(rows).to_csv(O+'A16b_noise.csv',index=False); print('A16b',flush=True)
