# P3：AutoDL 部署与验证

日期：2026-11-13（UTC）。

实际接入用户提供的 AutoDL 实例，项目目录 `/root/autodl-tmp/uyghur-nlp/`。

| 项目 | 实测 |
| --- | --- |
| GPU | NVIDIA GeForce GTX 1080 Ti，11264 MiB，单卡 |
| 驱动 | 535.129.03 |
| 镜像 Python | 3.12.3 |
| PyTorch | 2.3.0+cu121 |
| PyTorch CUDA runtime | 12.1 |
| 操作系统 | Ubuntu 22.04.3 LTS |
| 数据盘 | 50 GiB，项目部署前基本为空 |
| Stanza | 1.10.1 |
| pytest | 8.3.5 |

非交互 SSH 无默认 python PATH，使用镜像 `/root/miniconda3/bin/python` 创建带系统包的虚拟环境。没有替换 CUDA、驱动或已有 PyTorch。

验证证据：

- CUDA 可用；随机输入送入 GPU LSTM，前向与反向传播均通过。
- 远端测试：5 passed。
- 后台任务 `detached-smoke` 在一个 SSH 会话提交，在另一会话取到 complete、exit_code=0，实际约 5 秒，证明任务独立于连接。
- 32 句 overfit 检查约 5 秒，达到 100%（仅训练管道检查），GPU 峰值 allocated 约 40.8 MiB；不是显存总用量，也不是完整训练占用。
- 最佳 checkpoint 回收到本地，SHA-256 与远端 completion 中记录一致。

原始记录：`artifacts/environment.txt`、`nvidia-smi.txt`、`cpu.txt`、`disks.txt`、`jobs/*/status.json`、`runs/overfit-pipeline/completion.json`。

Stanza 远端直接下载连接停滞，已终止该次有界下载任务；改为本地下载官方文件并按官方资源 MD5 验证，显式上传，不修改模型内容。失败日志保留在 `artifacts/first-run.log`。

当前具备 SSH 接入、源码同步、后台限时运行、日志与结果回收能力。优化器状态续训尚未实现，不能声称训练无缝恢复。文件位于数据盘且有本地备份，不宣称平台磁盘绝对可靠。

页面参考单价 0.60 元／小时，本轮执行短期验证与一次有界训练；费用只是按运行时间估算，SSH 无法读取平台实际余额／扣费。未充值、未创建新机器，完成后需在控制台确认是否停止实例。
