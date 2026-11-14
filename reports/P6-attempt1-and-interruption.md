# P6：冻结测试质量验收

2026-11-13 UTC。首次正式 test 评分；CPU 资源结论另行补齐。

冻结候选 distilled，同容量监督对照 worddrop；固定种子 13／42／2026。发行 C13 在 test 打开前按 dev 非标点最高确定；尽管 C42 的 test 分数更高，未更换发行权重。

| 模型 | 总体 UPOS | 非标点 UPOS | OOV UPOS |
| --- | ---: | ---: | ---: |
| B0 | 89.6902% | 87.1591% | 79.7682% |
| C13 | 89.9032% | 87.4125% | 78.6408% |
| C42 | 90.2130% | 87.7987% | 79.9562% |
| C2026 | 90.1936% | 87.7746% | 80.0814% |
| S13 | 89.0513% | 86.3505% | 76.8243% |
| S42 | 89.4095% | 86.7970% | 77.7325% |
| S2026 | 89.7580% | 87.2435% | 78.4529% |
| 候选均值 | 90.1033% | 87.6619% | 79.5595% |
| 监督对照均值 | 89.4063% | 86.7970% | 77.6699% |

## 配对句子 bootstrap

1000 次、固定 seed13。差值为候选减教师，单位为百分点；句子作为抽样单元，不把三个模型的同句当独立样本。

| 模型 | 指标 | 点差 | 95% 下界 | 95% 上界 |
| --- | --- | ---: | ---: | ---: |
| C13 | overall | 0.2130 | -0.2733 | 0.7438 |
| C13 | nonpunct | 0.2534 | -0.3665 | 0.9067 |
| C42 | overall | 0.5227 | 0.0198 | 1.0559 |
| C42 | nonpunct | 0.6396 | 0.0239 | 1.3081 |
| C2026 | overall | 0.5034 | 0.0095 | 1.0296 |
| C2026 | nonpunct | 0.6155 | -0.0003 | 1.2602 |

## 逐标签风险披露

以下列出 support >=100 且候选 F1 相对基线下降超过 5pp 的项。
- C42 / AUX: support=254, F1 下降 5.477pp

## 证据与限制

原始预测、逐种子标签统计、分组正确数和 bootstrap 位于 `artifacts/final-quality/`；冻结文件 `artifacts/final-freeze.json` 记录所有模型、输入与源码哈希。教师及公开词向量来源、书面语范围、外部预训练覆盖限制继续有效。

本质量结果不独立代表 CPU 资源门槛通过。完整自动验收须结合最终 benchmark，再形成总判定。

## 随机种子波动

| 组别 | 指标 | 均值 | 样本标准差 |
| --- | --- | ---: | ---: |
| candidates | overall | 90.1033% | 0.1735pp |
| candidates | nonpunct | 87.6619% | 0.2163pp |
| candidates | oov | 79.5595% | 0.7981pp |
| controls | overall | 89.4063% | 0.3534pp |
| controls | nonpunct | 86.7970% | 0.4465pp |
| controls | oov | 77.6699% | 0.8161pp |

## 首轮资源判定

完整首轮结果为 INCONCLUSIVE，仅 C42 时延 CV=0.12288 超出 0.10，所有质量、加速及 p95 条件均通过。完整原始记录 `artifacts/final-benchmark-attempt1/`、`artifacts/final-acceptance-attempt1.json` 保留；按协议进行一次固定 CPU 0 的完整重测，见 P6-resource-retry-registration.md。重测尚未完成前不宣称总 PASS。

## 首轮完整资源表（不替代重测）

平台：Xeon E5-2680 v4 @ 2.40GHz，共享 AutoDL 主机；Ubuntu 22.04、Python 3.12.3、PyTorch 2.3.0+cu121，以 CPU 单线程、batch=1 测量，未使用 GPU 或量化。五个新进程测 RSS／冷启动，前三轮测延迟；warmup 为固定 dev 前 30 句，正式输入为全部 900 个 test 句。

宿主 lscpu 显示 56 个逻辑 CPU；平台页面为本实例分配 7 核、30GB 内存，不能把宿主全核数当独占配额。未逐时采样其他租户后台负载，干扰程度未知；跨轮 CV 是已实测的稳定性指标，不代表证明主机空闲。原始第一次没有固定核，唯一重测按登记固定允许集合中的最小 CPU=0。

