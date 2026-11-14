# P6：最终冻结验收

2026-11-14 UTC；总判定 **PASS**。首次 test 质量保持原始结果，最终资源证据使用环境中断后完整恢复的 35 个新进程。

候选 distilled、同容量监督 worddrop，种子 13／42／2026。发行 C13 在首次 test 评分前按 dev 非标点最高、同分取较小 seed 确定，未按 test 换权重。

## 测试质量

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
| 监督均值 | 89.4063% | 86.7970% | 77.6699% |

测试 900 句／10,330 词；OOV 3,193 词，定义相对于标注 train，即使公开词向量覆盖该词也算 OOV。词频／词长／句长分组、逐标签正确数与全部预测在 evidence 包 artifacts/final-quality/。

| 配置 | 指标 | 均值 | 样本标准差 pp |
| --- | --- | ---: | ---: |
| 候选 | overall | 90.1033% | 0.1735 |
| 候选 | nonpunct | 87.6619% | 0.2163 |
| 候选 | oov | 79.5595% | 0.7981 |
| 监督 | overall | 89.4063% | 0.3534 |
| 监督 | nonpunct | 86.7970% | 0.4465 |
| 监督 | oov | 77.6699% | 0.8161 |

## 配对句子 bootstrap

固定 seed13、1000 次，按句子配对抽样；每种子单独计算，不把同一句的三模型当成独立样本。差值与区间单位均为百分点。

| 模型 | 指标 | 差值 | 95% 下界 | 95% 上界 |
| --- | --- | ---: | ---: | ---: |
| C13 | overall | 0.2130 | -0.2733 | 0.7438 |
| C13 | nonpunct | 0.2534 | -0.3665 | 0.9067 |
| C42 | overall | 0.5227 | 0.0198 | 1.0559 |
| C42 | nonpunct | 0.6396 | 0.0239 | 1.3081 |
| C2026 | overall | 0.5034 | 0.0095 | 1.0296 |
| C2026 | nonpunct | 0.6155 | -0.0003 | 1.2602 |
| S13 | overall | -0.6389 | -1.1399 | -0.0765 |
| S13 | nonpunct | -0.8086 | -1.4377 | -0.1092 |
| S42 | overall | -0.2807 | -0.8596 | 0.2670 |
| S42 | nonpunct | -0.3621 | -1.0759 | 0.3158 |
| S2026 | overall | 0.0678 | -0.4257 | 0.5699 |
| S2026 | nonpunct | 0.0845 | -0.5325 | 0.7072 |

发行 C13 的区间跨越零，不能宣称显著超过 Stanza。质量边界为 -1pp，所有候选总体／非标点区间下界均在此边界之上；这是本固定测试的配对区间，不是对其他领域一般性非劣效的证明。

## 逐标签风险

- C42/AUX：support=254，F1 下降 5.477pp。

## 完整恢复轮 CPU 资源

平台：Xeon E5-2680 v4 @ 2.40GHz，Ubuntu 22.04、Python 3.12.3、PyTorch 2.3.0+cu121。GPU 关闭用于测量；CPU=0、线程=1、batch=1、无量化。宿主 56 逻辑 CPU，平台页面分配 7 核／30GB，共享后台负载见 recovery-environment-before/after.json。

每个模型 5 个新进程，模型顺序逐轮反转；所有进程遍历全部 test，dev 前 30 句预热。p50／p95 取前三轮各分位数的中位数，RSS／冷启动取五进程中位数；冻结脚本使用五轮 p50 的 CV 判断稳定性。时延计入输入 JSON 解析与输出序列化，不含首次模型加载。

| 模型 | p50 ms | p95 ms | 速度比 | RSS MiB（范围） | 冷启动 s | CV |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| B0 | 16.775 | 25.547 | 1.000x | 485.12 (484.12–485.38) | 3.621 | 0.01052 |
| C13 | 2.782 | 4.479 | 6.031x | 388.64 (388.47–388.68) | 2.124 | 0.01701 |
| C42 | 2.842 | 4.568 | 5.902x | 388.67 (388.54–388.82) | 2.152 | 0.01207 |
| C2026 | 2.910 | 4.780 | 5.766x | 388.65 (388.60–388.82) | 2.140 | 0.02097 |
| S13 | 2.935 | 4.846 | 5.716x | 388.61 (388.50–388.73) | 2.137 | 0.01897 |
| S42 | 2.905 | 4.767 | 5.775x | 388.78 (388.64–388.79) | 2.171 | 0.01230 |
| S2026 | 2.877 | 4.816 | 5.830x | 388.67 (388.52–388.84) | 2.154 | 0.00808 |

主目标一直为 p50 至少 2 倍且 p95 不变差，不以较容易通过的另一项替换；内存是绝对 RSS，不减去空进程基线。资源收益仅适用于本平台与配置。

## 逐项门槛

| 类别／门槛 | 判定 |
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
| resources/C42_measurement_stable | PASS |
| resources/C42_speedup_ge_2x | PASS |
| resources/C42_p95_not_worse | PASS |
| resources/C2026_measurement_stable | PASS |
| resources/C2026_speedup_ge_2x | PASS |
| resources/C2026_p95_not_worse | PASS |
| resources/full_test_benchmark | PASS |
| resources/frozen_benchmark_protocol | PASS |
| release/release_overall_loss_le_1pp | PASS |
| release/release_nonpunct_loss_le_1pp | PASS |

## 资源体积与成本

C13 checkpoint 14,602,130 字节，已包含词表／字符表／标签与推理权重；无需外部词向量。教师本地资源（resources、tokenize、POS、pretrain）合计 31,428,117 字节，逐文件哈希在冻结文件。完整 Python 环境体积另见 public-environment.json，不将模型体积与环境／RSS 混同。

训练／教师准备／推理成本分开记录于 COSTS.md。当前恢复只跑 CPU benchmark，没有重训、改质量分数或增加付费实例；真实余额／实付仍以平台账单为准。

## 尝试历史与最终证据选择

1. 首个完整轮：artifacts/final-benchmark-attempt1/，C42 CV 超阈值，INCONCLUSIVE，原始验收 final-acceptance-attempt1.json 保留。
2. 唯一性能重测的第一次启动：artifacts/final-benchmark-repeat/，因实例关机／重启中断，仅 27／35 份，无 summary；原样保留。
3. 该重测的环境故障恢复启动：完整 35 份，结果位于 artifacts/final-benchmark/；原始 recovered 目录／job 亦保留。按运行前登记无条件采用本轮，不混合前轮较优值。

因此有三次启动、两个完整轮；不把中断藏掉，也不称为从未重试。登记见 P6-interruption-recovery-registration.md；源码、输入、种子、质量与门槛均未改变。首轮详细历史见 P6-attempt1-and-interruption.md。

原始全部质量、bootstrap、35 个进程、冻结、环境及验收 JSON 在 evidence 包；独立逐进程及汇总复算见 final-resource-verification.json。公开数据为书面语，本项目没有验证方言、ASR、OCR 或业务领域，没有第三方采用证据。
