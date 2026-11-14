# 执行进度与证据索引

更新：2026-11-14 UTC。当前 P0–P8 的实验与本地发行准备均已完成，最终验收 **PASS**。首次质量预测未改变，资源采用中断后完整恢复轮，首轮与中断轮均保留；实际公开发布和社区采用另记。

| 阶段 | 当前状态 | 证据与剩余项 |
| --- | --- | --- |
| P0 | 本轮范围已记录 | [范围](P0-scope.md)；精确长期预算和目标岗位仍未知 |
| P1 | 数据准入审计已完成 | [数据审计](P1-data-audit.md)；固定版本、解析、完全重复、近重复检查与来源说明齐全；外部资源覆盖限制保留 |
| P2 | 基线来源及复现已完成 | [基线](P2-baseline.md)；官方 UD 2.15 说明与 checkpoint train/dev 记录一致，复跑预测一致；最终资源测量在 P6 |
| P3 | 首版环境已部署 | [环境](P3-environment.md)；GPU LSTM、后台断线及限时退出已验证；无优化器续训 |
| P4 | 监督训练闭环完成 | [学生](P4-student.md)、[多种子结果](P5-development-results.md)；初始模型质量不足的记录保留，后续通过有限改进提高 |
| P5 | 探索与固定三种子验证完成，候选已冻结 | [冻结决策](P5-candidate-decision.md)、[可定位错误分析](P5-error-analysis.md)；最终候选 distilled，对照 worddrop，发行 C13 按 dev 确定 |
| P6 | 质量与资源均 PASS | [最终报告](P6-final-evaluation.md)、[中断恢复登记](P6-interruption-recovery-registration.md)；完整 35 个新进程，全部硬门槛通过，失败／中断历史保留 |
| P7 | 干净安装、预测复现及候选包完成 | [复现](P7-reproduction.md)、[模型卡](../MODEL_CARD.md)；完整 test 预测逐字节一致，六个发行文件及模型哈希已核查 |
| P8 | 求职材料、实际演示及发行准备完成 | [展示材料](P8-portfolio.md)、[发行说明](P8-release-notes.md)；只陈述本项目预设门槛与已验证结果，实际公开发布与外部采用暂无 |

运行记录与大文件在项目私有 `artifacts/`、`runs/`、`data/`、`models/`，默认不提交；源码、公开说明和报告不含 SSH 密码。连接方法见 [操作说明](../docs/autodl-operations.md)。

逐要求的完成与缺口见 [完成审计](COMPLETION-AUDIT.md)，交付候选见 [发行说明](P8-release-notes.md)。最终 PASS 支持“达到本项目预设压缩门槛”，不支持对真实领域、显著优越或社区采用作扩大声明。
