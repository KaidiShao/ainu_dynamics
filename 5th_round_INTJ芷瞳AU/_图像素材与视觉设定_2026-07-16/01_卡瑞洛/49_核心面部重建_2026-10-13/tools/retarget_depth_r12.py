import pathlib,json,sys
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'47_三维头模结构试验_2026-10-12/tools/python'))
import numpy as np
from scipy.interpolate import LinearNDInterpolator
from scipy.spatial import cKDTree
p=np.load(R/'depth-r12/warped-prior.npz');M=p['M'];q=p['landmark_q'];V=np.load(R/'depth-r12/dense-base.npy');Q=V@M[:2].T;oldz=V@M[2]
interp=LinearNDInterpolator(p['q'],p['depth']);target=interp(Q);valid=np.isfinite(target)
delta=np.where(valid,target-oldz,0);delta=np.clip(delta,-9,9)
def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)
weight=smooth((25-V[:,1])/25)*smooth((V[:,2]+124)/20)*smooth((73-V[:,2])/25)*smooth((75-abs(V[:,0]))/16)
# Keep measured aperture and eyeball relationship. The orbital surface beyond the lid transitions to the prior.
for center in q[[468,473]]:
 rel=Q-center;r=np.sqrt((rel[:,0]/14.5)**2+(rel[:,1]/5.8)**2)
 weight*=smooth((r-1.02)/1.1)
# Keep the lip seam, but import philtrum and labiomental depth.
center=(q[13]+q[14])/2;rel=Q-center;r=np.sqrt((rel[:,0]/25)**2+(rel[:,1]/5.5)**2)
weight*=.25+.75*smooth((r-.55)/1.25)
delta*=weight*.78
# Smooth the displacement field on the spatial graph to avoid interpolation pinches.
tree=cKDTree(V);dist,ind=tree.query(V,k=12);weights=np.exp(-(dist/3.2)**2)
for iteration in range(3):
 avg=(delta[ind]*weights).sum(axis=1)/weights.sum(axis=1)
 delta=.68*delta+.32*avg
W=V+delta[:,None]*M[2]
np.save(R/'depth-r12/dense-r12a.npy',W)
report={'method':'Locally inferred 3DDFA_V2 depth, nonrigidly registered to T22 landmarks; native mesh retains frontal projection','max_delta':float(abs(delta).max()),'p95_delta':float(np.percentile(abs(delta),95)),'max_frontal_projection_change':float(abs((W-V)@M[:2].T).max()),'prior_scale':float(p['scale']),'prior_offset':float(p['offset'])}
(R/'depth-r12/retarget-report.json').write_text(json.dumps(report,indent=2));print(report)
