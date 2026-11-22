exec(open('/home/claude/an/style.py').read())
import pandas as pd, numpy as np
U='/mnt/user-data/uploads/VANET Paper/sybil_pipeline/'
R=pd.read_csv(U+'results_robust/robust_results.csv')
sets=[('NG -> Ext (all types)','P1: NextGen\n→ Extension'),('Ext non-Grid -> Grid 0709','P2: unseen\nGridSybil'),('NG -> NG test','NextGen test\n(in-domain)'),('Ext non-Grid -> seen 0709','Extension\nseen types')]
V=[('B','B: all features','#9e9e93'),('F','F: physical features','#6baed6'),('A','A: all + phantoms','#ee7f50'),('R','R: physical + phantoms','#2171b5')]
fig,axs=plt.subplots(1,2,figsize=(7.4,2.9),gridspec_kw=dict(width_ratios=[1.6,1]))
ax=axs[0]; w=0.2
for j,(v,l,c) in enumerate(V):
    m=[R[(R.setting==s)&(R.variant==v)].mcc.mean()*100 for s,_ in sets]; e=[R[(R.setting==s)&(R.variant==v)].mcc.std()*100 for s,_ in sets]
    ax.bar(np.arange(4)+(j-1.5)*w,m,w,yerr=e,color=c,label=l,capsize=1.5,error_kw=dict(lw=0.6))
ax.set_xticks(range(4)); ax.set_xticklabels([t for _,t in sets],fontsize=7); ax.set_ylabel('MCC (%)'); ax.set_ylim(0,105); ax.legend(frameon=False,fontsize=6.5,ncol=2,loc='upper center',bbox_to_anchor=(0.5,1.22)); ax.text(0.0,1.25,'(a) Message level',transform=ax.transAxes,fontsize=8.5)
ax=axs[1]; s='NG -> Ext (all types)'
for v,l,c in V:
    q=R[(R.setting==s)&(R.variant==v)]; ax.errorbar(q.ps_fpr_majority.mean()*100,q.ps_tpr_majority.mean()*100,xerr=q.ps_fpr_majority.std()*100,yerr=q.ps_tpr_majority.std()*100,fmt='o',color=c,ms=6,capsize=2)
    ax.annotate(v,(q.ps_fpr_majority.mean()*100,q.ps_tpr_majority.mean()*100),xytext=(5,-10),textcoords='offset points',fontsize=8)
ax.set_xlabel('genuine pseudonyms reported (%)'); ax.set_ylabel('Sybil pseudonyms reported (%)'); ax.set_title('(b) Pseudonym level, NextGen → Extension',fontsize=8.5); ax.set_xlim(0,30); ax.set_ylim(30,100)
save(fig,'R9_robust_ablation')
A=pd.read_csv(U+'results_adaptive/adaptive_by_k.csv'); P=pd.read_csv(U+'results_adaptive/adaptive_pseudonym.csv')
bins=['rec_k0','rec_k1','rec_k2-4','rec_k5-9','rec_k10-19','rec_k20+']; lab=['0','1','2–4','5–9','10–19','20+']
MC={'NG':('NextGen-trained','#d62728','-'),'EXT-3':('Extension, no GridSybil','#ff7f0e','-'),'EXT':('Extension, with GridSybil','#2ca02c','-'),'NG+R':('NextGen + phantoms, physical (R)','#1f77b4','--')}
fig,axs=plt.subplots(1,2,figsize=(7.6,3.2)); fig.subplots_adjust(wspace=0.3)
ax=axs[0]; q=A[A.test=='GridSybil (real)']
for m,(l,c,ls) in MC.items():
    z=q[q.model==m]; ax.errorbar(range(6),z[bins].mean()*100,yerr=z[bins].std()*100,color=c,ls=ls,marker='o',ms=3,capsize=2,label=l)
ax.set_xticks(range(6)); ax.set_xticklabels(lab); ax.set_xlabel('messages already heard from phantom (k)'); ax.set_ylabel('phantom messages detected (%)'); ax.set_ylim(-3,100); ax.set_title('(a) Real GridSybil phantoms, by warm-up k',fontsize=8.5)
fig.legend(*ax.get_legend_handles_labels(),frameon=False,fontsize=7,ncol=4,loc='upper center',bbox_to_anchor=(0.5,1.07))
ax=axs[1]; Ks=[0,1,3,5,10]
for m,(l,c,ls) in MC.items():
    z=P[(P.test=='GridSybil (real)')&(P.model==m)].groupby('warmup').ps_tpr.agg(['mean','std'])
    ax.errorbar(Ks,z['mean']*100,yerr=z['std']*100,color=c,ls=ls,marker='o',ms=3,capsize=2)
ax.set_xticks(Ks); ax.set_xlabel('warm-up K (messages before the attack phase)'); ax.set_ylabel('phantoms reported (majority, %)'); ax.set_ylim(-3,100); ax.set_title('(b) Pseudonym level after warm-up',fontsize=8.5)
save(fig,'R10_adaptive_attacker')
print('ok')
