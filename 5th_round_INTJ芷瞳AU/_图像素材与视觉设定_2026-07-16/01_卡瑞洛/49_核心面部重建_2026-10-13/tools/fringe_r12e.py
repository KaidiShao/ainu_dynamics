import bpy,pathlib,json,numpy as np,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R12D.blend'),load_ui=False)
P=np.load(R/'depth-r12/warped-prior.npz');M=P['M'];fw=Vector(M[2]);right=Vector(M[0]);up=Vector(M[1]);h=bpy.data.objects['Carrillo_Head'];bvh=BVHTree.FromPolygons([v.co[:] for v in h.data.vertices],[list(f.vertices) for f in h.data.polygons])
locks=bpy.data.objects['Long_loose_front_locks'];groups={}
for i,sp in enumerate(locks.data.splines):
 group=i//18
 if group not in groups:
  end=Vector(sp.points[-1].co[:3]);qq=np.array(end)@M[:2].T
  target=22+11*(abs(qq[0])/65)+8*math.sin(group*2.71)
  drop=max(0,min(25,qq[1]-target));groups[group]=(drop,qq)
 drop,qq=groups[group]
 for j,pt in enumerate(sp.points):
  t=j/(len(sp.points)-1);pos=Vector(pt.co[:3]);pos-=up*(drop*t**2.2)
  pos+=right*(2.0*math.sin(t*5+group*1.39)*t**2)
  xy=np.array(pos)@M[:2].T;skin,n,ix,dist=bvh.ray_cast(right*xy[0]+up*xy[1]+fw*300,-fw,600)
  if skin is not None:
   distance=(pos-skin).dot(fw)
   if distance<.7:pos+=fw*(.7-distance)
  pt.co=(*pos,1)
mat=bpy.data.objects['Carrillo_wavy_groom'].data.materials[0];nt=mat.node_tree
for n in nt.nodes:
 if n.type=='BSDF_HAIR_PRINCIPLED':
  n.inputs['Melanin'].default_value=.75;n.inputs['Melanin Redness'].default_value=.25
 if n.type=='MIX_SHADER':n.inputs[0].default_value=.55
sc=bpy.context.scene;sc.cycles.samples=24;sc.render.threads_mode='FIXED';sc.render.threads=6
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R12E.blend'))
skin=h.data.materials[0];neutral=bpy.data.materials['R10E_neutral_anatomy']
for cam,tag,mat in [('Core_T22_pose','front',skin),('Core_T22_pose','front-neutral',neutral),('View_threequarter','threequarter',skin),('Core_P14_pose','side',skin),('Core_P14_pose','side-neutral',neutral)]:
 sc.camera=bpy.data.objects[cam];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/r12e-{tag}.png');bpy.ops.render.render(write_still=True)
print('R12E_DONE',flush=True)
