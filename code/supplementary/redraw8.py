exec(open('/home/claude/an/style.py').read())
import re, numpy as np, pandas as pd
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon
GREY='#f0efec'; EDGE='#b8b6ad'; ACC='#1f6fd1'
def box(ax,x,y,w,h,title,sub='',fc='white',ec=EDGE,lw=1.2,tw='bold',fs=10,sfs=8.5,align='center'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02,rounding_size=0.12',fc=fc,ec=ec,lw=lw,zorder=3))
    if align=='center':
        ax.text(x+w/2,y+h*0.66,title,ha='center',va='center',fontsize=fs,weight=tw,zorder=4)
        if sub: ax.text(x+w/2,y+h*0.3,sub,ha='center',va='center',fontsize=sfs,color='#555',zorder=4)
    else:
        ax.text(x+0.2,y+h-0.25,title,ha='left',va='top',fontsize=fs,weight=tw,zorder=4)
        if sub: ax.text(x+0.2,y+h-0.62,sub,ha='left',va='top',fontsize=sfs,color='#555',zorder=4,linespacing=1.4)
def arr(ax,a,b,c='#999',lw=1.2):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=10,color=c,lw=lw,zorder=2))
# Fig1 architecture
fig,ax=plt.subplots(figsize=(10,7.3)); ax.set_xlim(0,13.4); ax.set_ylim(0,9.8); ax.axis('off')
ax.add_patch(FancyBboxPatch((0.4,6.8),12.6,2.3,boxstyle='round,pad=0.02,rounding_size=0.15',fc=GREY,ec=EDGE,zorder=1))
ax.text(0.7,8.8,'Offline: training on simulated datasets',fontsize=10,weight='bold',va='center')
for i,(t,s) in enumerate([('Simulated logs','VeReMi Extension,\nVeReMi NextGen'),('Harmonisation','one message schema\nfor both datasets'),('Feature extraction','21 receiver-side\nfeatures'),('HGB training','thresholds set on\nvalidation data')]):
    box(ax,0.7+i*3.08,7.0,2.8,1.35,t,s,fc=GREY)
    if i: arr(ax,(0.7+i*3.08-0.28,7.67),(0.7+i*3.08,7.67))
ax.add_patch(FancyBboxPatch((0.4,0.25),12.6,6.0,boxstyle='round,pad=0.02,rounding_size=0.15',fc='white',ec=EDGE,zorder=1))
ax.text(0.7,5.95,'On board: every received beacon, one CPU core',fontsize=10,weight='bold',va='center')
for i,(t,s) in enumerate([('V2X receiver','BSM or CAM with\na pseudonym'),('Receiver state','pseudonym history,\n1 s and 5 s windows'),('Feature extractor','kinematic, history,\nneighbourhood'),('Decision engine','HGB, 244 trees\n0.74 ms per beacon')]):
    last=i==3; box(ax,0.7+i*3.08,4.1,2.8,1.35,t,s,fc='#e4effb' if last else 'white',ec=ACC if last else EDGE,lw=2 if last else 1.2)
    if i: arr(ax,(0.7+i*3.08-0.28,4.77),(0.7+i*3.08,4.77))
arr(ax,(11.33,7.0),(11.33,5.45)); ax.text(11.2,6.5,'deploy model and threshold',ha='right',fontsize=8.5,color='#555')
ax.add_patch(Polygon([[11.33,3.9],[12.6,3.05],[11.33,2.2],[10.06,3.05]],fc='white',ec=EDGE,lw=1.2,zorder=3)); ax.text(11.33,3.05,'score above\nthreshold?',ha='center',va='center',fontsize=8.5,zorder=4)
arr(ax,(11.33,4.1),(11.33,3.9))
box(ax,6.86,2.38,2.8,1.35,'Aggregate alarms','per pseudonym,\nmessages or receivers'); arr(ax,(10.06,3.05),(9.66,3.05)); ax.text(9.95,3.25,'yes',fontsize=8.5,color='#555')
box(ax,3.78,2.38,2.8,1.35,'Report sender','misbehaviour report\nvia RSU to the MA'); arr(ax,(6.86,3.05),(6.58,3.05))
box(ax,9.93,0.55,2.8,1.15,'Accept message','pass to applications'); arr(ax,(11.33,2.2),(11.33,1.7)); ax.text(11.45,1.9,'no',fontsize=8.5,color='#555')
save(fig,'F01_architecture')
# Fig10 hierarchy
fig,ax=plt.subplots(figsize=(10,5.8)); ax.set_xlim(0,13.4); ax.set_ylim(0,7.8); ax.axis('off')
box(ax,4.4,6.6,4.6,0.85,'Features of one received message',fs=10)
cols=[('Kinematic (5)','Is one message\nphysically plausible?',['spd: claimed speed','acc: claimed acceleration','pos_noise: position error','spd_noise: speed error','dist_rcv: distance to receiver'],False),
      ('Pseudonym history (9)',"Are one pseudonym's messages\nconsistent with each other?",['beacon_dt','pos_jump','pos_pred_err','spd_change_rate','hed_motion_err','msg_idx','pseudo_age','is_new_pseudo','first_seen_dist'],True),
      ('Neighbourhood (7)','Do several identities\nappear together?',['n_pseudo_1s','n_near5','n_near20','min_dist_other','new_pseudo_5s','new_pseudo_frac_5s','n_similar_spd_near'],False)]
