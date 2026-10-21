import sys,pathlib,json
R=pathlib.Path(__file__).resolve().parents[1];OLD=R.parent/'47_三维头模结构试验_2026-10-12'
sys.path.insert(0,str(OLD/'tools/python'))
import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.spatial import cKDTree
base=json.loads((R/'base-geometry.json').read_text())
V=np.array(base['vertices']);surf=json.loads((R/'base-surface-landmarks.json').read_text())
S=np.array([v['point'] for v in surf])
F=json.loads((OLD/'head-fit.json').read_text())
T=np.array(F['face']['vertices']);T=np.column_stack((T[:,0],-T[:,2],T[:,1]))
scale=63/(35.8766*2)
S*=scale;V*=scale
for i in [1,4,6,33,133,159,145,263,362,0,13,14,17,152,234,454,10]:
 print(i,'SOURCE',S[i].round(2),'TARGET',T[i].round(2))
# front ray missing the rim may hit inside/back of head. Replace those uncertain depths.
bad=np.array([not q['hit'] for i,q in enumerate(surf)])
good=np.flatnonzero(~bad)
_,near=cKDTree(S[good][:,[0,2]]).query(S[bad][:,[0,2]])
S[bad,1]=S[good[near],1]
for i,p in enumerate(S):
 if 16<abs(p[0])<46 and -9<p[2]<7 and p[1]>-3:
  dist2=(abs(p[0])-31.5)**2+p[2]**2
  if dist2<(13.05*scale)**2:
   S[i,1]=-np.sqrt((13.05*scale)**2-dist2)
# Symmetrize the correspondence field before fitting. 
knn=cKDTree(T).query(T*np.array([-1,1,1]))[1]
S=(S+S[knn]*np.array([-1,1,1]))*.5
# Keep base anatomy and add only smooth deformation field. No remeshing of eyelids/lips.
# Outer-cheek contour is low confidence in image depth; use core face constraints, with regularization.
idx=np.arange(468)
# RBF smoothing reduces detector noise. Thin plate has affine linear far-field; anchors constrain back skull.
anchors=[];targets=[]
for x in [-85,-50,0,50,85]:
 for y,z in [(100,20),(125,-60),(80,95),(35,120),(70,-145),(20,-205),(80,-230)]:
  anchors.append([x,y,z]);targets.append([x*.96,y*.94,z])
A=np.array(anchors,float)
SS=np.concatenate((S,A),axis=0);TT=np.concatenate((T,np.array(targets)),axis=0)
smooth=np.concatenate((np.full(468,12.0),np.full(len(A),35.0)))
rbf=RBFInterpolator(SS,TT-SS,kernel='thin_plate_spline',smoothing=smooth,degree=1)
VV=V+rbf(V)
E=np.array([[-31.5,0,0],[31.5,0,0]],float);EE=E+rbf(E)
# transfer F03 photograph coordinates through dense landmark correspondence.
FL=json.loads((R/'base-landmarks.json').read_text())['F03']
uv=np.array(FL['landmarks'])[:468,:2];uv[:,1]=1-uv[:,1]
# photo UV interpolator is fit to target face x/up plus depth for contour consistency
uvfit=RBFInterpolator(T,uv,kernel='thin_plate_spline',smoothing=3.0)
UV=uvfit(VV)
out={'vertices':VV.tolist(),'faces':base['faces'],'uv':UV.tolist(),'eyes':EE.tolist(),'eye_radius':13.05*scale,'target_lm':T.tolist(),'base_correspondences':S.tolist(),'source_scale':scale}
(R/'fitted-geometry-v1.json').write_text(json.dumps(out),encoding='utf8')
print('EYES',EE.round(3),'BOUNDS',VV.min(0).round(2),VV.max(0).round(2),'BAD_RAYS',bad.sum())

