import pathlib,sys,json,os
R=pathlib.Path(__file__).resolve().parents[1];P=R.parent/'48_Blender头模精修_2026-10-13';OLD=R.parent/'47_三维头模结构试验_2026-10-12'
sys.path.insert(0,str(OLD/'tools/python'))
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.spatial import cKDTree
B=json.loads((P/'base-geometry.json').read_text());F=json.loads((OLD/'head-fit.json').read_text())
V=np.array(B['vertices'])*63/71.7532
raw=json.loads((P/'base-surface-landmarks.json').read_text())
S=np.array([p['point'] for p in raw])*63/71.7532
canonical=[]
for line in (OLD/'assets/canonical_face_model.obj').read_text().splitlines():
 if line.startswith('v '):canonical.append([float(x) for x in line.split()[1:]])
C=np.array(canonical);mirror=cKDTree(C).query(C*[-1,1,1])[1]
# Use anatomical correspondences rather than nearest points on the fitted target.
S=(S+S[mirror]*[-1,1,1])/2
for i,(x,y,z) in enumerate(S):
 if 14<abs(x)<48 and -12<z<10 and (y>-3 or not raw[i]['hit']):
  rr=(abs(x)-31.5)**2+z*z
  if rr<11.46**2:S[i,1]=-np.sqrt(11.46**2-rr)-.15
bad=[i for i,q in enumerate(raw) if not q['hit']]
good=[i for i in range(len(S)) if i not in bad]
for i in bad:
 if not (14<abs(S[i,0])<48 and -12<S[i,2]<10):
  near=cKDTree(S[good][:,[0,2]]).query(S[i,[0,2]])[1];S[i,1]=S[good[near],1]
T0=np.array(F['face']['vertices']);T=np.column_stack((T0[:,0],-T0[:,2],T0[:,1]))
# Camera constraint from T22. All depth edits preserve its projected image coordinates.
cam=np.array(F['metrics']['T22']['rotation'])
M=np.column_stack((cam[:,0],-cam[:,2],cam[:,1]))
XZ=M[:2][:,[0,2]]
EY=np.array([31.44174,3.,2.5]);radius=12.
eye_changed=[]
for i,(x,y,z) in enumerate(T.copy()):
 ax=abs(x);dx=ax-EY[0];dz=z-EY[2];d2=dx*dx+dz*dz
 if 17<ax<46 and -8<z<12 and d2<(radius-.15)**2:
  surface=EY[1]-np.sqrt(radius*radius-d2)-.3
  # Skin may stay in front of the globe, but must not pass through it.
  new_y=min(y,surface)
  wy=np.exp(-((z-2.5)/11)**4)*min(1,max(0,(46-ax)/3))
  dy=(new_y-y)*wy
  correction=np.linalg.solve(XZ,-M[:2,1]*dy)
  T[i]+=[correction[0],dy,correction[1]]
  if abs(dy)>.1:eye_changed.append(i)
# A coherent orbit and closed mouth are higher-priority than broad cheek estimates.
smooth=np.full(468,4.)
for i in range(468):
 x,y,z=S[i]
 if 14<abs(x)<48 and -15<z<19:smooth[i]=.55
 if abs(x)<23 and -57<z<-5:smooth[i]=.6
 if abs(x)<30 and -82<z<-58:smooth[i]=.4
# Preserve unaffected skull/neck rather than extending an unconstrained warp.
# A view-plane displacement field preserves front/back ordering of the anatomy.
# The previous 3D field could extrapolate an inner orbital/oral shell through skin.
anchors=np.array([[x,z] for x in [-115,-75,0,75,115] for z in [-250,-180,115,145]],float)
Q=np.r_[S[:,[0,2]],anchors];D=np.r_[T-S,np.zeros((len(anchors),3))]
W=np.r_[np.maximum(smooth,1.5),np.full(len(anchors),10.)]
coords,inverse=np.unique(np.round(Q,5),axis=0,return_inverse=True)
dd=np.zeros((len(coords),3));ww=np.zeros(len(coords));counts=np.zeros(len(coords))
for i,j in enumerate(inverse):dd[j]+=D[i];ww[j]+=W[i];counts[j]+=1
dd/=counts[:,None];ww/=counts
plane=RBFInterpolator(coords,dd[:,[0,2]],kernel='thin_plate_spline',smoothing=ww,degree=1)
depth=RBFInterpolator(coords,dd[:,1],kernel='thin_plate_spline',smoothing=np.maximum(ww,18),degree=1)
def rbf(points):
 q=points[:,[0,2]];xz=plane(q);y=depth(q)
 return np.column_stack((xz[:,0],y,xz[:,1]))
delta=rbf(V)
rear=np.clip((100-V[:,1])/65,0,1);rear=rear*rear*(3-2*rear)
VV=V+delta*rear[:,None]
# Two separately named photo mappings. Images are illumination-bearing references.
UV={}
refs=json.loads((OLD/'landmarks.json').read_text())
refs['F03']=json.loads((P/'base-landmarks.json').read_text())['F03']
for key in ['T22','F03']:
 uv=np.array(refs[key]['landmarks'])[:468,:2]*[1,-1]+[0,1]
 uvfit=RBFInterpolator(T,uv,kernel='thin_plate_spline',smoothing=.5)
 UV[key]=uvfit(VV).tolist()
out={'vertices':VV.tolist(),'faces':B['faces'],'uv':UV,'eyes':[[-EY[0],EY[1],EY[2]],EY.tolist()],
 'eye_radius':radius,'source_landmarks':S.tolist(),'target_landmarks':T.tolist(),'camera_T22':F['metrics']['T22'],
 'references':{k:refs[k]['path'] for k in ['T22','F03']},
 'method':'Fresh anatomical base, canonical landmark pairing, eye-surface constraint preserving T22 projection; view-plane displacement preserves internal shell depth ordering. Not an exact reconstruction.',
 'eye_constraint_count':len(eye_changed)}
(R/'core-fit-r2.json').write_text(json.dumps(out),encoding='utf8')
print(json.dumps({'eye_constraints':len(eye_changed),'eyes':out['eyes'],'bounds':[VV.min(0).tolist(),VV.max(0).tolist()],'correspondence_median_error':float(np.median(np.linalg.norm(S+rbf(S)-T,axis=1)))}))

