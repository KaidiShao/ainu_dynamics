import bpy,pathlib,json,math,random,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11H.blend'),load_ui=False)
D=json.loads((R/'face-r11h.json').read_text());M=np.array(D['M']);fw=Vector(M[2]);up=Vector(M[1]);right=Vector(M[0]);V=np.array(D['vertices']);Q=V@M[:2].T;h=bpy.data.objects['Carrillo_Head']
def mat(name,c,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=rough;return m
lashmat=mat('R11I_dark_lash',(.006,.0028,.0014),.65);tearmat=mat('R11I_subtle_lid_margin',(.18,.063,.044),.38)
def cu(name,bevel,m):
 cv=bpy.data.curves.new(name,'CURVE');cv.dimensions='3D';cv.bevel_depth=bevel;cv.bevel_resolution=2;ob=bpy.data.objects.new(name,cv);bpy.context.collection.objects.link(ob);cv.materials.append(m);return cv
lashes=cu('R11_upper_lash_fibres',.045,lashmat);upperline=cu('R11_upper_lid_margin',.07,lashmat);lowerline=cu('R11_lower_wet_margin',.055,tearmat)
deps=bpy.context.evaluated_depsgraph_get();ev=h.evaluated_get(deps);me=ev.to_mesh();bvh=BVHTree.FromPolygons([v.co for v in me.vertices],[list(f.vertices) for f in me.polygons]);rng=random.Random(10213)
def strand(curve,pts,radii=None):
 sp=curve.splines.new('POLY');sp.points.add(len(pts)-1)
 for i,(p,pt) in enumerate(zip(pts,sp.points)):pt.co=(*p,1);pt.radius=radii[i] if radii else 1
for patch,c in zip(D['patches'],D['eyes']):
 center=np.array(c)@M[:2].T;ids=patch['rings'][0];pts=V[ids];q=Q[ids]
 for i in range(len(ids)):
  j=(i+1)%len(ids);upper=(q[i,1]+q[j,1])/2>center[1];curve=upperline if upper else lowerline
  p0=Vector(pts[i]);p1=Vector(pts[j]);strand(curve,[p0+fw*.10,p1+fw*.10])
  if not upper:continue
  for t in [.2,.5,.8]:
   p=p0.lerp(p1,t);pos,n,ix,dist=bvh.ray_cast(p+fw*3,-fw,8)
   if pos and dist<4:p=pos+n*.1
   length=rng.uniform(.55,1.15);dr=fw*.45+up*.35+right*(patch['side']*.18)
   strand(lashes,[p,p+dr*length*.5,p+dr*length+up*.17],[1,.65,.05])
ev.to_mesh_clear()
# Broad, natural brow mass. Density comes from individual surface anchored fibres.
brow=bpy.data.objects['R10_brows'];brow.data.bevel_depth=.067
original=list(brow.data.splines)
for sp in original[::2]:
 pts=[Vector(p.co[:3]) for p in sp.points];offset=up*rng.uniform(-.45,.45)+right*rng.uniform(-.25,.25)
 strand(brow.data,[p+offset for p in pts],[p.radius*.85 for p in sp.points])
# Native physical hair shader with restrained visible fibre highlights.
hair=bpy.data.objects['Carrillo_wavy_groom'].data.materials[0];nt=hair.node_tree
for n in nt.nodes:
 if n.type=='BSDF_HAIR_PRINCIPLED':n.inputs['Melanin'].default_value=.84;n.inputs['Roughness'].default_value=.40
 if n.type=='MIX_SHADER':n.inputs[0].default_value=.28
sc=bpy.context.scene;sc.render.threads_mode='FIXED';sc.render.threads=6;sc.cycles.samples=24
skin=h.data.materials[0];neutral=bpy.data.materials['R10E_neutral_anatomy'];sc['status']='R11I internal likeness review, real orbital/oral topology rebuilt and fairing checked.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11I.blend'))
for cname,tag,material in [('Core_T22_pose','front',skin),('Core_T22_pose','front-neutral',neutral),('Core_P14_pose','side',skin),('Core_P14_pose','side-neutral',neutral),('View_threequarter','threequarter',skin)]:
 h.data.materials[0]=material;sc.camera=bpy.data.objects[cname];sc.render.filepath=str(R/f'renders/r11i-{tag}.png');bpy.ops.render.render(write_still=True)
# Matched dramatic light is checked only after the neutral and soft-light views.
h.data.materials[0]=skin;key=bpy.data.objects['Key'];key.location=(320,-140,160);key.rotation_euler=(Vector((0,0,-20))-key.location).to_track_quat('-Z','Y').to_euler();key.data.energy=1300000;key.data.size=85;bpy.data.objects['Fill'].data.energy=45000
sc.camera=bpy.data.objects['Core_T22_pose'];sc.render.filepath=str(R/'renders/r11i-dramatic.png');bpy.ops.render.render(write_still=True)
print('R11I_DONE',flush=True)
