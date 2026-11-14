#!/usr/bin/env python3
"""Download pinned official resources without installing torch on the controller."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]/'models'/'stanza'
PACKAGES={
    'tokenize/udt':'6273af062c361fb78a582e1a85265159',
    'pos/udt_nocharlm':'81f4ce5d27412ca9ee0f2122d0d2ac21',
    'pretrain/conll17':'f5f2bbde656b9b36effcbed4eb8bb9a7',
}

def fetch(url):
    with urllib.request.urlopen(url,timeout=60) as response:return response.read()

def download(item):
    name,md5=item
    dest=ROOT/'ug'/f'{name}.pt';dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() and hashlib.md5(dest.read_bytes()).hexdigest()==md5:
        print(name,'already verified',flush=True);return
    raw=fetch(f'https://huggingface.co/stanfordnlp/stanza-ug/resolve/v1.10.0/models/{name}.pt')
    if hashlib.md5(raw).hexdigest()!=md5:raise ValueError(f'checksum mismatch: {name}')
    temp=dest.with_suffix('.download');temp.write_bytes(raw);temp.replace(dest)
    print(name,len(raw),'bytes verified',flush=True)

if __name__=='__main__':
    ROOT.mkdir(parents=True,exist_ok=True)
    raw=fetch('https://raw.githubusercontent.com/stanfordnlp/stanza-resources/main/resources_1.10.0.json')
    import json
    manifest=json.loads(raw)
    for name,expected in PACKAGES.items():
        kind,package=name.split('/')
        if manifest['ug'][kind][package]['md5']!=expected:raise ValueError('official manifest changed')
    (ROOT/'resources.json').write_bytes(raw)
    with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(download,PACKAGES.items()))
