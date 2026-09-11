#!/usr/bin/env python3
"""Local, append-only-by-API execution journal; stdlib, macOS/Linux."""
import argparse
import copy
from datetime import datetime, timezone
import fcntl
import html
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
STAGES = {
    'plan': 'Specyfikacja i plan', 'build': 'Implementacja',
    'freeze': 'Zamrożenie kandydata', 'verify': 'Weryfikacja',
    'security': 'Bezpieczeństwo', 'review': 'Niezależny code review',
    'machine': 'Bramka maszynowa', 'human': 'Odbiór człowieka',
    'final': 'Bramka finalna', 'deploy': 'Publikacja', 'smoke': 'Kontrola produkcji',
}
BOUND = set(STAGES) - {'plan', 'freeze'}
CANDIDATE = re.compile(r'(snapshot:sha256:[a-f0-9]{64}|git:[a-f0-9]{7,40})\Z')
OUTCOMES = ['NONE', 'PASS', 'FAIL', 'BLOCKED', 'PARTIAL', 'SKIPPED']

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def atomic(path, text):
    fd, temp = tempfile.mkstemp(prefix='.delivery-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf8') as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

def load(run):
    data = json.loads((run / 'run.json').read_text())
    if data.get('schema_version') != 1:
        raise ValueError('Unsupported journal schema')
    return data

def frames(data):
    state = {key: {'execution': 'pending', 'outcome': 'NONE', 'candidate': None,
                   'note': '', 'evidence': [], 'stale': False} for key in STAGES}
    candidate = None
    result = []
    for e in data['events']:
        if e['kind'] == 'candidate':
            candidate = e['candidate']
            for key in BOUND:
                if state[key]['execution'] != 'pending':
                    state[key]['stale'] = state[key]['stale'] or state[key]['candidate'] != candidate
            state['freeze'] = dict(execution='done', outcome='PASS', candidate=candidate,
                                   note=e['note'], evidence=e['evidence'], stale=False)
        else:
            # A new attempt or result invalidates downstream conclusions, even
            # if the candidate bytes have not changed (e.g. flaky test failure).
            downstream = {
                'build': ['verify', 'security', 'review', 'machine', 'human', 'final'],
                'verify': ['machine', 'human', 'final'],
                'security': ['machine', 'human', 'final'],
                'review': ['machine', 'human', 'final'],
                'machine': ['human', 'final'],
                'human': ['final'],
            }
            for key in downstream.get(e['stage'], []):
                if state[key]['execution'] != 'pending':
                    state[key]['stale'] = True
            state[e['stage']] = dict(execution=e['execution'], outcome=e['outcome'],
                candidate=e['candidate'], note=e['note'], evidence=e['evidence'],
                stale=e['stage'] in BOUND and e['candidate'] != candidate)
        result.append({'event': e, 'candidate': candidate, 'stages': copy.deepcopy(state)})
    return result

def render(data, run):
    payload = json.dumps({'run': {k: data[k] for k in ['id', 'title', 'mode', 'created']},
                          'labels': STAGES, 'frames': frames(data)}, ensure_ascii=False)
    # Prevent closing the non-executable JSON script element, including malicious notes.
    payload = payload.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    template = (ROOT / 'assets/view.html').read_text()
    output = template.replace('__DELIVERY_DATA__', payload).replace('__TITLE__', html.escape(data['title']))
    atomic(run / 'index.html', output)

