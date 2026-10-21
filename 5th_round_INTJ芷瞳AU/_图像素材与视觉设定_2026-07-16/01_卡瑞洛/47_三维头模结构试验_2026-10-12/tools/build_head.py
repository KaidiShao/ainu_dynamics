"""Experimental shared mesh. Weak-perspective fit, not a calibrated reconstruction."""
import sys,json,pathlib,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/python'))
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import lsqr
D=json.loads((ROOT/'landmarks.json').read_text(encoding='utf8'))
canonical=[]; faces=[]
for line in (ROOT/'assets/canonical_face_model.obj').read_text().splitlines():
 if line.startswith('v '):canonical.append([float(x) for x in line.split()[1:]])
 if line.startswith('f '):faces.append([int(x.split('/')[0])-1 for x in line.split()[1:]])
C=np.array(canonical); F=np.array(faces); n=len(C)
mir=np.argmin(np.linalg.norm(C[:,None,:]-C[None,:,:]*[-1,1,1],axis=2),axis=1)
def sym(v):return (v+v[mir]*[-1,1,1])/2
obs={}; initial_rot={}
for key,d in D.items():
 l=np.array(d['landmarks'])[:468]; w,h=d['width'],d['height']
 obs[key]=l[:,:2]*[w,-h]
 initial_rot[key]=np.array(d['transform'])[:3,:3]
l=np.array(D['T22']['landmarks'])[:468]*[1086,-1448,-1086]
v=l@initial_rot['T22']
eye=(v[[33,133,263,362]].mean(axis=0)); v-=eye
scale=63/np.linalg.norm(v[[33,133]].mean(axis=0)-v[[263,362]].mean(axis=0)); v*=scale
v=sym(v); initial=v.copy()
adj=[set() for _ in range(n)]
for a,b,c in F:
 for i,j in [(a,b),(b,c),(c,a)]:adj[i].add(j);adj[j].add(i)
ids={'T22':np.arange(n),'P14':np.where(C[:,0]<.8)[0]}
# The far side in P14 is predicted by the detector, not directly observed: exclude it.
weights={'T22':np.ones(n),'P14':np.ones(n)*.65}
for k in weights:
 weights[k][C[:,1]>5]=.12
 weights[k][np.abs(C[:,0])>6.8]=.25
params={}
def fitcamera(key,mesh):
 ix=ids[key]; target=obs[key][ix]
 if key not in params:
  r=Rotation.from_matrix(initial_rot[key]).as_rotvec(); p=mesh@initial_rot[key].T
  s=np.std(target)/np.std(p[ix,:2]); t=np.mean(target-s*p[ix,:2],axis=0); init=np.r_[r,np.log(s),t]
 else:init=params[key]
 def fun(a):
  r=Rotation.from_rotvec(a[:3]).as_matrix(); projected=np.exp(a[3])*(mesh@r.T)[:,:2]+a[4:]
  return ((projected[ix]-target)*weights[key][ix,None]).ravel()
 result=least_squares(fun,init,loss='soft_l1',f_scale=4,max_nfev=150)
 params[key]=result.x
 return Rotation.from_rotvec(result.x[:3]).as_matrix(),np.exp(result.x[3]),result.x[4:]
# Alternating constrained surface fit. Front image retains stronger weight; a smooth
# displacement prior prevents fitting every noisy / occluded inferred point literally.
for iteration in range(5):
 cameras={k:fitcamera(k,v) for k in obs}
 rows=[]; rhs=[]
 def row(entries,b,w=1):rows.append([(j,a*w) for j,a in entries]);rhs.append(b*w)
 for k,(r,s,t) in cameras.items():
  for i in ids[k]:
   for d in range(2):row([(3*i+j,r[d,j]) for j in range(3)],(obs[k][i,d]-t[d])/s,weights[k][i])
 for i in range(n):
  for d in range(3):
   row([(3*i+d,1)],initial[i,d],[.45,.45,.22][d])
   js=list(adj[i]); entries=[(3*i+d,1)]+[(3*j+d,-1/len(js)) for j in js]
   row(entries,initial[i,d]-initial[js,d].mean(),2.4)
   row([(3*i+d,1),(3*mir[i]+d,1 if d==0 else -1)],0,2.0)
 A=lil_matrix((len(rows),3*n))
 for i,rr in enumerate(rows):
  for j,a in rr:A[i,j]+=a
 v=lsqr(A.tocsr(),rhs,atol=1e-8,btol=1e-8,iter_lim=500)[0].reshape(n,3)
v=sym(v)
metrics={}
for k in obs:
 r,s,t=fitcamera(k,v); pred=s*(v@r.T)[:,:2]+t
 e=np.linalg.norm(pred[ids[k]]-obs[k][ids[k]],axis=1)
 metrics[k]={'visible_landmark_count':len(ids[k]),'mean_pixel_residual':float(e.mean()),'median_pixel_residual':float(np.median(e)),'estimated_euler_xyz_degrees':Rotation.from_matrix(r).as_euler('xyz',degrees=True).tolist(),'scale_pixels_per_model_unit':s,'translation':t.tolist(),'rotation':r.tolist(),'warning':'Fitting residual is not identity accuracy; uncalibrated weak perspective and detector estimates.'}
uv=np.array(D['T22']['landmarks'])[:468,:2]*[1,-1]+[0,1]
oval=[10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
out={'face':{'vertices':v.round(5).tolist(),'triangles':F.tolist(),'uv':uv.round(7).tolist()},'initial_vertices':initial.round(5).tolist(),'oval':oval,'metrics':metrics,'sources':{k:d['path'] for k,d in D.items()},'scale_note':'63 model units between estimated eye centers chosen as a generic human scale; not measured anatomy.'}
(ROOT/'head-fit.json').write_text(json.dumps(out,separators=(',',':')),encoding='utf8')
print(json.dumps(metrics,indent=2));print('bounds',v.min(axis=0),v.max(axis=0))
