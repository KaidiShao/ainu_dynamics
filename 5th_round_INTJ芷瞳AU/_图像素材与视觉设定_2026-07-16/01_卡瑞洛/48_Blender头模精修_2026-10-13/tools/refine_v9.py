import bpy,pathlib,math,json
import numpy as np
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'carrillo-refined-v8.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];base=h.data.shape_keys.key_blocks['V8_cheek_and_jaw_planes']
key=h.shape_key_add(name='V9_mandible_side_plane',from_mix=True);key.relative_key=base;key.value=1
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
points=np.array([list(v.co) for v in base.data])
def weight(p):
 x,y,z=p;ax=abs(x)
 return smooth(27,42,ax)*(1-smooth(68,76,ax))*smooth(-4,10,y)*(1-smooth(52,65,y))*smooth(-98,-85,z)*(1-smooth(-56,-38,z))
weights=np.array([weight(p) for p in points])
A=np.column_stack([points[:,1],points[:,2],np.ones(len(points))])
fit=np.linalg.lstsq(A*np.sqrt(weights[:,None]),np.abs(points[:,0])*np.sqrt(weights),rcond=None)[0]
normal=Vector((1,-fit[0],-fit[1]));normal.normalize()
deltas=[]
for i,(src,dst) in enumerate(zip(base.data,key.data)):
 x,y,z=src.co;sgn=1 if x>=0 else -1
 distance=(abs(x)-fit[0]*y-fit[1]*z-fit[2])/math.sqrt(1+fit[0]**2+fit[1]**2)
 amount=max(-3,min(3,distance))*.82*weights[i]
 delta=Vector((-sgn*normal.x*amount,-normal.y*amount,-normal.z*amount))
 dst.co=src.co+delta
 if delta.length>.01:deltas.append(list(delta))
h.data.update()
sc=bpy.context.scene;skin=h.data.materials[0];neutral=bpy.data.materials['Neutral_anatomy']
sc['status']='V9 local mandibular plane refinement after V8 cheek reduction; not author-approved.'
sc['v9_note']='Broad, shallow planarity adjustment to mandibular side; no global narrowing, no squared chin.'
for camera_name,tag,mat in [('View_threequarter','threequarter',skin),('View_threequarter','neutral',neutral),('View_front','front',skin),('View_near-profile','near-profile',skin)]:
 sc.camera=bpy.data.objects[camera_name];h.data.materials[0]=mat
 sc.render.filepath=str(R/f'renders/refined-v9-{tag}.png');bpy.ops.render.render(write_still=True)
h.data.materials[0]=skin;sc.camera=bpy.data.objects['View_threequarter']
bpy.ops.wm.save_as_mainfile(filepath=str(R/'carrillo-refined-v9.blend'))
out={'side_plane_fit_x_from_y_z':list(fit),'affected_vertices':len(deltas),'max_displacement':max(Vector(x).length for x in deltas),'shape_key':key.name,'relative_key':base.name,'status':'candidate; local jaw-plane refinement only'}
(R/'v9-geometry-change.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('V9_DONE',json.dumps(out),flush=True)

