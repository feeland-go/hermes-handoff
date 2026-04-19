#!/usr/bin/env python3
"""Scaffold a new research project from template.

Usage: python3 setup_new_project.py

Will prompt for project details and generate a complete project structure.
"""

import json
import re
import shutil
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent / 'templates'
BASE_DIR = Path('/home/sst')  # Adjust if needed


def prompt(text: str, default: str = '') -> str:
    if default:
        val = input(f'{text} [{default}]: ').strip()
        return val or default
    val = input(f'{text}: ').strip()
    while not val:
        val = input(f'{text} (required): ').strip()
    return val


def prompt_batches() -> list:
    print('\n=== Batch Configuration ===')
    print('Format: PREFIX START END FOLDER_NAME')
    print('Example: P 1 50 A_pricing_valuation')
    print('Example: IHSG 1 15 regime_detection')
    print('Empty line to finish.\n')

    batches = []
    idx = 1
    while True:
        line = input(f'  Batch {idx} (or empty to finish): ').strip()
        if not line:
            break
        parts = line.split()
        if len(parts) != 4:
            print('    Format: PREFIX START END FOLDER_NAME')
            continue
        prefix, start_str, end_str, folder = parts
        try:
            start, end = int(start_str), int(end_str)
        except ValueError:
            print('    START and END must be integers')
            continue
        batches.append((prefix, start, end, folder))
        idx += 1

    return batches


def generate_operating_standard(project_dir: Path, name: str, domain: str,
                                 description: str, batches: list,
                                 source_tier1: str, source_tier2: str,
                                 min_chars: int) -> str:
    batch_folders = set()
    for prefix, start, end, folder in batches:
        batch_folders.add(folder)

    total_tasks = sum(end - start + 1 for _, start, end, _ in batches)

    content = f"""# OPERATING_STANDARD.md — {name} Research Run Standard

<!-- version: 1.0 | updated: 2026-04-19 | pending: {total_tasks} | done: 0 | total: {total_tasks} -->

Last updated: 2026-04-19

---

## 1. Konteks Proyek

{name} adalah proyek riset untuk {description}.

**Status saat ini:** 0/{total_tasks} done, {total_tasks} pending.

---

## 2. Runtime Flow

### Alur standar
1. `python3 runtime/tools/runtime_engine.py reconcile`
2. `python3 runtime/tools/runtime_engine.py start-run --run-id <id> --max-tasks 6`
3. `python3 runtime/tools/runtime_engine.py claim --run-id <id> --limit 6`
4. Jika 0 task: stop bersih
5. Jika 1-3 task: 1 batch worker
6. Jika 4-6 task: 2 batch worker, masing-masing maksimal 3 task
7. Worker hanya menulis output file
8. Coordinator melakukan finalize
9. `python3 runtime/tools/runtime_engine.py finalize --run-id <id> --success <ids> --failed <ids>`

### Pre-run context loading
```
python3 runtime/tools/pending_tasks.py
```
JANGAN muat TODO.md utuh ke context.

---

## 3. Prioritas Sumber & Fallback

### Tier 1 — {source_tier1}
### Tier 2 — {source_tier2}
### Tier 3 — Metadata / discovery
### Tier 4 — Secondary / supporting

---

## 4. Standar Output

### Header wajib
```markdown
# TASK_ID — Judul task
**Batch:** ...
**Topik:** ...
**Relevansi:** ...
```

### Section wajib
1. Ringkasan Eksekutif
2. Sintesis utama
3. Implikasi untuk proyek
4. Rekomendasi praktis
5. Sumber (DOI, URL, atau Sumber:)
6. Catatan fallback bila relevan

### Gaya editorial
- Bahasa Indonesia primer, istilah teknis Inggris boleh
- Anti-overclaim

---

## 5. Quality Gate

### Runtime validator
- File ada di canonical path
- >= {min_chars} karakter
- Task ID di baris pertama
- Ada section "ringkasan"
- Ada penanda sumber

---

## 6. Context Hygiene Rules

- Setelah 3+ search results, tulis findings ke research/notes/<task_id>_notes.md
- Fetch full content hanya top 3-5 results
- Sub-agent context target: < 8,000 token

---

## 7. Dekomposisi Agent & Orkestrasi

- Task sederhana → direct search
- Task kompleks → researcher → writer → verifier
- File-based handoffs via research/notes/

---

## 8. Sistem Provenance

- Sidecar: research/papers/<batch>/<task_id>.provenance.md
- Wajib untuk task baru
"""
    return content


