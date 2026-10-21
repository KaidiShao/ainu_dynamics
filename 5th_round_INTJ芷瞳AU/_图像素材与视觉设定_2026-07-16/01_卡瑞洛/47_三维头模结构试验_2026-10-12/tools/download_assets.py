import urllib.request, pathlib, concurrent.futures
root=pathlib.Path(__file__).resolve().parents[1]/'assets'
urls={
 'canonical_face_model.obj':'https://raw.githubusercontent.com/google-ai-edge/mediapipe/master/mediapipe/modules/face_geometry/data/canonical_face_model.obj',
 'face_landmarker.task':'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',
 'three.module.js':'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js',
 'three.core.js':'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.core.js',
 'OrbitControls.js':'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/controls/OrbitControls.js',
 'mediapipe-LICENSE':'https://raw.githubusercontent.com/google-ai-edge/mediapipe/master/LICENSE',
 'three-LICENSE':'https://cdn.jsdelivr.net/npm/three@0.180.0/LICENSE'
}
def run(item):
 name,url=item
 try:
  data=urllib.request.urlopen(url,timeout=45).read(); (root/name).write_bytes(data);return name,len(data)
 except Exception as e:return name,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for r in pool.map(run,urls.items()):print(r,flush=True)
