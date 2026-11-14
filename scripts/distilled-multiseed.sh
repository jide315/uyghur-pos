#!/usr/bin/env bash
set -euo pipefail
cd /root/autodl-tmp/uyghur-nlp
for seed in 42 2026; do
  .venv/bin/python -m uyghur_pos.cli train --train data/ud/train.jsonl --dev data/ud/dev.jsonl \
    --stats data/ud/training-stats.json --output "runs/distilled-seed${seed}" --seed "$seed" \
    --epochs 40 --patience 6 --max-seconds 300 --pretrain models/stanza/ug/pretrain/conll17.pt \
    --word-dropout .15 --teacher artifacts/teacher-train-soft.jsonl --alpha .5
done