def generate_pending_tasks(batches: list) -> str:
    # Group batches by prefix
    prefixes = {}
    for prefix, start, end, folder in batches:
        prefixes.setdefault(prefix, []).append((start, end, folder))

    batch_lines = []
    for prefix, entries in prefixes.items():
        for start, end, folder in entries:
            batch_lines.append(f"    ('{prefix}', {start}, {end}, '{folder}'),")

    batch_block = '\n'.join(batch_lines)

    return f"""#!/usr/bin/env python3
\"\"\"Extract pending/timeout tasks from TODO.md as compact JSON.
Also serves as drift detector for OPERATING_STANDARD.md version header.\"\"\"

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TODO_PATH = ROOT / 'TODO.md'
OPERATING_STANDARD_PATH = ROOT / 'OPERATING_STANDARD.md'

STATUS_RE = re.compile(r'^- \\[(?P<status>pending|in_progress|done|timeout)\\] (?P<id>[A-Z]+\\d+) — (?P<title>.+)$')
BATCH_RE = re.compile(r'^##\\s+(BATCH|Sprint|META|OUTPUT)')

RESEARCH_BATCHES = [
{batch_block}
]

HEADER_RE = re.compile(
    r'<!--\\s*version:\\s*[\\d.]+\\s*\\|\\s*updated:\\s*\\d{{4}}-\\d{{2}}-\\d{{2}}\\s*\\|\\s*pending:\\s*(\\d+)\\s*\\|\\s*done:\\s*(\\d+)\\s*\\|\\s*total:\\s*(\\d+)\\s*-->'
)


def task_output_path(task_id: str) -> str | None:
    for prefix, start, end, folder in RESEARCH_BATCHES:
        if task_id.startswith(prefix):
            try:
                num = int(task_id[len(prefix):])
            except ValueError:
                continue
            if start <= num <= end:
                return f'research/papers/{{folder}}/{{task_id}}.md'
    return None


def parse_todo():
    text = TODO_PATH.read_text(encoding='utf-8')
    lines = text.splitlines()
    tasks = []
    current_batch = ''
    counts = {{'pending': 0, 'in_progress': 0, 'done': 0, 'timeout': 0}}

    for line in lines:
        m = STATUS_RE.match(line)
        if m:
            tid = m.group('id')
            status = m.group('status')
            title = m.group('title').strip()
            counts[status] = counts.get(status, 0) + 1
            tasks.append({{
                'task_id': tid,
                'title': title,
                'status': status,
                'batch': current_batch,
                'output_path': task_output_path(tid),
            }})
        bm = BATCH_RE.match(line)
        if bm:
            current_batch = line.strip()

    return tasks, counts


def check_drift(actual_counts):
    if not OPERATING_STANDARD_PATH.exists():
        print("WARNING: OPERATING_STANDARD.md not found", file=sys.stderr)
        return
    text = OPERATING_STANDARD_PATH.read_text(encoding='utf-8')
    match = HEADER_RE.search(text)
    if match is None:
        print("WARNING: version header not found", file=sys.stderr)
        return
    try:
        hdr_pending = int(match.group(1))
        hdr_done = int(match.group(2))
        hdr_total = int(match.group(3))
    except (ValueError, IndexError):
        print("WARNING: unrecognized header format", file=sys.stderr)
        return
    actual_total = sum(actual_counts.values())
    warnings = []
    if hdr_pending != actual_counts.get('pending', 0):
        warnings.append(f"pending: header={{hdr_pending}} actual={{actual_counts.get('pending', 0)}}")
    if hdr_done != actual_counts.get('done', 0):
        warnings.append(f"done: header={{hdr_done}} actual={{actual_counts.get('done', 0)}}")
    if hdr_total != actual_total:
        warnings.append(f"total: header={{hdr_total}} actual={{actual_total}}")
    if warnings:
        print(f"WARNING: OPERATING_STANDARD.md stale — {{', '.join(warnings)}}", file=sys.stderr)


def main():
    tasks, counts = parse_todo()
    actionable = [t for t in tasks if t['status'] in ('pending', 'timeout')]
    result = {{
        'summary': {{
            'pending': counts.get('pending', 0),
            'timeout': counts.get('timeout', 0),
            'in_progress': counts.get('in_progress', 0),
            'done': counts.get('done', 0),
            'total': sum(counts.values()),
        }},
        'actionable_tasks': actionable,
    }}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    check_drift(counts)


if __name__ == '__main__':
    main()
"""


