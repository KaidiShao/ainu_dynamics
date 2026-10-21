import bpy,pathlib,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1];P=np.load(R/'depth-r12/warped-prior.npz');M=P['M'];prior=P['q']@M[:2]+P['depth'][:,None]*M[2];V=np.load(R/'depth-r12/dense-base.npy');Q=V@M[:2].T
bvh=BVHTree.FromPolygons([Vector(v) for v in prior],P['triangles'].tolist(),all_triangles=True);fw=Vector(M[2]);target=np.full(len(V),np.nan)
for i,q in enumerate(Q):
 origin=Vector(q@M[:2])+fw*400;pos,n,idx,dist=bvh.ray_cast(origin,-fw,800)
 if pos is not None:target[i]=Vector(pos).dot(fw)
np.save(R/'depth-r12/surface-depth.npy',target)
# Boundary distance is needed to avoid pulling the throat up into the facial shell.
edges={}
for f in P['triangles']:
 for a,b in zip(f,np.roll(f,-1)):
  e=tuple(sorted((int(a),int(b))));edges[e]=edges.get(e,0)+1
boundary=sorted({i for e,n in edges.items() if n==1 for i in e})
np.save(R/'depth-r12/prior-boundary.npy',P['q'][boundary]);print('SAMPLED',np.isfinite(target).sum(),len(V),flush=True)
