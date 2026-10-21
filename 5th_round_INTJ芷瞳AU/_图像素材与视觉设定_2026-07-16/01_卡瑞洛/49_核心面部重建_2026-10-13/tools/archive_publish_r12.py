import pathlib,json,hashlib,shutil
R=pathlib.Path(__file__).resolve().parents[1];MC=R.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
old=json.loads((R/'checksums-r9.json').read_text(encoding='utf-8-sig'))
for item in old:assert sha(pathlib.Path(item['Path']))==item['Hash'],'R9 asset changed'
refs={
'T22':MC/'37_眼色局部统一_2026-10-11/MC_STATE_T22_T19正面_浅蓝灰虹膜校准_v22.png',
'P14':MC/'29_正侧下巴衔接统一_2026-10-10/MC_ANGLE_P14_浅蓝灰原侧光_唇颏过渡轻统一_v14.png',
'F03':MC/'28_认可正面下巴轻校准_2026-10-09/MC_FRONT_F03_浅蓝灰柔光_下巴凹痕轻校准_v1.png'}
expected={'T22':'372FA2CDD803644135C0A730EC6DA25934F99F2594B4C7B358365857F92EF5B1','P14':'9806117B7EE4ED7B8B180FCF21FA5D355548EE779744267928739BB1923110D6','F03':'85DD3796B705BCC0B4ED8074D8095757143E2861E1A784C31C606C00DD950F31'}
for name,p in refs.items():assert sha(p)==expected[name],name+' changed'
qa=json.loads((R/'viewer-r12-validation.json').read_text());audit=json.loads((R/'geometry-audit-r12.json').read_text())
assert not qa['errors'] and not qa['failed']
assert audit['finite'] and not audit['degenerate_triangles_under_1e-9'] and not audit['inconsistent_shared_edge_winding'] and not audit['nonmanifold_edges_over_two_faces']
report={
'status':'R12G 保留为当前工作版本。没有标记为作者认可或最终身份还原。',
'request':'用户要求在发现明显缺陷后自主继续迭代，不能以自查未过为理由停止。',
'selected_native':'Carrillo_core_rebuild_R12.blend','selected_source':'Carrillo_core_rebuild_R12G.blend',
'progress':[
'R11 重建眼周与口周连续网格；移除内部重叠面，修复绕序、接缝与局部褶皱。',
'R11 比较后保留 L；M 的规则前额卷发效果不佳，淘汰。',
'R12 引入本机运行的 3DDFA_V2 深度先验，先用 T22 关键点校准正面投影，再把深度融合进真实头部网格。',
'R12A 平面插值把鼻孔内部与外表面混在一起，出现凹坑，淘汰；R12B 改为沿原三角表面射线取样。',
'R12C/D 修正细分后上睑漂移；重做细眉毛流；清理旧额头贴图痕迹；平顺唇下至颏上起伏。',
'R12D/F 收回鼻尖上方过量鼓面，保留鼻尖核心圆量、高鼻梁和窄鼻翼。',
'R12E 重调既有前发束与暗棕毛发材质，没有替换面部。',
'R12F/G 由 P14 相机像素射线定位外眦下方褶脊，修正其局部深度；45度机位继承 T22 的俯仰和滚转。',
'R12H 尝试从 T22 估计并减弱照片照明的顶点材质，实际放大斑驳和阴影，淘汰。当前仍用 F03 基础材质与 T22 虹膜。'],
'independent_review':{
'reviewer':'review_carrillo_angle',
'labio_mental':'D 相对 B 的多道波浪状凹凸基本消失，变成连续浅凹面。',
'nasal':'鼻型局部改善；仍有鼻背下段偏饱满的差异，不能宣称完全复现。',
'outer_canthus_G':'短脊比 D 减弱，接向颧面的过渡较缓；残留浅褶与小凹口，没有新增尖角、裂口或明显穿插。可作为当前局部迭代保留，不宜继续单点向内挖。',
'scope':'上述结论不代表整体身份匹配。'},
'limitations':['尚未达到 T22 的完整人物辨识和神态，不能宣称已经完全修完。','头发、耳廓、皮肤及眼睑细节仍有模型感。','鼻体与眶下的细节相似度仍有限；单张照片的深度估计是辅助约束，不是真实三维扫描。','T22 与 P14 分别生成，不能据此证明二者完全对应同一套三维结构。','浏览器简化发丝与角膜，光照不同于 Blender；素模检查与原生渲染单独保留。'],
'validation':qa,'geometry':audit,
'local_depth_source':{'repository':'https://github.com/cleardusk/3DDFA_V2','local_path':str(R.parents[3]/'_tools/3DDFA_V2'),'inference':'Local CPU PyTorch; reference images not uploaded.'},
'references':[{'name':k,'path':str(p),'sha256':sha(p)} for k,p in refs.items()],
'preservation':{'R9_native_and_glb_unchanged':True,'references_unchanged':True},
'selected_files':[{'path':str(p),'sha256':sha(p)} for p in [R/'Carrillo_core_rebuild_R12.blend',R/'carrillo-core-r12.glb']],
'publication':'Current work preview updated to R12; approved reference portraits remain unchanged.'}
(R/'review-r11-r12.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
# Preserve the old entry pages before making the actual repaired model visible.
backup=R/'preview-r9-preserved';backup.mkdir(exist_ok=True)
for name in ['index.html','comparison.html','sculpt-comparison.html']:
 if (R/name).exists() and not (backup/name).exists():shutil.copy2(R/name,backup/name)
mapping={'model-r12-candidate.html':'index.html','comparison-r12-candidate.html':'comparison.html','sculpt-comparison-r12-candidate.html':'sculpt-comparison.html'}
for src,dst in mapping.items():
 s=(R/src).read_text(encoding='utf8')
 s=s.replace('/model-r12-candidate.html','/').replace('/comparison-r12-candidate.html','/comparison.html').replace('/sculpt-comparison-r12-candidate.html','/sculpt-comparison.html')
 s=s.replace('/viewer-r12-candidate.js?v=11','/viewer-r12-candidate.js?v=12-final')
 (R/dst).write_text(s,encoding='utf8')
entry=f'''## R11–R12 自主重建与深度校准 · 2026年10月13日

当前预览已更新为 R12G，工程保存为 `49_核心面部重建_2026-10-13/Carrillo_core_rebuild_R12.blend`。重建眼周与口周连续网格，引入本地运行的 3DDFA_V2 深度先验，逐轮修正鼻体、外眦下方褶脊、唇下至颏上起伏；失败候选与原始参考均保留。

**这是当前工作版本，未标记为作者认可或最终身份还原。** 几何完整性与浏览器功能检查通过；独立复查认可唇颏和外眦的局部改善，不等同于整体相似度通过。鼻体、眼周细节、发束与气质仍有差距。T22 材质试验 R12H 因放大阴影和斑驳而淘汰。参见[完整自查与候选记录](<{(R/'review-r11-r12.json').as_posix()}>)。

'''
for p in [MC/'README_卡瑞洛视觉锚点.md',MC.parent/'00_素材登记总表.md']:
 s=p.read_text(encoding='utf8')
 if '## R11–R12 自主重建与深度校准' not in s:
  first,rest=s.split('\n',1);p.write_text(first+'\n\n'+entry+rest.lstrip('\n'),encoding='utf8')
print(json.dumps({'current':'R12G','originals_preserved':True,'model_test':'passed','final_likeness_approved':False},ensure_ascii=False))
