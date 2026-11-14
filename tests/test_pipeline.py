import json
import subprocess
import sys
import pytest
import torch
from torch.nn import functional as F
from uyghur_pos.data import read_conllu,validate_tokens
from uyghur_pos.metrics import evaluate
from uyghur_pos.model import Tagger,batch,vocabulary,load_model,predict

@pytest.fixture
def rows():
    return [dict(sent_id='s1',tokens=['مەن','بارىمەن','.'],upos=['PRON','VERB','PUNCT']),
            dict(sent_id='s2',tokens=['مەن'],upos=['PRON'])]

def test_conllu_ranges_and_empty_nodes(tmp_path):
    p=tmp_path/'data.conllu'
    p.write_text('# sent_id = one\n1-2\tab\t_\t_\t_\t_\t_\t_\t_\t_\n'
        '1\ta\t_\tNOUN\t_\t_\t0\troot\t_\t_\n'
        '1.1\tx\t_\tX\t_\t_\t_\t_\t_\t_\n'
        '2\tb\t_\tVERB\t_\t_\t1\tdep\t_\t_')
    row=read_conllu(p)[0]
    assert row['tokens']==['a','b'] and row['ids']==[1,2]

def test_metrics_alignment_and_oov(rows):
    result=evaluate(rows,rows,{'مەن':2},4)
    assert result['groups']['overall']==dict(correct=4,n=4,accuracy=1.)
    assert result['groups']['oov']['n']==2
    assert result['groups']['nonpunct']['n']==3
    wrong=[dict(rows[0],upos=['PRON','NOUN','PUNCT']),rows[1]]
    assert evaluate(rows,wrong,{},4)['groups']['overall']['accuracy']==.75
    with pytest.raises(ValueError): evaluate(rows,wrong[:1],{},4)
    with pytest.raises(ValueError): evaluate(rows,[dict(rows[0],tokens=['x']),rows[1]],{},4)

def test_padding_invariance_gradients_reload(rows,tmp_path):
    torch.set_num_threads(1); torch.manual_seed(13)
    vocab=vocabulary(rows); config=dict(hidden=8,char_hidden=4,word_dim=8,char_dim=4,dropout=0.)
    model=Tagger(vocab,**config).eval()
    words,chars,clens,lens,y=batch(rows,vocab,'cpu')
    logits=model(words,chars,clens,lens)
    one=batch(rows[1:],vocab,'cpu')
    assert torch.allclose(logits[1,0],model(*one[:4])[0,0],atol=1e-6)
    loss=F.cross_entropy(logits.flatten(0,1),y.flatten(),ignore_index=-100)
    manual=torch.cat([logits[i,:n] for i,n in enumerate(lens)])
    labels=torch.cat([y[i,:n] for i,n in enumerate(lens)])
    assert torch.allclose(loss,F.cross_entropy(manual,labels))
    loss.backward()
    assert model.words.weight.grad[0].abs().sum()==0
    path=tmp_path/'test.pt'
    torch.save(dict(model=model.state_dict(),vocab=vocab,config=config),path)
    restored,state=load_model(path)
    assert predict(model,rows,vocab)==predict(restored,rows,state['vocab'])
    unseen=[dict(tokens=['يېڭى🙂'])]
    assert len(predict(restored,unseen,vocab)[0]['upos'])==1
    inp=json.dumps(dict(tokens=[]))+'\n'+json.dumps(dict(tokens=['يېڭى🙂']))+'\n'
    run=subprocess.run([sys.executable,'-m','uyghur_pos.cli','predict','--model',str(path)],
                       input=inp,text=True,capture_output=True)
    assert run.returncode==0,run.stderr
    assert json.loads(run.stdout.splitlines()[0])==dict(tokens=[],upos=[])
    bad=subprocess.run([sys.executable,'-m','uyghur_pos.cli','predict','--model',str(path)],
                       input='{"tokens": [123]}\n',text=True,capture_output=True)
    assert bad.returncode==2 and 'nonempty strings' in bad.stderr

def test_invalid_tokens():
    for tokens in [None,'word',[3],[''],['a']*513,['x'*129]]:
        with pytest.raises(ValueError): validate_tokens(tokens)

def test_udt_literal_underscore_is_preserved(tmp_path):
    p=tmp_path/'underscore.conllu'
    p.write_text('1\t_\t_\tPUNCT\tY\t_\t0\troot\t_\t_\n')
    assert read_conllu(p)[0]['tokens']==['_']

def test_near_duplicates_preserve_sequence_order():
    from uyghur_pos.audit import near_duplicates
    a=[dict(sent_id='a',tokens=list('abcdefghij'))]
    b=[dict(sent_id='one-change',tokens=list('abcdefghiX')),
       dict(sent_id='reverse',tokens=list('jihgfedcba'))]
    matches=near_duplicates(a,b)
    assert len(matches)==1 and matches[0]['right']=='one-change' and matches[0]['ratio']==.9

def test_acceptance_does_not_hide_oov_or_missing_evidence():
    from uyghur_pos.acceptance import quality_gates,resource_gates,verdict
    def score(overall=.9,nonpunct=.88,oov=.8,n=1000):
        return dict(groups={k:dict(accuracy=v,n=n) for k,v in [('overall',overall),('nonpunct',nonpunct),('oov',oov)]})
    b=score()
    assert verdict(quality_gates(b,[score(.89,.87,.78)]*3))=='PASS'
    assert verdict(quality_gates(b,[score(.89,.87,.77)]*3))=='FAIL'
    assert verdict(quality_gates(b,[score()]*2))=='INCONCLUSIVE'
    assert verdict(quality_gates(score(n=10),[score()]*3))=='INCONCLUSIVE'
    base=dict(stable=True,p50=10.,p95=20.,rss=100.)
    fast=dict(stable=True,p50=3.,p95=21.,rss=40.)
    assert verdict(resource_gates(base,{'fast':fast},'latency'))=='FAIL'
    assert verdict({'known_failure':False,'missing':None})=='FAIL'

def test_distillation_masks_padding_and_checks_probabilities():
    from uyghur_pos.losses import soft_distillation
    logits=torch.randn(2,3,17,requires_grad=True)
    valid=torch.tensor([[True,True,True],[True,False,False]])
    targets=torch.softmax(torch.randn(2,3,17)/2.,dim=-1)
    loss=soft_distillation(logits,targets,valid,2.)
    loss.backward()
    assert torch.isfinite(loss) and logits.grad[1,1:].abs().sum()==0
    with pytest.raises(ValueError):soft_distillation(logits,targets*2,valid,2.)

def test_backup_excludes_active_runs(tmp_path):
    import importlib.util
    from pathlib import Path
    script=Path(__file__).resolve().parents[1]/'scripts/archive_results.py'
    spec=importlib.util.spec_from_file_location('archive_results_test',script)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.ROOT=tmp_path
    done=tmp_path/'runs'/'done';active=tmp_path/'runs'/'active'
    done.mkdir(parents=True);active.mkdir()
    (done/'completion.json').write_text('{}')
    (active/'best.pt').write_bytes(b'still being updated')
    assert module.selections('runs')==[done]
    with pytest.raises(ValueError):module.selections('runs/active')
    with pytest.raises(ValueError):module.selections('../credentials')