def generate_skill_template(name: str, project_dir: Path) -> str:
    slug = name.lower().replace(' ', '-').replace('_', '-')
    return f"""# SKILL.md — {name} Research Loop

## Context Loading
**File:** `{project_dir}/OPERATING_STANDARD.md`
Ini adalah satu-satunya dokumen instruksi yang perlu dimuat.

## Task Loading
```bash
python3 {project_dir}/runtime/tools/pending_tasks.py
```

## Runtime Flow
```bash
python3 {project_dir}/runtime/tools/runtime_engine.py reconcile
python3 {project_dir}/runtime/tools/runtime_engine.py start-run --run-id <run-id> --max-tasks 6
python3 {project_dir}/runtime/tools/runtime_engine.py claim --run-id <run-id> --limit 6
# ... process tasks ...
python3 {project_dir}/runtime/tools/runtime_engine.py finalize --run-id <run-id> --success <ids> --failed <ids>
```

## Worker Rules
- Jangan edit TODO.md
- Output path: sesuai mapping di pending_tasks.py
- Minimum 1200 karakter per output
- Wajib ada: Ringkasan, Relevansi, Sumber

## Scaling
- 0 task → clean stop
- 1-3 tasks → 1 worker
- 4-6 tasks → 2 workers (max 3 each)
"""


def generate_todo_skeleton(name: str, batches: list) -> str:
    lines = [
        f'# TODO — {name}',
        '',
        f'Progress: 0 / {sum(end - start + 1 for _, start, end, _ in batches)} task selesai',
        f'Last updated: 2026-04-19 (project created)',
        '',
    ]

    idx = 1
    for prefix, start, end, folder in batches:
        batch_letter = chr(ord('A') + idx - 1) if idx <= 26 else f'B{idx}'
        lines.append(f'## BATCH {batch_letter} — {folder.replace("_", " ").title()} ({end - start + 1} tasks)')
        lines.append('')
        for num in range(start, end + 1):
            task_id = f'{prefix}{num:03d}' if prefix in ('IHSG',) else f'{prefix}{num:03d}'
            lines.append(f'- [pending] {task_id} — TODO: {folder.replace("_", " ")} topic {num}')
        lines.append('')
        idx += 1

    lines.append('---')
    return '\n'.join(lines)


