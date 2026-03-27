# RAG Evaluation Anti-Overfitting Plan

Date: 2026-03-28
Branch: feature/gtp-guidebook-redesign

## Goal
Build an evaluation loop that improves retrieval quality without overfitting to a tiny set of representative questions.

## Core Principle
Never make keep/revert decisions from the dev set alone.

The evaluation process must be split into:
- `dev`: fast debugging and iteration
- `validation`: accept/reject gate
- `holdout`: final confirmation only

## Why This Exists
The current project is vulnerable to overfitting because retrieval changes can appear to improve a few hand-checked queries while making the broader corpus worse.

Typical failure modes:
- tuning too aggressively for a named regulation like `????` or `?? ??`
- adding heuristics that improve one wording but degrade similar unseen phrasing
- repeatedly inspecting the same cases until the model/path overfits to them

## Dataset Structure
The representative suite in `backend/tests/autorag/representative_cases.json` is now split into:

### Dev
Purpose:
- fast iteration
- debugging retrieval failures
- inspecting citations manually

Allowed use:
- run often
- inspect full answers and citations
- use during implementation

Not allowed use:
- final keep/revert decision by itself

### Validation
Purpose:
- decide whether a change is actually better
- catch regressions outside the dev set

Allowed use:
- compare baseline vs candidate
- inspect summary metrics and selected failing cases

Keep rule:
- a retrieval change is only accepted if validation is flat or better on the agreed metrics

### Holdout
Purpose:
- final confidence check before keeping a candidate
- detect hidden overfitting to dev/validation

Allowed use:
- run after a candidate already looks good on validation
- review only enough to confirm that it is still healthy

Not allowed use:
- repeated retuning against holdout specifics
- adding heuristics because a single holdout item failed

If holdout fails:
- do not tune directly against the holdout question
- go back to dev and validation and fix the broader pattern

## Acceptance Rules
A retrieval candidate should only be kept when all of the following are true:

1. Dev set improves or becomes easier to diagnose
2. Validation set does not regress on aggregate quality
3. Holdout does not show a meaningful regression
4. No severe citation-quality regression appears in manual spot checks

## Recommended Metrics
Do not rely on a single metric.

Track at least:
- target document hit rate
- top citation quality
- article-section hit rate
- noise chunk rate
- preview-only rate
- validation average keyword coverage
- validation worst-case case score

## Noise Regression Checks
The following snippet classes should be tracked explicitly because they currently dominate failures:
- numeric garbage blocks like `000000`
- table fragments like `| | | ...`
- symbol-only or stamp-like snippets such as `?`, `(?)`
- title/header-only chunks without article substance

A candidate should be rejected if these noise snippets increase materially on validation or holdout.

## Operating Loop
Recommended loop:

1. Pick one retrieval hypothesis
2. Run local tests
3. Run `dev`
4. If dev is promising, run `validation`
5. If validation is acceptable, run `holdout`
6. Keep or revert
7. Record the result in history

## Candidate Size Discipline
Each experiment should change one retrieval idea at a time.

Examples of acceptable experiment scope:
- stronger shortlist hard lock
- article-first filtering inside shortlisted documents
- addendum penalty tuning
- markdown sanitization for numeric noise

Examples of unacceptable experiment scope:
- changing shortlist, reranker, parser, and confidence gate all at once

## Review Policy
When a candidate fails:
- identify whether it failed on dev, validation, or holdout
- classify the failure as one of:
  - retrieval miss
  - wrong document selection
  - wrong section ranking
  - noisy chunk contamination
  - answerability gate issue
- fix the broad class, not the exact question wording

## Current Recommendation
For this repository, the next experiments should be evaluated in this order:
1. shortlist hard-lock strength
2. article-only or article-first retrieval in locked mode
3. addendum/appendix/table suppression in locked mode
4. markdown pre-sanitization for law/government converted text

## Implementation Note
`backend/tests/autorag/run_representative_snapshot.py` now supports `--split`.

Recommended usage:
- `--split dev` during implementation
- `--split validation` before deciding to keep
- `--split holdout` only after validation passes

## Hard Rule
If a change only looks good on dev but not on validation, it is a regression candidate, not a success.
