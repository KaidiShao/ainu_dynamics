---
task: MC_FACE_DERIVED_002_EYE_MICROCAL
date: 2026-07-18
recommended_existing_image: MC_FACE_DERIVED_002
selected_new_micro_edit: none
selected_new_alternate_state: MC_FACE_STATE_003
r03_generated: false
---

# 左眼微调｜最终推荐与使用边界

## 结论

两轮新图均未通过单眼微调标准。作为原“等待回应”状态，当前最佳结果仍是未经修改的：

`00_基准图/MC_FACE_DERIVED_002_EYE_CAL_BASELINE.png`

它是原文件`MC_FACE_DERIVED_002_孕后私下等待回应_SELECTED_STATE_CANDIDATE_v001.png`的逐字节副本。原文件继续保持：

```text
DERIVED
SELECTED_STATE_CANDIDATE
MC_STATE_PREGNANCY_CARE_002
NOT_IDENTITY_ANCHOR
```

## 为什么保留底图

底图画面左眼略窄，但这项不完整恰好与低唤醒、已经等待片刻、不催促的状态相容。两张微调图虽然让侧视更清楚，却同时：

- 把双眼变得更圆、更亮、更对称；
- 将安静等待提高为轻微警觉；
- 改写鼻唇、下颌、肤质、头发、衣装和背景；
- 将卡瑞洛偏窄、略长而清晰的骨相变成圆方标准男模脸。

因此“眼睛更清楚”没有抵消身份与状态损失。

## 新图使用限制

### R01

只可作为：

```text
OVEROPEN_UPPER_BOUND
NEGATIVE_REFERENCE
```

禁止继承其双眼开合、下颌、鼻尖、唇线、肤质或发型细节。

### R02

作为单眼微调轮次，它只能标记为：

```text
FAILED_MICRO_EDIT
PROCESS_DRIFT
NOT_SINGLE_PARAMETER_SUCCESS
NOT_IDENTITY_ANCHOR
```

它可以说明“比R01收回一些仍不够”，但不能作为左眼正确形态、身份或后续身份生成输入。

作者复看后，同时认可同一张图作为独立状态：

```text
MC_FACE_STATE_003
AUTHOR_SELECTED_ALTERNATE_STATE_CANDIDATE
PRIVATE_ATTENTIVE_FOCUS
CHILD_IF
PROCESS_DRIFT
NOT_IDENTITY_ANCHOR
```

这里的卡瑞洛不是继续低唤醒地等待，而是已经把全部注意力落在芷瞳身上。他不催促、不索取，却让她清楚知道自己的停顿、呼吸与细小反应正在被看见。专注本身构成关系压力，但不是威胁、审讯、哀求或外部权力表演。

状态图保存在：

`02_状态采用/MC_FACE_STATE_003_私下专注凝视_AUTHOR_SELECTED.png`

它与R02逐字节相同。另存的目的只是隔离技术记录和语义用途，不代表删除`PROCESS_DRIFT`。

## 为什么没有R03

R01与R02都不是有效局部编辑，无法充当精确插值端点。第三轮不会是可靠的2%—3%中间值，只会是另一张随机重绘脸，因此按预设停止规则不生成。

## 后续建议

当前不建议继续用整图生成方式磨这一只眼。若以后确有局部遮罩、确定性修图或人工眼睑微调工具，再从原状态图进行像素级局部处理；在此之前，保留底图比继续生成更安全。

本任务没有建立新身份锚点，也没有替换原状态图。`MC_FACE_STATE_003`当前先锁在`CHILD_IF／亲密私下状态`；若要用于`COMMON`，必须另行取得作者裁决，不得自动进入`MAIN`。
