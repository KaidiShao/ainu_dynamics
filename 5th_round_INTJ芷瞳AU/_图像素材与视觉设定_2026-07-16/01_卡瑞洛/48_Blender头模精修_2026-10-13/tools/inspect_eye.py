import json,pathlib,sys,os
R=pathlib.Path(__file__).resolve().parents[1];OLD=R.parent/'47_三维头模结构试验_2026-10-12'
sys.path.insert(0,str(OLD/'tools/python'))
os.environ['MPLCONFIGDIR']=str(R/'tools/mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
d=json.loads((R/'base-geometry.json').read_text());V=np.array(d['vertices'])*63/(35.8766*2)
fig,ax=plt.subplots(figsize=(13,8))
for f in d['faces']:
 p=V[f]
 if np.all(p[:,0]>12) and np.all(p[:,0]<53) and np.all(p[:,2]>-15) and np.all(p[:,2]<18) and np.all(p[:,1]<20):
  pp=np.vstack((p,p[0]));ax.plot(pp[:,0],pp[:,2],'-',color='#bbb',lw=.7)
for i,p in enumerate(V):
 if 13<p[0]<51 and -12<p[2]<16 and p[1]<12:
  ax.scatter(p[0],p[2],c=p[1],vmin=-15,vmax=12,cmap='viridis',s=18);ax.text(p[0]+.2,p[2],str(i),fontsize=7)
ax.set_aspect('equal');ax.grid();ax.set_xlabel('X');ax.set_ylabel('Z');fig.savefig(R/'renders/eye-topology.png',dpi=140,bbox_inches='tight')
print('saved')

