exec(open('/home/claude/an/style.py').read())
import pandas as pd, numpy as np, json, os
O='/home/claude/an/out/'
import sys; sys.path.insert(0,'/home/claude/scripts'); from experiments import KIN,HIST,NEIGH,ALL
def have(f): return os.path.exists(O+f)
from matplotlib.patches import Patch
# A1a single-feature AUC dumbbell
a=pd.read_csv(O+'A1_feature_auc_shift.csv')
fig,axs=plt.subplots(1,2,figsize=(7.4,4.4),sharey=True)
y=np.arange(len(a))[::-1]; gc={'KIN':'#1f77b4','HIST':'#c51b8a','NEIGH':'#b8860b'}
ax=axs[0]
for yy,(_,r) in zip(y,a.iterrows()):
    ax.plot([r.auc_ext,r.auc_ng],[yy,yy],color='#bbb',lw=1.5,zorder=1)
ax.scatter(a.auc_ext,y,color='#1f77b4',s=18,label='Extension',zorder=2); ax.scatter(a.auc_ng,y,color='#2ca02c',s=18,marker='D',label='NextGen',zorder=2)
ax.axvline(0.5,color='#888',ls='--',lw=0.8); ax.set_yticks(y); ax.set_yticklabels(a.feature,fontsize=7.5)
for t,yy in zip(ax.get_yticklabels(),y): t.set_color(gc[a.group.iloc[len(a)-1-yy]])
ax.set_xlabel('single-feature ROC AUC (Sybil vs genuine)'); ax.set_title('(a) Separability of each feature'); ax.legend(frameon=False,fontsize=7,loc='upper center',bbox_to_anchor=(0.5,-0.12),ncol=2); ax.set_xlim(0,1)
ax=axs[1]; h=0.38
ax.barh(y+h/2,a.ks_gen,h,color='#9ecae1',label='genuine'); ax.barh(y-h/2,a.ks_syb,h,color='#d62728',label='Sybil')
ax.set_xlabel('KS distance, Extension vs NextGen'); ax.set_title('(b) Cross-dataset shift per feature'); ax.legend(frameon=False,fontsize=7)
save(fig,'A1_feature_auc_shift')
# A1b violins of key features
v=pd.read_csv(O+'A1_violin_sample.csv.gz'); feats=['pseudo_age','msg_idx','beacon_dt','pos_jump','pos_noise','new_pseudo_frac_5s','min_dist_other','dist_rcv']
fig,axs=plt.subplots(2,4,figsize=(7.4,4.4)); fig.subplots_adjust(hspace=0.45)
for ax,f in zip(axs.ravel(),feats):
    data=[];pos=[];cols=[]
    for i,ds in enumerate(['Extension','NextGen']):
        for j,lab in enumerate([0,1]):
            x=v[(v.ds==ds)&(v.label==lab)][f].values.astype(float); x=np.sign(x)*np.log1p(np.abs(x)); data.append(x); pos.append(i*2.6+j); cols.append('#9ecae1' if lab==0 else '#d62728')
    parts=ax.violinplot(data,pos,widths=0.9,showmedians=True,showextrema=False)
    for b,c in zip(parts['bodies'],cols): b.set_facecolor(c); b.set_alpha(0.75); b.set_edgecolor('none')
    parts['cmedians'].set_color('k'); parts['cmedians'].set_linewidth(0.8)
    ax.set_xticks([0.5,3.1]); ax.set_xticklabels(['Ext','NG'],fontsize=7.5); ax.set_title(f,fontsize=8); ax.tick_params(labelsize=6.5)
axs[0,0].set_ylabel('sign·log(1+|x|)'); axs[1,0].set_ylabel('sign·log(1+|x|)')
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color='#9ecae1',label='genuine'),Patch(color='#d62728',label='Sybil')],ncol=2,frameon=False,loc='upper center',bbox_to_anchor=(0.5,1.04))
save(fig,'A1b_violins')
# A2 domain classifier
d=pd.read_csv(O+'A2_domain_clf.csv'); fig,ax=plt.subplots(figsize=(5.0,2.4))
fs=['all','KIN','HIST','NEIGH']; cl={'genuine':'#9ecae1','Sybil':'#d62728','all':'#555'}
for j,s in enumerate(['genuine','Sybil','all']):
    q=d[d.subset==s].set_index('features').loc[fs]; ax.bar(np.arange(4)+(j-1)*0.26,q.auc,0.25,color=cl[s],label=f'{s} messages')
    for i,vv in enumerate(q.auc): ax.text(i+(j-1)*0.26,vv+0.005,f'{vv:.3f}',ha='center',fontsize=5.8,rotation=90,va='bottom')
