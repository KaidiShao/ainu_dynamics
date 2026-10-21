import * as THREE from 'three';
import {OrbitControls} from './assets/OrbitControls.js';
const fit=await (await fetch('./head-fit.json')).json();
const stage=document.getElementById('stage');
const renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setClearColor(0x21242b);renderer.outputColorSpace=THREE.SRGBColorSpace;
stage.appendChild(renderer.domElement);
const scene=new THREE.Scene(), model=new THREE.Group();scene.add(model);
const camera=new THREE.OrthographicCamera(-180,180,180,-180,.1,3000);
const target=new THREE.Vector3(0,0,-20);camera.position.set(400,0,400);camera.lookAt(target);
const controls=new OrbitControls(camera,renderer.domElement);controls.target.copy(target);controls.enableDamping=false;controls.minZoom=.6;controls.maxZoom=3;
const hemi=new THREE.HemisphereLight(0xe5edff,0x4e4540,1.7);scene.add(hemi);
const key=new THREE.DirectionalLight(0xffefdf,3);key.position.set(-180,230,280);scene.add(key);
const fill=new THREE.DirectionalLight(0xc1d8ff,1.2);fill.position.set(190,70,180);scene.add(fill);
const rim=new THREE.DirectionalLight(0xaabdda,1.5);rim.position.set(80,200,-180);scene.add(rim);
const skin=new THREE.MeshStandardMaterial({color:0xa69988,roughness:.85,side:THREE.DoubleSide});
const eyeMat=new THREE.MeshStandardMaterial({color:0xbfc2bd,roughness:.5});
const hairMat=new THREE.MeshStandardMaterial({color:0x282522,roughness:.95});
const browMat=new THREE.MeshStandardMaterial({color:0x38322d,roughness:1});
const irisMat=new THREE.MeshStandardMaterial({color:0x667d88,roughness:.55});
const pupilMat=new THREE.MeshStandardMaterial({color:0x151c22,roughness:.4});
const meshes=[], hairGroup=new THREE.Group(), browGroup=new THREE.Group(), eyeGroup=new THREE.Group();
model.add(hairGroup,browGroup,eyeGroup);
const V=fit.face.vertices.map(v=>new THREE.Vector3(...v));
function geometry(points,triangles,uv){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(points.flatMap(v=>v.toArray?v.toArray():v),3));g.setIndex(triangles.flat());if(uv)g.setAttribute('uv',new THREE.Float32BufferAttribute(uv.flat(),2));g.computeVertexNormals();return g}
function mesh(name,g,mat=skin,parent=model){const m=new THREE.Mesh(g,mat);m.name=name;parent.add(m);meshes.push(m);return m}
// Loop subdivision smooths the coarse landmark surface; the low-resolution control cage is retained in head-fit.json.
function subdiv(points,faces,uv,iterations=2){let p=points.map(x=>x.clone()),f=faces.map(x=>x.slice()),u=uv?.map(x=>x.slice());for(let it=0;it<iterations;it++){
 const edges=new Map(),neighbors=p.map(()=>new Set()),boundary=p.map(()=>[]);
 for(const [a,b,c] of f)for(const [i,j,o]of[[a,b,c],[b,c,a],[c,a,b]]){const k=i<j?i+','+j:j+','+i;let e=edges.get(k);if(!e){e={i:Math.min(i,j),j:Math.max(i,j),opp:[]};edges.set(k,e)}e.opp.push(o);neighbors[i].add(j);neighbors[j].add(i)}
 for(const e of edges.values())if(e.opp.length===1){boundary[e.i].push(e.j);boundary[e.j].push(e.i)}
 const np=p.map((v,i)=>{const b=boundary[i];if(b.length===2)return v.clone().multiplyScalar(.75).addScaledVector(p[b[0]],.125).addScaledVector(p[b[1]],.125);const ns=[...neighbors[i]],beta=ns.length===3?3/16:3/(8*ns.length);let r=v.clone().multiplyScalar(1-ns.length*beta);for(const j of ns)r.addScaledVector(p[j],beta);return r});
 const nu=u?.map(x=>x.slice());
 for(const e of edges.values()){e.index=np.length;let q=p[e.i].clone().add(p[e.j]).multiplyScalar(.5);if(e.opp.length===2)q=p[e.i].clone().add(p[e.j]).multiplyScalar(.375).addScaledVector(p[e.opp[0]],.125).addScaledVector(p[e.opp[1]],.125);np.push(q);if(u)nu.push([(u[e.i][0]+u[e.j][0])/2,(u[e.i][1]+u[e.j][1])/2])}
 const edge=(i,j)=>edges.get(i<j?i+','+j:j+','+i).index,nf=[];for(const[a,b,c]of f){let ab=edge(a,b),bc=edge(b,c),ca=edge(c,a);nf.push([a,ab,ca],[b,bc,ab],[c,ca,bc],[ab,bc,ca])}p=np;f=nf;u=nu;
 }return{p,f,u}}
