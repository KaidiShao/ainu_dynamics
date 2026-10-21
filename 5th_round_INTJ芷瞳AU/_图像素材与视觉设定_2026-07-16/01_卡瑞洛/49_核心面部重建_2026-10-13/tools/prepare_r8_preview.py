import pathlib,json,shutil
R=pathlib.Path(__file__).resolve().parents[1]
for source,dest in [('index.html','model-r7.html'),('viewer.js','viewer-r7.js'),('comparison.html','comparison-r7.html'),('sculpt-comparison.html','sculpt-comparison-r7.html')]:
 if not (R/dest).exists():shutil.copy2(R/source,R/dest)
for f in ['model-r7.html','comparison-r7.html','sculpt-comparison-r7.html']:
 p=R/f;s=p.read_text(encoding='utf8').replace('href="/"','href="/model-r7.html"').replace('href="/comparison.html"','href="/comparison-r7.html"').replace('href="/sculpt-comparison.html"','href="/sculpt-comparison-r7.html"').replace('/viewer.js?v=7','/viewer-r7.js?v=7');p.write_text(s,encoding='utf8')
s=(R/'viewer-r7.js').read_text(encoding='utf8').replace('r7.glb','r8.glb');(R/'viewer.js').write_text(s,encoding='utf8')
s=(R/'model-r7.html').read_text(encoding='utf8').replace('R7','R8').replace('r7-','r8-').replace('/viewer-r7.js?v=7','/viewer.js?v=8')
s=s.replace('href="/model-r7.html"','href="/"').replace('href="/comparison-r7.html"','href="/comparison.html"').replace('href="/sculpt-comparison-r7.html"','href="/sculpt-comparison.html"')
s=s.replace('眼窝、下眼睑与下颌下巴调整','下鼻梁、鼻尖与眼周下颌调整').replace('本轮重做眼球与眼睑的深度衔接，并调整下颌后方转折及下巴侧面体积。','本轮收窄下鼻梁与鼻尖两侧，轻调鼻翼；整理上睑至眉弓的转折，以及下颌侧面与颌下的交接。').replace('R6 / R8','R7 / R8')
(R/'index.html').write_text(s,encoding='utf8')
s=(R/'sculpt-comparison-r7.html').read_text(encoding='utf8').replace('R7','R8').replace('r7-','r8-').replace('R6','R7').replace('r6-','r7-')
s=s.replace('href="/model-r7.html"','href="/"').replace('href="/comparison-r7.html"','href="/comparison.html"').replace('href="/sculpt-comparison-r7.html"','href="/sculpt-comparison.html"')
s=s.replace('重点检查眼窝、下眼睑，以及下颌角和下巴。','重点检查下鼻梁、鼻尖两侧、眼周与下颌转折。')
s=s.replace('<button data-view="eyes-neutral" class="active">','<button data-view="nose-neutral" class="active">鼻部正面 · 去贴图</button><button data-view="nose-side-neutral">鼻部转面 · 去贴图</button><button data-view="eyes-neutral">')
s=s.replace('src="/renders/core-r7-eyes-neutral.png"','src="/renders/core-r7-nose-neutral.png"').replace('src="/renders/core-r8-eyes-neutral.png"','src="/renders/core-r8-nose-neutral.png"').replace('眼部无贴图近景','鼻部无贴图近景')
s=s.replace('眼眶与眼睑修改可在去贴图视图中检查；下颌和下巴变化较轻，切换全脸与侧面观察。','下鼻梁与鼻尖两侧的收窄可在鼻部近景中检查。眼周与下颌变化较轻，请切换对应视图观察。')
(R/'sculpt-comparison.html').write_text(s,encoding='utf8')
a=json.loads((R/'likeness-alignment-r7.json').read_text(encoding='utf8'));model=a['images'].pop('R7');model['url']='/renders/core-r8-front.png';a['images']['R8']=model
a['status']='R8 working model; identity not established.';a['alignment_method']='Retained R7 image alignment for the same camera. No newly detected R8 contours or measurements.'
(R/'likeness-alignment-r8.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
s=(R/'comparison-r7.html').read_text(encoding='utf8').replace('R7','R8').replace('likeness-alignment-r7.json','likeness-alignment-r8.json').replace('R6 / R8','R7 / R8')
s=s.replace('href="/model-r7.html"','href="/"').replace('href="/comparison-r7.html"','href="/comparison.html"').replace('href="/sculpt-comparison-r7.html"','href="/sculpt-comparison.html"')
s=s.replace('<button data-region="lower">','<button data-region="nose">鼻部</button><button data-region="lower">')
s=s.replace("lower:{zoom:1.55", "nose:{zoom:3,x:256,y:282},lower:{zoom:1.55")
s=s.replace('沿用相同机位和眼部投影的对齐参数；仅参考图显示估计轮廓，不能当作骨骼测量。','沿用上一版的图像对齐位置；仅参考图显示估计轮廓，不能当作骨骼测量。')
s=s.replace('R8 调整了眼球与眼睑的深度关系、下颌后方转折和下巴侧面体积，人物相似度仍未通过。','R8 收窄下鼻梁与鼻尖两侧，轻调鼻翼，并整理上睑至眉弓、下颌侧面至颌下的转折。人物相似度仍未通过。')
(R/'comparison.html').write_text(s,encoding='utf8')
s=(R/'tools/verify_r7.cjs').read_text(encoding='utf8').replace('R7','R8').replace('r7','r8').replace("const views=['eyes-neutral'","const views=['nose-neutral','nose-side-neutral','eyes-neutral'")
s=s.replace("await page.click('[data-view=\"eyes-neutral\"]');await page.waitForFunction", "await page.click('[data-view=\"nose-neutral\"]');await page.waitForFunction")
s=s.replace("await page.screenshot({path:path.join(__dirname,'../renders/browser-r8-reference.png')});", "await page.screenshot({path:path.join(__dirname,'../renders/browser-r8-reference.png')});await page.click('[data-region=\"nose\"]');await page.screenshot({path:path.join(__dirname,'../renders/browser-r8-nose-reference.png')});")
(R/'tools/verify_r8.cjs').write_text(s,encoding='utf8')
(R/'Open_Carrillo_Core_R8.cmd').write_text((R/'Open_Carrillo_Core_R7.cmd').read_text().replace('R7','R8'),encoding='ascii')
print('R8 preview prepared; R7 versioned preview retained.')
