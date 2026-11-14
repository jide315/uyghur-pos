#!/usr/bin/env python3
"""Development errors only. Does not read test predictions."""
import argparse
import json
from pathlib import Path
from uyghur_pos.data import read_jsonl,write_json

p=argparse.ArgumentParser()
p.add_argument('--gold',required=True);p.add_argument('--predictions',required=True)
p.add_argument('--stats',required=True);p.add_argument('--output',required=True)
args=p.parse_args()
gold=read_jsonl(args.gold);pred=read_jsonl(args.predictions)
stats=json.loads(Path(args.stats).read_text())
if len(gold)!=len(pred): raise ValueError('sentence count mismatch')
errors=[]
for g,r in zip(gold,pred):
    if g['tokens']!=r['tokens'] or len(g['upos'])!=len(r['upos']): raise ValueError('alignment mismatch')
    for i,(word,y,z) in enumerate(zip(g['tokens'],g['upos'],r['upos'])):
        if y!=z:
            errors.append(dict(sent_id=g['sent_id'],word_id=i+1,word=word,gold=y,predicted=z,
                              train_frequency=stats['frequencies'].get(word,0),length=len(word),
                              interpretation='Disagrees with dataset label; not expert adjudication'))
write_json(args.output,dict(error_count=len(errors),examples=errors[:100]))
