# WeatherxProd — Instruksi Refactor

**Proyek:** `/home/sst/WeatherxProd/`
**Skill:** `~/.hermes/skills/sst-research/sst-research-loop/SKILL.md`

---

## Langkah 1: Backup file lama

```bash
mkdir -p /home/sst/WeatherxProd/Researchworkflow/_archive_pre_consolidation/

cp /home/sst/WeatherxProd/AGENTS.md /home/sst/WeatherxProd/Researchworkflow/_archive_pre_consolidation/AGENTS.md
cp /home/sst/WeatherxProd/PLANRESEARCH.md /home/sst/WeatherxProd/Researchworkflow/_archive_pre_consolidation/PLANRESEARCH.md
cp /home/sst/WeatherxProd/WORKFLOW_RUNTIME.md /home/sst/WeatherxProd/Researchworkflow/_archive_pre_consolidation/WORKFLOW_RUNTIME.md
cp /home/sst/Researchworkflow/RESEARCH_WORKFLOW_STANDARD.md /home/sst/WeatherxProd/Researchworkflow/_archive_pre_consolidation/RESEARCH_WORKFLOW_STANDARD.md
cp /home/sst/Researchworkflow/CRON_RUNTIME_HARDENING.md /home/sst/WeatherxProd/Researchworkflow/_archive_pre_consolidation/CRON_RUNTIME_HARDENING.md
cp /home/sst/Researchworkflow/AUDIT_P488_P493.md /home/sst/WeatherxProd/Researchworkflow/_archive_pre_consolidation/AUDIT_P488_P493.md
```

## Langkah 2: Pasang stubs

```bash
# Stubs di dalam WeatherxProd
cp stubs/AGENTS.md /home/sst/WeatherxProd/AGENTS.md
cp stubs/PLANRESEARCH.md /home/sst/WeatherxProd/PLANRESEARCH.md
cp stubs/WORKFLOW_RUNTIME.md /home/sst/WeatherxProd/WORKFLOW_RUNTIME.md

# Stubs di Researchworkflow top-level
cp stubs/RESEARCH_WORKFLOW_STANDARD.md /home/sst/Researchworkflow/RESEARCH_WORKFLOW_STANDARD.md
cp stubs/CRON_RUNTIME_HARDENING.md /home/sst/Researchworkflow/CRON_RUNTIME_HARDENING.md
cp stubs/AUDIT_P488_P493.md /home/sst/Researchworkflow/AUDIT_P488_P493.md
```

## Langkah 3: Pasang OPERATING_STANDARD.md

```bash
cp OPERATING_STANDARD.md /home/sst/WeatherxProd/OPERATING_STANDARD.md
```

## Langkah 4: Pasang pending_tasks.py

```bash
cp pending_tasks.py /home/sst/WeatherxProd/runtime/tools/pending_tasks.py
```

## Langkah 5: Pasang provenance template

```bash
mkdir -p /home/sst/WeatherxProd/runtime/templates/
cp provenance_template.md /home/sst/WeatherxProd/runtime/templates/provenance_template.md
```

## Langkah 6: Buat direktori scaffolding

```bash
mkdir -p /home/sst/WeatherxProd/prompts/
mkdir -p /home/sst/WeatherxProd/research/notes/
```

## Langkah 7: Update skill SKILL.md

Baca `SKILL_UPDATE.md` dan ikuti instruksinya untuk mengubah `~/.hermes/skills/sst-research/sst-research-loop/SKILL.md`.

## Langkah 8: Verifikasi

```bash
cd /home/sst/WeatherxProd
python3 runtime/tools/pending_tasks.py
# Harus keluar: 52 pending, 8 timeout, 495 done

python3 runtime/tools/runtime_engine.py status
# Harus keluar: counts yang sesuai

# Test dry-run
python3 runtime/tools/runtime_engine.py start-run --run-id test-wxp --max-tasks 6
python3 runtime/tools/runtime_engine.py claim --run-id test-wxp --limit 6
# Verifikasi 6 task ter-claim
```
