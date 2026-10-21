import bpy,pathlib,json,math,hashlib
R=pathlib.Path(__file__).resolve().parents[1];p=R/'Carrillo_3D_working.blend'
bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False)
h=bpy.data.objects['Carrillo_Head']
assert all(math.isfinite(c) for v in h.data.vertices for c in v.co)
deps=bpy.context.evaluated_depsgraph_get();evaluated=h.evaluated_get(deps);surface=evaluated.to_mesh()
assert all(math.isfinite(c) for v in surface.vertices for c in v.co)
evaluated_count=len(surface.vertices);evaluated.to_mesh_clear()
assert all(i.packed_file or i.source=='GENERATED' for i in bpy.data.images if i.type=='IMAGE')
out={'blender_version':bpy.app.version_string,'project_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'head_base_vertices':len(h.data.vertices),'head_base_faces':len(h.data.polygons),'hair_strands':sum(len(o.data.splines) for o in bpy.context.scene.objects if o.type=='CURVE'),'inspection_cameras':[o.name for o in bpy.context.scene.objects if o.type=='CAMERA'],'packed_images':[i.name for i in bpy.data.images if i.packed_file],'geometry_finite':True,'likeness_status':'not passed; not an approved character anchor'}
out['evaluated_head_vertices']=evaluated_count
out['corrective_shape_keys']={k.name:k.value for k in h.data.shape_keys.key_blocks} if h.data.shape_keys else {}
out['status']='Local face-volume correction; overall likeness unapproved'
(R/'project-validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))

