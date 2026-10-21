import pathlib,json,sys
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'47_三维头模结构试验_2026-10-12/tools/python'));import numpy as np
D=json.loads((R/'face-r11h.json').read_text());V=np.array(D['vertices']);used=set(j for f in D['faces'] for j in f)
for z in [15,5,-5,-15,-25,-32,-38,-44,-49]:
 ids=[i for i,p in enumerate(V) if i in used and abs(p[0])<15 and abs(p[2]-z)<3 and p[1]<0];print(z,[(i,V[i].round(2).tolist()) for i in sorted(ids,key=lambda k:V[k,1])[:9]])
for p in D['patches']:
 r=p['rings'][0];print('rim',p['side'],[(i,V[i].round(1).tolist()) for i in r])
