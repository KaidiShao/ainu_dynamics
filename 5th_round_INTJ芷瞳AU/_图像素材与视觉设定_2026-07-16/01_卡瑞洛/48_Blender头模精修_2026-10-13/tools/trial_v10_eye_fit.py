import bpy,pathlib,math,json
from mathutils import Vector,Quaternion
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'carrillo-refined-v9.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];previous=h.data.shape_keys.key_blocks['V9_mandible_side_plane']
key=h.shape_key_add(name='V10_lid_globe_fit_trial',from_mix=True);key.relative_key=previous;key.value=1
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
count=0
for src,dst in zip(previous.data,key.data):
 x,y,z=src.co;ax=abs(x)
 if not (17<ax<48 and y<12 and -14<z<15):continue
 taper=math.exp(-((ax-32)/11.5)**4)*(1-smooth(0,12,y))
 upper=math.exp(-((z-5.1)/3.4)**2)
 lower=math.exp(-((z+.6)/3.1)**2)
 # Restore the central aperture without raising brows or moving either canthus.
 delta=Vector((0,-.25*(upper+lower)*taper,(1.0*upper-1.2*lower)*taper))
 dst.co=src.co+delta
 if delta.length>.01:count+=1
h.data.update()
# Match the iris direction to the existing front camera elevation.
# No eye-colour change; this trial isolates anatomy and gaze direction.
for side in ['L','R']:
 eye=bpy.data.objects['Eyeball_'+side];old=eye.location.copy();eye.location.y-=1.4
 iris=bpy.data.objects['Iris_'+side]
 rot=Quaternion(Vector((1,0,0)),math.radians(-11.5))
 for v in iris.data.vertices:
  rel=v.co-old
  r=math.hypot(rel.x,rel.z)*1.025
  theta=math.atan2(rel.z,rel.x)
  p=Vector((r*math.cos(theta),-math.sqrt(max(.01,11.7**2-r*r))-.04,r*math.sin(theta)))
  v.co=eye.location+rot@p
 iris.data.update()
sc=bpy.context.scene;skin=h.data.materials[0];neutral=bpy.data.materials['Neutral_anatomy']
sc['status']='V10 eye aperture / globe / gaze trial. V9 rejected by author. No full likeness approval.'
sc['v10_note']='Upper central lid +1mm, lower central lid -1.2mm, canthi and brows retained; globe forward 1.4mm; iris faces front camera. Pigment unchanged.'
sc.cycles.samples=24
for camera_name,tag,mat in [('View_front','front',skin),('View_threequarter','threequarter',skin),('View_threequarter','neutral',neutral)]:
 sc.camera=bpy.data.objects[camera_name];h.data.materials[0]=mat
 sc.render.filepath=str(R/f'renders/refined-v10-{tag}.png');bpy.ops.render.render(write_still=True)
h.data.materials[0]=skin;sc.camera=bpy.data.objects['View_front']
bpy.ops.wm.save_as_mainfile(filepath=str(R/'carrillo-eye-fit-v10-EXPERIMENT.blend'))
(R/'v10-eye-trial.json').write_text(json.dumps({'status':'experiment only; do not promote without reviewing likeness','affected_lid_vertices':count,'changed':['central aperture','globe depth','iris gaze direction'],'preserved':['iris pigment','brows','nose','mouth','jaw','hair','lighting','cameras']},indent=2),encoding='utf8')
print('V10_TRIAL_DONE',flush=True)

