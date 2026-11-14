# P7：干净 CPU 环境复现（阶段记录）

2026-11-13 UTC。

本地用 `python3 -m venv .venv-reproduce` 创建**不继承系统包**的环境，安装官方 CPU PyTorch 2.3.0+cpu，再安装项目及固定的 Stanza／pytest。这与远端继承基础镜像系统包的 .venv 分开。

执行证据：

- `artifacts/clean-install.log`：从零安装依赖与 editable 包。
- `artifacts/clean-environment.txt`：完整包版本。
- `artifacts/clean-tests.txt`：6 passed in 11.87s。
- `artifacts/clean-pip-check.txt`：No broken requirements found。
- `artifacts/clean-lexical-dev.predictions.jsonl` 与远端原 `lexical-dev.predictions.jsonl` 逐字节一致。

因此已证明：同一个已保存 checkpoint 在干净 CPU 环境可以安装、加载、推理并复现开发集预测。没有据此声称重新训练或第三方独立复现；最终发行模型确定后还需用它再次复现、打包并核查模型卡。
