import bpy,pathlib
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11I.blend'),load_ui=False)
cameras={n:(bpy.data.objects[n].matrix_world.copy(),bpy.data.objects[n].data.ortho_scale) for n in ['Core_T22_pose','Core_P14_pose']}
lights={o.name:(o.matrix_world.copy(),o.data.energy,o.data.color[:],getattr(o.data,'size',1)) for o in bpy.data.objects if o.type=='LIGHT'}
sc=bpy.context.scene;res=(sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage);world=sc.world.copy();world.use_fake_user=True
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R9.blend'),load_ui=False)
sc=bpy.context.scene;sc.render.resolution_x,sc.render.resolution_y,sc.render.resolution_percentage=res;sc.render.threads_mode='FIXED';sc.render.threads=4;sc.cycles.samples=20
for o in bpy.data.objects:
 if o.type=='LIGHT' and o.name in lights:
  mx,e,c,size=lights[o.name];o.matrix_world=mx;o.data.energy=e;o.data.color=c;o.data.size=size
mat=bpy.data.materials.new('R11_control_neutral');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.30,.30,.30,1);bs.inputs['Roughness'].default_value=.68
bpy.data.objects['Carrillo_Head'].data.materials[0]=mat
for name,tag in [('Core_T22_pose','front'),('Core_P14_pose','side')]:
 data=bpy.data.cameras.new('R11_control_camera');data.type='ORTHO';data.ortho_scale=cameras[name][1];ob=bpy.data.objects.new('R11_control_camera',data);bpy.context.collection.objects.link(ob);ob.matrix_world=cameras[name][0];sc.camera=ob;sc.render.filepath=str(R/f'renders/r9-r11-camera-{tag}.png');bpy.ops.render.render(write_still=True)
print('R9_CONTROL_DONE',flush=True)
