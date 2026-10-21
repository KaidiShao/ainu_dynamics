import pathlib,json,sys
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'47_三维头模结构试验_2026-10-12/tools/python'));import numpy as np
D=json.loads((R/'face-r11f.json').read_text());V=np.array(D['vertices']);W=V.copy();M=np.array(D['M']);fw=M[2];up=M[1];right=M[0];Q=V@M[:2].T
svals=[0,.025,.065,.13,.22,.34,.49,.66,.83,1.]
for pi,p in enumerate(D['patches']):
 c=np.array(D['eyes'][pi]);center=c@M[:2].T
 for k,ids in enumerate(p['rings']):
  s=svals[k];ang=np.arctan2(Q[ids,1]-center[1],Q[ids,0]-center[0]);upper=np.clip(np.sin(ang)*1.5,0,1);lower=np.clip(-np.sin(ang)*1.5,0,1)
  dep=upper*(.55*np.exp(-((s-.12)/.075)**2)-1.25*np.exp(-((s-.4)/.12)**2)+.4*np.exp(-((s-.73)/.16)**2))
  dep+=lower*(.55*np.exp(-((s-.12)/.095)**2)-.22*np.exp(-((s-.4)/.15)**2))
  W[ids]+=dep[:,None]*fw
# Relax the lifted mouth corners and reduce the lower lip wings.
mouth=D['mouth'];rim=np.array(mouth['rings'][0]);mc=Q[rim].mean(0);half=np.max(abs(Q[rim,0]-mc[0]))
for k,ids in enumerate(mouth['rings']):
 x=(Q[ids,0]-mc[0])/half;lower=Q[ids,1]<mc[1];isLip=k<=6;fade=max(0,1-(k-6)/6) if k>6 else 1
 W[ids]-=up*(.85*np.abs(x)**3*fade)[:,None]
 if isLip:
  body=np.sin(np.pi*min(1,k/6))
  W[ids]-=fw*(lower*(.42+.85*np.abs(x)**1.5)*body)[:,None]
  # Two small upper-lip lobes give a shallow Cupid bow instead of one large pad.
  W[ids]+=fw*((~lower)*.35*np.exp(-((abs(x)-.22)/.2)**2)*body)[:,None]
# Refine the tip shoulders and domes while retaining the narrow high bridge.
x,y,z=V.T;front=np.clip((-6-y)/14,0,1)
tip=np.exp(-(x/9)**4-((z+34)/8)**4)*front
W[:,2]+=.95*tip;W[:,1]-=.35*tip
shoulder=np.exp(-((abs(x)-7.8)/4.6)**4-((z+34)/6.8)**4)*front
W[:,0]+=np.sign(x)*.62*shoulder
# Define the alar crease as a small, localized break between tip and wing.
crease=np.exp(-((abs(x)-11.8)/2.2)**2-((z+34)/5.8)**2)*front
W[:,1]+=.65*crease
# A broader terminal chin plane without widening the mandibular body.
chin=np.exp(-(x/23)**6-((z+100)/13)**4)*np.clip((5-y)/15,0,1)
W[:,0]+=1.35*np.tanh(x/9)*chin
W[:,2]+=.55*np.exp(-(x/13)**4-((z+108)/6)**2)*np.clip((5-y)/15,0,1)
D['vertices']=W.tolist();D['refinement_G']={'max_displacement':float(np.linalg.norm(W-V,axis=1).max()),'notes':['Upper-lid crease, hood and lower-lid roll','Quiet mouth corners and smaller lower-lip wings','Rounded narrow nasal tip with alar separation; bridge retained','Subtly broader chin termination']}
(R/'face-r11g.json').write_text(json.dumps(D));print(D['refinement_G'])
