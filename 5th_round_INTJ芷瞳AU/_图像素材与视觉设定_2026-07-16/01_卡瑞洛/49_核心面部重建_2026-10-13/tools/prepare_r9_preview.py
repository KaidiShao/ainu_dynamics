import pathlib,json,re
R=pathlib.Path(__file__).resolve().parents[1]
names={'index.html':'model-r8.html','viewer.js':'viewer-r8.js','comparison.html':'comparison-r8.html','sculpt-comparison.html':'sculpt-comparison-r8.html'}
source={k:(R/k).read_text(encoding='utf8') for k in names}
for name,backup in names.items():
 p=R/backup
 if not p.exists():
  s=source[name]
  if name.endswith('.html'):s=s.replace('href="/"','href="/model-r8.html"').replace('href="/comparison.html"','href="/comparison-r8.html"').replace('href="/sculpt-comparison.html"','href="/sculpt-comparison-r8.html"').replace('/viewer.js?v=8','/viewer-r8.js?v=8')
  p.write_text(s,encoding='utf8')
s=source['viewer.js'].replace('r8.glb','r9.glb');(R/'viewer.js').write_text(s,encoding='utf8')
s=source['index.html'].replace('R8','R9').replace('r8-','r9-').replace('/viewer.js?v=8','/viewer.js?v=9').replace('R7 / R9','R8 / R9')
s=s.replace('下鼻梁、鼻尖与眼周下颌调整','高鼻梁与窄鼻翼试修')
s=s.replace('本轮收窄下鼻梁与鼻尖两侧，轻调鼻翼；整理上睑至眉弓的转折，以及下颌侧面与颌下的交接。','依据作者纠正，抬高鼻根至鼻梁中段的前突，并收窄鼻翼及相连鼻孔缘。新增鼻部正侧面对照，检查真实高度变化。')
(R/'index.html').write_text(s,encoding='utf8')
s=source['sculpt-comparison.html'].replace('R8','R9').replace('r8-','r9-').replace('R7','R8').replace('r7-','r8-')
s=s.replace('重点检查下鼻梁、鼻尖两侧、眼周与下颌转折。','检查鼻梁高度与鼻翼宽度。正侧面可直接比较鼻梁的前突。')
s=re.sub(r'<button data-view="eyes[^"]*"[^>]*>.*?</button>','',s)
s=s.replace('<button data-view="nose-side-neutral">鼻部转面 · 去贴图</button>','<button data-view="nose-side-neutral">鼻部转面 · 去贴图</button><button data-view="nose-profile-neutral">鼻部正侧面 · 去贴图</button>')
s=s.replace('下鼻梁与鼻尖两侧的收窄可在鼻部近景中检查。眼周与下颌变化较轻，请切换对应视图观察。','R8 的鼻型已被作者否定。R9 同时调整鼻梁前突和鼻翼形态，请分别看正面宽度与正侧面高度。')
(R/'sculpt-comparison.html').write_text(s,encoding='utf8')
a=json.loads((R/'likeness-alignment-r8.json').read_text(encoding='utf8'));model=a['images'].pop('R8');model['url']='/renders/core-r9-front.png';a['images']['R9']=model
a['status']='R9 nasal form revision; author approval pending.';a['alignment_method']='Same camera and retained R8 image alignment. No new R9 automatic landmark measurements.'
(R/'likeness-alignment-r9.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf8')
s=source['comparison.html'].replace('R8','R9').replace('likeness-alignment-r8.json','likeness-alignment-r9.json').replace('R7 / R9','R8 / R9')
s=s.replace('R9 收窄下鼻梁与鼻尖两侧，轻调鼻翼，并整理上睑至眉弓、下颌侧面至颌下的转折。人物相似度仍未通过。','上一轮 R8 的鼻型不符：T22 鼻梁更高、鼻翼更窄。R9 已按这两项重调，仍需核对，不能据此认定匹配。')
s=s.replace('function transform(ctx)',"const requestedRegion=new URLSearchParams(location.search).get('region');if(presets[requestedRegion])region=requestedRegion;document.querySelectorAll('[data-region]').forEach(b=>b.classList.toggle('active',b.dataset.region===region));\nfunction transform(ctx)")
(R/'comparison.html').write_text(s,encoding='utf8')
s=(R/'tools/verify_r8.cjs').read_text(encoding='utf8').replace('R8','R9').replace('r8','r9')
s=re.sub(r"const views=\[.*?\];","const views=['nose-neutral','nose-side-neutral','nose-profile-neutral','neutral','front-neutral','front','threequarter','near-profile'];",s)
(R/'tools/verify_r9.cjs').write_text(s,encoding='utf8')
(R/'Open_Carrillo_Core_R9.cmd').write_text((R/'Open_Carrillo_Core_R8.cmd').read_text().replace('R8','R9'),encoding='ascii')
print('R9 preview prepared; R8 preserved.')
