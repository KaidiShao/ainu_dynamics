import pathlib,json,sys,os
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'47_三维头模结构试验_2026-10-12/tools/python'))
os.environ['MPLCONFIGDIR']=str(R)
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
d=json.loads((R/'r9-inspection.json').read_text());V=np.array(d['vertices']);F=d['faces']
edges=set()
for f in F:
 for a,b in zip(f,f[1:]+f[:1]):edges.add(tuple(sorted((a,b))))
for tag,bounds in [('eye',(14,50,-17,22)),('mouth',(0,33,-85,-44)),('nose',(0,25,-47,12))]:
 x0,x1,z0,z1=bounds;ids=set(np.where((V[:,0]>x0)&(V[:,0]<x1)&(V[:,2]>z0)&(V[:,2]<z1)&(V[:,1]<9))[0])
 fig,ax=plt.subplots(figsize=(16,12))
 for a,b in edges:
  if a in ids and b in ids:ax.plot(V[[a,b],0],V[[a,b],2],color='#cccccc',lw=.7)
 for i in ids:
  ax.scatter(V[i,0],V[i,2],c=[[min(1,max(0,(V[i,1]+50)/60)),.3,.6]],s=16)
  ax.annotate(str(i),V[i,[0,2]],fontsize=7)
 ax.set_aspect('equal');ax.set_title(tag+' X/Z control topology');ax.set_xlim(x0,x1);ax.set_ylim(z0,z1);fig.savefig(R/f'renders/topology-r10-{tag}.png',dpi=120);plt.close(fig)
 print(tag,[(int(i),V[i].round(2).tolist()) for i in sorted(ids)])
