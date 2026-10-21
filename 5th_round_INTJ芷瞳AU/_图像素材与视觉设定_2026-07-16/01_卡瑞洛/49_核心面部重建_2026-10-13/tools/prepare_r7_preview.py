import pathlib,json,shutil
R=pathlib.Path(__file__).resolve().parents[1]
# Preserve the complete previous preview before changing the default version.
for source,dest in [('index.html','model-r6.html'),('viewer.js','viewer-r6.js'),('comparison.html','comparison-r6.html'),('sculpt-comparison.html','sculpt-comparison-r6.html')]:
 if not (R/dest).exists():shutil.copy2(R/source,R/dest)
p=R/'model-r6.html';s=p.read_text(encoding='utf8');s=s.replace('/viewer.js?v=6','/viewer-r6.js?v=6');p.write_text(s,encoding='utf8')
s=(R/'viewer-r6.js').read_text(encoding='utf8').replace('r6.glb','r7.glb');(R/'viewer.js').write_text(s,encoding='utf8')
s=(R/'model-r6.html').read_text(encoding='utf8').replace('R6','R7').replace('r6-','r7-').replace('/viewer-r6.js?v=6','/viewer.js?v=7')
s=s.replace('下颌衔接、眼眶与鼻口结构调整','眼窝、下眼睑与下颌下巴调整').replace('本轮调整颧部—下颌—下巴衔接，再校准眼眶、眼睑和鼻口。','本轮重做眼球与眼睑的深度衔接，并调整下颌后方转折及下巴侧面体积。').replace('R5 / R7','R6 / R7')
(R/'index.html').write_text(s,encoding='utf8')
s=(R/'sculpt-comparison-r6.html').read_text(encoding='utf8').replace('R6','R7').replace('r6-','r7-').replace('R5','R6').replace('r5-','r6-')
s=s.replace('检查下颌转折、颧下过渡和眼睑。','重点检查眼窝、下眼睑，以及下颌角和下巴。')
s=s.replace('<button data-view="neutral" class="active">45° 去贴图</button>','<button data-view="eyes-neutral" class="active">眼部正面 · 去贴图</button><button data-view="eyes-side-neutral">眼部转面 · 去贴图</button><button data-view="eyes">眼部 · 贴图</button><button data-view="neutral">45° 去贴图</button>')
s=s.replace('/renders/core-r6-neutral.png','/renders/core-r6-eyes-neutral.png').replace('/renders/core-r7-neutral.png','/renders/core-r7-eyes-neutral.png').replace('无贴图三分之四视图','眼部无贴图近景')
s=s.replace('依次调整了颧部—下颌—颏部衔接、眼眶与眼睑、鼻体和口周。发型保持原样；虹膜色素保持原样，反射有所调整。几何检查与人物相似度分开判断，本轮尚未获得作者认可。','眼眶与眼睑修改可在去贴图视图中检查；下颌和下巴变化较轻，切换全脸与侧面观察。当前仍为待评价工作稿，人物相似度未通过。')
(R/'sculpt-comparison.html').write_text(s,encoding='utf8')
# The eye projection and camera are identical, so retain the previous image
# alignment matrix. Do not reuse the old model contour as current evidence.
a=json.loads((R/'likeness-alignment-r6.json').read_text(encoding='utf8'))
model=a['images'].pop('R6');model['url']='/renders/core-r7-front.png';model.pop('points',None)
a['images']['R7']=model;a.pop('metrics_eye_distance_normalized',None)
a['status']='R7 working model; identity not established.'
a['alignment_method']='R6 image alignment retained because camera and eye projection are unchanged. R7 model landmark contours omitted; not re-detected.'
(R/'likeness-alignment-r7.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
s=(R/'comparison-r6.html').read_text(encoding='utf8').replace('R6','R7').replace('r6.','r7.').replace('R5 / R7','R6 / R7')
s=s.replace('显示参考线与估计轮廓','显示参考图轮廓与对齐线')
s=s.replace('轮廓来自自动检测，可能受到贴图影响，不能当作骨骼测量。','沿用相同机位和眼部投影的对齐参数；仅参考图显示估计轮廓，不能当作骨骼测量。')
s=s.replace('R7 已调整下颌衔接、眼眶与鼻口，但仍为工作稿。眼窝和上睑轮廓尚未达到参考。','R7 调整了眼球与眼睑的深度关系、下颌后方转折和下巴侧面体积，人物相似度仍未通过。')
s=s.replace('for(const ids of Object.values(data.groups))','for(const ids of Object.values(d.points?data.groups:{}))')
(R/'comparison.html').write_text(s,encoding='utf8')
s=(R/'tools/verify_r6.cjs').read_text(encoding='utf8').replace('R6','R7').replace('r6','r7')
s=s.replace("const views=['neutral'","const views=['eyes-neutral','eyes-side-neutral','eyes','neutral'")
s=s.replace("await page.click('[data-view=\"neutral\"]');await page.waitForFunction", "await page.click('[data-view=\"eyes-neutral\"]');await page.waitForFunction")
(R/'tools/verify_r7.cjs').write_text(s,encoding='utf8')
(R/'Open_Carrillo_Core_R7.cmd').write_text((R/'Open_Carrillo_Core_R6.cmd').read_text().replace('R6','R7'),encoding='ascii')
print('Prepared R7 preview, preserved R6 preview and native files.')
