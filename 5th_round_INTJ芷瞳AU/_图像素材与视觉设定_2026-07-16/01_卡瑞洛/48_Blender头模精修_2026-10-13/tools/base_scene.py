import bpy, math, json, pathlib
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
source=R/'assets/human-base/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend'
with bpy.data.libraries.load(str(source),link=False) as (f,t):
 t.objects=['GEO-head_animation_realistic']
head=t.objects[0];bpy.context.collection.objects.link(head)
head.location=(0,0,0);head.rotation_euler=(0,0,0);head.scale=(1,1,1)
for m in list(head.modifiers):
 print('MOD',m.name,m.type,getattr(m,'levels',None),getattr(m,'total_levels',None),flush=True)
 head.modifiers.remove(m)
for v in head.data.vertices:
 v.co=Vector((v.co.x*1000,v.co.y*1000+115.3812,v.co.z*1000-310.0375))
head.name='Carrillo_Head'
for f in head.data.polygons:f.use_smooth=True
def mat(name,color,rough=.5):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough
 return m
skin=mat('Neutral_skin',(.42,.29,.235),.58);head.data.materials.append(skin)
sm=head.modifiers.new('Anatomical surface','SUBSURF');sm.levels=2;sm.render_levels=2
sclera=mat('Warm_sclera',(.67,.67,.60),.24)
iris=mat('Pale_gray_blue',(.105,.145,.16),.34);pupil=mat('Pupil',(.003,.004,.005),.25)
for x in [-35.8766,35.8766]:
 bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=13.05,location=(x,0,0))
 eye=bpy.context.object;eye.name='Eye';eye.data.materials.append(sclera)
 for f in eye.data.polygons:f.use_smooth=True
 for name,r,dep,ma in [('Iris',6.0,-12.1,iris),('Pupil',2.6,-12.9,pupil)]:
  bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=24,radius=1,location=(x,dep,0))
  o=bpy.context.object;o.name=name;o.scale=(r,.75,r);o.data.materials.append(ma)
  for f in o.data.polygons:f.use_smooth=True
def aim(o,point):o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-700,-24));cam=bpy.context.object;aim(cam,(0,0,-24));cam.data.type='ORTHO';cam.data.ortho_scale=300
bpy.context.scene.camera=cam
def area(name,pos,energy,size):
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.name=name;o.data.energy=energy;o.data.shape='DISK';o.data.size=size;aim(o,(0,0,-20))
area('Key',(-200,-350,300),2600000,260)
area('Fill',(200,-220,70),1000000,240)
area('Rim',(80,120,180),3000000,190)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24
sc.world.color=(.18,.18,.18);sc.view_settings.view_transform='AgX'
sc.render.resolution_x=900;sc.render.resolution_y=1100;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.render.film_transparent=False
out={'vertices':[list(v.co) for v in head.data.vertices],'faces':[list(p.vertices) for p in head.data.polygons],'camera':{'ortho_scale':300,'center_z':-24,'width':900,'height':1100}}
(R/'base-geometry.json').write_text(json.dumps(out),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'base-anatomical.blend'))
sc.render.filepath=str(R/'renders/base-front.png');bpy.ops.render.render(write_still=True)
cam.location=(700*math.sin(math.radians(65)),-700*math.cos(math.radians(65)),-24);aim(cam,(0,0,-24))
sc.render.filepath=str(R/'renders/base-threequarter.png');bpy.ops.render.render(write_still=True)

