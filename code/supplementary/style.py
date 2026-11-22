import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':10,'axes.labelsize':9,'legend.fontsize':8,
 'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':0.3,'grid.linewidth':0.5,'savefig.dpi':600,'figure.dpi':150})
C=dict(E1='#1f77b4',E2='#17becf',E3='#2ca02c',E4a='#ff7f0e',E4b='#d62728',rule='#7f7f7f')
M=dict(HGB='#1f77b4',RF='#2ca02c',LSTM='#9467bd',rule='#7f7f7f',LR='#8c564b',NB='#e377c2',DT='#bcbd22',kNN='#17becf',MLP='#ff7f0e',ET='#7f7f7f')
T=dict(DataReplaySybil='#1f77b4',DoSDisruptiveSybil='#ff7f0e',DoSRandomSybil='#2ca02c',GridSybil='#d62728',trafficCongestionSybil='#9467bd')
LAB=dict(E1='E1 Ext in-density',E2='E2 Ext 0709→1416',E3='E3 NG official split',E4a='E4a Ext→NG',E4b='E4b NG→Ext')
def save(fig,name): fig.savefig(f'/home/claude/an/figs/{name}.png',bbox_inches='tight',dpi=600); fig.savefig(f'/home/claude/an/figs/{name}.pdf',bbox_inches='tight'); fig.savefig(f'/home/claude/an/figs/{name}.svg',bbox_inches='tight'); plt.close(fig)
plt.rcParams.update({'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none'})
import numpy as _np
from matplotlib.axes import Axes as _Ax
_orig_imshow=_Ax.imshow
def _vimshow(self,A,cmap=None,vmin=None,vmax=None,aspect=None,**k):
    A=_np.asarray(A)
    if A.ndim!=2: return _orig_imshow(self,A,cmap=cmap,vmin=vmin,vmax=vmax,aspect=aspect,**k)
    m=self.pcolormesh(_np.arange(A.shape[1]+1)-0.5,_np.arange(A.shape[0]+1)-0.5,A,cmap=cmap,vmin=vmin,vmax=vmax,edgecolors='face',linewidth=0)
    self.set_xlim(-0.5,A.shape[1]-0.5); self.set_ylim(A.shape[0]-0.5,-0.5)
    if aspect!='auto': self.set_aspect('equal')
    return m
_Ax.imshow=_vimshow
from matplotlib.figure import Figure as _Fig
_orig_cb=_Fig.colorbar
def _cb(self,*a,**k):
    c=_orig_cb(self,*a,**k)
    try: c.solids.set_rasterized(False)
    except Exception: pass
    return c
_Fig.colorbar=_cb
plt.colorbar=lambda *a,**k: plt.gcf().colorbar(*a,**k)
