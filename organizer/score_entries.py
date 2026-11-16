"""Score team model payloads on the organizer's fixed final recordings."""
import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path
import re

import numpy as np

from deploy import ROOT
from model_golf import score

FIELDS = ('rank', 'team', 'bytes', 'accuracy', 'sensitivity', 'eligible', 'tn', 'fp', 'fn', 'tp',
          'sha256', 'status')
TEAM = re.compile(r'[A-Za-z0-9][A-Za-z0-9 _-]{0,39}')


def leaderboard(entries, final_data):
    rules = json.loads((ROOT / 'rules.json').read_text())
    with np.load(final_data, allow_pickle=False) as data:
        x, y = data['x'], data['y']
    rows = []
    for path in sorted(entries.glob('*.mgf')):
        team = path.stem
        if not TEAM.fullmatch(team):
            print(f'Skipped {path.name!r}. Use a team name of 1–40 letters, digits, spaces, _ or -.')
            continue
        try:
            # The widest FP32 payload is 6,346 bytes. Limit reads of invalid entries.
            with path.open('rb') as entry:
                blob = entry.read(6347)
            values = score(blob, x, y)
        except (OSError, ValueError) as error:
            rows.append(dict(team=team, eligible='no', status=f'Invalid model: {error}'))
            continue
        eligible = (values['accuracy'] >= rules['minimum_accuracy'] and
                    values['sensitivity'] >= rules['minimum_pvc_sensitivity'])
        rows.append(dict(team=team, **values, sha256=sha256(blob).hexdigest(),
                         eligible='yes' if eligible else 'no',
                         status='Qualified' if eligible else 'Below a scoring floor'))

    def sort_key(row):
        return (row['eligible'] != 'yes', row.get('bytes', float('inf')),
                -row.get('sensitivity', 0), -row.get('accuracy', 0))

    rows.sort(key=sort_key)
    last_key = None
    for position, row in enumerate(rows, start=1):
        if row['eligible'] == 'yes':
            key = sort_key(row)
            if key != last_key:
                rank = position
                last_key = key
            row['rank'] = rank
        for metric in ('accuracy', 'sensitivity'):
            if metric in row:
                row[metric] = f'{row[metric]:.4%}'
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('entries', type=Path, help='Directory of files named Team Name.mgf')
    parser.add_argument('--final-data', type=Path, default=ROOT / 'organizer' / 'final.npz',
                        help='Held-out final.npz from the separate organizer kit')
    parser.add_argument('--out', type=Path, default=Path('leaderboard.csv'))
    args = parser.parse_args()
    if not args.entries.is_dir():
        parser.error(f'{args.entries} is not a directory.')
    if not args.final_data.is_file():
        parser.error('Supply the organizer kit’s final.npz using --final-data.')
    rows = leaderboard(args.entries, args.final_data)
    with args.out.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    winners = [row['team'] for row in rows if row.get('rank') == 1]
    print(f'Wrote {len(rows)} scored entries to {args.out}.')
    print('First place: ' + ', '.join(winners) if winners else 'No qualifying entries.')
