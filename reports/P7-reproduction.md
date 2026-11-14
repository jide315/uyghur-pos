# P7：安装、模型和预测复现

2026-11-13 UTC。P6 权重已冻结，复现不参与候选选择。

## 干净环境

以不继承系统包的 `.venv-reproduce` 安装官方 CPU PyTorch 2.3.0+cpu、依赖及源码；完整记录见 P7-clean-environment.md。当前 9 项测试通过，包含模型／padding／指标、软蒸馏和备份竞争的回归检查。

## 真正安装 wheel

运行 `python -m build` 得到 wheel 与 sdist，再用 `pip install --no-deps --force-reinstall dist/uyghur_pos-0.1.0-py3-none-any.whl` 替换 editable 安装。

随后从源码树以外的临时目录运行 CLI，确认包实际位于 `site-packages`，使用冻结 C13 权重对完整 test 复现，预测 JSONL 与远端首次正式结果逐字节一致。非法 token 输入返回退出码 2。证据：

- `artifacts/wheel-install.log`
- `artifacts/wheel-reproduction.json`
- `artifacts/wheel-evaluation.log`
- `artifacts/wheel-test.predictions.jsonl`

由此证明 wheel 中代码能够独立于源码 editable 链接加载模型、执行推理并复现冻结预测；不是依赖当前工作目录偷用源码。

## 训练复现范围

GPU 侧已执行多个固定种子及同容量监督／蒸馏对照，逐次保存 train/dev/teacher/source 哈希和配置。没有声称外部第三方复现，也没有为了训练复现再花一遍相同 seed 的费用。最终发行包给出固定依赖、版本、数据准备与训练命令，复现限制如实保留。

## 发行边界

原创代码 MIT；学生权重单独保留 CC BY-SA 4.0 与外部 Apache-2.0 声明及完整许可。凭据、虚拟环境、缓存和无关文件排除。2026-11-14 完整资源恢复轮已 PASS，模型卡与性能报告已据此定稿；源码已公开于 [GitHub 仓库](https://github.com/jide315/uyghur-pos)，v0.1.0 发行入口见 [发行说明](P8-release-notes.md)。本报告记录项目自身复现，尚无第三方独立复现证据。

## 交付前核查

重新构建 wheel 并安装，在源码树外实测正常词句、空列表、OOV、数字 token、非法 JSON、超长句及超长词；非法输入退出 2。完整 900 句 test 再次复现预测逐字节一致，命令输出及耗时在 artifacts/final-wheel-reproduction.json，现场演示文本在 P8-demo-transcript.md。

原冻结的 32 个源码文件、8 个输入资源、6 个模型及协议共 47 项 SHA-256 均一致，证据 artifacts/local-freeze-verification.json。文档和许可补齐没有改训练／评测行为。源码／权重／实验模型／证据候选包与哈希已准备，最终资源验收 PASS；第一次 INCONCLUSIVE 和关机中断记录均保留。

## 最终发行检查

最终 wheel 的每个包内源码文件均须与冻结哈希一致；模型包解出的 model.pt 必须与冻结 C13 一致。从源码树外使用安装后的最终 wheel，加载实际模型包，执行正常／空列表／非法输入及完整 test 预测复现；结果保存在 artifacts/final-delivery-runtime.json。该复现不参与任何选优，也不覆盖首次质量记录。

发行 source 包显式保留 .gitignore，排除 backups、credentials、运行缓存与虚拟环境。原始依赖锁定、固定模型下载、可移植训练／评测命令和全部来源许可随源码给出。最终包成员及凭据排除检查在 artifacts/release-package-audit.json，六个分发文件的 SHA-256 在 dist/release-manifest.json 和 SHA256SUMS。
