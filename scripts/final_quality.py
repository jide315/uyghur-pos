#!/usr/bin/env python3
"""Score frozen models once, preserve all seeds and sentence-level uncertainty."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
from uyghur_pos.data import read_jsonl,write_json,digest

p=argparse.ArgumentParser();p.add_argument('--freeze',required=True)
p.add_argument('--output',default='artifacts/final-quality');p.add_argument('--authorize-test',action='store_true')
a=p.parse_args()
if not a.authorize_test:p.error('test scoring requires frozen configuration and --authorize-test')
freeze=json.loads(Path(a.freeze).read_text());out=Path(a.output)
for path,expected in freeze.get('source_sha256',{}).items():
    if digest(path)!=expected:raise ValueError(f'frozen source changed: {path}')
for path,expected in freeze['inputs_sha256'].items():
    if digest(path)!=expected:raise ValueError(f'frozen input changed: {path}')
if out.exists():raise ValueError('output already exists; never overwrite a test record')
out.mkdir(parents=True)
for name,path in freeze['models'].items():
    if digest(path)!=freeze['model_sha256'][name]:raise ValueError(f'model changed: {name}')
subprocess.run([sys.executable,'-m','uyghur_pos.cli','baseline','--data','data/ud/test.jsonl',
    '--stats','data/ud/training-stats.json','--output',str(out/'B0.json')],check=True)
for name,path in freeze['models'].items():
    subprocess.run([sys.executable,'-m','uyghur_pos.cli','student-eval','--model',path,
        '--data','data/ud/test.jsonl','--stats','data/ud/training-stats.json',
        '--output',str(out/f'{name}.json')],check=True)
gold=read_jsonl('data/ud/test.jsonl');teacher=read_jsonl(out/'B0.predictions.jsonl')
def counts(pred,nonpunct):
    good=[];total=[]
    for g,r in zip(gold,pred):
        if g['tokens']!=r['tokens']:raise ValueError('unaligned predictions')
        mask=[y!='PUNCT' if nonpunct else True for y in g['upos']]
        good.append(sum(m and y==z for m,y,z in zip(mask,g['upos'],r['upos'])))
        total.append(sum(mask))
    return np.array(good),np.array(total)
intervals={}
indices=np.random.default_rng(13).integers(0,len(gold),size=(1000,len(gold)))
for name in freeze['models']:
    pred=read_jsonl(out/f'{name}.predictions.jsonl');intervals[name]={}
    for label,nonpunct in [('overall',False),('nonpunct',True)]:
        t,n=counts(teacher,nonpunct);s,_=counts(pred,nonpunct)
        delta=(s[indices].sum(1)-t[indices].sum(1))/n[indices].sum(1)
        intervals[name][label]=dict(delta=float((s.sum()-t.sum())/n.sum()),
            lower=float(np.quantile(delta,.025)),upper=float(np.quantile(delta,.975)))
write_json(out/'bootstrap.json',intervals)
write_json(out/'manifest.json',dict(freeze_sha256=digest(a.freeze),test_sha256=digest('data/ud/test.jsonl'),
    note='First frozen test evaluation. No model selection based on these scores.'))
