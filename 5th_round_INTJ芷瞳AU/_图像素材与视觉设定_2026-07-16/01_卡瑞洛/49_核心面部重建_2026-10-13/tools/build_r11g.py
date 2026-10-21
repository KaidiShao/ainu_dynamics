import bpy,pathlib,json,math,numpy as np,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];old=h.data;D=json.loads((R/'face-r11g.json').read_text());V=np.array(D['vertices'])
mesh=bpy.data.meshes.new('R11G_rebuilt_orbital_surfaces');mesh.from_pydata(D['vertices'],[],D['faces']);mesh.update()
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
for name,uv in D['uv'].items():
 lay=mesh.uv_layers.new(name=name)
 for loop in mesh.loops:lay.data[loop.index].uv=uv[loop.vertex_index]
mesh.uv_layers.active_index=list(D['uv']).index('F03_reference_projection');mesh.uv_layers['F03_reference_projection'].active_render=True
for mat in old.materials:mesh.materials.append(mat)
for name in ['photo_weight','side_texture_weight','brow_photo_mix','scalp_cover']:
 attr=mesh.attributes.new(name=name,type='FLOAT',domain='POINT');prior=old.attributes.get(name)
 for i,p in enumerate(V):
  attr.data[i].value=prior.data[i].value if prior and i<len(prior.data) else (1 if name=='photo_weight' else 0)
h.data=mesh;h['R11_orbit_reconstruction']=D['method']
for f in mesh.polygons:f.use_smooth=True
for mod in h.modifiers:
 if mod.type=='SUBSURF':mod.levels=2;mod.render_levels=2
for ob in list(bpy.data.objects):
 if 'upper_lashes' in ob.name:bpy.data.objects.remove(ob,do_unlink=True)
deps=bpy.context.evaluated_depsgraph_get();ev=h.evaluated_get(deps);me=ev.to_mesh();bvh=BVHTree.FromPolygons([v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);fwd=Vector(D['M'][2])
brow=bpy.data.objects['R10_brows']
for sp in brow.data.splines:
 root=Vector(sp.points[0].co[:3]);pos,n,ix,dist=bvh.ray_cast(root+fwd*50,-fwd,100)
 if pos:
  shift=pos+n*.12-root
  for pt in sp.points:pt.co=(*(Vector(pt.co[:3])+shift),1)
ev.to_mesh_clear()
sc=bpy.context.scene;sc.cycles.samples=20;sc.render.threads_mode='FIXED';sc.render.threads=6
sc['status']='R11G rebuilt orbital topology: consistent normals and restored skin attributes; internal review.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11G.blend'))
skin=h.data.materials[0];neutral=bpy.data.materials['R10E_neutral_anatomy']
for cam,tag,mat in [('Core_T22_pose','front',skin),('Core_T22_pose','front-neutral',neutral),('Core_P14_pose','side-neutral',neutral)]:
 sc.camera=bpy.data.objects[cam];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/r11g-{tag}.png');bpy.ops.render.render(write_still=True)
print('R11G_DONE',flush=True)




