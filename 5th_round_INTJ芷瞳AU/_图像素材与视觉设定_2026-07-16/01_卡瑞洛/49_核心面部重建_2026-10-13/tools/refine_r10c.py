import bpy,pathlib,json,sys,numpy as np,math
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from eyes_r10 import rebuild_eyes
d=json.loads((R/'structure-r10.json').read_text());M=np.array(d['M']);fwd=M[2]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10B.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];kb=h.data.shape_keys.key_blocks;V=np.array([v.co[:] for v in kb[0].data])
for k in list(kb)[1:]:V+=(np.array([v.co[:] for v in k.data])-np.array([v.co[:] for v in k.relative_key.data]))*k.value
h.shape_key_clear()
for v,p in zip(h.data.vertices,V):v.co=p
h.shape_key_add(name='R10B_preserved')
W=V.copy();Q=V@M[:2].T;eyes=np.array(d['eyes']);eyeQ=eyes@M[:2].T
w=np.max([np.exp(-((Q[:,0]-q[0])/19)**4-((Q[:,1]-q[1])/12)**4) for q in eyeQ],axis=0)
rear=np.clip((70-V[:,1])/45,0,1);w*=rear
W-=fwd[None,:]*w[:,None]*2.7
eyes-=fwd[None,:]*2.7
# Recess the globe and its fitted lids together, retaining their frontal
# outline while reducing the protrusion visible from the side.
a=abs(V[:,0]);front=np.clip((45-V[:,1])/30,0,1)
sub=np.exp(-((a-40)/15)**4-((V[:,2]+51)/19)**4-((V[:,1]-2)/25)**2)
W[:,1]+=1.1*sub
chin=np.exp(-(V[:,0]/25)**4-((V[:,2]+102)/15)**2)*front
W[:,1]+=.55*chin;W[:,0]-=V[:,0]*.015*chin
# Smooth only the outer lip/crease relief, preserving the seam and outline.
adj=[set() for _ in V]
for f in h.data.polygons:
 for i in f.vertices:adj[i].update(f.vertices)
for it in range(3):
 out=W.copy()
 for i,p in enumerate(W):
  x,y,z=p
  if abs(x)>24 or y>-21:continue
  wt=math.exp(-(x/18)**4)*(.28*math.exp(-((z+58)/5)**4)+.36*math.exp(-((z+79)/5)**4))
  if wt>.01:out[i,1]+=np.clip(np.mean([W[j,1] for j in adj[i]])-y,-1.1,1.1)*wt
 W=out
key=h.shape_key_add(name='R10C_visible_orbit_depth_and_lip_relief')
for v,p in zip(key.data,W):v.co=p
key.value=1;h.data.update()
rebuild_eyes(eyes,M)
# Keep the cool gray-blue, lower the uniform blue brightness.
for name in ['Iris_L','Iris_R']:
 col=bpy.data.objects[name].data.color_attributes['Iris_fibres']
 for v in col.data:
  r,g,b,a=v.color
  if r>.005:v.color=(r*.65,g*.61,b*.58,a)
# Moderate dense-root reflections, retain individual fibre variation.
for name in ['R10_dark_brown_roots','R10_dark_brown_fibres']:
 bs=bpy.data.materials[name].node_tree.nodes.get('Principled BSDF')
 bs.inputs['Specular IOR Level'].default_value=0 if name.endswith('roots') else .08
# Preserve the original photographic hue but reduce the painted eyebrow
# contribution locally; 3D brow strands now carry the band and direction.
skin=h.data.materials[0];nt=skin.node_tree
attr=h.data.attributes.get('brow_photo_mix') or h.data.attributes.new(name='brow_photo_mix',type='FLOAT',domain='POINT')
for i,p in enumerate(W):
 x,y,z=p
 strength=.45*math.exp(-((abs(x)-32)/25)**6-((z-18)/7)**4)*max(0,min(1,(8-y)/15))
 attr.data[i].value=strength