ax.plot([2.25,11.15],[5.95,5.95],color=EDGE,lw=1.2); ax.plot([6.7,6.7],[6.6,5.95],color=EDGE,lw=1.2)
for i,(t,s,fs_,hl) in enumerate(cols):
    x=0.35+i*4.45; ax.plot([x+1.9,x+1.9],[5.95,5.45],color=EDGE,lw=1.2)
    box(ax,x,4.15,3.8,1.3,t,s,fc='#e4effb' if hl else 'white',ec=ACC if hl else EDGE,lw=2 if hl else 1.2,fs=10,sfs=8.3)
    ax.plot([x+1.9,x+1.9],[4.15,3.75],color=EDGE,lw=1.2)
    ax.add_patch(FancyBboxPatch((x,0.35),3.8,3.4,boxstyle='round,pad=0.02,rounding_size=0.12',fc='white',ec=ACC if hl else EDGE,lw=2 if hl else 1.2))
    for j,f in enumerate(fs_): ax.text(x+0.25,3.42-j*0.34,f,fontsize=8.3,va='center',family='DejaVu Sans Mono' if ':' not in f else 'DejaVu Sans')
save(fig,'F10_feature_hierarchy')
# Fig12 pipeline
fig,ax=plt.subplots(figsize=(10,3.9)); ax.set_xlim(0,13.4); ax.set_ylim(0,5.2); ax.axis('off')
box(ax,0.3,3.3,2.9,1.4,'VeReMi Extension','LuST, F2MD\n8 Sybil subsets',align='left',sfs=8.3)
box(ax,0.3,1.35,2.9,1.4,'VeReMi NextGen','InTAS, own simulator\n4 scenarios',align='left',sfs=8.3)
box(ax,3.75,2.3,2.8,1.5,'Harmonise','one message schema\ncompass heading\ntimes in seconds',align='left',sfs=8.3)
box(ax,7.0,2.3,2.8,1.5,'Features','21 per received message\nkinematic, history,\nneighbourhood',align='left',sfs=8.3)
box(ax,10.25,2.3,2.8,1.5,'Detector','HGB or RF\n1%-FPR threshold\nalarm per message',fc='#e4effb',ec=ACC,lw=2,align='left',sfs=8.3)
ax.plot([3.2,3.45,3.45,3.2],[4.0,4.0,2.05,2.05],color=EDGE,lw=1.2); arr(ax,(3.45,3.05),(3.75,3.05)); arr(ax,(6.55,3.05),(7.0,3.05)); arr(ax,(9.8,3.05),(10.25,3.05)); arr(ax,(8.4,2.3),(8.4,1.35))
ax.add_patch(FancyBboxPatch((3.75,0.25),9.3,1.05,boxstyle='round,pad=0.02,rounding_size=0.12',fc=GREY,ec=EDGE,lw=1.2)); ax.text(8.4,0.77,'Evaluation E1–E8: sender-grouped splits, thresholds from validation data',ha='center',va='center',fontsize=9)
save(fig,'F12_pipeline')
# Fig16 ROC
s=open('/home/claude/roc_code_final.json').read(); rows=re.findall(r"\{'slug':'([a-z-]+)','fpr':([\d.e-]+),'tpr':([\d.]+)\}",s)
R=pd.DataFrame(rows,columns=['slug','fpr','tpr']).astype({'fpr':float,'tpr':float})
lab={'ext-ext':('Extension → Extension',C['E1'],'-'),'ng-ng':('NextGen → NextGen',C['E3'],'-'),'ext-ng':('Extension → NextGen',C['E4a'],'--'),'ng-ext':('NextGen → Extension',C['E4b'],'--')}
fig,ax=plt.subplots(figsize=(5.4,3.6))
for k,(l,c,ls) in lab.items():
    q=R[R.slug==k]; ax.plot(q.fpr,q.tpr,ls,color=c,lw=1.6,label=l)
