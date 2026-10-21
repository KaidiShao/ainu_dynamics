import bpy,pathlib,json,math,numpy as np
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R6.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];kb=h.data.shape_keys.key_blocks;original=np.array([v.co[:] for v in kb[0].data])
for k in list(kb)[1:]:original+=(np.array([v.co[:] for v in k.data])-np.array([v.co[:] for v in k.relative_key.data]))*k.value
h.shape_key_clear()
for v,p in zip(h.data.vertices,original):v.co=p
h.shape_key_add(name='R6_preserved_baseline')
fit=json.loads((R/'lids-fit-r7.json').read_text());k=h.shape_key_add(name='R7_01_orbit_and_lower_lid_wrap');eyeV=np.array(fit['vertices'])
for v,p in zip(k.data,eyeV):v.co=p
k.value=1
for name in ['Eyeball_L','Eyeball_R','Iris_L','Iris_R']:bpy.data.objects[name].location+=Vector(fit['eye_translation'])
def g(v,c,w,p=2):return math.exp(-abs((v-c)/w)**p)
def stage(name,fn):
 prev=h.data.shape_keys.key_blocks[-1];key=h.shape_key_add(name=name,from_mix=True);key.relative_key=prev
 for v in key.data:
  x,y,z=v.co;v.co+=Vector(fn(x,y,z))
 key.value=1
def jaw(x,y,z):
 a=abs(x);sgn=1 if x>=0 else -1
 corner=g(a,52,12,4)*g(y,38,24,4)*g(z,-81,15,4)
 side=g(a,51,13,4)*g(y,20,26,4)*g(z,-61,18,4)
 return -sgn*(.85*corner+.65*side),3.2*corner,-1.30*corner
def chin(x,y,z):
 a=abs(x);sgn=1 if x>=0 else -1
 lateral=g(a,23,11)*g(z,-97,12,4)*g(y,-10,23,4)
 under=g(x,0,31,4)*g(z,-105,9)*g(y,5,20,4)
 transition=g(x,0,20,4)*g(z,-85,7)*g(y,-15,20,4)
 return -sgn*.9*lateral,1.05*lateral+.7*under-.45*transition,0
stage('R7_02_posterior_jaw_turn',jaw);stage('R7_03_chin_side_and_undersurface',chin)
current=np.array([v.co[:] for v in h.data.shape_keys.key_blocks[-1].data])
tris=[];edges=set()
for p in h.data.polygons:
 ids=list(p.vertices)
 for a,b in zip(ids,ids[1:]+ids[:1]):edges.add(tuple(sorted((a,b))))
 for j in range(1,len(ids)-1):tris.append([ids[0],ids[j],ids[j+1]])
tri=np.array(tris);edge=np.array(sorted(edges))
def normals(v):return np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])
n0,n1=normals(original),normals(current);l0=np.linalg.norm(n0,axis=1);l1=np.linalg.norm(n1,axis=1);valid=(l0>1e-5)&(l1>1e-5);cos=np.sum(n0[valid]*n1[valid],axis=1)/(l0[valid]*l1[valid]);reversed_ids=np.where(valid)[0][cos<0]
e0=np.linalg.norm(original[edge[:,0]]-original[edge[:,1]],axis=1);e1=np.linalg.norm(current[edge[:,0]]-current[edge[:,1]],axis=1);rat=e1[e0>1e-5]/e0[e0>1e-5]
report={'version':'R7','status':'candidate; pending visual and author review','finite':bool(np.isfinite(current).all()),'reversed_triangle_count':int(len(reversed_ids)),'reversed_triangles':tri[reversed_ids].tolist(),'edge_scale_range':[float(rat.min()),float(rat.max())],'max_displacement':float(np.linalg.norm(current-original,axis=1).max()),'eye_translation':fit['eye_translation'],'method':fit['method'],'changes':['Joint globe and lid repositioning','Individually constrained lower eyelid margin, roll, and transition','Posterior jaw turn repositioned without widening','Chin side and underside volume reduced locally'],'limits':['Landmark-compatible projection does not prove 3D likeness','Photo texture includes photographed lighting','Hair and appearance remain working approximations']}
forward=np.array(fit['eye_translation']);forward/=np.linalg.norm(forward)
eyeN=normals(eyeV);project0=n0@forward;project1=eyeN@forward;seen=abs(project0)>1e-5
report['eye_projected_winding_changes']=int(sum(project0[seen]*project1[seen]<0))
report['max_eye_projection_error']=float(np.max(np.linalg.norm((eyeV-original)-((eyeV-original)@forward)[:,None]*forward,axis=1)))
report['jaw_chin_orientation_reversals']=int(sum(np.sum(eyeN*n1,axis=1)<-1e-8))
report['orientation_note']='A changed normal direction can exceed 90 degrees when correcting a fold. Validate eye projected winding and jaw/chin orientation separately; visual inspection remains required.'
(R/'core-r7-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if not report['finite'] or report['eye_projected_winding_changes'] or report['jaw_chin_orientation_reversals']:raise RuntimeError('Local orientation check failed; inspect manifest')
sc=bpy.context.scene;sc.cycles.samples=20;sc.camera=bpy.data.objects['Core_T22_pose'];skin=h.data.materials[0];neutral=bpy.data.materials['Neutral_anatomy'];skin.use_fake_user=True
sc['status']='R7: orbit and lower-lid reconstruction, jaw and chin correction. Not author-approved.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R7.blend'))
for camera,tag,mat in [('Core_T22_pose','front-neutral',neutral),('View_threequarter','neutral',neutral),('Core_T22_pose','front',skin),('View_near-profile','near-profile',skin),('View_threequarter','threequarter',skin)]:
 sc.camera=bpy.data.objects[camera];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/core-r7-{tag}.png');bpy.ops.render.render(write_still=True)
print('R7_DONE',json.dumps(report),flush=True)
