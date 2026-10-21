import bpy,pathlib,json,math
import numpy as np
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R5.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];keys=h.data.shape_keys.key_blocks
original=np.array([v.co[:] for v in keys[0].data])
for k in list(keys)[1:]:original+=(np.array([p.co[:] for p in k.data])-np.array([p.co[:] for p in k.relative_key.data]))*k.value
h.shape_key_clear()
for v,p in zip(h.data.vertices,original):v.co=p
h.shape_key_add(name='R5_preserved_baseline')
def g(v,c,w,p=2):return math.exp(-abs((v-c)/w)**p)
def s(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def stage(name,fn):
 prev=h.data.shape_keys.key_blocks[-1];k=h.shape_key_add(name=name,from_mix=True);k.relative_key=prev
 before=np.array([v.co[:] for v in k.data])
 for v,p in zip(k.data,before):v.co=p+np.array(fn(*p))
 k.value=1
 after=np.array([v.co[:] for v in k.data]);delta=np.linalg.norm(after-before,axis=1)
 return after,{'name':name,'moved_vertices':int(sum(delta>.01)),'max_displacement':float(delta.max()),'mean_among_moved':float(delta[delta>.01].mean())}
def jaw(x,y,z):
 a=abs(x);sgn=1 if x>=0 else -1;front=1-s(42,80,y)
 # Support the posterior mandibular turn; do not reduce the whole jaw width.
 corner=g(a,51,12,4)*g(y,34,23,4)*g(z,-80,15,4)
 dx=sgn*2.35*corner;dy=1.25*corner;dz=-.65*corner
 # A broad, softly bounded side plane connects zygoma and mandibular body.
 plane_x=.264*y+.266*z+63.4
 region=s(35,48,a)*(1-s(61,72,a))*g(z,-60,24,4)*g(y,20,35,4)
 dx+=sgn*max(-1.8,min(1.0,plane_x-a))*.70*region
 # Retain a small zygomatic support above the submalar plane.
 zy=g(a,52,12,4)*g(y,4,18,4)*g(z,-25,12)
 dx+=sgn*.65*zy;dy-=.90*zy
 sub=g(a,43,14,4)*g(y,-1,19,4)*g(z,-48,14)
 dy+=1.30*sub
 # Reduce the rolled underside of the chin while preserving its front apex.
 lower=g(x,0,31,4)*g(z,-105,10)*g(y,0,25,4)
 dz+=1.0*lower
 lateral_chin=g(a,25,13)*g(z,-94,14)*g(y,-13,18)
 dx-=sgn*.60*lateral_chin;dy+=.45*lateral_chin
 return dx,dy,dz
def orbit(x,y,z):
 a=abs(x);front=1-s(0,16,y)
 # Orbital roof, crease and eyelid are separate, gently blended regions.
 roof=g(a,31,17,4)*g(z,15,6.8)*front
 crease=g(a,32,13,4)*g(z,8.8,2.2)*g(y,-6,10)
 upper=g(a,32,10.5,4)*g(z,4.8,2.1)*g(y,-6,6)
 lower=g(a,31,10,4)*g(z,-1.9,2.2)*g(y,-6,6)
 dy=-1.10*roof+.65*crease-.22*upper
 dz=-.30*upper+.22*lower
 # Mild lateral support, leaving inner and outer corner positions nearly fixed.
 under=g(a,37,12)*g(z,-8,4)*g(y,-5,9)
 dy+=.35*under
 return 0,dy,dz
def nose_mouth(x,y,z):
 a=abs(x);front=1-s(-1,13,y)
 root=g(x,0,7.5,4)*g(z,-1,10)*front
 tip=g(x,0,13,4)*g(z,-35,8)*front
 alar=g(a,14,5)*g(z,-40,5)*front
 dx=-x*.022*tip;dy=-.65*root+.55*tip+.40*alar;dz=-.30*tip
 oral=g(x,0,22,4)*g(z,-61,13,4)*front
 lower_lip=g(x,0,17,4)*g(z,-70,4)*front
 groove=g(x,0,21,4)*g(z,-79,6)*front
 dy+=.48*oral+.28*lower_lip-.65*groove
 return dx,dy,dz
stats=[]
for name,fn in [('R6_01_zygomatic_mandibular_chin_relation',jaw),('R6_02_orbital_roof_and_lid_wrap',orbit),('R6_03_nasal_oral_continuity',nose_mouth)]:
 current,st=stage(name,fn);stats.append(st)
# Keep iris pigment unchanged; restore restrained, sharper surface reflections.
iris=bpy.data.materials['Core_R4_iris'].copy();iris.name='R6_gray_blue_iris_surface'
bs=iris.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.085;bs.inputs['Specular IOR Level'].default_value=.20
for name in ['Iris_L','Iris_R']:bpy.data.objects[name].data.materials[0]=iris
sc=bpy.context.scene;sc.cycles.samples=20;sc.camera=bpy.data.objects['Core_T22_pose']
skin=h.data.materials[0];neutral=bpy.data.materials['Neutral_anatomy'];skin.use_fake_user=True
sc['status']='R6 relational sculpt from R5. Three separately editable anatomical corrections. Author approval pending.'
sc['scope']='Zygoma-jaw-chin relationship, orbital roof and eyelids, nose-mouth transitions. Reference identity remains T22; hair and cameras unchanged.'
# Check local triangle orientation and edge scale against the preserved R5.
tris=[];edges=set()
for p in h.data.polygons:
 ids=list(p.vertices)
 for a,b in zip(ids,ids[1:]+ids[:1]):edges.add(tuple(sorted((a,b))))
 for j in range(1,len(ids)-1):tris.append([ids[0],ids[j],ids[j+1]])
tri=np.array(tris);edge=np.array(sorted(edges))
def normals(v):return np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])
n0,n1=normals(original),normals(current);len0=np.linalg.norm(n0,axis=1);len1=np.linalg.norm(n1,axis=1);valid=(len0>1e-5)&(len1>1e-5)
cos=np.sum(n0[valid]*n1[valid],axis=1)/(len0[valid]*len1[valid]);l0=np.linalg.norm(original[edge[:,0]]-original[edge[:,1]],axis=1);l1=np.linalg.norm(current[edge[:,0]]-current[edge[:,1]],axis=1);ratio=l1[l0>1e-5]/l0[l0>1e-5]
report={'version':'R6','status':'working candidate; not author-approved','stages':stats,'finite':bool(np.isfinite(current).all()),'triangles_reversed_relative_to_R5':int(sum(cos<0)),'edge_scale_range':[float(ratio.min()),float(ratio.max())],'max_total_displacement':float(np.linalg.norm(current-original,axis=1).max()),'limits':['Geometry checks are not likeness verification','F03 projection contains photographic illumination','T22 and P14 are not calibrated stereo views','Hair is inherited and remains unapproved']}
(R/'core-r6-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if not report['finite'] or report['triangles_reversed_relative_to_R5']:raise RuntimeError('Deformation validation failed')
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R6.blend'))
for camera,tag,mat in [('View_threequarter','neutral',neutral),('Core_T22_pose','front-neutral',neutral),('Core_T22_pose','front',skin),('View_near-profile','near-profile',skin),('View_threequarter','threequarter',skin)]:
 sc.camera=bpy.data.objects[camera];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/core-r6-{tag}.png');bpy.ops.render.render(write_still=True)
h.data.materials[0]=skin;sc.camera=bpy.data.objects['Core_T22_pose'];print('R6_DONE',json.dumps(report),flush=True)
