#!/usr/bin/env bash
set -euo pipefail
cd /root/autodl-tmp/uyghur-nlp
if [ ! -x .venv/bin/python ]; then
    /root/miniconda3/bin/python -m venv --system-site-packages .venv
fi
.venv/bin/python -m pip install -e '.[baseline,test]'
mkdir -p artifacts
.venv/bin/python -m pip freeze > artifacts/environment.txt
.venv/bin/python - <<'PY'
import json,platform,torch
from uyghur_pos.data import write_json
assert torch.cuda.is_available(), 'CUDA not available'
x=torch.randn(2,3,5,device='cuda',requires_grad=True)
layer=torch.nn.LSTM(5,4,batch_first=True).cuda()
layer(x)[0].sum().backward()
info=dict(python=platform.python_version(),torch=torch.__version__,cuda=torch.version.cuda,
          gpu=torch.cuda.get_device_name(0),capability=torch.cuda.get_device_capability(0),
          gpu_lstm_backward='pass')
write_json('artifacts/environment.json',info)
print(json.dumps(info,indent=2))
PY
.venv/bin/python -m pytest -q | tee artifacts/tests.txt
