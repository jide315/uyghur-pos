#!/usr/bin/env bash
set -euo pipefail
cd /root/autodl-tmp/uyghur-nlp
export CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
.venv/bin/python scripts/final_quality.py --freeze artifacts/final-freeze.json --authorize-test > artifacts/final-quality.log 2>&1
.venv/bin/python scripts/formal_benchmark.py --freeze artifacts/final-freeze.json > artifacts/final-benchmark.log 2>&1
.venv/bin/python scripts/accept_final.py --freeze artifacts/final-freeze.json > artifacts/final-acceptance.log 2>&1
