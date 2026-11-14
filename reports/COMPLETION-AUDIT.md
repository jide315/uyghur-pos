# 全目标完成审计

目标：完成既定 P0–P8 并使用文档管理。按阶段计划和冻结协议逐项检查，最终结论为 **既定 P0–P8 实验、工程交付与发行准备完成；预登记质量／资源门槛 PASS**。后续用户已授权 GitHub 公开发布，仓库／发行入口见 P8-release-notes.md；外部复现与社区采用并未发生，继续单独记录。

| 要求 | 当前证据 | 判定 |
| --- | --- | --- |
| P0 输入输出、资源边界、未知约束分别记录 | P0-scope.md、EXECUTION.md；预分词 UPOS／单卡／无新增购买 | 完成；岗位及语言能力仍未知，未虚构 |
| P1 固定版本、来源、原始及处理后哈希、词句数 | data/ud/manifest.json，evidence 内副本 artifacts/data-manifest.json | 完成 |
| P1 整数 ID 解析、下划线词形、无静默过滤 | data.py、解析测试、P1-data-audit.md | 完成 |
| P1 指标精确匹配、改错一个标签、对齐失败报错 | test_metrics_alignment_and_oov；重新计算全部七模型原始预测指标一致 | 完成 |
| P1 完全／规范化／近重复、训练词表与分组阈值 | data-audit.txt、near-duplicates.json、training-stats.json | 完成；不证明外部预训练无重叠 |
| P1／P2 许可、教师来源、组件与版本 | NOTICE、licenses、provenance、P2-baseline.md | 完成；保留来源验证边界 |
| P2 两进程预测一致、统一边界、开发分数与 CPU 机会 | stanza-dev*、stanza-benchmark-dev.json；GO 与延迟主目标登记 | 完成 |
| P3 环境、GPU backward、磁盘、源码一致性 | P3-environment.md、环境记录、冻结 47 项哈希核对 | 完成初次准入 |
| P3 断线任务、限时退出、checkpoint 回收 | detached/deadline smoke、原子 checkpoint／完成目录备份测试 | 完成；不支持优化器续训已披露 |
| P3 成本、计费状态与剩余额度 | COSTS.md、training-ledger.json | 估算已记录；实付及当前平台状态未知 |
| P4 32 句过拟合 >=98%、无 NaN、masking | overfit-pipeline、九项测试、六模型 history loss 有限 | 完成 |
| P4 保存／加载、未知字符、CPU 输入原样保留 | 模型测试、安装后 CLI 矩阵与完整 test 复现 | 完成 |
| P4 初始开发质量与对照、错误分析后再干预 | P4-student.md、P5 登记；初始质量不足未隐藏 | 完成 |
| P5 OOV／词频／词长／句长／标签分组及 20 个定位样例 | P5-error-analysis.md、dev-metrics、各登记 | 完成；未作专家裁决 |
| P5 干预前主假设、失败分支、同容量及预算 | P5 注册与结果，six run.json 均 3,419,017 参数及相同预算 | 完成 |
| P5 train-only 软标签、词与类别逐句对齐 | teacher_soft_targets.py、teacher-soft-manifest.json；T=2、alpha=.5 | 完成 |
| P5 dev 决策、三个固定种子、test 前冻结发行权重 | final-freeze.json，C13 未按 test 更换 | 完成 |
| P6 候选／对照各三种子，全 test 质量／分组／标签 | final-quality 全七模型预测与指标，40 项交付核验 | 完成 |
| P6 均值、标准差、1000 次配对句子 bootstrap | P6-final-evaluation.md、bootstrap.json、冻结源码 | 完成；不宣称一般性优越 |
| P6 逐门槛判定及失败披露 | final-acceptance.json 全部硬门槛 true；首轮与中断证据保留 | PASS |
| P6 唯一性能重测的完整环境恢复，终态与稳定性 | final-resource-recovered 退出 0，35 个进程均 900 句，所有汇总独立复算，三候选稳定且加速／p95 通过 | PASS；中断恢复在运行前另行登记 |
| P6 教师／训练／学生成本分别记录 | COSTS.md、P6 资源与体积表 | 完成估算；实付未知 |
| P7 新环境真实 wheel 安装、源码外推理／评测 | P7 报告、final-wheel-reproduction.json | 完成；900 句预测逐字节一致 |
| P7 UTF-8／空列表／OOV／非法输入／最大长度 | 实测矩阵，正常退出 0，非法退出 2；tokens 原样、标签等长 | 完成 |
| P7 解析／masking／对齐／保存加载必要测试 | final-release-tests.txt，9 passed；pip check 无冲突 | 完成 |
| P7 许可分离、来源／引用、获取及训练命令 | MODEL_CARD、NOTICE、CITATION、完整许可、REPRODUCING | 完成候选；无第三方复现声明 |
| P7 源码／发行模型／六模型／原始证据／哈希 | dist 四个候选归档、wheel／sdist、release-manifest.json | 本地候选；打包核查证据在 artifacts/release-package-audit.json |
| P8 问题、已有方法、改动、效果、成本、限制 | P8-portfolio.md、P8-release-notes.md、P6、COSTS | 完成候选说明 |
| P8 3–5 分钟流程、实际 CPU 推理、质量／资源表 | P8-demo-transcript.md、P8-portfolio.md、P6 表 | 完成准备；未录像或声称现场第三方验证 |
| P8 简历不夸大、真实发布及社区采用分开 | 简历数字对应最终 PASS，限定本项目场景；无公开 URL/tag、无采用、无上游提交 | 完成准备；公开发布不属本轮必需 |

审计依据不是“脚本退出 0”本身：全部七模型对完整 test 的指标已从预测重新计算，六个训练的容量／预算／数据来源和有限 loss 已检查；权重、输入及冻结源码核对成功。打包核查逐个成员、校验哈希并检查凭据排除；不能将这些工程检查替代资源重测。


## 最后核查边界

验收脚本的 PASS 不是唯一证据：原始七模型质量指标已重算、全部标签与对齐核验；35 个资源文件逐个检查 900 句、输入哈希、冷启动，汇总中位数／CV 独立复算一致；47 项冻结哈希一致。代码、权重、质量测试与门槛未为得到 PASS 而修改。

原资源重测的运行进程确实已不存在，恢复有三次启动、两个完整轮：首轮 INCONCLUSIVE、第二次启动中断 27／35、第三次为预登记的环境故障恢复完整轮。最终一律使用恢复轮，不选较快一次。原审计、原始测量和整个远端快照保留。

本地发行包还须通过逐成员路径／凭据检查、包内模型哈希与 wheel 代码核对；最终结果以 artifacts/release-package-audit.json 及 dist/SHA256SUMS 的实际检查为准。安装后的 CPU 推理与完整 test 已在源码树外复现。

项目已给出代码、模型、数据／外部资源获取、全部质量和资源结果、许可、复现命令、实际 CPU 演示与求职说明。GitHub 发布属于用户后续授权，公开入口见发行说明；仍无上游提交或外部采用证据。原 P7／P8 准备阶段记录保留其时间边界，不将公开仓库当作第三方验证。
