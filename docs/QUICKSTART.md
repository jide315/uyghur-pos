# 快速使用与演示

## 使用已训练模型

准备 Python 3.12，将单独取得的模型包放到源码目录的 `dist/` 下（需要时先创建该目录），然后在源码根目录建立虚拟环境：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-cpu.txt
.venv/bin/python -m pip install .
mkdir -p model
tar -xzf dist/uyghur-pos-0.1.0-model.tar.gz -C model
printf '%s\n' '{"tokens":["مەن","بارىمەن","."]}' | .venv/bin/uyghur-pos predict --model model/model.pt
```

源码包与模型包单独分发；若只拿到源码，先按 README 训练，或取得模型候选包。不要把示例中的词序翻转。

输入必须已分词。输出保留原始词，附加等长 UPOS 列表。空 tokens 返回空标签，非法 JSON、数字 token 或超过长度限制会退出并给出错误；不会静默丢词。

## 复现质量

```bash
.venv/bin/uyghur-pos prepare
.venv/bin/uyghur-pos student-eval --model model/model.pt --data data/ud/test.jsonl --stats data/ud/training-stats.json --output artifacts/reproduced-test.json
```

测试分数公开后，此命令用于复现既有结果，不能将反复调参后的分数称为新的盲测。完整同容量对照、种子和数据哈希见最终报告及冻结清单。

## 求职演示顺序

1. 展示输入输出边界、公开数据版本与切分隔离。
2. 展示失败配置与改进登记，解释为什么冻结词向量及容量调整没有被采用。
3. 现场运行正常、空列表和非法输入的 CLI 示例。
4. 打开最终质量／资源表及逐种子结果，区分准确率、OOV、速度和内存。
5. 展示发行包哈希、干净环境复现证据、许可证及未覆盖的使用场景。

项目不需要常驻 GPU 推理服务；模型准备完成后可在 CPU 离线运行。AutoDL 的训练实例可以在结果回收后由控制台停止，是否停机需按实际平台状态确认。
