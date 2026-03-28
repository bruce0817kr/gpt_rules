# 규정/규칙 RAG 근본 개선 설계

## 1. 목표

특정 키워드나 개별 규정명을 하드코딩하지 않고, 규정/규칙/법령 문서 전반에서 더 일관되게 핵심 조문을 찾고 답변 품질을 높이는 검색 파이프라인을 만든다.

이번 설계의 핵심 목표는 아래와 같다.

- 문서 구조를 보존한 파싱과 청킹으로 부칙/별표/시행일 같은 약한 조각이 본문 조항보다 앞서지 않게 만든다.
- child-parent 청킹 구조로 검색 정밀도와 답변 맥락을 동시에 확보한다.
- dense 검색 하나에 의존하지 않고 hybrid retrieval, parent aggregation, answerability gate를 통해 규정형 질문 전반의 안정성을 올린다.
- 병렬 구현이 가능하도록 공통 타입과 모듈 경계를 먼저 고정한다.

## 2. 현재 병목

현재 파이프라인은 아래 특징 때문에 규정형 질문에서 품질 편차가 크다.

- 텍스트 chunk가 조문 구조를 충분히 반영하지 못한다.
- retrieval 후보가 부칙/별표/등급표 같은 약한 조각을 쉽게 상위에 올린다.
- reranker가 snippet만 보고 판단해 문서명과 조문 위치를 충분히 활용하지 못한다.
- 답변 전에 근거가 정말 질문에 답할 수 있는지 확인하는 gate가 없다.

이 문제는 특정 질의 하드코딩으로 덮기보다, 문서 표현과 retrieval 계층을 구조적으로 바꾸는 쪽이 맞다.

## 3. 목표 아키텍처

새 파이프라인은 아래 순서로 동작한다.

1. 구조화 파싱
2. parent chunk 생성
3. child chunk 생성
4. hybrid retrieval
5. parent aggregation
6. metadata-aware rerank
7. answerability gate
8. generation

## 4. 문서 구조 모델

### 4.1 구조 단위

규정/규칙/법령 문서를 아래 단위로 표현한다.

- document
- chapter
- section
- article
- paragraph
- item
- appendix
- addendum

여기서 retrieval과 generation의 핵심 단위는 `article`이다.

### 4.2 메타데이터

모든 parent/child chunk에 아래 메타데이터를 붙인다.

- `document_id`
- `document_title`
- `document_category`
- `source_type`
  - `article`, `appendix`, `addendum`, `table`, `metadata`
- `chapter_label`
- `section_label`
- `article_label`
- `paragraph_label`
- `item_label`
- `effective_date`
- `is_addendum`
- `is_appendix`
- `path_key`
  - 예: `제3장>제12조>제2항`
- `parent_id`
- `child_id`

### 4.3 설계 원칙

- 조문 본문과 부칙/별표는 같은 수준의 retrieval 대상이 아니다.
- 문서 구조를 잃지 않는 것이 chunk 길이 최적화보다 우선이다.
- 문서명과 조문 위치는 retrieval/rerank 입력에 항상 포함된다.

## 5. Child-Parent 청킹

### 5.1 Parent chunk

parent chunk는 기본적으로 `조문(article)` 단위로 잡는다.

규칙:

- 한 조문이 짧으면 조문 전체가 parent
- 한 조문이 길면 조문 내부 paragraph 묶음으로 parent 분할 허용
- 부칙과 별표는 본문 조문과 별도 parent 타입으로 생성
- parent는 answer context의 기본 단위다

### 5.2 Child chunk

child chunk는 parent 내부를 더 작은 의미 단위로 나눈다.

규칙:

- parent 내부 문장/문단 단위로 분할
- child 길이는 dense retrieval 정밀도를 높일 만큼만 작게 유지
- child는 반드시 parent를 참조한다
- child는 retrieval 후보, parent는 rerank/answer context 단위다

### 5.3 Parent-Child 관계

- 검색은 child 중심
- 재집계는 parent 중심
- citation은 parent를 우선으로 하되, pinpoint용 child 위치를 함께 가진다

