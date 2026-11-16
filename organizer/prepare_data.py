"""Build training and practice windows from MIT-BIH Arrhythmia Database v1.0.0."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from time import sleep
from urllib.request import urlopen

import numpy as np
import wfdb

SOURCE = 'https://physionet.org/files/mitdb/1.0.0/'
SPLITS = {
    'train': '100 106 114 116 119 200 203 213 215 221 233'.split(),
    'validation': '105 205 208 219 228'.split(),
}
LABELS = {'N': 0, 'V': 1}


def record_files(record, cache):
    hashes = {}
    for ext in ('hea', 'atr', 'dat'):
        name = f'{record}.{ext}'
        path = cache / name
        if not path.is_file():
            for attempt in range(3):
                try:
                    with urlopen(SOURCE + name, timeout=30) as response:
                        path.write_bytes(response.read())
                    break
                except OSError:
                    if attempt == 2:
                        raise
                    sleep(1 + attempt)
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    return hashes


def windows(record, cache):
    stem = str(cache / record)
    signal = wfdb.rdrecord(stem, channel_names=['MLII'])
    annotations = wfdb.rdann(stem, 'atr')
    if signal.fs != 360 or signal.sig_name != ['MLII']:
        raise ValueError(f'{record} has an unexpected lead or sample rate.')
    mv = signal.p_signal[:, 0]
    for i, symbol in zip(annotations.sample, annotations.symbol):
        if symbol not in LABELS or i < 63 or i + 129 > len(mv):
            continue
        # 192 raw samples in [-63, 129). Average consecutive triples.
        x = mv[i - 63:i + 129].reshape(64, 3).mean(axis=1)
        if not np.all(np.isfinite(x)):
            continue
        x -= x.mean()
        x /= max(0.05, np.max(np.abs(x)))
        yield x.astype(np.float32), LABELS[symbol], f'{record}:{i}'


def prepare(cache, out):
    cache.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    manifest = {'source': SOURCE, 'splits': {}, 'sha256': {}}
    classroom = {}
    for split, records in SPLITS.items():
        for record in records:
            manifest['sha256'].update(record_files(record, cache))
        x, y, ids = zip(*(example for record in records for example in windows(record, cache)))
        counts = np.bincount(y, minlength=2)
        if np.any(counts == 0):
            raise ValueError(f'{split} must contain both labels.')
        arrays = dict(x=np.stack(x), y=np.asarray(y, dtype=np.uint8), id=np.asarray(ids))
        manifest['splits'][split] = dict(records=records, N=int(counts[0]), V=int(counts[1]))
        classroom.update({f'{split}_{key}': value for key, value in arrays.items()})
        print(split, manifest['splits'][split])
    np.savez_compressed(out / 'classroom.npz', **classroom)
    (out / 'source-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, default=Path('raw-mitdb'))
    parser.add_argument('--out', type=Path, default=Path('rebuilt'))
    args = parser.parse_args()
    prepare(args.cache, args.out)
