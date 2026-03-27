# Distribution-Based RAG Evaluation Set Design

Date: 2026-03-28
Branch: feature/gtp-guidebook-redesign

## Goal
Replace the current small representative suite with a distribution-aware evaluation set that reduces overfitting risk and reflects the actual corpus and question mix.

## Why This Is Needed
The current representative suite is useful for smoke checks, but it is not sufficient for retrieval optimization.

Main risks today:
- too much weight on a few named-document questions
- repeated tuning against the same small cases
- poor visibility into which corpus slices regress
- optimization bias toward wording that appears in the current dev set

A better evaluation set must reflect:
- document-type distribution
- question-type distribution
- named-document vs unnamed-document balance
- retrieval difficulty variance

## Current Corpus Shape
The current root corpus is approximately:
- `rule`: 51
- `law`: 13
- `guide`: 11
- `foundation`: 2

Implication:
- evaluation should not be evenly balanced across document types
- `rule` must have the largest share
- `law` and `guide` must still be represented enough to catch regressions
- `foundation` can stay small and mostly appear in holdout or targeted checks

## Evaluation Set Structure
Use three levels:

### Dev Set
Purpose:
- rapid debugging
- reproduction of known failures
- manual inspection of citations and answer structure

Recommended size:
- `12` to `15` questions

Composition:
- `rule`: 7 to 9
- `law`: 2 to 3
- `guide`: 2 to 3
- `foundation`: 0 to 1

Rule:
- dev is allowed to contain known hard failures
- dev is not used as the final accept/reject gate

### Validation Set
Purpose:
- actual keep/revert decision
- detect regressions outside dev

Recommended size:
- `24` to `36` questions

Composition target:
- `rule`: 14 to 20
- `law`: 5 to 7
- `guide`: 4 to 6
- `foundation`: 1 to 2

Rule:
- validation must be broad enough that a heuristic aimed at one named regulation cannot dominate the result

### Holdout Set
Purpose:
- final confirmation after validation passes
- detect hidden overfitting

Recommended size:
- `12` to `18` questions

Composition:
- same general ratio as validation, but do not inspect these repeatedly during tuning

Rule:
- do not tune directly against individual holdout failures

## Required Metadata Per Question
Every evaluation question should carry these fields.

Required:
- `id`
- `split`
- `doc_type`
  - `foundation | rule | law | guide`
- `query_type`
  - `procedure | criteria | responsibility | evidence | lookup | comparison | definition | exception`
- `document_named`
  - `true | false`
- `answer_mode`
- `categories`
- `question`
- `expected_keywords`
- `benchmark_note`

Strongly recommended:
- `expected_target_document`
- `expected_source_type`
  - usually `ARTICLE`
- `difficulty`
  - `easy | medium | hard`
- `domain`
  - `hr | finance | procurement | legal | admin | facility | research`

## Query-Type Distribution
Do not let all questions collapse into named-document summary prompts.

Recommended validation mix:
- `procedure`: 20% to 25%
- `criteria`: 20% to 25%
- `responsibility`: 10% to 15%
- `evidence`: 10% to 15%
- `lookup`: 10% to 15%
- `comparison`: 5% to 10%
- `definition`: 5% to 10%
- `exception`: 5% to 10%

## Named vs Unnamed Balance
A large source of overfitting is named-document prompts.

Recommended ratio:
- named-document questions: `40%`
- unnamed-document questions: `60%`

Examples:
- named: `?? ??? ??? ?? ??? ????`
- unnamed: `??? ?? ??? ??? ???? ????`

The unnamed share is critical because real users often do not know the exact regulation name.

## Difficulty Bands
Questions should be distributed across difficulty levels.

### Easy
- one obvious target document
- one obvious target article
- direct keyword overlap

### Medium
- one likely document, but article selection still matters
- wording may be indirect
- multiple plausible sections exist

### Hard
- multiple plausible documents
- question is abstract or operational
- answer may require article selection plus exception handling

Validation should include all three. If not, retrieval tuning will overfit to easy named lookups.

## Acceptance Criteria For New Questions
A question is good enough for the evaluation set when:
- it maps to a realistic employee task
- the expected document family is clear enough to evaluate
- the expected article/source type is reasonably identifiable
- it is not just a trivial rewording of another question

Reject or rewrite questions that are:
- too generic to evaluate grounding quality
- duplicates in different wording only
- dependent on reviewer interpretation instead of concrete evidence

## Scoring Guidance
For validation and holdout, track metrics by segment, not only in aggregate.

Required slices:
- by `doc_type`
- by `query_type`
- by `document_named`
- by `difficulty`

At minimum, compare:
- keyword coverage
- preview-only rate
- top citation quality
- article hit rate
- noise chunk rate

A candidate should be rejected if it improves one slice while materially damaging another important slice.

## Rollout Plan
### Phase 1
Repair the current representative manifest so question strings are not corrupted.

### Phase 2
Add metadata fields to all current questions:
- `doc_type`
- `query_type`
- `document_named`
- `difficulty`
- `domain`
- `expected_target_document`
- `expected_source_type`

### Phase 3
Expand the set to the target counts:
- dev: 12 to 15
- validation: 24 to 36
- holdout: 12 to 18

### Phase 4
Update the validation gate to report segmented results, not just whole-split averages.

## Immediate Next Step
Before adding more retrieval heuristics, repair and enrich `backend/tests/autorag/representative_cases.json` with the metadata schema above. The current file should be treated as a temporary scaffold, not a stable long-term evaluation set.
