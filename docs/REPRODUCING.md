# 复现路径

## 已训练权重的推理与评测

建立全新 Python 3.12 环境，按 `artifacts/clean-environment.txt` 的记录安装 CPU PyTorch 2.3.0+cpu，再安装本项目（仅推理不需要 Stanza）。模型准备好后离线执行 `uyghur-pos predict --model <checkpoint>`，输入 UTF-8 JSONL。

批量评测使用 `student-eval`，输出预测 JSONL 与包含正确数、分母和分组结果的 JSON。相同权重的预测应与原报告一致；不同硬件的绝对耗时不能直接比较。

完整运行命令见根 README。不能把 tokenizer、ASR 或 OCR 的原始输出当作已验证输入场景。

## 从头训练

1. 执行 `uyghur-pos prepare`，核对原始版本和 `data/ud/manifest.json`。
2. 需要词向量时执行 `python scripts/download_stanza.py`，核对固定资源 MD5。
3. 按最终冻结记录中的结构、种子、超参数和命令训练，使用新 run 目录。
4. 只在 dev 上早停；训练日志、checkpoint、数据／资源哈希和训练参数都保留。
5. 未进入正式验证时不要评分 test；已经公开的测试分数不能被后续反复试探当作新盲测。

当前已实测 GPU 训练及 CPU 干净环境同权重复现，详见 P7 报告；不冒充第三方复现。训练数值有随机性，正式报告已列所有登记种子的波动。

### 可移植的完整命令

以下均在解压后的源码根目录执行，不依赖原 AutoDL 的绝对路径。安装 CUDA 版 torch 2.3.0 后安装本项目；纯 CPU 可用 `requirements-cpu.txt`，训练时改 `--device cpu` 并自行增加时间上限。这样产生的新训练不能声称与原 GPU 预算完全相同。

```bash
python -m pip install '.[baseline]'
uyghur-pos prepare
python scripts/download_stanza.py
mkdir -p artifacts
python scripts/teacher_soft_targets.py
for seed in 13 42 2026; do
  uyghur-pos train --train data/ud/train.jsonl --dev data/ud/dev.jsonl \
    --stats data/ud/training-stats.json --output "runs/reproduced-worddrop-${seed}" \
    --seed "$seed" --device cuda --epochs 40 --patience 6 --max-seconds 300 \
    --pretrain models/stanza/ug/pretrain/conll17.pt --word-dropout .15
  uyghur-pos train --train data/ud/train.jsonl --dev data/ud/dev.jsonl \
    --stats data/ud/training-stats.json --output "runs/reproduced-distilled-${seed}" \
    --seed "$seed" --device cuda --epochs 40 --patience 6 --max-seconds 300 \
    --pretrain models/stanza/ug/pretrain/conll17.pt --word-dropout .15 \
    --teacher artifacts/teacher-train-soft.jsonl --alpha .5
done
```

默认结构 hidden=128、char-hidden=32、batch=32、lr=.003、threads=1。词向量预训练启用时词维度由公开资源决定。每个 run.json 保存实际参数和哈希；completion.json 保存时长、早停及显存。复训允许随机波动，不要求新权重字节哈希相同；报告全部种子，不按 test 选优。

## 正式性能复现

`scripts/formal_benchmark.py` 读取冻结配置，同一 CPU 单线程下交替执行模型，5 个新进程覆盖内存和冷启动，前 3 轮覆盖时延；保留每句原始耗时。`scripts/accept_final.py` 按冻结门槛生成 PASS／FAIL／INCONCLUSIVE。

资源测量必须同时包含基线与候选，不能只在另一台更快的机器上跑候选。测量不稳定时按协议重测一次，不选择最好一次。

复现原始权重测量时，将 evidence 包和 experiments 包解压到源码根目录，执行 prepare 与固定资源下载，确认 artifacts/final-freeze.json 中输入及权重哈希。模型单包只包含发行 C13，不能单独完成全六模型验收。

```bash
python scripts/formal_benchmark.py --freeze artifacts/final-freeze.json --output artifacts/reproduced-benchmark
python scripts/accept_final.py --freeze artifacts/final-freeze.json \
  --quality artifacts/final-quality --benchmark artifacts/reproduced-benchmark \
  --output artifacts/reproduced-acceptance.json
```

这是接收者所在机器的新测量，不覆盖原实验。原 AutoDL 中断轮保留，最终采用的是按环境故障条款完整恢复的测量；见 P6-interruption-recovery-registration.md。公开首次 test 的预测已在 evidence 包中；不必为了复现指标重新运行教师，使用 CLI evaluate 对已有预测与固定 gold 评分即可。
