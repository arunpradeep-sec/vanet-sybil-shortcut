exec(open('/home/claude/an/style.py').read())
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle, Polygon
import numpy as np
def box(ax,x,y,w,h,t,fc='#eef3fb',ec='#1f4e79',fs=8,bold=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02,rounding_size=0.08',fc=fc,ec=ec,lw=1))
    ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=fs,weight='bold' if bold else 'normal',wrap=True)
def arr(ax,a,b,c='#333',ls='-',lw=1.1,txt=None,rad=0):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=9,color=c,lw=lw,ls=ls,connectionstyle=f'arc3,rad={rad}'))
    if txt: ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+0.12,txt,fontsize=7,ha='center',color=c)
def car(ax,x,y,c='#1f77b4',lab=None,ghost=False):
    ax.add_patch(FancyBboxPatch((x-0.28,y-0.13),0.56,0.26,boxstyle='round,pad=0.01,rounding_size=0.06',fc='none' if ghost else c,ec=c,lw=1.2,ls='--' if ghost else '-'))
    for dx in (-0.16,0.16): ax.add_patch(Circle((x+dx,y-0.15),0.05,fc='#333' if not ghost else 'none',ec='#333'))
    if lab: ax.text(x,y+0.24,lab,ha='center',fontsize=6.5,color=c)
# ---- Fig S1: VANET system model + threat model
fig,ax=plt.subplots(figsize=(7.2,3.6)); ax.set_xlim(0,12); ax.set_ylim(0,6); ax.axis('off')
ax.add_patch(Rectangle((0,1.2),12,1.6,fc='#d9d9d9',ec='none')); ax.plot([0,12],[2,2],'w--',lw=1.2)
box(ax,5.6,4.6,2.6,0.9,'Misbehaviour Authority (MA)\n+ Pseudonym CA',fc='#fff2cc',ec='#7f6000',fs=7.5)
for xr in (2.0,9.6):
    ax.add_patch(Polygon([[xr-0.2,2.85],[xr+0.2,2.85],[xr,4.1]],fc='#c5e0b4',ec='#385723')); ax.text(xr,4.25,'RSU',ha='center',fontsize=7.5)
    arr(ax,(xr,4.3),(5.6 if xr<6 else 8.2,4.95),c='#7f6000',ls='--')
for i,x in enumerate([1.0,3.4,6.2,10.8]): car(ax,x,2.45 if i%2==0 else 1.55,'#1f77b4',lab='genuine')
car(ax,7.8,1.55,'#c00000'); ax.text(7.8,1.0,'attacker',fontsize=6.5,color='#c00000',ha='center')
for k,(gx,gy) in enumerate([(8.9,2.45),(9.3,1.55),(10.0,2.45)]): car(ax,gx,gy,'#c00000',ghost=True)
ax.text(10.4,0.95,'Sybil pseudonyms (phantom vehicles)',fontsize=7,color='#c00000',ha='center')
for x in (6.2,): 
    for dx,c in [(-0.8,'#1f77b4'),(1.6,'#c00000')]: arr(ax,(x+dx,2.0+0.3),(x,2.3),c=c,rad=0.3)
box(ax,4.4,0.1,3.6,0.7,'On-board MDS: receiver-side features → HGB → alarm',fc='#e2f0d9',ec='#385723',fs=7.5)
arr(ax,(6.2,1.0),(6.2,2.2),c='#385723'); arr(ax,(8.0,0.6),(9.6,2.85),c='#385723',ls=':'); ax.text(9.9,0.35,'misbehaviour report → RSU → MA',fontsize=6.5,color='#385723')
ax.text(0.1,5.6,'V2V / V2I beacons (CAM/BSM, 1–10 Hz)',fontsize=8,weight='bold'); ax.text(0.1,4.85,'Beacon: pseudonym, time,\nposition, speed, heading',fontsize=7)
save(fig,'S1_system_model')
# ---- Fig S2: attack behaviours (5 panels)
fig,axs=plt.subplots(1,5,figsize=(7.4,1.9))
names=['DataReplaySybil','DoSRandomSybil','DoSDisruptiveSybil','GridSybil','trafficCongestionSybil (NG)']
r=np.random.default_rng(3)
for ax,n in zip(axs,names):
    ax.set_xlim(0,10); ax.set_ylim(0,6); ax.set_xticks([]); ax.set_yticks([]); ax.grid(False); ax.set_title(n.replace('Sybil','\nSybil'),fontsize=7.5)
    ax.add_patch(Rectangle((0,2),10,2,fc='#eeeeee',ec='none'))
    t=np.linspace(1,9,9)
    ax.plot(t,np.full(9,3.5),'o-',ms=2.5,c='#1f77b4',lw=0.7)
    if n.startswith('DataReplay'):
        ax.plot(t[:6]+0.0,np.full(6,2.5),'s--',ms=2.5,c='#c00000',lw=0.7); ax.annotate('',xy=(4,2.6),xytext=(2,3.4),arrowprops=dict(arrowstyle='->',color='#c00000',lw=0.6))
        ax.text(5,0.8,'replays a victim\'s\nbeacons, new pseudonym',fontsize=6,ha='center')
    elif n.startswith('DoSRandom'):
        ax.scatter(r.uniform(0.5,9.5,14),r.uniform(2.2,5.8,14),s=5,c='#c00000',marker='s'); ax.text(5,0.3,'high rate, random\npositions & pseudonyms',fontsize=6,ha='center')
    elif n.startswith('DoSDisruptive'):
        ax.scatter(t+0.3,np.full(9,2.6)+r.normal(0,0.1,9),s=5,c='#c00000',marker='s'); ax.text(5,0.6,'high rate, replays\nneighbours\' data',fontsize=6,ha='center')
    elif n.startswith('Grid'):
        for gx in (4,5.5,7):
            for gy in (2.4,3.0,3.6): ax.scatter(gx,gy,s=7,c='#c00000',marker='s')
        ax.text(5,0.6,'phantom grid that moves\nwith the attacker (jam)',fontsize=6,ha='center')
    else:
        for gx in np.linspace(3,8,6): ax.scatter(gx,2.5+r.normal(0,.1),s=7,c='#c00000',marker='s')
        ax.text(5,0.6,'slow phantom queue\nsignals congestion',fontsize=6,ha='center')
