import pathlib,json,sys
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'47_三维头模结构试验_2026-10-12/tools/python'))
import numpy as np
from PIL import Image,ImageDraw,ImageFont
a=json.loads((R/'likeness-alignment-r9.json').read_text());print(a.keys());print(a.get('canvas'))
ref=R.parent/'37_眼色局部统一_2026-10-11/MC_STATE_T22_T19正面_浅蓝灰虹膜校准_v22.png'
version=sys.argv[1] if len(sys.argv)>1 else 'r11f'
m=a['images']['T22']['matrix'];A=np.array([[m[0],m[2],m[4]],[m[1],m[3],m[5]],[0,0,1]])
B=np.array([[.6626401581716788,-.042176406219616186,28.084887644000133],[.042176406219616186,.6626401581716788,-131.72373115436818],[0,0,1]])
im=Image.new('RGB',(1440,650),(28,28,28));draw=ImageDraw.Draw(im)
for k,(label,path,T) in enumerate([('T22 reference',ref,A),(version+' surface',R/f'renders/{version}-front.png',B),(version+' geometry',R/f'renders/{version}-front-neutral.png',B)]):
 inv=np.linalg.inv(T);src=Image.open(path).convert('RGB');out=src.transform((480,610),Image.Transform.AFFINE,tuple(inv[:2].ravel()),Image.Resampling.BICUBIC);im.paste(out,(k*480,35));draw.text((k*480+12,10),label,fill='white')
im.save(R/f'renders/{version}-compare.png')
