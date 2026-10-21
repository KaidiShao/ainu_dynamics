import bpy,pathlib
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
for version in [8,9]:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'Carrillo_core_rebuild_R{version}.blend'),load_ui=False)
 h=bpy.data.objects['Carrillo_Head'];neutral=bpy.data.materials['Neutral_anatomy'];sc=bpy.context.scene;sc.cycles.samples=20;h.data.materials[0]=neutral
 sc.render.resolution_x=1000;sc.render.resolution_y=700
 views=[]
 if version==9:views=[('Core_T22_pose','nose-neutral',(0,-20,-25)),('View_threequarter','nose-side-neutral',(-7,-17,-25))]
 views.append(('PROFILE','nose-profile-neutral',(0,-15,-18)))
 for source,tag,center in views:
  c=bpy.data.objects['Core_T22_pose' if source=='PROFILE' else source].copy();c.data=c.data.copy();bpy.context.collection.objects.link(c);target=Vector(center)
  if source=='PROFILE':
   c.location=target+Vector((-700,0,0));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler()
  else:c.location=target+(c.rotation_euler.to_matrix()@Vector((0,0,1)))*700
  c.data.ortho_scale=92;sc.camera=c;sc.render.filepath=str(R/f'renders/core-r{version}-{tag}.png');bpy.ops.render.render(write_still=True)
 print('DETAILS_DONE',version,flush=True)
