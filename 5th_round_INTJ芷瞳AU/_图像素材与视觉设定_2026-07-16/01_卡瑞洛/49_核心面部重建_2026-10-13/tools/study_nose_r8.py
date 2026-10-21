import bpy,pathlib
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R8.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];h.data.shape_keys.key_blocks['R8_01_nasal_dorsum_and_tip_width'].value=1.55
sc=bpy.context.scene;sc.cycles.samples=12
sc.camera=bpy.data.objects['Core_T22_pose'];sc.render.filepath=str(R/'renders/core-r8-nose-study-front.png');bpy.ops.render.render(write_still=True)
c=sc.camera.copy();c.data=c.data.copy();bpy.context.collection.objects.link(c)
c.location=Vector((0,-20,-25))+(c.rotation_euler.to_matrix()@Vector((0,0,1)))*700;c.data.ortho_scale=92
sc.camera=c;h.data.materials[0]=bpy.data.materials['Neutral_anatomy'];sc.render.resolution_x=1000;sc.render.resolution_y=700
sc.render.filepath=str(R/'renders/core-r8-nose-study-neutral.png');bpy.ops.render.render(write_still=True)
print('STUDY_DONE',flush=True)
