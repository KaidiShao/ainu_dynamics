import pathlib,json,hashlib
R=pathlib.Path(__file__).resolve().parents[1]
for e in json.loads((R/'checksums-r7.json').read_text(encoding='utf-8-sig')):
 assert hashlib.sha256(pathlib.Path(e['Path']).read_bytes()).hexdigest().upper()==e['Hash'],'Previous R7 native file changed'
hashes=[{'Path':str(R/f),'Hash':hashlib.sha256((R/f).read_bytes()).hexdigest().upper()} for f in ['Carrillo_core_rebuild_R8.blend','carrillo-core-r8.glb']]
(R/'checksums-r8.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2),encoding='utf8')
p=R/'core-r8-manifest.json';d=json.loads(p.read_text(encoding='utf8'))
d['status']='Locally revised working model; overall character likeness not established; awaiting author evaluation.'
d['preservation']='R7 blend and GLB verified unchanged by SHA256. Previous R7 web preview versioned.'
d['alignment']='Same camera; retained R7 image alignment. No new automatic R8 landmark metrics.'
d['validation']=json.loads((R/'viewer-r8-validation.json').read_text(encoding='utf8'))
if (R/'review-r8.json').exists():d['review']=json.loads((R/'review-r8.json').read_text(encoding='utf8'))
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
model=(R/'Carrillo_core_rebuild_R8.blend').as_posix();manifest=(R/'core-r8-manifest.json').as_posix()
entry=f'''## R8 下鼻梁、鼻尖及眼周下颌调整 2026年10月13日

作者指出 R7 眼周与下颌角仍有差别，T22 鼻子更窄。本轮重点收窄下鼻梁连接鼻尖的部分与鼻尖两侧，鼻翼只轻调；保留鼻尖前后位置与自然圆度。眼周整理眉弓下表面至上睑折面的过渡，保留 R7 下睑支撑。下颌分别整理侧面与颌下平面交接，避免整体缩窄。保存 [R8 工程](<{model}>)、[复核与验证记录](<{manifest}>)、[十种同机位新旧视图](http://127.0.0.1:8849/sculpt-comparison.html)，[T22 对齐页](http://127.0.0.1:8849/comparison.html)增加“鼻部”放大。R7 原始工程及 GLB 哈希未改变。

**状态：局部修订工作稿，整体人物相似度未通过，待作者评价。** 鼻部变化最集中，眼周与下颌改善较轻。参考侧光会强化细鼻观感，不能把全部明暗边界当作几何轮廓；仍需结合去贴图与转面判断，不替换认可视觉锚点。

'''
for p in [R.parent/'README_卡瑞洛视觉锚点.md',R.parent.parent/'00_素材登记总表.md']:
 s=p.read_text(encoding='utf8')
 if '## R8 下鼻梁、鼻尖及眼周下颌调整 2026年10月13日' not in s:
  first,rest=s.split('\n',1);cut=rest.find('## R6 下颌、眼眶与鼻口衔接调整')
  if cut>=0:rest=rest[:cut].replace('http://127.0.0.1:8849/sculpt-comparison.html','http://127.0.0.1:8849/sculpt-comparison-r7.html')+rest[cut:]
  p.write_text(first+'\n\n'+entry+rest.lstrip('\n'),encoding='utf8')
print('R8 records saved; R7 verified unchanged.')
