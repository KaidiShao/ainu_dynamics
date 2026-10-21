import bpy,pathlib,numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'depth-r12/dense-base.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];V=np.load(R/'depth-r12/dense-base.npy');W=np.load(R/'depth-r12/dense-r12a.npy')
for v,p in zip(h.data.vertices,W):v.co=p
h.data.update()
tree=KDTree(len(V))
for i,p in enumerate(V):tree.insert(Vector(p),i)
tree.balance()
for ob in bpy.data.objects:
 if not ob.name.startswith(('R10_brows','R11_upper_l','R11_lower_w')):continue
 for sp in ob.data.splines:
  root=Vector(sp.points[0].co[:3]);near=tree.find_n(root,4);ww=np.array([1/max(.2,d)**2 for _,_,d in near]);delta=sum((W[i]-V[i])*w for (_,i,_),w in zip(near,ww))/sum(ww)
  for pt in sp.points:pt.co=(*(Vector(pt.co[:3])+Vector(delta)),1)
sc=bpy.context.scene;sc.cycles.samples=24;sc.render.threads_mode='FIXED';sc.render.threads=6
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R12A.blend'))
skin=h.data.materials[0];neutral=bpy.data.materials['R10E_neutral_anatomy']
for cam,tag,mat in [('Core_T22_pose','front',skin),('Core_T22_pose','front-neutral',neutral),('View_threequarter','threequarter',skin),('Core_P14_pose','side-neutral',neutral)]:
 sc.camera=bpy.data.objects[cam];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/r12a-{tag}.png');bpy.ops.render.render(write_still=True)
print('R12A_DONE',flush=True)
