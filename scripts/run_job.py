#!/usr/bin/env python3
"""Bounded detached jobs with per-name locking and persisted exit status."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--name',required=True);p.add_argument('--seconds',type=int,default=900)
    p.add_argument('--worker',action='store_true');p.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args()
    if not re.fullmatch('[A-Za-z0-9_-]+',a.name) or not 1<=a.seconds<=3600:
        p.error('invalid name or deadline (1..3600 seconds)')
    job=ROOT/'artifacts'/'jobs'/a.name;job.mkdir(parents=True,exist_ok=True)
    if not a.worker:
        # Claim a unique job directory. Retrying requires a new name.
        try:
            fd=os.open(job/'claimed',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.close(fd)
        except FileExistsError:
            p.error('job already exists; inspect its status before using a new name')
        command=a.command[1:] if a.command[:1]==['--'] else a.command
        if not command:p.error('command required')
        with (job/'log.txt').open('w') as log:
            child=subprocess.Popen([sys.executable,__file__,'--worker','--name',a.name,
                '--seconds',str(a.seconds),'--',*command],stdout=log,stderr=log,stdin=subprocess.DEVNULL,
                start_new_session=True,cwd=ROOT)
        print(json.dumps(dict(worker_pid=child.pid,job=str(job))),flush=True);return
    command=a.command[1:] if a.command[:1]==['--'] else a.command
    with (job/'lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        start=time.time();child=None
        state=dict(status='running',worker_pid=os.getpid(),start_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                   command=command,deadline_seconds=a.seconds)
        def save():
            temp=job/'status.tmp';temp.write_text(json.dumps(state,indent=2));temp.replace(job/'status.json')
        save()
        try:
            child=subprocess.Popen(command,cwd=ROOT,start_new_session=True)
            state['pid']=child.pid;save()
            code=child.wait(timeout=a.seconds)
            state.update(status='complete' if code==0 else 'failed',exit_code=code)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid,signal.SIGTERM)
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
            state.update(status='timeout',exit_code=124)
        except Exception as error:
            state.update(status='failed',error=str(error),exit_code=1)
        finally:
            state['elapsed_seconds']=time.time()-start;save()

if __name__=='__main__': main()
