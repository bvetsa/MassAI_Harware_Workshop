"""Exercise the competition notebook from a fresh student ZIP with NumPy and Matplotlib."""
import csv
from hashlib import sha256
from io import BytesIO
from itertools import product
import json
import os
from pathlib import Path
from statistics import median
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import perf_counter
from zipfile import ZipFile

import matplotlib
import numpy as np

matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def run_tool(script, *args):
    subprocess.run([sys.executable, str(ROOT / script), *map(str, args)], check=True)


def check_competition(workspace):
    run_tool('organizer/package_students.py', '--out', workspace)
    with ZipFile('MassAI_Model_Golf_Student.zip') as archive:
        with ZipFile(BytesIO(archive.read('model-golf-data.zip'))) as data_archive:
            assert set(data_archive.namelist()) == {
                'classroom.npz', 'demo_cases.npz', 'baseline.mgf', 'model_golf.py', 'rules.json',
                'DATA_ATTRIBUTION.md', 'wokwi/diagram.json', 'wokwi/src/main.cpp', 'wokwi/src/inference.h',
            }
        archive.extractall()
    cells = json.loads(Path('02_Model_Golf_Challenge.ipynb').read_text())['cells']
    namespace = {}
    times = {'standard': [], 'short': []}
    plots = []

    def capture_plot():
        fig = plt.gcf()
        plots.append(fig.axes[0])
        fig.canvas.draw()
        plt.close(fig)

    def time_training(*args, **kwargs):
        start = perf_counter()
        model = original_train(*args, **kwargs)
        times[kwargs['training']].append(perf_counter() - start)
        return model

    plt.show = capture_plot
    start = perf_counter()
    for cell in cells:
        if cell['cell_type'] != 'code':
            continue
        exec(compile(''.join(cell['source']), cell['id'], 'exec'), namespace)
        if cell['id'] == 'setup':
            original_train = namespace['train']
            assert Path(original_train.__code__.co_filename).is_relative_to(workspace / 'model-golf-data')
            namespace['train'] = time_training
        if cell['id'] == 'quantize':
            assert all(not measurements for measurements in times.values())
    default_time = perf_counter() - start

    assert len(namespace['baseline']) == 6346 and len(namespace['int8_baseline']) == 1674
    run_trial = namespace['run_trial']
    trials = namespace['trials']
    for width, seed, training, bits in product((4, 8, 16, 24), (18, 7, 42), ('standard', 'short'), (32, 8)):
        row = run_trial(width, bits, seed, training)
        expected_size = 6 + (8 if bits == 8 else 0) + 65 * width * (bits // 8) + 4 * (width + 1)
        assert len(row['payload']) == row['bytes'] == expected_size
        assert row['passes'] == (row['accuracy'] >= 0.80 and row['sensitivity'] >= 0.94)
    assert len(trials) == 48 and len(times['standard']) == 11 and len(times['short']) == 12
    alternate = trials[8, 8, 7, 'short']
    assert run_trial(8, 8, 7, 'short') is alternate and len(times['short']) == 12
    assert alternate['payload'] != trials[8, 8, 18, 'short']['payload']
    assert alternate['payload'] != trials[8, 8, 7, 'standard']['payload']
    repeat = original_train(namespace['x_train'], namespace['y_train'], 8, seed=7, training='short')
    assert namespace['encode'](repeat, 8) == alternate['payload']

    namespace['show_trials']()
    assert len(plots) == 2 and sum(len(series.get_offsets()) for series in plots[-1].collections) == 49
    assert np.allclose(plots[-1].lines[0].get_ydata(), [0.94, 0.94])
    best = namespace['smallest_passing_trial']()
    assert best['passes'] and best['bytes'] == min(row['bytes'] for row in trials.values() if row['passes'])

    export = namespace['export_submission']
    trials['invalid'] = dict(number=49, payload=b'MGF1')
    for team, trial in (('../escape', 2), ('', 2), ('Demo', 999), ('Demo', '2'), ('Demo', True), ('Demo', 49)):
        try:
            export(team, trial)
        except ValueError:
            pass
        else:
            raise AssertionError(f'Accepted invalid submission {team!r}, {trial!r}')
    del trials['invalid']
    assert not list(workspace.glob('*.mgf'))
    submission = export('MassAI Dry Run', alternate['number'])
    assert submission.name == 'MassAI Dry Run.mgf' and submission.read_bytes() == alternate['payload']

    # The scorer integration uses a practice fixture. Final recordings stay with the organizer.
    fixture = workspace / 'scorer-fixture.npz'
    np.savez(fixture, x=namespace['x_val'], y=namespace['y_val'])
    run_tool('organizer/score_entries.py', workspace, '--final-data', fixture, '--out', 'leaderboard.csv')
    with Path('leaderboard.csv').open(newline='') as f:
        scored, = csv.DictReader(f)
    assert int(scored['bytes']) == alternate['bytes'] and scored['eligible'] == ('yes' if alternate['passes'] else 'no')
    for metric in ('accuracy', 'sensitivity'):
        assert scored[metric] == f'{alternate[metric]:.4%}'
    run_tool('organizer/deploy.py', workspace / submission, '--out', 'entry-wokwi')
    expected = json.loads(Path('entry-wokwi/expected.json').read_text())
    assert expected['sha256'] == sha256(alternate['payload']).hexdigest() and len(expected['beats']) == 2
    print('PASS: clean ZIP, 48 trials, caching, deterministic repeat, plot, submission, scorer, and deployment export.')
    print(f'Default notebook cells including first plot: {default_time:.3f}s (Python with Agg backend).')
    for name, measurements in times.items():
        print(f'{name} CPU training ({len(measurements)} fits): median {median(measurements):.3f}s, '
              f'range {min(measurements):.3f}–{max(measurements):.3f}s.')
    for key in ((24, 32, 18, 'standard'), (24, 8, 18, 'standard'), (8, 8, 18, 'standard'),
                (8, 8, 7, 'standard'), (8, 8, 7, 'short'), (4, 8, 42, 'short')):
        print(key, namespace['format_score'](trials[key]))


if __name__ == '__main__':
    cwd = Path.cwd()
    with TemporaryDirectory() as temp:
        try:
            os.chdir(temp)
            check_competition(Path(temp).resolve())
        finally:
            os.chdir(cwd)
