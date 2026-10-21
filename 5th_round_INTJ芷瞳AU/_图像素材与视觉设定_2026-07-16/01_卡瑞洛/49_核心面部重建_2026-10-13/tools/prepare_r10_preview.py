import pathlib,json,sys,re,shutil
R=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'47_三维头模结构试验_2026-10-12/tools/python'))
import numpy as np
a=json.loads((R/'likeness-alignment-r10-internal.json').read_text());model=a['images'].pop('R10E');model['url']='/renders/core-r10-front-soft.png'
a['images']['R10']=model
a['status']='R10 self-reviewed working reconstruction. Not an established identity match.'
a['alignment_method']='Model orthographic camera mapped directly into the estimated T22 reference camera; a single shared canvas transform. No nonrigid image warp.'
a.pop('metrics_eye_distance_normalized',None)
(R/'likeness-alignment-r10.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
s=(R/'comparison.html').read_text(encoding='utf8')
s=s.replace('R9','R10').replace('likeness-alignment-r9.json','likeness-alignment-r10.json')
s=s.replace('先对齐眼睛的间距和画面旋转，再看具体形状。','按 T22 的估计机位对齐。可切换均衡照明、侧光和去贴图表面。')
s=s.replace('R10：重构后待核对','R10 · 相似度仍有差距')
s=s.replace('仅统一画面内旋转和眼间距，未统一头部俯仰、左右转角、镜头或表情。沿用上一版的图像对齐位置；仅参考图显示估计轮廓，不能当作骨骼测量。','模型按估计的 T22 相机位置对齐，未对渲染图作局部拉伸。相机参数、表情和参考轮廓仍有估计误差，叠合不能证明是同一张脸。')
s=re.sub(r'<section class="notes">.*?</section>','<section class="notes"><p><strong>本轮自查与修改：</strong>重调眼球与眼睑的关系、眉下转折、颧部至下颌和下巴的衔接；保留高鼻梁并收窄鼻翼与鼻尖两侧；整理唇部表面，重建发束并降低过强的反光。</p><p><strong>仍未解决：</strong>眼周还带有模型感，耳部与皮肤细节不足，发束尚未复现 T22 的自然层次；转面后的鼻唇轮廓仍需进一步雕塑。当前不能作为已定稿的多视角身份锚点。</p></section>',s,flags=re.S)
s=s.replace('<button id="overlay">','<button data-style="front-soft" class="active">均衡光</button><button data-style="front">侧光</button><button data-style="front-neutral">去贴图</button><button id="overlay">')
s=s.replace('R8 / R10 同机位对照','本轮多视角与自查')
s=s.replace("document.querySelector('#mix').oninput", """document.querySelectorAll('[data-style]').forEach(b=>b.onclick=()=>{const im=new Image();im.onload=()=>{images.R10=im;document.querySelectorAll('[data-style]').forEach(x=>x.classList.toggle('active',x===b));draw();};im.src='/renders/core-r10-'+b.dataset.style+'.png';});
document.querySelector('#mix').oninput""")
(R/'comparison-r10-candidate.html').write_text(s,encoding='utf8')
# Preview geometry receives the atlas as exported; remove the obsolete shader
# that used to repaint regions and discard material corrections.
s=(R/'viewer.js').read_text(encoding='utf8').replace('carrillo-core-r9.glb','carrillo-core-r10.glb')
start=s.index("o.material.onBeforeCompile=");end=s.index("o.userData.originalMaterial",start);s=s[:start]+s[end:]
s=s.replace("controls.target.set(0,-2,-25)","controls.target.set(0,-2,-25)")
s=s.replace("function angle(a){", """function angle(a){if(a===-56){camera.position.copy(controls.target).add(new THREE.Vector3(-.83002496,-.01832682,.55742506).multiplyScalar(700));camera.up.set(-.15420478,.96803939,-.19778935);camera.zoom=1;camera.updateProjectionMatrix();camera.lookAt(controls.target);controls.update();return;}""")
(R/'viewer-r10-candidate.js').write_text(s,encoding='utf8')
s=(R/'index.html').read_text(encoding='utf8').replace('R9','R10').replace('/viewer.js?v=9','/viewer-r10-candidate.js?v=10')
s=s.replace('高鼻梁与窄鼻翼试修','眼周、面部结构与发束综合修订')
s=s.replace('<button data-angle="-75">近侧面</button>','<button data-angle="-56">P14 对应机位</button><button data-angle="-75">近侧面</button>')
s=s.replace('依据作者纠正，抬高鼻根至鼻梁中段的前突，并收窄鼻翼及相连鼻孔缘。新增鼻部正侧面对照，检查真实高度变化。','重调眼睑包裹、颧颌与下巴衔接、鼻翼及唇部表面，重建发束。经过连续内部对照，仍未达到定稿相似度。')
s=s.replace('R8 / R10 同机位对照','本轮多视角与自查')
s=s.replace('core-r9-front.png','core-r10-front-soft.png').replace('core-r9-threequarter.png','core-r10-threequarter.png').replace('core-r9-neutral.png','core-r10-neutral.png')
(R/'model-r10-candidate.html').write_text(s,encoding='utf8')
html="""<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>卡瑞洛 · R10 多视角自查</title><style>
*{box-sizing:border-box}body{background:#171819;color:#ebe5db;font:15px/1.7 'Microsoft Yahei',sans-serif;margin:0}main{max-width:1300px;margin:auto;padding:26px}h1{font-weight:500;margin:0}p{color:#bbb4a7}nav{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0}button,a{padding:8px 13px;background:#292a28;color:#e7decc;border:1px solid #635d50;border-radius:5px;text-decoration:none;cursor:pointer}button.active{background:#d6c3a3;color:#24201a}.grid{display:grid;grid-template-columns:1fr 1fr;gap:15px}figure{margin:0;background:#252522}figcaption{padding:10px 15px}img{display:block;width:100%}article{border-top:1px solid #4a463f;margin-top:25px;padding-top:15px}strong{color:#e2cfad}</style><main>
<h1>卡瑞洛 · R10 多视角自查</h1><p>同一份真实模型的不同视角与材质。保留原版 R9 和本轮全部内部候选。</p>
<nav><button data-view="front-soft" class="active">正面 · 均衡光</button><button data-view="front">正面 · 侧光</button><button data-view="p14">P14 估计机位</button><button data-view="threequarter">45° 转面</button></nav>
<div class="grid"><figure><figcaption>表面与材质</figcaption><img id="colour" src="/renders/core-r10-front-soft.png" alt="R10 正面"></figure><figure><figcaption>去贴图 · 几何表面</figcaption><img id="clay" src="/renders/core-r10-front-neutral.png" alt="R10 几何表面"></figure></div>
<article><strong>本轮发现并处理</strong><p>眼球反光过亮、眼睑与球面不协调、唇部局部鼓包、鼻翼与鼻尖偏宽、颧部至下颌及下巴衔接、灰白头皮漏出、发束方向单一。每轮渲染后继续修改，未让作者逐项补充问题。</p><strong>当前仍有差距</strong><p>眼窝与眼睑的表面仍有模型感；耳部和皮肤缺少足够细节；发束层次与原图不同；侧面的鼻唇轮廓还不够贴近参考。R10 是保留的迭代结果，不能宣布身份匹配或替换已认可的人像图。</p></article>
<nav><a href="/">旋转模型</a><a href="/comparison.html">与 T22 对齐</a><a href="/comparison-r9.html">保留的 R9 对照</a><a href="/Carrillo_core_rebuild_R10.blend" download>Blender 工程</a></nav>
</main><script>document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{const v=b.dataset.view;document.querySelector('#colour').src='/renders/core-r10-'+v+'.png';document.querySelector('#clay').src='/renders/core-r10-'+({p14:'p14-neutral',threequarter:'neutral'}[v]||'front-neutral')+'.png';document.querySelectorAll('[data-view]').forEach(x=>x.classList.toggle('active',x===b));});</script></html>"""
(R/'sculpt-comparison-r10-candidate.html').write_text(html,encoding='utf8')
print('Candidate R10 preview prepared, public pages untouched.')
