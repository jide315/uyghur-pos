#!/usr/bin/env bash
set -euo pipefail
cd /root/autodl-tmp/uyghur-nlp
export PATH="$PWD/.venv/bin:$PATH"
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p artifacts reports runs
python -m pytest -q | tee artifacts/tests.txt
python -m uyghur_pos.cli prepare | tee artifacts/data-audit.txt
python -m uyghur_pos.cli dictionary --train data/ud/train.jsonl --data data/ud/dev.jsonl --stats data/ud/training-stats.json --output artifacts/dictionary-dev.json
# To avoid network waits on a metered instance, provision and verify models first.
# The CLI --download flag remains available when outbound downloads work.
timeout 180 python -m uyghur_pos.cli baseline --data data/ud/dev.jsonl --stats data/ud/training-stats.json --output artifacts/stanza-dev.json
python -m pip freeze > artifacts/environment.txt
