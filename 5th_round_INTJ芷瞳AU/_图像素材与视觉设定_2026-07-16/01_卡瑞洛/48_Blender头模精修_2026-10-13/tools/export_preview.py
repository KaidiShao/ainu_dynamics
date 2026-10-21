import bpy,pathlib,math,json
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_3D_working.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];uv=h.data.uv_layers.new(name='Baked_head_atlas')
for p in h.data.polygons:
 vals=[]
 for li in p.loop_indices:
  x,y,z=h.data.vertices[h.data.loops[li].vertex_index].co
  vals.append((math.atan2(x,85-y)/math.tau+.5,(z+265)/435))
 if max(v[0] for v in vals)-min(v[0] for v in vals)>.5:vals=[(u+1 if u<.5 else u,v) for u,v in vals]
 for li,co in zip(p.loop_indices,vals):uv.data[li].uv=co
h.data.uv_layers.active=uv;uv.active_render=True
mat=h.data.materials[0];nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');output=nt.nodes.get('Material Output')
tex=bpy.data.images.new('Carrillo_skin_baked',width=2048,height=2048,alpha=False)
node=nt.nodes.new('ShaderNodeTexImage');node.image=tex
for n in nt.nodes:n.select=False
node.select=True;nt.nodes.active=node
em=nt.nodes.new('ShaderNodeEmission');nt.links.new(bs.inputs['Base Color'].links[0].from_socket,em.inputs['Color']);nt.links.new(em.outputs[0],output.inputs['Surface'])
bpy.ops.object.select_all(action='DESELECT');h.select_set(True);bpy.context.view_layer.objects.active=h
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=1;sc.render.bake.margin=8;sc.render.bake.use_clear=True
bpy.ops.object.bake(type='EMIT')
tex.filepath_raw=str(R/'assets/carrillo_skin_projection.png');tex.file_format='PNG';tex.save()
webmat=bpy.data.materials.new('Projected_skin_WEB');webmat.use_nodes=True;bs=webmat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.7;bs.inputs['Specular IOR Level'].default_value=.25
tn=webmat.node_tree.nodes.new('ShaderNodeTexImage');tn.image=tex
un=webmat.node_tree.nodes.new('ShaderNodeUVMap');un.uv_map=uv.name
webmat.node_tree.links.new(un.outputs[0],tn.inputs['Vector']);webmat.node_tree.links.new(tn.outputs[0],bs.inputs['Base Color'])
h.data.materials[0]=webmat
for layer in list(h.data.uv_layers):
 if layer.name!=uv.name:h.data.uv_layers.remove(layer)
# Simplify only the web groom; the canonical Blender project keeps all fibres.
for name,stride in [('Carrillo_wavy_groom',6),('Long_loose_front_locks',3)]:
 o=bpy.data.objects.get(name)
 if not o:continue
 old=o.data;cu=bpy.data.curves.new(name+'_web','CURVE');cu.dimensions='3D';cu.bevel_depth=old.bevel_depth*1.65;cu.bevel_resolution=0
 for i,sp in enumerate(old.splines):
  if i%stride:continue
  ns=cu.splines.new('POLY');ns.points.add(len(sp.points)-1)
  ns.points.foreach_set('co',[v for p in sp.points for v in p.co]);ns.points.foreach_set('radius',[p.radius for p in sp.points])
 o.data=cu
 hm=bpy.data.materials.get('Web_dark_hair')
 if not hm:
  hm=bpy.data.materials.new('Web_dark_hair');hm.use_nodes=True
  hb=hm.node_tree.nodes.get('Principled BSDF');hb.inputs['Base Color'].default_value=(.008,.004,.002,1);hb.inputs['Roughness'].default_value=.68;hb.inputs['Specular IOR Level'].default_value=.22
 cu.materials.append(hm)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
bpy.ops.object.select_all(action='DESELECT')
for o in sc.objects:
 if o.type=='MESH':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'carrillo-web-preview.glb'),export_format='GLB',use_selection=True,export_apply=True,export_texcoords=True,export_normals=True,export_yup=True,export_cameras=False,export_lights=False)
manifest={'status':'Working candidate, likeness not author-approved','canonical':'Carrillo_3D_working.blend','preview':'carrillo-web-preview.glb','web_hair_stride':6,'texture':'Softer-light F03 projection with silhouette blending; some photographed shading remains','rendered_views':['front','threequarter','near-profile','neutral'],'objects':[{ 'name':o.name,'type':o.type,'vertices':len(o.data.vertices) if o.type=='MESH' else 0} for o in sc.objects if o.type=='MESH']}
(R/'model-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('EXPORT_DONE',flush=True)

