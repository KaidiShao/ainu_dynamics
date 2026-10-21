import pathlib,json,sys,collections,math
R=pathlib.Path(__file__).resolve().parents[1];O=R.parent/'47_三维头模结构试验_2026-10-12';P=R.parent/'48_Blender头模精修_2026-10-13';sys.path.insert(0,str(O/'tools/python'))
import numpy as np
from scipy.interpolate import PchipInterpolator,RBFInterpolator
D=json.loads((R/'mouth-pre-r11.json').read_text());V=np.array(D['vertices']);F=D['faces'];uv={k:np.array(v) for k,v in D['uv'].items()};orbit=json.loads((R/'orbits-r11.json').read_text())
s=json.loads((R/'structure-r10.json').read_text());M=np.array(s['M']);cam=s['camera'];fw=M[2];Q=V@M[:2].T
lm=np.array(json.loads((O/'landmarks.json').read_text())['T22']['landmarks'])[:468,:2];lq=(lm*[1086,-1448]-cam['translation'])/cam['scale_pixels_per_model_unit']
f03=np.array(json.loads((P/'base-landmarks.json').read_text())['F03']['landmarks'])[:468,:2]*[1,-1]+[0,1];uvf=RBFInterpolator(lq,f03,kernel='thin_plate_spline',smoothing=.6)
adj={int(k):v for k,v in D['boundary_adj'].items()};root=min(adj);loop=[root];prev=None;cur=root
while True:
 nxt=next(n for n in adj[cur] if n!=prev)
 if nxt==root:break
 loop.append(nxt);prev,cur=cur,nxt
pts=Q[loop];area=np.sum(pts[:,0]*np.roll(pts[:,1],-1)-pts[:,1]*np.roll(pts[:,0],-1))
if area<0:loop=loop[::-1];pts=Q[loop]
center=(lq[61]+lq[291])/2
theta=np.unwrap(np.arctan2(pts[:,1]-center[1],pts[:,0]-center[0]))
# Retain the monotone angle ordering while relaxing very small reversals of the outer border.
for i in range(1,len(theta)):theta[i]=max(theta[i],theta[i-1]+.025)
upper=np.sin(theta)>0
left=min(lq[61,0],lq[291,0]);right=max(lq[61,0],lq[291,0]);xx=(left+right)/2+(right-left)/2*np.cos(theta)
def curve(ids):
 p=lq[ids];p=p[np.argsort(p[:,0])];return PchipInterpolator(p[:,0],p[:,1],extrapolate=True)
ou=curve([61,185,40,39,37,0,267,269,270,409,291]);ol=curve([61,146,91,181,84,17,314,405,321,375,291])
su=curve([78,191,80,81,82,13,312,311,310,415,308]);sl=curve([78,95,88,178,87,14,317,402,318,324,308])
seam=(su(np.clip(xx,lq[78,0],lq[308,0]))+sl(np.clip(xx,lq[78,0],lq[308,0])))/2
# All lip curves end at the same canthus, without a dark broad mouth opening.
taper=np.maximum(0,1-((xx-(left+right)/2)/((right-left)/2))**2)
corner_line=np.interp(xx,[left,right],[lq[61,1],lq[291,1]])
seam=seam*taper**.3+corner_line*(1-taper**.3)
iq=np.column_stack([xx,seam+np.where(upper,.12,-.12)*taper])
border=np.column_stack([xx,np.where(upper,ou(xx),ol(xx))])
ringIds=[];lipX=xx-(left+right)/2
def add_ring(coords,depth):
 global V,Q,uv
 ids=[]
 for q,d in zip(coords,depth):
  p=q@M[:2]+d*fw;ids.append(len(V));V=np.vstack([V,p]);Q=np.vstack([Q,q])
  for name in uv:
   val=((q*cam['scale_pixels_per_model_unit']+cam['translation'])/[1086,1448])+[0,1] if name=='T22_core_reference' else uvf(q[None,:])[0]
   uv[name]=np.vstack([uv[name],val])
 return ids
def depth_y(q,y):return (y-(q@M[:2])[:,1])/fw[1]
for t in [0,.08,.23,.45,.68,.86,1.]:
 q=(1-t)*iq+t*border
 yborder=np.where(upper,-29.5,-27.8)+.026*lipX**2
 y=(1-t)*(-28.7+.026*lipX**2)+t*yborder
 y-=np.where(upper,1.55,2.3)*np.sin(np.pi*t)*taper
 ringIds.append(add_ring(q,depth_y(q,y)))
bd=depth_y(border,np.where(upper,-29.5,-27.8)+.026*lipX**2);outerD=V[loop]@fw
for t in [.10,.24,.43,.64,.83,1.]:
 if t==1:ringIds.append(loop);continue
 q=(1-t)*border+t*pts;blend=t*t*(3-2*t);dep=(1-blend)*bd+blend*outerD
 # Moderate philtrum groove and labiomental fold, without isolated point dimples.
 dep-=np.where(upper,.3,.65)*np.exp(-((t-.23)/.14)**2)*np.exp(-(lipX/14)**4)
 ringIds.append(add_ring(q,dep))
new=[]
for a,b in zip(ringIds[:-1],ringIds[1:]):
 for i in range(len(loop)):
  j=(i+1)%len(loop);new.append([a[i],b[i],b[j],a[j]])
back=add_ring(iq,depth_y(iq,-28.7+.026*lipX**2)-.9)
for i in range(len(loop)):
 j=(i+1)%len(loop);new.append([ringIds[0][i],back[i],back[j],ringIds[0][j]])
out={**orbit,'vertices':V.tolist(),'faces':F+new,'uv':{k:v.tolist() for k,v in uv.items()},'mouth':{'outer':loop,'rings':ringIds,'inner':back},'method':orbit['method']+' Oral shell removed; continuous upper/lower lips built from T22 lip outlines, subtle closed seam and stable lip-chin transition.'}
(R/'face-r11d.json').write_text(json.dumps(out));print('R11D',len(V),len(F+new),'mouth boundary',len(loop),'reference width',right-left)
