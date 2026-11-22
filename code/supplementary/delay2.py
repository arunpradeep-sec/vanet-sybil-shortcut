exec(open('/home/claude/an/analyses.py').read().split('T0=time.time()')[0])
B['ds']=np.where(B.subset.str.startswith('ext'),'ext','ng'); D0=B[B.ds=='ext'].copy()
D0['typ']=D0.subset.str.replace('ext_','').str[:-5]
rows=[];curve=[]
for s in ['E2','E4b']:
    m,pv,pt,t=run(s); D=D0.sort_values(['receiver','pseudo','rcvTime']).copy(); D['a']=m.predict_proba(D[ALL].values)[:,1]>=t
    D['k']=D.groupby(['receiver','pseudo','typ']).cumcount()
    G=D.groupby(['receiver','pseudo','typ'])
    P=pd.DataFrame(dict(lab=G.label.max(),n=G.size(),hits=G.a.sum(),frac=G.a.mean(),
        first=G.apply(lambda g: g.k[g.a].min() if g.a.any() else np.inf),t0=G.rcvTime.min(),
        tf=G.apply(lambda g: g.rcvTime[g.a].min() if g.a.any() else np.nan))).reset_index()
    P['dt']=P.tf-P.t0
    for typ,Q in P.groupby('typ'):
        for lab,R_ in Q.groupby('lab'):
            rows.append(dict(setting=s,typ=typ,lab=lab,streams=len(R_),med_len=R_.n.median(),mean_len=R_.n.mean(),msgs=int(R_.n.sum()),
              any_alarm=(R_.hits>0).mean(),majority=(R_.frac>=0.5).mean(),med_first=np.nanmedian(R_['first'].replace(np.inf,np.nan)),
              med_dt=R_.dt.median(),p90_dt=R_.dt.quantile(0.9)))
            if lab==1 or typ=='GridSybil':
                for kk in range(0,51):
                    curve.append(dict(setting=s,typ=typ,lab=lab,k=kk,frac=(R_['first']<=kk).mean()))
    print(s,flush=True)
pd.DataFrame(rows).to_csv(O+'A11b_pertype.csv',index=False); pd.DataFrame(curve).to_csv(O+'A11b_curve.csv',index=False)
