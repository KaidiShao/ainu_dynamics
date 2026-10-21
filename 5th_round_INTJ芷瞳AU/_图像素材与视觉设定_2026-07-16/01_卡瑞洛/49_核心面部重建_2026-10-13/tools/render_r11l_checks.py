import bpy,pathlib
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11L.blend'),load_ui=False)
sc=bpy.context.scene;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.cycles.samples=24;h=bpy.data.objects['Carrillo_Head'];h.data.materials[0]=bpy.data.materials['R10E_neutral_anatomy']
for name,tag in [('Core_T22_pose','front-neutral'),('Core_P14_pose','side-neutral')]:
 sc.camera=bpy.data.objects[name];sc.render.filepath=str(R/f'renders/r11l-{tag}.png');bpy.ops.render.render(write_still=True)
print('R11L_CHECKS_DONE',flush=True)
