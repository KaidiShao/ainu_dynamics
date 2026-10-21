import bpy,pathlib,numpy as np,json
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R10G.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];keys=h.data.shape_keys.key_blocks;V=np.array([v.co[:] for v in keys[0].data]);W=np.array([v.co[:] for v in keys[1].data]);T=[]
for f in h.data.polygons:
 ids=list(f.vertices)
 for j in range(1,len(ids)-1):T.append([ids[0],ids[j],ids[j+1]])
T=np.array(T)
def n(v):return np.cross(v[T[:,1]]-v[T[:,0]],v[T[:,2]]-v[T[:,0]])
a=n(V);b=n(W);valid=(np.linalg.norm(a,axis=1)>1e-8)&(np.linalg.norm(b,axis=1)>1e-8);bad=np.where((np.sum(a*b,axis=1)<0)&valid)[0]
report={'vertices':len(V),'triangles':len(T),'finite':bool(np.isfinite(W).all()),'triangles_rotated_over_90deg':len(bad),'affected_faces':T[bad].tolist(),'max_shift':float(np.linalg.norm(W-V,axis=1).max())}
(R/'geometry-audit-r10g.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='affected_faces'}),flush=True)
