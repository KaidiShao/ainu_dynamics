import json,struct,pathlib
R=pathlib.Path(__file__).resolve().parents[1];b=(R/'carrillo-web-preview.glb').read_bytes();n=struct.unpack_from('<I',b,12)[0];d=json.loads(b[20:20+n])
for i,m in enumerate(d['materials']):print(i,json.dumps(m))
for m in d['meshes']:
 if 'head' in m['name'].lower():print('HEAD',json.dumps(m))

