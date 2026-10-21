import sys,pathlib,json
R=pathlib.Path(__file__).resolve().parents[1];OLD=R.parent/'47_三维头模结构试验_2026-10-12'
sys.path.insert(0,str(OLD/'tools/python'))
import numpy as np,mediapipe as mp
from PIL import Image
options=mp.tasks.vision.FaceLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_buffer=(OLD/'assets/face_landmarker.task').read_bytes()),output_facial_transformation_matrixes=True,min_face_detection_confidence=.15,min_face_presence_confidence=.15)
out={}
refs={'BASE':R/'renders/base-front.png','F03':R.parent/'28_认可正面下巴轻校准_2026-10-09/MC_FRONT_F03_浅蓝灰柔光_下巴凹痕轻校准_v1.png'}
with mp.tasks.vision.FaceLandmarker.create_from_options(options) as det:
 for k,p in refs.items():
  a=np.asarray(Image.open(p).convert('RGB'))
  q=det.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=a))
  out[k]={'path':str(p),'width':a.shape[1],'height':a.shape[0],'landmarks':[[v.x,v.y,v.z] for v in q.face_landmarks[0]] if q.face_landmarks else [],'transform':q.facial_transformation_matrixes[0].tolist() if q.facial_transformation_matrixes else []}
  print(k,len(out[k]['landmarks']))
(R/'base-landmarks.json').write_text(json.dumps(out),encoding='utf8')

