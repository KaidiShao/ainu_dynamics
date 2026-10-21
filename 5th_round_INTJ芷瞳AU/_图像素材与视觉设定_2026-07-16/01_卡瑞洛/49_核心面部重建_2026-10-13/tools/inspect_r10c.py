import bpy,pathlib,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10C.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];kb=h.data.shape_keys.key_blocks;V=np.array([v.co[:] for v in kb[0].data])
for k in list(kb)[1:]:V+=(np.array([v.co[:] for v in k.data])-np.array([v.co[:] for v in k.relative_key.data]))*k.value
data={'vertices':V.tolist(),'faces':[list(f.vertices) for f in h.data.polygons]}
deps=bpy.context.evaluated_depsgraph_get();ev=h.evaluated_get(deps);me=ev.to_mesh();bvh=BVHTree.FromPolygons([v.co for v in me.vertices],[list(p.vertices) for p in me.polygons])
old=R.parent/'47_三维头模结构试验_2026-10-12';fit=json.loads((old/'head-fit.json').read_text());lm=json.loads((old/'landmarks.json').read_text());cam=fit['metrics']['T22'];r=np.array(cam['rotation']);M=np.column_stack((r[:,0],-r[:,2],r[:,1]));fwd=Vector(M[2]);data['landmarks']=[]
for i,p in enumerate(lm['T22']['landmarks'][:468]):
 q=(np.array(p[:2])*[1086,-1448]-cam['translation'])/cam['scale_pixels_per_model_unit']
 origin=Vector(q@M[:2])+fwd*350
 hit,n,ix,dist=bvh.ray_cast(origin,-fwd,700)
 data['landmarks'].append({'hit':hit is not None,'point':list(hit) if hit is not None else None})
(R/'r10c-inspection.json').write_text(json.dumps(data))
for i,p in enumerate(V):
 if abs(p[0])<27 and p[1]<-19 and -86<p[2]<-49: print(i,np.round(p,2).tolist())
ev.to_mesh_clear()
