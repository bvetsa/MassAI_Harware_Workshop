"""The workshop's one-hidden-layer MLP and deployable weight format."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import struct

import numpy as np

INPUTS = 64
WIDTHS = (4, 8, 16, 24)
LABELS = ('N (normal beat)', 'V (PVC)')
HEADER = struct.Struct('<4sBB')
BASELINE_WIDTH = 24
SEED = 18
TRAINING_SEEDS = (SEED, 7, 42)
TRAINING_EPOCHS = {'standard': 45, 'short': 15}


@dataclass
class Model:
    w1: np.ndarray  # [hidden neuron, input]
    b1: np.ndarray
    w2: np.ndarray
    b2: np.float32


def train(x, y, width=BASELINE_WIDTH, *, seed=SEED, training='standard'):
    """Fit on a seeded, class-balanced subset for the selected number of epochs."""
    if width not in WIDTHS:
        raise ValueError(f'Choose a hidden width from {WIDTHS}.')
    if not isinstance(seed, (int, np.integer)) or seed not in TRAINING_SEEDS:
        raise ValueError(f'Choose a random seed from {TRAINING_SEEDS}.')
    if training not in TRAINING_EPOCHS:
        raise ValueError(f'Choose a training preset from {tuple(TRAINING_EPOCHS)}.')
    rng = np.random.default_rng(seed)
    normal, pvc = (np.flatnonzero(y == label) for label in (0, 1))
    indices = np.r_[rng.choice(normal, len(pvc), replace=False), pvc]
    w1 = rng.normal(0, np.sqrt(2 / INPUTS), (width, INPUTS)).astype(np.float32)
    b1 = np.zeros(width, dtype=np.float32)
    w2 = rng.normal(0, np.sqrt(2 / width), width).astype(np.float32)
    b2 = np.zeros(1, dtype=np.float32)
    parameters = (w1, b1, w2, b2)
    mean = [np.zeros_like(p) for p in parameters]
    variance = [np.zeros_like(p) for p in parameters]
    step = 0
    for _ in range(TRAINING_EPOCHS[training]):
        rng.shuffle(indices)
        for offset in range(0, len(indices), 256):
            batch = indices[offset:offset+256]
            xb, yb = x[batch], y[batch]
            hidden = np.maximum(np.einsum('bi,hi->bh', xb, w1) + b1, 0)
            z = np.einsum('bh,h->b', hidden, w2) + b2
            probability = 1 / (1 + np.exp(-np.clip(z, -40, 40)))
            dz = (probability - yb) / len(batch)
            dh = (dz[:, None] * w2) * (hidden > 0)
            gradients = (np.einsum('bh,bi->hi', dh, xb), dh.sum(axis=0),
                         np.einsum('bh,b->h', hidden, dz), dz.sum())
            step += 1
            rate = 0.003 * np.sqrt(1 - 0.999**step) / (1 - 0.9**step)
            for parameter, m, v, grad in zip(parameters, mean, variance, gradients):
                m *= 0.9
                m += 0.1 * grad
                v *= 0.999
                v += 0.001 * grad**2
                parameter -= rate * m / (np.sqrt(v) + 1e-8)
    return Model(w1, b1, w2, b2[0])


def encode(model, bits):
    """Return the exact bytes stored in ESP32 flash for the model."""
    def floats(values):
        return np.asarray(values, dtype='<f4').tobytes()

    width = len(model.b1)
    if width not in WIDTHS or bits not in (8, 32):
        raise ValueError('Choose a supported hidden width and FP32 or INT8.')
    weights = (model.w1, model.w2)
    scales = b''
    if bits == 8:
        scale = np.array([max(np.max(np.abs(w)) / 127, 1e-9) for w in weights],
                         dtype=np.float32)
        weights = tuple(np.clip(np.rint(w / s), -127, 127).astype('i1').tobytes()
                        for w, s in zip(weights, scale))
        scales = floats(scale)
    else:
        weights = tuple(floats(w) for w in weights)
    blob = (HEADER.pack(b'MGF1', width, bits) + scales + weights[0] +
            floats(model.b1) + weights[1] + floats([model.b2]))
    decode(blob)
    return blob


def decode(blob):
    if len(blob) < HEADER.size:
        raise ValueError('Incomplete model header.')
    magic, width, bits = HEADER.unpack_from(blob)
    if magic != b'MGF1' or width not in WIDTHS or bits not in (8, 32):
        raise ValueError('Unsupported model header.')
    scale_bytes = 8 if bits == 8 else 0
    size = HEADER.size + scale_bytes + (INPUTS + 1) * width * (bits // 8) + 4 * (width + 1)
    if len(blob) != size:
        raise ValueError(f'Expected {size} model bytes, received {len(blob)}.')
    offset = HEADER.size

    def read(dtype, count):
        nonlocal offset
        values = np.frombuffer(blob, dtype=dtype, count=count, offset=offset)
        offset += values.nbytes
        return values

    def weights(count, scale):
        return read('i1', count).astype(np.float32) * scale if bits == 8 else read('<f4', count)

    scales = read('<f4', 2) if bits == 8 else (1.0, 1.0)
    if not all(0.0 < s <= 64.0 for s in scales):
        raise ValueError('Invalid INT8 scale.')
    w1 = weights(INPUTS * width, scales[0]).reshape(width, INPUTS)
    b1 = read('<f4', width)
    w2 = weights(width, scales[1])
    b2 = read('<f4', 1)[0]
    if not all(np.all(np.isfinite(w) & (np.abs(w) <= 64.0)) for w in (w1, b1, w2, b2)):
        raise ValueError('Non-finite or out-of-range model parameter.')
    return Model(w1, b1, w2, b2)


def logits(model, x):
    """Evaluate the exported model in firmware accumulation order, in FP32."""
    x = np.asarray(x, dtype=np.float32)
    hidden = np.broadcast_to(model.b1, (len(x), len(model.b1))).copy()
    for i in range(INPUTS):
        hidden += x[:, i, None] * model.w1[:, i]
    np.maximum(hidden, 0, out=hidden)
    result = np.full(len(x), model.b2, dtype=np.float32)
    for j, weight in enumerate(model.w2):
        result += hidden[:, j] * weight
    return result


def score(blob, x, y):
    pred = logits(decode(blob), x) >= 0
    tn = int(np.sum((y == 0) & ~pred))
    fp = int(np.sum((y == 0) & pred))
    fn = int(np.sum((y == 1) & ~pred))
    tp = int(np.sum((y == 1) & pred))
    return dict(bytes=len(blob), accuracy=(tn + tp) / len(y), sensitivity=tp / (tp + fn),
                tn=tn, fp=fp, fn=fn, tp=tp)


def format_score(result):
    return (f"{result['bytes']:,} bytes | accuracy {result['accuracy']:.1%} | "
            f"PVC sensitivity {result['sensitivity']:.1%} | "
            f"TN {result['tn']}, FP {result['fp']}, FN {result['fn']}, TP {result['tp']}")


def firmware_headers(blob, cases, out):
    """Write byte-for-byte model data and exactly round-trippable FP32 examples."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    digest = sha256(blob).hexdigest()
    byte_rows = ['  ' + ', '.join(f'0x{b:02x}' for b in blob[i:i+16]) + ','
                 for i in range(0, len(blob), 16)]
    (out / 'model_data.h').write_text(
        '#pragma once\n#include <stdint.h>\n\n'
        f'constexpr char kModelSha256[] = "{digest}";\n'
        'constexpr uint8_t kModel[] = {\n' + '\n'.join(byte_rows) + '\n};\n')
    z = logits(decode(blob), cases['x'])
    rows = ['#pragma once', '', 'constexpr DemoCase kDemoCases[] = {']
    for name, target, x, expected in zip(cases['id'], cases['y'], cases['x'], z):
        # Nine significant digits round-trip binary32, including in the C++ compiler.
        literals = [f'{v:.8e}f' for v in x]
        rows.extend([f'  {{"{name}", {target}, {expected:.8e}f, {{', *[
            '    ' + ', '.join(literals[i:i+8]) + ',' for i in range(0, INPUTS, 8)
        ], '  }},'])
    (out / 'demo_data.h').write_text('\n'.join(rows + ['};', '']))
    return z


def browser_sketch(source_dir):
    """Combine the same inference, model, fixtures and Arduino code for Wokwi.com."""
    source_dir = Path(source_dir)
    parts = []
    for name in ('inference.h', 'model_data.h', 'demo_data.h', 'main.cpp'):
        lines = (source_dir / name).read_text().splitlines()
        parts.append('\n'.join(line for line in lines
                               if not line.startswith(('#pragma once', '#include "'))))
    return '// Generated from the four firmware source files.\n#include <Arduino.h>\n\n' + '\n\n'.join(parts) + '\n'
