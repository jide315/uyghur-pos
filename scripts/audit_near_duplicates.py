#!/usr/bin/env python3
import argparse
from pathlib import Path
from uyghur_pos.data import read_jsonl,write_json,digest
from uyghur_pos.audit import near_duplicates

p=argparse.ArgumentParser();p.add_argument('--data',default='data/ud')
p.add_argument('--output',default='artifacts/near-duplicates.json');a=p.parse_args()
root=Path(a.data)
rows={s:read_jsonl(root/f'{s}.jsonl') for s in ['train','dev','test']}
result=dict(method='token SequenceMatcher ratio >= 0.90 with multiset upper-bound pruning; no model predictions',
            input_sha256={s:digest(root/f'{s}.jsonl') for s in rows},pairs={})
for x,y in [('train','dev'),('train','test'),('dev','test')]:
    matches=near_duplicates(rows[x],rows[y]);result['pairs'][f'{x}:{y}']=matches
    print(x,y,len(matches),flush=True)
write_json(a.output,result)
