import bpy,pathlib,json,numpy as np,math
from mathutils import Vector
from mathutils.kdtree import KDTree
R=pathlib.Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11J.blend'),load_ui=False)
D=json.loads((R/'face-r11h.json').read_text());h=bpy.data.objects['Carrillo_Head'];V=np.array([v.co[:] for v in h.data.vertices]);W=V.copy();M=np.array(D['M']);fw=M[2];Q=V@M[:2].T
# Fair the outer canthus into the temporal surface rather than retaining a deep corner pocket.
for patch in D['patches']:
 ids=patch['rings'][0];corner=max(ids,key=lambda i:patch['side']*V[i,0]);q=Q[corner]
 weight=np.exp(-((Q[:,0]-q[0])/6.0)**2-((Q[:,1]-q[1])/6.5)**2)*np.clip((25-V[:,1])/14,0,1)
 W+=fw*(2.8*weight)[:,None]
 # Reduce the uniform convex pad below the outer eyelid while preserving the lid roll.
 q2=q+[-patch['side']*4,-9]
 weight2=np.exp(-((Q[:,0]-q2[0])/9)**4-((Q[:,1]-q2[1])/6)**4)*np.clip((20-V[:,1])/12,0,1)
 W-=fw*(.9*weight2)[:,None]
# A subtle supratip transition and paired tip domes; no general alar widening.
x,y,z=V.T;front=np.clip((-12-y)/12,0,1)
supratip=np.exp(-(x/6.5)**4-((z+25)/5.5)**4)*front;W[:,1]+=1.45*supratip
domes=np.exp(-((abs(x)-4.0)/3.2)**4-((z+34)/5.0)**4)*front;W[:,1]-=.8*domes
# Support the lateral chin transition and define the jaw body locally.
chin=np.exp(-((abs(x)-18)/8)**4-((z+98)/11)**4)*np.clip((12-y)/17,0,1);W[:,0]+=np.sign(x)*.7*chin
buccal=np.exp(-((abs(x)-45)/12)**4-((z+64)/17)**4-((y-11)/26)**4);W[:,0]-=np.sign(x)*.75*buccal
for v,p in zip(h.data.vertices,W):v.co=p
h.data.update()
tree=KDTree(len(V))
for i,p in enumerate(V):tree.insert(Vector(p),i)
tree.balance()
for ob in bpy.data.objects:
 if not ob.name.startswith(('R11_upper_l','R11_lower_w')):continue
 for sp in ob.data.splines:
  for point in sp.points:
   co=Vector(point.co[:3]);near=tree.find_n(co,4);weights=np.array([1/max(.2,d)**2 for _,_,d in near]);delta=sum((W[i]-V[i])*ww for (_,i,_),ww in zip(near,weights))/sum(weights);point.co=(*(co+Vector(delta)),1)
D['vertices']=W.tolist();D['K_changes']=['Outer canthal pocket softened into temple; lower outer orbital pad reduced','Supratip transition and paired domes; alar width retained','Lateral chin support and local jaw-body plane'];(R/'face-r11k.json').write_text(json.dumps(D))
sc=bpy.context.scene;sc.render.threads_mode='FIXED';sc.render.threads=6;sc.cycles.samples=24;skin=h.data.materials[0];neutral=bpy.data.materials['R10E_neutral_anatomy']
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'Carrillo_core_rebuild_R11K.blend'))
for cname,tag,material in [('Core_T22_pose','front',skin),('Core_T22_pose','front-neutral',neutral),('Core_P14_pose','side',skin),('Core_P14_pose','side-neutral',neutral),('View_threequarter','threequarter',skin)]:
 sc.camera=bpy.data.objects[cname];h.data.materials[0]=material;sc.render.filepath=str(R/f'renders/r11k-{tag}.png');bpy.ops.render.render(write_still=True)
print('R11K_DONE',flush=True)
