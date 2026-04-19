# SKILL.md — IHSG-Stock-Analysis Research Loop

Skill ini menjalankan riset IHSG-Stock-Analysis secara otomatis via Hermes cron.

---

## Context Loading

Sebelum setiap run, muat dokumen operasional ini ke context:

**File:** `/home/sst/IHSG-Stock-Analysis/OPERATING_STANDARD.md`

Ini adalah **satu-satunya** dokumen instruksi yang perlu dimuat. JANGAN muat file lain (WORKFLOW_RUNTIME.md, PLANRESEARCH.md, dll).

## Task Loading

Sebelum memuat TODO.md, jalankan:

```bash
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/pending_tasks.py
```

Muat output JSON (~500 token) sebagai pengganti TODO.md utuh (~12,000 token).

## Runtime Flow

```bash
# 1. Reconcile
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/runtime_engine.py reconcile

# 2. Start run
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/runtime_engine.py start-run --run-id <run-id> --max-tasks 6

# 3. Claim tasks
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/runtime_engine.py claim --run-id <run-id> --limit 6

# 4. Process claimed tasks (research + write output files)
# ... worker logic here ...

# 5. Finalize
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/runtime_engine.py finalize --run-id <run-id> --success <ids> --failed <ids>
```

## Worker Rules

- Jangan edit TODO.md — hanya tulis output file
- Output path: sesuai mapping di pending_tasks.py
- Minimum 1000 karakter per output
- Wajib ada: Ringkasan Eksekutif, Relevansi IHSG, Sumber
- Bahasa Indonesia primer, istilah teknis Inggris

## Source Priority

1. **Tier 1:** IDX/BEI, OJK, BI, SEC EDGAR, Bloomberg
2. **Tier 2:** DOI paper, SSRN, jurnal finance
3. **Tier 3:** Google Scholar, Crossref
4. **Tier 4:** Blog teknis, newsletter

## Scaling

- 0 task claimed → clean stop
- 1-3 tasks → 1 batch worker
- 4-6 tasks → 2 batch workers (max 3 each)