ax.set_ylim(0.85,1.04); ax.set_xticks(range(4)); ax.set_xticklabels(['all 21','KIN (5)','HIST (9)','NEIGH (7)']); ax.set_ylabel('domain ROC AUC'); ax.legend(frameon=False,fontsize=7,ncol=3,loc='upper center',bbox_to_anchor=(0.5,1.2))
save(fig,'A2_domain_classifier')
# A3 correlation heatmaps
fig,axs=plt.subplots(1,2,figsize=(7.4,3.8))
for ax,ds,tt in [(axs[0],'ext','(a) Extension'),(axs[1],'ng','(b) NextGen')]:
    Cm=pd.read_csv(O+f'A3_spearman_{ds}.csv',index_col=0).values; im=ax.imshow(Cm,cmap='RdBu_r',vmin=-1,vmax=1)
    ax.set_xticks(range(21)); ax.set_yticks(range(21)); ax.set_xticklabels(ALL,rotation=90,fontsize=5.5); ax.set_yticklabels(ALL if ds=='ext' else [],fontsize=5.5); ax.grid(False); ax.set_title(tt)
    for b in (4.5,13.5): ax.axhline(b,color='k',lw=0.6); ax.axvline(b,color='k',lw=0.6)
fig.colorbar(im,ax=axs,fraction=0.025,label='Spearman ρ')
save(fig,'A3_correlation')
# A12 PCA
p=pd.read_csv(O+'A12_pca.csv'); ev=json.load(open(O+'A12_pca.json'))['evr']
fig,ax=plt.subplots(figsize=(5.0,3.6))
for ds,mk in [('Extension','o'),('NextGen','^')]:
    for lab,c in [(0,'#1f77b4' if ds=='Extension' else '#2ca02c'),(1,'#d62728' if ds=='Extension' else '#ff7f0e')]:
        q=p[(p.ds==ds)&(p.label==lab)]; ax.scatter(q.pc1,q.pc2,s=2,alpha=0.35,c=c,marker=mk,label=f'{ds} {"Sybil" if lab else "genuine"}')
ax.set_xlabel(f'PC1 ({ev[0]*100:.1f}% var.)'); ax.set_ylabel(f'PC2 ({ev[1]*100:.1f}% var.)'); leg=ax.legend(frameon=False,fontsize=7,markerscale=4)
save(fig,'A12_pca')
# A7 threshold sweep
t=pd.read_csv(O+'A7_threshold.csv'); cm=json.load(open(O+'A10_confusion.json'))
fig,axs=plt.subplots(1,5,figsize=(7.6,2.3),sharey=True)
for ax,s in zip(axs,['E1','E2','E3','E4a','E4b']):
    q=t[t.setting==s]
    for mt,c,l in [('prec','#2ca02c','precision'),('rec','#d62728','recall'),('f1','#1f77b4','F1'),('mcc','#9467bd','MCC'),('fpr','#7f7f7f','FPR')]: ax.plot(q.thr,q[mt],color=c,lw=1,label=l)
    ax.axvline(cm[s][2][0],color='k',ls=':',lw=0.8); ax.set_title(LAB[s].replace(' ','\n',1),fontsize=7.5); ax.set_xlabel('threshold τ',fontsize=7.5); ax.tick_params(labelsize=6.5)
fig.legend(*axs[0].get_legend_handles_labels(),frameon=False,fontsize=7,ncol=5,loc='upper center',bbox_to_anchor=(0.5,1.12)); axs[0].set_ylabel('metric value')
save(fig,'A7_threshold_sweep')
# A8 calibration + A9 PR
c=pd.read_csv(O+'A8_calibration.csv'); pr=pd.read_csv(O+'A9_pr.csv'); mm=json.load(open(O+'main_metrics.json'))
fig,axs=plt.subplots(1,2,figsize=(7.2,3.1))
ax=axs[0]
for s in ['E1','E2','E3','E4a','E4b']:
    q=pr[pr.setting==s]; ax.plot(q.rec,q.prec,color=C[s],lw=1.2,label=f'{LAB[s]} (AP {mm[s]["ap"]:.3f})')
ax.set_xlabel('recall'); ax.set_ylabel('precision'); ax.set_title('(a) Precision–recall'); ax.legend(frameon=False,fontsize=6.3,loc='lower left'); ax.set_ylim(0.4,1.01)
ax=axs[1]; ax.plot([0,1],[0,1],'k--',lw=0.8)
for s in ['E1','E2','E3','E4a','E4b']:
    q=c[c.setting==s]; ax.plot(q.pmean,q.frac,'o-',ms=3,color=C[s],label=f'{s} (Brier {mm[s]["brier"]:.3f})')
