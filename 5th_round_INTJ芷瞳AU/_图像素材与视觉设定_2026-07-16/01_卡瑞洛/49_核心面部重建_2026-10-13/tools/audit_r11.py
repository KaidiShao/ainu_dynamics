import bpy,pathlib,json,numpy as np
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];m=h.data
print('ATTRS',[(a.name,a.domain,a.data_type) for a in m.attributes])
print('MATS',[(x.name) for x in m.materials]);print('POLYMATS',np.unique([p.material_index for p in m.polygons],return_counts=True))
for mat in m.materials:
 print('MAT',mat.name)
 for n in mat.node_tree.nodes:
  print('NODE',n.name,n.type,getattr(n,'attribute_name',''),getattr(n,'uv_map',''),getattr(getattr(n,'image',None),'name',''))
  if n.type=='VALTORGB':print('RAMP',[(x.position,list(x.color)) for x in n.color_ramp.elements])
 for l in mat.node_tree.links:print('LINK',l.from_node.name,l.from_socket.name,'>',l.to_node.name,l.to_socket.name)
data={a.name:[d.value for d in a.data] for a in m.attributes if a.domain=='POINT' and a.data_type=='FLOAT'}
(R/'r11-baseline-attributes.json').write_text(json.dumps(data))
