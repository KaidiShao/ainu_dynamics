import bpy,pathlib,json,numpy as np
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10.blend'),load_ui=False)
M=np.array(json.loads((R/'structure-r10.json').read_text())['M']);f=M[2];eyes=np.array(json.loads((R/'r10c-manifest.json').read_text())['eyes'])
for suffix,c in zip(['L','R'],eyes):
 for prefix in ['Eyeball_','Iris_','Cornea_']:
  ob=bpy.data.objects[prefix+suffix]
  for v in ob.data.vertices:
   p=np.array(v.co[:]);depth=(p-c)@f;v.co=p-f*(depth*.20+.30)
  ob.data.update()
sc=bpy.context.scene;sc.cycles.samples=20;sc.render.threads_mode='FIXED';sc.render.threads=6
sc['R10_eye_surface']='Frontal aperture retained; ocular forward depth reduced 20 percent and recessed 0.3 model units to fit the actual lids.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10H.blend'))
h=bpy.data.objects['Carrillo_Head'];skin=h.data.materials[0];neutral=bpy.data.materials['R10E_neutral_anatomy']
for cname,tag,mat in [('Core_T22_pose','front',skin),('Core_P14_pose','neutral',neutral)]:
 sc.camera=bpy.data.objects[cname];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/r10h-{tag}.png');bpy.ops.render.render(write_still=True)
print('R10H_DONE',flush=True)
