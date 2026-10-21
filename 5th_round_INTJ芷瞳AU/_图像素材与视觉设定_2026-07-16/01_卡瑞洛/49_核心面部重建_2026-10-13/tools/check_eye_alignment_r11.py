import pathlib,json,sys
R=pathlib.Path(__file__).resolve().parents[1];O=R.parent/'47_三维头模结构试验_2026-10-12';sys.path.insert(0,str(O/'tools/python'));import numpy as np
D=json.loads((R/'face-r11k.json').read_text());S=json.loads((R/'structure-r10.json').read_text());M=np.array(D['M']);cam=S['camera'];eyes=np.array(D['eyes']);lm=np.array(json.loads((O/'landmarks.json').read_text())['T22']['landmarks']);q=(lm[:,:2]*[1086,-1448]-cam['translation'])/cam['scale_pixels_per_model_unit']
for i,(cc,ids) in enumerate(zip(eyes,[[468,159,145,33,133],[473,386,374,362,263]])):
 center=cc@M[:2].T;print('eye',i,'worldQ',center,'ref iris',q[ids[0]],'pixel error',(center-q[ids[0]])*cam['scale_pixels_per_model_unit']);print('rim ref',[(x,(q[x]-center).round(2).tolist(),(lm[x,:2]*[1086,1448]).round(1).tolist()) for x in ids[1:]])
