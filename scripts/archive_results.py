#!/usr/bin/env python3
"""Stream a result snapshot; never archive an actively changing run."""
from pathlib import Path
import sys,tarfile

ROOT=Path(__file__).resolve().parents[1]

def selections(relative):
    rel=Path(relative)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts:raise ValueError('invalid relative path')
    if rel.parts[0]=='credentials':raise ValueError('credentials cannot be exported')
    path=ROOT/rel
    if not path.exists():raise ValueError('source missing')
    if rel==Path('runs'):
        return [p for p in sorted(path.iterdir()) if p.is_dir() and (p/'completion.json').exists()]
    if rel.parts[0]=='runs' and not (ROOT/'runs'/rel.parts[1]/'completion.json').exists():
        raise ValueError('run still active/incomplete; wait for completion')
    return [path]

if __name__=='__main__':
    paths=selections(sys.argv[1])
    with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as archive:
        for path in paths:
            archive.add(path,arcname=str(path.relative_to(ROOT)))
