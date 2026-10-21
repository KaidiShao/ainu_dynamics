import bpy,pathlib,math,random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'carrillo-refined-v6.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head']
# Small proportional correction from aligned front-view landmarks, not a likeness score.
for v in h.data.vertices:
 x,y,z=v.co
 if z<0:
  w=math.exp(-((y+5)/100)**4)
  v.co.z=z*(1-.035*w)
  jaw=math.exp(-((z+85)/34)**4)*w
  v.co.x*=1-.047*jaw
 if y<-16:
  mouth=math.exp(-((z+66)/11)**4)*math.exp(-(x/28)**6)
  v.co.x*=1-.065*mouth
  chin=math.exp(-((z+97)/18)**4)*math.exp(-(x/27)**4)
  v.co.y+=2.4*chin
  root=math.exp(-((z-1)/14)**2)*math.exp(-(x/9)**4)
  v.co.y-=1.35*root
h.data.update()
# Sparse long front locks add the asymmetric loose fringe of the source, over the dense groom.
deps=bpy.context.evaluated_depsgraph_get();ev=h.evaluated_get(deps);mesh=ev.to_mesh()
V=[v.co.copy() for v in mesh.vertices];P=[list(p.vertices) for p in mesh.polygons];bvh=BVHTree.FromPolygons(V,P)
origin=Vector((0,85,22));rng=random.Random(92711)
cu=bpy.data.curves.new('Loose_fringe_fibres','CURVE');cu.dimensions='3D';cu.bevel_depth=.035;cu.bevel_resolution=0
o=bpy.data.objects.new('Long_loose_front_locks',cu);bpy.context.collection.objects.link(o);cu.materials.append(bpy.data.materials['Espresso_dark_hair'])
for k in range(210):
 theta=rng.uniform(-1.0,1.0);phi=rng.uniform(.67,1.12)
 direction=Vector((math.sin(phi)*math.sin(theta),-math.sin(phi)*math.cos(theta),math.cos(phi)))
 root,n,_,_=bvh.ray_cast(origin,direction,250)
 if root is None:continue
 endz=rng.uniform(22,40)+(15 if root.x>15 else 0)
 endx=root.x+rng.uniform(-18,12)
 p0=root+n*.5;p1=root+Vector((rng.uniform(-13,8),-15,20))
 p2=Vector((endx+12,-24,endz+36));p3=Vector((endx,-12,endz))
 phase=rng.uniform(-.5,.5);steps=30
 for child in range(20):
  off=Vector((rng.gauss(0,1.2),rng.gauss(0,.7),rng.gauss(0,.6)));length=rng.uniform(.8,1)
  sp=cu.splines.new('POLY');sp.points.add(steps-1)
  for j,pt in enumerate(sp.points):
   t=j/(steps-1)*length;u=1-t
   p=p0*u**3+p1*3*u*u*t+p2*3*u*t*t+p3*t**3
   p+=Vector((5*math.sin(t*math.tau+phase)*t,-3*math.sin(t*math.pi),0))+off
   pt.co=(*p,1);pt.radius=.8*(1-.999*(j/(steps-1))**1.4)
ev.to_mesh_clear()
# Preserve alternate inspection material in the .blend.
neutral=bpy.data.materials.get('Neutral_anatomy')
if not neutral:
 neutral=bpy.data.materials.new('Neutral_anatomy');neutral.use_nodes=True
 bs=neutral.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.3,.27,.25,1);bs.inputs['Roughness'].default_value=.7
neutral.use_fake_user=True;skin=h.data.materials[0];skin.use_fake_user=True
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=.001
sc.cycles.samples=24;sc.cycles.use_denoising=True
sc.render.resolution_x=760;sc.render.resolution_y=950
cam=sc.camera;cam.data.ortho_scale=305
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
for angle,elev,name in [(0,11.5,'front'),(-45,5,'threequarter'),(-75,3,'near-profile'),(-90,0,'profile')]:
 aa=math.radians(angle);e=math.radians(elev);target=Vector((0,25,-2))
 cam.location=target+Vector((700*math.sin(aa)*math.cos(e),-700*math.cos(aa)*math.cos(e),700*math.sin(e)));aim(cam,target)
 if name!='profile':
  sc.render.filepath=str(R/f'renders/refined-v7-{name}.png');bpy.ops.render.render(write_still=True)
 # Save independent named camera at every inspection angle.
 nc=cam.copy();nc.data=cam.data.copy();nc.name='View_'+name;bpy.context.collection.objects.link(nc)
h.data.materials[0]=neutral;sc.camera=bpy.data.objects['View_threequarter'];sc.render.filepath=str(R/'renders/refined-v7-neutral.png');bpy.ops.render.render(write_still=True)
h.data.materials[0]=skin;sc.camera=bpy.data.objects['View_threequarter']
sc['status']='Working likeness study; author approval pending. No claim of exact reconstruction.'
sc['references']='T22 front primary; P14 side auxiliary; F03 softer-light skin projection. Image illumination partly baked.'
sc['base_mesh']='Blender Studio Human Base Meshes v1.4.1, CC0.'
sc['scale_note']='Generic eye separation normalization, not measured anatomy.'
# Pack source images so the project opens without external texture paths.
bpy.ops.file.pack_all()
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.clip_end=10000;area.spaces.active.clip_start=.1
   area.spaces.active.region_3d.view_distance=420
   area.spaces.active.region_3d.view_location=(0,35,-5)
   area.spaces.active.shading.type='MATERIAL'
   area.spaces.active.region_3d.view_perspective='CAMERA'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_3D_working.blend'))

