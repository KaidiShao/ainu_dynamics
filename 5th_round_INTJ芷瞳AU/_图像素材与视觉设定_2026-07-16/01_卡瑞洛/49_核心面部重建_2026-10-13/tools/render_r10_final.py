import bpy,pathlib,json,math
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10F.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];skin=h.data.materials[0];neutral=bpy.data.materials['R10E_neutral_anatomy']
hair=bpy.data.objects['Carrillo_wavy_groom'].data.materials[0];nt=hair.node_tree;output=nt.nodes.get('Material Output');p=nt.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.66;p.inputs['Specular IOR Level'].default_value=.08
hs=next(n for n in nt.nodes if n.type=='BSDF_HAIR_PRINCIPLED');hs.inputs['Melanin'].default_value=.94;hs.inputs['Roughness'].default_value=.52
mix=nt.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.15;nt.links.new(p.outputs[0],mix.inputs[1]);nt.links.new(hs.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],output.inputs['Surface'])
brow=bpy.data.materials.new('R10_final_brow');brow.use_nodes=True;b=brow.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.004,.0018,.0009,1);b.inputs['Roughness'].default_value=.82;b.inputs['Specular IOR Level'].default_value=.05
bpy.data.objects['R10_brows'].data.materials[0]=brow
sc=bpy.context.scene;sc.cycles.samples=40;sc.camera=bpy.data.objects['Core_T22_pose'];sc['status']='R10: six internal candidate revisions reviewed. Likeness remains an approximation; no author approval claimed.'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10.blend'))
for cname,tag,mat in [('Core_T22_pose','front-soft',skin),('Core_T22_pose','front-neutral',neutral),('Core_P14_pose','p14',skin),('Core_P14_pose','p14-neutral',neutral),('View_threequarter','threequarter',skin),('View_threequarter','neutral',neutral)]:
 sc.camera=bpy.data.objects[cname];h.data.materials[0]=mat;sc.render.filepath=str(R/f'renders/core-r10-{tag}.png');bpy.ops.render.render(write_still=True)
key=bpy.data.objects['Key'];key.location=(320,-140,160);key.rotation_euler=(Vector((0,0,-20))-key.location).to_track_quat('-Z','Y').to_euler();key.data.energy=1300000;key.data.size=85
bpy.data.objects['Fill'].data.energy=45000
sc.camera=bpy.data.objects['Core_T22_pose'];h.data.materials[0]=skin;sc.render.filepath=str(R/'renders/core-r10-front.png');bpy.ops.render.render(write_still=True)
print('R10_FINAL_RENDER_DONE',flush=True)
