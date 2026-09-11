#!/usr/bin/env python3
"""Generate a clearly fictional run without publishing or changing a user project."""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
cli = Path(__file__).resolve().parents[1] / 'plugins/delivery-chain/scripts/delivery.py'
if args.output.exists():
    parser.error('Output already exists; choose another file')
with tempfile.TemporaryDirectory(prefix='delivery-example-') as temp:
    project = Path(temp)
    product = project / 'page.txt'
    product.write_text('Example v1')
    run = project / 'docs/quality/delivery-runs/demo'
    def call(*parts):
        subprocess.run([sys.executable, str(cli), *parts], check=True, stdout=subprocess.DEVNULL)
    def event(stage, outcome, note):
        call('event', '--run', str(run), '--stage', stage, '--outcome', outcome,
             '--note', 'DANE FIKCYJNE: ' + note, '--evidence', 'Symulacja demonstracyjna, nie rzeczywisty test')
    call('init', '--project', str(project), '--run-id', 'demo', '--title',
         'DEMO — fikcyjny przebieg', '--mode', 'reconstructed')
    event('plan', 'PASS', 'Plan małej strony.')
    call('freeze', '--run', str(run))
    event('build', 'PASS', 'Pierwsza wersja.')
    event('review', 'FAIL', 'Przycisk nie ma dostępnej nazwy.')
    event('build', 'NONE', 'Naprawa etykiety.')
    product.write_text('Example v2 with accessible label')
    call('freeze', '--run', str(run))
    for stage in ['build', 'verify', 'security', 'review', 'machine']:
        event(stage, 'PASS', 'Zaliczenie etapu w symulacji.')
    # Use exclusive creation: never overwrite an existing output, even in a race.
    with args.output.open('x', encoding='utf8') as output:
        output.write((run / 'index.html').read_text())
print(args.output.resolve())
