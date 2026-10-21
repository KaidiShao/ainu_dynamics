import bpy,pathlib,numpy as np
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11L.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];deps=bpy.context.evaluated_depsgraph_get();ev=h.evaluated_get(deps)
mesh=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=deps);h.data=mesh;h.modifiers.clear()
np.save(R/'depth-r12/dense-base.npy',np.array([v.co[:] for v in mesh.vertices]))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'depth-r12/dense-base.blend'))
print('DENSE_BASE',len(mesh.vertices),flush=True)
