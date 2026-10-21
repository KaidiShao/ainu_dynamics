import bpy,pathlib,numpy as np
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R12.blend'),load_ui=False);h=bpy.data.objects['Carrillo_Head'];D=np.load(R/'depth-r12/albedo-r12h.npz')
attr=h.data.color_attributes.new(name='T22_approx_albedo',type='FLOAT_COLOR',domain='POINT');colour=np.c_[D['colours'],np.ones(len(D['colours']))];attr.data.foreach_set('color',colour.ravel());weight=h.data.attributes.new(name='T22_albedo_weight',type='FLOAT',domain='POINT');weight.data.foreach_set('value',D['weight'])
mat=h.data.materials[0];nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');prior=bs.inputs['Base Color'].links[0].from_socket;col=nt.nodes.new('ShaderNodeVertexColor');col.layer_name='T22_approx_albedo';fac=nt.nodes.new('ShaderNodeAttribute');fac.attribute_name='T22_albedo_weight';mix=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(fac.outputs['Fac'],mix.inputs[0]);nt.links.new(prior,mix.inputs[1]);nt.links.new(col.outputs['Color'],mix.inputs[2]);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
sc=bpy.context.scene;sc.cycles.samples=24;sc.render.threads_mode='FIXED';sc.render.threads=6
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R12H.blend'))
for cname,tag in [('Core_T22_pose','front'),('View_threequarter','threequarter'),('Core_P14_pose','side')]:
 sc.camera=bpy.data.objects[cname];sc.render.filepath=str(R/f'renders/r12h-{tag}.png');bpy.ops.render.render(write_still=True)
print('R12H_DONE',flush=True)
