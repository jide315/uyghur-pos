# 全目标执行管理

更新：2026-11-14 UTC。当前目标：用户已恢复卡配置，继续完成既定 P0–P8，持续记录，不以单轮训练完成代替项目验收。

## 当前队列

| 项 | 待交付证据 | 状态 |
| --- | --- | --- |
| P0 | 范围、预算及本轮工作管理 | 已有；本文件持续管理 |
| P1 | 固定数据、解析、近重复审计、许可来源 | 已完成；P1 报告与 manifest |
| P2 | 教师版本／训练来源、可比基线 | 已完成；P2 报告与官方来源证据 |
| P3 | GPU、后台、产物回收、费用记录 | GPU 与 SSH 已恢复；既有成果已完整备份，COSTS 台账持续记录 |
| P4 | 监督模型训练、保存／加载 | 已完成；32 句管道检查及三种子有记录 |
| P5 | 有依据的改进、同容量对照、候选冻结 | 已完成；失败分支保留，六模型 test 前冻结 |
| P6 | 三种子质量、bootstrap、正式 CPU 测量及判定 | 完整恢复轮 35 进程完成，全部质量／资源／发行门槛 PASS，独立复算一致 |
| P7 | 干净安装、推理／评测复现、模型卡、发行包 | wheel 复现通过；六个发行文件逐成员、凭据排除及权重哈希核查通过 |
| P8 | 求职材料、演示、可核验发行材料 | 展示、发行说明、实际 CLI 演示与完整证据已准备；GitHub 源码仓库已公开，发行入口见 P8-release-notes.md |

## 不变条件

- 仅现有单卡；不充值、不新租机器；按已提供 0.60 元／小时记录估算与计费不确定性。
- 先完成有依据的有限探索，再在 test 评分前冻结配置、种子、门槛和单个发行权重。
- 保留失败记录；资源或质量未达标就明确 FAIL，不降低既定门槛以制造通过。
- 工程与发行材料仍要做完；若实际性能目标未达成，目标保持未达成，不能改写为“有报告即完成”。
- 实际公开仓库、对外消息、外部采用单独记录；未发生时不声称发生。

## 本轮顺序

1. 补齐近重复与基线官方来源证据。
2. 首轮四配置完成；一次容量／优化调整未超过小模型，结果保留。train-only 教师软标签抽取完成，逐句对齐通过；seed13 蒸馏非标点达到 88.50%，优于同容量监督。
3. 蒸馏三个固定种子已完成，候选 distilled／对照 worddrop 与发行 C13 已于 test 打开前冻结；首次测试质量全部门槛通过，不能重启质量评分或根据 test 换模型。
4. 冻结并进行最终测试与规范 benchmark，出逐项验收结论。
5. 完成干净环境复现、发行候选、模型说明、演示与简历材料。

后续执行结束逐项补证据路径与结论；阻碍某一项时继续其他独立工作，不虚报完成。

## 恢复前记录（历史状态）

- 冻结时间：2026-11-13 22:54:25 UTC；文件 `artifacts/final-freeze.json`，公开副本 `reports/final-freeze.json`。发行 C13，seed13 的 checkpoint 哈希 `6614613c3d398da75e53a686e9dbf5a64616dd876880102903dca3c29f15cc4b`。
- `final-evaluation` 后台任务已正常结束。首次质量结果在 `artifacts/final-quality/`，不可覆盖；总体三种子均值 90.1033%，基线 89.6902%。
- 首轮资源在 `artifacts/final-benchmark/`，验收 `artifacts/final-acceptance.json` 为 INCONCLUSIVE：仅 C42 时延 CV 超阈值，其他质量／速度／p95 条件均通过。
- 已按预登记启动唯一一次重测，远端 job `final-resource-repeat`（worker PID 11901、子进程 PID 11902），固定允许的最小 CPU=0。结果在 `artifacts/final-benchmark-repeat/`。恢复时先检查该任务及进程，不重启新测量。
- 重试完成后用冻结的 `scripts/accept_final.py --benchmark artifacts/final-benchmark-repeat --output artifacts/final-acceptance-repeat.json` 判定，保留第一次结果。重试一律作为最终资源证据，不选两次更好值；不得第三次重测。
- 已构建初步 wheel/sdist，并在干净 CPU 环境中从源码树外验证 C13 test 预测逐字节一致。初步 MODEL_CARD 的总判定仍是 INCONCLUSIVE，须待重试结束后定稿。
- 最终定稿时应保留首轮目录为 attempt1，将第二次完整结果作为 canonical（或明确指定路径）；再生成模型卡、最终报告、发行包及哈希，复核凭据排除。不要修改已冻结的评测／训练源代码去调整结论。

## 23:08 UTC 后的连接阻碍

SSH 与直接 TCP 均收到 Connection refused，实例状态未知，详见 reports/P3-remote-unavailable.md。已通过异步问题请求控制台状态或更新 SSH 参数。不能由连接拒绝推断任务死亡，不能重启测量；原重测结果不可访问时总判定继续 INCONCLUSIVE。

已继续本地独立工作：47 项冻结源码／输入／模型／协议哈希一致；补完整逐标签诊断、资源表、成本台账、可移植训练命令、发行说明与实际 CPU 演示。开源候选不等待外部采用，但压缩目标仍需原重测结果才可能完成。

