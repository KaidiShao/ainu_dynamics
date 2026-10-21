import pathlib,json,hashlib
R=pathlib.Path(__file__).resolve().parents[1]
for file in ['model-r6.html','comparison-r6.html','sculpt-comparison-r6.html']:
 p=R/file;s=p.read_text(encoding='utf8').replace('href="/"','href="/model-r6.html"').replace('href="/comparison.html"','href="/comparison-r6.html"').replace('href="/sculpt-comparison.html"','href="/sculpt-comparison-r6.html"');p.write_text(s,encoding='utf8')
previous=json.loads((R/'checksums-r6.json').read_text(encoding='utf-8-sig'))
for entry in previous:
 assert hashlib.sha256(pathlib.Path(entry['Path']).read_bytes()).hexdigest().upper()==entry['Hash'], 'Previous native file changed'
hashes=[{'Path':str(R/f),'Hash':hashlib.sha256((R/f).read_bytes()).hexdigest().upper()} for f in ['Carrillo_core_rebuild_R7.blend','carrillo-core-r7.glb']]
(R/'checksums-r7.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2),encoding='utf8')
p=R/'core-r7-manifest.json';d=json.loads(p.read_text(encoding='utf8'))
d['status']='Structurally revised working model; identity likeness not established; awaiting author evaluation.'
d['review']={
 'source':'Existing independent review_carrillo_angle agent plus main-agent image inspection',
 'intermediate_issue':'Outer upper-lid corner had a sharp depth discontinuity; fixed the missed-sphere-ray branch. New renders show no corresponding spike.',
 'improvement':'Lower-lid wrap is geometrically more explicit; chin sides slightly less full; jaw-angle change remains modest.',
 'final_refinement':'Reduced lower-lid roll radius from 13.10 to 12.70; reduced and shortened the crease below it after review flagged a mild eye-bag impression.',
 'final_independent_check':'Mild eye-bag impression reduced; crease shadow is shallower and lateral transition softer while lid support remains. No new obvious sharp fold or inverted surface visible in the inspected front and turned closeups.',
 'remaining':'Eye/lid shape and character expression still differ from T22. No identity pass.'}
d['image_alignment']='R6 camera alignment retained because eye projection is unchanged. Removed old model contour and metrics; no newly measured R7 identity metrics.'
d['preservation']='R6 native and GLB SHA256 hashes unchanged. Versioned R6 preview retained.'
d['render_views']=['front','threequarter','near-profile','front-neutral','neutral','eyes','eyes-neutral','eyes-side-neutral']
d['web_validation']=json.loads((R/'viewer-r7-validation.json').read_text(encoding='utf8'))
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
model=(R/'Carrillo_core_rebuild_R7.blend').as_posix();manifest=(R/'core-r7-manifest.json').as_posix()
entry=f'''## R7 眼窝、下眼睑与下颌下巴调整 2026年10月13日

作者指出眼窝、下眼睑差异较大，下颌角和下巴仍不符。在 R6 上联合调整眼球与眼睑深度，区分下睑缘、薄弧面和眶下过渡；局部修改下颌后方转折及下巴侧面、底部体积。修正试调中产生的外眼角尖折，并在复核后减弱下睑沟槽。保存 [R7 Blender 工程](<{model}>)、[复核记录](<{manifest}>)及[八种视图的新旧对照](http://127.0.0.1:8849/sculpt-comparison.html)。R6 工程和 GLB 校验未改变，[R6 旧预览](http://127.0.0.1:8849/model-r6.html)保留。

**状态：可检查的局部结构修订，人物相似度仍未通过，待作者评价。** 下睑包覆比 R6 清楚，下巴侧面稍少鼓，颌角改善较小；眼周尚未达到 T22 的结构与神态。原贴图包含摄影明暗，现有发型也未获认可。去贴图检查、浏览器功能验证及局部网格方向检查不能替代身份判断。

'''
for p in [R.parent/'README_卡瑞洛视觉锚点.md',R.parent.parent/'00_素材登记总表.md']:
 s=p.read_text(encoding='utf8');heading='## R7 眼窝、下眼睑与下颌下巴调整 2026年10月13日'
 if heading not in s:
  first,rest=s.split('\n',1)
  # Preserve the R5-to-R6 comparison destination in the older R6 entry.
  marker='## 核心面部重建 2026年10月13日';cut=rest.find(marker)
  if cut>=0:rest=rest[:cut].replace('http://127.0.0.1:8849/sculpt-comparison.html','http://127.0.0.1:8849/sculpt-comparison-r6.html')+rest[cut:]
  p.write_text(first+'\n\n'+entry+rest.lstrip('\n'),encoding='utf8')
print('R7 records updated; R6 hashes intact.')
