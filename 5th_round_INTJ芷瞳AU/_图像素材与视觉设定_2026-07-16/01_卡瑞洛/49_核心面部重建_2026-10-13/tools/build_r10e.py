import bpy,pathlib,json,numpy as np,math
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10D.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];kb=h.data.shape_keys.key_blocks;V=np.array([v.co[:] for v in kb[0].data])
for k in list(kb)[1:]:V+=(np.array([v.co[:] for v in k.data])-np.array([v.co[:] for v in k.relative_key.data]))*k.value
M=np.array(json.loads((R/'structure-r10.json').read_text())['M']);fwd=M[2];up=M[1]
eyes=np.array(json.loads((R/'r10c-manifest.json').read_text())['eyes'])
mirror=np.array([np.linalg.norm(V-p*[-1,1,1],axis=1).argmin() for p in V])
W=V.copy()
upper=[1813,2404,1818,1814,1815];body=[2335,2401,1838,1839,1840];hood=[1943,1942,2264,2263,1911]
for ids,drop in [(upper,1.2),(body,.65),(hood,.25)]:
 for i in ids:
  for j in [i,int(mirror[i])]:
   W[j]-=up*drop
   c=eyes[0 if W[j,0]<0 else 1];v=W[j]-c;dot=v@fwd;radius=12.02 if ids==upper else 12.32
   disc=dot*dot-v@v+radius*radius
   if disc>0:W[j]+=fwd*max(0,-dot+math.sqrt(disc))
# Smooth upper outer lip relief once more, with full support across the mouth.
for i,(x,y,z) in enumerate(V):
 if not (abs(x)<26 and -64<z<-50 and y<-12):continue
 zz=np.array([-64,-62,-60,-57,-55,-52,-50]);yy=np.array([-29.,-30.,-30.6,-30.5,-29.8,-28.,-27.])
 target=float(np.interp(z,zz,yy))+.028*x*x
 if y<target+3.5:
  wt=math.exp(-(x/22)**6)*min(1,(-50-z)/3)*min(1,(z+64)/2)
  W[i,1]+=max(-2,min(2,target-y))*wt*.75
# Spread each lid edit through the adjoining lid thickness before checking
# winding; moving only the visible lip of the opening can pinch its inner wall.
adj=[set() for _ in V];tri=[]
for f in h.data.polygons:
 ids=list(f.vertices)
 for i in ids:adj[i].update(ids)
 for j in range(1,len(ids)-1):tri.append([ids[0],ids[j],ids[j+1]])
tri=np.array(tri);delta=W-V
for it in range(2):
 out=delta.copy()
 for i,p in enumerate(V):
  if 15<abs(p[0])<50 and -1<p[2]<14 and p[1]<24:out[i]=.65*delta[i]+.35*np.mean([delta[j] for j in adj[i]],axis=0)
 delta=out
W=V+delta
def normals(v):return np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])
n0=normals(V);proposal=W.copy();weights=np.ones(len(V))
for it in range(30):
 n1=normals(W);valid=(np.linalg.norm(n0,axis=1)>1e-5)&(np.linalg.norm(n1,axis=1)>1e-5);bad=np.where((np.sum(n0*n1,axis=1)<0)&valid)[0]
 if not len(bad):break
 ids=set(tri[bad].ravel())
 for i in list(ids):ids.update(adj[i])
 for i in ids:weights[i]*=.78
 W=V+(proposal-V)*weights[:,None]