def main():
    print('=== New Research Project Setup ===\n')

    name = prompt('Project name (e.g. Crypto-Research)')
    domain = prompt('Domain (e.g. cryptocurrency, commodities, healthcare)')
    description = prompt('Short description')
    min_chars = int(prompt('Min output chars', '1200'))

    print(f'\nTier 1 sources (primary):')
    print('  Examples: IDX/BEI, JMA, NOAA, SEC EDGAR, WHO')
    source_tier1 = prompt('Tier 1 sources')

    print(f'\nTier 2 sources (academic):')
    print('  Examples: DOI papers, SSRN, jurnal resmi')
    source_tier2 = prompt('Tier 2 sources', 'Academic literature (DOI papers, journals)')

    print('\n=== Batch Configuration ===')
    print('Available examples in examples/EXAMPLE_BATCH_CONFIG.md')
    print()

    batches = prompt_batches()
    if not batches:
        print('No batches configured. Using default single batch.')
        prefix = prompt('Task prefix', 'P')
        count = int(prompt('Number of tasks', '10'))
        batches = [(prefix, 1, count, f'A_{domain.lower().replace(" ", "_")}')]

    # Create project
    project_dir = BASE_DIR / name
    project_dir.mkdir(parents=True, exist_ok=True)

    # OPERATING_STANDARD.md
    op_std = generate_operating_standard(
        project_dir, name, domain, description, batches,
        source_tier1, source_tier2, min_chars
    )
    (project_dir / 'OPERATING_STANDARD.md').write_text(op_std, encoding='utf-8')

    # pending_tasks.py
    pt = generate_pending_tasks(batches)
    (project_dir / 'runtime' / 'tools').mkdir(parents=True, exist_ok=True)
    (project_dir / 'runtime' / 'tools' / 'pending_tasks.py').write_text(pt, encoding='utf-8')

    # runtime_engine.py — copy from template (portable version)
    src_engine = TEMPLATES_DIR / 'runtime_engine.py'
    if src_engine.exists():
        shutil.copy2(src_engine, project_dir / 'runtime' / 'tools' / 'runtime_engine.py')
    else:
        print(f'WARNING: runtime_engine.py template not found at {src_engine}')

    # provenance_template.md
    prov_src = TEMPLATES_DIR / 'provenance_template.md'
    if prov_src.exists():
        (project_dir / 'runtime' / 'templates').mkdir(parents=True, exist_ok=True)
        shutil.copy2(prov_src, project_dir / 'runtime' / 'templates' / 'provenance_template.md')

    # TODO.md skeleton
    todo = generate_todo_skeleton(name, batches)
    (project_dir / 'TODO.md').write_text(todo, encoding='utf-8')

    # PLANRESEARCH.md
    plan = f'# PLANRESEARCH.md — {name}\n\n## 1. Niat awal\n\n{description}\n\n## 2. Batch structure\n\n'
    for prefix, start, end, folder in batches:
        plan += f'- {prefix}{start:03d}-{prefix}{end:03d}: {folder} ({end - start + 1} tasks)\n'
    plan += f'\nTotal: {sum(end - start + 1 for _, start, end, _ in batches)} tasks\n'
    (project_dir / 'PLANRESEARCH.md').write_text(plan, encoding='utf-8')

    # Directories
    for _, start, end, folder in batches:
        (project_dir / 'research' / 'papers' / folder).mkdir(parents=True, exist_ok=True)
    (project_dir / 'research' / 'notes').mkdir(parents=True, exist_ok=True)
    (project_dir / 'prompts').mkdir(parents=True, exist_ok=True)
    (project_dir / 'runtime' / 'runs').mkdir(parents=True, exist_ok=True)
    (project_dir / 'runtime' / 'results').mkdir(parents=True, exist_ok=True)
    (project_dir / 'runtime' / 'README.md').write_text(
        f'# Runtime — {name}\n\nSee OPERATING_STANDARD.md for runtime flow.\n', encoding='utf-8'
    )

    # SKILL.md template
    skill = generate_skill_template(name, project_dir)
    skill_dir = project_dir / '_skill_template'
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / 'SKILL.md').write_text(skill, encoding='utf-8')

    # Summary
    total_tasks = sum(end - start + 1 for _, start, end, _ in batches)
    print(f'\n=== Project created: {project_dir} ===')
    print(f'Total tasks: {total_tasks}')
    print(f'Batches: {len(batches)}')
    print(f'\nNext steps:')
    print(f'1. Edit TODO.md — replace "TODO:" placeholders with real task titles')
    print(f'2. Edit OPERATING_STANDARD.md — refine context and source tiers')
    print(f'3. python3 {project_dir}/runtime/tools/runtime_engine.py init')
    print(f'4. Copy _skill_template/SKILL.md to ~/.hermes/skills/')
    print(f'5. Register skill with Hermes')
    print(f'6. Test: python3 {project_dir}/runtime/tools/runtime_engine.py start-run --max-tasks 6')


if __name__ == '__main__':
    main()
