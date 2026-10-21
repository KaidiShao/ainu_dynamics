import pathlib,json,sys,collections
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'47_三维头模结构试验_2026-10-12/tools/python'));import numpy as np
from scipy.sparse import coo_matrix
D=json.loads((R/'face-r11e.json').read_text());V=np.array(D['vertices']);orig=V.copy();F=D['faces'];M=np.array(D['M']);Q=V@M[:2].T
adj=collections.defaultdict(set)
for f in F:
 for a,b in zip(f,f[1:]+f[:1]):adj[a].add(b);adj[b].add(a)
row=[];col=[];dat=[]
for i,nei in adj.items():
 for j in nei:row.append(i);col.append(j);dat.append(1/len(nei))
A=coo_matrix((dat,(row,col)),shape=(len(V),len(V))).tocsr()
r=np.sqrt((V[:,0]/39)**2+((V[:,2]+69)/31)**2)
w=np.clip((1.3-r)/.5,0,1)*(V[:,1]<0)*np.clip((-V[:,2]-43)/9,0,1)
for k,ring in enumerate(D['mouth']['rings']):w[ring]=[0,0,.06,.12,.2,.3,.4,.65,.9,1,1,1,1][k]
w[D['mouth']['inner']]=0
for i in range(len(V)):
 if i not in adj:w[i]=0
for _ in range(30):
 V+=.42*w[:,None]*(A@V-V)
 V-=.44*w[:,None]*(A@V-V)
for _ in range(20):V+=.23*w[:,None]*(A@V-V)
D['vertices']=V.tolist();D['mouth_fairing']={'max_displacement':float(np.max(np.linalg.norm(V-orig,axis=1))),'method':'Smooth closed seam-to-philtrum and lower-lip-to-chin junction; preserve lip outline.'}
(R/'face-r11f.json').write_text(json.dumps(D));print(D['mouth_fairing'])
