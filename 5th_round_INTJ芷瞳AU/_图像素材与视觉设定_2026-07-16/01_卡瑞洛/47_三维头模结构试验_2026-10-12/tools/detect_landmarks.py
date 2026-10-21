import sys,pathlib,json,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/python'))
import mediapipe as mp
from PIL import Image
refs={
 'T22':ROOT.parent/'37_眼色局部统一_2026-10-11/MC_STATE_T22_T19正面_浅蓝灰虹膜校准_v22.png',
 'P14':ROOT.parent/'29_正侧下巴衔接统一_2026-10-10/MC_ANGLE_P14_浅蓝灰原侧光_唇颏过渡轻统一_v14.png'}
options=mp.tasks.vision.FaceLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_buffer=(ROOT/'assets/face_landmarker.task').read_bytes()),output_facial_transformation_matrixes=True,min_face_detection_confidence=.3,min_face_presence_confidence=.3)
out={}
with mp.tasks.vision.FaceLandmarker.create_from_options(options) as detector:
 for key,path in refs.items():
  a=np.asarray(Image.open(path).convert('RGB'))
  r=detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=a))
  out[key]={'path':str(path),'width':a.shape[1],'height':a.shape[0],'landmarks':[[v.x,v.y,v.z] for v in r.face_landmarks[0]] if r.face_landmarks else [],'transform':r.facial_transformation_matrixes[0].tolist() if r.facial_transformation_matrixes else []}
  print(key,'landmarks',len(out[key]['landmarks']),flush=True)
(ROOT/'landmarks.json').write_text(json.dumps(out,indent=2),encoding='utf8')
