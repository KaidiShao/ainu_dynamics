---
asset_id: MC_FACE_DERIVED_002
parent_asset_id: MC_FACE_REF_001
character: 马尔切洛·卡瑞洛
asset_type: face_state_derivative
status: selected_state_candidate
usage: pregnancy_care_private_attention
identity_authority: original_reference_only
sha256: 699BC905002CEEB009542DE50F1DDD76EEE21FBDC0C87BAB89A7F2FECD74B1AF
---

# MC_FACE_DERIVED_002｜状态候选评估

## 1. 生成目标

重新从原图开始，以更保守的方式减少部分歪头、把视线移向房间里的具体对象、保持原图嘴唇和不对称，避免第一张派生图的似笑非笑与标准正脸漂移。

## 2. 作者反馈

> 这个好像好点，但是有点微妙的可爱。

作者随后询问它与原图是否像同一个人。当前结论为：第一眼可被接受为同一角色，并排细看仍未达到严格同一身份锚点的程度。

## 3. 评估结论

| 项目 | 结果 |
|---|---|
| 普通故事连续性 | 约8/10；多数观者可接受为同一角色 |
| 严格身份一致性 | 约6.5—7/10；不能与原图平级 |
| 情绪状态 | 高度适合孕后私下等待回应 |
| 外部权力场 | 不适合；显得年轻、无措并带微妙可爱 |
| 最终状态 | `SELECTED_STATE_CANDIDATE / NOT_IDENTITY_ANCHOR` |

## 4. “微妙可爱”的来源

- 视线侧移较多，像在确认芷瞳有没有回应；
- 眉间完全松开，眼睛比原图稍圆；
- 头仍略偏，像在认真听她说话；
- 嘴唇柔和，没有第一张的隐含微笑；
- 额前卷发较蓬松，削弱锋利感；
- 他不再求感情保证，而是在等一个允许自己做点实际事情的小许可。

这类可爱不是卡瑞洛的公共属性，而是芷瞳可能看见、卡瑞洛自己并不知道已经露出的无措。

## 5. 与原图的身份关系

相似部分：

- 深色微卷发、蓝灰眼睛；
- 长而清晰的脸型；
- 高鼻梁、克制唇形；
- 整体年龄与南欧视觉方向。

漂移部分：

- 眼睛更圆、更显年轻；
- 鼻尖与鼻翼轻微变化；
- 下唇、下巴和下颌转折不完全一致；
- 头发更蓬，改变额头与脸型比例；
- 原图的不对称仍被模型部分标准化。

因此：

```text
面孔身份只继承 MC_FACE_REF_001。
MC_FACE_DERIVED_002 只提供视线方向、头部姿态和孕后私下无措感。
不得用它覆盖原图的眼型、鼻尖、下颌、发量、肩宽或身体比例。
```

## 6. 推荐使用场景

接口名称：`MC_STATE_PREGNANCY_CARE_002`。

适合早孕照顾制度逐渐形成以后：他坐在不远处，刚问完一个很小的实际问题，没有催促，只观察她是否愿意回应。请求对象不是“你还爱不爱我”，而是“你愿不愿意告诉我，现在能为你做什么”。

不适合：

- 对外家族事务；
- 公开权力场；
- 冷酷审讯或威胁；
- 任何把微妙可爱写成撒娇、讨好或降低其判断力的场景。

## 7. 生成信息

- 生成工具：Codex内置 imagegen，`identity-preserve`编辑。
- 生成日期：2026-07-16。
- 父素材：`MC_FACE_REF_001`，未使用第一张派生图作为父素材。
- 输出尺寸：1122×1402 PNG。
- 原始生成文件：`exec-30220c29-f8cb-4840-8f7b-10503c77a761.png`。

### 完整提示词

```text
Make an extremely conservative edit of the exact same man. Preserve at least 90 percent of the original image and identity. Remove only the restrained pleading from his expression and replace it with quiet observation and a judgment already completed. He is not smiling, threatening, posing, or performing coldness.

Lock exactly the original face length, narrow lower face, jaw width and angle, eyebrow thickness and slope, eye shape and spacing, eyelids, nose bridge and tip, nostrils, philtrum, lip shape and asymmetry, cheekbones, ears, apparent age, shoulder width, coat, body size, crop, camera distance, background, dark naturally wavy hair, blue-gray eyes, warm ivory skin, and realistic skin texture. Do not redesign, normalize, beautify, symmetrize, standardize, or make a fashion-model front face.

Reduce the original head tilt by approximately one third while keeping the original three-quarter orientation. Shift his gaze only 5–10 degrees away from the camera toward a specific person in the room. Keep brow and forehead relaxed, with quiet focus in the lower eyelids and no predatory tension. Close only one additional shirt button. Preserve the hairstyle except for at most one or two loose strands.

He has not rushed to answer. He has already understood and judged the situation. His face is neutral, human, and alert. Authority comes from stillness and certainty, not menace. No hidden joke, concealed pleasure, implied threat, smirk, almost-smile, smiling eyes, seductive expression, anger, glare, blankness, predatory gaze, wider jaw, thicker eyebrows, rounder eyes, changed nose tip, more symmetrical lips, broadened shoulders, fashion campaign, mafia styling, Nordic styling, added jewelry, text, logos, signatures, platform marks, or watermarks.
```

