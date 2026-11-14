#!/usr/bin/env python3
"""Project-scoped SSH transport. Never puts the password in argv or logs."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import shlex
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--script', type=Path)
    p.add_argument('--upload', action='store_true', help='Upload source only, excluding credentials and results')
    p.add_argument('--include-models', action='store_true', help='Include downloaded baseline resources in upload')
    p.add_argument('--fetch', help='Fetch project-relative directory from remote into local project')
    p.add_argument('command', nargs='?', default='hostname')
    args = p.parse_args()
    private = ROOT / 'credentials'
    cfg = json.loads((private / 'autodl.json').read_text())
    env = dict(os.environ, SSH_ASKPASS=str(private / 'askpass.py'),
               SSH_ASKPASS_REQUIRE='force', DISPLAY=':0')
    base = ['ssh', '-T', '-p', str(cfg['port']), '-o', 'ConnectTimeout=15',
           '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=3',
           '-o', 'StrictHostKeyChecking=accept-new',
           '-o', f'UserKnownHostsFile={private / "known_hosts"}',
           f'{cfg["user"]}@{cfg["host"]}']
    remote = '/root/autodl-tmp/uyghur-nlp'
    if args.upload:
        with tempfile.TemporaryFile() as archive:
            with tarfile.open(fileobj=archive,mode='w') as tar:
                names=['pyproject.toml','.gitignore','src','scripts','tests','docs','reports','README.md','NOTICE.md','LICENSE','licenses','CITATION.cff','MODEL_CARD.md']
                if args.include_models: names.append('models/stanza')
                for name in names:
                    path=ROOT/name
                    if path.exists():
                        tar.add(path,arcname=name,filter=lambda t: None if '__pycache__' in t.name else t)
            archive.seek(0)
            result=subprocess.run(base+[f'mkdir -p {remote} && tar -xf - -C {remote}'],stdin=archive,
                                  env=env,start_new_session=True)
            raise SystemExit(result.returncode)
    if args.fetch:
        relative=Path(args.fetch)
        if relative.is_absolute() or '..' in relative.parts:
            p.error('fetch requires a project-relative path without parent traversal')
        with tempfile.TemporaryFile() as archive:
            archive_command=f'cd {remote} && .venv/bin/python scripts/archive_results.py {shlex.quote(str(relative))}'
            result=subprocess.run(base+[archive_command],
                                  stdout=archive,env=env,start_new_session=True)
            result.check_returncode(); archive.seek(0)
            with tarfile.open(fileobj=archive) as tar:
                tar.extractall(ROOT,filter='data')
        return
    cmd=base+['bash -s' if args.script else args.command]
    result = subprocess.run(cmd, input=args.script.read_bytes() if args.script else None,
                            env=env, start_new_session=True)
    raise SystemExit(result.returncode)

if __name__ == '__main__':
    main()
