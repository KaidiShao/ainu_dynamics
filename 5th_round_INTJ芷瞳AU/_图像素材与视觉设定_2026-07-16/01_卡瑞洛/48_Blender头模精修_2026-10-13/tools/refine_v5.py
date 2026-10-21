import bpy,pathlib,json,math
import numpy as np
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1];OLD=R.parent/'47_三维头模结构试验_2026-10-12'
bpy.ops.wm.open_mainfile(filepath=str(R/'carrillo-refined-v4.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head']
# Deeper eye globe, flatter upper lid, slightly supported lower lid.
for name in ['Eyeball_L','Eyeball_R','Iris_L','Iris_R']:
 o=bpy.data.objects[name]
 if name.startswith('Eyeball'):o.location.y+=1.7
 else:
  for v in o.data.vertices:v.co.y+=1.7
for v in h.data.vertices:
 x,y,z=v.co;ax=abs(x)
 if 16<ax<48 and y<15:
  taper=math.exp(-((ax-32)/13)**6)
  upper=math.exp(-((z-6)/4.6)**2)
  lower=math.exp(-((z+.3)/3.3)**2)
  v.co.z+=(-1.45*upper+.65*lower)*taper
  # inward globe adjustment also requires the lid edge to follow it, without changing the brow
  edge=math.exp(-((z-3)/5.5)**2)*taper
  v.co.y+=.8*edge
 if y<-21:
  nasal=math.exp(-(x/16)**4)*math.exp(-((z+34)/15)**2)
  v.co.z-=1.6*nasal
  v.co.y+=.45*nasal
  bridge=math.exp(-(x/9)**4)*math.exp(-((z+14)/13)**2)
  v.co.y-=1.1*bridge
 # compress the actual mouth opening to a contact line
 if abs(x)<28 and y<-17:
  seam=-65.7-1.5*(abs(x)/25)**1.5
  w=math.exp(-((z-seam)/2.8)**2)*math.exp(-(abs(x)/27)**6)
  v.co.z=seam+(v.co.z-seam)*(1-.58*w)
h.data.update()
# Lower sclera luminance without changing the selected low-saturation iris family.
bs=bpy.data.materials['Sclera_warm_offwhite'].node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(.235,.223,.207,1);bs.inputs['Coat Weight'].default_value=.28
# Remove experimental eyelash ribbons which no longer follow the edited lids.
o=bpy.data.objects.get('Brow_lash_fibres')
if o:bpy.data.objects.remove(o,do_unlink=True)
# Store a neutral structural material and a reference-projected material separately.
neutral=bpy.data.materials.new('Neutral_anatomy');neutral.use_nodes=True
pbs=neutral.node_tree.nodes.get('Principled BSDF');pbs.inputs['Base Color'].default_value=(.3,.27,.25,1);pbs.inputs['Roughness'].default_value=.7
F=json.loads((OLD/'head-fit.json').read_text())
def proj(co,key,mirror=False):
 x,y,z=co
 if mirror:x=-abs(x)
 vv=np.array([x,z,-y]);m=F['metrics'][key];rot=np.array(m['rotation']);p=m['scale_pixels_per_model_unit']*(rot@vv)[:2]+np.array(m['translation'])
 return (float(p[0]/1086),float(1+p[1]/1448))
uvnames={}
for key in ['T22','P14']:
 uv=h.data.uv_layers.new(name=key+'_projection');uvnames[key]=uv.name
 for poly in h.data.polygons:
  for li in poly.loop_indices:
   co=h.data.vertices[h.data.loops[li].vertex_index].co
   uv.data[li].uv=proj(co,key,mirror=(key=='P14'))
# Reference appearance material explicitly retains photographed illumination.
m=bpy.data.materials.new('Reference_appearance_T22_P14_baked_light');m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.68;bs.inputs['Specular IOR Level'].default_value=.2
for key in ['T22','P14']:
 tex=nt.nodes.new('ShaderNodeTexImage');tex.name=key;tex.image=bpy.data.images.load(F['sources'][key],check_existing=True);tex.extension='EXTEND'
 uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map=uvnames[key];nt.links.new(uv.outputs[0],tex.inputs['Vector'])
side=h.data.attributes.new('side_texture_weight','FLOAT','POINT')
for v in h.data.vertices:
 x,y,z=v.co
 # use side photograph only on lateral surfaces; avoid its far side
 side.data[v.index].value=max(0,min(1,(abs(x)-43)/23))*max(0,min(1,(y+8)/30))
attr=nt.nodes.new('ShaderNodeAttribute');attr.attribute_name=side.name
mix=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(attr.outputs['Fac'],mix.inputs[0]);nt.links.new(nt.nodes['T22'].outputs['Color'],mix.inputs[1]);nt.links.new(nt.nodes['P14'].outputs['Color'],mix.inputs[2])
# eliminate extrapolated jaw/background on neck and rear skull
weight=h.data.attributes['photo_weight']
for v in h.data.vertices:
 x,y,z=v.co
 weight.data[v.index].value=max(0,min(1,(100-y)/38))*max(0,min(1,(z+117)/16))
a=nt.nodes.new('ShaderNodeAttribute');a.attribute_name='photo_weight'
blend=nt.nodes.new('ShaderNodeMixRGB');blend.inputs[1].default_value=(.16,.092,.055,1);nt.links.new(a.outputs['Fac'],blend.inputs[0]);nt.links.new(mix.outputs[0],blend.inputs[2]);nt.links.new(blend.outputs[0],bs.inputs['Base Color'])
# retain an inspectable neutral-surface copy of the material slots
h.data.materials[0]=m
sc=bpy.context.scene;sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.view_settings.exposure=.0
sc.render.resolution_x=800;sc.render.resolution_y=1000
bpy.data.objects['Key'].data.energy=1800000;bpy.data.objects['Fill'].data.energy=550000
cam=sc.camera;cam.data.ortho_scale=310
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
def shot(angle,elev,name,material):
 h.data.materials[0]=material
 aa=math.radians(angle);e=math.radians(elev);target=Vector((0,25,-2))
 cam.location=target+Vector((700*math.sin(aa)*math.cos(e),-700*math.cos(aa)*math.cos(e),700*math.sin(e)));aim(cam,target)
 sc.render.filepath=str(R/f'renders/refined-v5-{name}.png');bpy.ops.render.render(write_still=True)
shot(0,11.5,'front',m)
shot(-45,3,'threequarter',m)
shot(-75,1,'near-profile',m)
# Neutral render has no photograph lighting or face colour, so geometry can be judged independently.
shot(-45,3,'neutral-geometry',neutral)
h.data.materials[0]=m
bpy.ops.wm.save_as_mainfile(filepath=str(R/'carrillo-refined-v5.blend'))

