exec(open('/home/claude/an/style.py').read())
import pandas as pd, numpy as np
O='/home/claude/an/out/'
z=pd.read_csv(O+'A5_zoo.csv'); order=['NB','LR','DT','kNN','MLP','ET','RF','HGB']; sets=['E1','E2','E3','E4a','E4b']
fig,axs=plt.subplots(1,2,figsize=(7.4,3.0))
for ax,met,tt in [(axs[0],'mcc','(a) MCC (%)'),(axs[1],'tpr1','(b) TPR at 1% FPR (%)')]:
    P=z.pivot(index='model',columns='setting',values=met).loc[order,sets]*100
    im=ax.imshow(P.values,cmap='viridis',vmin=0,vmax=100,aspect='auto'); ax.grid(False)
    for i in range(8):
        for j in range(5): ax.text(j,i,f'{P.values[i,j]:.1f}',ha='center',va='center',fontsize=7,color='w' if P.values[i,j]<60 else 'k')
    ax.set_xticks(range(5)); ax.set_xticklabels(['E1','E2','E3','E4a','E4b']); ax.set_yticks(range(8)); ax.set_yticklabels(['Gaussian NB','Logistic reg.','Decision tree','kNN','MLP','Extra trees','Random forest','HGB'] if met=='mcc' else [],fontsize=7.5); ax.set_title(tt,fontsize=9)
fig.colorbar(im,ax=axs,fraction=0.025)
save(fig,'A5_model_zoo')
# A11 delay
c=pd.read_csv(O+'A11b_curve.csv'); pt=pd.read_csv(O+'A11b_pertype.csv')
fig,axs=plt.subplots(1,2,figsize=(7.4,2.9),gridspec_kw=dict(width_ratios=[1,1.25]))
ax=axs[0]
for s,ls in [('E2','-'),('E4b','--')]:
    for lab,col,nm in [(1,'#d62728','GridSybil phantoms'),(0,'#1f77b4','genuine (Grid runs)')]:
        q=c[(c.setting==s)&(c.typ=='GridSybil')&(c.lab==lab)]; ax.step(q.k,q.frac*100,where='post',color=col,ls=ls,label=f'{nm}, {s}')
ax.set_xlabel('messages heard from the pseudonym (k)'); ax.set_ylabel('pseudonyms with ≥1 alarm by message k (%)'); ax.set_xlim(0,50); ax.set_ylim(0,100); ax.legend(frameon=False,fontsize=6.3,loc='upper center',bbox_to_anchor=(0.5,-0.2),ncol=2); ax.set_title('(a) Cumulative detection, GridSybil runs',fontsize=8.5)
ax=axs[1]; types=['DataReplaySybil','DoSDisruptiveSybil','DoSRandomSybil','GridSybil']; w=0.2
for j,(s,lab,rule,col,h) in enumerate([('E2',1,'majority','#1f77b4',None),('E4b',1,'majority','#d62728',None),('E2',0,'any_alarm','#9ecae1','///'),('E4b',0,'any_alarm','#fcae91','///')]):
    v=[pt[(pt.setting==s)&(pt.typ==t)&(pt.lab==lab)][rule].iloc[0]*100 for t in types]
    ax.bar(np.arange(4)+(j-1.5)*w,v,w,color=col,hatch=h,edgecolor='w',label=f'{s}: {"Sybil detected (majority)" if lab else "genuine with ≥1 alarm"}')
ax.set_xticks(range(4)); ax.set_xticklabels([t.replace('Sybil','') for t in types],fontsize=7.5); ax.set_ylabel('% of pseudonym streams'); ax.legend(frameon=False,fontsize=6.3,ncol=2,loc='upper center',bbox_to_anchor=(0.5,1.25)); ax.set_ylim(0,105)
save(fig,'A11_delay_pseudonym')
n=pd.read_csv(O+'A16b_noise.csv'); fig,axs=plt.subplots(1,2,figsize=(6.6,2.5))
for ax,met,tt in [(axs[0],'mcc','MCC (%)'),(axs[1],'tpr1','TPR at 1% FPR (%)')]:
    for s in ['E1','E2','E3','E4a']:
        q=n[n.setting==s]; ax.plot(q.sigma*100,q[met]*100,'o-',ms=3,color=C[s],label=LAB[s])
    ax.set_xlabel('relative noise σ (%)'); ax.set_ylabel(tt)
fig.legend(*axs[0].get_legend_handles_labels(),frameon=False,fontsize=7,ncol=4,loc='upper center',bbox_to_anchor=(0.5,1.1))
save(fig,'A16_noise')
print('ok')