## 本地交付核查结果

- 9 项最终测试通过，pip check 无冲突；40 项完整质量／训练记录核查通过。
- 全部 15 个训练 history 的 loss 有限；首轮 35 个资源进程均保存全部 900 句耗时及有效冷启动记录。C42 波动超阈值仍是实质缺口。
- 新 wheel 的代码逐文件匹配冻结哈希；六个归档／安装文件均逐成员检查路径、凭据排除及内容，发行 C13 与六模型归档中的权重哈希匹配冻结记录。
- 源码、发行 C13、六模型实验、原始证据四个归档，以及 wheel／sdist，均在 dist；清单 dist/release-manifest.json，核查 artifacts/release-package-audit.json。
- 当前全目标审计 reports/COMPLETION-AUDIT.md 为未完成：只剩原资源重测结果回收及其最终判定。没有重训、重新选模型或第三次测量。

## 2026-11-14：无卡开机后的优先备份

用户要求先将成果保存本机。SSH 已恢复，原重测 worker／子进程 PID 均不存在，status.json 的 running 是遗留状态；重测仅 27／35 份进程 JSON、无 summary，不能视为完成。

已保存独立快照 backups/autodl-20261114T000421Z/，442 个文件逐个校验；47 项冻结哈希与全部 15 个 checkpoint 均一致。缺失的远端结果另补回本机，未覆盖较新的本机文件。备份清单、压缩包及校验记录均保留，详见 reports/backup-2026-11-14.md。

本轮仅完成备份，没有训练或重启测量。此前“等待恢复 SSH”的阻碍已消除，但完整资源重测并未留下足够结果，整体验收继续 INCONCLUSIVE；后续路径需基于中断事实另行安排，不能把备份完成当作压缩目标完成。

## 2026-11-14：恢复全部目标

用户恢复卡配置并建立新的持续目标。已复核 GPU／CPU／torch 与原平台一致、旧 PID 不存在。按冻结协议的明确环境故障重试条款登记恢复方案，见 reports/P6-interruption-recovery-registration.md：保留 27 份中断结果，从头跑完整 35 个进程，结果无论优劣一律采用，不根据结果继续重测。首次 test 质量和全部训练／评测源代码不变。

## 最终验收与交付

final-resource-recovered 已退出 0，完整 35 个新进程、每进程 900 句。最终资源目录 artifacts/final-benchmark/ 是 recovered 的完整副本；首轮为 final-benchmark-attempt1，中断轮 final-benchmark-repeat。final-acceptance.json 为 PASS，所有布尔门槛为 true。原质量预测未重跑，代码、模型与协议仍匹配冻结哈希。

最终模型卡、P6、P8、复现与费用记录已按实际结果更新。发行文件含源码／模型／六模型实验／全部测量证据、wheel 与 sdist，清单与 SHA-256 在 dist；交付前检查见 reports/COMPLETION-AUDIT.md 和 artifacts/release-package-audit.json。本节记录实验验收与本机交付完成时的状态；后续公开发布见文末，第三方采用仍暂无。

本文件前面的连接故障、INCONCLUSIVE 和中断状态保留为历史；最新状态以本节、队列表及最终报告为准。

## 2026-11-14：目录归档与 GitHub 发布准备

用户要求统一存放本机项目文件，项目主体保持 /root/src/uyghur-nlp/。已将临时目录内 16 个辅助文件全部移动到 operations/local/，逐文件哈希一致；迁移清单与发布状态在该私有目录。目录说明见 docs/PROJECT_LAYOUT.md。

用户已授权创建 GitHub 仓库并公开发布。发布审查的 9 项测试通过、无关键代码阻碍；修复完整复现命令遗漏 baseline 可选依赖的问题，并增加公开代码包 CI。

发布准备时，用户提供的 /root/src/github_voucher/ 为账号 jide315 的 Windows DPAPI 连接配置；被引用的 .github-token.dpapi 不在目录内，Linux 主机当时不能直接使用。连接元数据曾私有归档 credentials/github_voucher/；当时因等待可用认证而尚未创建仓库或公开上传。该历史阻碍已由下节的设备授权解除，旧副本已按用户授权清理。

## GitHub 公开发布（用户后续授权）

已完成 GitHub 官方设备授权并验证账号 jide315；公开仓库 https://github.com/jide315/uyghur-pos 已创建，main 已推送。提交 7ec9824419f9732451da9b5fadeeef1c16ab3727 的 [GitHub Actions 测试与构建](https://github.com/jide315/uyghur-pos/actions/runs/43541536829) 已通过。

Release 版本固定 v0.1.0，发行资产包括源码、C13、六模型实验、原始证据、wheel／sdist、发行清单和 SHA256SUMS。仓库与发行入口见 reports/P8-release-notes.md；资产上传与校验的最终状态以服务端核验及本机 operations/local/publication-status.json 为准。尚无第三方复现、反馈或采用证据。

本次有效授权保存在 credentials/gh/（目录 700、文件 600）。之前 github_voucher 的 Windows 脚本和旧项目副本已删除，共享连接说明已替换为当前 Linux GitHub CLI 配置引用；凭证不进入 Git 或 Release。
