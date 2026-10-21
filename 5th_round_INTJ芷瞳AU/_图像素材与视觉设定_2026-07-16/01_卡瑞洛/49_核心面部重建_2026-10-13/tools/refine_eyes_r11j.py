import bpy,pathlib,json,math,random,numpy as np
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11I.blend'),load_ui=False)
D=json.loads((R/'face-r11h.json').read_text());M=np.array(D['M']);fw=Vector(M[2]);h=bpy.data.objects['Carrillo_Head'];V=np.array([v.co[:] for v in h.data.vertices]);Q=V@M[:2].T
# Prevent hair from the old photographic texture appearing as grey marks on the forehead.
photo=h.data.attributes.get('photo_weight')
for i,v in enumerate(h.data.vertices):
 z=v.co.z;fade=np.clip((z-21)/16,0,1)
 if abs(v.co.x)<70 and v.co.y<25:photo.data[i].value*=1-fade*.92
# Fine iris fibres and a modestly smaller pupil retain the established grey-blue palette.
for side in ['L','R']:
 o=bpy.data.objects['Iris_'+side];verts=o.data.vertices;ca=o.data.color_attributes['Iris_fibres'];c=np.array(D['eyes'][0 if side=='L' else 1])-np.array(o.location)
 for i,v in enumerate(verts):
  q=(np.array(v.co)-c)@M[:2].T;r=float(np.linalg.norm(q));ang=math.atan2(q[1],q[0]);pupil=1.95
  if r<pupil:col=(.001,.0012,.0013,1)
  else:
   fibres=(.82+.22*math.sin(ang*43+.65*math.sin(r*3))+.18*math.sin(ang*83+r*.8)+.1*math.sin(ang*119-r*4))
   crypt=.78+.22*math.sin(r*5.6+.6*math.sin(ang*13));limbal=.30+.70*min(1,max(0,(6.05-r)/.55));inner=.5+.5*min(1,max(0,(r-pupil)/.6));f=fibres*crypt*limbal*inner
   col=(.067*f,.080*f,.093*f,1)
  ca.data[i].color=col
 mat=o.data.materials[0];nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.48
 # Local occlusion strengthens the physical contact between the upper lid and the globe.
 if not nt.nodes.get('R11_contact_occlusion'):
  source=bs.inputs['Base Color'].links[0].from_socket;ao=nt.nodes.new('ShaderNodeAmbientOcclusion');ao.name='R11_contact_occlusion';ao.inputs['Distance'].default_value=7
  mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.65;nt.links.new(source,mix.inputs[1]);nt.links.new(ao.outputs['AO'],mix.inputs[2]);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
# Fine surface contrast, not artificial emissive or glowing eyes.
sc=bpy.context.scene;sc.render.threads_mode='FIXED';sc.render.threads=6;sc.cycles.samples=32
skin=h.data.materials[0];neutral=bpy.data.materials['R10E_neutral_anatomy'];bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11J.blend'))
for cname,tag,material in [('Core_T22_pose','front',skin),('Core_T22_pose','front-neutral',neutral),('Core_P14_pose','side',skin),('Core_P14_pose','side-neutral',neutral),('View_threequarter','threequarter',skin)]:
 sc.camera=bpy.data.objects[cname];h.data.materials[0]=material;sc.render.filepath=str(R/f'renders/r11j-{tag}.png');bpy.ops.render.render(write_still=True)
print('R11J_DONE',flush=True)
