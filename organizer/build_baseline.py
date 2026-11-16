"""Retrain the reference model and reproduce its export from the classroom data."""
import argparse
from pathlib import Path

import numpy as np

from deploy import ROOT, deploy
from model_golf import encode, format_score, score, train


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    with np.load(ROOT / 'classroom.npz', allow_pickle=False) as data:
        blob = encode(train(data['train_x'], data['train_y']), 32)
        (args.out / 'baseline.mgf').write_bytes(blob)
        print(format_score(score(blob, data['validation_x'], data['validation_y'])))
    with np.load(ROOT / 'demo_cases.npz', allow_pickle=False) as cases:
        report = deploy(blob, cases, args.out / 'wokwi')
    for beat in report['beats']:
        print(beat)
