import bpy,pathlib,numpy as np,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R12B.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];nt=h.data.materials[0].node_tree
for n in nt.nodes:
 print('NODE',n.name,n.type,[(x.name,str(x.default_value)) for x in n.inputs if not x.is_linked and hasattr(x,'default_value')][:8])
for l in nt.links:print('LINK',l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
P=np.load(R/'depth-r12/warped-prior.npz');M=P['M'];q=P['landmark_q'];fw=Vector(M[2]);V=[v.co[:] for v in h.data.vertices];F=[list(p.vertices) for p in h.data.polygons];bvh=BVHTree.FromPolygons(V,F)
for ix in [468,473]:
 hits=[]
 for dy in np.arange(-10,12,.25):
  qq=q[ix]+[0,dy];pos,n,idx,dist=bvh.ray_cast(Vector(qq@M[:2])+fw*200,-fw,350)
  if pos is not None and pos.dot(fw)>-15:hits.append(round(float(dy),2))
 print('EYE_MASK',ix,hits)
