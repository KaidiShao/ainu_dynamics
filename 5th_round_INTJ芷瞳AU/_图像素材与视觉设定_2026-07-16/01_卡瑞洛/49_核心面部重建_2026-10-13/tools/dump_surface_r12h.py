import bpy,pathlib,numpy as np
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R12.blend'),load_ui=False);h=bpy.data.objects['Carrillo_Head'];h.data.update()
np.savez_compressed(R/'depth-r12/surface-r12g.npz',vertices=np.array([v.co[:] for v in h.data.vertices]),normals=np.array([v.normal[:] for v in h.data.vertices]))
print('SURFACE_DUMPED',flush=True)
