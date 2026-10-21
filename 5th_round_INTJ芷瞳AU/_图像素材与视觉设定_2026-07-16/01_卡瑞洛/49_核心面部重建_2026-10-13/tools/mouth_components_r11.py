import pathlib,json,collections,sys
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'47_三维头模结构试验_2026-10-12/tools/python'));import numpy as np
D=json.loads((R/'orbits-r11.json').read_text());V=np.array(D['vertices']);F=D['faces']
mask=(V[:,0]/32)**2+((V[:,2]+68)/27)**2<1;mask&=(V[:,2]<-47)&(V[:,1]<60)
keep=[f for f in F if not all(mask[j] for j in f)];adj=collections.defaultdict(set)
for f in keep:
 for i in f:adj[i].update(f)
seen=set();comps=[]
for i in adj:
 if i in seen:continue
 stack=[i];ids=set()
 while stack:
  x=stack.pop()
  if x in ids:continue
  ids.add(x);stack+=list(adj[x]-ids)
 seen|=ids;comps.append(ids)
print([(len(c),V[list(c)].min(0).round(1).tolist(),V[list(c)].max(0).round(1).tolist()) for c in comps])
big=max(comps,key=len);keep=[f for f in keep if f[0] in big]
e=collections.Counter(tuple(sorted((f[i],f[(i+1)%len(f)]))) for f in keep for i in range(len(f)))
edges=[p for p,n in e.items() if n==1 and V[list(p),2].max()<-40];ad=collections.defaultdict(list)
for a,b in edges:ad[a].append(b);ad[b].append(a)
print('oralboundary',len(ad),collections.Counter(map(len,ad.values())))
(R/'mouth-pre-r11.json').write_text(json.dumps({'vertices':D['vertices'],'faces':keep,'uv':D['uv'],'boundary_adj':ad}))
