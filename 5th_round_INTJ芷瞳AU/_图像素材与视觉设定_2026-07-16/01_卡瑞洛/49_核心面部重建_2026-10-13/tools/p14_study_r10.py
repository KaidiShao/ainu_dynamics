import bpy,pathlib,json,numpy as np
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10B.blend'),load_ui=False)
c=json.loads((R.parent/'47_三维头模结构试验_2026-10-12/head-fit.json').read_text())['metrics']['P14'];r=np.array(c['rotation']);M=np.column_stack((r[:,0],-r[:,2],r[:,1]))
cam=bpy.data.objects['Core_T22_pose'].copy();cam.data=cam.data.copy();cam.name='Core_P14_pose';bpy.context.collection.objects.link(cam)
center=Vector((0,25,-2));cam.location=center+Vector(M[2])*700;cam.rotation_euler=Matrix(M.tolist()).transposed().to_euler();cam.data.ortho_scale=305
sc=bpy.context.scene;sc.camera=cam;sc.cycles.samples=16;h=bpy.data.objects['Carrillo_Head'];skin=h.data.materials[0]
for name,m in [('p14',skin),('p14-neutral',bpy.data.materials['Neutral_anatomy'])]:
 h.data.materials[0]=m;sc.render.filepath=str(R/f'renders/r10b-{name}.png');bpy.ops.render.render(write_still=True)
print('P14_STUDY_DONE')
