#!/usr/bin/env python3
"""One fresh-process measurement; retain all runs, never select fastest."""
import argparse
import json
import resource
import time
from pathlib import Path
import statistics
import torch
from uyghur_pos.data import read_jsonl,write_json,digest
from uyghur_pos.model import load_model,predict

p=argparse.ArgumentParser()
p.add_argument('--model',required=True,help='checkpoint path, or stanza')
p.add_argument('--data',required=True);p.add_argument('--output',required=True)
p.add_argument('--models',default='models/stanza');p.add_argument('--rounds',type=int,default=3)
p.add_argument('--warmup-data',help='Fixed dev data for warmup during final test measurements')
args=p.parse_args()
torch.set_num_threads(1)
start=time.perf_counter()
if args.model=='stanza':
    import stanza
    nlp=stanza.Pipeline('ug',dir=args.models,processors='tokenize,pos',package='udt',
                        tokenize_pretokenized=True,use_gpu=False,download_method=None,verbose=False)
    def infer(row):
        doc=nlp([row['tokens']])
        return dict(tokens=row['tokens'],upos=[w.upos for s in doc.sentences for w in s.words])
else:
    model,state=load_model(args.model)
    def infer(row):return predict(model,[row],state['vocab'],batch_size=1)[0]
load_seconds=time.perf_counter()-start
rows=read_jsonl(args.data)
first=infer(dict(tokens=rows[0]['tokens']))
print(json.dumps(dict(ready=True,first=first),ensure_ascii=False),flush=True)
warmup=read_jsonl(args.warmup_data) if args.warmup_data else rows
for row in warmup[:30]: infer(row)
rounds=[]
for _ in range(args.rounds):
    samples=[]
    for row in rows:
        text=json.dumps(dict(tokens=row['tokens']),ensure_ascii=False)
        t=time.perf_counter()
        inp=json.loads(text); result=infer(inp); json.dumps(result,ensure_ascii=False)
        samples.append(time.perf_counter()-t)
    ordered=sorted(samples)
    rounds.append(dict(seconds=samples,p50=statistics.median(samples),
        p95=ordered[min(len(ordered)-1,int(.95*len(ordered)))],
        tokens_per_second=sum(len(r['tokens']) for r in rows)/sum(samples)))
write_json(args.output,dict(model=args.model,data_sha256=digest(args.data),rounds=rounds,
    load_seconds=load_seconds,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
    note='Single fresh process; formal protocol requires 5 processes for RSS/cold-start.'))
