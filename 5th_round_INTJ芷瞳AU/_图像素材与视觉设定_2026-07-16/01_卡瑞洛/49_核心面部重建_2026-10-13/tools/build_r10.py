import bpy,pathlib,json,math,random,numpy as np,sys
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from groom_r10 import groom
from eyes_r10 import rebuild_eyes
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [];tag=args[0] if args else 'r10a'
d=json.loads((R/'structure-r10.json').read_text());M=np.array(d['M']);cam=d['camera'];fwd=M[2]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R9.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];old=np.array(d['baseline']);V=np.array(d['vertices']);h.shape_key_clear()
for v,p in zip(h.data.vertices,old):v.co=p
h.shape_key_add(name='R9_preserved_baseline');k=h.shape_key_add(name='R10_reference_outline_and_anatomical_lid_rows')
for v,p in zip(k.data,V):v.co=p
k.value=1
def g(v,c,w,p=2):return math.exp(-abs((v-c)/w)**p)
def sm(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def sculpt(x,y,z):
 a=abs(x);sg=1 if x>=0 else -1;front=1-sm(14,58,y);dx=dy=dz=0
 # Continuous zygomatic support, submalar transition, and mandibular plane.
 cheek=g(a,49,13,4)*g(z,-30,14)*g(y,5,25)
 dy-=.65*cheek
 sub=g(a,42,13,4)*g(z,-53,17)*g(y,6,24)
 dy+=.55*sub
 corner=g(a,52,11)*g(y,29,20)*g(z,-83,14)
 dx+=sg*.75*corner;dy+=1.2*corner;dz-=.8*corner
 chin=g(x,0,27,4)*g(z,-101,14)*g(y,-20,23)
 dx-=x*.026*chin;dy+=.75*chin;dz-=.35*chin
 # Align the lip volumes, cupid peaks and labiomental transition.
 upper=g(a,5.7,4.8)*g(z,-55.5,5)*front
 dz+=.20*upper;dy-=.25*upper
 lower=g(x,0,20,4)*g(z,-71.5,5)*front
 dy+=.45*lower
 groove=g(x,0,21,4)*g(z,-80,7)*front
 dy-=.65*groove
 corners=g(a,22,6)*g(z,-66,7)*front
 dy-=.35*corners
 # Narrow the dome/shoulders, maintain the alar opening and tip direction.
 dome=g(x,0,12,4)*g(z,-33,8)*front
 dx-=x*.07*dome;dz-=.9*dome
 sidewall=g(a,10,5)*g(z,-21,11)*front
 dy+=.35*sidewall
 crease=g(a,16,3.8)*g(z,-36,5)*front
 dy+=.35*crease
 return dx,dy,dz
prev=k;k=h.shape_key_add(name='R10_zygomatic_mandible_lips_nasal_planes',from_mix=True);k.relative_key=prev
for v,p in zip(k.data,V):v.co=p+np.array(sculpt(*p))
k.value=1;new=np.array([v.co[:] for v in k.data]);h.data.update()
# Rebuild both globes and irises as one coherent system. No emissive colour.
for ob in list(bpy.data.objects):
 if ob.name.startswith(('Eyeball_','Iris_')):bpy.data.objects.remove(ob,do_unlink=True)
def mat(name,color,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;return m
sclera=mat('R10_sclera',(.20,.181,.16),.26);sclera.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.3
iris=mat('R10_gray_blue_iris',(.035,.05,.065),.21);nt=iris.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Specular IOR Level'].default_value=.3;bs.inputs['Coat Weight'].default_value=.20;bs.inputs['Coat Roughness'].default_value=.07
vc=nt.nodes.new('ShaderNodeVertexColor');vc.layer_name='Iris_fibres';nt.links.new(vc.outputs['Color'],bs.inputs['Base Color'])
rng=random.Random(443);right=Vector(M[0]);up=Vector(M[1]);forward=Vector(M[2])
for suffix,cc in zip(['L','R'],d['eyes']):
 c=Vector(cc);radius=11.7
 bpy.ops.mesh.primitive_uv_sphere_add(segments=96,ring_count=64,radius=radius,location=c)
 o=bpy.context.object;o.name='Eyeball_'+suffix;o.data.materials.append(sclera)
 for f in o.data.polygons:f.use_smooth=True
 vs=[];fs=[];colors=[];nr=42;na=128;fib=[rng.uniform(.8,1.2) for i in range(na)]
 for j in range(nr+1):
  r=6*j/nr
  for aidx in range(na):
   a=aidx*math.tau/na;vs.append(tuple(c+right*r*math.cos(a)+up*r*math.sin(a)+forward*(math.sqrt(radius*radius-r*r)+.055)))
   if r<2.55:col=(.001,.0013,.0015)
   else:
    edge=sm(0,.65,6-r);inner=sm(2.55,3.05,r);f=fib[aidx]*(.9+.1*math.sin(r*10+aidx*.3))*(.25+.75*edge)*(.52+.48*inner)
    col=(.040*f,.058*f,.073*f)
   colors.append((*col,1))
 for j in range(nr):
  for a in range(na):
   x=j*na+a;y=j*na+(a+1)%na;fs.append((x,y,y+na,x+na))
 me=bpy.data.meshes.new('R10_iris');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('Iris_'+suffix,me);bpy.context.collection.objects.link(o);me.materials.append(iris)
 ca=me.color_attributes.new(name='Iris_fibres',type='FLOAT_COLOR',domain='POINT')
 for i,col in enumerate(colors):ca.data[i].color=col
 for f in me.polygons:f.use_smooth=True
rebuild_eyes(d['eyes'],M)
# Attenuate baked photographic lighting without replacing geometry with T22.
skin=h.data.materials[0].copy();skin.name='R10_reduced_photo_skin';nt=skin.node_tree;bs=nt.nodes.get('Principled BSDF')
photo=next(n for n in nt.nodes if n.type=='TEX_IMAGE');blend=nt.nodes.new('ShaderNodeMixRGB');blend.blend_type='MIX';blend.inputs[0].default_value=.12;blend.inputs[2].default_value=(.28,.155,.10,1);nt.links.new(photo.outputs['Color'],blend.inputs[1])
for link in list(photo.outputs['Color'].links):
 if link.to_node!=blend:nt.links.new(blend.outputs[0],link.to_socket)
bs.inputs['Subsurface Weight'].default_value=.075;bs.inputs['Roughness'].default_value=.52;bs.inputs['Specular IOR Level'].default_value=.24
h.data.materials[0]=skin;skin.use_fake_user=True
lm=json.loads((R.parent/'47_三维头模结构试验_2026-10-12/landmarks.json').read_text())['T22']['landmarks']
groom(h,R,M,lm,cam)
sc=bpy.context.scene;sc.camera=bpy.data.objects['Core_T22_pose'];sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.render.resolution_x=760;sc.render.resolution_y=950
# Check finite values and relative local winding, including an explicit record.
tri=[]
for f in h.data.polygons:
 ids=list(f.vertices)
 for j in range(1,len(ids)-1):tri.append([ids[0],ids[j],ids[j+1]])
tri=np.array(tri)
def norms(v):return np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])
a=norms(old);weights=np.ones(len(new));proposal=new.copy();neighbors=[set() for _ in new]
for f in h.data.polygons:
 for i in f.vertices:neighbors[i].update(f.vertices)
