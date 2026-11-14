# 数据与模型来源

本项目原创代码采用 MIT 许可（见 LICENSE），不覆盖下列数据、外部模型和资源。

- 本项目的数据准备脚本固定下载 UD Uyghur-UDT r2.15，commit `77a1c20dae6650284c4c50959833ea2485c5119a`。
- 语料作者及许可见下载后的 `data/ud/raw/README.md` 与 `LICENSE.txt`；语料为 CC BY-SA 4.0，不归本项目代码许可覆盖。
- Stanza 基线使用官方 stanza-ug v1.10.0 资源清单中的 `tokenize/udt`、`pos/udt_nocharlm`、`pretrain/conll17`。校验官方 MD5，并记录本地 SHA-256。
- 已读取官方 `stanza-ug` **v1.10.0** 模型卡，其许可字段为 Apache-2.0，与实际使用资源版本相同，副本保存在 `artifacts/provenance/hf-version-card.txt`。模型资源来源 https://huggingface.co/stanfordnlp/stanza-ug/tree/v1.10.0 。代码许可与模型资源许可分别记录，不把两者混同。
- 使用 UD 标注及外部词向量训练的学生发行候选将保守地保留 CC BY-SA 4.0 数据署名／相同方式共享说明及 Apache-2.0 资源声明；不将权重标为本项目代码的 MIT 许可。实际公开发布另记。
- 学生模型初版只使用官方训练切分。开发集用于选择模型；测试集未用于训练、词表生成、早停或本轮性能反馈。

参考：https://github.com/UniversalDependencies/UD_Uyghur-UDT 、https://github.com/stanfordnlp/stanza 。
