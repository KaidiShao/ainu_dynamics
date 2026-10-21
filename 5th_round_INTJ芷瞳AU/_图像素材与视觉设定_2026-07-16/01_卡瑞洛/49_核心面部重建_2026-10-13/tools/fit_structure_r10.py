import pathlib,json,sys
R=pathlib.Path(__file__).resolve().parents[1];OLD=R.parent/'47_三维头模结构试验_2026-10-12'
sys.path.insert(0,str(OLD/'tools/python'))
import numpy as np
from scipy.spatial import cKDTree
from scipy.interpolate import RBFInterpolator
d=json.loads((R/'r9-inspection.json').read_text());V=np.array(d['vertices']);uv=np.array(d['uv']['T22_core_reference'])
cam=json.loads((OLD/'head-fit.json').read_text())['metrics']['T22'];r=np.array(cam['rotation']);M=np.column_stack((r[:,0],-r[:,2],r[:,1]));fwd=M[2]
scale=cam['scale_pixels_per_model_unit'];trans=np.array(cam['translation']);size=np.array([1086,1448])
target=(uv*size-np.array([0,1448])-trans)/scale
Q=V@M[:2].T;D=target-Q
mask=(abs(V[:,0])<58)&(V[:,1]<18)&(V[:,2]>-106)&(V[:,2]<28)&(np.linalg.norm(D,axis=1)<12)
print('UV projection correction distribution',np.percentile(np.linalg.norm(D[mask],axis=1),[0,25,50,75,95,100]))
for ids in [[1819,1813,2404,1818,1814,1815,1816],[1837,2405,1830,1827,1828,1829],[2335,2401,1838,1839,1840],[1565,3180,3177,3174,2512],[1804,2406,1810,1811,2408,1812],[1846,2402,1845,1844,2403,1843],[1758,1759,1760,1761,1762,1763,1764],[1778,1790,1777,1799,1782,1779],[3079,1883,2059,1882,2075,2020]]:
 print('ROW',[(i,V[i].round(2).tolist(),D[i].round(2).tolist()) for i in ids])

# Restore the fitted reference outline in the frontal viewing plane. This
# is a geometric constraint only; it does not project the photo as a render.
ids=np.where(mask)[0];coords=Q[ids];delta=D[ids]
anchors=[]
for x in [-120,-85,0,85,120]:
 for z in [-190,-135,90,150]:anchors.append([x,z])
coords=np.r_[coords,anchors];delta=np.r_[delta,np.zeros((len(anchors),2))]
uq,ind=np.unique(np.round(coords,4),axis=0,return_index=True)
field=RBFInterpolator(coords[ind],delta[ind],kernel='thin_plate_spline',smoothing=3)
shift=field(Q);length=np.linalg.norm(shift,axis=1);shift*=np.minimum(1,7/np.maximum(length,1e-4))[:,None]
nasal=np.exp(-(V[:,0]/22)**4)*np.exp(-((V[:,2]+24)/29)**4)
shift[:,0]*=1-.75*nasal
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
w=(1-smooth(55,79,abs(V[:,0])))*(1-smooth(18,75,V[:,1]))*smooth(-135,-106,V[:,2])*(1-smooth(28,65,V[:,2]))
W=V+shift@M[:2]*w[:,None]
mirror=cKDTree(V).query(V*[-1,1,1])[1]

# Explicit anatomical rows: the margin, lid body, crease and orbital hood.
# Values are depth offsets along the reference-camera ray, continuous to
# adjacent interior folds, so the interior shell cannot pierce the eyelid.
rows=[([1837,2405,1830,1827,1828,1829],.38),
      ([2335,2401,1838,1839,1840],.10),
      ([1565,3180,3177,3174,2512],-1.25),
      ([2355,1555,1964,2331,2330,1728,1718],-.75),
      ([1556,1545,1750,1739,1943,1740,1751],.95),
      ([1547,1752,1741,1730],.50),
      ([1846,2402,1845,1844,2403,1843],.50),
      ([2500,2508,2120,2117,2110,2258],-.25)]
q=[];val=[]
for row,dist in rows:
 for i in row:
  for j in [i,int(mirror[i])]:q.append(Q[j]);val.append(dist)
for sg in [-1,1]:
 center=M[:2]@np.array([sg*31.44,8.2,1.15])
 for rad in [(23,23),(29,30)]:
  for t in np.linspace(0,2*np.pi,36,endpoint=False):q.append(center+[rad[0]*np.cos(t),rad[1]*np.sin(t)]);val.append(0)
q=np.array(q);val=np.array(val);uq,ind=np.unique(np.round(q,4),axis=0,return_index=True)
fold=RBFInterpolator(q[ind],val[ind],kernel='thin_plate_spline',smoothing=1.5)(Q)
fold=np.clip(fold,-1.3,1.1)*(1-smooth(18,70,V[:,1]))
W+=fold[:,None]*fwd
lm=json.loads((OLD/'landmarks.json').read_text())['T22']['landmarks'];eyes=[]
for sg,ix in [(-1,468),(1,473)]:
 c=np.array([sg*31.44174,8.21982157,1.149996]);pq=(np.array(lm[ix][:2])*[1086,-1448]-trans)/scale
 c+=(pq-M[:2]@c)@M[:2];eyes.append(c)
# Make the outer lid rows clear the spherical globe in the actual view.
QW=W@M[:2].T;qq=[];vv=[]
wraprows=[([1819,1813,2404,1818,1814,1815,1816,1804,2406,1810,1811,2408,1812],12.05),([2335,2401,1838,1839,1840,1846,2402,1845,1844,2403,1843],12.45)]
for row,rad in wraprows:
 for i in row:
  for j in [i,int(mirror[i])]:
   c=eyes[0 if W[j,0]<0 else 1];q=W[j]-c;dot=q@fwd;disc=dot*dot-q@q+rad*rad
   dt=np.clip(-dot+np.sqrt(max(0,disc)),-1.5,2.5)
   qq.append(QW[j]);vv.append(dt)
for c in eyes:
 center=M[:2]@c
 for t in np.linspace(0,2*np.pi,48,endpoint=False):qq.append(center+[25*np.cos(t),22*np.sin(t)]);vv.append(0)
qq=np.array(qq);vv=np.array(vv);_,ind=np.unique(np.round(qq,4),axis=0,return_index=True)
clear=RBFInterpolator(qq[ind],vv[ind],kernel='thin_plate_spline',smoothing=1.5)(QW)
dist=np.min([np.sqrt(((QW[:,0]-(M[:2]@c)[0])/25)**2+((QW[:,1]-(M[:2]@c)[1])/22)**2) for c in eyes],axis=0)
clear=np.clip(clear,-1.5,2.5)*(1-smooth(.8,1.15,dist))*(1-smooth(18,70,V[:,1]));W+=clear[:,None]*fwd
out={'vertices':W.tolist(),'baseline':V.tolist(),'eyes':[c.tolist() for c in eyes],'camera':cam,'M':M.tolist(),'projection_delta_max':float(np.linalg.norm(W-V,axis=1).max()),'method':'Reference-plane correspondence correction and explicit eyelid margin/body/crease/orbital-hood rows; source photo is not rendered onto the model.'}
(R/'structure-r10.json').write_text(json.dumps(out))
