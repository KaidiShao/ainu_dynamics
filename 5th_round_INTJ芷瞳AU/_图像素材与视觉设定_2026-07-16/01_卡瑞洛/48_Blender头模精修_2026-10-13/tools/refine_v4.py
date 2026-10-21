import bpy,pathlib,sys,math
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
bpy.ops.wm.open_mainfile(filepath=str(R/'carrillo-refined-v3.blend'),load_ui=False)
from groom_v4 import groom
groom()
sc=bpy.context.scene;cam=sc.camera;sc.cycles.samples=40;sc.view_settings.exposure=-.55
cam.data.ortho_scale=307;sc.render.resolution_x=850;sc.render.resolution_y=1050
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for angle,elev,name in [(0,11.5,'front'),(-45,3,'threequarter')]:
 a=math.radians(angle);e=math.radians(elev);target=Vector((0,25,-2))
 cam.location=target+Vector((700*math.sin(a)*math.cos(e),-700*math.cos(a)*math.cos(e),700*math.sin(e)));aim(cam,target)
 sc.render.filepath=str(R/f'renders/refined-v4-{name}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'carrillo-refined-v4.blend'))

