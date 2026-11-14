#!/usr/bin/env python3
"""Extract train-only teacher soft labels and verify word/class alignment."""
import torch
import stanza
from uyghur_pos.data import UPOS,read_jsonl,write_jsonl,write_json,digest

torch.set_num_threads(1)
nlp=stanza.Pipeline('ug',dir='models/stanza',processors='tokenize,pos',package='udt',
    tokenize_pretokenized=True,use_gpu=False,download_method=None,verbose=False)
trainer=nlp.processors['pos']._trainer
labels=trainer.vocab['upos']._id2unit
captured=[]
handle=trainer.model.upos_clf.register_forward_hook(lambda m,args,out:captured.append(out.detach().cpu()))
result=[];agreements=0;words=0
for row in read_jsonl('data/ud/train.jsonl'):
    captured.clear();doc=nlp([row['tokens']]);pred=[w for s in doc.sentences for w in s.words]
    if [w.text for w in pred]!=row['tokens'] or len(captured)!=1:raise ValueError('teacher extraction not aligned')
    logits=captured[0]
    if logits.shape[0]!=len(pred):raise ValueError('packed teacher word count mismatch')
    if [labels[i] for i in logits.argmax(-1).tolist()]!=[w.upos for w in pred]:raise ValueError('teacher packed order mismatch')
    mapped=torch.full((len(pred),len(UPOS)),-1000.)
    for i,label in enumerate(UPOS):
        if label in labels:mapped[:,i]=logits[:,labels.index(label)]
    probabilities=torch.softmax(mapped/2.,dim=-1)
    result.append(dict(sent_id=row['sent_id'],tokens=row['tokens'],upos=[w.upos for w in pred],
                       probabilities=probabilities.tolist(),labels=UPOS,temperature=2.))
    agreements+=sum(w.upos==y for w,y in zip(pred,row['upos']));words+=len(pred)
handle.remove()
write_jsonl('artifacts/teacher-train-soft.jsonl',result)
write_json('artifacts/teacher-soft-manifest.json',dict(sentences=len(result),words=words,
    train_sha256=digest('data/ud/train.jsonl'),target_sha256=digest('artifacts/teacher-train-soft.jsonl'),
    teacher_train_gold_agreement=agreements/words,temperature=2.,missing_teacher_labels=[s for s in UPOS if s not in labels],
    scope='Only annotated train. Full word order and class mapping checked for every sentence.'))
print('Teacher train soft labels extracted:',len(result),words,flush=True)
