exec(open('/home/claude/an/style.py').read())
import pandas as pd, numpy as np, json
R='/home/claude/repo/results/'
def ms(s): 
    a=s.astype(str).str.split(' ± ',expand=True); return a[0].astype(float),a[1].astype(float)
# R1 dataset composition
m=pd.read_csv('/mnt/user-data/uploads/VANET Paper/features/manifest.csv')
fig,axs=plt.subplots(1,2,figsize=(7.4,2.9),gridspec_kw=dict(width_ratios=[1.6,1]))
e=m[m.dataset=='ext']; lab=e.subset.str.replace('Sybil_',' ').str.replace('DoSDisruptive','DoSDisr.').str.replace('DoSRandom','DoSRand.').str.replace('DataReplay','DataRepl.')
x=np.arange(len(e)); ax=axs[0]
ax.bar(x,(e.messages-e.sybil)/1e6,color='#9ecae1',label='genuine'); ax.bar(x,e.sybil/1e6,bottom=(e.messages-e.sybil)/1e6,color='#d62728',label='Sybil')
for i,(t,s) in enumerate(zip(e.messages,e.sybil)): ax.text(i,t/1e6+0.08,f'{s/t*100:.0f}%',ha='center',fontsize=7)
ax.set_xticks(x); ax.set_xticklabels(lab,rotation=35,ha='right',fontsize=7); ax.set_ylabel('messages (millions)'); ax.set_title('(a) VeReMi Extension (label = Sybil share)'); ax.legend(frameon=False)
g=m[m.dataset=='ng'].copy(); g['sc']=g.subset.str.replace('InTAS_','').str.rsplit('_',n=1).str[0]; g['sp']=g.subset.str.rsplit('_',n=1).str[1]
P=g.pivot(index='sc',columns='sp',values='messages')[['Train','Validation','Test']]/1e6; ax=axs[1]
bot=np.zeros(len(P)); cs={'Train':'#2ca02c','Validation':'#98df8a','Test':'#ff7f0e'}
for c in P.columns: ax.bar(range(len(P)),P[c],bottom=bot,color=cs[c],label=c); bot+=P[c].values
ax.set_xticks(range(len(P))); ax.set_xticklabels(P.index,rotation=35,ha='right',fontsize=7); ax.set_title('(b) VeReMi NextGen (InTAS) splits'); ax.legend(frameon=False); ax.set_ylabel('messages (millions)')
save(fig,'R1_dataset_composition')
# R2 main results
d=pd.read_csv(R+'main/final_main.csv')
order=['Ext 0709','Ext 1416','Ext 0709 -> 1416','Ext 1416 -> 0709','NG official split','Ext -> NG test','NG train -> Ext']
short=['E1\n0709','E1\n1416','E2\n0709→1416','E2\n1416→0709','E3\nNG split','E4a\nExt→NG','E4b\nNG→Ext']
d.loc[d.setting_g=='NG -> Ext (rule on Ext)','setting_g']='NG train -> Ext'
fig,axs=plt.subplots(2,1,figsize=(7.4,4.6),sharex=True)
for ax,met,tt in [(axs[0],'mcc','MCC (%)'),(axs[1],'tpr_at_1fpr','TPR at 1% FPR (%)')]:
    for j,mo in enumerate(['HGB','RF','rule']):
        v=[];s=[]
        for o in order:
            r=d[(d.setting_g==o)&(d.model==mo)]
            if len(r): a,b=ms(r[met]); v.append(a.iloc[0]); s.append(b.iloc[0])
            else: v.append(np.nan); s.append(0)
        ax.bar(np.arange(7)+(j-1)*0.27,v,0.26,yerr=s,color=M[mo],label=mo,capsize=1.5,error_kw=dict(lw=0.6))
    ax.set_ylabel(tt); ax.set_ylim(0,105)
axs[0].legend(ncol=3,frameon=False,loc='lower left'); axs[1].set_xticks(range(7)); axs[1].set_xticklabels(short,fontsize=7.5)
axs[0].set_title('Main results, mean ± s.d. over 5 seeds')
save(fig,'R2_main_results')
# R3 per-type recall heatmap
p=pd.read_csv(R+'main/final_per_type_recall.csv'); p.loc[p.setting_g=='NG -> Ext (rule on Ext)','setting_g']='NG train -> Ext'
types=['DataReplaySybil','DoSDisruptiveSybil','DoSRandomSybil','GridSybil']
rows=[];labs=[]
for o in ['Ext 0709','Ext 1416','Ext 0709 -> 1416','Ext 1416 -> 0709','NG train -> Ext']:
    for mo in ['HGB','RF','rule']:
        r=p[(p.setting_g==o)&(p.model==mo)]
        if len(r): rows.append([ms(r['rec_'+t])[0].iloc[0] for t in types]); labs.append(f'{o.replace("NG train -> Ext","E4b NG→Ext").replace("Ext ","Ext ").replace(" -> ","→")} · {mo}')
