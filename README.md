# Hermes Handoff — WeatherxProd + IHSG Workflow Refactor

**Tanggal:** 2026-04-19
**Tujuan:** Refactor 2 proyek riset di PC ini agar hemat token dan bisa jalan 6 task per session.

---

## Urutan Eksekusi

**Prioritas 1: `02_IHSG/`** — 201 pending tasks (86% belum selesai), belum punya skill Hermes.
**Prioritas 2: `01_WEATHERXPROD/`** — 52 pending tasks (9%), sudah punya skill tapi perlu update.
**Prioritas 3: `03_PROJECT_TEMPLATE/`** — Template untuk proyek riset baru ke depan.

## Peringatan

- **JANGAN ubah `runtime_engine.py`** — path sudah benar di PC ini
- **JANGAN ubah format `TODO.md`** — regex engine bergantung padanya
- **JANGAN modifikasi file di `research/`** — semua output harus utuh
- **Test manual 1 run** sebelum aktifkan cron

## Struktur Folder

```
HERMES_HANDOFF/
├── 01_WEATHERXPROD/     ← Refactor WeatherxProd (update skill + stub 6 file lama)
├── 02_IHSG/             ← Setup IHSG (buat skill baru + OPERATING_STANDARD)
├── 03_PROJECT_TEMPLATE/ ← Template scaffolding proyek riset baru
└── VERIFY.md            ← Checklist verifikasi setelah selesai
```

## Cara Pakai

1. Baca `02_IHSG/INSTRUCTIONS.md` → eksekusi langkah-langkahnya
2. Baca `01_WEATHERXPROD/INSTRUCTIONS.md` → eksekusi langkah-langkahnya
3. Jalankan `VERIFY.md` checklist
4. Test: `python3 runtime/tools/runtime_engine.py start-run --run-id test-001 --max-tasks 6`
5. Claim: `python3 runtime/tools/runtime_engine.py claim --run-id test-001 --limit 6`
6. Pastikan 6 task ter-claim, lalu finalize test run

## Token Savings (per run, per proyek)

| Komponen | Sebelum | Sesudah | Hemat |
|---|---|---|---|
| Dokumen instruksi | ~21,000 | ~3,500 | ~17,500 |
| TODO.md context | ~12,000 | ~500 | ~11,500 |
| **Total context** | **~33,000** | **~4,000** | **~29,000** |
