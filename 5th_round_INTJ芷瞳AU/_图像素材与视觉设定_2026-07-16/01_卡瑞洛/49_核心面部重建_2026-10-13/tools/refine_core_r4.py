import bpy,pathlib,json,math
import numpy as np
from mathutils import Vector,Quaternion
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R3.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];base=np.array([v.co[:] for v in h.data.vertices]);h.shape_key_add(name='Rebuilt_core_R3')
k=h.shape_key_add(name='R4_lids_nasal_bridge_labiomental_transition')
def gauss(v,c,w,p=2):return math.exp(-abs((v-c)/w)**p)
for i,v in enumerate(k.data):
 x,y,z=base[i];ax=abs(x);front=1/(1+math.exp(min(50,(y-3)/5)))
 # Reshape the middle upper eyelid, keeping both canthi and lower lid stable.
 lid=gauss(ax,32,10,4)*gauss(z,5.8,3.0)*gauss(y,-6,7)
 dz=-.8*lid
 # A supported orbital roof instead of a round, surprised aperture.
 orbit=gauss(ax,31,17,4)*gauss(z,13,6)*front
 dy=-.6*orbit
 # Lengthen the visible nasal bridge relationship without projecting the tip.
 bridge=gauss(x,0,8,4)*gauss(z,-8,16)*front
 dy-=1.65*bridge
 tip=gauss(z,-34,10)*gauss(x,0,18,4)*front
 dx=-x*.035*tip
 # Reduce the dent between lower lip and chin; recede the round chin prominence.
 groove=gauss(x,0,21,4)*gauss(z,-84,7)*front
 chin=gauss(x,0,28,4)*gauss(z,-102,12)*front
 dy+=-1.65*groove+1.35*chin
 dx-=x*.022*chin
 v.co=(x+dx,y+dy,z+dz)
k.value=1
h['reconstruction']='R4: original anatomical core refit, repaired rear-shell ray hits; controlled lid, bridge and lip-chin corrections. Likeness unapproved.'
# Use the actual vertex-colour iris with a restrained specular response.
# Large area lights previously washed the pupil into a gray disc.
for name in ['Iris_L','Iris_R']:
 o=bpy.data.objects[name];m=bpy.data.materials.get('Core_R4_iris')
 if m is None:
  m=bpy.data.materials.new('Core_R4_iris');m.use_nodes=True
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.55;bs.inputs['Specular IOR Level'].default_value=.07
  col=m.node_tree.nodes.new('ShaderNodeVertexColor');col.layer_name='Iris_fibres';m.node_tree.links.new(col.outputs['Color'],bs.inputs['Base Color'])
 o.data.materials.clear();o.data.materials.append(m)
 center=bpy.data.objects[name.replace('Iris','Eyeball')].location
 # Two degrees lower, rather than raising the eye to meet the camera.
 q=Quaternion((1,0,0),math.radians(2))
 for v in o.data.vertices:v.co=center+q@(v.co-center)
for name in ['Eyeball_L','Eyeball_R']:
 m=bpy.data.objects[name].data.materials[0];bs=m.node_tree.nodes.get('Principled BSDF')
 bs.inputs['Base Color'].default_value=(.22,.205,.185,1);bs.inputs['Roughness'].default_value=.4;bs.inputs['Specular IOR Level'].default_value=.18;bs.inputs['Coat Weight'].default_value=0
sc=bpy.context.scene;sc.cycles.samples=24
skin=h.data.materials[0];neutral=bpy.data.materials['Neutral_anatomy'];skin.use_fake_user=True
for camera,tag,mat in [('Core_T22_pose','front',skin),('Core_T22_pose','front-neutral',neutral),('View_threequarter','threequarter',skin),('View_threequarter','neutral',neutral),('View_near-profile','near-profile',skin)]:
 sc.camera=bpy.data.objects[camera];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/core-r4-{tag}.png');bpy.ops.render.render(write_still=True)
h.data.materials[0]=skin;sc.camera=bpy.data.objects['Core_T22_pose'];sc['status']='Rebuilt core R4: author review pending. Original V9 remains unchanged. Not a validated reconstruction.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R4.blend'))
V=np.array([v.co[:] for v in k.data]);report={'version':'R4','status':'awaiting visual and author review','finite':bool(np.isfinite(V).all()),'max_local_corrective_displacement':float(np.linalg.norm(V-base,axis=1).max()),'base':'Fresh original anatomical head core; V9 peripheral scalp/hair/neck','corrections':['Discard mouth ray hits 41/271 on interior shell','View-plane displacement preserving internal depth ordering','Joint eyelid/eyeball placement','Upper lid central curve','Nasal bridge and tip balance','Lip-chin volume continuity','Reduced iris specular washout'],'limits':['T22 and P14 are not calibrated multiview photography','F03 skin still includes photographed lighting','Hair inherited from earlier unapproved model','A technically valid mesh does not establish likeness']}
(R/'core-r4-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('R4_DONE',json.dumps(report),flush=True)
