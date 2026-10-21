import bpy, pathlib, math, json, shutil
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
source=R/'Carrillo_3D_working.blend'
backup=R/'carrillo-refined-v7-before-face-slimming.blend'
if not backup.exists():shutil.copy2(source,backup)
bpy.ops.wm.open_mainfile(filepath=str(backup),load_ui=False)
h=bpy.data.objects['Carrillo_Head']
if h.data.shape_keys is None:h.shape_key_add(name='Basis')
key=h.shape_key_add(name='V8_cheek_and_jaw_planes')
key.slider_min=0;key.slider_max=1;key.value=1
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)))
 return t*t*(3-2*t)
moves=[]
for v,kv in zip(h.data.vertices,key.data):
 x,y,z=v.co;ax=abs(x);sign=1 if x>=0 else -1
 # Local cheek volume below the zygoma. Preserve orbital rim and central nose/lips.
 outer=smooth(24,41,ax)*(1-smooth(68,77,ax))
 front=1-smooth(40,64,y)
 cheek=math.exp(-((z+43)/22)**4)*outer*front
 # Reduce the masseter's rounded silhouette, leave the ear and bony jaw corner intact.
 mass=math.exp(-((z+53)/22)**4)*smooth(45,60,ax)*smooth(0,23,y)*(1-smooth(56,71,y))
 # Stronger taper into the lower face, not a widened/squared chin.
 lower=math.exp(-((z+78)/20)**4)*smooth(23,46,ax)*(1-smooth(65,79,y))
 dx=-sign*(4.2*cheek+3.2*mass+2.0*lower)
 dy=3.3*cheek*math.exp(-((ax-43)/19)**4)
 # A restrained malar plane above the cheek reduction; not an exaggerated hollow.
 malar=math.exp(-((z+20)/9)**2)*math.exp(-((ax-51)/12)**4)*(1-smooth(22,40,y))
 dy-=.7*malar
 # Tighten under-jaw volume while keeping the actual jaw contour and chin tip.
 under=math.exp(-((z+107)/15)**4)*smooth(-4,18,y)*(1-smooth(72,95,y))
 dx-=sign*1.6*under*smooth(15,35,ax)
 dy+=2.2*under*(1-smooth(29,47,ax))
 delta=Vector((dx,dy,0));kv.co=v.co+delta
 if delta.length>.01:moves.append(list(delta))
h.data.update()
h['v8_note']='Author: face too full. Local cheek and masseter reduction; jaw taper. Basis retains v7. Eye colour, eyes, hair and lighting unchanged.'
sc=bpy.context.scene
sc['status']='V8 face volume correction; likeness not author-approved.'
sc.render.resolution_x=760;sc.render.resolution_y=950
sc.cycles.samples=24;sc.cycles.use_denoising=True
skin=h.data.materials[0];neutral=bpy.data.materials['Neutral_anatomy']
for camera_name,tag,material in [
 ('View_threequarter','threequarter',skin),
 ('View_front','front',skin),
 ('View_threequarter','neutral',neutral),
 ('View_near-profile','near-profile',skin)
]:
 sc.camera=bpy.data.objects[camera_name];h.data.materials[0]=material
 sc.render.filepath=str(R/f'renders/refined-v8-{tag}.png')
 bpy.ops.render.render(write_still=True)
h.data.materials[0]=skin;sc.camera=bpy.data.objects['View_threequarter']
# Save both a working sculpt and a deliberate v7/v8 comparison using the same setup.
bpy.ops.wm.save_as_mainfile(filepath=str(R/'carrillo-refined-v8.blend'))
stats={'source':backup.name,'candidate':'carrillo-refined-v8.blend','shape_key':key.name,'affected_vertices':len(moves),
 'max_displacement':max(Vector(d).length for d in moves),'max_lateral_reduction':max(abs(d[0]) for d in moves),
 'preserved':'eye geometry, iris colour, hair, cameras, lights, topology','status':'candidate; pending visual check'}
(R/'v8-geometry-change.json').write_text(json.dumps(stats,indent=2),encoding='utf8')
print('V8_DONE',json.dumps(stats),flush=True)

