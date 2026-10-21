import json,pathlib,struct
R=pathlib.Path(__file__).resolve().parents[1];p=R/'carrillo-web-preview.glb';b=p.read_bytes()
n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n]);binary=b[20+n:]
for m in d['materials']:
 if m['name']=='Projected_skin_WEB':m['pbrMetallicRoughness']['baseColorTexture']['texCoord']=0
for mesh in d['meshes']:
 if mesh['name']=='GEO-head_animation_realistic':
  for prim in mesh['primitives']:
   att=prim['attributes'];baked=att.get('TEXCOORD_4')
   if baked is not None:
    for k in list(att):
     if k.startswith('TEXCOORD_'):del att[k]
    att['TEXCOORD_0']=baked
j=json.dumps(d,separators=(',',':'),ensure_ascii=False).encode();j+=b' '*((-len(j))%4)
p.write_bytes(struct.pack('<III',0x46546c67,2,20+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+binary)
print('Patched preview to a single atlas UV',p.stat().st_size)

