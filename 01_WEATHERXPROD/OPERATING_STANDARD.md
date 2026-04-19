# OPERATING_STANDARD.md — WeatherxProd Research Run Standard

<!-- version: 1.1 | updated: 2026-04-19 | pending: 52 | done: 495 | total: 555 -->

Last updated: 2026-04-19

---

## 1. Konteks Proyek

WeatherxProd adalah metocean SaaS untuk Indonesia — domain maritim, offshore, pelayaran, dan cuaca tropis. Tujuan riset ini membangun knowledge base terstruktur untuk merancang produk.

**Hipotesis kunci:**
1. Bukan "weather app umum", tapi layanan metocean bernilai tinggi
2. Kekuatan: kombinasi nowcasting + forecasting + satelit + interpretasi operasional
3. Indonesia punya kebutuhan unik: maritim luas, observasi tidak merata, konveksi tropis kompleks
4. Nilai komersial dari information product yang actionable, bukan data mentah
5. Differentiation dari kombinasi multi-layer, bukan satu layer tunggal

**Status saat ini:** 495/555 done, 52 pending, 8 timeout.

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

### Aturan penting
- Reconcile wajib sebelum claim baru
- Jangan claim lebih dari 6 task per run
- Jangan melebihi 3 task per batch worker
- Worker tidak boleh edit TODO.md
- Finalize terpusat oleh coordinator

### Pre-run context loading
Sebelum memuat TODO.md ke context, jalankan:
```
python3 runtime/tools/pending_tasks.py
```
Ini mengembalikan hanya task yang bisa dikerjakan (pending + timeout).
JANGAN muat TODO.md utuh ke context kecuali untuk review manual penuh.

---

## 3. Prioritas Sumber & Fallback

### Tier 1 — Operator / official docs
Pakai dulu untuk topik operasional (format data, kebijakan, spesifikasi sistem, licensing).

Contoh: JMA, JAXA, WMO, NOAA, ECMWF, vendor resmi.

### Tier 2 — Formal literature
Pakai untuk method, validation, scientific capability, comparative findings.

Contoh: DOI paper, jurnal resmi, conference paper.

### Tier 3 — Metadata / discovery
Pakai untuk menemukan jejak sumber formal. Bukan fondasi tunggal jika sumber primer ada.

Contoh: Crossref, publisher metadata, abstract records.

### Tier 4 — Secondary / supporting
Gunakan terbatas dan hati-hati.

Contoh: blog teknis kredibel, catatan komunitas.

### Fallback strategy
- **arXiv rule:** satu brief pass saja. Jika 429 / zero-hit / noisy / irrelevant → pivot cepat ke CrossRef → operator docs → publisher pages.
- **Operational-topic rule:** untuk data format, service architecture, licensing → operator docs dulu, paper hanya pelengkap.
- **Fallback note rule:** catat setiap fallback signifikan di output.

---

## 4. Standar Output

### Header wajib
```markdown
# Pxxx — Judul task
**Batch:** ...
**Topik:** ...
**Relevansi WeatherxProd:** ...
```

### Section wajib
1. Ringkasan Eksekutif
2. Sintesis utama (bukan dump sumber)
3. Implikasi untuk WeatherxProd
4. Rekomendasi praktis / posisi realistis
5. Sumber (DOI, URL, atau `Sumber:`)
6. Catatan fallback bila relevan

### Gaya editorial
- Bahasa Indonesia primer, istilah teknis Inggris boleh
- Anti-overclaim: bedakan supported / plausible / hypothesis / not-ready
- Jawab "So what for WeatherxProd?" secara eksplisit

---

## 5. Quality Gate

### Runtime validator (otomatis)
- File ada di canonical path
- >= 1200 karakter
- Task ID di baris pertama
- Ada section "ringkasan"
- Ada penanda sumber (DOI/URL/Sumber:)

### Editorial gate (manual checklist)
- [ ] Relevansi WeatherxProd eksplisit
- [ ] Ringkasan Eksekutif ada
- [ ] Sintesis, bukan dump sumber
- [ ] Implikasi produk jelas
- [ ] Rekomendasi realistis
- [ ] Sumber tercantum
- [ ] Catatan fallback jika ada
- [ ] Anti-overclaim
- [ ] Jawaban "so what?" jelas

---

## 6. Context Hygiene Rules

### Progressive disk writing
- Setelah 3+ search results, tulis findings ke research/notes/<task_id>_notes.md
- Jangan akumulasi full web page di conversation context
- Extract relevant quotes, discard the rest

### Search triage
- Review snippet dulu (title + preview)
- Fetch full content hanya top 3-5 results
- Skip source yang low-quality dari snippet

### File-based handoffs
- Researcher tulis notes ke research/notes/<task_id>_notes.md
- Researcher return 1-line summary: "Found N sources. Notes at [path]."
- Writer baca notes file, bukan menerima raw research di prompt
- Writer tulis output ke canonical path

### Context budget
- Target: sub-agent context tidak melebihi 8,000 token
- Lead agent load OPERATING_STANDARD.md sekali, dispatch focused sub-agents
- Sub-agent hanya load prompt-nya sendiri + file spesifik yang dibutuhkan

---

## 7. Dekomposisi Agent & Orkestrasi

### Scale decision
- Task sederhana (lookup, deskripsi tunggal) → direct search, tanpa sub-agent
- Task kompleks (multi-source, comparative) → gunakan alur 3-tahap

### Alur orkestrasi (task kompleks)
1. Coordinator claims task, assign ke researcher
2. Researcher baca prompts/researcher.md, kumpulkan bukti
3. Researcher tulis notes ke research/notes/<task_id>_notes.md
4. Researcher return 1-line summary ke coordinator
5. Coordinator assign ke writer
6. Writer baca prompts/writer.md + notes file → tulis output
7. Coordinator assign ke verifier
8. Verifier baca prompts/verifier.md → cek sitasi, verifikasi URL
9. Verifier tulis provenance sidecar
10. Verifier return 1-line: "Verification: PASS/FAIL. Provenance at [path]."
11. Coordinator finalize

### Status implementasi
Prompt files akan dibuat di prompts/ ketika dibutuhkan (untuk IHSG atau sisa task kompleks WeatherxProd).

---

## 8. Sistem Provenance

### Lokasi sidecar
- Output: `research/papers/<batch>/<task_id>.md`
- Provenance: `research/papers/<batch>/<task_id>.provenance.md`

### Konten provenance
```markdown
# Provenance: TASK_ID — Title
- **Date:** ...
- **Run ID:** ...
- **Sources consulted:** N
- **Sources accepted:** N
- **Sources rejected:** N — [reasons]
- **Fallback events:** [description]
- **Verification:** PASS / PASS WITH NOTES / BLOCKED
- **Research notes:** research/notes/<task_id>_notes.md
```

### Kebijakan
- Opsional untuk task yang sudah done
- Wajib untuk task baru
- Kehadiran provenance tidak memblokir finalize
