import pathlib,sys,json
R=pathlib.Path(__file__).resolve().parents[1];OLD=R.parent/'47_三维头模结构试验_2026-10-12'
sys.path.insert(0,str(OLD/'tools/python'))
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import spsolve
from scipy.interpolate import RBFInterpolator
d=json.loads((R/'r6-control-geometry.json').read_text());V=np.array(d['vertices']);N=len(V)
cam=np.array(json.loads((OLD/'head-fit.json').read_text())['metrics']['T22']['rotation']);M=np.column_stack((cam[:,0],-cam[:,2],cam[:,1]));forward=M[2]
eye_translation=-forward*1.25
mirror=cKDTree(V).query(V*[-1,1,1])[1]
upper=[1819,1813,2404,1818,1814,1815,1816]
lower=[1804,2406,1810,1811,2408,1812]
roll=[1846,2402,1845,1844,2403,1843]
below=[2500,2508,2120,2117,2110,2258]
targets={};roles={}
def project_lid(i,radius):
 p=V[i];center=np.array([np.sign(p[0])*31.44174,7.,1.4])+eye_translation;q=p-center
 dot=q@forward;disc=dot*dot-q@q+radius*radius
 # Rays just outside the globe continue to its tangent depth. Falling back
 # to a shallow translation here creates a discontinuity at the canthus.
 distance=-dot+np.sqrt(max(0.,disc))
 return forward*np.clip(distance,-8,1.5)
for ids,radius,role in [(upper,12.05,'upper_margin'),(lower,12.05,'lower_margin'),(roll,12.70,'lower_lid_roll')]:
 for i in ids:targets[i]=project_lid(i,radius);roles[i]=role
# A shallow crease follows the lower roll; it is not a painted dark line.
for i in below:
 near=min(roll,key=lambda j:abs(V[i,0]-V[j,0]));crease=.18*np.clip((39-abs(V[i,0]))/9,0,1);targets[i]=targets[near]-forward*crease;roles[i]='lower_lid_transition'
for ids,radius,role in [(upper,12.05,'upper_margin'),(lower,12.05,'lower_margin'),(roll,12.70,'lower_lid_roll')]:
 for i in ids:
  j=int(mirror[i]);targets[j]=project_lid(j,radius);roles[j]=role
for i in below:
 j=int(mirror[i]);near=min(roll,key=lambda n:abs(V[i,0]-V[n,0]));crease=.18*np.clip((39-abs(V[j,0]))/9,0,1);targets[j]=targets[int(mirror[near])]-forward*crease;roles[j]='lower_lid_transition'
# A shared displacement along each T22 viewing ray moves inner and outer
# surfaces together. The earlier harmonic trial let adjacent interior folds
# lag behind the margin. This field preserves projected triangle winding.
Q=[];values=[];smooth=[]
for i,delta in targets.items():Q.append(M[:2]@V[i]);values.append(delta@forward);smooth.append(2.)
for sign in [-1,1]:
 center=M[:2]@np.array([sign*31.44174,7,1.4])
 for radius in [(22,18),(27,25)]:
  for a in np.linspace(0,2*np.pi,36,endpoint=False):
   Q.append(center+[radius[0]*np.cos(a),radius[1]*np.sin(a)]);values.append(0.);smooth.append(.5)
field=RBFInterpolator(np.array(Q),np.array(values),kernel='thin_plate_spline',smoothing=np.array(smooth))
q=V@M[:2].T;t=np.clip(field(q),-8.5,1.5)
# Fade outside the two orbits and far behind the anterior head, continuously.
centers=[M[:2]@np.array([s*31.44174,7,1.4]) for s in [-1,1]]
radius=np.min([np.sqrt(((q[:,0]-c[0])/25)**2+((q[:,1]-c[1])/22)**2) for c in centers],axis=0)
fade=np.clip((1.15-radius)/.35,0,1);fade=fade*fade*(3-2*fade)
rear=np.clip((110-V[:,1])/75,0,1);rear=rear*rear*(3-2*rear)
D=t[:,None]*forward[None,:]*fade[:,None]*rear[:,None]
W=V+D
out={'vertices':W.tolist(),'eye_translation':eye_translation.tolist(),'anchors':[{'vertex':i,'role':roles[i],'delta':targets[i].tolist()} for i in targets],
 'method':'Shared camera-ray depth field preserves the T22 eye outline and moves internal folds coherently; translated globes, separate margin/roll/transition constraints.',
 'finite':bool(np.isfinite(W).all()),'max_displacement':float(np.linalg.norm(D,axis=1).max())}
(R/'lids-fit-r7.json').write_text(json.dumps(out,ensure_ascii=False),encoding='utf8')
print(json.dumps({k:out[k] for k in ['finite','max_displacement','eye_translation']}))
