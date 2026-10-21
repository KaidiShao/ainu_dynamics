import pathlib,json,hashlib
R=pathlib.Path(__file__).resolve().parents[1];MC=R.parent
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
old=json.loads((R/'checksums-r9.json').read_text(encoding='utf-8-sig'))
for e in old:assert digest(pathlib.Path(e['Path']))==e['Hash'],'R9 preservation failed'
refs={
'T22':MC/'37_眼色局部统一_2026-10-11/MC_STATE_T22_T19正面_浅蓝灰虹膜校准_v22.png',
'P14':MC/'29_正侧下巴衔接统一_2026-10-10/MC_ANGLE_P14_浅蓝灰原侧光_唇颏过渡轻统一_v14.png',
'F03':MC/'28_认可正面下巴轻校准_2026-10-09/MC_FRONT_F03_浅蓝灰柔光_下巴凹痕轻校准_v1.png'}
expected={'T22':'372FA2CDD803644135C0A730EC6DA25934F99F2594B4C7B358365857F92EF5B1','P14':'9806117B7EE4ED7B8B180FCF21FA5D355548EE779744267928739BB1923110D6','F03':'85DD3796B705BCC0B4ED8074D8095757143E2861E1A784C31C606C00DD950F31'}
for key,p in refs.items():assert digest(p)==expected[key],key+' preservation failed'
iterations=[
{'version':'R10A','changes':'重调正面投影对应、眼周、颧颌、鼻唇，重建眼球与发束。','self_review':'眼球大块反光、灰色发丝、唇部鼓包；3 个局部三角形发生超过 90 度的法线变化。淘汰。'},
{'version':'R10B','changes':'修复局部翻转，拆分角膜与虹膜，修正鼻翼横向拟合。','self_review':'法线检查通过；仍有突眼、眼窝与眼睑不协调及发顶反光问题。'},
{'version':'R10C','changes':'眼球与眼周共同后移、唇面整理、下颌与下巴支撑调整。','self_review':'确认基础网格含内部眼窝面，旧的一些控制点不位于实际可见表面；侧面关系仍不理想。'},
{'version':'R10D','changes':'改用可见上睑/睑沟/下睑表面，继续整理唇部、下颌、鼻尖与发根。','self_review':'灰白头皮漏出和局部唇下鼓包减轻；眼睛仍显得睁得过满。'},
{'version':'R10E','changes':'上睑覆盖、真实睫毛与眉部厚度、唇面第二次调整。','self_review':'回退会引起局部面翻转的位移后通过控制网格检查，仍未达到 T22 的眼周形态。'},
{'version':'R10F','changes':'发束方向与曲率重建，尝试毛发着色器。','self_review':'产生过亮发丝和眉毛；直接版本淘汰。'},
{'version':'R10 material revision','changes':'将毛发着色器贡献降低，眉毛材质独立，保存为 Carrillo_core_rebuild_R10.blend。','self_review':'材料改善，但浏览器去贴图暴露上睑/眼球干涉，因此未发布。'},
{'version':'R10G','changes':'在细分后表面排除眼球与可见眼睑干涉。','self_review':'正面干涉减轻，但 271 个三角形相对原表面法线旋转超过 90 度。明确淘汰，不能作为修复版本。'},
{'version':'R10H','changes':'保留原头部拓扑，缩减眼球前后深度并后移；保持正面眼色与虹膜投影大小。','self_review':'正面白色穿插减轻，但转面眼窝与睑缘仍不自然。仍未通过整体相似度自查。'}]
report={
'date':'2026-10-13',
'status':'内部自查未通过；本轮没有完成作者要求的足够相似的重建。',
'author_request':'全部修正，自主分析与迭代，不把仍有明显问题的试稿反复交给作者挑错。',
'iterations':iterations,
'verified_improvements':['眼球大块矩形高光受到抑制','保留较高鼻梁并对鼻翼及鼻尖两侧进行收窄','颧部—下颌—下巴衔接进行了多轮真实网格调整','局部唇面与唇下鼓包减轻','发束方向与发根覆盖更新','确认旧近侧面机位并不对应 P14；另建 P14 估计机位'],
'unresolved':['眼窝与上下睑的连续曲面及厚度仍不够自然；局部位移容易造成穿插或翻面','转面后的鼻唇深度、下巴与下颌关系没有充分复现参考','眉眼尚未稳定表达 T22 的冷峻审视','发束层次、耳部、皮肤表面仍有明显模型感'],
'conclusion':'当前以基础网格拟合、局部程序形变和照明照片贴图叠加的做法，没有达到可靠的人物还原。不能把技术检查通过或局部变好等同于身份匹配。接下来的有效工作需要重新建立关键眼周与口周的连续拓扑及深度约束，而非延续小幅高斯位移。',
'publication':{'public_preview':'R9 retained at http://127.0.0.1:8849/','promoted':False,'reason':'作者要求先自行排除明显问题；R10 系列仍未通过自查，因此不要求作者验收。','candidate_web_source':'Carrillo_core_rebuild_R10.blend before R10G/H; not the latest ocular-depth experiment.'},
'web_functional_test':json.loads((R/'viewer-r10-validation.json').read_text()),
'geometry_review':{'R10E':json.loads((R/'r10e-manifest.json').read_text()),'R10G_rejected':json.loads((R/'geometry-audit-r10g.json').read_text())},
'independent_agent_review':'Existing reviewer attempt failed with stream disconnect; no independent review received and none claimed.',
'preservation':{'R9_native_and_glb_unchanged':True,'references':[{'name':k,'path':str(p),'sha256':digest(p)} for k,p in refs.items()]},
'artifacts':[{'path':str(p),'sha256':digest(p)} for p in sorted(R.glob('Carrillo_core_rebuild_R10*.blend'))]
}
(R/'review-r10.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
(R/'checksums-r10-internal.json').write_text(json.dumps(report['artifacts'],ensure_ascii=False,indent=2),encoding='utf8')
# Keep archive navigation explicit that these are not approved replacements.
entry=f"""## R10 内部自查与未通过的迭代 · 2026年10月13日

本轮按作者要求独立进行多轮修改、渲染和对照，处理眼周、鼻唇、颧颌下巴、发束及材质。**未达到足够相似的交付标准，未替换正式预览，未请求作者继续逐项挑错。** [完整自查记录](<{(R/'review-r10.json').as_posix()}>)列明各候选的改动、失败原因、剩余问题与保存路径。

R10G 的细分后排除穿插方案出现 271 个三角形法线大幅翻转，已明确淘汰。R10H 正面眼球穿插减轻，但转面眼周仍不自然，也未认可。R9 工程、GLB 和 T22/P14/F03 原图哈希均未改变。R10 各试稿仅作研究与回溯，不能替换已认可的人物视觉锚点。

"""
for p in [MC/'README_卡瑞洛视觉锚点.md',MC.parent/'00_素材登记总表.md']:
 s=p.read_text(encoding='utf8')
 if '## R10 内部自查与未通过的迭代' not in s:
  first,rest=s.split('\n',1);p.write_text(first+'\n\n'+entry+rest.lstrip('\n'),encoding='utf8')
print(json.dumps({'status':report['status'],'iterations':len(iterations),'public_preview_unchanged':True,'original_hashes_verified':True,'review':str(R/'review-r10.json')},ensure_ascii=False))
