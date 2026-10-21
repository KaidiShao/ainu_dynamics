import bpy,pathlib,numpy as np,math
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R12F.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];P=np.load(R/'depth-r12/warped-prior.npz');M=P['M'];q=P['landmark_q'];V=np.array([v.co[:] for v in h.data.vertices]);Q=V@M[:2].T;delta=np.zeros(len(V))
for side,ix in [(-1,33),(1,263)]:
 c=q[ix]+[-side*4.0,-6.3]
 delta-=1.45*np.exp(-((Q[:,0]-c[0])/4.1)**2-((Q[:,1]-c[1])/2.6)**2)
delta*=np.clip((20-V[:,1])/12,0,1)
W=V+delta[:,None]*M[2]
for v,p in zip(h.data.vertices,W):v.co=p
h.data.update()
rot=Matrix.Rotation(math.radians(-45),3,'Z');base=bpy.data.objects['Core_T22_pose'];cam=bpy.data.objects['View_threequarter'];center=Vector((0,25,-2));cam.location=center+rot@(base.location-center);cam.rotation_euler=(rot@base.rotation_euler.to_matrix()).to_euler();cam.data.ortho_scale=305
sc=bpy.context.scene;sc.cycles.samples=28;sc.render.threads_mode='FIXED';sc.render.threads=6
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R12G.blend'))
skin=h.data.materials[0];neutral=bpy.data.materials['R10E_neutral_anatomy']
for cname,tag,mat in [('Core_P14_pose','side-neutral',neutral),('Core_T22_pose','front',skin),('Core_T22_pose','front-neutral',neutral),('View_threequarter','threequarter',skin),('Core_P14_pose','side',skin)]:
 sc.camera=bpy.data.objects[cname];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/r12g-{tag}.png');bpy.ops.render.render(write_still=True)
print('R12G_DONE',flush=True)
