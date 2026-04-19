# OPERATING_STANDARD.md — IHSG-Stock-Analysis Research Run Standard

<!-- version: 1.0 | updated: 2026-04-19 | pending: 201 | done: 23 | total: 232 -->

Last updated: 2026-04-19

---

## 1. Konteks Proyek

IHSG-Stock-Analysis adalah proyek riset untuk membangun sistem analisis saham IHSG (Indeks Harga Saham Gabungan) berbasis multiple approach: regime detection, technical analysis, fundamental analysis, smart money tracking, dan hybrid scoring.

**Hipotesis kunci:**
1. IHSA memiliki karakteristik unik: emerging market, dominated by commodities, limited liquidity di banyak saham
2. Multi-factor approach (regime + technical + fundamental + sentiment) lebih robust dari single-factor
3. Kombinasi academic research + practical repo analysis + data sourcing menghasilkan actionable intelligence
4. Regime detection adalah foundation — strategi harus adaptif terhadap market condition

**Status saat ini:** 23/232 done, 201 pending, 8 timeout.

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

### Tier 1 — Official / exchange data
Pakai dulu untuk data pasar, regulasi, dan spesifikasi produk keuangan.

Contoh: IDX/BEI, OJK, Bank Indonesia, SEC EDGAR, Bloomberg, Reuters.

### Tier 2 — Academic literature
Pakai untuk method, validation, scientific capability, comparative findings.

Contoh: DOI paper, SSRN, jurnal finance, conference paper (AFA, EFA).

### Tier 3 — Metadata / discovery
Pakai untuk menemukan jejak sumber formal. Bukan fondasi tunggal jika sumber primer ada.

Contoh: Google Scholar, Crossref, publisher metadata.

### Tier 4 — Secondary / supporting
Gunakan terbatas dan hati-hati.

Contoh: blog analisis teknis kredibel, catatan komunitas trading, newsletter.

### Fallback strategy
- **arXiv/SSRN rule:** satu brief pass saja. Jika 429 / zero-hit / noisy / irrelevant → pivot cepat ke Google Scholar → official docs → publisher pages.
- **Data-topic rule:** untuk data format, API spesifikasi, licensing → official docs dulu, paper hanya pelengkap.
- **Fallback note rule:** catat setiap fallback signifikan di output.

---

## 4. Standar Output

### Header wajib
```markdown
# IHSGxxx — Judul task
**Batch:** ...
**Topik:** ...
**Relevansi IHSG:** ...
```

### Section wajib
1. Ringkasan Eksekutif
2. Sintesis utama (bukan dump sumber)
3. Implikasi untuk IHSG-Stock-Analysis
4. Rekomendasi praktis / posisi realistis
5. Sumber (DOI, URL, atau `Sumber:`)
6. Catatan fallback bila relevan

### Gaya editorial
- Bahasa Indonesia primer, istilah teknis Inggris boleh
- Anti-overclaim: bedakan supported / plausible / hypothesis / not-ready
- Jawab "So what for IHSG analysis?" secara eksplisit

---

## 5. Quality Gate

### Runtime validator (otomatis)
- File ada di canonical path
- >= 1000 karakter
- Task ID di baris pertama
- Ada section "ringkasan"
- Ada penanda sumber (DOI/URL/Sumber:)
- Ada "relevansi proyek" atau "implikasi"

### Editorial gate (manual checklist)
- [ ] Relevansi IHSG eksplisit
- [ ] Ringkasan Eksekutif ada
- [ ] Sintesis, bukan dump sumber
- [ ] Implikasi produk/analisis jelas
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
