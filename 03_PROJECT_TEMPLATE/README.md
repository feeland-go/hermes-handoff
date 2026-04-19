# Project Template — Cara Pakai

Template ini untuk membuat proyek riset baru dengan satu command.

## Cara Pakai

```bash
cd /home/sst/Researchworkflow/HERMES_HANDOFF/03_PROJECT_TEMPLATE/
python3 setup_new_project.py
```

Script akan menanyakan:
1. Nama proyek (misal: `Crypto-Research`, `Komoditas-Analysis`)
2. Domain riset (misal: cryptocurrency, commodities, healthcare)
3. Deskripsi singkat
4. Daftar batch — bisa pilih dari contoh atau custom

Output: folder proyek siap pakai di `/home/sst/<NAMA_PROYEK>/`

## File yang Dihasilkan

```
<NAMA_PROYEK>/
├── OPERATING_STANDARD.md      ← Dokumen operasional tunggal
├── TODO.md                    ← Backlog task (skeleton)
├── PLANRESEARCH.md             ← Rencana riset
├── runtime/
│   ├── tools/
│   │   ├── runtime_engine.py  ← Engine (portabel, dynamic ROOT)
│   │   └── pending_tasks.py   ← Ekstrak pending tasks + drift detection
│   ├── templates/
│   │   └── provenance_template.md
│   ├── runs/
│   └── results/
├── research/
│   ├── papers/<batch_folders>/
│   └── notes/
└── prompts/
```

## Setelah Generate

1. Edit `TODO.md` — isi task sesuai rencana riset
2. Edit `OPERATING_STANDARD.md` — sesuaikan section 1 (konteks) dan section 3 (sumber)
3. Buat skill Hermes berdasarkan `templates/SKILL.md.template`
4. Daftarkan skill ke Hermes
5. Jalankan `python3 runtime/tools/runtime_engine.py init`
6. Test: `python3 runtime/tools/runtime_engine.py start-run --max-tasks 6`
7. Aktifkan cron

## Contoh Konfigurasi Batch

Lihat `examples/EXAMPLE_BATCH_CONFIG.md` untuk contoh batch mapping berbagai domain.
