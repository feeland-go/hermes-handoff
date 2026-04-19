#!/usr/bin/env python3
import argparse
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
TODO_PATH = ROOT / 'TODO.md'
RUNTIME_DIR = ROOT / 'runtime'
RUNS_DIR = RUNTIME_DIR / 'runs'
RESULTS_DIR = RUNTIME_DIR / 'results'
TASK_REGISTRY_PATH = RUNTIME_DIR / 'task_registry.json'

STATUS_RE = re.compile(r'^- \[(?P<status>pending|in_progress|done|timeout)\] (?P<id>(?:[A-Z]+\d+|OUT-\d+)) [\—\–\-\―] (?P<title>.+)$')
PROGRESS_RE = re.compile(r'^Progress:\s+(\d+)\s*/\s*(\d+)\s+task selesai\s*$')
LAST_UPDATED_RE = re.compile(r'^Last updated:\s+.*$')

RESEARCH_BATCHES = [
    ('R', 1, 6, 'A_market_regime_macro'),
    ('R', 7, 12, 'B_sector_rotation_fundamental'),
    ('R', 13, 18, 'C_technical_flow_microstructure'),
    ('R', 19, 24, 'D_risk_portfolio_strategy'),
    ('IHSG', 1, 15, 'regime_detection'),
    ('IHSG', 16, 45, 'technical_analysis'),
    ('IHSG', 46, 70, 'hybrid_scoring'),
    ('IHSG', 71, 85, 'exit_strategy'),
    ('IHSG', 86, 105, 'sector_sentiment'),
    ('IHSG', 106, 110, 'smart_money'),
]
BM_BATCHES = [
    (1, 3, 'A_brokers_research_tools'),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    for path in [RUNTIME_DIR, RUNS_DIR, RESULTS_DIR, RUNTIME_DIR / 'tools']:
        path.mkdir(parents=True, exist_ok=True)


@dataclass
class Task:
    task_id: str
    title: str
    status: str
    line_no: int
    line_text: str

    @property
    def kind(self) -> str:
        if self.task_id.startswith('R') or self.task_id.startswith('IHSG'):
            return 'research'
        if self.task_id.startswith('BM'):
            return 'business_model'
        if self.task_id.startswith('OUT-'):
            return 'output'
        return 'other'


def parse_from_lines(lines: List[str]) -> Tuple[List[str], List[Task], Optional[int], Optional[int], Optional[int]]:
    tasks: List[Task] = []
    progress_line_idx = None
    progress_done = None
    progress_total = None
    for idx, line in enumerate(lines):
        m = STATUS_RE.match(line)
        if m:
            tasks.append(Task(
                task_id=m.group('id'),
                title=m.group('title').strip(),
                status=m.group('status'),
                line_no=idx,
                line_text=line,
            ))
        pm = PROGRESS_RE.match(line)
        if pm:
            progress_line_idx = idx
            progress_done = int(pm.group(1))
            progress_total = int(pm.group(2))
    return lines, tasks, progress_line_idx, progress_done, progress_total


def parse_todo_lines() -> Tuple[List[str], List[Task], Optional[int], Optional[int], Optional[int]]:
    text = TODO_PATH.read_text(encoding='utf-8')
    return parse_from_lines(text.splitlines())


def update_todo(updates: Dict[str, str], note: str) -> Dict[str, int]:
    lines, tasks, progress_line_idx, _, progress_total = parse_todo_lines()
    task_map = {t.task_id: t for t in tasks}
    for task_id, new_status in updates.items():
        task = task_map[task_id]
        lines[task.line_no] = f'- [{new_status}] {task.task_id} — {task.title}'

    _, tasks_after, _, _, _ = parse_from_lines(lines)
    status_counts = {'pending': 0, 'in_progress': 0, 'done': 0, 'timeout': 0}
    done_count = 0
    for task in tasks_after:
        status_counts[task.status] = status_counts.get(task.status, 0) + 1
        if task.status == 'done':
            done_count += 1

    if progress_line_idx is not None and progress_total is not None:
        lines[progress_line_idx] = f'Progress: {done_count} / {progress_total} task selesai'
    for idx, line in enumerate(lines):
        if LAST_UPDATED_RE.match(line):
            today = datetime.now().strftime('%Y-%m-%d')
            lines[idx] = f'Last updated: {today} ({note})'
            break

    TODO_PATH.write_text("\n".join(lines) + "\n", encoding='utf-8')
    return status_counts


def task_output_path(task: Task) -> Optional[Path]:
    if task.kind == 'research':
        # Handle different prefixes: R001 -> 1, IHSG001 -> 1
        if task.task_id.startswith('IHSG'):
            number = int(task.task_id[4:])
        else:
            number = int(task.task_id[1:])
        for prefix, start, end, folder in RESEARCH_BATCHES:
            if task.task_id.startswith(prefix) and start <= number <= end:
                return ROOT / 'research' / 'papers' / folder / f'{task.task_id}.md'
    elif task.kind == 'business_model':
        number = int(task.task_id[2:])
        for start, end, folder in BM_BATCHES:
            if start <= number <= end:
                return ROOT / 'research' / 'business_models' / folder / f'{task.task_id}.md'
    elif task.kind == 'output':
        return ROOT / 'output' / f'{task.task_id}.md'
    return None


def validate_output(task: Task) -> Dict[str, object]:
    output_path = task_output_path(task)
    if output_path is None:
        return {'valid': False, 'reason': 'no_output_mapping', 'path': None}
    if not output_path.exists():
        return {'valid': False, 'reason': 'missing_file', 'path': str(output_path)}
    text = output_path.read_text(encoding='utf-8', errors='ignore')
    stripped = text.strip()
    if len(stripped) < 1000:
        return {'valid': False, 'reason': 'too_short', 'path': str(output_path), 'chars': len(stripped)}
    first_line = stripped.splitlines()[0] if stripped.splitlines() else ''
    if task.task_id not in first_line:
        return {'valid': False, 'reason': 'missing_task_id_in_title', 'path': str(output_path), 'title_line': first_line}
    low = stripped.lower()
    if 'ringkasan' not in low:
        return {'valid': False, 'reason': 'missing_summary_section', 'path': str(output_path)}
    if ('relevansi proyek' not in low) and ('implikasi' not in low):
        return {'valid': False, 'reason': 'missing_project_relevance', 'path': str(output_path)}
    if ('doi' not in low) and ('http://' not in low) and ('https://' not in low) and ('sumber:' not in low):
        return {'valid': False, 'reason': 'missing_source_markers', 'path': str(output_path)}
    return {'valid': True, 'reason': 'ok', 'path': str(output_path), 'chars': len(stripped)}


def load_registry() -> Dict[str, object]:
    ensure_dirs()
    if TASK_REGISTRY_PATH.exists():
        return json.loads(TASK_REGISTRY_PATH.read_text(encoding='utf-8'))
    registry = {'version': 1, 'updated_at': now_iso(), 'tasks': {}, 'active_runs': {}}
    TASK_REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')
    return registry


def save_registry(registry: Dict[str, object]) -> None:
    registry['updated_at'] = now_iso()
    TASK_REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding='utf-8')


