import pathlib,sys,json,os
R=pathlib.Path(__file__).resolve().parents[1];OLD=R.parent/'47_三维头模结构试验_2026-10-12';sys.path.insert(0,str(OLD/'tools/python'))
import numpy as np,mediapipe as mp
from PIL import Image
D=json.loads((OLD/'landmarks.json').read_text())
options=mp.tasks.vision.FaceLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_buffer=(OLD/'assets/face_landmarker.task').read_bytes()),output_facial_transformation_matrixes=True,min_face_detection_confidence=.15,min_face_presence_confidence=.15)
with mp.tasks.vision.FaceLandmarker.create_from_options(options) as det:
 for name in ['refined-v6-front']:
  a=np.asarray(Image.open(R/f'renders/{name}.png').convert('RGB'));q=det.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=a))
  D[name]={'landmarks':[[v.x,v.y,v.z] for v in q.face_landmarks[0]],'width':a.shape[1],'height':a.shape[0]}
out={}
for k in ['T22','refined-v6-front']:
 d=D[k];p=np.array(d['landmarks'])*[d['width'],d['height'],d['width']]
 eye1=p[[33,133],:2].mean(0);eye2=p[[263,362],:2].mean(0);eyes=(eye1+eye2)/2
 scale=np.linalg.norm(eye2-eye1)
 out[k]={'eye_scale':float(scale),'eye_to_chin':float((p[152,1]-eyes[1])/scale),'nose_length':float((p[2,1]-eyes[1])/scale),'mouth_width':float(np.linalg.norm(p[61,:2]-p[291,:2])/scale),'eye_aperture':float((p[145,1]-p[159,1])/scale),'jaw_width':float(np.linalg.norm(p[172,:2]-p[397,:2])/scale)}
 print(k,out[k])
(R/'candidate-landmarks.json').write_text(json.dumps(D),encoding='utf8')
(R/'candidate-ratios.json').write_text(json.dumps(out,indent=2),encoding='utf8')

