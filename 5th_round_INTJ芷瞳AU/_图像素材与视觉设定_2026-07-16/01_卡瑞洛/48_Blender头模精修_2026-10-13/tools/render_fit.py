import bpy,json,pathlib,math,sys
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'base-anatomical.blend'),load_ui=False)
d=json.loads((R/'fitted-geometry-v1.json').read_text());h=bpy.data.objects['Carrillo_Head']
for v,co in zip(h.data.vertices,d['vertices']):v.co=co
h.data.update()
for i,suf in enumerate(['','.001']):
 for name,dep in [('Eye',0),('Iris',-12.1),('Pupil',-12.9)]:
  o=bpy.data.objects[name+suf];o.location=Vector(d['eyes'][i])+Vector((0,dep*d['source_scale'],0));o.scale*=d['source_scale']
# constrain eye center relative to upper/lower lids, independent of interior interpolation
for i,suf in enumerate(['','.001']):
 for name in ['Eye','Iris','Pupil']:
  bpy.data.objects[name+suf].location.y+=6.8
sc=bpy.context.scene;cam=sc.camera;cam.data.ortho_scale=280
sc.cycles.samples=32;sc.cycles.use_denoising=True
sc.render.resolution_x=900;sc.render.resolution_y=1100
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for angle in [0,45,90]:
 cam.location=(700*math.sin(math.radians(angle)),-700*math.cos(math.radians(angle)),-24);aim(cam,(0,0,-24))
 sc.render.filepath=str(R/f'renders/fit-v1-clay-{angle}.png');bpy.ops.render.render(write_still=True)
# photo reference mapping, staged separately from neutral material
uv=h.data.uv_layers.new(name='F03_reference_projection')
for poly in h.data.polygons:
 for li in poly.loop_indices:
  uv.data[li].uv=d['uv'][h.data.loops[li].vertex_index]
skin=h.data.materials[0];nt=skin.node_tree;bs=nt.nodes.get('Principled BSDF')
tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R.parent/'28_认可正面下巴轻校准_2026-10-09/MC_FRONT_F03_浅蓝灰柔光_下巴凹痕轻校准_v1.png'))
tex.interpolation='Linear';tex.extension='EXTEND'
uvn=nt.nodes.new('ShaderNodeUVMap');uvn.uv_map=uv.name;nt.links.new(uvn.outputs['UV'],tex.inputs['Vector'])
# vertex attribute ensures the photograph only covers the face, not the rear skull/neck
att=h.data.attributes.new('photo_weight','FLOAT','POINT')
for v in h.data.vertices:
 x,y,z=v.co;fy=max(0,min(1,(75-y)/30));fz=max(0,min(1,(z+145)/25))
 att.data[v.index].value=fy*fz
attr=nt.nodes.new('ShaderNodeAttribute');attr.attribute_name='photo_weight'
mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[1].default_value=(.32,.205,.155,1)
nt.links.new(attr.outputs['Fac'],mix.inputs[0]);nt.links.new(tex.outputs['Color'],mix.inputs[2]);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value=.55
sc.render.filepath=str(R/'renders/fit-v1-photo-45.png');cam.location=(495,-495,-24);aim(cam,(0,0,-24));bpy.ops.render.render(write_still=True)
cam.location=(0,-700,-24);aim(cam,(0,0,-24));sc.render.filepath=str(R/'renders/fit-v1-photo-0.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'carrillo-fitted-v1.blend'))

