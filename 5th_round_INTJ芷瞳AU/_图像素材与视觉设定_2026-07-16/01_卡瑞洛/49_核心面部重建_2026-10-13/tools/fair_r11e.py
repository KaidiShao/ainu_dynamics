import pathlib,json,sys,collections
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'47_三维头模结构试验_2026-10-12/tools/python'));import numpy as np
from scipy.sparse import coo_matrix
D=json.loads((R/'face-r11d.json').read_text());V=np.array(D['vertices']);M=np.array(D['M']);F=D['faces'];original=V.copy()
adj=collections.defaultdict(set)
for f in F:
 for a,b in zip(f,f[1:]+f[:1]):adj[a].add(b);adj[b].add(a)
row=[];col=[];dat=[]
for i,nei in adj.items():
 for j in nei:row.append(i);col.append(j);dat.append(1/len(nei))
A=coo_matrix((dat,(row,col)),shape=(len(V),len(V))).tocsr()
w=np.zeros(len(V))
for p in D['patches']:
 c=np.array(D['eyes'][0 if p['side']<0 else 1]);r=np.sqrt(((V[:,0]-c[0])/32)**2+((V[:,2]-2)/31)**2)
 influence=np.clip((1.35-r)/.6,0,1)*(V[:,1]<20)
 w=np.maximum(w,influence)
 for k,ring in enumerate(p['rings']):w[ring]=[0,0,.15,.5,.85,1,1,1,1,.9][k]
 # Inner turn at the aperture is fixed.
 used=set(j for f in p['faces'] for j in f);allrings=set(j for ring in p['rings'] for j in ring)
 for i in used-allrings:w[i]=0
# Preserve nasal bridge and tip; broad smoothing only on orbital surfaces.
w*=np.clip((np.abs(V[:,0])-7)/8,0,1)
w*=np.clip((V[:,2]+38)/15,0,1)
for i in range(len(V)):
 if i not in adj:w[i]=0
for _ in range(32):
 V+=.42*w[:,None]*(A@V-V)
 V-=.44*w[:,None]*(A@V-V)
# Slow positional fairing removes the remaining narrow seam needles.
for _ in range(14):V+=.2*w[:,None]*(A@V-V)
D['vertices']=V.tolist();D['fairing']={'method':'Volume-preserving Taubin fairing around orbit junctions; aperture and nasal bridge constrained','max_displacement':float(np.max(np.linalg.norm(V-original,axis=1)))}
(R/'face-r11e.json').write_text(json.dumps(D));print(D['fairing'])
