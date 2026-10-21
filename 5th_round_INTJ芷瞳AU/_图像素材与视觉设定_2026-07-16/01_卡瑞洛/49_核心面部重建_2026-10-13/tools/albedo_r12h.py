"""Reference-driven vertex material; this does not alter reference images or rendered images."""
import pathlib,json,sys
R=pathlib.Path(__file__).resolve().parents[1];O=R.parent/'47_三维头模结构试验_2026-10-12';sys.path.insert(0,str(O/'tools/python'))
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
data=np.load(R/'depth-r12/surface-r12g.npz');V=data['vertices'];N=data['normals'];P=np.load(R/'depth-r12/warped-prior.npz');M=P['M'];q=P['landmark_q'];Q=V@M[:2].T
cam=json.loads((R/'structure-r10.json').read_text())['camera'];s=cam['scale_pixels_per_model_unit'];t=np.array(cam['translation']);uv=(Q*s+t)*[1,-1]
ref=json.loads((O/'landmarks.json').read_text())['T22'];im=np.array(Image.open(ref['path']).convert('RGB'))/255.;im=np.where(im<=.04045,im/12.92,((im+.055)/1.055)**2.4)
rgb=np.array([map_coordinates(im[:,:,i],[uv[:,1],uv[:,0]],order=1,mode='nearest') for i in range(3)]).T
nn=N@M.T;x,y,z=nn.T;X=np.c_[np.ones(len(V)),x,y,z,x*y,x*z,y*z,x*x-y*y,3*z*z-1];lum=rgb@np.array([.2126,.7152,.0722])
mask=(V[:,1]<18)&(abs(V[:,0])<59)&(Q[:,1]>-101)&(Q[:,1]<21)&(z>.15)&(lum>.008)&(lum<.58)
for center in q[[468,473]]:mask&=(((Q[:,0]-center[0])/18)**2+((Q[:,1]-center[1])/12)**2>1)
mask&=(((Q[:,0]-((q[13]+q[14])/2)[0])/31)**2+((Q[:,1]-((q[13]+q[14])/2)[1])/10)**2>1)
for center in q[[105,334]]:mask&=(((Q[:,0]-center[0])/22)**2+((Q[:,1]-center[1])/8)**2>1)
xx=X[mask];yy=lum[mask];weights=np.ones(len(yy));ridge=np.eye(9)*.008;ridge[0,0]=0
for it in range(12):
 beta=np.linalg.solve(xx.T@(xx*weights[:,None])+ridge,xx.T@(yy*weights));err=yy-xx@beta;scale=np.median(abs(err))+.001;weights=1/(1+(err/(2.5*scale))**2)
shade=np.clip(X@beta,.014,.65);gain=np.clip(.14/shade,.4,5)
albedo=np.clip(rgb*gain[:,None],0,.75)
def smooth(a):
 a=np.clip(a,0,1);return a*a*(3-2*a)
weight=smooth((z+.10)/.55)*smooth((30-V[:,1])/18)*smooth((Q[:,1]+116)/11)*smooth((39-Q[:,1])/17)*smooth((68-abs(V[:,0]))/14)
# Keep a restrained F03 contribution at poorly observed dark/edge areas.
weight*=.88*smooth(lum/.025)
np.savez_compressed(R/'depth-r12/albedo-r12h.npz',colours=albedo,weight=weight)
(R/'depth-r12/albedo-r12h-report.json').write_text(json.dumps({'source':ref['path'],'method':'Reference sampled onto real mesh vertices; robust second-order spherical-harmonic illumination estimate removed approximately. Blends into existing side material.','reference_modified':False,'geometry_modified':False,'fitted_skin_samples':int(mask.sum()),'shading_coefficients':beta.tolist(),'limitations':['Single-photo albedo and lighting separation is approximate.','Shadowed regions and silhouette retain more of the prior material.','Texture matching is not evidence of correct geometry.']},indent=2))
print('ALBEDO_READY',mask.sum(),np.percentile(gain,[5,50,95]),flush=True)