ax.axvline(0.01,color='#888',ls=':',lw=0.9); ax.text(0.0105,0.03,'1% FPR',fontsize=7.5,color='#555')
ax.set_xscale('log'); ax.set_xlim(1e-4,1); ax.set_ylim(0,1.02); ax.set_xlabel('false-positive rate (log)'); ax.set_ylabel('true-positive rate'); ax.legend(frameon=False,fontsize=7.5,loc='upper left')
save(fig,'F16_roc')
# Fig17 group importance
fig,ax=plt.subplots(figsize=(5.4,2.8)); g=['Pseudonym history','Neighbourhood','Kinematic']; e=[0.337,0.081,0.028]; n=[0.402,0.012,0.0004]
y=np.arange(3)[::-1]; ax.barh(y+0.18,e,0.34,color='#9e9e93',label='Extension-trained, Extension test'); ax.barh(y-0.18,n,0.34,color=ACC,label='NextGen-trained, NextGen test')
for yy,v in zip(y,e): ax.text(v+0.005,yy+0.18,f'{v:.3f}',va='center',fontsize=7.5)
for yy,v in zip(y,n): ax.text(v+0.005,yy-0.18,'<0.001' if v<0.001 else f'{v:.3f}',va='center',fontsize=7.5)
ax.set_yticks(y); ax.set_yticklabels(g); ax.set_xlim(0,0.48); ax.set_xlabel('drop in ROC AUC when the group is permuted'); ax.legend(frameon=False,fontsize=7.5,loc='lower right')
save(fig,'F17_group_importance')
# Fig20 LOTO dumbbell
lo=pd.read_csv('/home/claude/repo/results/main/final_loto.csv'); f1=lambda t,m,ft: float(lo[(lo.held_out==t)&(lo.model==m)&(lo.feats==ft)].f1.iloc[0].split(' ±')[0])
types=['GridSybil','DataReplaySybil','DoSDisruptiveSybil','DoSRandomSybil']
fig,ax=plt.subplots(figsize=(5.4,2.9)); y=np.arange(4)[::-1]
for yy,t in zip(y,types):
    s_,u,r=f1(t,'HGB','seen'),f1(t,'HGB','unseen'),f1(t,'rule','is_new_pseudo')
    ax.plot([u,s_],[yy,yy],color='#c8c7be',lw=2,zorder=1); ax.scatter(s_,yy,s=45,color='#9e9e93',zorder=3); ax.scatter(u,yy,s=45,color=ACC,zorder=3); ax.plot([r,r],[yy-0.22,yy+0.22],color='#555',lw=1.6)
    ax.text(s_,yy+0.25,f'{s_:.1f}',ha='center',fontsize=7.5,color='#555'); ax.text(u,yy-0.38,f'{u:.1f}',ha='center',fontsize=7.5,color=ACC,weight='bold')
ax.set_yticks(y); ax.set_yticklabels(types); ax.set_xlim(0,102); ax.set_ylim(-0.7,3.6); ax.set_xlabel('F1 (%)')
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([],[],marker='o',ls='',color='#9e9e93',label='seen in training'),Line2D([],[],marker='o',ls='',color=ACC,label='unseen (held out)'),Line2D([],[],marker='|',ls='',color='#555',ms=10,label='new-pseudonym rule')],frameon=False,fontsize=7.5,loc='upper center',bbox_to_anchor=(0.45,1.2),ncol=3)
save(fig,'F20_loto')
# Fig21 precision vs prevalence
P=[('E1 Ext 0709',0.0099,0.8322,C['E1'],'-'),('E2 Ext 1416→0709',0.0165,0.8663,C['E2'],'-'),('E3 NG split',0.0106,0.9982,C['E3'],'-'),('E4a Ext→NG',0.016,0.686,C['E4a'],'-'),('E4b NG→Ext',0.0258,0.3436,C['E4b'],'-'),('Rule, Ext 0709',0.0532,0.5683,C['rule'],'--')]
pi=np.logspace(-3,np.log10(0.5),200); fig,ax=plt.subplots(figsize=(5.4,3.4))
for l,fp,tp,c,ls in P: ax.plot(pi*100,tp*pi/(tp*pi+fp*(1-pi))*100,ls,color=c,lw=1.6,label=l)
ax.axvline(1,color='#888',ls=':',lw=0.9); ax.text(1.05,3,'1% Sybil traffic',fontsize=7.5,color='#555')
ax.set_xscale('log'); ax.set_xlabel('Sybil prevalence π (%, log)'); ax.set_ylabel('precision of alarms (%)'); ax.set_ylim(0,102); ax.legend(frameon=False,fontsize=7.3,loc='lower right')
save(fig,'F21_precision_prevalence')
# Fig24 phantom bars
cats=['None','5%','10%','20%','10% drift only']; p2=[5.5,34.0,37.8,38.6,35.5]; p1=[2.4,56.0,66.1,72.3,69.1]; fa=[0.05,10.8,17.7,15.8,18.7]
fig,ax=plt.subplots(figsize=(6.4,3.2)); x=np.arange(5); w=0.26
for k,(v,c,l) in enumerate([(p2,'#4a8fe0','Unseen GridSybil recall, within Extension (P2)'),(p1,'#ee7f50','GridSybil recall, NextGen → Extension (P1)'),(fa,'#e48c8c','False alarms on genuine messages with history (P1)')]):
    ax.bar(x+(k-1)*w,v,w,color=c,label=l)
    for xx,vv in zip(x,v): ax.text(xx+(k-1)*w,vv+1,'<0.1' if vv<0.1 else f'{vv:.1f}',ha='center',fontsize=6.5)
ax.set_xticks(x); ax.set_xticklabels(cats); ax.set_xlabel('share of genuine training vehicles given synthetic phantoms'); ax.set_ylabel('%'); ax.set_ylim(0,85); ax.legend(frameon=False,fontsize=7,loc='upper left')
save(fig,'F24_phantom_bars')
print('ok')
