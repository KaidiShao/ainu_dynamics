import bpy,pathlib,json,numpy as np,bmesh
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11L.blend'),load_ui=False)
D=json.loads((R/'face-r11k.json').read_text());M=np.array(D['M']);depth=np.load(R/'depth-r12/T22-3ddfa.npz');P=depth['vertices'];tri=depth['triangles']
s=2.834066269931101;t=np.array([492.22805693585536,-472.4964321812029]);Q=(P[:,:2]*[1,-1]-t)/s
V=Q@M[:2]+(P[:,2]/s-78)[:,None]*M[2]
mesh=bpy.data.meshes.new('3DDFA_T22_depth_probe');mesh.from_pydata(V.tolist(),[],tri.tolist());mesh.update()
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
ob=bpy.data.objects.new('R12_depth_prior_probe',mesh);bpy.context.collection.objects.link(ob);mesh.materials.append(bpy.data.materials['R10E_neutral_anatomy'])
for f in mesh.polygons:f.use_smooth=True
for o in bpy.context.scene.objects:
 if o.type in ['MESH','CURVE'] and o!=ob:o.hide_render=True
sc=bpy.context.scene;sc.cycles.samples=16;sc.render.threads_mode='FIXED';sc.render.threads=6
for cam,tag in [('Core_T22_pose','front'),('View_threequarter','threequarter')]:
 sc.camera=bpy.data.objects[cam];sc.render.filepath=str(R/f'depth-r12/prior-{tag}.png');bpy.ops.render.render(write_still=True)
print('PROBE_DONE',flush=True)
