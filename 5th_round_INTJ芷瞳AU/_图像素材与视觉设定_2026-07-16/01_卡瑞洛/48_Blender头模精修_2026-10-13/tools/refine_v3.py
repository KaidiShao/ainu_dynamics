import bpy,pathlib,math,random,json
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'carrillo-refined-v2.blend'),load_ui=False)
# Hair shader is independent of skin and does not produce plastic scalp glare.
m=bpy.data.materials['Espresso_dark_hair'];bs=m.node_tree.nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.82;bs.inputs['Coat Weight'].default_value=0;bs.inputs['Specular IOR Level'].default_value=.12
# cap must never inherit a glossy fibre shader
capmat=m.copy();capmat.name='Matte_dense_hair_roots';bpy.data.objects['Hair_base_density'].data.materials[0]=capmat
nt=m.node_tree;nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial');hair=nt.nodes.new('ShaderNodeBsdfHairPrincipled');hair.parametrization='COLOR'
hair.inputs['Color'].default_value=(.012,.006,.0035,1);hair.inputs['Roughness'].default_value=.42
if 'Radial Roughness' in hair.inputs:hair.inputs['Radial Roughness'].default_value=.55
nt.links.new(hair.outputs[0],out.inputs['Surface'])
# Variable strand endings break up cut-edge bundles. Fine fibres curl independently within each lock.
cu=bpy.data.objects['Carrillo_wavy_groom'].data
rng=random.Random(80922)
for sp in cu.splines:
 old=[p.co.copy() for p in sp.points];n=len(old);length=rng.uniform(.64,1)
 amplitude=rng.uniform(.2,1.35);phase=rng.uniform(0,math.tau)
 for j,p in enumerate(sp.points):
  t=j/(n-1);f=t*length*(n-1);k=min(int(f),n-2);q=old[k].lerp(old[k+1],f-k)
  q.x+=amplitude*math.sin(t*8+phase)*t
  q.z+=amplitude*.6*math.sin(t*11+phase)*t
  p.co=q;p.radius=(.7+.25*rng.random())*(1-.998*t**1.6)
cu.bevel_depth=.038
# Match the low-saturation eye reference: more iris depth, less luminous grey.
for name in ['Iris_L','Iris_R']:
 o=bpy.data.objects[name]
 for c in o.data.color_attributes['Iris_fibres'].data:
  col=c.color
  if max(col[:3])>.008:c.color=(col[0]*.53,col[1]*.51,col[2]*.50,1)
# Sculpt small residual geometry differences from the neutral base.
h=bpy.data.objects['Carrillo_Head']
for v in h.data.vertices:
 x,y,z=v.co
 # flatten overly globular nasal tip/ala slightly, leave nostril apertures intact
 if y<-25:
  w=math.exp(-((z+34)/12)**2)*math.exp(-(x/18)**4)
  v.co.x=x*(1-.045*w)
 # narrow eye aperture through upper lid only, no brow scowl
 if abs(x)>18 and abs(x)<46 and y<8:
  w=math.exp(-((z-6.5)/3.6)**2)*math.exp(-((abs(x)-32)/12)**4)
  v.co.z-=.65*w
 # soften broad chin pad, retain mentolabial continuity
 if z<-82 and y<12:
  w=math.exp(-((z+99)/15)**2)*math.exp(-(x/35)**4)
  v.co.x*=1-.035*w
h.data.update()
# Wardrobe: a quiet black high collar follows the lower neck to support the bust silhouette.
cloth=bpy.data.materials.new('Charcoal_fabric');cloth.use_nodes=True;bs=cloth.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.008,.009,.011,1);bs.inputs['Roughness'].default_value=.88
# use actual shoulder/neck geometry as a fitted cloth shell, rather than unrelated primitives
verts=[];faces=[];mp={}
for poly in h.data.polygons:
 if max(h.data.vertices[i].co.z for i in poly.vertices)<-155:
  p=[]
  for i in poly.vertices:
   if i not in mp:
    mp[i]=len(verts);v=h.data.vertices[i].co.copy();v.x*=1.07;v.y=70+(v.y-70)*1.065
    verts.append(v)
   p.append(mp[i])
  faces.append(p)
me=bpy.data.meshes.new('Collar_and_shoulders');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Dark_collar',me);bpy.context.collection.objects.link(o);me.materials.append(cloth)
for f in me.polygons:f.use_smooth=True
mod=o.modifiers.new('Tailored_surface','SUBSURF');mod.levels=2
# Camera and lighting
sc=bpy.context.scene;sc.cycles.samples=48;sc.cycles.use_denoising=True;sc.view_settings.exposure=-.45
sc.world.color=(.018,.018,.018)
key=bpy.data.objects['Key'];key.location=(200,-310,240);key.data.energy=1900000;key.data.size=210
fill=bpy.data.objects['Fill'];fill.location=(-230,-200,60);fill.data.energy=330000;fill.data.size=240
rim=bpy.data.objects['Rim'];rim.data.energy=950000;rim.data.size=170
cam=sc.camera;cam.data.ortho_scale=325
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for o in [key,fill,rim]:aim(o,(0,10,-10))
for angle,elev,name in [(0,11.5,'front'),(-45,3,'threequarter'),(-56,-1,'side-reference')]:
 a=math.radians(angle);e=math.radians(elev);target=Vector((0,25,-10))
 cam.location=target+Vector((700*math.sin(a)*math.cos(e),-700*math.cos(a)*math.cos(e),700*math.sin(e)));aim(cam,target)
 sc.render.filepath=str(R/f'renders/refined-v3-{name}.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'carrillo-refined-v3.blend'))

