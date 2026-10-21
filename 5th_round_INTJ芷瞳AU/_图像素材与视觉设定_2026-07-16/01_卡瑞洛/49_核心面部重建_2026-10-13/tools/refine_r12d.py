import bpy,pathlib,numpy as np,json,random,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R12D0.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];P=np.load(R/'depth-r12/warped-prior.npz');M=P['M'];q=P['landmark_q'];fw=Vector(M[2]);right=Vector(M[0]);up=Vector(M[1]);V=np.array([v.co[:] for v in h.data.vertices]);Q=V@M[:2].T;W=V.copy()
def smooth(v):
 v=np.clip(v,0,1);return v*v*(3-2*v)
front=smooth((25-V[:,1])/18)
# Fair the imported labiomental and outer-canthal depth only; keep the frontal outline.
edge=np.array([e.vertices[:] for e in h.data.edges]);a=np.r_[edge[:,0],edge[:,1]];b=np.r_[edge[:,1],edge[:,0]];counts=np.bincount(a,minlength=len(V));depth=V@M[2]
rel=Q-(q[13]+q[14])/2
fair=np.exp(-(rel[:,0]/28)**6-((rel[:,1]+17)/11)**4)*front*.42
for center,outer in zip(q[[468,473]],q[[33,263]]):
 rr=Q-outer;local=np.exp(-(rr[:,0]/7.0)**4-((rr[:,1]+4)/8.0)**4)
 e=Q-center;ellipse=np.sqrt((e[:,0]/14.5)**2+(e[:,1]/5.8)**2)
 fair=np.maximum(fair,.36*local*smooth((ellipse-1.04)/.50)*front)
for it in range(55):
 mean=np.bincount(a,weights=depth[b],minlength=len(V))/np.maximum(counts,1)
 depth+=(mean-depth)*fair
W+=(depth-V@M[2])[:,None]*M[2]

for j,c in enumerate(q[[468,473]]):
 rel=Q-c;xx=rel[:,0];yy=rel[:,1];across=np.exp(-(xx/12.8)**6)
 # Correct measured post-subdivision upper aperture drift, keeping the globe fixed.
 close=-(.72 if j==0 else .32)*np.exp(-((yy-3.3)/3.3)**4)*across*front
 W+=close[:,None]*M[1]
 # A modest upper lid roll followed by a shallow fold; retain lower eyelid support.
 relief=(.72*np.exp(-((yy-5.3)/2.4)**2)-.28*np.exp(-((yy-9.0)/2.0)**2))*across*front
 relief+=.25*np.exp(-((yy+6.1)/1.7)**2)*across*front
 W+=relief[:,None]*M[2]
for v,p in zip(h.data.vertices,W):v.co=p
h.data.update()
# Remove baked old fringe marks from forehead albedo. Real fibres remain separate geometry.
photo=h.data.attributes.get('photo_weight')
for i,v in enumerate(h.data.vertices):
 fade=smooth((Q[i,1]-11)/9)*smooth((70-abs(v.co.x))/12)*smooth((40-v.co.y)/15)
 photo.data[i].value*=1-fade
# Fine natural brow flow: ascending inner hairs, outward mid-brow, flattening tails.
old=bpy.data.objects['R10_brows'];mat=old.data.materials[0];bpy.data.objects.remove(old,do_unlink=True)
cu=bpy.data.curves.new('R12_natural_brow_fibres','CURVE');cu.dimensions='3D';cu.bevel_depth=.032;cu.bevel_resolution=1;cu.resolution_u=1;cu.materials.append(mat)
ob=bpy.data.objects.new('R10_brows',cu);bpy.context.collection.objects.link(ob)
bvh=BVHTree.FromPolygons([v.co[:] for v in h.data.vertices],[list(f.vertices) for f in h.data.polygons]);rng=random.Random(271)
for top,bottom in [([107,66,105,63,70],[55,65,52,53,46]),([336,296,334,293,300],[285,295,282,283,276])]:
 aa=[Vector(q[i]) for i in top];bb=[Vector(q[i]) for i in bottom]
 for k in range(1450):
  u=rng.uniform(.01,3.95);i=int(u);f=u-i;cross=rng.betavariate(1.3,1.3);qq=aa[i].lerp(aa[i+1],f).lerp(bb[i].lerp(bb[i+1],f),cross)
  side=-1 if qq.x<0 else 1
  length=rng.uniform(2.4,4.0);angle=1.0-.95*min(1,u/2.5)+rng.gauss(0,.16)
  direction=Vector((side*math.cos(angle),math.sin(angle)))*length
  sp=cu.splines.new('POLY');sp.points.add(5)
  for j,pt in enumerate(sp.points):
   t=j/5;xy=qq+direction*t;origin=right*xy.x+up*xy.y+fw*300;pos,n,ix,dist=bvh.ray_cast(origin,-fw,600)
   if pos is None:pos=origin-fw*300;n=fw
   pt.co=(*(pos+n*(.065+.11*math.sin(math.pi*t))),1);pt.radius=(.7+rng.random()*.35)*(1-.98*t**1.5)
# Existing frontal locks droop as irregular groups instead of adding evenly spaced curls.
locks=bpy.data.objects.get('Long_loose_front_locks')
if locks:
 for index,sp in enumerate(locks.data.splines):
  group=index//18;drop=4.5+4*math.sin(group*1.79)**2
  for j,pt in enumerate(sp.points):
   t=j/max(1,len(sp.points)-1);p=Vector(pt.co[:3]);p-=up*(drop*t**2.6);p+=fw*(.6*t**2);pt.co=(*p,1)
# Use the T22 camera elevation and roll for the intermediate rotation.
from mathutils import Matrix
rot=Matrix.Rotation(math.radians(32),3,'Z');base=bpy.data.objects['Core_T22_pose'];cam3=bpy.data.objects['View_threequarter'];center=Vector((0,25,-2));cam3.location=center+rot@(base.location-center);cam3.rotation_euler=(rot@base.rotation_euler.to_matrix()).to_euler();cam3.data.ortho_scale=305
sc=bpy.context.scene;sc.cycles.samples=24;sc.render.threads_mode='FIXED';sc.render.threads=6
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R12D.blend'))
skin=h.data.materials[0];neutral=bpy.data.materials['R10E_neutral_anatomy']
for cam,tag,mat in [('Core_T22_pose','front',skin),('Core_T22_pose','front-neutral',neutral),('View_threequarter','threequarter',skin),('Core_P14_pose','side',skin),('Core_P14_pose','side-neutral',neutral)]:
 sc.camera=bpy.data.objects[cam];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/r12d-{tag}.png');bpy.ops.render.render(write_still=True)
print('R12D_DONE',flush=True)