for iteration in range(30):
 b=norms(new);valid=(np.linalg.norm(a,axis=1)>1e-5)&(np.linalg.norm(b,axis=1)>1e-5);bad=np.where((np.sum(a*b,axis=1)<0)&valid)[0]
 if not len(bad):break
 affected=set(tri[bad].ravel())
 for i in list(affected):affected.update(neighbors[i])
 for i in affected:weights[i]*=.78
 new=old+(proposal-old)*weights[:,None]
for v,p in zip(k.data,new):v.co=p
b=norms(new);valid=(np.linalg.norm(a,axis=1)>1e-5)&(np.linalg.norm(b,axis=1)>1e-5)
report={'version':tag,'finite':bool(np.isfinite(new).all()),'normal_rotations_over_90deg':int(sum(np.sum(a[valid]*b[valid],axis=1)<0)),'max_displacement':float(np.linalg.norm(new-old,axis=1).max()),'status':'Internal revision; requires visual audit before promotion.','eyes':d['eyes'],'scope':['Reference-plane proportions','Anatomical upper/lower lid rows and globe clearance','Cheek/jaw/chin continuity','Lip and nasal planes','Rebuilt eyes and groom','Reduced baked-photo influence']}
(R/f'{tag}-manifest.json').write_text(json.dumps(report,indent=2))
if not report['finite']:raise RuntimeError('Non-finite geometry')
sc['status']='Internal R10 all-face iteration; likeness not assumed.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/f'Carrillo_core_rebuild_{tag.upper()}.blend'))
neutral=bpy.data.materials['Neutral_anatomy']
for camera,name,matr in [('Core_T22_pose','front-soft',skin),('Core_T22_pose','front-neutral',neutral),('View_threequarter','neutral',neutral),('View_near-profile','profile',skin)]:
 sc.camera=bpy.data.objects[camera];h.data.materials[0]=matr;sc.render.filepath=str(R/f'renders/{tag}-{name}.png');bpy.ops.render.render(write_still=True)
key=bpy.data.objects['Key'];key.location=(300,-240,170);key.rotation_euler=(Vector((0,0,-20))-key.location).to_track_quat('-Z','Y').to_euler();key.data.energy=1600000;key.data.size=100
bpy.data.objects['Fill'].data.energy=105000;bpy.data.objects['Rim'].data.energy=240000
sc.camera=bpy.data.objects['Core_T22_pose'];h.data.materials[0]=skin;sc.render.filepath=str(R/f'renders/{tag}-front.png');bpy.ops.render.render(write_still=True)
print('INTERNAL_RENDER_DONE',json.dumps(report),flush=True)
