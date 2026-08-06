---
task: MC_BODY_R03_FUSION
date: 2026-07-17
generated_rounds: 3
maximum_authorized_rounds: 6
stopped_early: true
primary_finalist: MC_BODY_FUSION_R03
secondary_finalist: MC_BODY_FUSION_R01
identity_anchor_unchanged: MC_FACE_REF_001
body_anchor_created: false
---

# R03结构融合校准｜最终推荐与使用边界

## 1. 结果

流程在融合R03达到完整候选门槛后提前停止，共生成三轮：

| 轮次 | 身份 | 身体 | 颈肩 | 站姿 | 手 | 中性 | 保守总分 | 定位 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| R01 | 33 | 18 | 13 | 9 | 8 | 4 | 85 | 第二推荐；身体结构备选 |
| R02 | 34 | 18 | 13 | 8 | 8 | 4 | 85 | 研究保留 |
| R03 | 35 | 18 | 14 | 9 | 8 | 5 | 89 | 第一推荐；达到停止门槛 |

三轮均无视觉硬淘汰。三轮都发生了不同程度的全图重生，因此均保留`PROCESS_DRIFT / NOT_SINGLE_PARAMETER_SUCCESS`标记。

## 2. 第一推荐｜MC_BODY_FUSION_R03

文件：

```text
01_轮次图/MC_BODY_FUSION_R03.png
```

适合提供：

- 当前最接近原图的全身身份统一效果；
- R03较自然的颈长和肩颈坡度；
- 稳定的胸廓—骨盆叠放；
- 健康修长但不单薄的185 cm男性体量；
- 可接受的窄掌和长指方向；
- 中性、无权力表演的技术参考状态。

仍有不足：

- 下颌—下巴仍比最初原图略宽、略方；
- 嘴唇略薄；
- 眉眼不对称已经恢复，但仍比原图稍规整；
- 双膝略直；
- 画面左手掌面仍略宽，部分指缘偏软。

定位：

```text
PRIMARY_FUSION_CANDIDATE
PROVISIONAL
PROCESS_DRIFT
NOT_BODY_ANCHOR
NOT_IDENTITY_ANCHOR
AUTHOR_SELECTION_REQUIRED
```

## 3. 第二推荐｜MC_BODY_FUSION_R01

文件：

```text
01_轮次图/MC_BODY_FUSION_R01.png
```

适合提供：

- 较自然的头肩与重心关系；
- 清瘦但不脆弱的整体体量；
- 可接受的颈肩与站姿备选；
- 与R03不同的自然全身重生样本。

限制：

- 身份专审只有33/40；
- 下半脸横向扩展并方正化；
- 下颌角和下巴更接近商业男模标准化；
- 只能作为身体结构与自然站姿备选，不能作为脸部参考。

定位：

```text
SECONDARY_BODY_GEOMETRY_CANDIDATE
PROVISIONAL
PROCESS_DRIFT
NOT_BODY_ANCHOR
NOT_IDENTITY_ANCHOR
NOT_IDENTITY_REFERENCE
AUTHOR_SELECTION_REQUIRED
```

## 4. R02为什么没有入选

R02确实修窄了R01的下半脸，但同时把眼睛放大、变圆、变亮，使眉线更高、更对称，人物重新趋向标准AI俊脸；站姿也比R01与R03更像正面男模陈列。它保留为下颌修正研究，不进入最终两张。

## 5. 锚点边界

`MC_FACE_REF_001`继续是唯一脸部身份锚点。

本轮没有建立：

```text
BODY_ANCHOR
IDENTITY_ANCHOR
PROVISIONAL_BODY_ANCHOR
```

原因：

1. 三张都是单一正面角度；
2. 内置生成器存在全图重生；
3. 侧脸、后脑、背面、真实肩宽、胸背深度尚未核验；
4. 手部仍只达到可接受下限；
5. 尚未获得作者对最终两张的明确采用裁决。

## 6. 下一阶段接口

如果作者采用R03的总体方向，下一阶段应先生成同一结构的三分之四与侧面核验，而不是直接进入成品服装图。

多角度阶段仍需：

- 原图作为唯一脸部身份锚点；
- 融合R03只约束正面体量、颈肩和站姿方向；
- 不从单张正面图推导未见的侧脸、后脑或背部；
- 185 cm继续作为文字常量；
- 通过多角度后才讨论`PROVISIONAL_BODY_ANCHOR`。

## 7. 给作者的最短选择说明

```text
R03：脸、颈肩、身体和站姿最均衡；当前第一推荐。

R01：身体自然，但脸部下颌偏宽方；只作身体结构备选。
```

## 后续头身比例复核｜2026-07-17

作者随后注意到融合R01与融合R03可能存在轻微头大感。独立完成的`05_头身比例微调_2026-07-17`表明：

- 只收紧发量的测试能小幅减轻头大感，但没有实质超过本轮融合R03；
- “完整头部缩小2%”测试发生严重全局缩放与构图漂移，无法作为有效证据；
- 两项测试不构成成功的互补修正，因此没有生成综合版。

本文件的第一推荐`MC_BODY_FUSION_R03`继续有效。它的头身比例位于真人合理范围偏大端，但仍比未经验证的小头版本安全。
