const http=require('http'),fs=require('fs'),path=require('path');
const root=__dirname,old=path.join(root,'..','47_三维头模结构试验_2026-10-12');
const refs=JSON.parse(fs.readFileSync(path.join(old,'head-fit.json'),'utf8')).sources;
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.png':'image/png','.glb':'model/gltf-binary','.blend':'application/octet-stream','.json':'application/json; charset=utf-8'};
http.createServer((req,res)=>{try{
 const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
 let file;
 if(pathname==='/refs/front.png')file=refs.T22;
 else if(pathname==='/refs/side.png')file=refs.P14;
 else if(pathname.startsWith('/vendor/')){file=path.resolve(old,'assets',pathname.slice(8));if(!file.startsWith(path.resolve(old,'assets')+path.sep))throw Error('path');}
 else{file=path.resolve(root,'.'+(pathname==='/'?'/index.html':pathname));if(!file.startsWith(path.resolve(root)+path.sep))throw Error('path');}
 const stat=fs.statSync(file);if(!stat.isFile())throw Error('file');
 res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Content-Length':stat.size,'Cache-Control':'no-cache'});
 fs.createReadStream(file).pipe(res);
}catch(e){res.writeHead(404);res.end('Not found');}}).listen(8849,'127.0.0.1',()=>console.log('Carrillo 3D: http://127.0.0.1:8849/'));

