import bpy,pathlib,json,sys,numpy as np,math
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10C.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];dd=json.loads((R/'structure-r10d.json').read_text());V=np.array(dd['baseline']);W=np.array(dd['vertices'])
h.shape_key_clear()
for v,p in zip(h.data.vertices,V):v.co=p
h.shape_key_add(name='R10C_preserved');key=h.shape_key_add(name='R10D_visible_lids_lips_jaw')
tri=[];adj=[set() for _ in V]
for f in h.data.polygons:
 ids=list(f.vertices)
 for i in ids:adj[i].update(ids)
 for j in range(1,len(ids)-1):tri.append([ids[0],ids[j],ids[j+1]])
tri=np.array(tri)
def norms(v):return np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])
n0=norms(V);proposal=W.copy();weights=np.ones(len(V))
for it in range(30):
 n1=norms(W);valid=(np.linalg.norm(n0,axis=1)>1e-5)&(np.linalg.norm(n1,axis=1)>1e-5);bad=np.where((np.sum(n0*n1,axis=1)<0)&valid)[0]
 if not len(bad):break
 ids=set(tri[bad].ravel())
 for i in list(ids):ids.update(adj[i])
 for i in ids:weights[i]*=.78
 W=V+(proposal-V)*weights[:,None]
for v,p in zip(key.data,W):v.co=p
key.value=1;h.data.update()
skin=h.data.materials[0];nt=skin.node_tree;bs=nt.nodes.get('Principled BSDF')
# Thin fibres need a dark scalp underneath; this also prevents gray exposed
# scalp between crown clumps in neutral geometry renders.
attr=h.data.attributes.get('scalp_cover') or h.data.attributes.new(name='scalp_cover',type='FLOAT',domain='POINT')
for i,(x,y,z) in enumerate(W):
 v=Vector((x,y-85,z-22));ph=math.acos(max(-1,min(1,v.z/max(1e-5,v.length))));th=math.atan2(v.x,-v.y)
 lim=1.12+1*((1-math.cos(th))*.5)**.72+.025*math.sin(th*7)
 attr.data[i].value=max(0,min(1,(lim-.08-ph)/.15))
fac=nt.nodes.new('ShaderNodeAttribute');fac.attribute_name='scalp_cover'
mix=nt.nodes.new('ShaderNodeMixRGB');mix.inputs[2].default_value=(.0035,.0018,.001,1)
nt.links.new(fac.outputs['Fac'],mix.inputs[0])
nt.links.new(bs.inputs['Base Color'].links[0].from_socket,mix.inputs[1]);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
# Copy the same anatomical-only diagnostic material with the scalp mask.
neutral=bpy.data.materials['Neutral_anatomy'].copy();neutral.name='R10D_neutral_anatomy'
nn=neutral.node_tree;nbs=nn.nodes.get('Principled BSDF');na=nn.nodes.new('ShaderNodeAttribute');na.attribute_name='scalp_cover';nm=nn.nodes.new('ShaderNodeMixRGB');nm.inputs[1].default_value=nbs.inputs['Base Color'].default_value;nm.inputs[2].default_value=(.0035,.0018,.001,1);nn.links.new(na.outputs['Fac'],nm.inputs[0]);nn.links.new(nm.outputs[0],nbs.inputs['Base Color'])
# Denser coherent bundles, with less lift at the very top.
origin=Vector((0,85,22))
for name in ['Carrillo_wavy_groom','Long_loose_front_locks']:
 ob=bpy.data.objects[name];ob.data.bevel_depth*=1.18
 for sp in ob.data.splines:
  for j,pt in enumerate(sp.points):
   p=Vector(pt.co[:3]);v=p-origin;t=j/max(1,len(sp.points)-1)
   if p.z>67:p-=v.normalized()*min(3.4,(p.z-67)*.055)*math.sin(math.pi*t)
   pt.co=(*p,1)
# Small, diffuse corneal catchlights, no rectangular softbox dominating the iris.
for name in ['Cornea_L','Cornea_R']:
 b=bpy.data.objects[name].data.materials[0].node_tree.nodes.get('Principled BSDF')
 b.inputs['Roughness'].default_value=.07;b.inputs['Specular IOR Level'].default_value=.23
# Low-amplitude microrelief on actual skin surface.
tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=230;tex.inputs['Detail'].default_value=2;tex.inputs['Roughness'].default_value=.65
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.14;bump.inputs['Distance'].default_value=.085
nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
sc=bpy.context.scene;sc.cycles.samples=32;sc.camera=bpy.data.objects['Core_T22_pose']
keylight=bpy.data.objects['Key'];keylight.location=(260,-260,150);keylight.rotation_euler=(Vector((0,0,-20))-keylight.location).to_track_quat('-Z','Y').to_euler();keylight.data.energy=1350000;keylight.data.size=120
bpy.data.objects['Fill'].data.energy=160000;bpy.data.objects['Fill'].data.size=350
bpy.data.objects['Rim'].data.energy=110000
sc['status']='R10D self-reviewed iteration, not established likeness or author-approved model.'
report={'version':'R10D','finite':bool(np.isfinite(W).all()),'normal_rotations_over_90deg':len(bad),'max_displacement_from_R10C':float(np.linalg.norm(W-V,axis=1).max()),'scope':dd['notes'],'status':'Rendering for internal visual review'}
(R/'r10d-manifest.json').write_text(json.dumps(report,indent=2))
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10D.blend'))
for cname,tag,mat in [('Core_T22_pose','front-soft',skin),('Core_T22_pose','front-neutral',neutral),('Core_P14_pose','p14-neutral',neutral),('Core_P14_pose','p14',skin)]:
 sc.camera=bpy.data.objects[cname];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/r10d-{tag}.png');bpy.ops.render.render(write_still=True)
keylight.location=(320,-140,160);keylight.rotation_euler=(Vector((0,0,-20))-keylight.location).to_track_quat('-Z','Y').to_euler();keylight.data.energy=1300000;keylight.data.size=85
bpy.data.objects['Fill'].data.energy=45000
sc.camera=bpy.data.objects['Core_T22_pose'];h.data.materials[0]=skin;sc.render.filepath=str(R/'renders/r10d-front.png');bpy.ops.render.render(write_still=True)
print('R10D_DONE',json.dumps(report),flush=True)
