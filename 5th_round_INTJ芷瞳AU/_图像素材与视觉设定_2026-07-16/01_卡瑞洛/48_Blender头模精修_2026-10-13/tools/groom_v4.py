import bpy,math,random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def groom():
 rng=random.Random(74133)
 h=bpy.data.objects['Carrillo_Head']
 for name in ['Carrillo_wavy_groom','Hair_base_density','Dark_collar']:
  o=bpy.data.objects.get(name)
  if o:bpy.data.objects.remove(o,do_unlink=True)
 deps=bpy.context.evaluated_depsgraph_get();ev=h.evaluated_get(deps);mesh=ev.to_mesh()
 V=[v.co.copy() for v in mesh.vertices];P=[list(p.vertices) for p in mesh.polygons];bvh=BVHTree.FromPolygons(V,P)
 origin=Vector((0,85,22))
 def pmx(t):return 1.09+1.05*((1-math.cos(t))*.5)**.67
 def sph(t,p):return Vector((math.sin(p)*math.sin(t),-math.sin(p)*math.cos(t),math.cos(p)))
 def skinpoint(t,p):
  direction=sph(t,p);loc,n,ix,dist=bvh.ray_cast(origin,direction,350)
  if loc is None:return origin+Vector((direction.x*82,direction.y*110,direction.z*97)),direction
  if n.dot(direction)<0:n=-n
  return loc,n
 # matte dark cap restricted to the roots, beneath the natural hairline
 mat=bpy.data.materials['Matte_dense_hair_roots'];bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.0012,.0008,.0006,1);bs.inputs['Specular IOR Level'].default_value=.02
 cv=[];cf=[];mp={}
 for poly in P:
  okay=True
  for ix in poly:
   q=V[ix]-origin;th=math.atan2(q.x,-q.y);ph=math.acos(max(-1,min(1,q.z/q.length)))
   if ph>pmx(th)-.2:okay=False;break
  if okay:
   face=[]
   for ix in poly:
    if ix not in mp:
     mp[ix]=len(cv);q=V[ix];cv.append(tuple(q+(q-origin).normalized()*.35))
    face.append(mp[ix])
   cf.append(face)
 me=bpy.data.meshes.new('Hair_roots_surface');me.from_pydata(cv,[],cf);me.update()
 cap=bpy.data.objects.new('Hair_base_density',me);bpy.context.collection.objects.link(cap);me.materials.append(mat)
 for f in me.polygons:f.use_smooth=True
 hair=bpy.data.materials['Espresso_dark_hair'];nt=hair.node_tree;nt.nodes.clear()
 out=nt.nodes.new('ShaderNodeOutputMaterial');pr=nt.nodes.new('ShaderNodeBsdfHairPrincipled');pr.parametrization='COLOR';pr.inputs['Color'].default_value=(.0018,.001,.00055,1);pr.inputs['Roughness'].default_value=.55
 diff=nt.nodes.new('ShaderNodeBsdfDiffuse');diff.inputs['Color'].default_value=(.003,.0018,.001,1);diff.inputs['Roughness'].default_value=.8
 mix=nt.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.62;nt.links.new(pr.outputs[0],mix.inputs[1]);nt.links.new(diff.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
 cu=bpy.data.curves.new('Fine_waves','CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=.035;cu.bevel_resolution=0
 ob=bpy.data.objects.new('Carrillo_wavy_groom',cu);bpy.context.collection.objects.link(ob);cu.materials.append(hair)
 # Dense covering layer, with the longer top swept in coherent S waves.
 guides=2000;children=19;steps=26
 for gi in range(guides):
  th=rng.uniform(-math.pi,math.pi);ph=math.acos(rng.uniform(math.cos(pmx(th)),1))
  frontal=max(0,math.cos(th));top=max(0,1-ph/1.65)
  if abs(th)<1.65:
   endth=th*.65-.48
   endph=min(ph+rng.uniform(.36,.73),pmx(endth)+rng.uniform(.12,.3))
  else:
   endth=th+math.copysign(rng.uniform(.1,.3),th);endph=min(ph+rng.uniform(.18,.4),pmx(endth)+.09)
  phase=rng.uniform(0,math.tau);c=[];nms=[];tgs=[]
  for j in range(steps):
   t=j/(steps-1);theta=th+(endth-th)*t+.075*math.sin(t*math.tau*1.35+phase)*math.sin(math.pi*t)
   phi=ph+(endph-ph)*t
   p,n=skinpoint(theta,phi);tan=Vector((math.cos(theta),math.sin(theta),0)).normalized()
   lift=.45+(5+12*top)*math.sin(math.pi*t*.98)**.9
   wave=(2+3.5*top)*math.sin(t*math.tau*1.5+phase)*math.sin(math.pi*t)
   c.append(p+n*lift+tan*wave);nms.append(n);tgs.append(tan)
  for ch in range(children):
   length=rng.uniform(.62,1);ox=rng.gauss(0,1.55);oy=rng.gauss(0,.65);phase2=rng.random()*math.tau
   sp=cu.splines.new('POLY');sp.points.add(steps-1)
   for j,pt in enumerate(sp.points):
    t=j/(steps-1);f=t*length*(steps-1);k=min(int(f),steps-2);mix=f-k
    p=c[k].lerp(c[k+1],mix)+tgs[k]*ox+nms[k]*oy
    p+=tgs[k]*(.35*math.sin(t*16+phase2)*t)
    pt.co=(*p,1);pt.radius=(.75+.3*rng.random())*(1-.998*t**1.5)
 ev.to_mesh_clear()
 print('GROOM_V4',len(cu.splines),'fibres',flush=True)

