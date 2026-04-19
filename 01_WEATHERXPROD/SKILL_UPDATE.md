# Skill Update — sst-research-loop

**File:** `~/.hermes/skills/sst-research/sst-research-loop/SKILL.md`

---

## Perubahan yang harus dilakukan

### 1. Hapus loading 6 file lama

Hapus referensi ke file-file ini dari SKILL.md:

| File | Lokasi |
|---|---|
| PLANRESEARCH.md | `/home/sst/WeatherxProd/PLANRESEARCH.md` |
| WORKFLOW_RUNTIME.md | `/home/sst/WeatherxProd/WORKFLOW_RUNTIME.md` |
| AGENTS.md | `/home/sst/WeatherxProd/AGENTS.md` |
| RESEARCH_WORKFLOW_STANDARD.md | `/home/sst/Researchworkflow/RESEARCH_WORKFLOW_STANDARD.md` |
| CRON_RUNTIME_HARDENING.md | `/home/sst/Researchworkflow/CRON_RUNTIME_HARDENING.md` |
| AUDIT_P488_P493.md | `/home/sst/Researchworkflow/AUDIT_P488_P493.md` |

### 2. Tambah loading OPERATING_STANDARD.md

Ganti 6 file di atas dengan 1 file:

```
/home/sst/WeatherxProd/OPERATING_STANDARD.md
```

### 3. Ganti TODO.md context

**Sebelum:** Skill memuat TODO.md utuh ke context.

**Sesudah:** Skill menjalankan command ini dan memuat output-nya:
```
python3 /home/sst/WeatherxProd/runtime/tools/pending_tasks.py
```

Output adalah JSON compact (~500 token) yang berisi:
- `summary`: counts per status
- `actionable_tasks`: array task yang bisa dikerjakan (pending + timeout)

### 4. Pastikan max-tasks 6

Runtime flow harus menggunakan:
```bash
python3 /home/sst/WeatherxProd/runtime/tools/runtime_engine.py start-run --run-id <id> --max-tasks 6
python3 /home/sst/WeatherxProd/runtime/tools/runtime_engine.py claim --run-id <id> --limit 6
```

`--max-tasks 6` dan `--limit 6` adalah default, tapi pastikan tidak di-override ke 1.

### 5. Token savings yang diharapkan

| Komponen | Sebelum | Sesudah |
|---|---|---|
| Dokumen instruksi | ~21,000 token | ~3,500 token |
| TODO.md context | ~12,000 token | ~500 token |
| **Total context** | **~33,000** | **~4,000** |
