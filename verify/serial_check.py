"""Compare the simulator's captured serial log to Python's exported predictions."""
import argparse
import json
import math
from pathlib import Path
import re


def check(log, expected):
    identity = f"MODEL bytes={expected['model_bytes']} sha256={expected['sha256']}"
    if identity not in log.splitlines():
        raise ValueError('The serial log is missing the expected model identity.')
    beats = {beat['id']: beat for beat in expected['beats']}
    seen = set()
    for line in log.splitlines():
        if not line.startswith('BEAT '):
            continue
        match = re.fullmatch(r'BEAT (\S+) annotation=([NV]) esp32=(\S+) python=(\S+) '
                             r'predicted=([NV]) parity=PASS', line)
        if not match:
            raise ValueError(f'Invalid result line: {line}')
        name, annotation, actual, echoed, predicted = match.groups()
        beat = beats[name]
        for value in (actual, echoed):
            if not math.isclose(float(value), beat['logit'], rel_tol=0, abs_tol=expected['tolerance']):
                raise ValueError(f'{name} logit mismatch: {value} versus {beat["logit"]}.')
        if (annotation, predicted) != (beat['annotation'], beat['predicted']):
            raise ValueError(f'{name} label mismatch.')
        seen.add(name)
    if seen != beats.keys():
        raise ValueError(f'Missing demo beats: {beats.keys() - seen}.')
    print(f'PASS: model identity, labels and logits for {len(seen)} shared ECG windows.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('serial', type=Path)
    parser.add_argument('expected', type=Path)
    args = parser.parse_args()
    check(args.serial.read_text(), json.loads(args.expected.read_text()))
