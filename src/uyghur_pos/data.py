import hashlib
import json
from pathlib import Path

UPOS = 'ADJ ADP ADV AUX CCONJ DET INTJ NOUN NUM PART PRON PROPN PUNCT SCONJ SYM VERB X'.split()

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)

def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')

def read_jsonl(path):
    with Path(path).open() as f:
        return [json.loads(line) for line in f if line.strip()]

def read_conllu(path):
    sentences, tokens, tags, ids = [], [], [], []
    sent_id = None
    def flush():
        nonlocal tokens, tags, ids, sent_id
        if tokens:
            sentences.append(dict(sent_id=sent_id or str(len(sentences)), tokens=tokens, upos=tags, ids=ids))
        tokens, tags, ids, sent_id = [], [], [], None
    for n, raw in enumerate(Path(path).read_text().splitlines(), 1):
        if not raw.strip():
            flush()
            continue
        if raw.startswith('#'):
            if raw.startswith('# sent_id = '):
                sent_id = raw.split(' = ', 1)[1]
            continue
        fields = raw.split('\t')
        if len(fields) != 10:
            raise ValueError(f'{path}:{n}: expected 10 fields')
        word_id = fields[0]
        if '-' in word_id or '.' in word_id:
            continue
        if not word_id.isdigit() or int(word_id) != len(tokens) + 1:
            raise ValueError(f'{path}:{n}: nonconsecutive word ID')
        # UDT contains literal '_' tokens annotated as punctuation; preserve them.
        if fields[3] not in UPOS or not fields[1]:
            raise ValueError(f'{path}:{n}: missing FORM or invalid UPOS')
        tokens.append(fields[1]); tags.append(fields[3]); ids.append(int(word_id))
    flush()
    return sentences

def validate_tokens(tokens, max_tokens=512, max_chars=128):
    if not isinstance(tokens, list) or any(not isinstance(t, str) or not t for t in tokens):
        raise ValueError('tokens must be a list of nonempty strings')
    if len(tokens) > max_tokens or any(len(t) > max_chars for t in tokens):
        raise ValueError(f'input exceeds limit: {max_tokens} tokens / {max_chars} characters per token')
