import bpy,pathlib,math
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'carrillo-refined-v5.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head']
# Restore the softer-light source. Side-only dark seams were baked photograph edges, not sculpting.
with bpy.data.libraries.load(str(R/'carrillo-refined-v4.blend'),link=False) as (src,dst):
 dst.materials=['Neutral_skin']
mat=dst.materials[0];mat.name='Carrillo_soft_reference_skin';mat.use_fake_user=True
nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.64;bs.inputs['Specular IOR Level'].default_value=.25
bs.inputs['Subsurface Weight'].default_value=.07
for node in nt.nodes:
 if node.type=='MIX_RGB' and node.blend_type=='MIX':
  node.inputs[1].default_value=(.27,.147,.094,1)
# Use reference texture in the central features, fade uncertain silhouette regions gracefully.
att=h.data.attributes['photo_weight']
for v in h.data.vertices:
 x,y,z=v.co
 lateral=max(0,min(1,(74-abs(x))/30))
 depth=max(0,min(1,(65-y)/45))
 lower=max(0,min(1,(z+112)/26))
 att.data[v.index].value=lateral*depth*lower
for node in nt.nodes:
 if node.type=='TEX_NOISE':node.inputs['Scale'].default_value=1250
h.data.materials[0]=mat
# Anatomically gentle lid settling between v3 and v5.
for v in h.data.vertices:
 x,y,z=v.co
 if 16<abs(x)<48 and y<15:
  taper=math.exp(-((abs(x)-32)/8.5)**4)
  v.co.z+=.55*math.exp(-((z-4.8)/3.6)**2)*taper
h.data.update()
sc=bpy.context.scene;sc.cycles.samples=20;sc.cycles.use_denoising=True
sc.render.resolution_x=760;sc.render.resolution_y=950
sc.view_settings.exposure=-.45
sc.world.color=(.025,.025,.025)
key=bpy.data.objects['Key'];key.location=(210,-340,180);key.data.energy=1600000;key.data.size=250
fill=bpy.data.objects['Fill'];fill.location=(-220,-250,80);fill.data.energy=520000
rim=bpy.data.objects['Rim'];rim.data.energy=700000
cam=sc.camera;cam.data.ortho_scale=305
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for o in [key,fill,rim]:aim(o,(0,0,-10))
for angle,elev,name in [(0,11.5,'front'),(-45,5,'threequarter'),(-75,3,'near-profile')]:
 aa=math.radians(angle);e=math.radians(elev);target=Vector((0,25,-2))
 cam.location=target+Vector((700*math.sin(aa)*math.cos(e),-700*math.cos(aa)*math.cos(e),700*math.sin(e)));aim(cam,target)
 sc.render.filepath=str(R/f'renders/refined-v6-{name}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'carrillo-refined-v6.blend'))

