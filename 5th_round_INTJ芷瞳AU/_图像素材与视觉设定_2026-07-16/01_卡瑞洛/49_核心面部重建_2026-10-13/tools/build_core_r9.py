import bpy,pathlib,json,math,numpy as np
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R8.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];kb=h.data.shape_keys.key_blocks
original=np.array([v.co[:] for v in kb[0].data])
for k in list(kb)[1:]:original+=(np.array([v.co[:] for v in k.data])-np.array([v.co[:] for v in k.relative_key.data]))*k.value
h.shape_key_clear()
for v,p in zip(h.data.vertices,original):v.co=p
h.shape_key_add(name='R8_preserved_baseline')
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
def bridge(x,y,z):
 front=1-s(-8,10,y)
 # Raise projection of the root and bony/cartilaginous dorsum. The smooth
 # transverse falloff makes a raised central ridge with sloping sidewalls.
 root=3.2*g(z,0,10)*g(x,0,7.8)
 dorsum=3.5*g(z,-12,15)*g(x,0,8.0)
 dy=-(root+dorsum)*front
 dx=-x*.045*g(x,0,13,4)*g(z,-5,18,4)*front
 return dx,dy,0
def alae(x,y,z):
 a=abs(x);front=1-s(-3,8,y)
 zone=g(z,-36,9,4)*g(a,0,24,6)*front
 lateral=s(5,12,a)
 # Move the ala and attached nostril rim together. Keep the tip core and
 # columella outside the strongest narrowing, rather than pinching them.
 dx=-x*.14*lateral*zone
 dy=.70*s(8,14,a)*zone
 return dx,dy,0
stage('R9_01_high_root_and_dorsal_projection',bridge)
stage('R9_02_narrow_alar_form_and_attached_rim',alae)
current=np.array([v.co[:] for v in h.data.shape_keys.key_blocks[-1].data])
tri=[];edges=set()
for p in h.data.polygons:
 ids=list(p.vertices)
 for a,b in zip(ids,ids[1:]+ids[:1]):edges.add(tuple(sorted((a,b))))
 for j in range(1,len(ids)-1):tri.append([ids[0],ids[j],ids[j+1]])
tri=np.array(tri);edge=np.array(sorted(edges))
def normals(v):return np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])
n0,n1=normals(original),normals(current);valid=(np.linalg.norm(n0,axis=1)>1e-5)&(np.linalg.norm(n1,axis=1)>1e-5)
reversed_count=int(sum(np.sum(n0[valid]*n1[valid],axis=1)<0))
e0=np.linalg.norm(original[edge[:,0]]-original[edge[:,1]],axis=1);e1=np.linalg.norm(current[edge[:,0]]-current[edge[:,1]],axis=1);rat=e1[e0>1e-5]/e0[e0>1e-5]
ids=[3119,3118,3117,3166,3116,3115,3114,3113,3112,3111,1873,1872,2005,2259]
report={'version':'R9','status':'Nasal-form revision; not author-approved','author_correction':'T22 has a higher nasal bridge and narrower alae. R8 was a different nose type, not merely too broad at the tip.','finite':bool(np.isfinite(current).all()),'normal_rotations_over_90deg':reversed_count,'edge_scale_range':[float(rat.min()),float(rat.max())],'stages':stats,'diagnostic_vertices':[{'id':i,'R8':original[i].tolist(),'R9':current[i].tolist()} for i in ids],'limits':['A reference portrait does not supply measured depth. This is a reviewable shape hypothesis.','R8 nose was rejected by the author; earlier local-positive review did not establish correctness.','F03 photographic texture carries shading. Neutral and true-profile renders are supplied for geometry review.']}
(R/'core-r9-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
if not report['finite'] or reversed_count:raise RuntimeError('Inspect local geometry before rendering')
sc=bpy.context.scene;sc.cycles.samples=20;sc.camera=bpy.data.objects['Core_T22_pose'];skin=h.data.materials[0];neutral=bpy.data.materials['Neutral_anatomy'];skin.use_fake_user=True
sc['status']='R9: higher nasal bridge and narrower alae after explicit author correction. Not a validated likeness.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R9.blend'))
for camera,tag,mat in [('Core_T22_pose','front-neutral',neutral),('Core_T22_pose','front',skin),('View_threequarter','neutral',neutral),('View_threequarter','threequarter',skin),('View_near-profile','near-profile',skin)]:
 sc.camera=bpy.data.objects[camera];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/core-r9-{tag}.png');bpy.ops.render.render(write_still=True)
print('R9_DONE',json.dumps(report),flush=True)
