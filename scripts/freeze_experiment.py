#!/usr/bin/env python3
"""Freeze a fully specified candidate and same-capacity control before test."""
import argparse,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
from uyghur_pos.data import write_json,digest

p=argparse.ArgumentParser();p.add_argument('--candidate',required=True)
p.add_argument('--control',required=True);p.add_argument('--output',default='artifacts/final-freeze.json')
a=p.parse_args()
if Path(a.output).exists():raise ValueError('freeze already exists; never overwrite')
models={};hashes={};candidates=[];controls=[];scores={}
for prefix,config in [('C',a.candidate),('S',a.control)]:
    for seed in [13,42,2026]:
        name=f'{prefix}{seed}';root=Path('runs')/f'{config}-seed{seed}'
        if not (root/'completion.json').exists():raise ValueError(f'incomplete run: {root}')
        model=str(root/'best.pt');models[name]=model;hashes[name]=digest(model)
        metric=json.loads((root/'dev-metrics.json').read_text())['groups']['nonpunct']['accuracy']
        (candidates if prefix=='C' else controls).append(name);scores[name]=metric
release=sorted(candidates,key=lambda n:(-scores[n],int(n[1:])))[0]
inputs=['data/ud/train.jsonl','data/ud/dev.jsonl','data/ud/test.jsonl','data/ud/training-stats.json',
        'models/stanza/resources.json','models/stanza/ug/pos/udt_nocharlm.pt',
        'models/stanza/ug/pretrain/conll17.pt','models/stanza/ug/tokenize/udt.pt']
record=dict(created_utc=datetime.now(timezone.utc).isoformat(),candidate_config=a.candidate,
    control_config=a.control,seeds=[13,42,2026],models=models,model_sha256=hashes,
    inputs_sha256={path:digest(path) for path in inputs},benchmark_models=models,
    candidates=candidates,controls=controls,release_model=release,
    release_selection='Highest dev nonpunct, ties by smaller numerical seed',
    dev_nonpunct=scores,resource_target='latency',quality_loss_pp=1.,worst_seed_loss_pp=1.5,
    oov_loss_pp=2.,speedup=2.,protocol_sha256=digest('docs/plans/05-evaluation-protocol.md'),
    source_sha256={str(f):digest(f) for directory in ['src','scripts'] for f in sorted(Path(directory).rglob('*')) if f.is_file() and f.suffix in {'.py','.sh'}})
write_json(a.output,record);print('Frozen',a.candidate,'vs',a.control,'release',release)
