# Test Mode — Single Run + Token Report

Jalankan prompt ini secara manual (bukan via cron) untuk test 1x run dan lihat token usage.

Pilih salah satu: WxP atau IHSG. Ganti `/home/sst/` sesuai PC kamu.

---

## Test: WeatherxProd

```
TEST MODE — single run with token tracking. Do NOT run as cron.

You are testing an optimized WeatherxProd research loop. The goal is to run exactly ONCE, process tasks, and report token usage.

== GUARD ==
Run: python3 /home/sst/WeatherxProd/runtime/tools/runtime_engine.py has-active-runs
If blocked: true, report and STOP.

== LOAD STANDARD ==
read_file /home/sst/WeatherxProd/OPERATING_STANDARD.md

== GET TASKS ==
python3 /home/sst/WeatherxProd/runtime/tools/pending_tasks.py
Parse JSON. Report: pending, timeout, done counts.

== START RUN ==
python3 /home/sst/WeatherxProd/runtime/tools/runtime_engine.py reconcile
python3 /home/sst/WeatherxProd/runtime/tools/runtime_engine.py start-run --run-id test_$(date +%Y%m%d_%H%M%S) --max-tasks 6
python3 /home/sst/WeatherxProd/runtime/tools/runtime_engine.py claim --run-id <RUN_ID> --limit 6

== PROCESS (BUDGET ENFORCED) ==
For each claimed task:
- web_search: MAX 3 calls per task
- web_extract: MAX 2 per task (snippet review first)
- Output: 1200-2500 chars. Single pass. No retry.
- On failure: write partial output + note. Move to next.

== FINALIZE ==
python3 /home/sst/WeatherxProd/runtime/tools/runtime_engine.py finalize --run-id <RUN_ID> --success "<ids>" --failed "<ids>"

== TOKEN REPORT (MANDATORY) ==
After finalize, print this exact format:

```
========== TEST RUN REPORT ==========
Run ID: <RUN_ID>
Tasks claimed: <n>
Tasks success: <n>
Tasks failed: <n> — <reasons>

BUDGET USAGE:
- web_search calls: <actual> / 18 max
- web_extract calls: <actual> / 12 max
- Output files written: <n>
- Shortest output: <chars> chars (<task_id>)
- Longest output: <chars> chars (<task_id>)

ESTIMATED TOKEN USAGE:
- Context loading (OPERATING_STANDARD + pending_tasks): ~4,000
- Web research (search + fetch): ~<calculate based on calls × ~5,000 avg>
- Agent reasoning + output: ~<calculate based on tasks × ~8,000 avg>
- Total estimated: ~<sum>

REMAINING BACKLOG:
- Pending: <n>
- Timeout: <n>
- Done: <n>
=====================================
```

HARD STOPS: Never claim more than 6. Finalize once. On error: finalize failed and report.
```

---

## Test: IHSG

```
TEST MODE — single run with token tracking. Do NOT run as cron.

You are testing an optimized IHSG research loop. The goal is to run exactly ONCE, process tasks, and report token usage.

== GUARD ==
Run: python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/runtime_engine.py status
If in_progress > 0, report "[BLOCKED]" and STOP.

== LOAD STANDARD ==
read_file /home/sst/IHSG-Stock-Analysis/OPERATING_STANDARD.md

== GET TASKS ==
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/pending_tasks.py
Parse JSON. Report: pending, timeout, done counts.

== START RUN ==
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/runtime_engine.py reconcile
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/runtime_engine.py start-run --run-id test_$(date +%Y%m%d_%H%M%S) --max-tasks 6
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/runtime_engine.py claim --run-id <RUN_ID> --limit 6

== PROCESS (BUDGET ENFORCED) ==
For each claimed task:
- web_search: MAX 3 calls per task
- web_extract: MAX 2 per task (snippet review first)
- Output: 1200-2500 chars. Single pass. No retry.
- On failure: write partial output + note. Move to next.

== FINALIZE ==
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/runtime_engine.py finalize --run-id <RUN_ID> --success "<ids>" --failed "<ids>"

== TOKEN REPORT (MANDATORY) ==
After finalize, print this exact format:

```
========== TEST RUN REPORT ==========
Run ID: <RUN_ID>
Tasks claimed: <n>
Tasks success: <n>
Tasks failed: <n> — <reasons>

BUDGET USAGE:
- web_search calls: <actual> / 18 max
- web_extract calls: <actual> / 12 max
- Output files written: <n>
- Shortest output: <chars> chars (<task_id>)
- Longest output: <chars> chars (<task_id>)

ESTIMATED TOKEN USAGE:
- Context loading (OPERATING_STANDARD + pending_tasks): ~4,000
- Web research (search + fetch): ~<calculate based on calls × ~5,000 avg>
- Agent reasoning + output: ~<calculate based on tasks × ~8,000 avg>
- Total estimated: ~<sum>

REMAINING BACKLOG:
- Pending: <n>
- Timeout: <n>
- Done: <n>
=====================================
```

HARD STOPS: Never claim more than 6. Finalize once. On error: finalize failed and report.
```

---

## Cara Pakai

1. Paste salah satu prompt di atas ke Hermes sebagai pesan manual (bukan cron)
2. Tunggu sampai selesai
3. Baca TEST RUN REPORT di akhir output
4. Cek token usage aktual dari dashboard API provider
5. Bandingkan estimasi vs aktual

## Yang Dicari dari Test

- [ ] Run selesai tanpa error
- [ ] 6 task ter-claim
- [ ] Output files written di canonical path
- [ ] web_search ≤ 18 calls
- [ ] web_extract ≤ 12 calls
- [ ] Output antara 1200-2500 chars
- [ ] Token usage aktual < 100.000 (target: 60.000-80.000)
- [ ] TEST RUN REPORT lengkap tercetak

Kalau token > 100.000, berarti budget belum efektif — perlu disesuaikan.
