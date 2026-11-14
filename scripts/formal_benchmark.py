#!/usr/bin/env python3
"""Five fresh processes per model, alternating order, no fastest-run selection."""
import argparse
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from uyghur_pos.data import write_json,digest

p=argparse.ArgumentParser();p.add_argument('--freeze',required=True)
p.add_argument('--data',default='data/ud/test.jsonl')
p.add_argument('--output',default='artifacts/final-benchmark');a=p.parse_args()
freeze=json.loads(Path(a.freeze).read_text())
for path,expected in freeze.get('source_sha256',{}).items():
    if digest(path)!=expected:raise ValueError(f'frozen source changed: {path}')
for path,expected in freeze['inputs_sha256'].items():
    if digest(path)!=expected:raise ValueError(f'frozen input changed: {path}')
for name,path in freeze['models'].items():
    if digest(path)!=freeze['model_sha256'][name]:raise ValueError(f'frozen model changed: {name}')
out=Path(a.output)
if out.exists():raise ValueError('new output directory required')
out.mkdir(parents=True)
models={'B0':'stanza',**freeze['benchmark_models']}
records={name:[] for name in models}
env=dict(os.environ,CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
for repeat in range(5):
    names=list(models)
    if repeat%2:names.reverse()
    for name in names:
        target=out/f'{name}-{repeat}.json'
        command=[sys.executable,'scripts/benchmark.py','--model',models[name],
            '--data',a.data,'--warmup-data','data/ud/dev.jsonl',
            '--output',str(target),'--rounds','1']
        start=time.perf_counter()
        with (out/f'{name}-{repeat}.stderr').open('w') as err:
            child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=err,text=True,env=env)
            first=child.stdout.readline()
            cold=time.perf_counter()-start
            if not json.loads(first).get('ready'):raise RuntimeError('missing first response')
            child.communicate(timeout=120)
            if child.returncode:raise RuntimeError(f'benchmark child failed: {name}')
        r=json.loads(target.read_text());r['cold_start_seconds']=cold
        write_json(target,r);records[name].append(r)
        print(name,repeat,'done',flush=True)
        write_json(out/'progress.json',{k:len(v) for k,v in records.items()})
summary={}
for name,runs in records.items():
    medians=[r['rounds'][0]['p50'] for r in runs]
    cv=statistics.pstdev(medians)/statistics.mean(medians)
    summary[name]=dict(p50=statistics.median(medians[:3]),
        p95=statistics.median([r['rounds'][0]['p95'] for r in runs[:3]]),
        rss=statistics.median([r['peak_rss_bytes'] for r in runs]),
        cold_start=statistics.median([r['cold_start_seconds'] for r in runs]),
        p50_cv=cv,stable=cv<=.1,fresh_processes=len(runs))
write_json(out/'summary.json',dict(models=summary,freeze_sha256=digest(a.freeze),
    protocol='First 3 fresh rounds for latency, all 5 for RSS/cold start; alternating order',
    data_sha256=digest(a.data)))
