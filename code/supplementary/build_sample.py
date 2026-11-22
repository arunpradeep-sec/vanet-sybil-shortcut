import glob, os, gc, numpy as np, pandas as pd
F=os.environ.get('FEAT','../features'); OUT=os.environ.get('OUT','results_supp'); os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(int(os.environ.get('SEED','0'))); out=[]; blk=[]
N={'ext':60000,'Train':30000,'Validation':15000,'Test':50000}
for p in sorted(glob.glob(F+'/*.pkl.gz')):
    b=os.path.basename(p).replace('.pkl.gz',''); d=pd.read_pickle(p)
    key='ext' if b.startswith('ext') else b.split('_')[-1]
    n=min(N[key],len(d)); s=d.iloc[np.sort(rng.choice(len(d),n,replace=False))].copy(); s['subset']=b; out.append(s)
    if b.endswith('1416') or key=='Test':
        rc=d.receiver.unique(); pick=rng.choice(rc,min(40 if key=='ext' else 20,len(rc)),replace=False)
        k=d[d.receiver.isin(pick)].copy(); k['subset']=b; blk.append(k)
    print(b,len(d),n,flush=True); del d; gc.collect()
S=pd.concat(out,ignore_index=True); B=pd.concat(blk,ignore_index=True)
S.to_pickle(OUT+'/sample.pkl'); B.to_pickle(OUT+'/blocks.pkl'); print(len(S),len(B))
