# IHSG-Stock-Analysis — Instruksi Setup

**Proyek:** `/home/sst/IHSG-Stock-Analysis/`
**Skill:** Belum ada — perlu dibuat

---

## Langkah 1: Pasang OPERATING_STANDARD_IHSG.md

```bash
cp OPERATING_STANDARD_IHSG.md /home/sst/IHSG-Stock-Analysis/OPERATING_STANDARD.md
```

## Langkah 2: Pasang pending_tasks.py

```bash
cp pending_tasks.py /home/sst/IHSG-Stock-Analysis/runtime/tools/pending_tasks.py
```

## Langkah 3: Pasang provenance template

```bash
mkdir -p /home/sst/IHSG-Stock-Analysis/runtime/templates/
cp provenance_template.md /home/sst/IHSG-Stock-Analysis/runtime/templates/provenance_template.md
```

## Langkah 4: Buat direktori scaffolding

```bash
mkdir -p /home/sst/IHSG-Stock-Analysis/prompts/
mkdir -p /home/sst/IHSG-Stock-Analysis/research/notes/
```

## Langkah 5: Buat skill baru untuk IHSG

Baca `SKILL_TEMPLATE.md` dan buat skill baru:

```bash
mkdir -p ~/.hermes/skills/ihsg-research/ihsg-research-loop/
# Buat SKILL.md berdasarkan template
```

## Langkah 6: Daftarkan skill ke Hermes

Jalankan command pendaftaran skill sesuai mekanisme Hermes di PC ini.
Pastikan skill `ihsg-research-loop` terdaftar dan aktif.

## Langkah 7: Verifikasi

```bash
cd /home/sst/IHSG-Stock-Analysis
python3 runtime/tools/pending_tasks.py
# Harus keluar: 201 pending, 8 timeout, 23 done

python3 runtime/tools/runtime_engine.py status
# Harus keluar counts yang sesuai

# Test dry-run
python3 runtime/tools/runtime_engine.py start-run --run-id test-ihsg --max-tasks 6
python3 runtime/tools/runtime_engine.py claim --run-id test-ihsg --limit 6
# Verifikasi 6 task ter-claim
```

## Langkah 8: Aktifkan cron

Setelah test berhasil, aktifkan cron untuk IHSG:
- Interval: sesuaikan (misal setiap 2-3 jam)
- Command: jalankan skill `ihsg-research-loop`
- Max-tasks: 6 per session
