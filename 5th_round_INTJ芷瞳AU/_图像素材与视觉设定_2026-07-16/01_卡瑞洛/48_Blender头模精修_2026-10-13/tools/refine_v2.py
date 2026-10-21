import bpy,json,pathlib,math,random
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'carrillo-fitted-v1.blend'),load_ui=False)
rng=random.Random(80719)
h=bpy.data.objects['Carrillo_Head'];d=json.loads((R/'fitted-geometry-v1.json').read_text())
# Close the lip seam while preserving upper/lower lip volume.
for v in h.data.vertices:
 x,y,z=v.co
 if abs(x)<29 and y<-15:
  seam=-65.6-1.6*(abs(x)/25)**1.5
  w=math.exp(-((z-seam)/1.8)**2)*math.exp(-(abs(x)/27)**6)
  v.co.z=seam+(z-seam)*(1-.72*w)
h.data.update()
# Smooth nostril artefacts from uncertain detector/raycast points.
vg=h.vertex_groups.new(name='Nostril_cleanup')
for v in h.data.vertices:
 x,y,z=v.co
 w=math.exp(-((z+40)/10)**2)*math.exp(-((abs(x)-9)/10)**2) if y<-25 else 0
 if w>.02:vg.add([v.index],w,'REPLACE')
m=h.modifiers.new('Nostril refinement','SMOOTH');m.factor=.45;m.iterations=3;m.vertex_group=vg.name
# Stable eye spheres + curved iris, radial fibres, limbal ring and corneal coat.
for o in list(bpy.data.objects):
 if o.name.startswith(('Eye','Iris','Pupil')):bpy.data.objects.remove(o,do_unlink=True)
