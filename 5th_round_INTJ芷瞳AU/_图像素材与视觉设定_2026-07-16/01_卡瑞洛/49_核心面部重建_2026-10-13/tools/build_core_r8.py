import bpy,pathlib,json,math,numpy as np
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R7.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];kb=h.data.shape_keys.key_blocks
original=np.array([v.co[:] for v in kb[0].data])
for k in list(kb)[1:]:original+=(np.array([v.co[:] for v in k.data])-np.array([v.co[:] for v in k.relative_key.data]))*k.value
h.shape_key_clear()
for v,p in zip(h.data.vertices,original):v.co=p
h.shape_key_add(name='R7_preserved_baseline')
def g(v,c,w,p=2):return math.exp(-abs((v-c)/w)**p)
def s(a,b,v):
 t=max(0.,min(1.,(v-a)/(b-a)));return t*t*(3-2*t)
stats=[]
def stage(name,fn):
 previous=h.data.shape_keys.key_blocks[-1];key=h.shape_key_add(name=name,from_mix=True);key.relative_key=previous
 before=np.array([v.co[:] for v in key.data])
 for v,p in zip(key.data,before):v.co=p+np.array(fn(*p))
 key.value=1;after=np.array([v.co[:] for v in key.data]);delta=np.linalg.norm(after-before,axis=1)
 stats.append({'name':name,'max_displacement':float(delta.max()),'moved_vertices':int(sum(delta>.01))})
def nose(x,y,z):
 # Narrow the dorsum and tip shoulders more than the alar base.
 front=1-s(-2,13,y);a=abs(x)
 bridge=g(x,0,14,4)*g(z,-23,15,4)*front
 tip=g(x,0,14,4)*g(z,-34,7,4)*front
 alar=g(a,15,5)*g(z,-39,6)*front
 return -x*1.55*(.105*bridge+.030*tip+.020*alar),0,0
def orbit(x,y,z):
 # Shape the upper fold and supported roof; do not deepen the globes again.
 a=abs(x);front=1-s(9,28,y)
 fold=g(a,31,11,4)*g(z,8.8,2.4)*front
 roof=g(a,31,16,4)*g(z,15.0,5.4)*front
 lateral=g(a,42,7)*g(z,5.5,5)*front
 return 0,.65*fold-.50*roof,-.12*lateral
def jaw(x,y,z):
 a=abs(x);sgn=1 if x>=0 else -1
 corner=g(a,52,13,4)*g(y,40,23,4)*g(z,-81,16,4)
 side=g(a,50,13,4)*g(y,20,30,4)*g(z,-74,17,4)
 underside=g(a,36,13,4)*g(y,12,27,4)*g(z,-96,11,4)
 # Blend separately toward lateral and submandibular planes instead of
 # scaling the whole jaw. Their intersection supplies the local turn.
 side_delta=max(-2.2,min(1.4,.264*y+.266*z+62.4-a))*.60*side
 underside_delta=max(-1.5,min(1.5,.30*y-100-z))*.45*underside
 return sgn*(side_delta-.30*corner),.55*corner,underside_delta
stage('R8_01_nasal_dorsum_and_tip_width',nose)
stage('R8_02_upper_lid_fold_and_orbital_roof',orbit)
stage('R8_03_mandibular_angle_and_body',jaw)
current=np.array([v.co[:] for v in h.data.shape_keys.key_blocks[-1].data])
tris=[];edges=set()
for p in h.data.polygons:
 ids=list(p.vertices)
 for a,b in zip(ids,ids[1:]+ids[:1]):edges.add(tuple(sorted((a,b))))
 for j in range(1,len(ids)-1):tris.append([ids[0],ids[j],ids[j+1]])
tri=np.array(tris);edge=np.array(sorted(edges))
def normal(v):return np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])
n0,n1=normal(original),normal(current);valid=(np.linalg.norm(n0,axis=1)>1e-5)&(np.linalg.norm(n1,axis=1)>1e-5)
reversed_count=int(sum(np.sum(n0[valid]*n1[valid],axis=1)<0))
e0=np.linalg.norm(original[edge[:,0]]-original[edge[:,1]],axis=1);e1=np.linalg.norm(current[edge[:,0]]-current[edge[:,1]],axis=1);rat=e1[e0>1e-5]/e0[e0>1e-5]
report={'version':'R8','status':'working candidate; author approval pending','finite':bool(np.isfinite(current).all()),'normal_rotations_over_90deg':reversed_count,'edge_scale_range':[float(rat.min()),float(rat.max())],'stages':stats,'limits':['Geometry validation is not identity validation.','Nasal narrowing is localized; tip projection and alar base mostly preserved.','Photographic skin shading and inherited hair remain approximations.']}
(R/'core-r8-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if not report['finite'] or reversed_count:raise RuntimeError('Inspect local geometry before rendering')
sc=bpy.context.scene;sc.cycles.samples=20;sc.camera=bpy.data.objects['Core_T22_pose'];skin=h.data.materials[0];neutral=bpy.data.materials['Neutral_anatomy'];skin.use_fake_user=True
sc['status']='R8: nasal dorsum/tip width, upper orbital relief, mandibular angle/body. Identity not established.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R8.blend'))
for camera,tag,mat in [('Core_T22_pose','front-neutral',neutral),('Core_T22_pose','front',skin),('View_threequarter','neutral',neutral),('View_threequarter','threequarter',skin),('View_near-profile','near-profile',skin)]:
 sc.camera=bpy.data.objects[camera];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/core-r8-{tag}.png');bpy.ops.render.render(write_still=True)
print('R8_DONE',json.dumps(report),flush=True)
