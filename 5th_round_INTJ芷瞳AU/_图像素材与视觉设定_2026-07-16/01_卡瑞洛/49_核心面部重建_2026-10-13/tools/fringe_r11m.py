import bpy,pathlib,json,numpy as np,math,random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11L.blend'),load_ui=False)
D=json.loads((R/'face-r11k.json').read_text());M=np.array(D['M']);fw=Vector(M[2]);up=Vector(M[1]);right=Vector(M[0]);h=bpy.data.objects['Carrillo_Head'];deps=bpy.context.evaluated_depsgraph_get();ev=h.evaluated_get(deps);me=ev.to_mesh();bvh=BVHTree.FromPolygons([v.co for v in me.vertices],[list(f.vertices) for f in me.polygons])
cu=bpy.data.curves.new('R11M_forehead_curl_clumps','CURVE');cu.dimensions='3D';cu.bevel_depth=.044;cu.bevel_resolution=1;ob=bpy.data.objects.new('R11M_forehead_curl_clumps',cu);bpy.context.collection.objects.link(ob);cu.materials.append(bpy.data.objects['Carrillo_wavy_groom'].data.materials[0]);rng=random.Random(101331)
for k in range(17):
 x0=-40+k*5.2;z0=rng.uniform(66,89);x1=x0+rng.uniform(-10,8);z1=(18 if k<8 else 29)+rng.uniform(0,13);phase=rng.uniform(-1,1);pts=[]
 for j in range(48):
  t=j/47;x=x0+(x1-x0)*t+(4+3*t)*math.sin(t*6.7+phase)*math.sin(math.pi*t);z=z0+(z1-z0)*t+3*math.sin(t*6.4)*math.sin(math.pi*t)
  pos,n,ix,dist=bvh.ray_cast(right*x+up*z+fw*200,-fw,450)
  if pos is None:pos=right*x+up*z+fw*25
  lift=1.1+10*math.sin(math.pi*t)**1.1;pts.append(pos+fw*lift)
 for child in range(44):
  dx=rng.gauss(0,.42);dz=rng.gauss(0,.35);dd=rng.gauss(0,.35);sp=cu.splines.new('POLY');sp.points.add(47)
  for j,p in enumerate(sp.points):
   t=j/47;position=pts[j]+right*(dx+.17*math.sin(t*15+child)*t)+up*dz+fw*dd;p.co=(*position,1);p.radius=(.72+rng.random()*.32)*(1-.995*t**2.2)
ev.to_mesh_clear();sc=bpy.context.scene;sc.render.threads_mode='FIXED';sc.render.threads=6;sc.cycles.samples=24;skin=h.data.materials[0];neutral=bpy.data.materials['R10E_neutral_anatomy'];bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11M.blend'))
for name,tag,mat in [('Core_T22_pose','front',skin),('Core_T22_pose','front-neutral',neutral),('Core_P14_pose','side',skin),('Core_P14_pose','side-neutral',neutral),('View_threequarter','threequarter',skin)]:
 sc.camera=bpy.data.objects[name];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/r11m-{tag}.png');bpy.ops.render.render(write_still=True)
print('R11M_DONE',flush=True)