photo=next(n for n in nt.nodes if n.type=='TEX_IMAGE')
fac=nt.nodes.new('ShaderNodeAttribute');fac.attribute_name='brow_photo_mix'
mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[2].default_value=(.23,.125,.079,1);nt.links.new(fac.outputs['Fac'],mix.inputs[0]);nt.links.new(photo.outputs['Color'],mix.inputs[1])
for link in list(photo.outputs['Color'].links):
 if link.to_node!=mix:nt.links.new(mix.outputs[0],link.to_socket)
# Slightly longer, thicker brow fibres read as brows rather than isolated dots.
bo=bpy.data.objects.get('R10_brows')
if bo:
 bo.data.bevel_depth=.052
 for sp in bo.data.splines:
  root=Vector(sp.points[0].co[:3])
  for j,pt in enumerate(sp.points):
   p=Vector(pt.co[:3]);p=root+(p-root)*1.7;pt.co=(*p,1)
# Explicit geometry audit and local rollback of any newly inverted triangles.
tri=[]
for f in h.data.polygons:
 ids=list(f.vertices)
 for j in range(1,len(ids)-1):tri.append([ids[0],ids[j],ids[j+1]])
tri=np.array(tri)
def normals(v):return np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])
n0=normals(V);proposal=W.copy();weights=np.ones(len(V))
for it in range(30):
 n1=normals(W);valid=(np.linalg.norm(n0,axis=1)>1e-5)&(np.linalg.norm(n1,axis=1)>1e-5);bad=np.where((np.sum(n0*n1,axis=1)<0)&valid)[0]
 if not len(bad):break
 ids=set(tri[bad].ravel())
 for i in list(ids):ids.update(adj[i])
 for i in ids:weights[i]*=.78
 W=V+(proposal-V)*weights[:,None]
for v,p in zip(key.data,W):v.co=p
report={'version':'R10C','finite':bool(np.isfinite(W).all()),'normal_rotations_over_90deg':int(len(bad)),'eye_recession':2.7,'max_displacement':float(np.linalg.norm(W-V,axis=1).max()),'status':'Internal visual review required','eyes':eyes.tolist()}
(R/'r10c-manifest.json').write_text(json.dumps(report,indent=2))
sc=bpy.context.scene;sc.cycles.samples=20;sc.camera=bpy.data.objects['Core_T22_pose'];h.data.materials[0]=skin
# Add the auxiliary reference pose so it remains inspectable in the native file.
c=json.loads((R.parent/'47_三维头模结构试验_2026-10-12/head-fit.json').read_text())['metrics']['P14'];r=np.array(c['rotation']);pm=np.column_stack((r[:,0],-r[:,2],r[:,1]))
cam=sc.camera.copy();cam.data=cam.data.copy();cam.name='Core_P14_pose';bpy.context.collection.objects.link(cam);center=Vector((0,25,-2));cam.location=center+Vector(pm[2])*700;cam.rotation_euler=Matrix(pm.tolist()).transposed().to_euler()
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10C.blend'))
neutral=bpy.data.materials['Neutral_anatomy']
for camera,tag,mat in [('Core_T22_pose','front-soft',skin),('Core_T22_pose','front-neutral',neutral),('Core_P14_pose','p14-neutral',neutral),('Core_P14_pose','p14',skin)]:
 sc.camera=bpy.data.objects[camera];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/r10c-{tag}.png');bpy.ops.render.render(write_still=True)
keylight=bpy.data.objects['Key'];keylight.location=(320,-140,160);keylight.rotation_euler=(Vector((0,0,-20))-keylight.location).to_track_quat('-Z','Y').to_euler();keylight.data.energy=1300000;keylight.data.size=85
bpy.data.objects['Fill'].data.energy=45000;bpy.data.objects['Rim'].data.energy=240000
sc.camera=bpy.data.objects['Core_T22_pose'];h.data.materials[0]=skin;sc.render.filepath=str(R/'renders/r10c-front.png');bpy.ops.render.render(write_still=True)
print('R10C_DONE',json.dumps(report),flush=True)
