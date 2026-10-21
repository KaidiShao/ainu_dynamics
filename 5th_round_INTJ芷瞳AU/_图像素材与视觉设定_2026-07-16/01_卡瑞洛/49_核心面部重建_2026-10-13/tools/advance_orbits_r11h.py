import pathlib,json,sys
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'47_三维头模结构试验_2026-10-12/tools/python'));import numpy as np
D=json.loads((R/'face-r11g.json').read_text());V=np.array(D['vertices']);M=np.array(D['M']);fw=M[2]
svals=[0,.025,.065,.13,.22,.34,.49,.66,.83,1.]
for p in D['patches']:
 for s,ids in zip(svals,p['rings']):
  blend=1-s*s*(3-2*s);V[ids]+=fw*4.0*blend
 used=set(j for f in p['faces'] for j in f);rings=set(j for rr in p['rings'] for j in rr)
 for i in used-rings:V[i]+=fw*4.0
D['vertices']=V.tolist();D['eyes']=(np.array(D['eyes'])+fw*4.0).tolist();D['eye_advance']=4.0
D['method']+=' R11H anatomical globe advance 4 units, same iris projection, continuous lid support taper; no eye opening narrowing.'
(R/'face-r11h.json').write_text(json.dumps(D))
