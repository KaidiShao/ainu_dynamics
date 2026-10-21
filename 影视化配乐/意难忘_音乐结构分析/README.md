# 关大洲《意难忘》：音乐结构、重复候选与具身情绪假设

研究日期：2026-10-21。对象：用户提供的**这一份实际录音**，不是根据曲名或乐评写作的赏析。

**交付状态：已完成实际音频的计算分析、候选片段频谱检查与研究报告；尚未完成听觉复核。** 当前会话没有可将这份录音直接输入模型听觉感知的接口。运行播放器并不等于分析者听到了声音。因此，M1–M6 是有时间序列证据的**动机候选编号**，不能当作已经完成的听写、配器识别或全曲主题目录。主旋律真正第一次进入的位置、所有旋律变形、和弦功能和声部交接，仍有需要人工确认的部分。

## 从哪里开始

1. [structure_analysis.md](structure_analysis.md)：全曲 15 个工作分段、声音变化与解释边界。
2. [motif_analysis.md](motif_analysis.md)：6 组短片段、18 个定位窗口、重复证据、弱候选与排除理由。这是报告的核心。
3. [embodied_hypotheses.md](embodied_hypotheses.md)：音乐证据怎样支持可被否证的体验假设。
4. [ainu_composition_lessons.md](ainu_composition_lessons.md)：面向有孩子 IF 线的原创配乐设计实验，不含成品配乐。
5. [listening_review.html](listening_review.html)：用浏览器打开，手动选择原始 FLAC；无需服务器、不会上传文件。可完整播放、按窗口定位、记录并导出 CSV。**首次身体感受记录建议先完整聆听，不展开分析提示。**

最可靠的发现是：00:57.8–01:26.5 与 01:26.5–01:55.2 有连续材料的回返；04:45.7–05:14.4 与 05:14.4–05:43.1 也有连续回返。它们内部并非只有整段相似，还可拆出 6–7 秒的短序列。02:26.0 附近的波动型候选与后半段多处相关，但成员之间的证据强度不同。05:44.6 之后的大幅收束中，05:51.0 与 06:06.3 的短句仍相似，第二次还稍弱；“重复的作用只来自越来越响”不符合全部声学数据。**这些事实没有直接证明任何人的情绪或身体反应。**

## 音频来源与身份

工作目录中未找到 MP3/WAV/FLAC 等目标音频；随后读取用户在请求中明确提供的本地路径。未下载替代版本。

| 项目 | 实测值 |
| --- | --- |
| 原始文件 | `C:/Users/kdsha/Music/关大洲 - 意难忘.flac` |
| 来源 | 用户提供；演奏、版本与发行信息未经独立核验 |
| 格式 | FLAC / PCM_24 |
| 原始采样率、声道 | 48,000 Hz / 2 |
| 帧数 | 18,510,272 |
| 时长 | 385.6306667 秒，即 06:25.631 |
| 文件大小 | 62,241,041 字节 |
| SHA-256 | `75753ca7b73eaafc26634cfed1af1a7f1487df4e4307d81b5b295b2c103a6735` |
| 原始样本峰值 | 0.986454；没有达到 ±1 的样本。这不排除上游限幅或压缩 |

**原始音频、可试听音频切片均未复制到仓库，也未提交 Git。** 文件内的数值结果与此哈希绑定；不同发行版、片头静音或剪辑版不能直接套用时间戳。

已先阅读两份背景文档。本地检出缺少它们，因此通过 GitHub 连接器读取 `KaidiShao/ainu_dynamics` 默认分支版本，未更改现有检出：

