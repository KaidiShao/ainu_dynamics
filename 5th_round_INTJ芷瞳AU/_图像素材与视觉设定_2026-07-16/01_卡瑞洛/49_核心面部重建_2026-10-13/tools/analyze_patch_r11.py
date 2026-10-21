import pathlib,json,sys,collections
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'47_三维头模结构试验_2026-10-12/tools/python'));import numpy as np
D=json.loads((R/'orbits-r11.json').read_text());V=np.array(D['vertices']);F=D['faces'];M=np.array(D['M']);Q=V@M[:2].T;dep=V@M[2]
E=collections.defaultdict(list)
for k,f in enumerate(F):
 for a,b in zip(f,f[1:]+f[:1]):E[tuple(sorted([a,b]))].append((a,b,k))
print('INCONSISTENT',len([x for x in E.values() if len(x)==2 and x[0][:2]==x[1][:2]]))
for p in D['patches']:
 print('EYE',p['side'])
 for i in p['outer']: print(i,*V[i].round(2),*Q[i].round(2),round(dep[i],2))
 for a,b in zip(p['rings'][:-1],p['rings'][1:]):
  bad=[]
  for i in range(len(a)):
   j=(i+1)%len(a);quad=Q[[a[i],b[i],b[j],a[j]]];ar=np.sum(quad[:,0]*np.roll(quad[:,1],-1)-quad[:,1]*np.roll(quad[:,0],-1))/2
   if ar<=0:bad.append((i,round(ar,3)))
  print('negativeareas',bad)