A=np.array(rows); fig,ax=plt.subplots(figsize=(5.6,5.2)); im=ax.imshow(A,cmap='RdYlGn',vmin=0,vmax=100,aspect='auto')
for i in range(A.shape[0]):
    for j in range(A.shape[1]): ax.text(j,i,f'{A[i,j]:.1f}',ha='center',va='center',fontsize=7,color='k')
ax.set_xticks(range(4)); ax.set_xticklabels([t.replace('Sybil','') for t in types]); ax.set_yticks(range(len(labs))); ax.set_yticklabels(labs,fontsize=7); ax.grid(False)
for y in (2.5,5.5,8.5,11.5): ax.axhline(y,color='w',lw=2)
plt.colorbar(im,ax=ax,label='recall (%)',fraction=0.04); ax.set_title('Recall per Sybil type (F1-optimal validation threshold)')
save(fig,'R3_recall_heatmap')
# R4 ablation heatmap
ab=pd.read_csv(R+'main/final_ablation.csv'); variants=['only kinematic','only history','only neighbourhood','all minus kinematic','all minus history','all minus neighbourhood','new_pseudo + neighbourhood']
sets=['Ext 0709','Ext 1416','NG official split']; A=np.array([[ms(ab[(ab.setting_g==s)&(ab.feats==v)].mcc)[0].iloc[0] for s in sets] for v in variants])
full=[88.90,88.27,98.82]; A=np.vstack([full,A]); variants=['all 21 features']+variants
fig,ax=plt.subplots(figsize=(5.2,3.6)); im=ax.imshow(A,cmap='viridis',vmin=0,vmax=100,aspect='auto')
for i in range(A.shape[0]):
    for j in range(3): ax.text(j,i,f'{A[i,j]:.1f}',ha='center',va='center',fontsize=8,color='w' if A[i,j]<60 else 'k')
ax.set_xticks(range(3)); ax.set_xticklabels(['Ext 0709','Ext 1416','NG split']); ax.set_yticks(range(len(variants))); ax.set_yticklabels(variants,fontsize=8); ax.grid(False)
plt.colorbar(im,ax=ax,label='MCC (%)',fraction=0.05); ax.set_title('Feature-group ablation, HGB (MCC)')
save(fig,'R4_ablation_heatmap')
# R5 shortcut fixes
s=pd.read_csv(R+'main/final_shortcut.csv'); st=['in-domain Ext 0709 -> 1416','in-domain NG official','Ext -> NG test','NG train -> Ext']
vs=['all','drop_age','drop_history','mask25','mask50']; cols=['#1f77b4','#6baed6','#d62728','#fdae6b','#e6550d']
fig,ax=plt.subplots(figsize=(7.2,3.0))
for j,v in enumerate(vs):
    a=[ms(s[(s.setting==x)&(s.feats==v)].mcc)[0].iloc[0] for x in st]; e=[ms(s[(s.setting==x)&(s.feats==v)].mcc)[1].iloc[0] for x in st]
    ax.bar(np.arange(4)+(j-2)*0.16,a,0.15,yerr=e,color=cols[j],label=v.replace('_',' '),capsize=1.5,error_kw=dict(lw=0.6))
ax.set_xticks(range(4)); ax.set_xticklabels(['E2 Ext 0709→1416','E3 NG split','E4a Ext→NG','E4b NG→Ext']); ax.set_ylabel('MCC (%)'); ax.legend(ncol=5,frameon=False,fontsize=7,loc='upper center',bbox_to_anchor=(0.5,1.15)); ax.set_ylim(0,105)
save(fig,'R5_shortcut_fixes')
# R6 seen vs unseen per model incl LSTM
lo=pd.read_csv(R+'main/final_loto.csv'); ls=pd.read_csv(R+'lstm/lstm_summary.csv')
types=['GridSybil','DataReplaySybil','DoSRandomSybil','DoSDisruptiveSybil']
fig,axs=plt.subplots(1,4,figsize=(7.4,2.6),sharey=True)
for ax,t in zip(axs,types):
    for j,mo in enumerate(['HGB','RF','LSTM']):
        for k,mode in enumerate(['seen','unseen']):
            if mo=='LSTM': r=ls[(ls.group==f'{t} {mode}')&(ls.model=='LSTM')]; v,e=ms(r.mcc)
            else: r=lo[(lo.held_out==t)&(lo.model==mo)&(lo.feats==mode)]; v,e=ms(r.mcc)
            ax.bar(j*2.4+k,v.iloc[0],0.9,yerr=e.iloc[0],color=M[mo],alpha=1 if mode=='seen' else 0.45,hatch=None if mode=='seen' else '///',edgecolor='w',capsize=1.5,error_kw=dict(lw=0.6))
    ax.set_xticks([0.5,2.9,5.3]); ax.set_xticklabels(['HGB','RF','LSTM'],fontsize=7); ax.set_title(t.replace('Sybil',''),fontsize=8.5)
