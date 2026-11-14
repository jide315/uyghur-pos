#!/usr/bin/env python3
"""Create reviewable source/model bundles from explicit allowlists."""
import hashlib,json,tarfile
from pathlib import Path
from uyghur_pos.data import write_json,digest

root=Path('.');out=root/'dist';out.mkdir(exist_ok=True)
freeze=json.loads((root/'artifacts/final-freeze.json').read_text())
release=freeze['release_model'];model=root/freeze['models'][release]
if digest(model)!=freeze['model_sha256'][release]:raise ValueError('release checkpoint changed')
public=['README.md','MODEL_CARD.md','LICENSE','NOTICE.md','CITATION.cff','pyproject.toml','MANIFEST.in',
        'requirements-cpu.txt','requirements-cpu.lock','src','scripts','tests','docs','reports','licenses']
def clean(info):
    if '__pycache__' in info.name or info.name.endswith('.pyc'):return None
    info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
    return info
source=out/'uyghur-pos-0.1.0-source.tar.gz'
with tarfile.open(source,'w:gz') as tar:
    for name in public:
        if not (root/name).exists():raise ValueError(f'missing deliverable: {name}')
        tar.add(root/name,arcname=f'uyghur-pos-0.1.0/{name}',filter=clean)
weights=out/'uyghur-pos-0.1.0-model.tar.gz'
with tarfile.open(weights,'w:gz') as tar:
    tar.add(model,arcname='model.pt',filter=clean)
    for name in ['MODEL_CARD.md','NOTICE.md','licenses']:
        tar.add(root/name,arcname=name,filter=clean)
manifest=dict(release_model=release,checkpoint_sha256=digest(model),
    bundles={p.name:dict(bytes=p.stat().st_size,sha256=digest(p)) for p in [source,weights]},
    code_license='MIT',weights_license='CC-BY-SA-4.0 with retained Apache-2.0 resource notices',
    status='local release candidate; public hosting and external adoption separately recorded')
write_json(out/'release-manifest.json',manifest)
print(json.dumps(manifest,indent=2))
