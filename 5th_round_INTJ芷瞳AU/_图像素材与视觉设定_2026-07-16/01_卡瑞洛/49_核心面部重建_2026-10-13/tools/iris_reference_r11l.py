import bpy,pathlib,numpy as np,json
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11K.blend'),load_ui=False)
D=json.loads((R/'face-r11k.json').read_text());M=np.array(D['M']);img=bpy.data.images.load(str(R.parent/'37_眼色局部统一_2026-10-11/MC_STATE_T22_T19正面_浅蓝灰虹膜校准_v22.png'),check_existing=True)
mat=bpy.data.materials.new('R11L_T22_iris_reference_detail');mat.use_nodes=True;nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.52;bs.inputs['Specular IOR Level'].default_value=.08
uvnode=nt.nodes.new('ShaderNodeUVMap');uvnode.uv_map='T22_iris_detail_only';tex=nt.nodes.new('ShaderNodeTexImage');tex.image=img;nt.links.new(uvnode.outputs[0],tex.inputs['Vector']);gamma=nt.nodes.new('ShaderNodeGamma');gamma.inputs['Gamma'].default_value=.88;nt.links.new(tex.outputs['Color'],gamma.inputs['Color']);nt.links.new(gamma.outputs[0],bs.inputs['Base Color'])
for side in ['L','R']:
 ob=bpy.data.objects['Iris_'+side];c=np.array(D['eyes'][0 if side=='L' else 1])-np.array(ob.location);me=ob.data;uv=me.uv_layers.new(name='T22_iris_detail_only')
 for lp in me.loops:
  q=(np.array(me.vertices[lp.vertex_index].co)-c)@M[:2].T;uv.data[lp.index].uv=((587.50+q[0]*18/6.05)/1086,1-(459.20-q[1]*18/6.05)/1448)
 me.materials[0]=mat;ob['texture_scope']='Only the iris disk samples the approved T22 iris; sclera, lids and facial geometry remain physical surfaces.'
sc=bpy.context.scene;sc.render.threads_mode='FIXED';sc.render.threads=6;sc.cycles.samples=24;bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11L.blend'))
for name,tag in [('Core_T22_pose','front'),('Core_P14_pose','side'),('View_threequarter','threequarter')]:
 sc.camera=bpy.data.objects[name];sc.render.filepath=str(R/f'renders/r11l-{tag}.png');bpy.ops.render.render(write_still=True)
print('R11L_DONE',flush=True)
