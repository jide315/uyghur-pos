#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from uyghur_pos.acceptance import quality_gates,resource_gates,verdict
from uyghur_pos.data import write_json,digest

p=argparse.ArgumentParser();p.add_argument('--freeze',required=True)
p.add_argument('--quality',default='artifacts/final-quality');p.add_argument('--benchmark',default='artifacts/final-benchmark')
p.add_argument('--output',default='artifacts/final-acceptance.json');a=p.parse_args()
freeze=json.loads(Path(a.freeze).read_text());q=Path(a.quality)
baseline=json.loads((q/'B0.json').read_text())
names=freeze['candidates']
metrics=[json.loads((q/f'{n}.json').read_text()) for n in names]
quality=quality_gates(baseline,metrics)
quality['registered_seed_set']=sorted(freeze['seeds'])==[13,42,2026]
benchmark_record=json.loads((Path(a.benchmark)/'summary.json').read_text())
benchmark=benchmark_record['models']
resources=resource_gates(benchmark['B0'],{n:benchmark[n] for n in names},freeze['resource_target'])
resources['full_test_benchmark']=benchmark_record['data_sha256']==freeze['inputs_sha256']['data/ud/test.jsonl']
resources['frozen_benchmark_protocol']=benchmark_record['freeze_sha256']==digest(a.freeze)
quality_record=json.loads((q/'manifest.json').read_text())
quality['frozen_test_inputs']=quality_record['test_sha256']==freeze['inputs_sha256']['data/ud/test.jsonl']
quality['frozen_protocol']=quality_record['freeze_sha256']==digest(a.freeze)
release=json.loads((q/f'{freeze["release_model"]}.json').read_text())['groups']
release_checks={f'release_{k}_loss_le_1pp':baseline['groups'][k]['accuracy']-release[k]['accuracy']<=.01+1e-12 for k in ['overall','nonpunct']}
intervals=json.loads((q/'bootstrap.json').read_text())
uncertain={name:{k:v['lower']<-.01 for k,v in intervals[name].items()} for name in names}
write_json(a.output,dict(verdict=verdict({**quality,**resources,**release_checks}),
    quality=quality,resources=resources,release=release_checks,
    interval_crosses_quality_boundary=uncertain,
    note='PASS is the registered point-estimate decision; crossing intervals limit statistical claims.'))
print(Path(a.output).read_text())
