import pathlib,json,re
R=pathlib.Path(__file__).resolve().parents[1]
variant='r12g'
a=json.loads((R/'likeness-alignment-r9.json').read_text());a['images']={'T22':a['images']['T22'],'R12':{'url':f'/renders/{variant}-front.png','width':760,'height':950,'matrix':[.6626401581716788,.042176406219616186,-.042176406219616186,.6626401581716788,28.084887644000133,-131.72373115436818]}};a['status']='结构重建后的当前试稿；T22身份参考保持不变。';a['alignment_method']='Reference camera projection plus a single common scale/rotation; no local face warping.'
(R/'likeness-alignment-r12.json').write_text(json.dumps(a,ensure_ascii=False),encoding='utf8')
html=(R/'comparison.html').read_text(encoding='utf8').replace('R9','R12').replace('likeness-alignment-r9.json','likeness-alignment-r12.json')
html=html.replace('R12：重构后待核对','R12：眼周与口周重建').replace('工作试验 · 非定稿','真实 3D 渲染')
html=re.sub(r'<p class="notice">.*?</p>','<p class="notice">使用 T22 估计机位渲染，再统一画面旋转与大小；没有局部拉伸五官。原图仍是身份参考。</p>',html)
html=re.sub(r'<section class="notes">.*?</section>','<section class="notes"><p><strong>本轮结构变化：</strong>重建眼周与口周连续网格，并用本地三维深度估计校准鼻体、眶下和唇颏层次；修平局部褶脊及唇下起伏。</p><p>可切换无贴图版本，单独查看真实曲面。身份仍以 T22 为准。这是可旋转的同一套网格；皮肤沿用 F03 材质，虹膜取自 T22。光照、毛发和皮肤细节尚有差异，不能把网格检查通过等同于完全还原。</p></section>',html)
html=html.replace('R8 / R12 同机位对照','R9 / R12 结构对照').replace('/Carrillo_core_rebuild_R12.blend','/Carrillo_core_rebuild_R12.blend')
html=html.replace('</nav>','<button id="materialToggle">去贴图检查</button></nav>')
html=html.replace("let data,images={},region='face'","let neutralView=false;let data,images={},region='face'")
script="""document.querySelector('#materialToggle').onclick=async e=>{neutralView=!neutralView;const im=new Image();im.src=neutralView?'/renders/VAR-front-neutral.png':'/renders/VAR-front.png';await im.decode();images.R12=im;draw();e.target.classList.toggle('active',neutralView);e.target.textContent=neutralView?'恢复表面材质':'去贴图检查';};""".replace('VAR',variant)
html=html.replace("document.querySelector('#lines').onchange",script+"\ndocument.querySelector('#lines').onchange")
html=html.replace('href="/"','href="/model-r12-candidate.html"').replace('/sculpt-comparison.html','/sculpt-comparison-r12-candidate.html')
(R/'comparison-r12-candidate.html').write_text(html,encoding='utf8')
viewer=(R/'viewer-r10-candidate.js').read_text(encoding='utf8').replace('/carrillo-core-r10.glb','/carrillo-core-r12.glb').replace('/hair|groom|fringe|locks/i','/hair|groom|fringe|locks|curl/i')
viewer=viewer.replace('(a===0?11.5:4)','11.5').replace("function angle(a){","function angle(a){if(a===-45){const axis=new THREE.Vector3(0,1,0),theta=-Math.PI/4;camera.position.copy(controls.target).add(new THREE.Vector3(.08775785,.20000315,.97585721).applyAxisAngle(axis,theta).multiplyScalar(700));camera.up.copy(new THREE.Vector3(.05259548,.97734005,-.20503692).applyAxisAngle(axis,theta));camera.zoom=1;camera.updateProjectionMatrix();camera.lookAt(controls.target);controls.update();return;}")
(R/'viewer-r12-candidate.js').write_text(viewer,encoding='utf8')
index=(R/'model-r10-candidate.html').read_text(encoding='utf8').replace('R10','R12').replace('r10','r12')
index=re.sub(r'<div class="sub">.*?</div>','<div class="sub">R12 · 眼周、鼻唇与下颌结构重建</div>',index)
index=re.sub(r'<header>(.*?)<span>.*?</span></header>',r'<header>\1<span>当前工作版本</span></header>',index,flags=re.S)
index=re.sub(r'<div class="notes">.*?</div>','<div class="notes"><strong>这一轮：</strong>重建眼周与口周网格；融合本地估计的立体深度，再校准眼睑、鼻体、眶下和唇颏。可旋转或去贴图检查。<br>完整 Blender 工程保留全部发丝；浏览器简化发丝，光照与角膜显示也略有不同。</div>',index,flags=re.S)
index=index.replace('core-r12-front.png',variant+'-front.png').replace('core-r12-threequarter.png',variant+'-threequarter.png').replace('core-r12-neutral.png',variant+'-front-neutral.png')
index=index.replace('core-r12-front-soft.png',variant+'-front.png').replace('/viewer-r12-candidate.js?v=10','/viewer-r12-candidate.js?v=11').replace('href="/sculpt-comparison.html"','href="/sculpt-comparison-r12-candidate.html"').replace('href="/comparison.html"','href="/comparison-r12-candidate.html"')
index=index.replace('R9 / R12 同机位对照','R9 / R12 结构对照')
index=index.replace('data-angle="-35"','data-angle="-45"')
(R/'model-r12-candidate.html').write_text(index,encoding='utf8')
style='body{margin:0;background:#171719;color:#e7e1d7;font:15px/1.7 Microsoft Yahei,sans-serif}main{max-width:1200px;margin:auto;padding:24px}h1{font-size:24px;font-weight:500}p{color:#bbb3a5}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}figure{margin:0}img{width:100%;display:block}figcaption{padding:8px;background:#292927}button,a{font:inherit;color:#e5d4b8;background:#292927;border:1px solid #655d50;padding:7px 13px;text-decoration:none;cursor:pointer;margin-right:8px}.bar{margin:18px 0}'
comparison=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>R9 与 R12 结构对照</title><style>{style}</style><main><h1>R9 与 R12 · 同机位结构对照</h1><p>相同相机与主灯参数；去掉照片贴图，检查眼周、鼻唇及下颌的实际曲面。</p><div class="bar"><button onclick="setView('front')">正面</button><button onclick="setView('side')">P14 估计机位</button><a href="/comparison-r12-candidate.html">与 T22 对照</a></div><div class="grid"><figure><figcaption>修正前 R9</figcaption><img id="old" src="/renders/r9-r11-camera-front.png"></figure><figure><figcaption>重建后 R12</figcaption><img id="new" src="/renders/{variant}-front-neutral.png"></figure></div></main><script>function setView(v){{document.querySelector('#old').src='/renders/r9-r11-camera-'+v+'.png';document.querySelector('#new').src='/renders/{variant}-'+v+'-neutral.png';}}</script></html>'''
(R/'sculpt-comparison-r12-candidate.html').write_text(comparison,encoding='utf8')
print('R12 preview candidates prepared',variant)
