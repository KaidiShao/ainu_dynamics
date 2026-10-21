import pathlib,json,re
R=pathlib.Path(__file__).resolve().parents[1]
variant='r11l'
a=json.loads((R/'likeness-alignment-r9.json').read_text());a['images']={'T22':a['images']['T22'],'R11':{'url':f'/renders/{variant}-front.png','width':760,'height':950,'matrix':[.6626401581716788,.042176406219616186,-.042176406219616186,.6626401581716788,28.084887644000133,-131.72373115436818]}};a['status']='结构重建后的当前试稿；T22身份参考保持不变。';a['alignment_method']='Reference camera projection plus a single common scale/rotation; no local face warping.'
(R/'likeness-alignment-r11.json').write_text(json.dumps(a,ensure_ascii=False),encoding='utf8')
html=(R/'comparison.html').read_text(encoding='utf8').replace('R9','R11').replace('likeness-alignment-r9.json','likeness-alignment-r11.json')
html=html.replace('R11：重构后待核对','R11：眼周与口周重建').replace('工作试验 · 非定稿','真实 3D 渲染')
html=re.sub(r'<p class="notice">.*?</p>','<p class="notice">使用 T22 估计机位渲染，再统一画面旋转与大小；没有局部拉伸五官。原图仍是身份参考。</p>',html)
html=re.sub(r'<section class="notes">.*?</section>','<section class="notes"><p><strong>本轮结构变化：</strong>重建上下眼睑与眼窝的连接，重做唇缘与唇下过渡，减轻嘴角笑意；细化鼻尖转折和下巴两侧支撑。</p><p>可切换无贴图版本，单独查看真实曲面。头部皮肤沿用 F03 材质，虹膜盘取自 T22；光影和皮肤细节仍与原图有差异。</p></section>',html)
html=html.replace('R8 / R11 同机位对照','R9 / R11 结构对照').replace('/Carrillo_core_rebuild_R11.blend','/Carrillo_core_rebuild_R11.blend')
html=html.replace('</nav>','<button id="materialToggle">去贴图检查</button></nav>')
html=html.replace("let data,images={},region='face'","let neutralView=false;let data,images={},region='face'")
script="""document.querySelector('#materialToggle').onclick=async e=>{neutralView=!neutralView;const im=new Image();im.src=neutralView?'/renders/VAR-front-neutral.png':'/renders/VAR-front.png';await im.decode();images.R11=im;draw();e.target.classList.toggle('active',neutralView);e.target.textContent=neutralView?'恢复表面材质':'去贴图检查';};""".replace('VAR',variant)
html=html.replace("document.querySelector('#lines').onchange",script+"\ndocument.querySelector('#lines').onchange")
html=html.replace('href="/"','href="/model-r11-candidate.html"').replace('/sculpt-comparison.html','/sculpt-comparison-r11-candidate.html')
(R/'comparison-r11-candidate.html').write_text(html,encoding='utf8')
viewer=(R/'viewer-r10-candidate.js').read_text(encoding='utf8').replace('/carrillo-core-r10.glb','/carrillo-core-r11.glb').replace('/hair|groom|fringe|locks/i','/hair|groom|fringe|locks|curl/i')
(R/'viewer-r11-candidate.js').write_text(viewer,encoding='utf8')
index=(R/'model-r10-candidate.html').read_text(encoding='utf8').replace('R10','R11').replace('r10','r11')
index=re.sub(r'<div class="sub">.*?</div>','<div class="sub">R11 · 眼周、鼻唇与下颌结构重建</div>',index)
index=re.sub(r'<header>(.*?)<span>.*?</span></header>',r'<header>\1<span>当前工作版本</span></header>',index,flags=re.S)
index=re.sub(r'<div class="notes">.*?</div>','<div class="notes"><strong>这一轮：</strong>重新连接上下眼睑、眼窝和颊部，重建唇缘与唇颏过渡，整理鼻尖和下巴。可旋转或去贴图检查。<br>完整 Blender 工程保留全部发丝；浏览器简化发丝，光照与角膜显示也略有不同。</div>',index,flags=re.S)
index=index.replace('core-r11-front.png',variant+'-front.png').replace('core-r11-threequarter.png',variant+'-threequarter.png').replace('core-r11-neutral.png',variant+'-front-neutral.png')
index=index.replace('core-r11-front-soft.png',variant+'-front.png').replace('/viewer-r11-candidate.js?v=10','/viewer-r11-candidate.js?v=11').replace('href="/sculpt-comparison.html"','href="/sculpt-comparison-r11-candidate.html"').replace('href="/comparison.html"','href="/comparison-r11-candidate.html"')
index=index.replace('R9 / R11 同机位对照','R9 / R11 结构对照')
(R/'model-r11-candidate.html').write_text(index,encoding='utf8')
style='body{margin:0;background:#171719;color:#e7e1d7;font:15px/1.7 Microsoft Yahei,sans-serif}main{max-width:1200px;margin:auto;padding:24px}h1{font-size:24px;font-weight:500}p{color:#bbb3a5}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}figure{margin:0}img{width:100%;display:block}figcaption{padding:8px;background:#292927}button,a{font:inherit;color:#e5d4b8;background:#292927;border:1px solid #655d50;padding:7px 13px;text-decoration:none;cursor:pointer;margin-right:8px}.bar{margin:18px 0}'
comparison=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>R9 与 R11 结构对照</title><style>{style}</style><main><h1>R9 与 R11 · 同机位结构对照</h1><p>相同相机与主灯参数；去掉照片贴图，检查眼周、鼻唇及下颌的实际曲面。</p><div class="bar"><button onclick="setView('front')">正面</button><button onclick="setView('side')">P14 估计机位</button><a href="/comparison-r11-candidate.html">与 T22 对照</a></div><div class="grid"><figure><figcaption>修正前 R9</figcaption><img id="old" src="/renders/r9-r11-camera-front.png"></figure><figure><figcaption>重建后 R11</figcaption><img id="new" src="/renders/{variant}-front-neutral.png"></figure></div></main><script>function setView(v){{document.querySelector('#old').src='/renders/r9-r11-camera-'+v+'.png';document.querySelector('#new').src='/renders/{variant}-'+v+'-neutral.png';}}</script></html>'''
(R/'sculpt-comparison-r11-candidate.html').write_text(comparison,encoding='utf8')
print('R11 preview candidates prepared',variant)
