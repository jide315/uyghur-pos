# 维吾尔语 NLP 求职与开源项目

当前主题：**面向 CPU 部署的轻量维吾尔语词性标注——基于公开数据的模型压缩与误差评测**。

当前阶段（2026-11-14 UTC）：P0–P8 的实验、工程交付和求职展示准备已完成，总判定 **PASS**。训练、冻结后的三种子质量测试、完整 CPU 测量与安装复现均有原始证据。实际公开发布和外部采用尚未发生。详见 [最终评测](reports/P6-final-evaluation.md)、[完成审计](reports/COMPLETION-AUDIT.md) 和 [发行说明](reports/P8-release-notes.md)。

| 测试指标 | Stanza 基线 | 学生三个种子均值 | 发行 C13 |
| --- | ---: | ---: | ---: |
| 总体准确率 | 89.690% | 90.103% | 89.903% |
| 非标点准确率 | 87.159% | 87.662% | 87.413% |
| OOV 准确率 | 79.768% | 79.559% | 78.641% |

发行 C13 完整恢复轮 CPU p50 为 2.782 ms，基线 16.775 ms，速度比 6.031x。配对区间跨零，不宣称显著优于基线；全部尝试与关机中断记录保留。成果已备份本机，见 [备份记录](reports/backup-2026-11-14.md)。

当前执行状态见 [进度索引](reports/README.md)，最新开发集改进见 [P5 结果](reports/P5-development-results.md)。原创代码采用 [MIT 许可](LICENSE)，外部数据与权重另遵守各自条款。

本轮交付与验证见 [首版实现报告](reports/implementation-2026-11-13.md)。

## 当前实现

- 固定 UD r2.15 与来源哈希，检查 CoNLL-U 整数词、标签和切分重复；保留原始下划线词形。
- 统一总体、非标点、OOV、词频／词长／句长和逐标签指标。
- 字符双向 GRU＋词级 BiLSTM，支持 GPU 训练、最佳 checkpoint、CPU 加载与 JSONL 推理。
- 支持监督训练、可选字符消融、训练集硬标签或软概率蒸馏。最终使用 train-only、温度 2、混合权重 0.5 的软蒸馏；同容量开发集对照与全部失败分支见 [冻结决策](reports/P5-candidate-decision.md)。
- 支持显式使用固定 conll17 预训练词向量；标注 train 的词频／OOV 定义不变，外部词典与参数量变化单独披露，见 [改进实验登记](reports/P5-experiment-registration.md)。
- `train --pretrain <词向量路径> --freeze-words` 可固定词向量，只训练其他层，用于检验小标注集上词表示过拟合的假设。
- Stanza／词典基线、开发错误分析、CPU 初步 benchmark。
- SSH 私有配置、源码同步、结果回收和有截止时间的后台任务。

数据与权重默认不入库。来源和许可边界见 [NOTICE](NOTICE.md)，远端操作见 [AutoDL 操作说明](docs/autodl-operations.md)。

## 安装与运行

以下命令在已经提供合适 PyTorch 的环境执行；本次 AutoDL 实测为 Python 3.12.3、PyTorch 2.3.0+cu121、GTX 1080 Ti。镜像依赖版本记录于回收的 `artifacts/environment.txt`。

```bash
python -m pip install -e '.[baseline,test]'
python -m pytest -q
uyghur-pos prepare
uyghur-pos baseline --data data/ud/dev.jsonl --stats data/ud/training-stats.json --output artifacts/stanza-dev.json --download
uyghur-pos train --train data/ud/train.jsonl --dev data/ud/dev.jsonl --stats data/ud/training-stats.json --output runs/my-run --device cuda --seed 13 --max-seconds 300
uyghur-pos student-eval --model runs/my-run/best.pt --data data/ud/dev.jsonl --stats data/ud/training-stats.json --output artifacts/student-dev.json
```

下载资源需要网络；模型准备好后，推理不访问网络。已有 run 目录拒绝覆盖，请使用新名称。当前仅恢复最佳权重用于推理，不支持优化器状态续训。

```bash
printf '%s\n' '{"tokens":["مەن","بارىمەن","."]}' | uyghur-pos predict --model runs/my-run/best.pt
python scripts/analyze.py --gold data/ud/dev.jsonl --predictions artifacts/student-dev.predictions.jsonl --stats data/ud/training-stats.json --output artifacts/student-errors.json
python scripts/benchmark.py --model runs/my-run/best.pt --data data/ud/dev.jsonl --output artifacts/student-benchmark-dev.json
```

每行输入 `tokens` 必须为非空字符串的列表；允许空列表并返回空标签。最多 512 个词，每词最多 128 个 Unicode 码点，超长或非法输入以非零退出码报错，不静默截断。输出保持词形与顺序，标签列表等长。该工具要求预分词，不能把结果描述为原始文本端到端能力。

`scripts/benchmark.py` 是单进程探索入口；正式验收用 `scripts/formal_benchmark.py` 交替执行全部模型、五个新进程测 RSS／冷启动、前三轮测时延，并用 `scripts/accept_final.py` 判定。完整命令见 [复现指南](docs/REPRODUCING.md)，发行模型使用见 [快速使用](docs/QUICKSTART.md)。

## 方案文档

- [阶段目标与验收清单（执行主入口）](docs/plans/04-phase-goals-and-acceptance.md)
- [评测与决策协议](docs/plans/05-evaluation-protocol.md)
- [进度与验收证据模板](docs/plans/06-progress-and-evidence-template.md)
- [当前方案与边界](docs/plans/01-project-proposal.md)
- [实验、预算与验收计划](docs/plans/02-experiment-plan.md)
- [备选方向与决策记录](docs/plans/03-decisions-and-alternatives.md)

方案文档保留预登记目标与历史状态；已执行结果以进度索引和最终报告为准。发行候选与证据包的文件及哈希见 `dist/release-manifest.json`，目前仅本地保存，没有虚构公开下载地址。

阶段顺序：P0 边界 → P1 数据 → P2 基线 → P3 执行环境 → P4 监督学生 → P5 错误驱动改进 → P6 最终评测 → P7 可复现候选包 → P8 开源与求职展示准备。

压缩目标维持为：质量平均损失不超过 1 个百分点，同时达到预选的 CPU 加速 2 倍或峰值内存减半目标；详细分组保护、种子、统计及判定口径见评测协议。实际开源发布与社区采用单独记录，不与文档或实验完成混同。