## 6. Retrieval 파이프라인

### 6.1 Hybrid retrieval

1차 retrieval은 아래 두 축을 병행한다.

- dense retrieval
  - child chunk 임베딩 기반 의미 검색
- sparse retrieval
  - BM25 또는 동등한 lexical 검색
  - 문서명, 조문명, 핵심 명사, 숫자, 항목어에 민감하게 반응

이 둘을 reciprocal rank fusion 또는 가중 결합으로 합친다.

### 6.2 Candidate 확장

- top child candidates를 parent 기준으로 묶는다.
- 같은 parent에 속한 child가 여러 개 잡히면 그 parent의 점수를 올린다.
- 서로 다른 문서로 지나치게 분산되면 score를 조정해 문서 집중도를 반영한다.

### 6.3 Parent aggregation

parent 점수는 아래 정보를 합쳐 계산한다.

- 최고 child score
- 동일 parent child hit 개수
- 문서명 lexical match 점수
- 조문 구조 match 점수
- chunk type penalty
  - 부칙/별표/시행일 계열은 본문보다 불리하게

## 7. Rerank와 Answerability

### 7.1 Metadata-aware rerank

reranker 입력은 snippet만 쓰지 않는다.

입력 포맷:

- question
- document title
- path key
- source type
- parent summary text
- representative child text

이렇게 해야 본문 조항과 부칙/별표를 더 잘 구분할 수 있다.

### 7.2 Answerability gate

최종 generation 전에 아래를 검사한다.

- 상위 parent가 질문 의도에 직접 답하는가
- 문서명과 조문이 질문의 핵심 명사를 충족하는가
- 부칙/별표만으로 답을 구성하려는가
- 동일 parent에 근거가 충분히 모였는가

gate를 통과하지 못하면:

- 더 넓은 retrieval 재시도
- parent 재선정
- category 제한 재시도
- 그래도 실패하면 low-confidence fallback

## 8. 인덱스 스키마 변경

필수 payload 변경:

- 기존 `text`, `location`, `page_number` 외에 구조 메타데이터 추가
- child chunk payload와 parent lookup 키 추가
- source type 별 filter 지원

추가 저장물:

- `parent_records`
- `child_records`
- `parent_to_children` mapping
- 문서 구조 파싱 결과 캐시

## 9. 모듈 경계

### 9.1 Parser layer

책임:

- 원문에서 구조 추출
- article / appendix / addendum 구분
- path_key 생성

### 9.2 Chunking layer

책임:

- parent chunk 생성
- child chunk 생성
- parent-child 연결 보존

### 9.3 Index layer

책임:

- child 임베딩 저장
- payload 저장
- parent metadata 조회 지원

### 9.4 Retrieval layer

책임:

- dense + sparse retrieval
- candidate merge
- parent aggregation

### 9.5 Ranking layer

책임:

- metadata-aware rerank
- source type penalty
- answerability gate

### 9.6 Generation layer

책임:

- answer context 구성
- citation 출력 정렬
- fallback 판단

## 10. 병렬 구현을 위한 고정 계약

병렬 작업 전 아래 인터페이스를 먼저 고정한다.

- `StructuredSection`
- `ParentChunkRecord`
- `ChildChunkRecord`
- `AggregatedParentHit`
- `AnswerabilityResult`

또한 아래 함수 시그니처를 먼저 합의한다.

- `parse_structured_sections(file_path) -> list[StructuredSection]`
- `build_parent_chunks(sections) -> list[ParentChunkRecord]`
- `build_child_chunks(parents) -> list[ChildChunkRecord]`
- `search_children(question, categories, top_k) -> list[ChildHit]`
- `aggregate_parent_hits(question, child_hits) -> list[AggregatedParentHit]`
- `rerank_parent_hits(question, parent_hits, top_k) -> list[AggregatedParentHit]`
- `evaluate_answerability(question, parent_hits) -> AnswerabilityResult`

## 11. 병렬 작업 분해

### Task A. 구조 모델과 공통 타입

소유 범위:

