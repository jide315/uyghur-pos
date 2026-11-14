#!/usr/bin/env python3
"""Summarize development results without ever opening test predictions."""
import json
from pathlib import Path
import statistics
from uyghur_pos.data import write_json

result={}
for config in ['supervised','lexical','frozen','worddrop','refined','distilled']:
    entries=[]
    for seed in [13,42,2026]:
        root=Path('runs')/f'{config}-seed{seed}'
        if not (root/'completion.json').exists():continue
        metrics=json.loads((root/'dev-metrics.json').read_text())['groups']
        entries.append(dict(seed=seed,checkpoint=str(root/'best.pt'),
            **{k:metrics[k]['accuracy'] for k in ['overall','nonpunct','oov','seen']}))
    if entries:
        result[config]=dict(runs=entries,mean={k:statistics.mean(x[k] for x in entries)
            for k in ['overall','nonpunct','oov','seen']},
            sd={k:statistics.stdev(x[k] for x in entries) if len(entries)>1 else None
                for k in ['overall','nonpunct','oov','seen']})
write_json('artifacts/development-summary.json',result)
for name,r in result.items():print(name,len(r['runs']),{k:round(v*100,3) for k,v in r['mean'].items()})
