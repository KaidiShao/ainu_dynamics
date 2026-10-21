import * as THREE from 'three';
import { OrbitControls } from 'three/addons/OrbitControls.js';
import { GLTFLoader } from 'three/addons/GLTFLoader.js';
const canvas=document.querySelector('#view'),host=canvas.parentElement;
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
const scene=new THREE.Scene(),camera=new THREE.OrthographicCamera();
camera.near=.1;camera.far=5000;
const controls=new OrbitControls(camera,canvas);controls.target.set(0,-2,-25);controls.enableDamping=true;controls.minZoom=.5;controls.maxZoom=4;
scene.add(new THREE.HemisphereLight(0xe4e8ef,0x45403b,1.25));
function light(c,intensity,p){const l=new THREE.DirectionalLight(c,intensity);l.position.set(...p);scene.add(l);}
light(0xffeddb,2.4,[200,210,330]);light(0xccd8e8,.65,[-220,90,240]);light(0xffffff,1.1,[100,160,-180]);
function resize(){const w=host.clientWidth,h=host.clientHeight,scale=305;camera.left=-scale*w/h/2;camera.right=scale*w/h/2;camera.top=scale/2;camera.bottom=-scale/2;camera.updateProjectionMatrix();renderer.setSize(w,h,false);}
new ResizeObserver(resize).observe(host);resize();
function angle(a){if(a===-56){camera.position.copy(controls.target).add(new THREE.Vector3(-.83002496,-.01832682,.55742506).multiplyScalar(700));camera.up.set(-.15420478,.96803939,-.19778935);camera.zoom=1;camera.updateProjectionMatrix();camera.lookAt(controls.target);controls.update();return;}const rad=a*Math.PI/180,e=(a===0?11.5:4)*Math.PI/180;
camera.position.copy(controls.target).add(new THREE.Vector3(700*Math.sin(rad)*Math.cos(e),700*Math.sin(e),700*Math.cos(rad)*Math.cos(e)));
camera.up.set(0,1,0); if(a===0){camera.position.copy(controls.target).add(new THREE.Vector3(.08775785,.20000315,.97585721).multiplyScalar(700));camera.up.set(.05259548,.97734005,-.20503692);} camera.zoom=1;camera.updateProjectionMatrix();camera.lookAt(controls.target);controls.update();}
angle(0);
let root,head=[],hair=[],isNeutral=false,showHair=true;
const neutral=new THREE.MeshStandardMaterial({color:0xb6aca0,roughness:.78});
new GLTFLoader().load('/carrillo-core-r10.glb',g=>{
 root=g.scene;scene.add(root);const size=new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());if(size.y<10)root.scale.setScalar(1000);let meshes=0,vertices=0;
 root.traverse(o=>{if(o.isMesh){meshes++;vertices+=o.geometry.attributes.position.count;if(o.name.includes('Carrillo_Head')){head.push(o);o.userData.originalMaterial=o.material;}if(/hair|groom|fringe|locks/i.test(o.name))hair.push(o);}});
 window.modelReady=true;window.sceneStats={meshes,vertices,head:head.length,hair:hair.length};window.model=root;
 document.querySelector('#loading').hidden=true;
},p=>{if(p.total)document.querySelector('#loading').textContent='正在载入模型 '+Math.round(p.loaded/p.total*100)+'%';},
e=>{document.querySelector('#loading').textContent='模型未能载入，请检查本地预览服务。';console.error(e);});
document.querySelectorAll('[data-angle]').forEach(b=>b.onclick=()=>{angle(Number(b.dataset.angle));document.querySelectorAll('[data-angle]').forEach(x=>x.classList.toggle('active',x===b));});
document.querySelector('#neutral').onclick=e=>{isNeutral=!isNeutral;head.forEach(o=>o.material=isNeutral?neutral:o.userData.originalMaterial);e.target.classList.toggle('active',isNeutral);e.target.textContent=isNeutral?'恢复人像贴图':'去贴图检查';window.neutralMode=isNeutral;};
document.querySelector('#hair').onclick=e=>{showHair=!showHair;hair.forEach(o=>o.visible=showHair);e.target.classList.toggle('active',!showHair);e.target.textContent=showHair?'隐藏头发':'显示头发';};
document.querySelectorAll('[data-ref]').forEach(b=>b.onclick=()=>{document.querySelector('#ref').src='/refs/'+b.dataset.ref+'.png';document.querySelectorAll('[data-ref]').forEach(x=>x.classList.toggle('active',x===b));});
function frame(){requestAnimationFrame(frame);controls.update();renderer.render(scene,camera);}frame();



