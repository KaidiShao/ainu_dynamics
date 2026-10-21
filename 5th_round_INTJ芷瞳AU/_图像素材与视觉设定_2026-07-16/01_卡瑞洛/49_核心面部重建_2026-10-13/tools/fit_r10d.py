import pathlib,sys,json
R=pathlib.Path(__file__).resolve().parents[1];O=R.parent/'47_三维头模结构试验_2026-10-12';sys.path.insert(0,str(O/'tools/python'))
import numpy as np
from scipy.interpolate import RBFInterpolator,PchipInterpolator
from scipy.spatial import cKDTree
D=json.loads((R/'r10c-inspection.json').read_text());V=np.array(D['vertices']);F=np.array(json.loads((R/'structure-r10.json').read_text())['M']);W=V.copy();mirror=cKDTree(V).query(V*[-1,1,1])[1]
# Sculpt the visible lid surfaces, not the internal orbital cap.
controls=[];deltas=[]
rows=[
([1813,2404,1818,1814,1815],[-.00,.00,-.55]),
([2335,2401,1838,1839,1840],[.0,-.15,-.30]),
([1869,2334,2103,2514,2333,2331,2513,2330],[.0,.40,.00]),
([2028,2263,2111,2264,1942,1943,1911,2328,2327],[.0,-.40,-.55]),
([1804,2406,1810,1811,2408,1812],[.0,-.1,.20]),
([1846,2402,1845,1844,2403,1843],[.0,-.50,.1]),
([2500,2508,2120,2117,2110,2258],[.0,.18,.0])]
for ids,delta in rows:
 for i in ids:
  for j in [i,int(mirror[i])]:controls.append((F[:2]@V[j]).tolist());deltas.append(delta)
Q=V@F[:2].T
for c in json.loads((R/'r10c-manifest.json').read_text())['eyes']:
 q=F[:2]@c
 for a in np.linspace(0,2*np.pi,36,endpoint=False):controls.append((q+[26*np.cos(a),27*np.sin(a)]).tolist());deltas.append([0,0,0])
controls=np.array(controls);deltas=np.array(deltas);_,ix=np.unique(np.round(controls,4),axis=0,return_index=True)
delta=RBFInterpolator(controls[ix],deltas[ix],smoothing=2.5)(Q);delta=np.clip(delta,[-.1,-.65,-.65],[.1,.5,.3]);fade=np.clip((36-V[:,1])/25,0,1);delta*=fade[:,None];W+=delta
# Remove the tiny central lip/underlip ridges while retaining distinct lip volumes.
z=np.array([-100,-88,-83,-79,-76,-73,-70,-67,-65,-64,-62,-60,-57,-55,-52,-48,-44])
y=np.array([-25.2,-25.6,-25.5,-26.0,-27.3,-28.8,-29.5,-28.8,-27.5,-29.0,-30.0,-30.6,-30.5,-29.8,-28.0,-26.2,-26.0])
profile=PchipInterpolator(z,y)
for i,(x,yy,zz) in enumerate(V):
 if abs(x)>25 or not(-86<zz<-49) or yy>-11:continue
 target=float(profile(zz))+.028*x*x
 # Do not remap the hidden oral cavity: only the outer skin and lip surface.
 if yy>target+3.6:continue
 weight=np.exp(-(x/21)**6)*min(1,(-49-zz)/4)*min(1,(zz+86)/5)
 W[i,1]+=float(np.clip(target-yy,-1.65,1.65))*weight*.78
# A continuous supporting chin plane, and a firmer mandibular turning plane.
a=abs(V[:,0]);front=np.clip((45-V[:,1])/25,0,1)
wt=np.exp(-(V[:,0]/21)**4-((V[:,2]+98)/16)**4)*front
W[:,1]-=.65*wt
jaw=np.exp(-((a-50)/11)**4-((V[:,1]-24)/21)**4-((V[:,2]+83)/13)**4)
W[:,0]+=np.sign(V[:,0])*.7*jaw
# Slightly narrower nasal tip shoulders, leaving the high bridge intact.
tip=np.exp(-((a-10)/6)**4-((V[:,2]+34)/8)**4)*np.clip((-5-V[:,1])/20,0,1)
W[:,0]-=np.sign(V[:,0])*.45*tip
(R/'structure-r10d.json').write_text(json.dumps({'baseline':V.tolist(),'vertices':W.tolist(),'notes':['Visible lid planes','Bounded outer lip smoothing','Chin support and mandibular turn','Nasal tip shoulders; bridge preserved']}))
print('R10D max proposed',np.linalg.norm(W-V,axis=1).max())
