import bpy,pathlib,json,numpy as np
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10A.blend'),load_ui=False)
sc=bpy.context.scene;sc.cycles.samples=16
key=bpy.data.objects['Key'];key.location=(300,-240,170);key.rotation_euler=(Vector((0,0,-20))-key.location).to_track_quat('-Z','Y').to_euler();key.data.energy=1600000;key.data.size=100
bpy.data.objects['Fill'].data.energy=105000;bpy.data.objects['Rim'].data.energy=240000
for name in ['R10_dark_brown_fibres','R10_dark_brown_roots']:
 b=bpy.data.materials[name].node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.0038,.0019,.001,1);b.inputs['Roughness'].default_value=.57;b.inputs['Specular IOR Level'].default_value=.12
sc.render.filepath=str(R/'renders/r10a-light-study.png');bpy.ops.render.render(write_still=True)
h=bpy.data.objects['Carrillo_Head'];keys=h.data.shape_keys.key_blocks;V=np.array([v.co[:] for v in keys[-1].data]);O=np.array([v.co[:] for v in keys[0].data]);tri=[]
for f in h.data.polygons:
 q=list(f.vertices)
 for j in range(1,len(q)-1):tri.append([q[0],q[j],q[j+1]])
tri=np.array(tri)
def n(v):return np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])
a,b=n(O),n(V);bad=np.where(np.sum(a*b,axis=1)<0)[0]
print('ROTATED_TRIANGLES',[(tri[i].tolist(),O[tri[i]].mean(0).tolist()) for i in bad],flush=True)
