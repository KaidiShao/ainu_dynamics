import bpy,pathlib,json
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R3.blend'),load_ui=False)
for ob in bpy.data.objects:
 if ob.name.startswith(('Iris_','Eyeball_')):
  print(ob.name)
  for m in ob.data.materials:
   for n in m.node_tree.nodes:
    print(' NODE',n.name,n.bl_idname, getattr(n,'layer_name',None),getattr(n,'attribute_name',None))
   print(' LINKS',[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links])
for ob in bpy.data.objects:
 if ob.type=='LIGHT':print('LIGHT',ob.name,ob.data.energy,ob.location[:],getattr(ob.data,'size',None))
