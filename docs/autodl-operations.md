# AutoDL 操作说明

## 连接与保存

连接信息保存在本地项目 `credentials/autodl.json`，目录权限 700、文件权限 600，并由 `.gitignore` 排除。`credentials/known_hosts` 保存首次接入时取得的服务器主机密钥；此为首次信任记录，并非独立带外核验。

密码不进入命令行参数、不上传到训练机、不写入运行日志。SSH 由项目私有 askpass 程序读取密码。后续连接发现主机密钥变化时 SSH 会拒绝，需核查实例是否已更换。

```bash
cd /root/src/uyghur-nlp
python3 scripts/remote.py 'nvidia-smi'
python3 scripts/remote.py --upload
python3 scripts/remote.py --fetch artifacts
python3 scripts/remote.py --fetch runs
```

`--upload` 仅传源码、测试与文档，不传凭据、数据、结果或虚拟环境；显式加 `--include-models` 才会传入已下载的 Stanza 资源。`--fetch` 将指定的远端项目相对目录拷回本地，不接受绝对路径或父目录跳转。

`--fetch runs` 只包含已经有 `completion.json` 的训练目录，避免复制正在重写的 checkpoint；指定未完成训练目录会被拒绝。checkpoint 与 JSON 状态采用临时文件写完后原子替换。执行中任务仍以远端 PID 和日志判断，不因某次备份失败重启训练。

## 环境

远端项目：`/root/autodl-tmp/uyghur-nlp/`。

虚拟环境：`/root/autodl-tmp/uyghur-nlp/.venv/`，使用镜像的系统包（包括 PyTorch 2.3.0+cu121）。因此这是依赖基础镜像的隔离环境，不声称独立于基础镜像可复现；完整包版本保存在 `artifacts/environment.txt`。

非交互 SSH 默认找不到 `python`，请使用 `.venv/bin/python` 的明确路径。数据、模型和结果放在数据盘，仍需同步到本地备份。镜像、驱动和 GPU 实测记录见执行报告。

从同款基础镜像重建时，先上传源码，再运行 `bash scripts/bootstrap-autodl.sh`。它建立环境、安装项目、验证 GPU LSTM、保存环境信息并运行测试，不自动启动正式训练。模型资源需单独下载或用 `--upload --include-models` 从本地传入。

本地不需要安装 PyTorch 即可下载基线资源：`python3 scripts/download_stanza.py`。脚本固定资源版本、核对官方清单与三个已登记 MD5，已存在的正确文件不重复下载。完成后执行 `python3 scripts/remote.py --upload --include-models`。

## 后台任务

本轮已训练的候选为 `runs/lexical-seed13/best.pt`，监督对照为 `runs/supervised-seed13/best.pt`。可直接在远端使用 `echo '{"tokens":["مەن","بارىمەن","."]}' | .venv/bin/uyghur-pos predict --model runs/lexical-seed13/best.pt`；运行目录为远端项目根目录。

```bash
python3 scripts/remote.py 'cd /root/autodl-tmp/uyghur-nlp && .venv/bin/python scripts/run_job.py --name train-new --seconds 900 -- .venv/bin/python -m uyghur_pos.cli train --train data/ud/train.jsonl --dev data/ud/dev.jsonl --stats data/ud/training-stats.json --output runs/train-new --max-seconds 840'
```

任务独立于 SSH 会话。每个 job 名只能启动一次，状态位于 `artifacts/jobs/<名称>/status.json`，包含 worker PID、子进程 PID、退出码及截止时间，日志为同目录 `log.txt`。同名任务拒绝重复提交。状态文件为历史记录，判断是否仍运行需要结合远端 PID／进程命令；断线后不直接重启。

任务超时会终止其子进程组；训练每轮保存最佳模型和历史。当前训练不支持优化器状态续训：中断后可以读取已保存的最佳 checkpoint 做推理，重新训练必须使用新 run ID，不能冒称无缝续训。

## 费用与停止

用户提供页面单价为 0.60 元／小时，账户余额曾显示 10 元，实际余额与收费由控制台为准。本轮仅执行短期验证与首轮训练，不充值、不包时段、不创建其他实例。

脚本中的任务截止时间只停止任务，不关闭 AutoDL 实例。实例保持开机仍可能计费；所有结果同步后，在控制台停止实例即可结束 GPU 占用，存储计费按平台规则另核。没有平台控制凭据时，SSH 无法证明平台已关机或停止计费。
