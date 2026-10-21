import bpy,pathlib,sys
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
versions=[int(x) for x in sys.argv[sys.argv.index('--')+1:]] if '--' in sys.argv else [7,8]
for version in versions:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'Carrillo_core_rebuild_R{version}.blend'),load_ui=False)
 h=bpy.data.objects['Carrillo_Head'];skin=h.data.materials[0];neutral=bpy.data.materials['Neutral_anatomy'];sc=bpy.context.scene;sc.cycles.samples=20
 views=[]
 if version==8:
  views += [('Core_T22_pose','eyes-neutral',neutral,(0,5,1.4),132,460),('View_threequarter','eyes-side-neutral',neutral,(-12,5,1.4),100,460),('Core_T22_pose','eyes',skin,(0,5,1.4),132,460)]
 views += [('Core_T22_pose','nose-neutral',neutral,(0,-20,-25),92,700),('View_threequarter','nose-side-neutral',neutral,(-7,-17,-25),92,700)]
 for source,tag,mat,center,scale,height in views:
  c=bpy.data.objects[source].copy();c.data=c.data.copy();c.name='Detail_'+tag;bpy.context.collection.objects.link(c)
  forward=c.rotation_euler.to_matrix()@Vector((0,0,1));c.location=Vector(center)+forward*700;c.data.ortho_scale=scale
  sc.camera=c;sc.render.resolution_x=1000;sc.render.resolution_y=height;h.data.materials[0]=mat
  sc.render.filepath=str(R/f'renders/core-r{version}-{tag}.png');bpy.ops.render.render(write_still=True)
 print('DETAILS_DONE',version,flush=True)
