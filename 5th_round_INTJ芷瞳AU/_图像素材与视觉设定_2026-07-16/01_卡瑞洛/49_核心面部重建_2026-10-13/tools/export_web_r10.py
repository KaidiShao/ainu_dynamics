import bpy,pathlib,sys,json,math
R=pathlib.Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
source=args[0] if args else 'Carrillo_core_rebuild_R10F.blend'
output=args[1] if len(args)>1 else 'carrillo-core-r10.glb'
bpy.ops.wm.open_mainfile(filepath=str(R/source),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];deps=bpy.context.evaluated_depsgraph_get()
me=bpy.data.meshes.new_from_object(h.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps);h.data=me
for m in list(h.modifiers):h.modifiers.remove(m)
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
# Bake the existing material's base colour (including its scalp/brow masks).
# This is an atlas of the 3D material, not a replacement reference portrait.
mat=h.data.materials[0];nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');out=nt.nodes.get('Material Output')
for n in nt.nodes:
 if n.type=='TEX_IMAGE' and not n.inputs['Vector'].is_linked:
  uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='F03_reference_projection';nt.links.new(uv.outputs['UV'],n.inputs['Vector'])
uv=h.data.uv_layers.new(name='R10_web_atlas');h.data.uv_layers.active=uv;uv.active_render=True
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.1519,island_margin=.008,area_weight=.2);bpy.ops.object.mode_set(mode='OBJECT')
img=bpy.data.images.new('R10_existing_skin_colour_atlas',width=2048,height=2048,alpha=False);img.colorspace_settings.name='sRGB'
target=nt.nodes.new('ShaderNodeTexImage');target.image=img;nt.nodes.active=target
emit=nt.nodes.new('ShaderNodeEmission');nt.links.new(bs.inputs['Base Color'].links[0].from_socket,emit.inputs['Color']);nt.links.new(emit.outputs[0],out.inputs['Surface'])
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=1;sc.render.bake.margin=10
bpy.ops.object.bake(type='EMIT')
(R/'assets').mkdir(exist_ok=True);img.filepath_raw=str(R/'assets/r10-head-colour.png');img.file_format='PNG';img.save();img.pack()
webmat=bpy.data.materials.new('R10_web_skin_material_atlas');webmat.use_nodes=True;wn=webmat.node_tree;wb=wn.nodes.get('Principled BSDF');wb.inputs['Roughness'].default_value=.64;wb.inputs['Specular IOR Level'].default_value=.18
tex=wn.nodes.new('ShaderNodeTexImage');tex.image=img;wn.links.new(tex.outputs['Color'],wb.inputs['Base Color']);h.data.materials[0]=webmat
for name in [layer.name for layer in h.data.uv_layers]:
 if name!='R10_web_atlas':h.data.uv_layers.remove(h.data.uv_layers[name])
hm=bpy.data.materials.new('R10_web_dark_brown_hair');hm.use_nodes=True;hb=hm.node_tree.nodes.get('Principled BSDF');hb.inputs['Base Color'].default_value=(.006,.0028,.0013,1);hb.inputs['Roughness'].default_value=.6;hb.inputs['Specular IOR Level'].default_value=.16
curve_stats={}
for o in list(sc.objects):
 if o.type!='CURVE':continue
 old=o.data;stride=6 if o.name=='Carrillo_wavy_groom' else (3 if o.name=='Long_loose_front_locks' else 1)
 cu=bpy.data.curves.new(o.name+'_web','CURVE');cu.dimensions='3D';cu.bevel_depth=old.bevel_depth*math.sqrt(stride);cu.bevel_resolution=0
 for i,sp in enumerate(old.splines):
  if i%stride:continue
  ns=cu.splines.new('POLY');ns.points.add(len(sp.points)-1);ns.points.foreach_set('co',[v for p in sp.points for v in p.co]);ns.points.foreach_set('radius',[p.radius for p in sp.points])
 o.data=cu;cu.materials.append(hm);curve_stats[o.name]=len(cu.splines)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
# Keep the root surface dark and the physical eye components intact.
bpy.data.objects['Hair_base_density'].data.materials[0]=hm
bpy.ops.object.select_all(action='DESELECT')
for o in sc.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/output),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_yup=True,export_cameras=False,export_lights=False)
(R/'web-export-r10.json').write_text(json.dumps({'source':source,'output':output,'curves':curve_stats,'skin':'Existing F03-based shader baked to a non-overlapping UV atlas, including scalp and brow weights. Not T22 projection.','hair':'Downsampled fibres; Principled web substitute for native hair BSDF.','limitations':'Web light and corneal transmission differ from native Cycles renders.'},indent=2))
print('R10_WEB_EXPORT_DONE',curve_stats,flush=True)
