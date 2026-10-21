import bpy,pathlib,json,numpy as np
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R6.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];kb=h.data.shape_keys.key_blocks;v=np.array([x.co[:] for x in kb[0].data])
for k in list(kb)[1:]:v+=(np.array([p.co[:] for p in k.data])-np.array([p.co[:] for p in k.relative_key.data]))*k.value
(R/'r6-control-geometry.json').write_text(json.dumps({'vertices':v.tolist(),'faces':[list(p.vertices) for p in h.data.polygons]}))
for label,ids in [('upper_margin',[1819,1813,2404,1818,1814,1815,1816]),('upper_fold',[1836,1837,2401,1838,1839,1840,1841]),('lower_margin',[1804,2406,1810,1811,2408,1812]),('lower_roll',[1846,2402,1845,1844,2403,1843]),('below_lower',[1607,2500,2508,2120,2117,2110,2258,1674])]:
 print(label,[(i,v[i].round(3).tolist()) for i in ids])
print('eyes',[(o.name,o.location[:]) for o in bpy.data.objects if o.name.startswith('Eyeball')])
