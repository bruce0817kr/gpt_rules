# HANDOFF

## Scope
- Branch: `feature/gtp-guidebook-redesign`
- PR: `https://github.com/bruce0817kr/gpt_rules/pull/1`
- Workspace used for implementation: `c:\Project\gpt_rules\.worktrees\gtp-guidebook-redesign`
- Canonical project root and runtime data: `c:\Project\gpt_rules`

## Current State
This branch contains two major tracks of work:
- UI redesign for `??????? ?? ? ???? ????`
- RAG retrieval investigation and child-parent retrieval groundwork

The codebase is testable and the recent retrieval/debugging changes are locally verified, but representative answer quality is still not acceptable.

## What Changed Recently
- Improved Korean title matching in `backend/app/services/retrieval_utils.py`
- Added shortlist-aware section scoring in `backend/app/services/chat.py`
- Added stronger parser/chunker filtering for weak markdown units
- Reindexed the full runtime corpus (`77` documents) against the latest worktree ingestion path
- Added a stronger shortlist path that can prefer lexical section search before dense retrieval
- Rebuilt the representative evaluation structure to reduce overfitting risk

## Evaluation Policy Reference
- `Docs/superpowers/specs/2026-03-28-rag-evaluation-anti-overfitting-plan.md`

## Representative Evaluation Structure
The representative suite is now split into three lanes in `backend/tests/autorag/representative_cases.json`:
- `dev`: fast debugging set
- `validation`: decision gate set
- `holdout`: final check set

Current principle:
- Tune on `dev`
- Decide on `validation`
- Confirm on `holdout`
- Do not repeatedly inspect and tune against holdout results

The runner now supports split selection:
- `python backend/tests/autorag/run_representative_snapshot.py --split dev --output-dir ...`
- `python backend/tests/autorag/run_representative_snapshot.py --split validation --output-dir ...`
- `python backend/tests/autorag/run_representative_snapshot.py --split holdout --output-dir ...`

## Files Changed In This Handoff Window
- `backend/app/services/retrieval_utils.py`
- `backend/app/services/chat.py`
- `backend/app/services/document_parser.py`
- `backend/app/services/chunker.py`
- `backend/tests/test_retrieval_utils.py`
- `backend/tests/test_chat.py`
- `backend/tests/test_document_parser.py`
- `backend/tests/test_chunker.py`
- `backend/tests/autorag/representative_cases.json`
- `backend/tests/autorag/run_representative_snapshot.py`
- `backend/tests/autorag/README.md`

## Verification
Recent successful runs in the worktree backend:
- `python -m pytest backend/tests/test_document_parser.py backend/tests/test_chunker.py -q`
  - `12 passed`
- `python -m pytest backend/tests/test_chat.py backend/tests/test_retrieval_utils.py -q`
  - `26 passed`

## Runtime Operations Performed
These runtime changes were applied against the root runtime environment:
- Full corpus reindex of all `77` documents
- Root DB `file_path` normalization to local Windows upload paths under `c:\Project\gpt_rules\backend\uploads`

These runtime changes were not committed as source changes.

## Current Retrieval Diagnosis
Even after full reindex, representative retrieval still fails in practice.

Observed failure modes:
- numeric garbage blocks like `000000`
- table fragments like `| | | ...`
- symbol-only snippets like `?`, `(?)`
- unrelated but high-similarity converted markdown fragments outranking article text

What is already true:
- raw uploaded markdown files are mostly readable
- parser-level extraction for representative documents looks reasonable
- dense retrieval over the shared collection is still attracted to low-signal converted chunks

## Likely Next Step
The next meaningful change is retrieval strategy, not another blind reindex.

Recommended order:
1. Strengthen shortlist hard-lock behavior when top1 title score is clearly dominant
2. When locked, search only the top1 document and prefer `ARTICLE` sections first
3. Exclude or heavily demote `ADDENDUM`, `APPENDIX`, `TABLE`, and `METADATA` sections during locked retrieval
4. Re-run `dev`, then `validation`, then `holdout`

## Important Git Hygiene
Do not commit runtime artifacts:
- `backend/data/huggingface/**`
- `backend/data/autorag/representative/**`

These were modified locally for offline runtime verification and snapshot output only.
