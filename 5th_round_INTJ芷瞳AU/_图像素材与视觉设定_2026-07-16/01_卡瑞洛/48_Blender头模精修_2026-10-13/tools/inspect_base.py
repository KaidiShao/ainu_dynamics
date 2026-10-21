import bpy,json,pathlib
R=pathlib.Path(__file__).resolve().parents[1]
source=R/'assets/human-base/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend'
with bpy.data.libraries.load(str(source),link=False) as (f,t):
 print('AVAILABLE_OBJECTS',f.objects,flush=True)
 t.objects=[name for name in f.objects if any(w in name.lower() for w in ['head','eye'])]
out=[]
for o in t.objects:
 if not o:continue
 bpy.context.collection.objects.link(o)
 d={'name':o.name,'type':o.type,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'dimensions':list(o.dimensions),'modifiers':[(m.name,m.type) for m in o.modifiers]}
 if o.type=='MESH':
  d['vertices']=len(o.data.vertices);d['polygons']=len(o.data.polygons);d['materials']=[m.name if m else None for m in o.data.materials];d['groups']=[g.name for g in o.vertex_groups];d['bounds_local']=[[min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)] for i in range(3)]
 out.append(d)
(R/'base-inventory.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('INVENTORY',json.dumps(out),flush=True)
prefs=bpy.context.preferences.addons['cycles'].preferences
try:
 prefs.get_devices();print('CYCLES_DEVICES',[(d.name,d.type) for d in prefs.devices],flush=True)
except Exception as e:print(e)
print('BLENDER_OK',bpy.app.version_string,flush=True)
