import pathlib,sys,json,math
R=pathlib.Path(__file__).resolve().parents[1];OLD=R.parent/'47_三维头模结构试验_2026-10-12'
sys.path.insert(0,str(OLD/'tools/python'))
import numpy as np,mediapipe as mp
from PIL import Image
D=json.loads((OLD/'landmarks.json').read_text(encoding='utf8'))
options=mp.tasks.vision.FaceLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_buffer=(OLD/'assets/face_landmarker.task').read_bytes()),output_facial_transformation_matrixes=True,min_face_detection_confidence=.15,min_face_presence_confidence=.15)
with mp.tasks.vision.FaceLandmarker.create_from_options(options) as det:
 a=np.asarray(Image.open(R/'renders/core-r7-front.png').convert('RGB'))
 q=det.detect(mp.Image(image_format=mp.ImageFormat.SRGB,data=a))
 if not q.face_landmarks:raise RuntimeError('No landmarks detected')
 D['R7']={'landmarks':[[v.x,v.y,v.z] for v in q.face_landmarks[0]],'width':a.shape[1],'height':a.shape[0]}
out={'status':'R7 reconstructed core; likeness not yet established; image alignment is diagnostic only, not a 3D reconstruction or identity score.','images':{}}
groups={
 'left_eye':[33,160,159,158,133,153,145,144,33],
 'right_eye':[263,387,386,385,362,380,374,373,263],
 'left_brow':[70,63,105,66,107],
 'right_brow':[300,293,334,296,336],
 'nose':[168,6,197,195,5,4,1,2],
 'nose_base':[98,97,2,326,327],
 'lips':[61,40,37,0,267,270,291,321,314,17,84,91,61],
 'jaw':[234,93,132,58,172,136,150,149,176,148,152,377,400,378,379,365,397,288,361,323,454]
}
metrics={}
for key,url in [('T22','/refs/front.png'),('R7','/renders/core-r7-front.png')]:
 d=D[key];p=np.array(d['landmarks'])*[d['width'],d['height'],d['width']]
 e1=p[[33,133],:2].mean(0);e2=p[[263,362],:2].mean(0);mid=(e1+e2)*.5
 distance=np.linalg.norm(e2-e1);angle=math.atan2(e2[1]-e1[1],e2[0]-e1[0])
 c=math.cos(-angle);s=math.sin(-angle);rotation=np.array([[c,-s],[s,c]])
 normalized=((p[:,:2]-mid)@rotation.T)/distance
 scale=130/distance
 matrix=[scale*c,scale*s,-scale*s,scale*c,256-scale*(c*mid[0]-s*mid[1]),205-scale*(s*mid[0]+c*mid[1])]
 out['images'][key]={'url':url,'width':d['width'],'height':d['height'],'matrix':matrix,
  'points':(normalized*130+[256,205]).tolist(),'eye_midpoint':mid.tolist(),'eye_distance':float(distance),'roll_degrees':float(math.degrees(angle))}
 lm=normalized
 def width(i,j):return float(np.linalg.norm(lm[i]-lm[j]))
 metrics[key]={'eye_to_chin':float(lm[152,1]),'eye_to_nose_base':float(lm[2,1]),'eye_to_mouth':float(lm[13,1]),
  'mouth_width':width(61,291),'jaw_width':width(172,397),'nose_base_width':width(98,327),
  'left_eye_width':width(33,133),'right_eye_width':width(263,362),
  'left_eye_height':width(159,145),'right_eye_height':width(386,374)}
out['groups']=groups;out['metrics_eye_distance_normalized']=metrics
out['limitations']=['Landmark detector estimates may follow texture rather than anatomy.','Matching roll and eye distance does not match yaw, pitch, lens or expression.','Shadow contours are not bone boundaries.']
(R/'likeness-alignment-r7.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(metrics,ensure_ascii=False,indent=2))