const eyeRims=[new Set([33,7,163,144,145,153,154,155,133,173,157,158,159,160,161,246]),new Set([263,249,390,373,374,380,381,382,362,398,384,385,386,387,388,466])];
const facialTriangles=fit.face.triangles.filter(t=>!eyeRims.some(r=>t.every(i=>r.has(i))));
const smooth=subdiv(V,facialTriangles,fit.face.uv,2);
const face=mesh('Face_T22_P14_shared_fit',geometry(smooth.p,smooth.f,smooth.u));
const loader=new THREE.TextureLoader(), texture=await loader.loadAsync('/ref/T22.png');texture.colorSpace=THREE.SRGBColorSpace;
const photo=new THREE.MeshBasicMaterial({map:texture,side:THREE.DoubleSide});
// Close the facial boundary with an explicitly estimated cranial loft.
const oval=fit.oval.map(i=>smooth.p[i]), cp=[],cf=[],rings=16;
for(let j=0;j<=rings;j++){const t=j/rings*Math.PI/2;for(const v of oval){const top=Math.max(0,(v.y+12)/65);cp.push(new THREE.Vector3(v.x*Math.cos(t),10+(v.y-10)*Math.cos(t)+47*Math.sin(2*t)*top*top,v.z*Math.cos(t)-116*Math.sin(t)))}}
for(let j=0;j<rings;j++)for(let i=0;i<oval.length;i++){const a=j*oval.length+i,b=j*oval.length+(i+1)%oval.length,c=b+oval.length,d=a+oval.length;cf.push([a,b,c],[a,c,d])}
mesh('Cranium_ESTIMATED',geometry(cp,cf));
function ellipsoid(name,center,radii,mat,parent=model){const g=new THREE.SphereGeometry(1,40,28);g.scale(...radii);g.translate(...center);return mesh(name,g,mat,parent)}
// Neck and shoulder pedestal are separate blockout meshes, not recovered anatomy.
const neck=ellipsoid('Neck_ESTIMATED',[0,-120,-57],[39,54,40],skin);
const shoulders=ellipsoid('Bust_ESTIMATED',[0,-170,-56],[116,42,61],new THREE.MeshStandardMaterial({color:0x34363a,roughness:1}));
for(const side of[-1,1]){
 const ear=ellipsoid('Ear_ESTIMATED_'+side,[side*72,-21,-58],[10,25,14],skin);ear.rotation.z=-side*.12;
 const inner=ellipsoid('Ear_concha_ESTIMATED_'+side,[side*79,-21,-50],[2,13,7],new THREE.MeshStandardMaterial({color:0x837765,roughness:1}));
}
function tube(name,points,r,mat,parent,segments=64){const path=new THREE.CatmullRomCurve3(points);return mesh(name,new THREE.TubeGeometry(path,segments,r,6,false),mat,parent)}
const eyeLoops=[[33,160,158,133,153,144],[263,387,385,362,380,373]];
for(let e=0;e<2;e++){
 const loop=eyeLoops[e],a=V[loop[0]],b=V[loop[3]],width=a.distanceTo(b),r=width*.52;
 const center=a.clone().add(b).multiplyScalar(.5);center.y+=2;center.z-=r*.67;
 ellipsoid('Eyeball_'+e,center.toArray(),[r,r,r],eyeMat,eyeGroup);
 // The gaze points along the head, so it remains constant as the camera rotates.
 const iris=new THREE.Mesh(new THREE.SphereGeometry(r+.18,40,24,0,Math.PI*2,0,.40),irisMat);
 iris.rotation.x=Math.PI/2;iris.position.copy(center);iris.name='Iris_'+e;eyeGroup.add(iris);meshes.push(iris);
 const pupil=new THREE.Mesh(new THREE.SphereGeometry(r+.28,32,16,0,Math.PI*2,0,.18),pupilMat);pupil.rotation.x=Math.PI/2;pupil.position.copy(center);pupil.name='Pupil_'+e;eyeGroup.add(pupil);meshes.push(pupil);
}
for(const ids of[[70,63,105,66,107],[336,296,334,293,300]]){const p=ids.map(i=>V[i].clone().add(new THREE.Vector3(0,0,1.5)));tube('Brow_blockout',p,1.65,browMat,browGroup,32)}
// Scalp envelope and broad wavy locks: silhouette placeholder, not strand hair.
function hairPoint(t,phi,offset=0){const front=Math.max(0,Math.cos(phi)),back=Math.max(0,-Math.cos(phi));const end=1.53-.37*front*front+.44*back*back;const theta=t*end;const wave=1.3*Math.sin(7*phi+8*t)+.9*Math.cos(17*phi-9*t);const r=1+offset*.008+wave*.009;return new THREE.Vector3(83*r*Math.sin(theta)*Math.sin(phi),12+115*r*Math.cos(theta),-44+84*r*Math.sin(theta)*Math.cos(phi))}
const hp=[],hf=[],hRows=36,hCols=80;
for(let j=0;j<=hRows;j++)for(let i=0;i<=hCols;i++)hp.push(hairPoint(j/hRows,i/hCols*Math.PI*2));
for(let j=0;j<hRows;j++)for(let i=0;i<hCols;i++){const a=j*(hCols+1)+i,b=a+1,c=b+hCols+1,d=a+hCols+1;hf.push([a,c,b],[a,d,c])}
mesh('Hair_envelope_ESTIMATED',geometry(hp,hf),hairMat,hairGroup);
for(let i=0;i<68;i++){const phi=i/68*Math.PI*2,points=[];for(let j=0;j<=25;j++){let t=.12+j/25*.88,ph=phi+.38*Math.sin(t*7+i*.31)+.065*Math.sin(t*28+i);points.push(hairPoint(t,ph,1.5))}tube('Hair_lock_ESTIMATED_'+i,points,2+(i%4)*.24,hairMat,hairGroup,40)}
// Slightly uneven front lock silhouettes retain the fuller original reference hairstyle.
for(let i=0;i<7;i++){const phi=-.5+i*.16,pts=[];for(let j=0;j<14;j++){let t=.72+j/13*.34;const p=hairPoint(t,phi+.14*Math.sin(j*.45+i),2);p.y-=Math.max(0,t-.92)*22;pts.push(p)}tube('Fringe_lock_ESTIMATED_'+i,pts,2.6,hairMat,hairGroup,28)}
function setAngle(a){const rad=a*Math.PI/180;camera.position.set(-570*Math.sin(rad),0,-20+570*Math.cos(rad));camera.up.set(0,1,0);camera.lookAt(target);controls.target.copy(target);controls.update();document.getElementById('yaw').value=a;document.getElementById('angle-label').textContent=`${a===0?'正面':a===90?'正侧面':a+'°'} · 正交结构视图`;document.querySelectorAll('[data-a]').forEach(b=>b.classList.toggle('active',+b.dataset.a===a));render()}
function lighting(mode){const hard=mode==='side';hemi.intensity=hard?.35:1.7;key.intensity=hard?4.3:3;fill.intensity=hard?.08:1.2;rim.intensity=hard?1.4:1.5;key.position.set(hard?-240:-180,hard?110:230,hard?150:280);render()}
function surface(mode){face.material=mode==='photo'?photo:skin;for(const m of meshes)if(m.material!==photo)m.material.wireframe=mode==='wire';render()}
function render(){renderer.render(scene,camera)}
function resize(){const w=stage.clientWidth,h=stage.clientHeight;renderer.setSize(w,h);const half=190;camera.left=-half*w/h;camera.right=half*w/h;camera.top=half;camera.bottom=-half;camera.updateProjectionMatrix();render()}
function exportOBJ(){let text='# Carrillo experimental shared head mesh. Units assumed mm. Not approved likeness.\n',offset=1;model.updateMatrixWorld(true);for(const m of meshes){if(!m.visible||!m.parent.visible)continue;const g=m.geometry,p=g.attributes.position;const ix=g.index;text+='o '+m.name+'\n';for(let i=0;i<p.count;i++){const v=new THREE.Vector3().fromBufferAttribute(p,i).applyMatrix4(m.matrixWorld);text+=`v ${v.x.toFixed(5)} ${v.y.toFixed(5)} ${v.z.toFixed(5)}\n`}for(let i=0;i<(ix?ix.count:p.count);i+=3){const a=ix?ix.getX(i):i,b=ix?ix.getX(i+1):i+1,c=ix?ix.getX(i+2):i+2;text+=`f ${a+offset} ${b+offset} ${c+offset}\n`}offset+=p.count}return text}
document.getElementById('angles').onclick=e=>{if(e.target.dataset.a!==undefined)setAngle(+e.target.dataset.a)};
document.getElementById('yaw').oninput=e=>setAngle(+e.target.value);
document.getElementById('lighting').onchange=e=>lighting(e.target.value);document.getElementById('surface').onchange=e=>surface(e.target.value);
document.getElementById('hair').onchange=e=>{hairGroup.visible=e.target.checked;render()};document.getElementById('brows').onchange=e=>{browGroup.visible=e.target.checked;irisMat.color.setHex(e.target.checked?0x667d88:0x8d8d86);render()};
document.getElementById('reset').onclick=()=>{camera.zoom=1;camera.updateProjectionMatrix();setAngle(45)};
document.getElementById('obj').onclick=()=>{const url=URL.createObjectURL(new Blob([exportOBJ()],{type:'text/plain'}));const a=document.createElement('a');a.href=url;a.download='carrillo-head-blockout-v1.obj';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
controls.addEventListener('change',render);new ResizeObserver(resize).observe(stage);resize();setAngle(45);
document.getElementById('loading').remove();document.getElementById('status').textContent=`T22 + P14 共用面部网格 · ${smooth.p.length.toLocaleString()} 个面部顶点 · 灰模用于结构评估，照片投影仅作辅助`;
function exportSceneData(){model.updateMatrixWorld(true);return meshes.map(m=>{const g=m.geometry,p=g.attributes.position,n=g.attributes.normal,normalMatrix=new THREE.Matrix3().getNormalMatrix(m.matrixWorld),positions=[],normals=[];for(let i=0;i<p.count;i++){positions.push(...new THREE.Vector3().fromBufferAttribute(p,i).applyMatrix4(m.matrixWorld).multiplyScalar(.001).toArray());normals.push(...new THREE.Vector3().fromBufferAttribute(n,i).applyMatrix3(normalMatrix).normalize().toArray())}return{name:m.name,positions,normals,indices:g.index?Array.from(g.index.array):Array.from({length:p.count},(_,i)=>i),color:m.material.color.toArray(),roughness:m.material.roughness??.85}})}
window.headTest={ready:true,setAngle,lighting,surface,render,exportOBJ,exportSceneData,fit,model,scene,camera,renderer,meshes,counts:()=>meshes.map(m=>({name:m.name,vertices:m.geometry.attributes.position.count,triangles:(m.geometry.index?.count||m.geometry.attributes.position.count)/3}))};
