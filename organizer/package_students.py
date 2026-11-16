"""Build the distributable Model Golf student ZIP from a checkout."""
import argparse
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
DATA_FILES = (
    'classroom.npz', 'demo_cases.npz', 'baseline.mgf', 'model_golf.py', 'rules.json',
    'DATA_ATTRIBUTION.md', 'wokwi/diagram.json', 'wokwi/src/main.cpp', 'wokwi/src/inference.h',
)
STUDENT_FILES = ('01_ECG_to_ESP32.ipynb', '02_Model_Golf_Challenge.ipynb', 'DATA_ATTRIBUTION.md')


def package(out):
    data = BytesIO()
    with ZipFile(data, 'w', ZIP_DEFLATED) as archive:
        for name in DATA_FILES:
            archive.write(ROOT / name, name)
    out.mkdir(parents=True, exist_ok=True)
    path = out / 'MassAI_Model_Golf_Student.zip'
    with ZipFile(path, 'w', ZIP_DEFLATED) as archive:
        for name in STUDENT_FILES:
            archive.write(ROOT / name, name)
        archive.write(ROOT / 'materials' / 'START_HERE.md', 'START_HERE.md')
        archive.writestr('model-golf-data.zip', data.getvalue())
    return path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'dist')
    print(package(parser.parse_args().out))
