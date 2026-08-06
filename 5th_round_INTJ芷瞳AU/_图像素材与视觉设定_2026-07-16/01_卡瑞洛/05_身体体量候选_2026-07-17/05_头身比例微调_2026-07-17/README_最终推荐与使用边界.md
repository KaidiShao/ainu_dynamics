---
task: MC_BODY_HEADSCALE_TEST
date: 2026-07-17
baseline: MC_BODY_FUSION_R03
generated_rounds: 2
maximum_authorized_rounds: 3
composite_round_generated: false
primary_finalist: MC_BODY_FUSION_R03
secondary_finalist: MC_BODY_HEADSCALE_R01
body_anchor_created: false
identity_anchor_unchanged: MC_FACE_REF_001
---

# 头身比例微调测试｜最终推荐与使用边界

## 1. 结论

当前最佳仍是融合R03原版。

测试证明：

1. 头大感有一部分来自头发外轮廓；
2. 收紧发量只能带来小幅改善；
3. 原版和发量测试版都仍在真人合理比例范围；
4. 内置生成器没有成功执行可验证的独立2%缩头；
5. 不应为了追求小头继续随机生成或滑向时装模特比例。

## 2. 并排评分

| 图像 | 身份 | 头身 | 颈肩 | 身体/站姿 | 手 | 衣着机位 | 保守总分 | 裁决 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 融合R03原版 | 35 | 16 | 14 | 14 | 4 | 5 | 88 | 第一推荐；原版保留 |
| 头身R01 | 35 | 17 | 14 | 14 | 4 | 5 | 89 | 第二推荐；有效发量对照 |
| 头身R02 | 34 | 16 | 12 | 12 | 3 | 1 | 78 | 流程硬淘汰 |

原版在前一轮的任务口径下为89分；本表按本轮更严格的头身专项分项重新计分，因此为88。分数不能跨不同评分表直接比较。

虽然R01在保守分项相加中高1分，但它的身份未达到36分门槛，且独立综合审计认为两张整体打平。新图没有形成足够证据替代原版，所以原版继续排名第一。

## 3. 第一推荐｜融合R03原版

本目录比较副本：

```text
00_基准图/MC_BODY_HEADSCALE_BASELINE_FUSION_R03.png
```

正式素材路径：

```text
../04_R03结构融合校准_2026-07-17/01_轮次图/MC_BODY_FUSION_R03.png
```

优点：

- 身份最稳；
- 眉眼、唇线和自然不对称保留较多；
- 颈肩、身体、站姿和手部已经通过上一轮门槛；
- 头身比例虽然位于真人合理范围偏大端，但没有时装化。

定位不变：

```text
PRIMARY_FUSION_CANDIDATE
PROVISIONAL
NOT_BODY_ANCHOR
NOT_IDENTITY_ANCHOR
AUTHOR_SELECTION_REQUIRED
```

## 4. 第二推荐｜头身R01

文件：

```text
01_轮次图/MC_BODY_HEADSCALE_R01_HAIR_ONLY.png
```

有效变化：

- 发顶和两侧外轮廓约收紧4%—6%；
- 没有可辨认的头脸整体缩放；
- 头大感小幅下降；
- 颈肩、身体、站姿、手和机位基本连续。

限制：

- 身份35/40，略低于原版综合身份稳定度；
- 改善幅度小；
- 剩余头大感已经不能继续靠削发解决；
- 继续减少发量会破坏原始发型身份。

定位：

```text
VALID_HAIR_VOLUME_TEST
SECONDARY_PROVISIONAL
NOT_BODY_ANCHOR
NOT_IDENTITY_ANCHOR
AUTHOR_SELECTION_REQUIRED
```

## 5. 淘汰｜头身R02

文件：

```text
01_轮次图/MC_BODY_HEADSCALE_R02_HEAD_MINUS_2PCT.png
```

失败原因：

- 没有证据表明只把头缩小2%；
- 同尺寸画布中整个人物缩小并后移约18%—20%；
- 头顶留白和脚下地面大幅增加；
- 阴影、构图重心、脚距、身体轮廓、手和衣物均重绘；
- 较远取景使脸部身份细节丢失。

定位：

```text
REJECTED_GLOBAL_SCALE_AND_FRAMING_DRIFT
NEGATIVE_REFERENCE
PROCESS_DRIFT
NOT_BODY_ANCHOR
NOT_IDENTITY_ANCHOR
```

不得从R02推断小头版本更合理，也不得将其用于后续生成。

## 6. 为什么没有生成综合R03

综合轮的前提是：

- R01成功解决发量问题；
- R02成功验证独立2%缩头；
- 两者分别提供可组合的有效修正。

实际只有R01是基本有效的局部测试，R02则完全改变了人物与构图尺度。两者不存在可合并的两项成功参数。因此按授权停止，不生成综合R03。

## 7. 下一阶段边界

当前不建议继续磨正面头身比例。若作者接受融合R03或发量测试R01中的任一方向，下一步应进入三分之四与侧面核验。

无论作者选择哪张：

- 原始近景仍是唯一脸部身份锚点；
- 当前正面图不能决定侧脸与后脑；
- 185 cm继续作为文字常量；
- 尚未建立身体锚点；
- 多角度通过前不进入最终服装成品图。

## 8. 给作者的最短选择说明

```text
融合R03原版：身份更稳，头部略大但仍合理；第一推荐。

头身R01：发量更收敛，头大感略轻；可作为保守备选。

头身R02：全局缩放失败，淘汰。
```
