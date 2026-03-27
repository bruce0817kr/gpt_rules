# Child-Parent Retrieval Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 규정/규칙/법령 문서 전반에서 child-parent 청킹과 구조 메타데이터를 기반으로 retrieval 품질을 근본적으로 개선한다.

**Architecture:** 문서를 조문 중심 parent와 의미 단위 child로 분해하고, hybrid retrieval 후 parent 단위로 다시 집계한다. generation 전 answerability gate를 둬 weak chunk 중심 응답을 줄이고, 병렬 구현이 가능하도록 공통 타입과 모듈 경계를 먼저 잠근다.

**Tech Stack:** FastAPI, Python, Qdrant, sentence-transformers, CrossEncoder, pytest

---

## Parallel Work Map

### Lane 0. Integration Owner

책임:
- 공통 타입 고정
- 병렬 lane 취합
- 최종 regression QA 실행

수정 범위:
- 공통 타입 정의 파일
- integration notes
- 최종 merge 브랜치

### Lane 1. Structured Parser

책임:
- 조문/부칙/별표 구조 파싱
- path_key 생성

예상 파일:
- `backend/app/services/document_parser.py`
- `backend/tests/test_document_parser.py`
- 새 fixture 파일들

### Lane 2. Parent/Child Chunking

책임:
- parent chunk 생성
- child chunk 생성
- source type tagging

예상 파일:
- `backend/app/services/chunker.py`
- `backend/tests/test_chunker.py`
- 신규 chunk schema tests

### Lane 3. Index Schema And Storage

책임:
- vector store payload 확장
- parent-child mapping 저장

예상 파일:
- `backend/app/services/vector_store.py`
- `backend/app/models/schemas.py`
- `backend/tests/test_catalog.py`
- 신규 index schema tests

### Lane 4. Retrieval + Aggregation

책임:
- hybrid retrieval
- child candidate merge
- parent aggregation

예상 파일:
- `backend/app/services/retrieval_utils.py`
- `backend/app/services/library_search.py`
- `backend/tests/test_retrieval_utils.py`

### Lane 5. Rerank + Answerability Gate

책임:
- metadata-aware rerank
- answerability scoring
- generation 전 fallback 분기

예상 파일:
- `backend/app/services/reranker.py`
- `backend/app/services/chat.py`
- `backend/tests/test_reranker.py`
- `backend/tests/test_chat.py`

### Lane 6. QA And Benchmark Harness

책임:
- 대표 질문 세트 관리
- retrieval regression 지표
- 비교 리포트

예상 파일:
- `backend/tests/autorag/*`
- `backend/tests/test_autorag_eval.py`
- 새 representative QA fixtures

---

## Merge Safety Rules

- Lane 0 완료 전 나머지 lane은 공통 타입 수정 금지
- 같은 파일에 두 lane이 동시에 쓰지 않음
- 각 lane은 자기 수정 범위를 문서로 명시
- 취합 전 전체 regression과 representative QA를 반드시 다시 돌림
- 모델 캐시, feedback data, runtime 산출물은 커밋 금지

## Recommended Task Order

1. Lane 0: 공통 타입/계약 확정
2. Lane 1 + Lane 2 병렬
3. Lane 3 병렬
4. Lane 4
5. Lane 5
6. Lane 6 병렬 유지
7. Lane 0 취합 및 최종 검증

## Fast Finish Checklist

- [ ] 공통 타입 문서화
- [ ] parser/chunker 계약 잠금
- [ ] hybrid retrieval 초안 구현
- [ ] answerability gate 추가
- [ ] representative QA set 최소 10개 확보
- [ ] baseline 대비 citation 품질 비교
- [ ] 취합 브랜치에서 backend 테스트/실문답 QA 완료
