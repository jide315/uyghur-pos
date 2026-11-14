from collections import Counter
from pathlib import Path
import difflib
import math
import urllib.request
from .data import digest, read_conllu, write_json, write_jsonl

COMMIT = '77a1c20dae6650284c4c50959833ea2485c5119a'  # UD release r2.15

def prepare(directory):
    root = Path(directory)
    raw = root / 'raw'; raw.mkdir(parents=True, exist_ok=True)
    base = f'https://raw.githubusercontent.com/UniversalDependencies/UD_Uyghur-UDT/{COMMIT}/'
    manifest = dict(commit=COMMIT, release='r2.15', sources={})
    datasets = {}
    for name in ['LICENSE.txt','README.md'] + [f'ug_udt-ud-{s}.conllu' for s in ['train','dev','test']]:
        path = raw / name
        if not path.exists():
            with urllib.request.urlopen(base+name, timeout=60) as response:
                content = response.read()
            path.write_bytes(content)
        manifest['sources'][name] = dict(url=base+name, sha256=digest(path))
    for split in ['train','dev','test']:
        rows = read_conllu(raw / f'ug_udt-ud-{split}.conllu')
        datasets[split] = rows
        write_jsonl(root / f'{split}.jsonl', rows)
        manifest[split] = dict(sentences=len(rows),words=sum(len(r['tokens']) for r in rows),
                               sha256=digest(root / f'{split}.jsonl'))
    frequencies = Counter(w for row in datasets['train'] for w in row['tokens'])
    lengths = sorted(map(len,frequencies))
    threshold = lengths[math.ceil(.75*len(lengths))-1]
    audit = dict(long_threshold=threshold, train_types=len(frequencies), splits={},duplicates={})
    for split,rows in datasets.items():
        audit['splits'][split] = dict(sentences=len(rows),words=sum(len(r['tokens']) for r in rows),
            literal_underscore=sum(w=='_' for r in rows for w in r['tokens']),
            oov=sum(w not in frequencies for r in rows for w in r['tokens']),
            max_tokens=max(map(lambda r:len(r['tokens']), rows)),
            max_word_chars=max(len(w) for r in rows for w in r['tokens']))
    # Content-only overlap checks; never score test predictions here.
    for left,right in [('train','dev'),('train','test'),('dev','test')]:
        a={tuple(r['tokens']) for r in datasets[left]}
        b={tuple(r['tokens']) for r in datasets[right]}
        normalize=lambda seq:' '.join(seq).casefold()
        norm_a={normalize(seq) for seq in a}; norm_b={normalize(seq) for seq in b}
        audit['duplicates'][f'{left}:{right}']=dict(exact=len(a & b), normalized=len(norm_a & norm_b))
    write_json(root/'manifest.json',manifest)
    write_json(root/'audit.json',audit)
    write_json(root/'training-stats.json',dict(frequencies=dict(frequencies), long_threshold=threshold))
    return audit
