# Cron Prompt — IHSG-Stock-Analysis Research Loop (FINAL)

## Metadata
- **Interval:** every 120m (2 jam)
- **Max-tasks:** 6
- **Deliver:** telegram
- **Skill:** ihsg-research/ihsg-research-loop

---

## Prompt

```
IHSG Research Loop — autonomous run.

== GUARD ==
Run: python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/runtime_engine.py status
Parse JSON. If in_progress > 0, print "[BLOCKED] IHSG loop skipped — active runs" and STOP.

== LOAD STANDARD ==
read_file /home/sst/IHSG-Stock-Analysis/OPERATING_STANDARD.md

== GET TASKS ==
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/pending_tasks.py
Parse JSON. If 0 actionable_tasks, print "[IDLE] IHSG — no pending tasks" and STOP.

== REPORT START ==
Print exactly this line (this gets delivered to chat):
"[RUN] IHSG starting. Backlog: {pending} pending, {timeout} timeout, {done} done."

== RECONCILE ==
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/runtime_engine.py reconcile

== START RUN ==
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/runtime_engine.py start-run --run-id cron_$(date +%Y%m%d_%H%M%S) --max-tasks 6

== CLAIM ==
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/runtime_engine.py claim --run-id <RUN_ID> --limit 6

If 0 claimed: print "[IDLE] IHSG — no tasks claimed" and STOP.

== PROCESS (BUDGET ENFORCED) ==
For each claimed task:
- web_search: MAX 3 calls per task. Use specific queries.
- web_extract / full page fetch: MAX 2 per task. ONLY fetch after reviewing search snippets. Skip low-quality results from snippet preview.
- Output: 1200-2500 characters. Stop writing after 2500.
- Single-pass only: research once, write once, finalize. No revision loops.
- If search returns empty/429: write output with available info + note "partial research — source unavailable". Do NOT retry.
- If 3+ searches fail for one task: mark as failed, move to next task. Do not burn tokens.

Scaling:
- 1-3 tasks: 1 delegate_task batch
- 4-6 tasks: 2 delegate_task batches of 3 each

Worker output format:
- # IHSGxxx — Title
- ## Ringkasan Eksekutif
- ## Relevansi Proyek / Implikasi IHSG
- ## Sintesis
- ## Sumber (DOI/URL/Sumber:)

Workers MUST NOT edit TODO.md. Only write output files.

== FINALIZE ==
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/runtime_engine.py finalize --run-id <RUN_ID> --success "<ids>" --failed "<ids>"

== REPORT END ==
Run status again:
python3 /home/sst/IHSG-Stock-Analysis/runtime/tools/runtime_engine.py status

Print exactly this (this gets delivered to chat):
"[DONE] IHSG run <RUN_ID>. Success: <n>/<total>. Remaining: <pending> pending, <done> done. Failed: <list failed ids and reasons>"

== HARD STOPS ==
- Never skip guard
- Never claim more than 6
- Finalize exactly once
- On persistent 429/error: finalize failed tasks and stop
- Total web_search calls this run: MAX 18 (6 tasks × 3)
- Total web_extract calls this run: MAX 12 (6 tasks × 2)
```