fig.text(0.5,-0.04,'blue: genuine trajectory   red squares: beacons from Sybil pseudonyms',ha='center',fontsize=7)
save(fig,'S2_attack_types')
# ---- Fig S3: evaluation protocol matrix
fig,ax=plt.subplots(figsize=(7.0,2.9)); ax.set_xlim(0,14); ax.set_ylim(0,6.2); ax.axis('off')
box(ax,0.2,4.3,2.6,1.2,'VeReMi Ext\n0709',fc='#deebf7',fs=8); box(ax,0.2,2.6,2.6,1.2,'VeReMi Ext\n1416',fc='#deebf7',fs=8)
box(ax,0.2,0.4,2.6,1.6,'VeReMi NextGen\nTrain | Val | Test',fc='#e5f5e0',ec='#2ca02c',fs=8)
items=[('E1  5-fold by sender, per density',C['E1'],5.1),('E2  0709 ↔ 1416',C['E2'],4.45),('E3  NG Train→Test (new area)',C['E3'],3.8),
('E4a Ext → NG Test',C['E4a'],3.15),('E4b NG Train → Ext',C['E4b'],2.5),('E5  rule "new pseudonym = Sybil"',C['rule'],1.85),
('E6/E7 feature ablation, shortcut fixes','#555',1.2),('E8  leave-one-Sybil-type-out','#9467bd',0.55)]
for t,c,y in items: box(ax,4.0,y-0.27,5.0,0.54,t,fc='white',ec=c,fs=7.2)
box(ax,10.2,3.3,3.5,1.9,'Metrics\nF1, MCC, AUC,\nTPR@1%FPR,\nprecision@prevalence',fc='#fff2cc',ec='#7f6000',fs=7.5)
box(ax,10.2,0.6,3.5,2.0,'E9 phantoms, LSTM,\nRaspberry Pi latency,\nmodel zoo,\nshift & delay analyses',fc='#fbe5d6',ec='#c55a11',fs=7.5)
for y in (4.9,3.2): arr(ax,(2.8,y),(4.0,4.6),c='#888')
arr(ax,(2.8,1.2),(4.0,3.4),c='#888'); arr(ax,(9.0,3.5),(10.2,4.2),c='#888'); arr(ax,(9.0,1.5),(10.2,1.6),c='#888')
save(fig,'S3_protocol_matrix')
# ---- Fig S4: online feature state machine per pseudonym
fig,ax=plt.subplots(figsize=(7.2,2.6)); ax.set_xlim(0,14); ax.set_ylim(0,5); ax.axis('off')
box(ax,0.2,2.0,2.2,1.0,'beacon\n(p, t, x, v, θ)',fc='#deebf7')
box(ax,3.2,3.3,2.8,1.2,'pseudonym table\nlast msg, first-seen,\ncount, age',fc='#e5f5e0',ec='#2ca02c',fs=7.5)
box(ax,3.2,0.5,2.8,1.2,'1 s / 5 s windows\n(deques + counters)',fc='#e5f5e0',ec='#2ca02c',fs=7.5)
box(ax,6.9,3.6,2.4,0.8,'HIST (9)',fc='#fde0dd',ec='#c51b8a'); box(ax,6.9,2.1,2.4,0.8,'KIN (5)',fc='#deebf7'); box(ax,6.9,0.6,2.4,0.8,'NEIGH (7)',fc='#fff2cc',ec='#7f6000')
box(ax,10.0,2.0,1.6,1.0,'HGB\n244 trees',fc='#fbe5d6',ec='#c55a11'); box(ax,12.2,2.0,1.6,1.0,'p ≥ τ ?\nalarm',fc='#f2f2f2',ec='#333')
arr(ax,(2.4,2.5),(3.2,3.9)); arr(ax,(2.4,2.5),(3.2,1.1)); arr(ax,(2.4,2.5),(6.9,2.5))
arr(ax,(6.0,3.9),(6.9,4.0)); arr(ax,(6.0,1.1),(6.9,1.0))
for y in (4.0,2.5,1.0): arr(ax,(9.3,y),(10.0,2.5))
arr(ax,(11.6,2.5),(12.2,2.5)); arr(ax,(4.6,3.3),(4.6,1.7),c='#2ca02c',ls=':',txt='update')
ax.text(10.8,1.4,'τ from validation\n(F1-opt or 1% FPR)',fontsize=6.5,ha='center')
save(fig,'S4_online_state')
print('ok')
