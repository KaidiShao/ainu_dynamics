import bpy,pathlib,json,numpy as np
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];deps=bpy.context.evaluated_depsgraph_get();ev=h.evaluated_get(deps);me=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=deps)
V=np.array([v.co[:] for v in me.vertices]);N=np.array([v.normal[:] for v in me.vertices]);W=V.copy()
M=np.array(json.loads((R/'structure-r10.json').read_text())['M']);fwd=M[2];eyes=np.array(json.loads((R/'r10c-manifest.json').read_text())['eyes']);reports=[]
for c in eyes:
 q=V-c;dot=q@fwd;rad2=np.sum(q*q,axis=1)-dot*dot
 # Anterior-facing visible skin only, evaluated after subdivision.
 mask=(rad2<11.9**2)&(dot>0)&(N@fwd>.05)&(np.linalg.norm(q,axis=1)<12.0)
 goal=np.sqrt(np.maximum(0,12.12**2-rad2));offset=np.maximum(0,goal-dot)
 ids=np.where(mask)[0];W[ids]+=fwd*offset[ids,None]
 reports.append({'vertices':len(ids),'maximum_penetration':float(offset[ids].max()) if len(ids) else 0,'ids':ids.tolist()})
print('EVALUATED_EYELID_INTERSECTIONS',json.dumps([{k:v for k,v in r.items() if k!='ids'} for r in reports]),flush=True)
h.data=me
for mod in list(h.modifiers):h.modifiers.remove(mod)
h.shape_key_add(name='R10_pre_clearance_evaluated_surface');key=h.shape_key_add(name='R10_evaluated_visible_eyelid_clearance')
for v,p in zip(key.data,W):v.co=p
key.value=1
(R/'eyelid-clearance-r10.json').write_text(json.dumps(reports,indent=2))
sc=bpy.context.scene;sc.cycles.samples=20;sc.render.threads_mode='FIXED';sc.render.threads=6
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10G.blend'))
skin=h.data.materials[0];neutral=bpy.data.materials['R10E_neutral_anatomy']
for cname,tag,mat in [('Core_T22_pose','front',skin),('Core_P14_pose','neutral',neutral)]:
 sc.camera=bpy.data.objects[cname];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/r10g-{tag}.png');bpy.ops.render.render(write_still=True)
print('R10G_DONE',flush=True)