- [主导动机与声音叙事设计_v1.md](https://github.com/KaidiShao/ainu_dynamics/blob/main/影视化配乐/主导动机与声音叙事设计_v1.md)，blob `85617195389eeeb1eed6a7953e90734e8f312c2d`。
- [具身动机_序列性身体感受与音乐叙事实验_v1.md](https://github.com/KaidiShao/ainu_dynamics/blob/main/影视化配乐/具身动机_序列性身体感受与音乐叙事实验_v1.md)，blob `2d5e82125876ce6fd5d9d4cddd3b094d3ec46c05`。

文档中的创作设想作为项目背景使用，**没有被用来预设《意难忘》一定存在“试探—悬置—自由回应”结构**。

## 复现

需要 Python 3.12 与 [requirements-lock.txt](requirements-lock.txt) 中的软件版本。通常的独立环境安装方式：

```powershell
python -m venv .venv
& ./.venv/Scripts/python.exe -m pip install -r requirements-lock.txt
& ./.venv/Scripts/python.exe analysis.py --audio 'C:/Users/kdsha/Music/关大洲 - 意难忘.flac'
```

本次实际执行使用仓库根目录下、已忽略的 `.audio-analysis-venv`：

```powershell
# 在 E:/ainu_dynamics 中运行
& ./.audio-analysis-venv/Scripts/python.exe '影视化配乐/意难忘_音乐结构分析/analysis.py' --audio 'C:/Users/kdsha/Music/关大洲 - 意难忘.flac'
```

本机捆绑 Python 的 `ensurepip` 不可用，实际通过捆绑解释器的 `pip --python <目标解释器>` 安装到隔离环境。该环境本身不含 pip；这不影响分析运行。不要把它当成通用 Python 安装的要求。

也可复制 `audio_config.example.json` 为已忽略的 `audio_config.local.json`，修改 `audio_path` 后运行 `analysis.py`。`--recompute` 强制重算特征；`--skip-discovery` 跳过全局发现，但仍复算已选模板的检索与比较。默认会写入本目录的 `data/`、`figures/` 和已忽略的 `.cache/`，不会修改音频。注释窗口绑定原始录音哈希；换成不同文件内容时程序会拒绝套用这些窗口，需要另建分析目录并重新标注。

## 处理与判断流程

1. SoundFile 读取原始双声道，记录哈希、样本峰值和立体声 RMS。双声道平均为 mono 后重采样至 22,050 Hz；不做响度归一化。
2. STFT：2048 样本窗、512 hop，帧间隔约 23.22 ms。HPSS 使用 31 帧/频点核与 margin=2，得到偏持续成分，**不等于乐器分离**。
3. 对持续成分做 C2–B7、每半音一个 bin 的 CQT。没有人工校准调律，不输出乐谱。分析量重采样到 0.1 秒网格。
4. CQT 每帧减去中位数底噪并截零。C4–B6 的平方根幅度经列归一化，形成保留音区的特征；同一范围按八度折叠后再归一化，形成 upper chroma。两种余弦相似度各占一半。
5. 全曲检索 2、4、6、8、10 秒序列。排除重叠及相邻不足 1 秒的配对；过滤低能量片段；每种长度保留最多 100 对非冗余高分窗口。这是**候选发现**，不是全部音乐动机的穷举。
6. 频谱检查后，在 `annotations.json` 固定 6 个模板。全曲再搜 0.90、0.95、1.00、1.05、1.10 倍长度，混合特征与八度折叠特征分别召回候选。局部 DTW 限制在约 15% 对角带。
7. 每对比较保留线性对齐、DTW、低频 chroma、onset 相关，以及 200 次 0.5 秒块重排的第 95 百分位参考。顺序增益不是显著性检验；模板与候选来自同一录音，存在选择偏差。
8. 额外做 1–11 半音移位的 upper-chroma 筛查，防止只看绝对音高；结果仅为弱证据，不能靠移调后高分认定同一旋律。
9. 结构解释之后才写具身假设与原创设计建议。没有进行自动和弦标注、乐器分类或复调听写。

时间戳中的小数表示**定位网格精度**，不是乐句边界准确度。强起音通常可在约 ±0.2–0.5 秒附近复核；连奏、弱起、混响和语义分段可能偏移 1–2 秒。100 ms 网格和 DTW 路径不能证明几十毫秒的演奏微时值变化。

## 文件与指标

- `analysis.py`：提取、全曲候选检索、图表；`motif_review.py`：模板复查、DTW、时序对照、分段统计。
- `annotations.json`：分析者选定的工作边界与候选窗口。手工选择不代表耳听确认。
- `data/audio_metadata.json`：音频身份与软件版本；`background_sources.json`：背景文档版本。
- `features_100ms.csv`：逐帧指标；`boundary_candidates.csv`：±2/4/8 秒前后描述量变化。
- `repeat_candidates.csv`：全曲短窗候选；`template_search.csv`：每个模板的保留匹配峰；`transposition_screen.csv`：移调筛查。
- `motif_occurrences.csv`：报告中的全部定位窗口与得分；`phrase_comparisons.csv`：长短层级对应；`section_features.csv`、`onset_periodicity.csv`：段落指标与周期线索。
- `figures/01–08`：总体特征、波形/CQT、chroma、边界候选、自相似矩阵、动机时间轴、起音周期性、6 秒序列相似矩阵；`local_M1–M6.png`：逐次局部频谱与能量比较。共 14 张。
- `data/run_manifest.json`：音频、分析代码、注释窗口与依赖清单的哈希；缓存同时核对源音频、提取函数与主要库版本。
- `validate_outputs.py`：检查时间边界、数值、报告链接、音频隔离与一个正/负序列对照；结果写入 `data/validation.json`。运行 `python validate_outputs.py`，可加 `--audio <路径>` 再核对原文件哈希。

报告里的 RMS 默认采用原始双声道 100 ms 块的等权能量汇总，单位 dBFS。它不是感知响度 LUFS、播放声压，也不是人的唤醒度。频谱质心、频带比例来自 mono；CQT 占用率不是声部数；side/mid 不是听者感觉的“包裹程度”。低频 bin 的相邻泄漏可能产生 G/F 等标签，CSV 中 `bass_pc_top3` 等字段**只是频谱排名，不是实际和弦音确认**。听辨、独立听感记录和因果对照均尚未完成。