| 模型 | p50 ms | p95 ms | 速度比 | RSS MiB 中位数（范围） | 冷启动 s | p50 CV | 稳定 |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| B0 | 18.213 | 27.310 | 1.000x | 484.59 (484.13–485.58) | 3.639 | 0.02467 | 是 |
| C13 | 3.051 | 5.068 | 5.969x | 388.62 (388.35–388.67) | 2.032 | 0.02039 | 是 |
| C42 | 2.961 | 4.894 | 6.152x | 388.58 (388.56–388.76) | 2.012 | 0.12288 | 否 |
| C2026 | 3.039 | 4.977 | 5.994x | 388.58 (388.56–388.62) | 2.045 | 0.01718 | 是 |
| S13 | 3.024 | 4.973 | 6.024x | 388.69 (388.39–388.97) | 2.097 | 0.01542 | 是 |
| S42 | 3.040 | 5.119 | 5.992x | 388.68 (388.55–388.86) | 2.034 | 0.01868 | 是 |
| S2026 | 3.038 | 5.061 | 5.996x | 388.67 (388.36–388.75) | 2.092 | 0.01043 | 是 |

所有候选首轮速度比与 p95 门槛通过，但 C42 CV=0.12288 >0.10。因此本表不能支持整个方案 PASS。C13 RSS 相对 B0 约下降 19.8%，没有达到内存减半；预注册主目标是延迟，不切换门槛。

## 逐项验收与恢复阻碍

| 门槛 | 结论 |
| --- | --- |
| quality/overall_mean_loss_le_1pp | PASS |
| quality/nonpunct_mean_loss_le_1pp | PASS |
| quality/worst_overall_loss_le_1_5pp | PASS |
| quality/oov_loss_le_2pp | PASS |
| quality/registered_seed_set | PASS |
| quality/frozen_test_inputs | PASS |
| quality/frozen_protocol | PASS |
| resources/C13_measurement_stable | PASS |
| resources/C13_speedup_ge_2x | PASS |
| resources/C13_p95_not_worse | PASS |
| resources/C42_measurement_stable | INCONCLUSIVE |
| resources/C42_speedup_ge_2x | PASS |
| resources/C42_p95_not_worse | PASS |
| resources/C2026_measurement_stable | PASS |
| resources/C2026_speedup_ge_2x | PASS |
| resources/C2026_p95_not_worse | PASS |
| resources/full_test_benchmark | PASS |
| resources/frozen_benchmark_protocol | PASS |
| release/release_overall_loss_le_1pp | PASS |
| release/release_nonpunct_loss_le_1pp | PASS |

2026-11-13 23:08 UTC 起，本地 SSH 与直接 TCP 连接均收到 connection refused，尚不能查明平台实例状态或读取唯一重测结果。不能由连接拒绝推断进程已完成或已终止；不重启、不进行第三次测量，也不把本地主机测量混入远端正式组。恢复后检查原 job `final-resource-repeat` 的 status、PID 和完整输出，再按已登记规则判定。
原始首轮 `artifacts/final-benchmark-attempt1/` 和 `artifacts/final-acceptance-attempt1.json` 作为 attempt 1 保留。当前总判定仍为 INCONCLUSIVE，压缩目标尚未获完整证据。

## 必需资源体积与执行成本

教师本地运行资源包括以下全部文件（非仅 POS 权重）：

| 文件 | 字节 |
| --- | ---: |
| models/stanza/resources.json | 434,061 |
| models/stanza/ug/tokenize/udt.pt | 626,525 |
| models/stanza/ug/pos/udt_nocharlm.pt | 18,356,895 |
| models/stanza/ug/pretrain/conll17.pt | 12,010,636 |

教师资源合计 31,428,117 字节。学生 C13 单个 checkpoint 14,602,130 字节，已内置推理所需词表／字符表／标签及权重，不需要外部词向量文件。

完整 Python 环境与模型资源应分别计量；CPU 干净虚拟环境文件体积记录在发行核查证据中，硬链接／缓存磁盘占用不能等同模型权重。训练耗时和 GPU 峰值见 COSTS.md；教师软标签抽取 37.35 秒属于一次性准备成本，不计为学生单句延迟。
