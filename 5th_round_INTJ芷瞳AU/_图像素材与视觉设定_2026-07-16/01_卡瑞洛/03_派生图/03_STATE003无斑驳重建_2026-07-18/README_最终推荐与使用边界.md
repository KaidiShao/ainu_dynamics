# `MC_FACE_STATE_003_CLEAN_REBUILD` 最终推荐与使用边界

```text
TASK_ID=MC_FACE_STATE_003_CLEAN_REBUILD
ACTUAL_ROUNDS=3
PASSED_ROUNDS=0
NO_CLEAN_STATE_REBUILD_PASS
GENERATION_METHOD_LIMIT_REACHED
THREE_CONSECUTIVE_LOCALITY_FAILURES
LOCAL_MASKED_REPAIR_RECOMMENDED
```

## 1. 最终结论

本次没有生成达到门槛的干净 `STATE_003` 重建图。

三轮均严格从输入 A＋输入 B 重新开始，对照 C 从未作为生成输入。R01使用完整身份保持提示词，R02只加强局部编辑边界，R03改用极短的纯几何提示。三种提示策略仍都使生成工具重新绘制整张人物区域，而不是只编辑目标上眼睑。

因此失败原因不是提示词仍不够长，也不是眼睛幅度尚未找到，而是当前整图生成式编辑方法无法可靠执行这一像素级局部任务。

## 2. 三轮裁决

| 轮次 | 总分 | 最有价值之处 | 主要失败 | 裁决 |
|---|---:|---|---|---|
| R01 | 82.5 | 三轮中皮肤最干净，目标专注状态仍有保留 | 非目标眼、双眉、鼻唇和下颌被重绘 | `BEST_FAILED_ATTEMPT / HARD_REJECT` |
| R02 | 69.5 | 验证加强局部边界仍无效 | 双眼更圆亮，目标眼过开，状态滑向警觉／可爱 | `HARD_REJECT` |
| R03 | 67.5 | 目标注意方向仍可辨 | 全脸重绘持续，双颊和颈部斑驳明显回归 | `HARD_REJECT` |

三轮共同触发：

```text
NON_TARGET_EYE_DRIFT
NON_TARGET_FACE_REGENERATION
PROCESS_DRIFT
NOT_LOCAL_RECONSTRUCTION_SUCCESS
```

## 3. 最佳失败轮次

`02_最终候选/MC_FACE_STATE_003_CLEAN_REBUILD_BEST_FAILED_R01_RESEARCH_ONLY.png`

这是 R01 的逐字节副本。它只能说明“从干净 B 出发可以得到接近 C 的注意强度，同时暂时减轻斑驳”；不能说明单眼局部编辑成功。

它不得作为：

- 新 `STATE_003`；
- 身份锚点；
- 后续衣装或背景编辑底图；
- 鼻唇、下颌、另一只眼或皮肤质地参考。

## 4. 保守语义参考

`02_最终候选/MC_FACE_STATE_003_CONSERVATIVE_SEMANTIC_REFERENCE_WITH_TEXTURE_DRIFT.png`

这是旧 `MC_FACE_STATE_003` 的逐字节副本，用于保留作者已经确认的关系语义。它继续承担：

```text
AUTHOR_SELECTED_SEMANTIC_STATE_REFERENCE
PRIVATE_ATTENTIVE_FOCUS
```

同时新增边界：

```text
HISTORICAL_TEXTURE_DRIFT_SOURCE
NOT_EDIT_BASE
NOT_IDENTITY_ANCHOR
```

它保住状态，但不解决斑驳；不得再直接用于换衣、换背景或其他整图派生。

## 5. 干净编辑底图

输入 B 仍是当前唯一干净编辑底图：

`00_基准图/INPUT_B_MC_FACE_DERIVED_002_干净编辑底图.png`

它不等于 `STATE_003`，只保留较低唤醒度的等待状态。不得为了画质干净而把它虚报为已经重建了作者认可的专注状态。

## 6. 下一方法边界

若以后继续，必须另开任务并更换方法类别，例如真正限制在目标上眼睑区域的局部蒙版修补或确定性像素编辑。不得把这种方法更换伪装成本轮 R04，也不得继续用整图随机重生成碰运气。

在作者批准新方法并获得通过图之前：

- 暂停重新执行衣装／背景组合；
- 保留旧 C 的语义裁决；
- 保留 B 的干净底图资格；
- 三张新图全部只作失败过程记录。

## 7. 使用状态

所有新图统一保持：

```text
REJECTED_RECONSTRUCTION_ATTEMPT
NEGATIVE_PROCESS_REFERENCE
NOT_IDENTITY_ANCHOR
NOT_STATE_REPLACEMENT
NOT_EDIT_BASE
INTERNAL_VISUAL_DEVELOPMENT_ONLY
```