def record(data, args):
    fs = frames(data)
    current = fs[-1]['candidate'] if fs else None
    common = {'seq': len(data['events']) + 1, 'recorded_at': now(), 'note': args.note,
              'evidence': args.evidence or [], 'origin': data['mode']}
    if args.command == 'freeze':
        candidate = args.candidate
        if not candidate:
            spec = importlib.util.spec_from_file_location('fingerprint', ROOT / 'skills/safe-web-delivery/scripts/fingerprint_candidate.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            candidate = module.fingerprint(Path(data['project']))[0]
        if not CANDIDATE.fullmatch(candidate):
            raise ValueError('Invalid candidate identifier')
        e = dict(common, kind='candidate', candidate=candidate)
    else:
        candidate = args.candidate or current
        if candidate and not CANDIDATE.fullmatch(candidate):
            raise ValueError('Invalid candidate identifier')
        if args.stage in BOUND and args.outcome == 'PASS' and not candidate:
            raise ValueError('PASS requires a frozen candidate for this stage')
        if args.stage == 'freeze':
            raise ValueError('Use freeze to record a candidate')
        if args.stage == 'human':
            if args.command != 'decision':
                raise ValueError('Use decision for human approval; a stage PASS is not approval')
        if args.command == 'decision':
            if args.execution != 'done':
                raise ValueError('A recorded decision requires execution=done')
            if not current or candidate != current:
                raise ValueError('Decision must concern the current frozen candidate')
            if not args.actor.strip() or not args.statement.strip():
                raise ValueError('Decision requires actor and exact user statement')
            common['actor'] = args.actor
            common['statement'] = args.statement
            args.outcome = args.decision
        if args.outcome == 'PASS' and not common['evidence']:
            raise ValueError('PASS requires an evidence reference')
        if args.execution != 'done' and args.outcome in ['PASS', 'FAIL']:
            raise ValueError('PASS/FAIL require execution=done')
        # Gates check journal consistency, not underlying code or evidence authenticity.
        if args.stage in ['machine', 'final'] and args.outcome == 'PASS':
            prior = fs[-1]['stages'] if fs else {}
            required = ['build', 'verify', 'security', 'review']
            if args.stage == 'final':
                required += ['machine', 'human']
            for key in required:
                s = prior.get(key, {})
                expected = 'APPROVED' if key == 'human' else 'PASS'
                if s.get('outcome') != expected or s.get('execution') != 'done' or s.get('candidate') != candidate or s.get('stale'):
                    raise ValueError(f'{args.stage} PASS requires current {key} {expected}')
        e = dict(common, kind='decision' if args.command == 'decision' else 'stage',
                 stage=args.stage, execution=args.execution, outcome=args.outcome, candidate=candidate)
        if args.stage == 'deploy':
            prior = fs[-1]['stages'] if fs else {}
            e['before_approval'] = prior.get('human', {}).get('outcome') != 'APPROVED' or prior.get('human', {}).get('stale', True) or prior.get('human', {}).get('candidate') != candidate
            e['before_final'] = prior.get('final', {}).get('outcome') != 'PASS' or prior.get('final', {}).get('stale', True) or prior.get('final', {}).get('candidate') != candidate
    data['events'].append(e)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('--project', required=True, type=Path)
    init.add_argument('--run-id', required=True)
    init.add_argument('--title', required=True)
    init.add_argument('--mode', choices=['observed', 'reconstructed'], default='observed')
    for command in ['event', 'freeze', 'decision', 'render', 'show']:
        p = sub.add_parser(command)
        p.add_argument('--run', required=True, type=Path)
        if command in ['render', 'show']:
            continue
        p.add_argument('--candidate')
        p.add_argument('--note', default='')
        p.add_argument('--evidence', action='append')
        if command == 'freeze':
            continue
        p.add_argument('--execution', choices=['running', 'done', 'pending'], default='done')
        if command == 'decision':
            p.set_defaults(stage='human', outcome='NONE')
            p.add_argument('--decision', required=True, choices=['APPROVED', 'REJECTED'])
            p.add_argument('--actor', required=True)
            p.add_argument('--statement', required=True)
        else:
            p.add_argument('--stage', required=True, choices=list(STAGES))
            p.add_argument('--outcome', choices=OUTCOMES, default='NONE')
    args = parser.parse_args()
    if args.command == 'init':
        if not re.fullmatch('[a-z0-9][a-z0-9-]{0,63}', args.run_id):
            raise ValueError('run-id must be a short lowercase slug')
        project = args.project.resolve(strict=True)
        run = project / 'docs/quality/delivery-runs' / args.run_id
        run.mkdir(parents=True, exist_ok=False)
        data = dict(schema_version=1, id=args.run_id, title=args.title, mode=args.mode,
                    project=str(project), created=now(), events=[])
        atomic(run / 'run.json', json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        render(data, run)
    else:
        run = args.run.resolve(strict=True)
        # Serialize whole read-modify-write-render transaction across agents.
        with (run / '.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            data = load(run)
            if args.command == 'show':
                print(json.dumps(data, ensure_ascii=False, indent=2))
                return
            if args.command != 'render':
                record(data, args)
                atomic(run / 'run.json', json.dumps(data, ensure_ascii=False, indent=2) + '\n')
            render(data, run)
    print(run / 'index.html')

if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
