# P2：基线与继续依据

日期：2026-11-13（UTC）；状态：已得到可运行基线与探索测量，完整阶段验收仍有未完成项。

数据固定为 UD Uyghur-UDT r2.15，Stanza 1.10.1，模型资源 v1.10.0，包 `udt_nocharlm` 与 `conll17`。使用官方资源清单 MD5 核验下载文件；来源的详细训练过程尚待进一步核对，不能称完全受控训练比较。

开发集：900 句、10,644 词。

| 指标 | Stanza |
| --- | ---: |
| 总体正确／总词数 | 9664 / 10644 |
| 总体 UPOS | 90.7929% |
| 非标点 UPOS | 88.5794% |
| OOV UPOS | 81.8155%（3448 词） |

原始记录：`artifacts/stanza-dev.json`、`artifacts/stanza-dev.predictions.jsonl`。

CPU 单线程开发集探索：三轮 p50 分别为 17.049、16.988、16.945 ms；一个新进程峰值 RSS 为 520,364,032 字节。见 `artifacts/stanza-benchmark-dev.json`。尚不满足正式协议的五进程内存测量与交替执行要求，不能作为最终压缩收益结论。

继续决定：GO（限一次有界学生训练，以检验假设）。预注册主目标选延迟：希望将本机同口径单句 p50 降至约 8.5 ms 以下，并满足正式质量门槛。使用约 500 MiB 内存、十余 ms 的强基线作参照，小模型具有可验证的部署改善空间；目标用户需求仍为假设。

先运行一个 seed=13 的监督模型，若低于教师 5 个百分点以上，按计划分析原因再决定容量调整或蒸馏，不连续扫参。测试集保持未评分。

第二独立进程复跑已完成，`stanza-dev-repeat.predictions.jsonl` 与首轮预测逐字节一致。

补充来源核查：官方 [v1.10.1 发布说明](https://github.com/stanfordnlp/stanza/releases/tag/v1.10.1) 确认模型基于 UD 2.15 重建；官方 [训练脚本](https://github.com/stanfordnlp/stanza/blob/v1.10.1/stanza/utils/training/run_pos.py) 将 train 用于训练，dev 用于选优，test 仅在独立评分模式使用。实际 checkpoint config 中 `train_file` 为 `ug_udt.train.in.conllu`，`eval_file` 为 `ug_udt.dev.in.conllu`，shorthand 为 `ug_udt`，与公开流程一致。因此可以作为已知官方来源的基线，但无法仅凭文件名独立证明原始训练机器的全部操作；公开词向量的原始网页覆盖仍是双方共享限制。

尚未完成：正式资源测量与最终三种子评测。原始源码版本和资源哈希均保留，不把官网旧版端到端表格当本地预分词结果。
