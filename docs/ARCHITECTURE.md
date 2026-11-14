# 实现与实验数据流

```mermaid
flowchart LR
    UD[固定版本 UD] --> Audit[解析及重复审计]
    Audit --> Train[train / 词表及统计]
    Audit --> Dev[dev / 错误分析及选优]
    Audit --> Test[test / 冻结后评分]
    Vectors[固定公开词向量] --> Student[字符 GRU + 词 BiLSTM]
    Train --> Student
    Dev --> Student
    Teacher[官方 Stanza 基线] --> Comparison[同词边界对照]
    Student --> Comparison
    Comparison --> Freeze[配置与权重哈希冻结]
    Freeze --> Test
    Test --> Gates[质量及资源验收]
    Gates --> Package[候选包 / 报告 / 求职演示]
```

`src/uyghur_pos` 提供数据、模型、训练、评测和推理；`scripts` 提供实验管理、正式评测与打包；`reports` 记录假设及证据。私有 SSH 凭据不参与任何训练或发行包。

所有模型输入为预分词的词序列。字符编码不改变词边界；padding 只用于批处理，句子／字符循环网络都使用长度感知的 packing，避免 padding 影响双向表示。损失忽略填充位置。

同一统计口径贯穿所有模型，OOV 始终按标注 train 定义；外部词向量词典的覆盖不改变这个定义。性能报告区分纯训练时间、完整运行时间、冷启动、预热后延迟和绝对峰值内存。

正式评分之前冻结所有候选、对照、种子、发行权重和输入哈希。评分之后不覆盖结果或回头改门槛；实现修复若影响测试，必须另作受污染评测记录。
