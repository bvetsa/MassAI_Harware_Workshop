"""Check recorded Wokwi dial/B1 results against the two exported Python models."""
import json
from pathlib import Path
import re

from serial_check import check

ROOT = Path(__file__).resolve().parents[1]
expected = json.loads((ROOT / 'wokwi/interactive/expected.json').read_text())
logs = {name: [] for name in expected}
active = None
for line in (ROOT / 'verify/interactive-serial.txt').read_text().splitlines():
    if line.startswith('MODEL '):
        match = re.fullmatch(r'MODEL active=(baseline|compact) bytes=(\d+) sha256=([a-f0-9]{64})', line)
        if not match:
            raise ValueError(f'Invalid active-model line: {line}')
        active, size, digest = match.groups()
        model = expected[active]
        if int(size) != model['bytes'] or digest != model['sha256']:
            raise ValueError('Wrong model size or fingerprint in the observed simulator log.')
    elif line.startswith('BEAT '):
        if active is None:
            raise ValueError('BEAT line before active model identity.')
        logs[active].append(line)

for name, model in expected.items():
    identity = f"MODEL bytes={model['bytes']} sha256={model['sha256']}"
    report = dict(model_bytes=model['bytes'], sha256=model['sha256'], tolerance=1e-5,
                  beats=[dict(id=beat, logit=z, annotation=label, predicted='NV'[int(z >= 0)])
                         for (beat, z), label in zip(model['logits'].items(), ('N', 'V'))])
    check('\n'.join([identity, *logs[name]]), report)
print('PASS: both cases under both active payloads in the recorded dial/B1 run.')
