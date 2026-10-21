import json,pathlib,struct,hashlib
import numpy as np
R=pathlib.Path(__file__).resolve().parents[1]
meshes=json.loads((R/'scene-meshes.json').read_text())
g={'asset':{'version':'2.0','generator':'Carrillo head blockout v1: constrained MediaPipe landmark fit + explicitly estimated cranial/hair/ear meshes'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'materials':[],'buffers':[{'byteLength':0}],'bufferViews':[],'accessors':[]}
buf=bytearray()
def acc(a,kind,component,target):
 a=np.ascontiguousarray(a);offset=len(buf);buf.extend(a.tobytes());buf.extend(b'\0'*((-len(buf))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':a.nbytes,'target':target});d={'bufferView':vi,'componentType':component,'count':len(a),'type':kind}
 if kind=='VEC3':d.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
 g['accessors'].append(d);return len(g['accessors'])-1
for m in meshes:
 p=np.array(m['positions'],dtype='<f4').reshape(-1,3);n=np.array(m['normals'],dtype='<f4').reshape(-1,3);f=np.array(m['indices'],dtype='<u4')
 assert np.isfinite(p).all() and np.isfinite(n).all() and f.max()<len(p)
 ma=len(g['materials']);g['materials'].append({'name':m['name']+'_material','doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':m['color']+[1],'metallicFactor':0,'roughnessFactor':m['roughness']}})
 g['meshes'].append({'name':m['name'],'primitives':[{'attributes':{'POSITION':acc(p,'VEC3',5126,34962),'NORMAL':acc(n,'VEC3',5126,34962)},'indices':acc(f,'SCALAR',5125,34963),'material':ma}]})
 g['nodes'].append({'name':m['name'],'mesh':len(g['meshes'])-1});g['scenes'][0]['nodes'].append(len(g['nodes'])-1)
g['buffers'][0]['byteLength']=len(buf)
j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
out=struct.pack('<4sII',b'glTF',2,12+8+len(j)+8+len(buf))+struct.pack('<I4s',len(j),b'JSON')+j+struct.pack('<I4s',len(buf),b'BIN\0')+buf
(R/'carrillo-head-blockout-v1.glb').write_bytes(out)
report={'meshes':len(meshes),'vertices':sum(len(m['positions'])//3 for m in meshes),'triangles':sum(len(m['indices'])//3 for m in meshes),'bytes':len(out),'sha256':hashlib.sha256(out).hexdigest(),'coordinate_system':'glTF right handed, Y up; metres (assumed scale)','status':'EXPERIMENTAL_BLOCKOUT_NOT_AUTHOR_APPROVED','source_geometry':'head-fit.json + viewer.js; identical mesh across five renders','limitations':['Uncalibrated weak perspective fit to detector landmarks, not measured anatomy','Face is intentionally symmetrized','Cranium, ears, hair, neck and eyeballs are estimated additions','No production facial rig, no validated expression, no skin texture in GLB','Separate component meshes; not a watertight production or printing model']}
(R/'model-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
