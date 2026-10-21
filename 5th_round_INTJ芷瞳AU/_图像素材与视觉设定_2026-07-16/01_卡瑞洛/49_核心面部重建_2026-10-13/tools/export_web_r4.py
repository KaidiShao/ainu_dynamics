import bpy,pathlib,json,sys
R=pathlib.Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
source=args[0] if args else 'Carrillo_core_rebuild_R4.blend'
output=args[1] if len(args)>1 else 'carrillo-core-r4.glb'
bpy.ops.wm.open_mainfile(filepath=str(R/source),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];uvname='F03_reference_projection'
# Bake the evaluated surface so active corrective shape keys and subdivision
# are carried into the preview. The saved native sculpt stays editable.
deps=bpy.context.evaluated_depsgraph_get()
evaluated=bpy.data.meshes.new_from_object(h.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
h.data=evaluated
for modifier in list(h.modifiers):h.modifiers.remove(modifier)
for name in [v.name for v in h.data.uv_layers]:
 if name!=uvname:h.data.uv_layers.remove(h.data.uv_layers[name])
img=next(n.image for n in h.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
m=bpy.data.materials.new('Projected_skin_WEB');m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.74;bs.inputs['Specular IOR Level'].default_value=.18
tn=nt.nodes.new('ShaderNodeTexImage');tn.image=img
nt.links.new(tn.outputs['Color'],bs.inputs['Base Color']);h.data.materials[0]=m
for name,stride in [('Carrillo_wavy_groom',6),('Long_loose_front_locks',3)]:
 o=bpy.data.objects[name];old=o.data;cu=bpy.data.curves.new(name+'_web','CURVE');cu.dimensions='3D';cu.bevel_depth=old.bevel_depth*4.2;cu.bevel_resolution=0
 for i,sp in enumerate(old.splines):
  if i%stride:continue
  ns=cu.splines.new('POLY');ns.points.add(len(sp.points)-1);ns.points.foreach_set('co',[v for p in sp.points for v in p.co]);ns.points.foreach_set('radius',[p.radius for p in sp.points])
 o.data=cu
 hm=bpy.data.materials.get('Web_dark_hair')
 if not hm:
  hm=bpy.data.materials.new('Web_dark_hair');hm.use_nodes=True;hb=hm.node_tree.nodes.get('Principled BSDF');hb.inputs['Base Color'].default_value=(.006,.0035,.002,1);hb.inputs['Roughness'].default_value=.82;hb.inputs['Specular IOR Level'].default_value=.15
 cu.materials.append(hm)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
cap=bpy.data.objects['Hair_base_density'];cap.data.materials[0]=hm
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/output),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_yup=True,export_cameras=False,export_lights=False)
print('EXPORT_WEB_V2_DONE')


