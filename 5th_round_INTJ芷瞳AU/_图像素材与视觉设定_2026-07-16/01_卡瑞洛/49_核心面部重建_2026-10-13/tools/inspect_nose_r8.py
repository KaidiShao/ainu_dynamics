import bpy,pathlib,json,numpy as np
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R8.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];kb=h.data.shape_keys.key_blocks;V=np.array([v.co[:] for v in kb[0].data])
for k in list(kb)[1:]:V+=(np.array([v.co[:] for v in k.data])-np.array([v.co[:] for v in k.relative_key.data]))*k.value
(R/'r8-control-geometry.json').write_text(json.dumps({'vertices':V.tolist(),'faces':[list(p.vertices) for p in h.data.polygons]}))
ids=np.where((abs(V[:,0])<1.7)&(V[:,1]<5)&(V[:,2]>-52)&(V[:,2]<23))[0]
print('CENTERLINE',[(int(i),V[i].round(2).tolist()) for i in sorted(ids,key=lambda i:-V[i,2])])
ids=np.where((V[:,0]>8)&(V[:,0]<23)&(V[:,1]<-8)&(V[:,2]>-46)&(V[:,2]<-29))[0]
print('ALAR_REGION',[(int(i),V[i].round(2).tolist()) for i in ids])
