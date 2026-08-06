---
asset_id: MC_FACE_DERIVED_001
parent_asset_id: MC_FACE_REF_001
character: 马尔切洛·卡瑞洛
asset_type: face_state_derivative
status: rejected_expression_drift
usage: negative_reference_only
sha256: 9648E5F5A3F4577962E234B37A3DB602B68EA56538D3513A8CAA8B178771C78D
---

# MC_FACE_DERIVED_001｜负面样本评估

## 1. 生成目标

尝试把原图中冷战后期／孕后照顾期的克制请求，转换成卡瑞洛面对外部权力场时平静、准确、完整控制的状态，同时保持同一张脸。

## 2. 作者反馈

> 有点似笑非笑，表情有点瘆人。

作者同意该图不应作为正向基准。

## 3. 评估结论

| 项目 | 结果 |
|---|---|
| 状态转换 | 约85%；头位、衣领和整体秩序明显改变 |
| 身份保持 | 约65—70%；只能视为相似选角，不能视为严格同一张脸 |
| 卡瑞洛气质 | 部分成立，但滑向“漂亮的深色贵公子／礼貌威胁” |
| 最终状态 | `REJECTED_EXPRESSION_DRIFT` |

## 4. 成功部分

- 头位端正，外部完整感增强；
- 衣领和肩部秩序更明确；
- 没有北欧金发化、黑帮壮汉化或愤怒瞪视；
- 证明“状态转换”在技术上可行。

## 5. 失败部分

- 嘴角被轻微抬高，形成似笑非笑；
- 双眼完全正对镜头，产生等待观众不安的瘆人感；
- 面孔被高度对称化，失去原图的具体人与关系对象；
- 下颌变宽、变方；
- 眉毛更平、更浓，眼睛略圆；
- 鼻尖、鼻翼、嘴唇与下巴发生身份漂移；
- 外套扩大肩背，使未锁定体量被误当成事实；
- 更像时尚人物海报，而不是一个正在判断具体局势的人。

## 6. 禁止继承

后续提示词必须明确禁止：

- lifted mouth corner / smirk / half-smile / suppressed smile；
- 完全正对镜头的固定凝视；
- 面孔对称化和标准正脸美化；
- 加宽下颌、加粗眉毛、增大鼻尖；
- 扩大肩背与外套；
- 用隐含威胁代替无需表演的权力。

本图只能作为负面校准样本，不得进入人物正向参考、多图身份参考或最终服装图。

## 7. 生成信息

- 生成工具：Codex内置 imagegen，`identity-preserve`编辑。
- 生成日期：2026-07-16。
- 父素材：`MC_FACE_REF_001`。
- 输出尺寸：1122×1402 PNG。
- 原始生成文件：`exec-852ad491-6e58-41a7-9c39-730ac642ee92.png`。

### 完整提示词

```text
Create a minimal edit of the exact same man, changing only his emotional and grooming state from restrained pleading to calm external authority. This must remain unmistakably the same individual, not a redesigned or merely similar face.

Preserve aggressively the exact face length, skull proportions, eyebrow shape, eye spacing, eye shape, nose, lips, cheekbones, jawline, ears, apparent age, dark naturally wavy hair, blue-gray eyes, warm ivory skin direction, head size, camera distance, realistic skin texture, and lean facial structure.

Straighten the slightly tilted head into a natural upright position. Change the gaze to level, quiet, precise, and already finished judging the situation. Remove restrained pleading and melancholy while keeping him human. Do not make him angry, glaring, blank, cruel, or expressionless. Tidy the hair around the forehead slightly while retaining natural dark waves. Close and refine the shirt collar modestly; keep the dark jacket and restrained, precise clothing. Shift the lighting to neutral, low-saturation indoor light while retaining a dark understated interior.

Southern European old-family dangerous restraint; authority that does not need display; beautiful but not soft, controlled but not brutal.

Avoid face drift, a different lookalike, beauty-filter skin, younger or older appearance, added muscles, exaggerated square jaw, blond hair, Nordic transparent-pale styling, mafia-poster aggression, seductive open shirt, fashion-ad posing, heroic low angle, extra jewelry, logos, text, signatures, platform marks, or watermarks.
```

