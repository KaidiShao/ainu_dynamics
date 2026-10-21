import bpy,pathlib,json,numpy as np
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11I.blend'),load_ui=False)
D=json.loads((R/'face-r11h.json').read_text());M=np.array(D['M']);print('DET M',np.linalg.det(M),'cross',np.cross(M[0],M[1]),'fw',M[2])
for o in bpy.data.objects:
 if not o.name.startswith(('Iris_','Cornea_','Eyeball_')):continue
 V=np.array([v.co[:] for v in o.data.vertices]);Ns=np.array([p.normal[:] for p in o.data.polygons]);ps=np.array([p.center[:] for p in o.data.polygons]);c=np.array(D['eyes'][0 if o.name.endswith('L') else 1])-np.array(o.location)
 print(o.name,'front dot',np.median(Ns@M[2]),'radial',np.median(np.sum(Ns*(ps-c),axis=1)), 'mat',o.data.materials[0].name)
