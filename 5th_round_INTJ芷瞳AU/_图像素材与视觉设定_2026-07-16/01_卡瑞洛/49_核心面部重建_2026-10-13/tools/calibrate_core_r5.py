import bpy,pathlib,json,math
import numpy as np
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R4.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];previous=h.data.shape_keys.key_blocks[-1];k=h.shape_key_add(name='R5_front_proportion_calibration',from_mix=True);k.relative_key=previous
base=np.array([v.co[:] for v in k.data])
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
for i,v in enumerate(k.data):
 x,y,z=base[i];ax=abs(x);front=1-smooth(20,75,y)
 center=(1-smooth(55,78,ax))*front
 dz=-z*.038*smooth(-135,-111,z)*(1-smooth(-8,1,z))*center
 mouth=math.exp(-((z+64)/13)**4)*math.exp(-(ax/29)**6)*front
 jaw=math.exp(-((z+88)/29)**4)*smooth(22,42,ax)*front
 nose=math.exp(-((z+39)/10)**4)*math.exp(-(ax/22)**6)*front
 dx=-x*(.070*mouth+.026*jaw+.018*nose)
 v.co=(x+dx,y,z+dz)
k.value=1
sc=bpy.context.scene;sc.cycles.samples=20;sc.camera=bpy.data.objects['Core_T22_pose'];skin=h.data.materials[0];neutral=bpy.data.materials['Neutral_anatomy']
sc['status']='R5 reconstructed-core working model. Central anatomy rebuilt; identity not established and not approved by author.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R5.blend'))
for camera,tag,mat in [('Core_T22_pose','front',skin),('Core_T22_pose','front-neutral',neutral),('View_threequarter','threequarter',skin),('View_threequarter','neutral',neutral),('View_near-profile','near-profile',skin)]:
 sc.camera=bpy.data.objects[camera];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/core-r5-{tag}.png');bpy.ops.render.render(write_still=True)
h.data.materials[0]=skin;sc.camera=bpy.data.objects['Core_T22_pose']
V=np.array([v.co[:] for v in k.data]);report=json.loads((R/'core-r4-manifest.json').read_text(encoding='utf8'));report.update(version='R5',status='Core rebuilt and rendered; likeness not established',max_R5_corrective_displacement=float(np.linalg.norm(V-base,axis=1).max()),finite=bool(np.isfinite(V).all()))
report['corrections']+=['Small mid/lower face length correction','Localized mouth and alar width correction; separate editable shape key']
(R/'core-r5-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('R5_DONE',json.dumps(report),flush=True)
