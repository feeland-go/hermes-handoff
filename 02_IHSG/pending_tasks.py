#!/usr/bin/env python3
"""Extract pending/timeout tasks from TODO.md as compact JSON — IHSG version.
Also serves as drift detector for OPERATING_STANDARD.md version header."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TODO_PATH = ROOT / 'TODO.md'
OPERATING_STANDARD_PATH = ROOT / 'OPERATING_STANDARD.md'

STATUS_RE = re.compile(r'^- \[(?P<status>pending|in_progress|done|timeout)\] (?P<id>(?:[A-Z]+\d+|OUT-\d+)) — (?P<title>.+)$')
BATCH_RE = re.compile(r'^##\s+(BATCH|Sprint|META|OUTPUT|Tier)')

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

HEADER_RE = re.compile(
    r'<!--\s*version:\s*[\d.]+\s*\|\s*updated:\s*\d{4}-\d{2}-\d{2}\s*\|\s*pending:\s*(\d+)\s*\|\s*done:\s*(\d+)\s*\|\s*total:\s*(\d+)\s*-->'
)


def task_output_path(task_id: str) -> str | None:
    if task_id.startswith('OUT-'):
        return None
    if task_id.startswith('R'):
        try:
            num = int(task_id[1:])
        except ValueError:
            return None
        for prefix, start, end, folder in RESEARCH_BATCHES:
            if prefix == 'R' and start <= num <= end:
                return f'research/papers/{folder}/{task_id}.md'
    elif task_id.startswith('IHSG'):
        try:
            num = int(task_id[4:])
        except ValueError:
            return None
        for prefix, start, end, folder in RESEARCH_BATCHES:
            if prefix == 'IHSG' and start <= num <= end:
                return f'research/papers/{folder}/{task_id}.md'
    elif task_id.startswith('BM'):
        try:
            num = int(task_id[2:])
        except ValueError:
            return None
        for start, end, folder in BM_BATCHES:
            if start <= num <= end:
                return f'research/papers/{folder}/{task_id}.md'
    return None


def parse_todo():
    text = TODO_PATH.read_text(encoding='utf-8')
    lines = text.splitlines()
    tasks = []
    current_batch = ''
    counts = {'pending': 0, 'in_progress': 0, 'done': 0, 'timeout': 0}

    for line in lines:
        m = STATUS_RE.match(line)
        if m:
            tid = m.group('id')
            status = m.group('status')
            title = m.group('title').strip()
            counts[status] = counts.get(status, 0) + 1
            tasks.append({
                'task_id': tid,
                'title': title,
                'status': status,
                'batch': current_batch,
                'output_path': task_output_path(tid),
            })
        bm = BATCH_RE.match(line)
        if bm:
            current_batch = line.strip()

    return tasks, counts


def check_drift(actual_counts):
    if not OPERATING_STANDARD_PATH.exists():
        print("WARNING: OPERATING_STANDARD.md not found — drift detection disabled", file=sys.stderr)
        return

    text = OPERATING_STANDARD_PATH.read_text(encoding='utf-8')
    match = HEADER_RE.search(text)

    if match is None:
        print("WARNING: version header not found in OPERATING_STANDARD.md — drift detection disabled", file=sys.stderr)
        return

    try:
        hdr_pending = int(match.group(1))
        hdr_done = int(match.group(2))
        hdr_total = int(match.group(3))
    except (ValueError, IndexError):
        print("WARNING: unrecognized header format in OPERATING_STANDARD.md — drift detection disabled", file=sys.stderr)
        return

    actual_total = sum(actual_counts.values())
    warnings = []
    if hdr_pending != actual_counts.get('pending', 0):
        warnings.append(f"pending: header={hdr_pending} actual={actual_counts.get('pending', 0)}")
    if hdr_done != actual_counts.get('done', 0):
        warnings.append(f"done: header={hdr_done} actual={actual_counts.get('done', 0)}")
    if hdr_total != actual_total:
        warnings.append(f"total: header={hdr_total} actual={actual_total}")

    if warnings:
        print(f"WARNING: OPERATING_STANDARD.md stale — {', '.join(warnings)}", file=sys.stderr)


def main():
    tasks, counts = parse_todo()

    actionable = [t for t in tasks if t['status'] in ('pending', 'timeout')]

    result = {
        'summary': {
            'pending': counts.get('pending', 0),
            'timeout': counts.get('timeout', 0),
            'in_progress': counts.get('in_progress', 0),
            'done': counts.get('done', 0),
            'total': sum(counts.values()),
        },
        'actionable_tasks': actionable,
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))

    check_drift(counts)


if __name__ == '__main__':
    main()
