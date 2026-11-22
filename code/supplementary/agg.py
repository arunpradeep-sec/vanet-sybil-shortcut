import pandas as pd, numpy as np, json, os
B='/mnt/user-data/uploads/VANET Paper/sybil_pipeline/results_supp/seed'
def cat(f): return pd.concat([pd.read_csv(f'{B}{s}/{f}').assign(seed=s) for s in range(5)],ignore_index=True)
pd.set_option('display.width',250)
A1=cat('A1_feature_auc_shift.csv'); print(A1.groupby('feature')[['auc_ext','auc_ng','ks_gen','ks_syb']].agg(['mean','std']).round(3).to_string())
A2=cat('A2_domain_clf.csv'); print(A2.groupby(['subset','features']).auc.agg(['mean','std']).round(4))
M=pd.DataFrame([dict(seed=s,setting=k,**v) for s in range(5) for k,v in json.load(open(f'{B}{s}/main_metrics.json')).items()])
print((M.groupby('setting')[['f1','mcc','auc','ap','tpr1','fpr','brier']].agg(['mean','std'])*100).round(2).to_string())
print('=== ZOO'); Z=cat('A5_zoo.csv')
zz=(Z.groupby(['model','setting']).mcc.agg(['mean','std'])*100).round(1); print(zz.unstack('setting').to_string())
print((Z.groupby(['model','setting']).tpr1.mean()*100).round(1).unstack().to_string()); print(Z.groupby('model').sec.agg(['min','max']).round(1))
print('=== LEARN'); L=cat('A4_learning.csv'); print((L.groupby(['setting','n'])[['mcc','tpr1']].agg(['mean','std'])*100).round(1).to_string())
print('=== HP'); H=cat('A6_hparam.csv'); hp=(H.groupby(['setting','lr','it']).mcc.agg(['mean','std'])*100).round(1); print(hp['mean'].unstack('it').to_string()); print(hp['std'].unstack('it').max(level=0) if False else hp['std'].groupby(level=0).max())
print('=== THR'); T=cat('A7_threshold.csv'); Tm=T.groupby(['setting','thr']).mcc.mean().reset_index()
for s in ['E1','E2','E3','E4a','E4b']:
    q=Tm[Tm.setting==s]; r=q[(q.thr>=.2)&(q.thr<=.8)]; print(s,'best',round(q.mcc.max()*100,1),round(q.thr[q.mcc.idxmax()],2),'range',round(r.mcc.min()*100,1),round(r.mcc.max()*100,1))
best=T.groupby(['setting','seed']).mcc.max().groupby('setting').agg(['mean','std'])*100; print(best.round(1))
print('=== CAL'); C=cat('A8_calibration.csv'); print(C[C.setting.isin(['E4a','E4b'])].groupby(['setting','bin'])[['pmean','frac','n']].mean().round(3).to_string())
print('=== CONF'); cm={s:np.sum([np.array(json.load(open(f'{B}{k}/A10_confusion.json'))[s][:2]) for k in range(5)],axis=0) for s in ['E1','E2','E3','E4a','E4b']}
for s,v in cm.items(): tn,fp,fn,tp=v.ravel(); print(s,'FPR',round(fp/(fp+tn)*100,1),'FNR',round(fn/(fn+tp)*100,1),int(fn),int(fn+tp))
per=[]
for k in range(5):
    j=json.load(open(f'{B}{k}/A10_confusion.json'))
    for s in j: (tn,fp),(fn,tp)=j[s][:2]; per.append(dict(s=s,fpr=fp/(fp+tn),fnr=fn/(fn+tp)))
print((pd.DataFrame(per).groupby('s').agg(['mean','std'])*100).round(1))
print('=== PERM'); P=cat('A13_perm_E1.csv'); print((P.groupby('feature').imp.agg(['mean','std'])*100).round(2).sort_values('mean',ascending=False).to_string())
for s in range(5): print(s, list(pd.read_csv(f'{B}{s}/A13_perm_E1.csv').sort_values('imp',ascending=False).feature[:3]))
print('=== TOPK'); K=cat('A13_topk.csv'); print((K.groupby(['k','setting']).mcc.agg(['mean','std'])*100).round(1).unstack('setting').to_string())
print('=== AGG'); G=cat('A11_aggregate.csv'); print((G.groupby(['setting','rule'])[['tpr','fpr']].agg(['mean','std'])*100).round(1).to_string())
print('=== PERTYPE'); PT=cat('A11b_pertype.csv'); print(PT.groupby(['setting','typ','lab'])[['streams','med_len','mean_len','any_alarm','majority','p90_dt']].mean().round(3).to_string())
CU=cat('A11b_curve.csv'); print((CU[(CU.typ=='GridSybil')&(CU.k.isin([0,5,50]))].groupby(['setting','lab','k']).frac.agg(['mean','std'])*100).round(1).to_string())
print('=== NOISE'); N=cat('A16b_noise.csv'); print((N.groupby(['sigma','setting'])[['mcc','tpr1']].mean()*100).round(1).unstack('setting').to_string())