- schema/type 정의
- 구조 메타데이터 계약

산출물:

- parser/chunker/retrieval이 함께 쓰는 공통 타입
- fixture 문서 예시

병렬성:

- 모든 작업의 선행 조건
- 가장 먼저 끝나야 함

### Task B. 구조화 파서

소유 범위:

- document parser
- article/appendix/addendum 분리

병렬성:

- Task A 이후 바로 가능
- Task C와 병렬 가능

### Task C. child-parent chunker

소유 범위:

- parent/child chunk 생성기
- 약한 chunk type 분리

병렬성:

- Task A 이후 가능
- Task B와 병렬 가능하되 parser 출력 계약 필요

### Task D. 인덱스/저장 스키마

소유 범위:

- vector store payload 변경
- parent/child 저장 구조

병렬성:

- Task A 이후 가능
- Task B/C와 부분 병렬 가능

### Task E. hybrid retrieval + parent aggregation

소유 범위:

- retrieval 계층
- candidate merge
- parent score 집계

병렬성:

- Task C/D 이후 가능

### Task F. rerank + answerability gate

소유 범위:

- metadata-aware rerank
- answerability 판단
- fallback 분기

병렬성:

- Task E와 강하게 연결
- 같은 작업자 또는 직렬 추천

### Task G. 회귀 테스트/품질 벤치

소유 범위:

- parser/chunker fixture
- retrieval regression
- representative QA set

병렬성:

- Task A 이후 가능
- 거의 전 구간과 병렬 가능
- 단, fixture 계약은 고정 필요

## 12. 취합 포인트

병렬 작업에서 가장 중요한 건 취합 규율이다.

취합 규칙:

- 공통 타입은 Task A 이후 잠근다.
- 각 태스크는 자기 write scope 밖 수정 금지.
- 병렬 작업자는 동일 파일 동시 수정 금지.
- merge 전에 integration owner가 아래를 확인한다.

integration owner 체크리스트:

- parser output이 chunker 계약과 일치하는가
- child payload가 vector store와 일치하는가
- parent aggregation 입력이 reranker 기대값과 일치하는가
- answerability gate가 citation 출력과 충돌하지 않는가
- representative QA set에서 baseline 대비 실제 개선이 있는가

## 13. 검증 전략

### 13.1 단위 테스트

- 구조 파싱 테스트
- parent/child chunk 생성 테스트
- weak chunk classification 테스트
- reranker input formatting 테스트
- answerability gate 테스트

### 13.2 회귀 QA 세트

분야별 대표 질문 세트 유지:

- 여비/출장비
- 취업규칙/징계
- 법인차량 관리 규칙
- 계약/입찰
- 시설/공사 관련 법령

각 질문마다 아래를 본다.

- top citation의 문서 적중 여부
- 부칙/별표 과다 노출 여부
- confidence
- answerability
- 사람이 보기 좋은가

### 13.3 지표

- citation precision@k
- parent hit accuracy
- weak chunk rate in top-k
- answerability pass rate
- low-confidence fallback rate

## 14. 위험과 대응

주요 위험:

- 구조 파싱 규칙이 문서 변형을 충분히 못 다룸
- parent를 너무 크게 잡아 다시 잡음 증가
- sparse 검색 도입 후 latency 상승
- 병렬 구현 중 타입 계약 드리프트

대응:

- fixture 문서 다양화
- parent/child 크기 실험
- retrieval stage별 시간 측정
- 통합 owner review를 merge 조건으로 강제

## 15. 추천 실행 순서

1. Task A
2. Task B + Task C 병렬
3. Task D 병렬
4. Task E
5. Task F
6. Task G 상시 병렬
7. integration branch에서 취합

## 16. 결론

핵심은 특정 질문을 맞추는 하드코딩이 아니라, 규정 문서를 `조문 중심 구조 데이터`로 다루는 것이다.

근본 개선 버전은 아래 조합으로 본다.

- 구조화 파싱
- child-parent 청킹
- hybrid retrieval
- parent aggregation
- metadata-aware rerank
- answerability gate
- representative QA set 기반 검증
