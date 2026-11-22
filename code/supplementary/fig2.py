import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch, Rectangle, Polygon
plt.rcParams.update({'font.family':'DejaVu Sans','pdf.fonttype':42,'ps.fonttype':42})
NAVY='#163d6b'; BLUE='#1f6fd1'; RED='#d42020'; GREEN='#1e7a2e'
fig,ax=plt.subplots(figsize=(14,7.8)); ax.set_xlim(0,18); ax.set_ylim(0,10); ax.axis('off')
def box(x,y,w,h,fc,ec,lw=1.5,r=0.15):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0.02,rounding_size={r}',fc=fc,ec=ec,lw=lw,zorder=3))
def arr(a,b,c,ls='-',lw=2,rad=0,ms=16,z=5,style='-|>'):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle=style,mutation_scale=ms,color=c,lw=lw,ls=ls,connectionstyle=f'arc3,rad={rad}',zorder=z))
def car(x,y,c,ghost=False,s=1.0):
    w,h=1.1*s,0.38*s
    if ghost:
        ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.02,rounding_size=0.12',fc='#f8dcdc',ec=RED,lw=1.8,ls=(0,(3,2)),zorder=4))
    else:
        ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.02,rounding_size=0.1',fc=c,ec='#222',lw=0.8,zorder=4))
        ax.add_patch(Polygon([[x-0.3*s,y+h/2],[x-0.18*s,y+h/2+0.22*s],[x+0.22*s,y+h/2+0.22*s],[x+0.34*s,y+h/2]],fc=c,ec='#222',lw=0.8,zorder=4))
        ax.add_patch(Rectangle((x-0.16*s,y+h/2+0.03*s),0.16*s,0.15*s,fc='#cfe3f7',ec='none',zorder=5))
        ax.add_patch(Rectangle((x+0.03*s,y+h/2+0.03*s),0.16*s,0.15*s,fc='#cfe3f7',ec='none',zorder=5))
    for dx in (-0.3*s,0.3*s): ax.add_patch(Circle((x+dx,y-h/2),0.12*s,fc='white' if ghost else '#222',ec=RED if ghost else '#222',lw=1.5,zorder=6))
def callout(x,y,t,tx,ty,ec=NAVY,fc='#e6f1fb',col=NAVY):
    ax.annotate(t,(tx,ty),(x,y),ha='center',va='center',fontsize=11,weight='bold',color=col,zorder=8,
        bbox=dict(boxstyle='round,pad=0.3',fc=fc,ec=ec,lw=1.3),arrowprops=dict(arrowstyle='-',color=ec,lw=1.3))
def tower(x,y):
    ax.add_patch(Polygon([[x-0.35,y],[x+0.35,y],[x,y+1.4]],fc='none',ec=GREEN,lw=2.2,zorder=3))
    for k in (0.35,0.7,1.0): ax.plot([x-0.35*(1-k/1.4),x+0.35*(1-k/1.4)],[y+k,y+k],color=GREEN,lw=1.6,zorder=3)
    for r in (0.25,0.45): 
        for sgn in (-1,1): ax.add_patch(matplotlib.patches.Arc((x,y+1.45),2*r,2*r,theta1=(60 if sgn>0 else 100),theta2=(80 if sgn>0 else 120),color=GREEN,lw=2))
    ax.add_patch(matplotlib.patches.Arc((x,y+1.45),0.6,0.6,theta1=-40,theta2=40,color=GREEN,lw=2)); ax.add_patch(matplotlib.patches.Arc((x,y+1.45),0.6,0.6,theta1=140,theta2=220,color=GREEN,lw=2))
    ax.add_patch(Circle((x,y+1.45),0.07,color=GREEN))
    box(x-0.6,y-0.75,1.2,0.6,'#e6f1fb',NAVY); ax.text(x,y-0.45,'RSU',ha='center',va='center',fontsize=14,weight='bold',color=NAVY,zorder=6)
