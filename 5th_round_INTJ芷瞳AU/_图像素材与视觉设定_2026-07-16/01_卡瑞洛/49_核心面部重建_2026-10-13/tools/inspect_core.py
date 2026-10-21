import json,pathlib,sys
R=pathlib.Path(__file__).resolve().parents[1];P=R.parent/'48_Blender头模精修_2026-10-13'
sys.path.insert(0,str(R.parent/'47_三维头模结构试验_2026-10-12/tools/python'))
import numpy as np
B=json.loads((P/'base-geometry.json').read_text());d=json.loads((R/'core-fit-r2.json').read_text());V=np.array(B['vertices'])*63/71.7532;W=np.array(d['vertices']);S=np.array(d['source_landmarks']);T=np.array(d['target_landmarks'])
ix=np.where((abs(V[:,0])<25)&(V[:,2]<-58)&(V[:,2]>-85))[0]
print('Mouth extreme output vertices:')
for i in ix[np.argsort(W[ix,1])[:18]]:print(i, np.round(V[i],2), np.round(W[i],2))
print('Mouth control displacements:')
ix=np.where((abs(S[:,0])<30)&(S[:,2]<-55)&(S[:,2]>-86))[0]
for i in ix:print(i,np.round(S[i],2),np.round(T[i]-S[i],2))