ax.set_xlabel('mean predicted probability'); ax.set_ylabel('observed Sybil fraction'); ax.set_title('(b) Reliability'); ax.legend(frameon=False,fontsize=6.3)
save(fig,'A8_pr_calibration')
# A10 confusion matrices
fig,axs=plt.subplots(1,5,figsize=(7.6,1.9))
for ax,s in zip(axs,['E1','E2','E3','E4a','E4b']):
    M_=np.array(cm[s][:2],float); N=M_/M_.sum(1,keepdims=True)
    ax.imshow(N,cmap='Blues',vmin=0,vmax=1); ax.grid(False)
    for i in range(2):
        for j in range(2): ax.text(j,i,f'{N[i,j]*100:.1f}%\n{int(M_[i,j]):,}',ha='center',va='center',fontsize=6,color='w' if N[i,j]>0.6 else 'k')
    ax.set_xticks([0,1]); ax.set_yticks([0,1]); ax.set_xticklabels(['gen.','Sybil'],fontsize=6.5); ax.set_yticklabels(['gen.','Sybil'],fontsize=6.5); ax.set_title(s,fontsize=8)
axs[0].set_ylabel('true',fontsize=7); [a.set_xlabel('predicted',fontsize=7) for a in axs]
save(fig,'A10_confusion')
# A13 importance + topk
pi=pd.read_csv(O+'A13_perm_E1.csv').sort_values('imp'); tk=pd.read_csv(O+'A13_topk.csv')
fig,axs=plt.subplots(1,2,figsize=(7.4,3.3),gridspec_kw=dict(width_ratios=[1,1.2]))
ax=axs[0]; col=[gc['KIN'] if f in KIN else gc['HIST'] if f in HIST else gc['NEIGH'] for f in pi.feature]
ax.barh(range(21),pi.imp*100,xerr=pi.sd*100,color=col); ax.set_yticks(range(21)); ax.set_yticklabels(pi.feature,fontsize=6.5); ax.set_xlabel('AUC drop when permuted (pp)'); ax.set_title('(a) Permutation importance, E1',fontsize=8.5)
ax.legend(handles=[Patch(color=gc[g],label=g) for g in gc],frameon=False,fontsize=6.5,loc='lower right')
ax=axs[1]
for s in ['E1','E2','E3','E4a','E4b']:
    q=tk[tk.setting==s]; ax.plot(q.k,q.mcc*100,'o-',ms=3,color=C[s],label=LAB[s])
ax.set_xlabel('top-k features (ranked on E1)'); ax.set_ylabel('MCC (%)'); ax.set_title('(b) Performance vs number of features',fontsize=8.5); ax.legend(frameon=False,fontsize=6.3); ax.set_xticks([1,3,5,8,12,16,21])
save(fig,'A13_importance_topk')
if have('A4_learning.csv'):
    l=pd.read_csv(O+'A4_learning.csv').groupby(['setting','n']).mcc.agg(['mean','std']).reset_index()
    fig,ax=plt.subplots(figsize=(4.6,2.8))
    for s in ['E1','E3','E4b']:
        q=l[l.setting==s]; ax.errorbar(q.n,q['mean']*100,q['std']*100,marker='o',ms=3,color=C[s],label=LAB[s],capsize=2,lw=1)
    ax.set_xscale('log'); ax.set_xlabel('training messages (log)'); ax.set_ylabel('MCC (%)'); ax.legend(frameon=False,fontsize=7); ax.set_title('Learning curves (3 repeats)',fontsize=9)
    save(fig,'A4_learning_curve')
if have('A6_hparam.csv'):
    h=pd.read_csv(O+'A6_hparam.csv'); fig,axs=plt.subplots(1,4,figsize=(7.6,2.2))
    for ax,s in zip(axs,['E2','E3','E4a','E4b']):
        P=h[h.setting==s].pivot(index='lr',columns='it',values='mcc')*100; im=ax.imshow(P.values,cmap='viridis',vmin=30,vmax=100,aspect='auto'); ax.grid(False)
        for i in range(P.shape[0]):
            for j in range(P.shape[1]): ax.text(j,i,f'{P.values[i,j]:.1f}',ha='center',va='center',fontsize=6.5,color='w' if P.values[i,j]<70 else 'k')
        ax.set_xticks(range(P.shape[1])); ax.set_xticklabels(P.columns,fontsize=6.5); ax.set_yticks(range(P.shape[0])); ax.set_yticklabels(P.index if s=='E2' else [],fontsize=6.5); ax.set_title(LAB[s],fontsize=7.5); ax.set_xlabel('iterations',fontsize=7)
    axs[0].set_ylabel('learning rate',fontsize=7); fig.colorbar(im,ax=axs,fraction=0.02,label='MCC (%)')
    save(fig,'A6_hparam')
print('ok')
