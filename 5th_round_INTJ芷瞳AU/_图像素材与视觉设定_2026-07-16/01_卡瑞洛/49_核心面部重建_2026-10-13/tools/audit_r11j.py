import bpy,bmesh,pathlib,json,numpy as np,collections
R=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11J.blend'),load_ui=False)
h=bpy.data.objects['Carrillo_Head'];m=h.data;bm=bmesh.new();bm.from_mesh(m)
unused=[v for v in bm.verts if not v.link_faces];unused_count=len(unused);bmesh.ops.delete(bm,geom=unused,context='VERTS');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
V=np.array([v.co[:] for v in m.vertices]);E=collections.defaultdict(list)
for p in m.polygons:
 f=list(p.vertices)
 for a,b in zip(f,f[1:]+f[:1]):E[tuple(sorted([a,b]))].append((a,b))
inconsistent=sum(len(x)==2 and x[0]==x[1] for x in E.values());nonmanifold=sum(len(x)>2 for x in E.values());boundary=sum(len(x)==1 for x in E.values())
deps=bpy.context.evaluated_depsgraph_get();ev=h.evaluated_get(deps);mesh=ev.to_mesh();mesh.calc_loop_triangles();vv=np.array([v.co[:] for v in mesh.vertices]);tt=np.array([list(t.vertices) for t in mesh.loop_triangles]);nn=np.cross(vv[tt[:,1]]-vv[tt[:,0]],vv[tt[:,2]]-vv[tt[:,0]]);areas=np.linalg.norm(nn,axis=1)/2
report={'source':'Carrillo_core_rebuild_R11J.blend','version':'R11J','finite':bool(np.isfinite(V).all()),'base_vertices':len(V),'base_polygons':len(m.polygons),'removed_unreferenced_vertices':unused_count,'inconsistent_shared_edge_winding':int(inconsistent),'nonmanifold_edges_over_two_faces':int(nonmanifold),'intentional_aperture_boundary_edges':int(boundary),'evaluated_vertices':len(vv),'evaluated_triangles':len(tt),'degenerate_triangles_under_1e-9':int(sum(areas<1e-9)),'limitations':['Numerical integrity is not a likeness judgement.','The inner eyelid and mouth turn has an open edge inside each aperture.','F03-based material contains residual photographic illumination.']}
ev.to_mesh_clear();(R/'geometry-audit-r11.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
if not report['finite'] or inconsistent or nonmanifold:raise RuntimeError('Mesh integrity failed')
h['geometry_audit']='geometry-audit-r11.json';bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11.blend'))

