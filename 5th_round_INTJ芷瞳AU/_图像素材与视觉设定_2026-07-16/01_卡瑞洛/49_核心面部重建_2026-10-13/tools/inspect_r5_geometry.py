import bpy,pathlib,json,numpy as np
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R5.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];kb=h.data.shape_keys.key_blocks
v=np.array([x.co[:] for x in kb[0].data])
for k in list(kb)[1:]:v+=(np.array([p.co[:] for p in k.data])-np.array([p.co[:] for p in k.relative_key.data]))*k.value
(R/'r5-control-geometry.json').write_text(json.dumps({'vertices':v.tolist(),'faces':[list(p.vertices) for p in h.data.polygons]}))
for zc in [-35,-50,-65,-80,-95]:
 ids=np.where((v[:,0]>40)&(abs(v[:,2]-zc)<6)&(v[:,1]<80))[0]
 print('BAND',zc,[(int(i),v[i].round(1).tolist()) for i in ids])
print('CAMERAS',[(o.name,o.location[:],o.rotation_euler[:]) for o in bpy.data.objects if o.type=='CAMERA'])
