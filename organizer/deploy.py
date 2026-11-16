"""Generate the Wokwi firmware sources and Python reference JSON for a .mgf model."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model_golf import browser_sketch, firmware_headers


def deploy(blob, cases, out):
    out.mkdir(parents=True, exist_ok=True)
    src = out / 'src'
    src.mkdir(exist_ok=True)
    template = ROOT / 'wokwi'
    for name in ('diagram.json', 'wokwi.toml', 'platformio.ini', 'src/main.cpp', 'src/inference.h'):
        if (out / name).resolve() != (template / name).resolve():
            shutil.copyfile(template / name, out / name)
    z = firmware_headers(blob, cases, src)
    (out / 'sketch.ino').write_text(browser_sketch(src))
    report = dict(model_bytes=len(blob), sha256=sha256(blob).hexdigest(), tolerance=1e-5,
                  beats=[dict(id=str(i), annotation='NV'[int(y)], logit=float(logit),
                              predicted='NV'[int(logit >= 0)])
                         for i, y, logit in zip(cases['id'], cases['y'], z)])
    (out / 'expected.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    with np.load(ROOT / 'demo_cases.npz', allow_pickle=False) as cases:
        print(json.dumps(deploy(args.model.read_bytes(), cases, args.out), indent=2))
