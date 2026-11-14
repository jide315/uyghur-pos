#!/usr/bin/env python3
"""Generate model and portfolio records from frozen, measured results only."""
import json,statistics
from pathlib import Path

freeze=json.loads(Path('artifacts/final-freeze.json').read_text())
accept=json.loads(Path('artifacts/final-acceptance.json').read_text())
bench=json.loads(Path('artifacts/final-benchmark/summary.json').read_text())['models']
q=Path('artifacts/final-quality');teacher=json.loads((q/'B0.json').read_text())['groups']
models={n:json.loads((q/f'{n}.json').read_text())['groups'] for n in freeze['candidates']}
release=freeze['release_model'];path=Path(freeze['models'][release]);b=bench[release]
mean={k:statistics.mean(r[k]['accuracy'] for r in models.values()) for k in ['overall','nonpunct','oov']}
speed=bench['B0']['p50']/b['p50']
lines=['# Uyghur pretokenized UPOS student', '',
       f'Experiment version 0.1.0. Registered decision: **{accept["verdict"]}**.', '',
       '## Task and architecture', '',
       'Input: a UTF-8 JSONL object with a pretokenized `tokens` list. Output preserves the list and adds equally long UPOS labels. Character bidirectional GRU + word bidirectional LSTM; CPU inference requires PyTorch only. This model does not perform tokenization.', '',
       f'Frozen configuration: `{freeze["candidate_config"]}`. Release weights were chosen by development non-punctuation accuracy before test scoring: `{release}`.',
       f'SHA-256: `{freeze["model_sha256"][release]}`. Checkpoint size: {path.stat().st_size:,} bytes.', '',
       '## Training data and provenance', '',
       'UD Uyghur-UDT r2.15, commit 77a1c20dae6650284c4c50959833ea2485c5119a: 1,656 train sentences / 19,262 words; 900 development and 900 test sentences. Source authors: Marhaba Eli, Daniel Zeman, Francis Tyers. UPOS annotations are manual/native according to the source metadata; the texts are literature and school reading material.', '',
       'Fixed public conll17 vectors and Stanza v1.10.0 Uyghur teacher resources are separately attributed. Teacher probability targets, when used, come only from train. Test does not build vocabulary, supply targets, select epochs or choose release weights.', '',
       '## Frozen test results', '',
       '| Metric | Stanza baseline | Candidate three-seed mean | Release checkpoint |',
       '| --- | ---: | ---: | ---: |']
for key in ['overall','nonpunct','oov']:
    lines.append(f'| {key} | {teacher[key]["accuracy"]*100:.3f}% | {mean[key]*100:.3f}% | {models[release][key]["accuracy"]*100:.3f}% |')
lines += ['', 'Raw predictions, sentence-paired bootstrap intervals, every seed and each failed/missing gate are preserved in the final experiment report. A point-estimate PASS does not establish general statistical non-inferiority; crossing intervals must be disclosed.', '',
          '## Measured CPU behavior', '',
          f'Release p50: {b["p50"]*1000:.3f} ms; p95: {b["p95"]*1000:.3f} ms; speed ratio vs baseline: {speed:.3f}x; median peak RSS: {b["rss"]:,} bytes.',
          'Same machine, CPU-only, one thread, batch=1, alternating model order. Five fresh processes per model measure memory/cold start; the first three full rounds measure latency. Input parsing and output serialization are included. See final report for hardware, variability and raw measurements.', '',
          '## Limitations', '',
          'Small, fiction-oriented evaluation; no validated dialect, speech, OCR or business-domain capability. OOV is defined relative to annotated train even when public vectors cover the word. Possible overlap between external vector pretraining text and evaluation text cannot be independently excluded. No third-party adoption or independent external replication is claimed.', '',
          '## Licensing and attribution', '',
          'Original software: MIT. Trained checkpoint distribution: CC BY-SA 4.0 with UD attribution and share-alike notice; Apache-2.0 third-party resource notices are retained. The checkpoint is not covered solely by the code MIT license. See NOTICE.md and licenses/.', '',
          '## Use', '',
          'Install the wheel and a supported PyTorch build. Run `uyghur-pos predict --model model.pt` and pipe JSONL input. No network access is required after the weights are available. Empty lists return empty labels; invalid inputs are rejected. Maximum 512 tokens per sentence and 128 Unicode code points per token.', '']
Path('MODEL_CARD.md').write_text('\n'.join(lines))
portfolio=['# P8：求职展示材料', '',f'冻结实验判定：{accept["verdict"]}。以下所有数字均来自最终 test／benchmark，不能换用开发分数。', '',
    '## 3–5 分钟演示', '',
    '1. 用一张数据流图说明预分词 UPOS、公开数据版本和 train/dev/test 隔离。',
    '2. 展示从零训练、公开词向量、冻结、word dropout、容量调整与软标签蒸馏的登记及失败结果。',
    '3. 运行一次 CPU JSONL 推理及非法输入检查。',
    '4. 展示最终三种子质量、OOV、配对区间、CPU p50/p95、RSS 与失败门槛。',
    '5. 说明能复现什么、许可边界、未验证的真实领域及开源采用状态。', '',
    '## 可用于简历的事实', '',
    '独立实现维吾尔语预分词词性标注训练与 CPU 部署工具，完成固定公开数据审计、强基线复现、错误驱动改进、同容量监督／蒸馏对照、三随机种子验证及自动验收。',
    f'最终候选测试总体准确率三种子均值 {mean["overall"]*100:.3f}%，选定权重 CPU p50 {b["p50"]*1000:.3f} ms，对照基线测得速度比 {speed:.3f}x；是否达到低损压缩门槛以 {accept["verdict"]} 为准。', '',
    '若 FAIL／INCONCLUSIVE，简历不得写“达到低损压缩目标”；可展示诊断、性能取舍和完整实验能力。', '',
    '## 开源与采用状态', '',
    '发行候选包含可复现源码、权重、模型卡、许可、报告与哈希。实际公开 URL／tag／时间及外部反馈另记；没有外部采用证据时填“暂无”，不以本机复现代替第三方采用。', '']
Path('reports/P8-portfolio.md').write_text('\n'.join(portfolio))
