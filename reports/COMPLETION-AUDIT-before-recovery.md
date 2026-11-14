# 全目标完成审计

目标：完成既定 P0–P8 并使用文档管理。按阶段计划和冻结协议逐项检查，当前结论为 **未完成全部目标**。工程候选可以使用，压缩收益尚未通过完整验收。

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
| P6 逐门槛判定及失败披露 | final-acceptance.json；首轮 C42 CV=.12288 | INCONCLUSIVE |
| P6 唯一完整资源重测，终态、稳定性与最终判定 | 重试登记及原 job PID；远端拒绝连接，输出未回收 | **未完成，阻碍总目标** |
| P6 教师／训练／学生成本分别记录 | COSTS.md、P6 资源与体积表 | 完成估算；实付未知 |
| P7 新环境真实 wheel 安装、源码外推理／评测 | P7 报告、final-wheel-reproduction.json | 完成；900 句预测逐字节一致 |
| P7 UTF-8／空列表／OOV／非法输入／最大长度 | 实测矩阵，正常退出 0，非法退出 2；tokens 原样、标签等长 | 完成 |
| P7 解析／masking／对齐／保存加载必要测试 | final-release-tests.txt，9 passed；pip check 无冲突 | 完成 |
| P7 许可分离、来源／引用、获取及训练命令 | MODEL_CARD、NOTICE、CITATION、完整许可、REPRODUCING | 完成候选；无第三方复现声明 |
| P7 源码／发行模型／六模型／原始证据／哈希 | dist 四个候选归档、wheel／sdist、release-manifest.json | 本地候选；打包核查证据在 artifacts/release-package-audit.json |
| P8 问题、已有方法、改动、效果、成本、限制 | P8-portfolio.md、P8-release-notes.md、P6、COSTS | 完成候选说明 |
| P8 3–5 分钟流程、实际 CPU 推理、质量／资源表 | P8-demo-transcript.md、P8-portfolio.md、P6 表 | 完成准备；未录像或声称现场第三方验证 |
| P8 简历不夸大、真实发布及社区采用分开 | 简历明确 INCONCLUSIVE；无公开 URL/tag、无采用、无上游提交 | 完成准备；公开发布不属本轮必需 |

审计依据不是“脚本退出 0”本身：全部七模型对完整 test 的指标已从预测重新计算，六个训练的容量／预算／数据来源和有限 loss 已检查；权重、输入及冻结源码核对成功。打包核查逐个成员、校验哈希并检查凭据排除；不能将这些工程检查替代资源重测。

恢复只需取得原 final-resource-repeat 的终态及输出。若完整且稳定，按冻结脚本判定，保留首轮、不混选更优值；若仍不稳定，保持 INCONCLUSIVE，不能放宽阈值或进行第三轮。没有必要重训或重跑首次质量评分。

## 2026-11-14 补充审计

已在无卡开机后取得远端现场：原 PID 均不存在，重测只有 27／35 份结果且无 summary。上述“恢复后取得完整结果”的预期未成立，旧 running 状态不能继续当存活证据。成果已完整快照回收，442 个文件、47 项冻结哈希及 15 个 checkpoint 校验通过，详见 backup-2026-11-14.md。备份要求已完成，资源验收仍未完成，不自动重启原实验或追加第三次测量。
