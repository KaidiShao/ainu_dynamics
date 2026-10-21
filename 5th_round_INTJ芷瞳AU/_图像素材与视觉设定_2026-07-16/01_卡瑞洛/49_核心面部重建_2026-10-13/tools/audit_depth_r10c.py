import pathlib,json,sys
R=pathlib.Path(__file__).resolve().parents[1];OLD=R.parent/'47_三维头模结构试验_2026-10-12'
sys.path.insert(0,str(OLD/'tools/python'))
import numpy as np
from scipy.interpolate import RBFInterpolator
D=json.loads((R/'r10c-inspection.json').read_text());V=np.array(D['vertices']);F=json.loads((OLD/'head-fit.json').read_text());L=json.loads((OLD/'landmarks.json').read_text())
def cam(key):
 c=F['metrics'][key];r=np.array(c['rotation']);M=np.column_stack((r[:,0],-r[:,2],r[:,1]));return c,M
c,M=cam('T22');p,PM=cam('P14');direction=PM[:2]@M[2];corr=[]
# Corresponding non-silhouette landmarks only.
groups={'nose':[168,6,197,195,5,4,1,2,98,97,326,327,19,94],'lips':[0,13,14,17,37,39,40,61,84,87,267,269,270,291,314,317],'chin':[18,200,199,175],'eyes':[33,133,159,145,263,362,386,374]}
for name,ids in groups.items():
 print(name)
 for ix in ids:
  h=D['landmarks'][ix]
  if not h['hit']:continue
  v=np.array(h['point']);target=(np.array(L['P14']['landmarks'][ix][:2])*[1086,-1448]-p['translation'])/p['scale_pixels_per_model_unit']
  delta=target-PM[:2]@v;amount=delta@direction/(direction@direction)
  residual=np.linalg.norm(delta-direction*amount)
  print(ix, np.round(v,1), 'depth',round(amount,2),'res',round(residual,2))
  corr.append({'index':ix,'group':name,'point':v.tolist(),'depth':float(amount),'residual':float(residual)})
(R/'p14-depth-audit-r10c.json').write_text(json.dumps(corr,indent=2))
