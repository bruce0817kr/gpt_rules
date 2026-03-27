# AutoRAG Evaluation Harness

This folder uses AutoRAG's evaluation decorators to test the current RAG implementation.

What it does:

- `build_bootstrap_dataset.py`
  - exports `corpus.parquet` from the ingested document catalog
  - exports `qa.parquet` from seed questions
  - uses the current system response and citations as bootstrap ground truth
- `evaluate_current_rag.py`
  - evaluates the current retrieval path with AutoRAG retrieval metrics
  - evaluates the current answer generation with AutoRAG generation metrics
- `representative_cases.json`
  - a small, stable query suite for integration checks and before/after comparisons
  - covers the questions that most often regress in this domain: travel expense rules, disciplinary procedures, vehicle management, contract review, facility-law lookup, procurement, leave, and audit evidence
- representative split policy
  - `dev`: fast debugging set; can be inspected frequently during tuning
  - `validation`: selection gate; use this to decide whether a retrieval change is actually better
  - `holdout`: final check; do not repeatedly tune against individual holdout results
- `compare_representative_runs.py`
  - compares two saved AutoRAG result directories against the representative query suite
  - scores generated answers with simple keyword coverage and reports retrieval/generation deltas
Important:

- The generated QA set is a bootstrap dataset, not a human-reviewed gold set.
- It is useful for smoke testing and relative regression checking.
- For trustworthy optimization, replace `generation_gt` and `retrieval_gt` with reviewed labels.

Gold-set expansion workflow:

- `generate_persona_candidates.py`
  - uses a persona sub-agent (for example `寃쎈젰 5?꾩감 吏곸썝`) to generate realistic question candidates
  - writes candidate cases to `backend/data/autorag/candidates/`
- `build_review_queue.py`
  - runs the current system on those candidates
  - pre-fills bootstrap answer/citation labels into a human review queue in `backend/data/autorag/review/`
- `export_reviewed_gold.py`
  - exports only approved review rows into `backend/data/autorag/gold/qa_gold_<run>.parquet`
  - this file can be passed to `evaluate_current_rag.py --qa-path ...`
- `merge_review_queues.py`
  - merges persona review queues and feedback review queues into one deduplicated backlog
  - writes `merged_review_queue_<run>.json` to `backend/data/autorag/review/`
- `generate_gold_backlog_report.py`
  - summarizes pending / approved / gold-ready review rows from the merged backlog
  - writes `gold_backlog_<run>.md` and `.json` to `backend/data/autorag/review/`
- `generate_review_packets.py`
  - splits pending review rows into balanced packets for human review
  - writes `review_packets_<run>.md` and `.json` to `backend/data/autorag/review/`
- `apply_review_decisions.py`
  - applies qid-based review decisions back to source `review_queue_*.json` / `feedback_review_queue_*.json`
  - use this before rerunning merge/export so approved rows survive the next gold ops loop

Recommended review rule:

- Persona-generated questions are candidate prompts, not gold labels.
- A row becomes gold only after a human reviewer confirms or edits `reviewed_generation_gt` and `reviewed_retrieval_gt`, then marks `review_status=approved`.

Suggested run order inside the backend container:

```bash
pip install -r /app/tests/autorag/requirements.txt
python /app/tests/autorag/build_bootstrap_dataset.py
python /app/tests/autorag/evaluate_current_rag.py
```

Representative integration check:

```bash
python /app/tests/autorag/evaluate_current_rag.py --qa-path /app/data/autorag/bootstrap/qa.parquet --output-dir /app/data/autorag/runs/baseline
python /app/tests/autorag/evaluate_current_rag.py --qa-path /app/data/autorag/bootstrap/qa.parquet --output-dir /app/data/autorag/runs/candidate
python /app/tests/autorag/compare_representative_runs.py --baseline-output-dir /app/data/autorag/runs/baseline --candidate-output-dir /app/data/autorag/runs/candidate --output-dir /app/data/autorag/representative --run-id integration_check
```

The representative comparison is row-aligned. Keep the case ordering in `representative_cases.json` stable so baseline and candidate runs stay comparable.
Persona candidate run:

```bash
python /app/tests/autorag/generate_persona_candidates.py --persona-id five_year_employee --run-id demo_run
python /app/tests/autorag/build_review_queue.py --cases-path /app/data/autorag/candidates/candidate_cases_five_year_employee_demo_run.json --run-id demo_run
python /app/tests/autorag/export_reviewed_gold.py --review-queue-path /app/data/autorag/review/review_queue_demo_run.json --run-id demo_run
python /app/tests/autorag/evaluate_current_rag.py --qa-path /app/data/autorag/gold/qa_gold_demo_run.parquet
```

Feedback-driven tuning workflow:

- The chat API now logs each answer with a `response_id` into `backend/data/feedback/chat_interactions.jsonl`.
- The frontend sends `good / bad` feedback per answer into `backend/data/feedback/chat_feedback.jsonl`.
- `bad` feedback requires at least one selected reason code such as `answer_incorrect`, `grounding_weak`, or `citation_mismatch`.
- `generate_feedback_report.py`
  - summarizes recent rated answers by answer mode and bad-reason distribution
  - writes artifacts to `backend/data/autorag/feedback/`
- `build_feedback_review_queue.py`
  - converts recent `bad` feedback into a review queue in `backend/data/autorag/review/`
  - deduplicates repeated bad questions and carries duplicate counts into `review_notes`

Suggested cadence:

- Launch stage: run every 3 days
- Stabilizing stage: run every 7 days
- Maintenance stage: run every 30 days

Feedback tuning run:

```bash
python /app/tests/autorag/generate_feedback_report.py --lookback-days 3 --run-id feedback_demo
python /app/tests/autorag/build_feedback_review_queue.py --lookback-days 3 --run-id feedback_demo
```

PowerShell wrapper:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_feedback_tuning_loop.ps1 -CadenceStage launch -RunId feedback_demo
```

Gold ops wrapper:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_gold_ops_loop.ps1 -RunId gold_ops_demo
```

If you also want to generate a fresh persona batch before merging:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_gold_ops_loop.ps1 -RunId gold_ops_demo -GenerateCandidates -PersonaIds new_employee,five_year_employee,team_lead,finance_officer
```





Representative split usage:

```bash
python /app/tests/autorag/run_representative_snapshot.py --cases-path /app/tests/autorag/representative_cases.json --split dev --output-dir /app/data/autorag/representative/dev_snapshot
python /app/tests/autorag/run_representative_snapshot.py --cases-path /app/tests/autorag/representative_cases.json --split validation --output-dir /app/data/autorag/representative/validation_snapshot
python /app/tests/autorag/run_representative_snapshot.py --cases-path /app/tests/autorag/representative_cases.json --split holdout --output-dir /app/data/autorag/representative/holdout_snapshot
```

Recommended evaluation loop:

1. Tune on `dev` only.
2. Accept or reject the change on `validation`.
3. Run `holdout` only after a candidate is worth keeping.
4. If `holdout` regresses, do not tune directly against it; go back to `dev` and `validation`.
