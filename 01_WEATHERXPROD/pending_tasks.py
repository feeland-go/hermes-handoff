#!/usr/bin/env python3
"""Extract pending/timeout tasks from TODO.md as compact JSON.
Also serves as drift detector for OPERATING_STANDARD.md version header."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TODO_PATH = ROOT / 'TODO.md'
OPERATING_STANDARD_PATH = ROOT / 'OPERATING_STANDARD.md'

STATUS_RE = re.compile(r'^- \[(?P<status>pending|in_progress|done|timeout)\] (?P<id>[A-Z]+\d+) — (?P<title>.+)$')
BATCH_RE = re.compile(r'^##\s+(BATCH|META|OUTPUT|Tier Naming)')

PAPER_BATCHES = [
    (1, 50, 'A_pricing_valuation'),
    (51, 130, 'B_squall_nowcasting'),
    (131, 210, 'C_nwp_ocean_forecasting'),
    (211, 290, 'D_saas_pricing_theory'),
    (291, 370, 'E_marine_service_adoption'),
    (371, 450, 'F_indonesia_maritime'),
    (451, 500, 'G_himawari_remote_sensing'),
]
BM_BATCHES = [
    (1, 15, 'A_metocean_providers'),
    (16, 30, 'B_data_as_a_service'),
    (31, 40, 'C_government_providers'),
    (41, 50, 'D_saas_analogies'),
]

HEADER_RE = re.compile(
    r'<!--\s*version:\s*[\d.]+\s*\|\s*updated:\s*\d{4}-\d{2}-\d{2}\s*\|\s*pending:\s*(\d+)\s*\|\s*done:\s*(\d+)\s*\|\s*total:\s*(\d+)\s*-->'
)


def task_output_path(task_id: str) -> str | None:
    if task_id.startswith('P'):
        try:
            num = int(task_id[1:])
        except ValueError:
            return None
        for start, end, folder in PAPER_BATCHES:
            if start <= num <= end:
                return f'research/papers/{folder}/{task_id}.md'
    elif task_id.startswith('BM'):
        try:
            num = int(task_id[2:])
        except ValueError:
            return None
        for start, end, folder in BM_BATCHES:
            if start <= num <= end:
                return f'research/business_models/{folder}/{task_id}.md'
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