def material(name,col,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF')
 bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Roughness'].default_value=rough
 return m
sclera=material('Sclera_warm_offwhite',(.47,.435,.38),.26);bs=sclera.node_tree.nodes.get('Principled BSDF');bs.inputs['Coat Weight'].default_value=.35;bs.inputs['Coat Roughness'].default_value=.12
irism=material('Iris_low_saturation_gray_blue',(.12,.15,.17),.31);nt=irism.node_tree;bs=nt.nodes.get('Principled BSDF')
an=nt.nodes.new('ShaderNodeVertexColor');an.layer_name='Iris_fibres';nt.links.new(an.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Coat Weight'].default_value=.6;bs.inputs['Coat Roughness'].default_value=.12
eye_centers=[]
for side in [-1,1]:
 center=Vector((side*31.6,6.25,1.6));eye_centers.append(center)
 radius=11.7
 bpy.ops.mesh.primitive_uv_sphere_add(segments=96,ring_count=64,radius=radius,location=center)
 o=bpy.context.object;o.name='Eyeball_L' if side<0 else 'Eyeball_R';o.data.materials.append(sclera)
 for f in o.data.polygons:f.use_smooth=True
 vs=[];fs=[];cols=[];nr=32;na=128
 fibres=[rng.uniform(.62,1.4) for _ in range(na)]
 for j in range(nr+1):
  r=6.0*j/nr
  for k in range(na):
   a=k*math.tau/na
   vs.append(list(center+Vector((r*math.cos(a),-math.sqrt(radius*radius-r*r)-.04,r*math.sin(a)))))
   if r<2.1:c=(.002,.003,.004)
   else:
    edge=max(0,min(1,(6-r)/.65));inner=max(0,min(1,(r-2.1)/.8))
    f=fibres[k]*(.8+.15*math.sin(r*5+k*.11))*(.22+.78*edge)*(.55+.45*inner)
    c=(.12*f,.155*f,.17*f)
   cols.append(c)
 for j in range(nr):
  for k in range(na):
   a=j*na+k;b=j*na+(k+1)%na;fs.append((a,b,b+na,a+na))
 me=bpy.data.meshes.new('Curved_iris');me.from_pydata(vs,[],fs);me.update()
 o=bpy.data.objects.new('Iris_L' if side<0 else 'Iris_R',me);bpy.context.collection.objects.link(o);me.materials.append(irism)
 ca=me.color_attributes.new(name='Iris_fibres',type='FLOAT_COLOR',domain='POINT')
 for i,c in enumerate(cols):ca.data[i].color=(*c,1)
 for p in me.polygons:p.use_smooth=True
# Controlled texture boundary: fade before the extrapolated UV crosses the jaw/temple.
att=h.data.attributes['photo_weight']
for v in h.data.vertices:
 x,y,z=v.co
 fy=max(0,min(1,(67-y)/30))
 # prevent neck/ear background colours from the portrait bleeding into skin
 fz=max(0,min(1,(z+111)/17))
 fx=max(0,min(1,(74-abs(x))/10))
 att.data[v.index].value=fy*fz*fx
skin=h.data.materials[0];nt=skin.node_tree;bs=nt.nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.57;bs.inputs['Subsurface Weight'].default_value=.055
bs.inputs['Subsurface Radius'].default_value=(1.0,.46,.23)
noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=310;noise.inputs['Detail'].default_value=2.5;noise.inputs['Roughness'].default_value=.7
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.035
nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
# Geometry-based scalp and wave groom; all fibres rotate and relight with the head.
deps=bpy.context.evaluated_depsgraph_get();ev=h.evaluated_get(deps);mesh=ev.to_mesh()
V=[v.co.copy() for v in mesh.vertices];P=[list(p.vertices) for p in mesh.polygons]
bvh=BVHTree.FromPolygons(V,P,all_triangles=False)
origin=Vector((0,85,22))
def pmx(t):
 return 1.16+1.03*((1-math.cos(t))*.5)**.67
def sph(t,p):
 return Vector((math.sin(p)*math.sin(t),-math.sin(p)*math.cos(t),math.cos(p)))
def skinpoint(t,p):
 direction=sph(t,p)
 loc,n,ix,dist=bvh.ray_cast(origin,direction,350)
 if loc is None:return origin+Vector((direction.x*82,direction.y*110,direction.z*97)),direction
 if n.dot(direction)<0:n=-n
 return loc,n
def hairmat(name,col):
 m=material(name,col,.4);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Coat Weight'].default_value=.2
 for sock in bs.inputs:
  if sock.name.startswith('Anisotropic') and sock.type=='VALUE':sock.default_value=.45;break
 return m
hair=hairmat('Espresso_dark_hair',(.009,.006,.0045))
# scalp cap uses mesh surface, avoiding any separate helmet ellipsoid
capv=[];capf=[];capmap={}
for p in P:
 eligible=True
 for ix in p:
  q=V[ix]-origin;theta=math.atan2(q.x,-q.y);phi=math.acos(max(-1,min(1,q.z/q.length)))
  if phi>pmx(theta)+.025:eligible=False;break
 if eligible:
  pp=[]
  for ix in p:
   if ix not in capmap:
    capmap[ix]=len(capv);q=V[ix];n=(q-origin).normalized();capv.append(tuple(q+n*.3))
   pp.append(capmap[ix])
  capf.append(pp)
me=bpy.data.meshes.new('Scalp_mesh');me.from_pydata(capv,[],capf);me.update()
cap=bpy.data.objects.new('Hair_base_density',me);bpy.context.collection.objects.link(cap);me.materials.append(hair)
for p in me.polygons:p.use_smooth=True
# Actual curve geometry, clustered into wavy locks, tapered individual fibres.
cu=bpy.data.curves.new('Wave_fibres','CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=.055;cu.bevel_resolution=1;cu.resolution_u=1
ob=bpy.data.objects.new('Carrillo_wavy_groom',cu);bpy.context.collection.objects.link(ob);cu.materials.append(hair)
guides=620;children=15;steps=26
for gi in range(guides):
 theta=rng.uniform(-math.pi,math.pi)
 phi=math.acos(rng.uniform(math.cos(pmx(theta)),1))
 frontal=max(0,math.cos(theta));top=max(0,1-phi/1.5)
 dl=rng.uniform(.31,.55)+(top*.2)
 sweep=-.36*frontal*(.4+top)+rng.uniform(-.1,.1)
 phase=rng.uniform(0,math.tau);freq=rng.uniform(.7,1.5)
 coords=[];norms=[];tangents=[]
 for j in range(steps):
  t=j/(steps-1);th=theta+sweep*t+.025*math.sin(t*6+phase)*t
  ph=min(phi+dl*t,pmx(th)+.42*frontal+.12)
  p,n=skinpoint(th,ph)
  lift=.6+(8+13*top)*math.sin(math.pi*t*.9)**.85
  # lock waves in normal and tangential directions
  tangent=Vector((math.cos(th),math.sin(th),0)).normalized()
  wiggle=(1.8+2*top)*math.sin(t*math.tau*freq+phase)*math.sin(math.pi*t)
  coords.append(p+n*lift+tangent*wiggle);norms.append(n);tangents.append(tangent)
 for child in range(children):
  ox=rng.gauss(0,1.7);oy=rng.gauss(0,.8);jitter=rng.uniform(-.1,.1);length=rng.uniform(.9,1)
  sp=cu.splines.new('POLY');sp.points.add(steps-1)
  for j in range(steps):
   t=j/(steps-1)
   p=coords[j]+tangents[j]*(ox*(.7+.3*t))+norms[j]*oy
   p+=norms[j]*(.28*math.sin(t*19+child*.7)*t)
   sp.points[j].co=(*p,1);sp.points[j].radius=(.85+.3*rng.random())*(1-.86*t**2)
print('HAIR_FIBRES',len(cu.splines),flush=True)
ev.to_mesh_clear()
# Brow/lash fibres follow the existing reference brow, adding fine relief rather than changing it.
lashmat=hairmat('Brow_and_lash',(.008,.005,.004))
brow=bpy.data.curves.new('Brow_lash_fibres','CURVE');brow.dimensions='3D';brow.bevel_depth=.047;brow.bevel_resolution=1
bo=bpy.data.objects.new('Brow_lash_fibres',brow);bpy.context.collection.objects.link(bo);brow.materials.append(lashmat)
TL=np.array(d['target_lm'])
# use only tiny lash lengths; large eyelashes distort masculine eyelid shape
for ids in [[33,246,161,160,159,158,157,173,133],[263,466,388,387,386,385,384,398,362]]:
 pts=[Vector(TL[i]) for i in ids]
 for k in range(45):
  u=k/44*(len(pts)-1);i=min(int(u),len(pts)-2);t=u-i;p=pts[i].lerp(pts[i+1],t)
  sp=brow.splines.new('POLY');sp.points.add(3)
  for j in range(4):
   q=p+Vector((0,-.6-j*.25,j*.18))
   sp.points[j].co=(*q,1);sp.points[j].radius=1-j*.25
# Portrait lighting. Neutral camera keeps geometry inspectable.
sc=bpy.context.scene;cam=sc.camera;sc.cycles.samples=40;sc.cycles.use_denoising=True
sc.world.color=(.055,.055,.055);cam.data.ortho_scale=325
sc.render.resolution_x=900;sc.render.resolution_y=1100
def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.data.objects['Key'].data.energy=1950000;bpy.data.objects['Fill'].data.energy=430000;bpy.data.objects['Rim'].data.energy=1600000
for angle,elev,name in [(0,11.5,'front'),(-45,3,'threequarter'),(-90,0,'profile')]:
 a=math.radians(angle);e=math.radians(elev)
 target=Vector((0,25,-10));cam.location=target+Vector((700*math.sin(a)*math.cos(e),-700*math.cos(a)*math.cos(e),700*math.sin(e)));aim(cam,target)
 sc.render.filepath=str(R/f'renders/refined-v2-{name}.png')
 bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'carrillo-refined-v2.blend'))