def cmd_init(args):
    ensure_dirs()
    registry = load_registry()
    _, tasks, _, _, _ = parse_todo_lines()
    for task in tasks:
        registry['tasks'].setdefault(task.task_id, {
            'task_id': task.task_id,
            'title': task.title,
            'kind': task.kind,
            'last_known_status': task.status,
            'output_path': str(task_output_path(task)) if task_output_path(task) else None,
            'last_claimed_run': None,
            'last_completed_run': None,
            'notes': [],
        })
    save_registry(registry)
    print(json.dumps({'ok': True, 'task_count': len(tasks), 'registry_path': str(TASK_REGISTRY_PATH)}, indent=2))


def cmd_status(args):
    _, tasks, _, _, _ = parse_todo_lines()
    counts = {'pending': 0, 'in_progress': 0, 'done': 0, 'timeout': 0}
    for task in tasks:
        counts[task.status] = counts.get(task.status, 0) + 1
    print(json.dumps({'ok': True, 'counts': counts, 'total': len(tasks)}, indent=2))


def cmd_reconcile(args):
    registry = load_registry()
    _, tasks, _, _, _ = parse_todo_lines()
    updates = {}
    report = {'done_from_outputs': [], 'reverted_to_pending': [], 'valid_done': [], 'invalid_done': []}
    for task in tasks:
        validation = validate_output(task)
        entry = registry['tasks'].setdefault(task.task_id, {
            'task_id': task.task_id,
            'title': task.title,
            'kind': task.kind,
            'output_path': str(task_output_path(task)) if task_output_path(task) else None,
            'last_known_status': task.status,
            'last_claimed_run': None,
            'last_completed_run': None,
            'notes': [],
        })
        entry['last_validation'] = validation
        entry['last_known_status'] = task.status
        if task.status == 'done':
            if validation.get('valid'):
                report['valid_done'].append(task.task_id)
            else:
                report['invalid_done'].append({'task_id': task.task_id, 'reason': validation.get('reason')})
        elif task.status == 'in_progress':
            if validation.get('valid'):
                updates[task.task_id] = 'done'
                report['done_from_outputs'].append(task.task_id)
            else:
                updates[task.task_id] = 'pending'
                report['reverted_to_pending'].append({'task_id': task.task_id, 'reason': validation.get('reason')})
    if updates:
        update_todo(updates, 'runtime reconcile by Hermes')
    save_registry(registry)
    print(json.dumps({'ok': True, 'updates': updates, 'report': report}, indent=2))


def load_manifest(run_id: str):
    run_dir = RUNS_DIR / run_id
    manifest_path = run_dir / 'manifest.json'
    if not manifest_path.exists():
        raise SystemExit(f'Run manifest not found: {manifest_path}')
    return run_dir, json.loads(manifest_path.read_text(encoding='utf-8'))


