import pathlib,json,sys,collections,math
R=pathlib.Path(__file__).resolve().parents[1];O=R.parent/'47_三维头模结构试验_2026-10-12';P=R.parent/'48_Blender头模精修_2026-10-13';sys.path.insert(0,str(O/'tools/python'))
import numpy as np
from scipy.interpolate import PchipInterpolator,RBFInterpolator
D=json.loads((R/'r11-baseline.json').read_text());V=np.array(D['vertices']);faces=D['faces'];uv={k:np.array(v) for k,v in D['uv'].items()}
d=json.loads((R/'structure-r10.json').read_text());M=np.array(d['M']);cam=d['camera'];forward=M[2];Q=V@M[:2].T
eyes=np.array(json.loads((R/'r10c-manifest.json').read_text())['eyes']);L=json.loads((O/'landmarks.json').read_text());lm=np.array(L['T22']['landmarks'])[:468,:2];lq=(lm*[1086,-1448]-cam['translation'])/cam['scale_pixels_per_model_unit']
f03=np.array(json.loads((P/'base-landmarks.json').read_text())['F03']['landmarks'])[:468,:2]*[1,-1]+[0,1]
uvf=RBFInterpolator(lq,f03,kernel='thin_plate_spline',smoothing=.6)
oldedges=collections.Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in faces for i in range(len(f)))
remove=set();patches=[]
for sign,c in zip([-1,1],eyes):
 inside=(((V[:,0]-sign*32)/23)**2+((V[:,2]-2)/21)**2<1)&(V[:,1]<60)
 drop={k for k,f in enumerate(faces) if all(inside[i] for i in f)};remove.update(drop)
 e=collections.Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for k,f in enumerate(faces) if k not in drop for i in range(len(f)))
 edges=[p for p,n in e.items() if n==1 and oldedges[p]>1];adj=collections.defaultdict(list)
 for a,b in edges:adj[a].append(b);adj[b].append(a)
 assert all(len(x)==2 for x in adj.values())
 root=min(adj);loop=[root];prev=None;cur=root
 while True:
  nxt=next(n for n in adj[cur] if n!=prev)
  if nxt==root:break
  loop.append(nxt);prev,cur=cur,nxt
 assert len(loop)==len(adj)
 # CCW in the reference camera plane, so the visible surface points outward.
 pts=Q[loop];area=np.sum(pts[:,0]*np.roll(pts[:,1],-1)-pts[:,1]*np.roll(pts[:,0],-1))
 if area<0:loop=loop[::-1];pts=Q[loop]
 center=M[:2]@c;rawtheta=np.arctan2(pts[:,1]-center[1],pts[:,0]-center[0])
 lengths=np.linalg.norm(np.roll(pts,-1,axis=0)-pts,axis=1)
 theta=rawtheta[0]+2*np.pi*np.r_[0,np.cumsum(lengths[:-1])]/sum(lengths)
 theta=(theta+np.pi)%(2*np.pi)-np.pi
 boundary_lm=([33,246,161,160,159,158,157,173,133,155,154,153,145,144,163,7] if sign<0 else [263,466,388,387,386,385,384,398,362,382,381,380,374,373,390,249])
 inner=lq[boundary_lm];angles=np.arctan2(inner[:,1]-center[1],inner[:,0]-center[0]);radii=np.linalg.norm(inner-center,axis=1);order=np.argsort(angles);angles=angles[order];radii=radii[order]
 radius=PchipInterpolator(np.r_[angles[-2:]-2*np.pi,angles,angles[:2]+2*np.pi],np.r_[radii[-2:],radii,radii[:2]])(theta)
 iq=center+np.column_stack([np.cos(theta),np.sin(theta)])*radius[:,None]
 depth_c=c@forward;outer_depth=V[loop]@forward
 # Elliptical front globe envelope; the far corners terminate in soft canthal tissue.
 r2=np.sum((iq-center)**2,axis=1);aperture=depth_c+np.sqrt(np.maximum(25.,12.3**2-r2))
 rings=[]
 for s in [0,.025,.065,.13,.22,.34,.49,.66,.83,1.]:
  if s==1:rings.append(loop);continue
  coords=(1-s)*iq+s*pts
  out=[];upper=np.clip((np.sin(theta)+.15)/.75,0,1)
  # Lid body / crease / orbital hood, joined with a continuous depth profile.
  blend=s*s*(3-2*s)
  depth=(1-blend)*aperture+blend*outer_depth
  depth+=(.28+upper*.18)*np.exp(-((s-.065)/.055)**2)-upper*.25*np.exp(-((s-.23)/.09)**2)
  rr=np.sum((coords-center)**2,axis=1)
  guard=depth_c+np.sqrt(np.maximum(0,12.18**2-rr))
  depth=np.where(rr<12.18**2,np.maximum(depth,guard),depth)
  for q,z in zip(coords,depth):
   p=q@M[:2]+z*forward;out.append(len(V));V=np.vstack([V,p]);Q=np.vstack([Q,q])
   for name in uv:
    if name=='T22_core_reference':value=((q*cam['scale_pixels_per_model_unit']+cam['translation'])*[1,-1])/[1086,1448]*[1,-1]+[0,1]
    elif name=='F03_reference_projection':value=uvf(q[None,:])[0]
    else:value=uvf(q[None,:])[0]
    uv[name]=np.vstack([uv[name],value])
  rings.append(out)
 newfaces=[]
 for a,b in zip(rings[:-1],rings[1:]):
  for i in range(len(loop)):
   j=(i+1)%len(loop);newfaces.append([a[i],b[i],b[j],a[j]])
 # A thin inner turn of the eyelid, left open behind the visible rim.
 inner_ids=[]
 for i in rings[0]:
  p=V[i]-forward*.65;inner_ids.append(len(V));V=np.vstack([V,p]);Q=np.vstack([Q,Q[i]])
  for name in uv:uv[name]=np.vstack([uv[name],uv[name][i]])
 for i in range(len(loop)):
  j=(i+1)%len(loop);newfaces.append([rings[0][i],inner_ids[i],inner_ids[j],rings[0][j]])
 patches.append({'side':sign,'outer':loop,'faces':newfaces,'rings':rings,'removed_faces':len(drop)})
 print('PATCH',sign,'boundary',len(loop),'removed',len(drop),'new faces',len(newfaces))
F=[f for i,f in enumerate(faces) if i not in remove]+[f for p in patches for f in p['faces']]
out={'vertices':V.tolist(),'faces':F,'uv':{k:v.tolist() for k,v in uv.items()},'patches':patches,'removed_faces':len(remove),'eyes':eyes.tolist(),'M':M.tolist(),'method':'Remove complete old orbital shells; reconstruct continuous concentric lid surfaces from T22 aperture to preserved outer boundary. No image-generation replacement.'}
(R/'orbits-r11.json').write_text(json.dumps(out));print('R11 mesh',len(V),len(F))
