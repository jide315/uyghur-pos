#!/usr/bin/env bash
set -euo pipefail
cd /root/autodl-tmp/uyghur-nlp
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
for seed in 42 2026; do
  for config in supervised lexical; do
    output="runs/${config}-seed${seed}"
    if [ -f "$output/completion.json" ]; then continue; fi
    extra=()
    if [ "$config" = lexical ]; then extra=(--pretrain models/stanza/ug/pretrain/conll17.pt); fi
    .venv/bin/python -m uyghur_pos.cli train --train data/ud/train.jsonl --dev data/ud/dev.jsonl \
      --stats data/ud/training-stats.json --output "$output" --seed "$seed" \
      --epochs 40 --patience 6 --max-seconds 300 "${extra[@]}"
  done
done
