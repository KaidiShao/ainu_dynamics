import bpy,math,random,json,pathlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def groom(h,R,M,lm,cam):
 rng=random.Random(20261013)
 for name in ['Carrillo_wavy_groom','Long_loose_front_locks','Hair_base_density','Brow_lash_fibres','R10_brows','R10_lashes']:
  ob=bpy.data.objects.get(name)
  if ob:bpy.data.objects.remove(ob,do_unlink=True)
 deps=bpy.context.evaluated_depsgraph_get();ev=h.evaluated_get(deps);me=ev.to_mesh()
 V=[v.co.copy() for v in me.vertices];P=[list(f.vertices) for f in me.polygons];bvh=BVHTree.FromPolygons(V,P);origin=Vector((0,85,22))
 def limit(t):return 1.12+1.00*((1-math.cos(t))*.5)**.72+.025*math.sin(t*7)
 def sph(t,p):return Vector((math.sin(p)*math.sin(t),-math.sin(p)*math.cos(t),math.cos(p)))
 def scalp(t,p):
  direction=sph(t,p);pos,n,ix,dist=bvh.ray_cast(origin,direction,350)
  if pos is None:return origin+Vector((direction.x*82,direction.y*110,direction.z*97)),direction
  if n.dot(direction)<0:n=-n
  return pos,n
 def hairmat(name,color,rough):
  m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Specular IOR Level'].default_value=.24
  return m
 hair=hairmat('R10_dark_brown_fibres',(.0038,.0019,.001),.57)
 hair.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.12
 roots=hairmat('R10_dark_brown_roots',(.004,.002,.001),.75)
 cv=[];cf=[];mp={}
 for f in P:
  if all(math.acos(max(-1,min(1,(V[i]-origin).z/(V[i]-origin).length)))<limit(math.atan2((V[i]-origin).x,-(V[i]-origin).y))-.20 for i in f):
   ff=[]
   for i in f:
    if i not in mp:mp[i]=len(cv);cv.append(tuple(V[i]+(V[i]-origin).normalized()*.35))
    ff.append(mp[i])
   cf.append(ff)
 mesh=bpy.data.meshes.new('R10_root_surface');mesh.from_pydata(cv,[],cf);mesh.update()
 ob=bpy.data.objects.new('Hair_base_density',mesh);bpy.context.collection.objects.link(ob);mesh.materials.append(roots)
 for f in mesh.polygons:f.use_smooth=True
 def curves(name,bevel):
  cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=bevel;cu.bevel_resolution=1
  ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);cu.materials.append(hair);return cu
 cu=curves('Carrillo_wavy_groom',.049);locks=curves('Long_loose_front_locks',.047)
 for gi in range(1050):
  th=rng.uniform(-math.pi,math.pi);ph=math.acos(rng.uniform(math.cos(limit(th)),1))
  top=max(0,1-ph/1.7);front=max(0,math.cos(th))
  if abs(th)<1.5:
   # Multiple locks break the uniform diagonal fringe; wave amplitudes and
   # end directions vary by root position rather than one global sweep.
   eth=th*.78-.22+rng.uniform(-.20,.20)
   eph=min(ph+rng.uniform(.34,.72),limit(eth)+rng.uniform(.04,.26))
  else:eth=th+math.copysign(rng.uniform(.04,.18),th);eph=min(ph+rng.uniform(.16,.35),limit(eth)+.10)
  phase=th*2.2+ph*4.3;freq=.9+.15*math.sin(th*2);coords=[];norms=[];tans=[];steps=30
  for j in range(steps):
   t=j/(steps-1);theta=th+(eth-th)*t+.055*math.sin(t*math.tau+phase)*math.sin(math.pi*t);phi=ph+(eph-ph)*t
   pos,n=scalp(theta,phi);tan=Vector((math.cos(theta),math.sin(theta),0))
   lift=.7+(7+18*top)*math.sin(math.pi*t*.93)**.85
   wave=(2.2+5*top)*math.sin(t*math.tau*freq+phase)*math.sin(math.pi*t)
   coords.append(pos+n*lift+tan*wave);norms.append(n);tans.append(tan)
  for ch in range(17):
   ox=rng.gauss(0,1.35);oy=rng.gauss(0,.8);end=rng.uniform(.8,1);sp=cu.splines.new('POLY');sp.points.add(steps-1)
   for j,pt in enumerate(sp.points):
    t=j/(steps-1);s=t*end*(steps-1);k=min(int(s),steps-2);f=s-k
    pos=coords[k].lerp(coords[k+1],f)+tans[k]*ox+norms[k]*oy
    pos+=tans[k]*(.3*math.sin(t*16+ch)*t);pt.co=(*pos,1);pt.radius=(.8+.3*rng.random())*(1-.985*t**2)
 # Fringe clumps with curled ends rather than a continuous solid hairline.
 for gi in range(85):
  th=rng.uniform(-1.35,1.1);ph=rng.uniform(.56,.95);eth=th-.22+rng.uniform(-.17,.17);eph=limit(eth)+rng.uniform(.18,.42)
  phase=rng.random()*math.tau;amplitude=16+7*rng.random();steps=36;coords=[];norms=[];tans=[]
  for j in range(steps):
   t=j/(steps-1);theta=th+(eth-th)*t+.08*math.sin(t*6+phase)*t;phi=ph+(eph-ph)*t
   pos,n=scalp(theta,phi);tan=Vector((math.cos(theta),math.sin(theta),0))
   lift=1+amplitude*math.sin(math.pi*t*.91)**.9
   pos+=n*lift+tan*5*math.sin(t*math.tau+phase)*math.sin(math.pi*t)
   coords.append(pos);norms.append(n);tans.append(tan)
  for ch in range(18):
   ox=rng.gauss(0,.9);oy=rng.gauss(0,.55);sp=locks.splines.new('POLY');sp.points.add(steps-1)
   for j,pt in enumerate(sp.points):
    t=j/(steps-1);pos=coords[j]+tans[j]*ox+norms[j]*oy;pt.co=(*pos,1);pt.radius=(.75+.35*rng.random())*(1-.999*t**1.6)
 # Fine true brow fibres, anchored to the fitted T22 brow bands on the mesh.
 forward=Vector(M[2]);right=Vector(M[0]);up=Vector(M[1]);scale=cam['scale_pixels_per_model_unit'];tx,ty=cam['translation']
 def refpoint(ix):
  p=lm[ix];return ((p[0]*1086-tx)/scale,(-p[1]*1448-ty)/scale)
 def hit(q):
  pos,n,ix,dist=bvh.ray_cast(right*q[0]+up*q[1]+forward*350,-forward,700)
  return pos,n
 brow=curves('R10_brows',.043)
 for top,bottom in [([70,63,105,66,107],[46,53,52,65,55]),([300,293,334,296,336],[276,283,282,295,285])]:
  aa=[Vector(refpoint(i)) for i in top];bb=[Vector(refpoint(i)) for i in bottom]
  for k in range(430):
   u=rng.uniform(0,3.99);i=int(u);f=u-i;a=aa[i].lerp(aa[i+1],f);b=bb[i].lerp(bb[i+1],f);q=a.lerp(b,rng.random())
   pos,n=hit(q)
   if pos is None:continue
   sg=-1 if q.x<0 else 1;dir=right*(sg*rng.uniform(.7,1.5))+up*rng.uniform(.7,1.3)
   sp=brow.splines.new('POLY');sp.points.add(3)
   for j,pt in enumerate(sp.points):
    t=j/3;pp=pos+n*(.12+.12*math.sin(math.pi*t))+dir*t;pt.co=(*pp,1);pt.radius=1-.95*t
 ev.to_mesh_clear()
 print('R10_GROOM',len(cu.splines),len(locks.splines),len(brow.splines),flush=True)
