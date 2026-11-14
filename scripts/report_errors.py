#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from collections import Counter
from uyghur_pos.data import read_jsonl
from uyghur_pos.metrics import evaluate

p=argparse.ArgumentParser();p.add_argument('--predictions',required=True)
p.add_argument('--name',required=True);a=p.parse_args()
gold=read_jsonl('data/ud/dev.jsonl');pred=read_jsonl(a.predictions)
teacher=read_jsonl('artifacts/stanza-dev.predictions.jsonl')
stats=json.loads(Path('data/ud/training-stats.json').read_text())
scores=evaluate(gold,pred,stats['frequencies'],stats['long_threshold'])
errors=[]
for g,r,b in zip(gold,pred,teacher):
    for i,(w,y,z,t) in enumerate(zip(g['tokens'],g['upos'],r['upos'],b['upos'])):
        if y!=z:
            errors.append(dict(sentence=g['sent_id'],id=i+1,word=w,gold=y,pred=z,teacher=t,
                               frequency=stats['frequencies'].get(w,0)))
errors.sort(key=lambda r:(r['frequency']!=0,r['teacher']!=r['gold'],r['sentence'],r['id']))
selected=[];seen=set()
for row in errors:
    if row['sentence'] not in seen:
        selected.append(row);seen.add(row['sentence'])
    if len(selected)>=20:break
lines=['# P5：开发集错误分析', '',f'候选：{a.name}；本报告只读取 dev，不读取 test。', '',
       '标签仅代表现有 UD 标注，不声称语言学专家已裁决。所列词例来自 UD Uyghur-UDT（CC BY-SA 4.0），来源与作者见 NOTICE。', '',
       '| 群体 | 词数 | 错误数 | 准确率 |','| --- | ---: | ---: | ---: |']
for name,r in scores['groups'].items():
    value=f'{r["accuracy"]*100:.3f}%' if r['n'] else 'N/A'
    lines.append(f'| {name} | {r["n"]} | {r["n"]-r["correct"]} | {value} |')
lines += ['', '## 可定位错误样例', '',
          '优先列出 OOV 且教师正确、候选错误的不同句子，以检查差距；这是定向样例，不是随机抽样。', '',
          '| 句 ID | 词 ID | 原词 | Gold | 候选 | 教师 | Train 频次 |',
          '| --- | ---: | --- | --- | --- | --- | ---: |']
for r in selected:
    word=r['word'].replace('|','\\|')
    lines.append(f'| {r["sentence"]} | {r["id"]} | {word} | {r["gold"]} | {r["pred"]} | {r["teacher"]} | {r["frequency"]} |')
lines += ['', '## 解释边界', '',
          '数据标签与预测可机械比较；样例不支持自行改 Gold。未登录词与已见词的差异是群体观察，不能独立证明机制；相应干预、容量变化和失败对照见各实验登记与结果。', '']
Path('reports/P5-error-analysis.md').write_text('\n'.join(lines))
