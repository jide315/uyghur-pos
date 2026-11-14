import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import time
from .data import read_jsonl, write_json, write_jsonl, validate_tokens, digest
from .metrics import evaluate

def parser():
    p=argparse.ArgumentParser(description='Uyghur pretokenized UPOS experiments')
    sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('prepare'); q.add_argument('--output',default='data/ud')
    q=sub.add_parser('train')
    for name in ['train','dev','stats','output']: q.add_argument('--'+name,required=True)
    q.add_argument('--device',choices=['cpu','cuda'],default='cuda')
    q.add_argument('--teacher'); q.add_argument('--alpha',type=float,default=.25)
    q.add_argument('--pretrain',help='Optional official Stanza conll17 word vectors; vocabulary source is recorded')
    q.add_argument('--freeze-words',action='store_true',help='Keep pretrained word embeddings fixed')
    q.add_argument('--word-dropout',type=float,default=0.)
    q.add_argument('--no-chars',action='store_true')
    for name,default in [('seed',13),('threads',1),('epochs',40),('patience',6),
                         ('batch-size',32),('hidden',128),('char-hidden',32),('limit',0),('max-seconds',1800)]:
        q.add_argument('--'+name,type=int,default=default)
    q.add_argument('--lr',type=float,default=.003)
    q=sub.add_parser('predict'); q.add_argument('--model',required=True)
    q.add_argument('--threads',type=int,default=1)
    q=sub.add_parser('evaluate')
    for name in ['gold','predictions','stats','output']: q.add_argument('--'+name,required=True)
    q=sub.add_parser('student-eval')
    for name in ['model','data','stats','output']: q.add_argument('--'+name,required=True)
    q.add_argument('--threads',type=int,default=1)
    q=sub.add_parser('baseline')
    for name in ['data','stats','output']: q.add_argument('--'+name,required=True)
    q.add_argument('--models',default='models/stanza'); q.add_argument('--download',action='store_true')
    q=sub.add_parser('dictionary')
    for name in ['train','data','stats','output']: q.add_argument('--'+name,required=True)
    return p

def score(args,rows,pred):
    stats=json.loads(Path(args.stats).read_text())
    result=evaluate(rows,pred,stats['frequencies'],stats['long_threshold'])
    write_json(args.output,result)
    return result

def main():
    args=parser().parse_args()
    try:
        if args.command=='prepare':
            from .prepare import prepare
            print(json.dumps(prepare(args.output),ensure_ascii=False,indent=2)); return
        if args.command=='train':
            if not 0<=args.alpha<=1: raise ValueError('alpha must be between 0 and 1')
            if args.freeze_words and not args.pretrain:
                raise ValueError('--freeze-words requires --pretrain')
            from .train import train
            train(args); return
        if args.command=='evaluate':
            print(json.dumps(score(args,read_jsonl(args.gold),read_jsonl(args.predictions)))); return
        if args.command=='predict':
            import torch
            from .model import load_model,predict
            torch.set_num_threads(args.threads)
            model,state=load_model(args.model)
            for n,line in enumerate(sys.stdin,1):
                try:
                    row=json.loads(line)
                    if not isinstance(row,dict) or 'tokens' not in row: raise ValueError('tokens field required')
                    validate_tokens(row['tokens'])
                    pred=predict(model,[row],state['vocab'])[0]['upos'] if row['tokens'] else []
                    print(json.dumps(dict(tokens=row['tokens'],upos=pred),ensure_ascii=False),flush=True)
                except (ValueError,TypeError,KeyError) as e:
                    raise ValueError(f'line {n}: {e}') from e
            return
        if args.command=='student-eval':
            import torch
            from .model import load_model,predict
            torch.set_num_threads(args.threads)
            rows=read_jsonl(args.data); model,state=load_model(args.model)
            pred=predict(model,rows,state['vocab'])
        elif args.command=='baseline':
            import torch
            import stanza
            torch.set_num_threads(1)
            if args.download:
                stanza.download('ug',model_dir=args.models,package='udt',processors='tokenize,pos')
            nlp=stanza.Pipeline('ug',dir=args.models,package='udt',processors='tokenize,pos',
                                tokenize_pretokenized=True,use_gpu=False,download_method=None)
            rows=read_jsonl(args.data); pred=[]; timings=[]
            for row in rows:
                start=time.perf_counter()
                doc=nlp([row['tokens']])
                timings.append(time.perf_counter()-start)
                words=[w for s in doc.sentences for w in s.words]
                pred.append(dict(sent_id=row['sent_id'],tokens=[w.text for w in words],upos=[w.upos for w in words]))
            write_json(Path(args.output).with_suffix('.timings.json'),dict(seconds=timings,
                note='Exploratory single pass; not a formal CPU benchmark',stanza=stanza.__version__,
                input_sha256=digest(args.data)))
        else:
            rows=read_jsonl(args.data); training=read_jsonl(args.train)
            lookup={}; totals=Counter()
            for r in training:
                for w,y in zip(r['tokens'],r['upos']):
                    lookup.setdefault(w,Counter())[y]+=1; totals[y]+=1
            default=totals.most_common(1)[0][0]
            pred=[dict(sent_id=r['sent_id'],tokens=r['tokens'],
                 upos=[lookup[w].most_common(1)[0][0] if w in lookup else default for w in r['tokens']]) for r in rows]
        write_jsonl(Path(args.output).with_suffix('.predictions.jsonl'),pred)
        print(json.dumps(score(args,rows,pred)['groups'],indent=2))
    except (ValueError,RuntimeError,OSError) as e:
        print(f'error: {e}',file=sys.stderr); raise SystemExit(2)

if __name__=='__main__': main()
