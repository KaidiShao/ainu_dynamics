import bpy,pathlib,json,math,random
import numpy as np
from mathutils import Vector,Matrix
R=pathlib.Path(__file__).resolve().parents[1];P=R.parent/'48_Blender头模精修_2026-10-13'
d=json.loads((R/'core-fit-r2.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(P/'carrillo-refined-v9.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head']
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
# Retain only the surrounding skull, scalp and neck from the previous scene.
# The central face is reconstructed from the original anatomical base.
old=np.array([v.co[:] for v in h.data.vertices])
if h.data.shape_keys:
 kb=h.data.shape_keys.key_blocks
 old=np.array([v.co[:] for v in kb[0].data])
 for key in list(kb)[1:]:
  old+=(np.array([v.co[:] for v in key.data])-np.array([v.co[:] for v in key.relative_key.data]))*key.value
h.shape_key_clear()
fresh=np.array(d['vertices']);weights=[]
for i,(v,co) in enumerate(zip(h.data.vertices,fresh)):
 x,y,z=co
 w=smooth(-125,-103,z)*(1-smooth(29,55,z))*(1-smooth(23,70,y))*(1-smooth(53,74,abs(x)))
 weights.append(w);v.co=old[i]*(1-w)+co*w
for mod in list(h.modifiers):
 if mod.type!='SUBSURF':h.modifiers.remove(mod)
h.data.update()
h['reconstruction']='R2 fresh central face from anatomical base. V9 only supplies peripheral transition, scalp, hair and neck.'
# Preserve old skin UV at the scalp/neck transition, use freshly fitted UV inside face.
existing=h.data.uv_layers.get('F03_reference_projection')
old_uv=[u.uv.copy() for u in existing.data]
for name,key in [('F03_reference_projection','F03'),('T22_core_reference','T22')]:
 layer=h.data.uv_layers.get(name) or h.data.uv_layers.new(name=name)
 for li,loop in enumerate(h.data.loops):
  ix=loop.vertex_index;uv=Vector(d['uv'][key][ix])
  if key=='F03':uv=old_uv[li].lerp(uv,weights[ix])
  layer.data[li].uv=uv
skin=h.data.materials[0].copy();skin.name='Core_R2_soft_reference_skin'
bs=skin.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.62;bs.inputs['Subsurface Weight'].default_value=.055
h.data.materials[0]=skin;skin.use_fake_user=True
# A separately named projection diagnostic; never treat its photograph shading as geometry.
proj=bpy.data.materials.new('T22_projection_DIAGNOSTIC_baked_light');proj.use_nodes=True;nt=proj.node_tree;nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');em.inputs['Strength'].default_value=.75
tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(d['references']['T22'],check_existing=True);tex.extension='EXTEND'
uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='T22_core_reference';nt.links.new(uv.outputs[0],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs[0]);proj.use_fake_user=True
# Build each eyeball and iris in the same coordinate system as the new lids.
for o in list(bpy.data.objects):
 if o.name.startswith(('Eyeball_','Iris_')):bpy.data.objects.remove(o,do_unlink=True)
sclera=bpy.data.materials.get('Sclera_warm_offwhite').copy();sclera.name='Core_R2_sclera'
bs=sclera.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.30,.285,.26,1);bs.inputs['Roughness'].default_value=.32;bs.inputs['Coat Weight'].default_value=.12
irisMat=bpy.data.materials.get('Iris_low_saturation_gray_blue').copy();irisMat.name='Core_R2_gray_blue_iris'
bs=irisMat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.4;bs.inputs['Coat Weight'].default_value=.2
rmat=np.array(d['camera_T22']['rotation']);M=np.column_stack((rmat[:,0],-rmat[:,2],rmat[:,1]))
right,up,forward=[Vector(v) for v in M]
rng=random.Random(9042);radius=d['eye_radius']
for idx,co in enumerate(d['eyes']):
 suffix='L' if idx==0 else 'R';center=Vector(co)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=96,ring_count=64,radius=radius,location=center)
 eye=bpy.context.object;eye.name='Eyeball_'+suffix;eye.data.materials.append(sclera)
 for p in eye.data.polygons:p.use_smooth=True
 vs=[];fs=[];colors=[];nr=36;na=128;fibres=[rng.uniform(.72,1.27) for i in range(na)]
 for j in range(nr+1):
  r=6.0*j/nr
  for k in range(na):
   a=k*math.tau/na
   vs.append(tuple(center+right*r*math.cos(a)+up*r*math.sin(a)+forward*(math.sqrt(radius*radius-r*r)+.035)))
   if r<1.9:c=(.0015,.002,.0025)
   else:
    rim=max(0,min(1,(6-r)/.45));inner=max(0,min(1,(r-1.9)/.65))
    f=fibres[k]*(.86+.13*math.sin(r*7+k*.11))*(.34+.66*rim)*(.6+.4*inner)
    c=(.085*f,.115*f,.133*f)
   colors.append(c)
 for j in range(nr):
  for k in range(na):
   a=j*na+k;b=j*na+(k+1)%na;fs.append((a,b,b+na,a+na))
 mesh=bpy.data.meshes.new('Core_iris_surface');mesh.from_pydata(vs,[],fs);mesh.update()
 o=bpy.data.objects.new('Iris_'+suffix,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(irisMat)
 col=mesh.color_attributes.new(name='Iris_fibres',type='FLOAT_COLOR',domain='POINT')
 for i,c in enumerate(colors):col.data[i].color=(*c,1)
 for p in mesh.polygons:p.use_smooth=True
# Camera that uses the T22 fitted pose, not a guessed symmetric front camera.
sc=bpy.context.scene
cam=bpy.data.objects['View_front'].copy();cam.data=cam.data.copy();cam.name='Core_T22_pose';bpy.context.collection.objects.link(cam)
center=Vector((0,25,-2));cam.location=center+forward*700;cam.rotation_euler=Matrix(M.tolist()).transposed().to_euler();cam.data.ortho_scale=305
sc.cycles.samples=20;sc.cycles.use_denoising=True;sc.render.resolution_x=760;sc.render.resolution_y=950
neutral=bpy.data.materials['Neutral_anatomy']
for camera_name,tag,material in [
 ('Core_T22_pose','front',skin),
 ('View_threequarter','threequarter',skin),
 ('View_threequarter','neutral',neutral),
 ('View_near-profile','near-profile',skin)
]:
 sc.camera=bpy.data.objects[camera_name];h.data.materials[0]=material
 sc.render.filepath=str(R/f'renders/core-r2-{tag}.png');bpy.ops.render.render(write_still=True)
h.data.materials[0]=skin;sc.camera=cam
sc['status']='Core reconstruction R2. Independent working candidate, not author-approved.'
sc['source']='Original anatomical base for core; shared anatomical constraints; T22 pose. F03 skin projection contains photographed lighting.'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R2.blend'))
delta=np.array([v.co[:] for v in h.data.vertices])-old
summary={'status':'rendered candidate, pending visual review','new_core_vertex_count':int(sum(w>.95 for w in weights)),
 'mean_core_displacement':float(np.linalg.norm(delta,axis=1)[np.array(weights)>.95].mean()),'max_displacement':float(np.linalg.norm(delta,axis=1).max()),
 'eyes':d['eyes'],'eye_radius':radius,'geometry_finite':bool(np.isfinite(delta).all()),
 'preserved':'Peripheral skull/scalp/hair/neck only. Rebuilt central geometry, eyelid-eye relationship and camera pose.',
 'projection_warning':'projection-diagnostic has baked T22 shading; not proof of geometric likeness'}
(R/'core-r2-manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print('CORE_R2_DONE',json.dumps(summary),flush=True)