axs[0].set_ylabel('MCC (%)'); 
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color='#555',label='type seen in training'),Patch(fc='#555',alpha=0.45,hatch='///',label='type held out (unseen)')],ncol=2,frameon=False,loc='upper center',bbox_to_anchor=(0.5,1.07))
save(fig,'R6_seen_unseen_models')
# R7 latency
pi=json.load(open(R+'latency/raspberry_pi_4b.json')); m2=json.load(open(R+'latency/apple_m2.json'))
comp=[('feature extraction',lambda d:d['features_us']),('HGB (scikit-learn)',lambda d:d['single_us']['HGB']),('RF (scikit-learn)',lambda d:d['single_us']['RF']),('HGB lean (flat NumPy)',lambda d:d['single_us']['HGB_lean']),('end-to-end lean',lambda d:d['end_to_end_HGB_lean_us'])]
fig,axs=plt.subplots(1,2,figsize=(7.4,2.8),gridspec_kw=dict(width_ratios=[2,1]))
ax=axs[0]
for j,(nm,d,c) in enumerate([('Raspberry Pi 4B',pi,'#c51b8a'),('Apple M2',m2,'#2171b5')]):
    v=[f(d)['median'] for _,f in comp]; p99=[f(d)['p99'] for _,f in comp]
    y=np.arange(len(comp))+(j-0.5)*0.38; ax.barh(y,v,0.36,color=c,label=nm); ax.scatter(p99,y,marker='|',color='k',s=40,zorder=3)
    for yy,vv,pp in zip(y,v,p99): ax.text(pp*1.4,yy,f'{vv/1000:.2f} ms' if vv>=1000 else f'{vv:.0f} µs',va='center',fontsize=6.5)
ax.set_xscale('log'); ax.set_yticks(range(len(comp))); ax.set_yticklabels([c[0] for c in comp],fontsize=7.5); ax.invert_yaxis(); ax.set_xlabel('per-message latency, median (µs, log); | = p99'); ax.legend(frameon=False,fontsize=7,loc='lower right')
ax.axvline(100000,color='#888',ls='--',lw=0.8); ax.text(100000,-0.7,'100 ms beacon period',fontsize=6.5,ha='center',color='#555'); ax.set_xlim(1,4e5)
ax=axs[1]; ax.bar([0,1],[pi['model_bytes']['HGB']/1e6,pi['model_bytes']['RF']/1e6],color=[M['HGB'],M['RF']]); ax.set_yscale('log'); ax.set_xticks([0,1]); ax.set_xticklabels(['HGB','RF']); ax.set_ylabel('model size (MB, log)')
for i,v in enumerate([pi['model_bytes']['HGB']/1e6,pi['model_bytes']['RF']/1e6]): ax.text(i,v*1.15,f'{v:.1f} MB',ha='center',fontsize=7)
ax.set_title('Serialized model size',fontsize=8.5)
save(fig,'R7_latency')
# R8 phantom fraction curves
ph=pd.read_csv(R+'phantom/phantom_summary.csv'); pdft=pd.read_csv(R+'phantom_drift/phantom_summary.csv')
fr={'base':0,'aug0.05':5,'aug0.1':10,'aug0.2':20}
fig,axs=plt.subplots(1,3,figsize=(7.4,2.5))
ax=axs[0]; P1=ph[ph.setting=='NG train -> Ext']
for t in ['GridSybil','DataReplaySybil','DoSRandomSybil','DoSDisruptiveSybil']:
    ax.plot([fr[v] for v in P1.variant],ms(P1['rec_'+t])[0],'o-',ms=3,color=T[t],label=t.replace('Sybil',''))
ax.set_title('(a) P1 NG→Ext recall by type',fontsize=8.5); ax.set_xlabel('phantom hosts (% of senders)'); ax.set_ylabel('recall (%)'); ax.legend(frameon=False,fontsize=6.5)
ax=axs[1]
for df,lab,c in [(ph,'mixed phantoms','#d62728'),(pdft,'drift-only phantoms','#ff7f0e')]:
    q=df[df.setting=='GridSybil 1416->0709 unseen']; q=q[q.variant.isin(fr) | q.variant.str.startswith('aug')]
    xv=[fr.get(v,fr.get(v.replace('_drift',''),None)) for v in q.variant]; ax.plot(xv,ms(q.f1)[0],'o-',ms=3,color=c,label=lab)
q=ph[ph.setting=='3 seen types 1416->0709']; ax.plot([fr[v] for v in q.variant],ms(q.f1)[0],'s--',ms=3,color='#1f77b4',label='3 seen types')
ax.set_title('(b) P2 unseen GridSybil F1',fontsize=8.5); ax.set_xlabel('phantom hosts (% of senders)'); ax.set_ylabel('F1 (%)'); ax.legend(frameon=False,fontsize=6.5)
ax=axs[2]; q=ph[ph.setting=='NG train -> NG test']
ax.plot([fr[v] for v in q.variant],ms(q.fa_first_msg)[0],'o-',ms=3,color='#7f7f7f',label='first message of a pseudonym')
ax.plot([fr[v] for v in q.variant],ms(q.fa_with_history)[0],'o-',ms=3,color='#2ca02c',label='messages with history')
ax.set_title('(c) P1 genuine false alarms, NG test',fontsize=8.5); ax.set_xlabel('phantom hosts (% of senders)'); ax.set_ylabel('false-alarm rate (%)'); ax.legend(frameon=False,fontsize=6.5)
save(fig,'R8_phantom_curves')
print('done')
