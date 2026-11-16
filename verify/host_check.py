"""Compare the same C++ inference used on ESP32 to Python on every practice beat."""
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model_golf import WIDTHS, decode, encode, logits, train


with np.load(ROOT / 'classroom.npz', allow_pickle=False) as data, TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    x = data['validation_x']
    inputs = tmp / 'inputs.bin'
    # Host runner reads floats in the host's native byte order.
    x.astype(np.float32).tofile(inputs)
    binary = tmp / 'native-inference'
    subprocess.run(['c++', '-std=c++11', '-O2', '-Wall', '-Wextra',
                    '-I', str(ROOT / 'wokwi' / 'src'),
                    str(ROOT / 'verify' / 'host_inference.cpp'), '-o', str(binary)], check=True)
    baseline = (ROOT / 'baseline.mgf').read_bytes()
    for width in WIDTHS:
        model = train(data['train_x'], data['train_y'], width) if width != 24 else decode(baseline)
        for bits in (32, 8):
            blob = encode(model, bits)
            entry = tmp / 'entry.mgf'
            entry.write_bytes(blob)
            observed = np.fromstring(subprocess.check_output([str(binary), str(entry), str(inputs)],
                                                            text=True), sep=' ', dtype=np.float32)
            expected = logits(decode(blob), x)
            np.testing.assert_allclose(observed, expected, atol=1e-5, rtol=0)
            np.testing.assert_array_equal(observed >= 0, expected >= 0)
            print(f'PASS width={width} bits={bits} windows={len(x):,} '
                  f'max_abs_error={np.max(np.abs(observed-expected)):g}')
