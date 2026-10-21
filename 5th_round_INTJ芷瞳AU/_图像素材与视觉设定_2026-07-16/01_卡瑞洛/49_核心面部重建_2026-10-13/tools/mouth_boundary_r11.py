import pathlib,json,collections,sys
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'47_三维头模结构试验_2026-10-12/tools/python'));import numpy as np
D=json.loads((R/'orbits-r11.json').read_text());V=np.array(D['vertices']);F=D['faces'];E=collections.Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in F for i in range(len(f)))
for rx,rz,zz in [(32,27,-68),(34,30,-69),(36,33,-68)]:
 mask=(V[:,0]/rx)**2+((V[:,2]-zz)/rz)**2<1;mask&=(V[:,2]<-47)&(V[:,1]<60)
 drop={i for i,f in enumerate(F) if all(mask[j] for j in f)}
 ee=collections.Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for k,f in enumerate(F) if k not in drop for i in range(len(f)))
 edges=[p for p,n in ee.items() if n==1 and E[p]>1];adj=collections.defaultdict(list)
 for a,b in edges:adj[a].append(b);adj[b].append(a)
 seen=set();loops=[]
 for i in adj:
  if i in seen:continue
  todo=[i];ids=set()
  while todo:
   x=todo.pop()
   if x in ids:continue
   ids.add(x);todo+=adj[x]
  seen|=ids;loops.append(ids)
 print(rx,rz,zz,len(drop),[(len(x),V[list(x)].min(0).round(1).tolist(),V[list(x)].max(0).round(1).tolist()) for x in loops],collections.Counter(len(x) for x in adj.values()))