# title + beacon box
box(0.3,9.3,7.6,0.6,NAVY,NAVY); ax.text(4.1,9.6,'V2V / V2I beacons (CAM/BSM, 1–10 Hz)',ha='center',va='center',fontsize=14,weight='bold',color='white',zorder=6)
box(0.3,8.45,6.2,0.55,'#eef5fc','#7fa7d4'); ax.text(3.4,8.72,'Beacon: pseudonym, time, position, speed, heading',ha='center',va='center',fontsize=9.8,zorder=6)
# MA
box(7.3,7.8,5.0,1.25,'#fff2cc','#7f6000',lw=2); ax.text(9.8,8.42,'Misbehaviour Authority (MA)\n+ pseudonym PKI',ha='center',va='center',fontsize=15,weight='bold',zorder=6)
tower(2.6,6.3); tower(16.4,6.3)
arr((3.05,7.85),(7.3,8.3),NAVY,ls='--',style='<|-|>'); arr((15.95,7.85),(12.3,8.3),NAVY,ls='--',style='<|-|>')
ax.text(4.9,7.45,'RSU ↔ MA\n(secure link)',ha='center',fontsize=10.5,color=NAVY); ax.text(13.9,7.45,'RSU ↔ MA\n(secure link)',ha='center',fontsize=10.5,color=NAVY)
# road
ax.add_patch(Rectangle((0.3,3.3),17.4,2.15,fc='#d6d6d6',ec='none',zorder=1)); ax.plot([0.3,17.7],[4.37,4.37],color='white',lw=3,ls=(0,(6,4)),zorder=2)
# vehicles
G=[(1.6,4.85),(4.6,3.8),(16.0,3.8)]; RX=(8.6,4.85); ATT=(11.3,3.8); PH=[(12.9,4.85),(14.5,4.85),(13.6,3.8)]
for p in G: car(*p,BLUE)
car(*RX,BLUE); car(*ATT,RED)
for p in PH: car(*p,None,ghost=True)
callout(1.0,6.15,'Genuine\nvehicle',1.5,5.2); callout(4.6,2.75,'Genuine\nvehicle',4.6,3.5); callout(16.0,2.75,'Genuine\nvehicle',16.0,3.5)
callout(7.6,6.35,'Receiver\n(genuine, runs MDS)',8.5,5.25,ec=GREEN,fc='#e2f0d9',col=GREEN)
callout(11.6,2.75,'Attacker (insider,\nvalid certificates)',11.3,3.5,ec=RED,fc='#fdeaea',col=RED)
callout(13.0,6.4,'Sybil pseudonyms\n(phantom vehicles)',13.4,5.15,ec=RED,fc='#fdeaea',col=RED)
# genuine past trajectory into receiver
arr((6.6,4.7),(7.95,4.8),BLUE,rad=0.25)
# claimed trajectory of phantoms
arr((12.35,5.1),(15.3,5.1),RED,rad=-0.2)
# beacons heard by receiver
for p in [G[0],G[1]]: arr((p[0]+0.6,p[1]+0.1),(RX[0]-0.6,RX[1]+0.05),BLUE,ls=':',lw=1.5,rad=0.1,ms=11)
for p in [ATT]+PH[:1]+PH[2:]: arr((p[0]-0.55,p[1]+0.05),(RX[0]+0.6,RX[1]-0.05),RED,ls=':',lw=1.5,rad=-0.1,ms=11)
# report from receiver to RSU
arr((9.0,5.25),(15.75,5.95),GREEN,ls='--',lw=2.2,rad=-0.25)
ax.text(10.9,5.62,'misbehaviour report',fontsize=10.5,color=GREEN,ha='center',style='italic',zorder=9)
# MDS box
box(5.9,0.15,5.85,1.2,'#e2f0d9',GREEN,lw=2); ax.text(8.82,0.75,'On-board MDS:\nReceiver-side features → HGB → Alarm',ha='center',va='center',fontsize=12,weight='bold',zorder=6)
arr((8.6,1.35),(8.6,4.4),GREEN,lw=2.2)
# abbreviations
box(0.3,0.15,5.4,2.05,'#eef5fc','#7fa7d4')
ab=[('CAM','Cooperative Awareness Message'),('BSM','Basic Safety Message'),('V2V/V2I','Vehicle-to-vehicle / -infrastructure'),('RSU','Roadside unit'),('MA','Misbehaviour authority'),('PKI','Public key infrastructure'),('MDS','Misbehaviour detection system'),('HGB','Histogram-based gradient boosting')]
for i,(a,b) in enumerate(ab):
    y=2.0-i*0.235; ax.text(0.45,y,a,fontsize=9,weight='bold',va='center',zorder=6); ax.text(1.5,y,': '+b,fontsize=9,va='center',zorder=6)
# legend
box(11.9,0.15,5.8,1.75,'white',NAVY)
L=[(BLUE,'-','Genuine trajectory (past)'),(RED,'-','Claimed trajectory of phantoms'),(BLUE,':','Beacon heard (genuine)'),(RED,':','Beacon heard (attacker / phantom)'),(GREEN,'--','Misbehaviour report via RSU → MA')]
for i,(c,ls,t) in enumerate(L):
    y=1.65-i*0.31; arr((12.05,y),(13.0,y),c,ls=ls,lw=2,ms=12,z=7); ax.text(13.15,y,t,fontsize=9.5,va='center',zorder=7)
fig.savefig('/home/claude/an/figs/S1_system_model.png',dpi=600,bbox_inches='tight'); fig.savefig('/home/claude/an/figs/S1_system_model.pdf',bbox_inches='tight')
fig.savefig('/home/claude/an/web/S1_system_model.png',dpi=200,bbox_inches='tight')
