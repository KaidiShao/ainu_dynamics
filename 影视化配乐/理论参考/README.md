# 《爱奴》影视化配乐｜按需调用的理论资料库

> 目的：**先听、先感受、先记录，再让理论帮助解决眼前的问题。** 这不是一份要求作者依次读完的书单。
>
> 建立日期：2026-10-24。状态：参考入口已核验；书籍为出版社页面与章节索引；开放论文有官方 PDF 链接与本地下载脚本（是否已在个人电脑下载，以运行结果为准）。

## 怎么用（最低负担）

遇到一个真正打动自己的音乐片段时，只需向 ChatGPT / Codex 提供 **作品、具体乐句或时间戳、谱面（如有）、自己的身体感受和想知道的问题**。Agent 先查本目录的 [THEORY_ROUTER.md](THEORY_ROUTER.md)，最多推荐 1–2 个最相关的理论概念、实际对应关系，以及一个可尝试的音乐变形或对照片段。**除非主动要求，不给漫长理论综述，不布置阅读作业。**

例如：
- 「舒伯特有一个从低音区突然跳高又回来的酸涩点，是哪种音乐运动机制？」
- 「《意难忘》一个旋律循环让我先感到胸口、喉咙，再到后颈；哪些解释属于音乐预期，哪些是具身模拟？」
- 「温柔与自罚怎么在同一个短动机里同时存在？给出有音乐操作性的候选，而不是只说某个和弦很悲伤。」
- 「帮我针对这段谱子，挑一个理论最可能解释的地方，不用讲一大堆背景。」

### 资料放在哪里

- **出版书籍**：以下四本尚未取得可合法存放于仓库的全文。保存出版社目录、关键章节与购买/图书馆线索；以后如果作者自行获得授权副本，可以让本地 Codex 在合法访问条件下检索。不要把盗版全文推送到公开 GitHub。
- **开放论文**：以下两篇已经找到出版社/作者官方 PDF URL。执行 `python 影视化配乐/理论参考/download_open_access.py` 可在你的电脑上下载至本目录被 Git 忽略的 `papers/`。原始 PDF 不建议上传公开仓库，避免变成长期重复或无意的版权再分发。
- **延伸理论**：有文章全文链接，但未纳入本轮自动 PDF 下载。需要时按问题再打开。

## A. 四本最重要的书：保留章节入口，不需要通读

| 书 | 用到什么问题时再查 | 优先章节 | 正版来源 |
|---|---|---|---|
| **Steve Larson, _Musical Forces_ (2012)** | 音符为什么像受重力/吸引/惯性推动？跳进—回落有怎样的运动预期？ | Ch. 4–6（melodic forces、expectation、rhythm）；Ch. 7 分析实例 | https://iupress.org/9780253005496/musical-forces/ |
| **David Huron, _Sweet Anticipation_ (2006)** | 为什么预期建立、等待、被打断与实现会产生不同的情绪？ | ITPRA 模型与 anticipation / tension / prediction 相关章节；MIT Press 官网有样章资源入口 | https://mitpress.mit.edu/9780262582780/sweet-anticipation/ |
| **Arnie Cox, _Music and Embodied Cognition_ (2016)** | 为什么听见音高运动好像身体也在上探、回落？是发声/运动模拟还是内感受？ | Ch. 4（Pitch Height）、5（Temporal Motion）、8（Musical Affect） | https://iupress.org/9780253021670/music-and-embodied-cognition/ |
| **Robert Hatten, _Interpreting Musical Gestures, Topics, and Tropes_ (2004)** | 整段乐句而非某个孤立音符，如何形成一个有心理意味的动作？ | Ch. 5–8，特别 Ch. 8 的舒伯特 D.959/D.784；Ch. 11–12 连续/中断 | https://iupress.org/9780253344595/interpreting-musical-gestures-topics-and-tropes/ |

**重要**：Hatten 的 Ch. 8 分析的是 D.959 与 D.784，**不是**我们正在听的 D.899 No.1/No.3；后者只能借理论自己做读谱，不要伪称书里逐小节讲过它们。

## B. 可以获得官方全文 PDF 的核心论文

| 文献 | 解决什么问题 | PDF | 理论地位 |
|---|---|---|---|
| **Putkinen et al., _Bodily maps of musical sensations across cultures_ (PNAS, 2024)** | 音乐情绪与主观身体位置感的跨文化联系；身体地图可以怎样记录？ | https://emotion.utu.fi/wp-content/uploads/2023/02/Putkinen_et_al_23.pdf | 实证研究，主要是片段/群体的身体感觉图谱，**不是**乐句内部随时间迁移的因果模型 |
| **Tsai, _Music-induced emotion as controlled hallucination: an active interoceptive inference account_ (Frontiers in Psychology, 2026)** | 音乐结构是否可能作为 pseudo-interoceptive evidence，和身体信号、先验一起参与情感推断？ | https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1759699/pdf | **Hypothesis and Theory**，不能当成已有定量因果验证 |

这两篇按 CC BY 开放获取。这里保存原始作者/出版社链接，使用时明确署名和出处。下载脚本不需要登录。

## C. 进一步需要时再查的论文

- **Patrik Juslin (2013), _From everyday emotions to aesthetic emotions: Towards a unified theory of musical emotions_.** 多机制解释：包括音乐预期、情绪感染、运动/节奏同步、记忆等。适合提醒我们「同一情感不必由唯一机制产生」。OA 正文：https://www.sciencedirect.com/science/article/pii/S1571064513000638 ，DOI:10.1016/j.plrev.2013.05.008。
- **Gold et al. (2019), _Predictability and Uncertainty in the Pleasure of Music: A Reward for Learning?_** 期待的 information content 与 entropy 怎样与喜欢程度相关；注意偏向 reward/pleasure，不等于酸涩。OA 正文：https://pmc.ncbi.nlm.nih.gov/articles/PMC6867811/ ，DOI:10.1523/JNEUROSCI.0428-19.2019。

## D. 当前三个案例：永远先从体验提问题

| 案例 | 已有第一人称观察 | 理论会被用来回答什么 |
|---|---|---|
| **关大洲《意难忘》** | 动机重复时从膻中附近到喉咙、后颈/头皮，再在肩膀附近回落，近似呼吸式循环 | 音高动作/预期/身体运动想象/内感受解释，分别解释了什么？ |
| **舒伯特 D.899 No.1 / No.3** | 温柔中有「酸涩」；酸涩多在中脘附近并向脖颈、后颈延伸 | 哪段乐句最明显？相同感觉能否由不同音乐动作产生？ |
| **舒伯特「低音区突然跃升又返回」片段** | 往复运动引发显著酸涩 | 主要影响来自跳进、返回、停留时间、句法预期，还是音乐语境？ |

第一人称体验是**创作目标的重要事实**，但不是一种通用生理机制已经成立的证明。理论只帮助产生可以推翻的解释和下一次比较，不得把「某音一定激活中脘」写成规律。

## E. 每次把理论用到创作时，留下一个极短记录

可以复制：

```markdown
### Case: 作品／时间戳／小节
- 我实际上感觉到：［身体位置、运动、同时存在的情绪］
- 谱面/音频观察：［已核实的音高/节奏/动态］
- 最相关理论：［作者、章节/论文节、一个概念］
- 候选解释（不是定论）：［为什么可能形成这种体验］
- 一个最小对照：［只改一个音乐变量］
- 试听后决定：保留／淘汰／待验证
```

**希望达到的效果**：不是把创作变成读书计划，而是让理论像工具库一样随取随用；每次只解决面前那个鲜明的、真实感受到的问题。