def save_manifest(run_dir: Path, manifest: Dict[str, object]):
    manifest['updated_at'] = now_iso()
    (run_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')


def cmd_start_run(args):
    registry = load_registry()
    run_id = args.run_id or datetime.now().strftime('run_%Y%m%d_%H%M%S')
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        'run_id': run_id,
        'created_at': now_iso(),
        'status': 'started',
        'max_tasks': args.max_tasks,
        'claimed_tasks': [],
        'completed_tasks': [],
        'failed_tasks': [],
        'notes': [],
    }
    save_manifest(run_dir, manifest)
    registry['active_runs'][run_id] = {'started_at': manifest['created_at'], 'status': 'started'}
    save_registry(registry)
    print(json.dumps({'ok': True, 'run_id': run_id, 'run_dir': str(run_dir)}, indent=2))


def cmd_claim(args):
    registry = load_registry()
    run_dir, manifest = load_manifest(args.run_id)
    _, tasks, _, _, _ = parse_todo_lines()
    pending = [t for t in tasks if t.status == 'pending' and t.kind in {'research', 'business_model'}]
    selected = pending[:args.limit]
    updates = {t.task_id: 'in_progress' for t in selected}
    if updates:
        update_todo(updates, f'run {args.run_id} claimed tasks')
    manifest['claimed_tasks'] = [asdict(t) for t in selected]
    for task in selected:
        entry = registry['tasks'].setdefault(task.task_id, {'task_id': task.task_id, 'title': task.title, 'kind': task.kind, 'notes': []})
        entry['last_claimed_run'] = args.run_id
        entry['last_known_status'] = 'in_progress'
    save_manifest(run_dir, manifest)
    save_registry(registry)
    print(json.dumps({'ok': True, 'run_id': args.run_id, 'claimed': [t.task_id for t in selected]}, indent=2))


def cmd_finalize(args):
    registry = load_registry()
    run_dir, manifest = load_manifest(args.run_id)
    _, tasks, _, _, _ = parse_todo_lines()
    task_map = {t.task_id: t for t in tasks}
    success_ids = [x.strip() for x in args.success.split(',') if x.strip()] if args.success else []
    failed_ids = [x.strip() for x in args.failed.split(',') if x.strip()] if args.failed else []
    updates = {}
    completed = []
    failed = []
    for task_id in success_ids:
        task = task_map.get(task_id)
        if not task:
            continue
        validation = validate_output(task)
        if validation.get('valid'):
            updates[task_id] = 'done'
            completed.append({'task_id': task_id, 'validation': validation})
            entry = registry['tasks'].setdefault(task_id, {'task_id': task_id, 'notes': []})
            entry['last_completed_run'] = args.run_id
            entry['last_known_status'] = 'done'
            entry['last_validation'] = validation
        else:
            updates[task_id] = 'timeout'
            failed.append({'task_id': task_id, 'reason': f"invalid_output:{validation.get('reason')}"})
    for task_id in failed_ids:
        if task_id in updates:
            continue
        updates[task_id] = 'timeout' if args.fail_status == 'timeout' else 'pending'
        failed.append({'task_id': task_id, 'reason': args.fail_reason or 'manual_finalize'})
        entry = registry['tasks'].setdefault(task_id, {'task_id': task_id, 'notes': []})
        entry['last_known_status'] = updates[task_id]
    if updates:
        update_todo(updates, f'run {args.run_id} finalized tasks')
    manifest['status'] = 'finalized'
    manifest['completed_tasks'] = completed
    manifest['failed_tasks'] = failed
    save_manifest(run_dir, manifest)
    registry['active_runs'].pop(args.run_id, None)
    save_registry(registry)
    print(json.dumps({'ok': True, 'run_id': args.run_id, 'updates': updates, 'completed': completed, 'failed': failed}, indent=2))


def main():
    parser = argparse.ArgumentParser(description='IHSG-Stock-Analysis lightweight runtime engine')
    sub = parser.add_subparsers(dest='cmd', required=True)
    sub.add_parser('init')
    sub.add_parser('status')
    sub.add_parser('reconcile')
    p_start = sub.add_parser('start-run')
    p_start.add_argument('--run-id', default='')
    p_start.add_argument('--max-tasks', type=int, default=6)
    p_claim = sub.add_parser('claim')
    p_claim.add_argument('--run-id', required=True)
    p_claim.add_argument('--limit', type=int, default=6)
    p_finalize = sub.add_parser('finalize')
    p_finalize.add_argument('--run-id', required=True)
    p_finalize.add_argument('--success', default='')
    p_finalize.add_argument('--failed', default='')
    p_finalize.add_argument('--fail-status', choices=['pending', 'timeout'], default='pending')
    p_finalize.add_argument('--fail-reason', default='')
    args = parser.parse_args()
    if args.cmd == 'init':
        cmd_init(args)
    elif args.cmd == 'status':
        cmd_status(args)
    elif args.cmd == 'reconcile':
        cmd_reconcile(args)
    elif args.cmd == 'start-run':
        cmd_start_run(args)
    elif args.cmd == 'claim':
        cmd_claim(args)
    elif args.cmd == 'finalize':
        cmd_finalize(args)


if __name__ == '__main__':
    main()
