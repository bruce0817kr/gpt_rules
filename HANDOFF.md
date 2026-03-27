# HANDOFF

## Scope
- Branch: `feature/gtp-guidebook-redesign`
- PR: `https://github.com/bruce0817kr/gpt_rules/pull/1`
- Workspace used for implementation: `c:\Project\gpt_rules\.worktrees\gtp-guidebook-redesign`
- Canonical project root and runtime data: `c:\Project\gpt_rules`

## What Changed In This Session
- Improved Korean document-title matching for shortlist routing.
- Hardened shortlist section scoring in `chat.py` so section fallback uses the same Korean token normalization as retrieval.
- Repaired corrupted user-facing fallback/system prompt strings in `chat.py` with clean ASCII text.
- Added parser/chunker filtering for weak markdown units:
  - front matter separators
  - standalone effective-date headers
  - title metadata lines
  - symbol-only / zero-only / short low-information blocks
- Added focused regression tests for:
  - Korean particle-aware title matching
  - shortlist section scoring
  - markdown front matter filtering
  - zero/symbol-only chunk dropping
- Reindexed all 77 documents in the root runtime DB/Qdrant using the latest worktree ingestion code.

## Files Changed
- `backend/app/services/retrieval_utils.py`
- `backend/app/services/chat.py`
- `backend/app/services/document_parser.py`
- `backend/app/services/chunker.py`
- `backend/tests/test_retrieval_utils.py`
- `backend/tests/test_chat.py`
- `backend/tests/test_document_parser.py`
- `backend/tests/test_chunker.py`

## Verification Run
Executed successfully in the worktree backend:
- `python -m pytest backend/tests/test_document_parser.py backend/tests/test_chunker.py -q`
- `python -m pytest backend/tests/test_chat.py backend/tests/test_retrieval_utils.py -q`

Latest observed results:
- parser/chunker tests: `12 passed`
- chat/retrieval tests: `26 passed`

## Runtime Work Performed
The following runtime operation was performed against the root runtime data:
- Full reindex of all `77` documents using the latest worktree ingestion pipeline.
- Root DB document `file_path` values were normalized to local Windows paths under `c:\Project\gpt_rules\backend\uploads` where needed.

## Current Status
The code changes are structurally correct and tests are green, but representative retrieval quality is still not acceptable.

Representative questions still fail in practice:
- `?????? ?? ??? ???? ????`
- `???? ?? ???? ?? ??? ?? ?? ??? ????`
- `?? ??? ??? ?? ??? ????`

Current failure mode:
- Dense retrieval continues to surface noisy converted chunks such as:
  - `000000`
  - table fragments like `| | | ...`
  - symbol-only snippets such as `?`, `(?)`
- Even after full reindex, these noisy chunks still outrank the intended article text for the representative queries.

## Root Cause Assessment
The current bottleneck is no longer "needs reindex".

The remaining bottleneck is retrieval strategy and corpus normalization:
- Converted markdown for many regulations/laws still contains many low-signal blocks.
- Dense retrieval over the shared collection is still attracted to those blocks.
- Title shortlist and section fallback are improved, but not sufficient by themselves.

## Recommended Next Steps
1. Make document shortlist a stronger constraint in `chat.py`.
   - When shortlist confidence is high, prefer shortlisted-document-only retrieval instead of using it as a weak hint.
2. In shortlisted documents, prefer `ARTICLE` sections and demote or exclude `ADDENDUM`, `APPENDIX`, `TABLE`, and `METADATA` sections by default.
3. Add a markdown sanitization step before section splitting.
   - Remove top metadata bullets like `- efYd:` and `- API:`.
   - Remove pure numeric ID lines.
   - Remove repeated table separator fragments that have no semantic payload.
4. Reindex all 77 documents again after the next sanitization/retrieval change.
5. Re-run the three representative questions after each retrieval change.

## Important Git Hygiene
Do not commit these runtime artifacts:
- `backend/data/huggingface/**`
- `backend/data/autorag/representative/**`

These were modified locally for offline model/runtime verification and are not source changes.

## Suggested Commit Grouping
This handoff commit should include only:
- source code files
- test files
- this `HANDOFF.md`

It should exclude runtime cache and generated evaluation artifacts.
