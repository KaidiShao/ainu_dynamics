import bpy,json,pathlib
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'base-anatomical.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];lm=json.loads((R/'base-landmarks.json').read_text())['BASE']['landmarks']
deps=bpy.context.evaluated_depsgraph_get();ev=h.evaluated_get(deps)
out=[]
for u,v,z in lm[:468]:
 x=(u-.5)*300*900/1100;zz=(.5-v)*300-24
 hit,p,n,i=ev.ray_cast(Vector((x,-400,zz)),Vector((0,1,0)))
 out.append({'point':list(p) if hit else [x,-25,zz],'hit':hit,'normal':list(n) if hit else [0,-1,0]})
(R/'base-surface-landmarks.json').write_text(json.dumps(out),encoding='utf8')
print('HITS',sum(x['hit'] for x in out),len(out))
# dump boundary loops in base mesh
edges={}
for f in h.data.polygons:
 v=list(f.vertices)
 for a,b in zip(v,v[1:]+v[:1]):
  e=tuple(sorted((a,b)));edges[e]=edges.get(e,0)+1
boundary=[e for e,n in edges.items() if n==1]
(R/'base-boundary.json').write_text(json.dumps(boundary))
print('BOUNDARY_EDGES',len(boundary))

