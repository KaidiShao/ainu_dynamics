import pathlib,json,sys
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'47_三维头模结构试验_2026-10-12/tools/python'))
import numpy as np
a=json.loads((R/'likeness-alignment-r9.json').read_text());d=json.loads((R/'structure-r10.json').read_text());M=np.array(d['M']);cam=d['camera'];rat=cam['scale_pixels_per_model_unit']/(950/305)
t=np.array(cam['translation'])*[1,-1]-[380*rat,475*rat]+np.array([M[0]@[0,25,-2],-M[1]@[0,25,-2]])*cam['scale_pixels_per_model_unit']
B=np.array([[rat,0,t[0]],[0,rat,t[1]],[0,0,1]]);m=a['images']['T22']['matrix'];A=np.array([[m[0],m[2],m[4]],[m[1],m[3],m[5]],[0,0,1]])@B
a['images']={'T22':a['images']['T22'],'R10E':{'url':'/renders/r10e-front-soft.png','width':760,'height':950,'matrix':[A[0,0],A[1,0],A[0,1],A[1,1],A[0,2],A[1,2]]}}
(R/'likeness-alignment-r10-internal.json').write_text(json.dumps(a,ensure_ascii=False))
html=(R/'comparison.html').read_text(encoding='utf8').replace('R9','R10E').replace('/likeness-alignment-r9.json','/likeness-alignment-r10-internal.json')
(R/'internal-r10.html').write_text(html,encoding='utf8')
print('direct camera affine',a['images']['R10E']['matrix'])

