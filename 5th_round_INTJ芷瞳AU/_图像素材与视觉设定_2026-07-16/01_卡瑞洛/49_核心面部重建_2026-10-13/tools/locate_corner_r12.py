import bpy,pathlib,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R12F.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];P=np.load(R/'depth-r12/warped-prior.npz');M=P['M'];q=P['landmark_q'];bvh=BVHTree.FromPolygons([v.co[:] for v in h.data.vertices],[list(f.vertices) for f in h.data.polygons]);cam=bpy.data.objects['Core_P14_pose'];rot=cam.rotation_euler.to_matrix();right=rot@Vector((1,0,0));up=rot@Vector((0,1,0));fw=rot@Vector((0,0,1))
for px,py in [(382,480),(378,468),(389,482),(376,473),(390,493),(383,483),(372,476)]:
 origin=cam.location+right*((px/760-.5)*244)+up*((.5-py/950)*305);pos,n,idx,dist=bvh.ray_cast(origin,-fw,1000)
 if pos:
  qq=np.array(pos)@M[:2].T;print(px,py,'world',list(pos),'q',qq.tolist(),'from33',(qq-q[33]).tolist(),'from263',(qq-q[263]).tolist())
