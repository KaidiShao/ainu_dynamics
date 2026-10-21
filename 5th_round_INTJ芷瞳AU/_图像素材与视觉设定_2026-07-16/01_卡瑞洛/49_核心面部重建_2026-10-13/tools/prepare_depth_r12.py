import pathlib,json,sys
R=pathlib.Path(__file__).resolve().parents[1];O=R.parent/'47_三维头模结构试验_2026-10-12';sys.path.insert(0,str(O/'tools/python'))
import numpy as np
from scipy.interpolate import RBFInterpolator,LinearNDInterpolator
from scipy.spatial import cKDTree
S=json.loads((R/'structure-r10.json').read_text());M=np.array(json.loads((R/'face-r11k.json').read_text())['M']);cam=S['camera'];s=cam['scale_pixels_per_model_unit'];t=np.array(cam['translation'])
prior=np.load(R/'depth-r12/T22-3ddfa.npz');P=prior['vertices'];lm=prior['landmarks'];ref=np.array(json.loads((O/'landmarks.json').read_text())['T22']['landmarks']);q=(ref[:,:2]*[1086,-1448]-t)/s
mp=[234,93,132,58,172,136,150,149,152,378,379,365,397,288,361,323,454,70,63,105,66,107,336,296,334,293,300,168,6,197,4,98,97,2,326,327,33,160,158,133,153,144,362,385,387,263,373,380,61,40,37,0,267,270,291,321,314,17,84,91,78,81,13,311,308,402,14,178]
src=(lm[:,:2]*[1,-1]-t)/s;dst=q[mp]
# Preserve T22's measured frontal layout while importing only an independent depth prior.
warp=RBFInterpolator(src,dst-src,kernel='thin_plate_spline',smoothing=4)
Q=(P[:,:2]*[1,-1]-t)/s;Q+=warp(Q)
D=json.loads((R/'face-r11k.json').read_text());V=np.array(D['vertices']);oldq=V@M[:2].T;oldz=V@M[2];depth=P[:,2]/s
interp=LinearNDInterpolator(Q,depth);values=interp(oldq)
used=np.zeros(len(V),bool);used[list({j for f in D['faces'] for j in f})]=True
sel=np.isfinite(values)&used&(V[:,1]<15)&(abs(V[:,0])<55)&(V[:,2]<20)&(V[:,2]>-95)
# Robust affine depth scale/offset; exclude open rims and estimate on broad structural regions.
sel&=(abs(V[:,0])<15)|((abs(V[:,0])>40)&(V[:,2]<-15))
A=np.c_[values[sel],np.ones(sel.sum())];b=oldz[sel]
scale,offset=np.linalg.lstsq(A,b,rcond=None)[0];scale=np.clip(scale,.85,1.15);offset=np.median(b-scale*A[:,0])
new=depth*scale+offset
np.savez_compressed(R/'depth-r12/warped-prior.npz',q=Q,depth=new,M=M,triangles=prior['triangles'],landmark_q=q,scale=scale,offset=offset)
diff=values*scale+offset-oldz
for name,mask in [('nose',(abs(V[:,0])<14)&(V[:,2]>-45)&(V[:,2]<8)),('cheek',(abs(V[:,0])>22)&(abs(V[:,0])<55)&(V[:,2]>-50)&(V[:,2]<-8)),('chin',(abs(V[:,0])<30)&(V[:,2]<-85)),('forehead',(abs(V[:,0])<40)&(V[:,2]>25))]:
 take=used&mask&np.isfinite(diff)&(V[:,1]<20);print(name,np.percentile(diff[take],[10,50,90]))
print('depth affine',scale,offset,'median keypoint warp',np.median(np.linalg.norm(dst-src,axis=1)))
