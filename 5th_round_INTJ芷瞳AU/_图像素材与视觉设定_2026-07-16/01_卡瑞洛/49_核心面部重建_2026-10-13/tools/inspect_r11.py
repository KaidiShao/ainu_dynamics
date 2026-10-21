import bpy,pathlib,json,numpy as np
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];kb=h.data.shape_keys.key_blocks;V=np.array([v.co[:] for v in kb[0].data])
for k in list(kb)[1:]:V+=(np.array([v.co[:] for v in k.data])-np.array([v.co[:] for v in k.relative_key.data]))*k.value
uv={}
for layer in h.data.uv_layers:
 arr=np.zeros((len(V),2));cnt=np.zeros(len(V))
 for l in h.data.loops:arr[l.vertex_index]+=np.array(layer.data[l.index].uv);cnt[l.vertex_index]+=1
 uv[layer.name]=(arr/np.maximum(cnt[:,None],1)).tolist()
objects=[]
for o in bpy.context.scene.objects:
 d={'name':o.name,'type':o.type,'location':list(o.location),'rotation':list(o.rotation_euler)}
 if o.type=='LIGHT':d.update(energy=o.data.energy,size=getattr(o.data,'size',None))
 if o.type=='CAMERA':d.update(scale=o.data.ortho_scale,ctype=o.data.type)
 if o.type=='CURVE':d.update(splines=len(o.data.splines),bevel=o.data.bevel_depth)
 objects.append(d)
data={'vertices':V.tolist(),'faces':[list(f.vertices) for f in h.data.polygons],'uv':uv,'objects':objects}
(R/'r11-baseline.json').write_text(json.dumps(data))
print(json.dumps({'objects':objects,'uv':list(uv),'material':h.data.materials[0].name,'nodes':[(n.name,n.type) for n in h.data.materials[0].node_tree.nodes]},indent=2))

