"""Local 3DDFA_V2 inference. Existing reference images are read only."""
import sys,pathlib,json,pickle,importlib.util,os
R=pathlib.Path(__file__).resolve().parents[1];ROOT=R.parents[3]
sys.path.insert(0,str(ROOT/'_tools/face-depth-python'))
sys.path.insert(0,str(R.parent/'47_三维头模结构试验_2026-10-12/tools/python'))
REPO=ROOT/'_tools/3DDFA_V2';sys.path.insert(0,str(REPO))
os.environ['MPLCONFIGDIR']=str(R/'depth-r12/mpl-cache')
import numpy as np,cv2,torch
from models.mobilenet_v1 import mobilenet
from utils.functions import crop_img,parse_roi_box_from_landmark
from utils.tddfa_util import similar_transform,_parse_param
torch.set_num_threads(4)
net=mobilenet(num_classes=62,widen_factor=1)
state=torch.load(REPO/'weights/mb1_120x120.pth',map_location='cpu',weights_only=True)['state_dict']
state={k.replace('module.','').replace('fc_param.','fc.'):v for k,v in state.items() if not k.replace('module.','').startswith('fc_lm.')}
net.load_state_dict(state);net.eval()
def read(p):
 with open(REPO/p,'rb') as f:return pickle.load(f,encoding='latin1')
b=read('configs/bfm_noneck_v3.pkl');norm=read('configs/param_mean_std_62d_120x120.pkl');tri=read('configs/tri.pkl').T.astype(int)
u=b['u'].astype('float32');ws=b['w_shp'][:,:40];we=b['w_exp'][:,:10];key=b['keypoints'].astype(int)
land=json.loads((R.parent/'47_三维头模结构试验_2026-10-12/landmarks.json').read_text())
out=R/'depth-r12';out.mkdir(exist_ok=True)
for name,ref in land.items():
 img=cv2.imdecode(np.fromfile(ref['path'],np.uint8),cv2.IMREAD_COLOR)
 lm=np.array(ref['landmarks'])*[ref['width'],ref['height'],ref['width']]
 # Start with the visible face contour plus brows, then use the predicted 68-point crop.
 subset=[234,93,132,58,172,136,150,149,152,378,379,365,397,288,361,323,454,70,63,105,66,107,336,296,334,293,300]
 roi=parse_roi_box_from_landmark(lm[subset,:2].T)
 for iteration in range(2):
  crop=cv2.resize(crop_img(img,roi),(120,120)).astype('float32')
  inp=torch.from_numpy(((crop-127.5)/128).transpose(2,0,1).copy())[None]
  with torch.no_grad():p=net(inp).numpy().ravel()*norm['std']+norm['mean']
  rot,offset,shape,exp=_parse_param(p)
  canonical=(u+ws@shape+we@exp).reshape(3,-1,order='F')
  raw=rot@canonical+offset
  pts=similar_transform(raw.copy(),roi,120)
  kp=(u+ws@shape+we@exp)[key].reshape(3,-1,order='F')
  landmarks=similar_transform(rot@kp+offset,roi,120)
  if iteration==0:roi=parse_roi_box_from_landmark(landmarks[:2])
 np.savez_compressed(out/f'{name}-3ddfa.npz',vertices=pts.T,canonical=canonical.T,triangles=tri,landmarks=landmarks.T,parameters=p,roi=roi)
 canvas=img.copy()
 for i,xy in enumerate(landmarks[:2].T):
  cv2.circle(canvas,tuple(np.round(xy).astype(int)),2,(0,255,120),-1)
  cv2.putText(canvas,str(i),tuple(np.round(xy+[2,0]).astype(int)),cv2.FONT_HERSHEY_SIMPLEX,.25,(0,255,120),1)
 cv2.imencode('.png',canvas)[1].tofile(out/f'{name}-landmarks.png')
 print(name,'vertices',pts.shape,'range',pts.min(axis=1),pts.max(axis=1),'roi',roi,flush=True)
print('LOCAL_DEPTH_DONE',flush=True)