h.shape_key_clear()
for v,p in zip(h.data.vertices,V):v.co=p
h.shape_key_add(name='R10D_preserved');key=h.shape_key_add(name='R10E_relaxed_upper_lid_and_lip_surface')
for v,p in zip(key.data,W):v.co=p
key.value=1;h.data.update()
# Slim true eyelashes on the external margin, following the existing anatomy.
mat=bpy.data.materials.new('R10E_lash_dark_brown');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.009,.004,.002,1);bs.inputs['Roughness'].default_value=.7
cu=bpy.data.curves.new('R10E_upper_lashes','CURVE');cu.dimensions='3D';cu.bevel_depth=.049;cu.bevel_resolution=1
ob=bpy.data.objects.new('R10E_upper_lashes',cu);bpy.context.collection.objects.link(ob);cu.materials.append(mat)
for side in [1,-1]:
 ids=[1819,1813,2404,1818,1814,1815,1816];ids=ids if side==1 else [int(mirror[i]) for i in ids]
 for idx in range(len(ids)-1):
  for k in range(6):
   t=(k+.3)/6;pos=Vector(W[ids[idx]]).lerp(Vector(W[ids[idx+1]]),t)
   direction=Vector(fwd)*.55+Vector(M[0])*(side*.28)-Vector(up)*.32
   sp=cu.splines.new('POLY');sp.points.add(3)
   for j,p in enumerate(sp.points):
    u=j/3;pp=pos+Vector(fwd)*.16+direction*u+Vector(up)*.20*u*u;p.co=(*pp,1);p.radius=1-.96*u
# Restore some of the broad eyebrow mass, keeping the actual brow fibres.
attr=h.data.attributes.get('brow_photo_mix')
if attr:
 for a in attr.data:a.value*=.32
sc=bpy.context.scene;sc.cycles.samples=32;sc.camera=bpy.data.objects['Core_T22_pose'];skin=h.data.materials[0]
neutral=bpy.data.materials['Neutral_anatomy'].copy();neutral.name='R10E_neutral_anatomy';neutral.use_fake_user=True
nn=neutral.node_tree;nbs=nn.nodes.get('Principled BSDF');na=nn.nodes.new('ShaderNodeAttribute');na.attribute_name='scalp_cover';nm=nn.nodes.new('ShaderNodeMixRGB');nm.inputs[1].default_value=nbs.inputs['Base Color'].default_value;nm.inputs[2].default_value=(.0035,.0018,.001,1);nn.links.new(na.outputs['Fac'],nm.inputs[0]);nn.links.new(nm.outputs[0],nbs.inputs['Base Color'])
tri=[]
for f in h.data.polygons:
 ids=list(f.vertices)
 for j in range(1,len(ids)-1):tri.append([ids[0],ids[j],ids[j+1]])
tri=np.array(tri)
def norms(v):return np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])
n0=norms(V);n1=norms(W);valid=(np.linalg.norm(n0,axis=1)>1e-5)&(np.linalg.norm(n1,axis=1)>1e-5);bad=np.where((np.sum(n0*n1,axis=1)<0)&valid)[0]
report={'version':'R10E','finite':bool(np.isfinite(W).all()),'normal_rotations_over_90deg':int(len(bad)),'max_displacement_from_R10D':float(np.linalg.norm(W-V,axis=1).max()),'status':'Internal visual review'}
if len(bad):raise RuntimeError('New inverted triangles: '+str(tri[bad].tolist()))
(R/'r10e-manifest.json').write_text(json.dumps(report,indent=2))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10E.blend'))
for cname,tag,mat in [('Core_T22_pose','front-soft',skin),('Core_T22_pose','front-neutral',neutral),('Core_P14_pose','p14-neutral',neutral),('Core_P14_pose','p14',skin),('View_threequarter','threequarter',skin)]:
 sc.camera=bpy.data.objects[cname];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/r10e-{tag}.png');bpy.ops.render.render(write_still=True)
keylight=bpy.data.objects['Key'];keylight.location=(320,-140,160);keylight.rotation_euler=(Vector((0,0,-20))-keylight.location).to_track_quat('-Z','Y').to_euler();keylight.data.energy=1300000;keylight.data.size=85
bpy.data.objects['Fill'].data.energy=45000
sc.camera=bpy.data.objects['Core_T22_pose'];h.data.materials[0]=skin;sc.render.filepath=str(R/'renders/r10e-front.png');bpy.ops.render.render(write_still=True)
print('R10E_DONE',json.dumps(report),flush=True)
