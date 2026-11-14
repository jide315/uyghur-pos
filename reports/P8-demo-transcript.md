# 实际 CPU 演示记录

使用安装后的 wheel，在源码目录之外运行冻结 C13，无需访问网络。以下示例是工具行为演示，语言标签未获专家重新裁决。

```bash
printf '%s\n' '{"tokens":["مەن","بارىمەن","."]}' | uyghur-pos predict --model model/model.pt
```

```json
{"tokens": ["مەن", "بارىمەن", "."], "upos": ["PRON", "VERB", "PUNCT"]}
```

空列表输出：
```json
{"tokens": [], "upos": []}
```

数字 token、非法 JSON、513 词、129 码点词均实际退出 2，错误可见，无静默截断。OOV 输入保留原词且输出一个标签。完整 900 句 test 在安装环境复现退出 0，预测与首次正式 C13 逐字节一致。

运行输出与耗时见 evidence 包 artifacts/final-wheel-reproduction.json；这里耗时含进程启动，不能替代 P6 的正式单句时延。

3–5 分钟讲解顺序与质量／资源对照见 P8-portfolio.md 和 P6-final-evaluation.md。
