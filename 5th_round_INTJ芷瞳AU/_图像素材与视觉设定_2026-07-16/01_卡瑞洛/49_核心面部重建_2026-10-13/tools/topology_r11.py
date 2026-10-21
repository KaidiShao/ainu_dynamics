import pathlib,json,sys,collections
R=pathlib.Path(__file__).resolve().parents[1];O=R.parent/'47_三维头模结构试验_2026-10-12';sys.path.insert(0,str(O/'tools/python'))
import numpy as np
d=json.loads((R/'r10c-inspection.json').read_text());V=np.array(d['vertices']);F=d['faces']
edges=collections.Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in F for i in range(len(f)))
print('topology',len(V),len(F),'boundary edges',sum(v==1 for v in edges.values()),'nonmanifold',sum(v>2 for v in edges.values()))
for limits in [(25,24,32),(24,20,35),(25,26,42),(23,21,60)]:
 rx,rz,ymax=limits
 inside=(((V[:,0]-32)/rx)**2+((V[:,2]-2)/rz)**2<1)&(V[:,1]<ymax)
 drop=[k for k,f in enumerate(F) if all(inside[i] for i in f)]
 e=collections.Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for k,f in enumerate(F) if k not in set(drop) for i in range(len(f)))
 boundary=[p for p,n in e.items() if n==1 and edges[p]>1]
 adj=collections.defaultdict(list)
 for a,b in boundary:adj[a].append(b);adj[b].append(a)
 seen=set();loops=[]
 for i in adj:
  if i in seen:continue
  stack=[i];ids=set()
  while stack:
   j=stack.pop()
   if j in ids:continue
   ids.add(j);stack+=adj[j]
  seen.update(ids);loops.append(ids)
 print(limits,'faces dropped',len(drop),'boundary components',[(len(ids),V[list(ids)].min(0).round(1).tolist(),V[list(ids)].max(0).round(1).tolist()) for ids in loops],'degrees',collections.Counter(len(v) for v in adj.values()))
