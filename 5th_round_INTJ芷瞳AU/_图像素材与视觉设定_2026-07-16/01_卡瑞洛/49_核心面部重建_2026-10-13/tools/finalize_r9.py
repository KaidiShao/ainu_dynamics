import pathlib,json,hashlib
R=pathlib.Path(__file__).resolve().parents[1]
for e in json.loads((R/'checksums-r8.json').read_text(encoding='utf-8-sig')):
 assert hashlib.sha256(pathlib.Path(e['Path']).read_bytes()).hexdigest().upper()==e['Hash'],'Previous R8 native file changed'
hashes=[{'Path':str(R/f),'Hash':hashlib.sha256((R/f).read_bytes()).hexdigest().upper()} for f in ['Carrillo_core_rebuild_R9.blend','carrillo-core-r9.glb']]
(R/'checksums-r9.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2),encoding='utf8')
p=R/'core-r8-manifest.json';old=json.loads(p.read_text(encoding='utf8'));old['status']='Author rejected the nasal type; retained as prior working model.';old['subsequent_author_feedback']='我感觉你这两个人的鼻型就不一样 T22是鼻梁也比较高而且鼻翼窄的 你这个不对';p.write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding='utf8')
p=R/'review-r8.json';old_review=json.loads(p.read_text(encoding='utf8'));old_review['identity_status']='Subsequently rejected by the author: nasal type is incorrect; T22 has a higher bridge and narrower alae.';old_review['review_correction']='Earlier directionally-closer and no-further-alar-narrowing judgments were not supported by the author evaluation and are superseded by the R9 correction.';p.write_text(json.dumps(old_review,ensure_ascii=False,indent=2),encoding='utf8')
p=R/'core-r9-manifest.json';d=json.loads(p.read_text(encoding='utf8'));d['status']='Nasal form revision following author correction; waiting for author evaluation, not a validated match.'
d['preservation']='R8 native blend and GLB SHA256 unchanged; versioned R8 preview retained.'
d['web_validation']=json.loads((R/'viewer-r9-validation.json').read_text(encoding='utf8'))
if (R/'review-r9.json').exists():d['review']=json.loads((R/'review-r9.json').read_text(encoding='utf8'))
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
model=(R/'Carrillo_core_rebuild_R9.blend').as_posix();manifest=(R/'core-r9-manifest.json').as_posix()
entry=f'''## R9 按作者纠正重调鼻型 2026年10月13日

**作者明确否定 R8 鼻型：T22 鼻梁更高、鼻翼更窄；差异不是单纯鼻尖宽度。** 上一轮“鼻翼只轻调”的方向判断撤回，R8 不作为鼻型还原依据。

R9 在同一网格上分开调整鼻根至鼻梁中段的前突，以及鼻翼连同鼻孔缘的宽度，保留鼻尖核心。新增 R8/R9 同机位的去贴图正侧面，配合正面和转面检查。保存 [R9 Blender 工程](<{model}>)、[复核记录](<{manifest}>)、[新旧鼻型对照](http://127.0.0.1:8849/sculpt-comparison.html)及[T22 鼻部对照](http://127.0.0.1:8849/comparison.html?region=nose)。R8 工程与 GLB 哈希未改变，保留用于回溯。

**状态：按纠正方向制作的鼻型试稿，未获得作者认可，不能把高度/宽度已改变等同于匹配 T22。** 参考图不提供精确深度，最终仍需结合整体鼻型和多视角判断。

'''
for p in [R.parent/'README_卡瑞洛视觉锚点.md',R.parent.parent/'00_素材登记总表.md']:
 s=p.read_text(encoding='utf8')
 if '## R9 按作者纠正重调鼻型 2026年10月13日' not in s:
  first,rest=s.split('\n',1);cut=rest.find('## R7 眼窝、下眼睑与下颌下巴调整')
  if cut>=0:rest=rest[:cut].replace('http://127.0.0.1:8849/sculpt-comparison.html','http://127.0.0.1:8849/sculpt-comparison-r8.html').replace('http://127.0.0.1:8849/comparison.html','http://127.0.0.1:8849/comparison-r8.html')+rest[cut:]
  p.write_text(first+'\n\n'+entry+rest.lstrip('\n'),encoding='utf8')
print('R9 archived; R8 nose rejection recorded; previous native hashes intact.')
