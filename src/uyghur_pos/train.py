import copy
import json
from pathlib import Path
import random
import time
import numpy as np
import torch
from torch.nn import functional as F
from .data import digest, read_jsonl, write_json, write_jsonl
from .metrics import evaluate
from .model import Tagger, batch, predict, vocabulary
from .losses import soft_distillation

def train(args):
    torch.set_num_threads(args.threads)
    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    if args.device == 'cuda': torch.cuda.manual_seed_all(args.seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    train_rows = read_jsonl(args.train)
    if args.limit: train_rows = train_rows[:args.limit]
    dev_rows = read_jsonl(args.dev)
    teacher = read_jsonl(args.teacher) if args.teacher else None
    if teacher:
        if len(teacher)!=len(train_rows): raise ValueError('teacher sentence count mismatch')
        for row,t in zip(train_rows,teacher):
            if row['tokens']!=t['tokens'] or len(t['upos'])!=len(row['tokens']):
                raise ValueError('teacher token alignment mismatch')
    vocab = vocabulary(train_rows)
    config = dict(hidden=args.hidden,char_hidden=args.char_hidden,use_chars=not args.no_chars,word_dropout=args.word_dropout)
    pretrained = None
    if args.pretrain:
        from stanza.models.common.pretrain import Pretrain
        pretrained = Pretrain(args.pretrain)
        # Fixed external vocabulary, never constructed from dev/test. OOV metrics
        # remain defined against annotated train, not this external dictionary.
        external = set(pretrained.vocab._id2unit[4:])
        vocab['words']={word:i+2 for i,word in enumerate(sorted(set(vocab['words']) | external))}
        config['word_dim']=int(pretrained.emb.shape[1])
    model = Tagger(vocab,**config).to(args.device)
    if pretrained is not None:
        with torch.no_grad():
            for word,index in vocab['words'].items():
                pre_id=pretrained.vocab.unit2id(word)
                if pre_id>1:
                    model.words.weight[index].copy_(pretrained.emb[pre_id].to(args.device))
        # Fine-tuning is permitted, but fixed dropout and capacity keep the
        # comparison focused on external lexical information, not extra labels.
    if args.freeze_words:
        model.words.weight.requires_grad_(False)
    optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad),lr=args.lr)
    stats = json.loads(Path(args.stats).read_text())
    out = Path(args.output)
    if out.exists(): raise ValueError('output directory already exists; choose a new run ID')
    out.mkdir(parents=True)
    start = time.monotonic(); best=-1.; stale=0; history=[]
    provenance = dict(train_sha256=digest(args.train),dev_sha256=digest(args.dev),
        teacher_sha256=digest(args.teacher) if args.teacher else None,
        pretrain_sha256=digest(args.pretrain) if args.pretrain else None,
        stats_sha256=digest(args.stats),seed=args.seed,arguments=vars(args),
        torch=torch.__version__,cuda=torch.version.cuda,parameters=sum(p.numel() for p in model.parameters()),
        trainable_parameters=sum(p.numel() for p in model.parameters() if p.requires_grad))
    write_json(out/'run.json',provenance)
    for epoch in range(1,args.epochs+1):
        if time.monotonic()-start > args.max_seconds: break
        model.train(); order=list(range(len(train_rows))); random.shuffle(order)
        total_loss=0.; total_tokens=0
        for offset in range(0,len(order),args.batch_size):
            indices=order[offset:offset+args.batch_size]
            rows=[train_rows[i] for i in indices]
            words,chars,clens,lens,y=batch(rows,vocab,args.device)
            optimizer.zero_grad(set_to_none=True)
            logits=model(words,chars,clens,lens)
            loss=F.cross_entropy(logits.reshape(-1,len(vocab['labels'])),y.reshape(-1),ignore_index=-100)
            if teacher:
                trows=[teacher[i] for i in indices]
                if 'probabilities' in trows[0]:
                    temperatures={r['temperature'] for r in trows}
                    if len(temperatures)!=1:raise ValueError('mixed teacher temperatures')
                    targets=torch.zeros_like(logits)
                    for i,r in enumerate(trows):
                        if r['labels']!=vocab['labels']:raise ValueError('teacher class ordering mismatch')
                        targets[i,:len(r['tokens'])]=torch.tensor(r['probabilities'],device=args.device)
                    tloss=soft_distillation(logits,targets,y!=-100,next(iter(temperatures)))
                else:
                    *_,ty=batch(trows,vocab,args.device)
                    tloss=F.cross_entropy(logits.reshape(-1,len(vocab['labels'])),ty.reshape(-1),ignore_index=-100)
                loss=(1-args.alpha)*loss+args.alpha*tloss
            if not torch.isfinite(loss): raise RuntimeError('nonfinite loss')
            loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),5.)
            optimizer.step()
            count=sum(lens); total_loss+=loss.item()*count; total_tokens+=count
        pred=predict(model,dev_rows,vocab,args.device)
        metrics=evaluate(dev_rows,pred,stats['frequencies'],stats['long_threshold'])
        score=metrics['groups']['nonpunct']['accuracy']
        entry=dict(epoch=epoch,loss=total_loss/total_tokens,dev=metrics['groups'],seconds=time.monotonic()-start)
        history.append(entry); print(json.dumps(entry),flush=True)
        if score > best:
            best=score; stale=0
            checkpoint=dict(model={k:v.detach().cpu() for k,v in model.state_dict().items()},
                            vocab=vocab,config=config,seed=args.seed,epoch=epoch)
            torch.save(checkpoint,out/'best.pt.tmp')
            (out/'best.pt.tmp').replace(out/'best.pt')
            write_json(out/'dev-metrics.json',metrics)
            write_jsonl(out/'dev-predictions.jsonl',pred)
        else: stale+=1
        write_json(out/'history.json',history)
        if stale>=args.patience: break
    if not history: raise RuntimeError('no epoch completed within time limit')
    write_json(out/'completion.json',dict(status='complete',epochs=len(history),
        seconds=time.monotonic()-start,best_nonpunct=best,checkpoint_sha256=digest(out/'best.pt'),
        peak_gpu_bytes=torch.cuda.max_memory_allocated() if args.device=='cuda' else None))
