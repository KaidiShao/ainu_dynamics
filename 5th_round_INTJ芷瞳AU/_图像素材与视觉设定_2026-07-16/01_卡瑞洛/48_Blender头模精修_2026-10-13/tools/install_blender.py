import pathlib,urllib.request,hashlib,zipfile,json,time,concurrent.futures
R=pathlib.Path(__file__).resolve().parents[1]
INSTALL=pathlib.Path('D:/新建文件夹/ainu_dynamics/_tools/blender')
VERSION='4.5.14'
URL=f'https://download.blender.org/release/Blender4.5/blender-{VERSION}-windows-x64.zip'
def download(url,path):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
 with urllib.request.urlopen(req,timeout=90) as response, open(path,'wb') as out:
  total=int(response.headers.get('Content-Length',0));got=0;last=time.monotonic()
  while True:
   b=response.read(1024*1024)
   if not b:break
   out.write(b);got+=len(b)
   if time.monotonic()-last>10:print(path.name,got,total,flush=True);last=time.monotonic()
 print('downloaded',path.name,got,flush=True)
def extract(archive,dest):
 dest=dest.resolve()
 with zipfile.ZipFile(archive) as z:
  for name in z.namelist():
   if not (dest/name).resolve().is_relative_to(dest):raise RuntimeError('Archive path escaped destination')
  z.extractall(dest)
archive=INSTALL/f'blender-{VERSION}-windows-x64.zip'
asset=R/'assets/human-base-meshes-bundle-v1.4.1.zip'
asset_url='https://download.blender.org/demo/asset-bundles/human-base-meshes/human-base-meshes-bundle-v1.4.1.zip'
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 fs=[pool.submit(download,URL,archive),pool.submit(download,asset_url,asset)]
 for f in fs:f.result()
sha_url=f'https://download.blender.org/release/Blender4.5/blender-{VERSION}.sha256'
checks=urllib.request.urlopen(urllib.request.Request(sha_url,headers={'User-Agent':'Mozilla/5.0'})).read().decode()
(INSTALL/f'blender-{VERSION}.sha256').write_text(checks)
line=next(l for l in checks.splitlines() if archive.name in l);expected=line.split()[0].lower();actual=hashlib.file_digest(open(archive,'rb'),'sha256').hexdigest();assert expected==actual,'SHA256 mismatch'
print('official SHA256 matched',actual,flush=True)
extract(archive,INSTALL);extract(asset,R/'assets/human-base')
folder=INSTALL/f'blender-{VERSION}-windows-x64'
(folder/'portable').mkdir(exist_ok=True);(folder/'4.5/config').mkdir(parents=True,exist_ok=True)
manifest={'version':VERSION,'source':URL,'sha256':actual,'checksum_source':sha_url,'executable':str(folder/'blender.exe'),'portable':True,'asset_source':asset_url,'asset_sha256':hashlib.file_digest(open(asset,'rb'),'sha256').hexdigest()}
(R/'installation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(manifest,ensure_ascii=False),flush=True)
