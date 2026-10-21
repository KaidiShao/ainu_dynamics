import bpy,pathlib,json,sys,math
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10E.blend'),load_ui=False)
# Reuse the surface-anchored groom while changing its flow and fibre shader.
source=(R/'tools/groom_r10.py').read_text()
source=source.replace("range(1050)","range(1250)").replace("range(17)","range(24)")
source=source.replace("eth=th*.78-.22+rng.uniform(-.20,.20)","eth=th+.20*math.sin(th*3+ph*4)+rng.uniform(-.30,.30)")
source=source.replace("eph=min(ph+rng.uniform(.34,.72),limit(eth)+rng.uniform(.04,.26))","eph=min(ph+rng.uniform(.20,.55),limit(eth)+rng.uniform(.04,.19))")
source=source.replace("freq=.9+.15*math.sin(th*2)","freq=1.25+.25*math.sin(th*2)")
source=source.replace("lift=.7+(7+18*top)","lift=.7+(9+17*top)")
source=source.replace("wave=(2.2+5*top)","wave=(4+8*top)")
source=source.replace("range(85)","range(105)")
source=source.replace("eth=th-.22+rng.uniform(-.17,.17)","eth=th+.20*math.sin(th*4)+rng.uniform(-.28,.28)")
source=source.replace("eph=limit(eth)+rng.uniform(.18,.42)","eph=limit(eth)+rng.uniform(.12,.33)")
source=source.replace("tan*5*math.sin(t*math.tau+phase)","tan*9*math.sin(t*math.tau*1.35+phase)")
source=source.replace("curves('Carrillo_wavy_groom',.049)","curves('Carrillo_wavy_groom',.052)")
namespace={};exec(compile(source,'groom_r10f_inline','exec'),namespace)
d=json.loads((R/'structure-r10.json').read_text());lm=json.loads((R.parent/'47_三维头模结构试验_2026-10-12/landmarks.json').read_text())['T22']['landmarks']
h=bpy.data.objects['Carrillo_Head'];namespace['groom'](h,R,d['M'],lm,d['camera'])
hair=bpy.data.objects['Carrillo_wavy_groom'].data.materials[0];nt=hair.node_tree;out=nt.nodes.get('Material Output')
sh=nt.nodes.new('ShaderNodeBsdfHairPrincipled');sh.parametrization='MELANIN'
settings={'Melanin':.83,'Melanin Redness':.26,'Roughness':.34,'Radial Roughness':.40,'IOR':1.55,'Random Color':.08,'Random Roughness':.10}
for name,value in settings.items():
 if name in sh.inputs:sh.inputs[name].default_value=value
nt.links.new(sh.outputs[0],out.inputs['Surface'])
# Restore the fuller brow fibres after rebuilding the groom.
bo=bpy.data.objects['R10_brows'];bo.data.bevel_depth=.052
for sp in bo.data.splines:
 root=Vector(sp.points[0].co[:3])
 for p in sp.points:
  q=root+(Vector(p.co[:3])-root)*1.7;p.co=(*q,1)
sc=bpy.context.scene;sc.cycles.samples=32;sc.camera=bpy.data.objects['Core_T22_pose'];skin=h.data.materials[0]
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10F.blend'))
for cname,tag in [('Core_T22_pose','front-soft'),('Core_P14_pose','p14')]:
 sc.camera=bpy.data.objects[cname];sc.render.filepath=str(R/f'renders/r10f-{tag}.png');bpy.ops.render.render(write_still=True)
keylight=bpy.data.objects['Key'];keylight.location=(320,-140,160);keylight.rotation_euler=(Vector((0,0,-20))-keylight.location).to_track_quat('-Z','Y').to_euler();keylight.data.energy=1300000;keylight.data.size=85
bpy.data.objects['Fill'].data.energy=45000
sc.camera=bpy.data.objects['Core_T22_pose'];sc.render.filepath=str(R/'renders/r10f-front.png');bpy.ops.render.render(write_still=True)
print('R10F_DONE',flush=True)
