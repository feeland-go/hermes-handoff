# Verification Checklist

Jalankan setelah selesai semua langkah di 01_WEATHERXPROD dan 02_IHSG.

---

## WeatherxProd (`/home/sst/WeatherxProd/`)

```bash
cd /home/sst/WeatherxProd
```

### 1. pending_tasks.py
```bash
python3 runtime/tools/pending_tasks.py
```
- [ ] Output JSON: `pending: 52, timeout: 8, done: 495, total: 555`
- [ ] Tidak ada WARNING di stderr (drift detection clean)

### 2. runtime_engine.py status
```bash
python3 runtime/tools/runtime_engine.py status
```
- [ ] Counts sesuai: 495 done, 52 pending, 8 timeout

### 3. Stubs benar
```bash
wc -l AGENTS.md PLANRESEARCH.md WORKFLOW_RUNTIME.md
```
- [ ] Semua stub 4 baris atau kurang

```bash
wc -l /home/sst/Researchworkflow/RESEARCH_WORKFLOW_STANDARD.md /home/sst/Researchworkflow/CRON_RUNTIME_HARDENING.md /home/sst/Researchworkflow/AUDIT_P488_P493.md
```
- [ ] Semua stub 3 baris atau kurang

### 4. OPERATING_STANDARD.md ada
```bash
wc -l OPERATING_STANDARD.md
```
- [ ] >= 150 baris

### 5. Archive lengkap
```bash
ls Researchworkflow/_archive_pre_consolidation/
```
- [ ] Ada 6 file: AGENTS.md, PLANRESEARCH.md, WORKFLOW_RUNTIME.md, RESEARCH_WORKFLOW_STANDARD.md, CRON_RUNTIME_HARDENING.md, AUDIT_P488_P493.md

### 6. Skill hanya load OPERATING_STANDARD.md
- [ ] SKILL.md tidak referensi file lama
- [ ] SKILL.md memanggil `python3 /home/sst/WeatherxProd/runtime/tools/pending_tasks.py`

### 7. Dry-run test
```bash
python3 runtime/tools/runtime_engine.py start-run --run-id test-wxp --max-tasks 6
python3 runtime/tools/runtime_engine.py claim --run-id test-wxp --limit 6
```
- [ ] 6 task ter-claim
- [ ] Task IDs terlihat di output

---

## IHSG-Stock-Analysis (`/home/sst/IHSG-Stock-Analysis/`)

```bash
cd /home/sst/IHSG-Stock-Analysis
```

### 1. pending_tasks.py
```bash
python3 runtime/tools/pending_tasks.py
```
- [ ] Output JSON: `pending: 201, timeout: 8, done: 23, total: 232`
- [ ] Tidak ada WARNING di stderr

### 2. runtime_engine.py status
```bash
python3 runtime/tools/runtime_engine.py status
```
- [ ] Counts sesuai

### 3. OPERATING_STANDARD.md ada
```bash
wc -l OPERATING_STANDARD.md
```
- [ ] >= 150 baris

### 4. Skill terdaftar
```bash
ls ~/.hermes/skills/ihsg-research/
```
- [ ] Skill directory ada
- [ ] SKILL.md ada dan berisi instruksi

### 5. Dry-run test
```bash
python3 runtime/tools/runtime_engine.py start-run --run-id test-ihsg --max-tasks 6
python3 runtime/tools/runtime_engine.py claim --run-id test-ihsg --limit 6
```
- [ ] 6 task ter-claim
- [ ] Task IDs terlihat di output

---

## Global

### Research output utuh
```bash
find /home/sst/WeatherxProd/research/ -name "*.md" | wc -l
find /home/sst/IHSG-Stock-Analysis/research/ -name "*.md" | wc -l
```
- [ ] WeatherxProd: ~544 file (tidak berkurang)
- [ ] IHSG: ~37 file (tidak berkurang)

### Cron siap
- [ ] Cron WeatherxProd: aktif, interval sesuai, skill `sst-research-loop`
- [ ] Cron IHSG: aktif, interval sesuai, skill `ihsg-research-loop`
- [ ] Kedua cron menjalankan `--max-tasks 6` dan `--limit 6`
