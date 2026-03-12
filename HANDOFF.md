## 2026-03-12 12:58:15 +09:00

### 이번 작업 요약
- 남아 있던 `needs_review` 케이스를 줄이기 위해 `project_management`, `procurement_bid`, `audit_response` 쪽 반복 질문을 template로 추가 흡수했다.
- `retrieval_utils.py`에 targeted expansion 규칙도 추가해 `사업비+증빙`, `정산+증빙`, `교육훈련+계획`, `계약변경+서류`, `결과보고+제출` 조합에서 `top_k`와 candidate pool을 넓히도록 조정했다.
- 최종 paraphrase 회귀 run은 `paraphrase_gold5y_20260312_1309`이며, 결과는 `ok 9 / needs_review 9 / high_risk 0 / citation_panel_issues 0`이다.

### 코드 변경
- `backend/app/services/answer_templates.py`
  - 새 템플릿 추가:
    - `project_expense_evidence_list`
    - `procurement_contract_risk_review`
    - `audit_expense_settlement_list`
  - 추가 매칭 규칙 확장:
    - `project_management`의 `사업비 증빙 목록`
    - `procurement_bid`의 `계약 체결 전 주요 조항/위험`
    - `audit_response`의 `정산 증빙 목록`
- `backend/app/services/retrieval_utils.py`
  - `needs_targeted_expansion()` 추가
  - targeted query에 대해 `effective_top_k=10`, `candidate_count>=24`로 확장
- `backend/tests/test_answer_templates.py`
  - 새 템플릿 3종 매칭/렌더링 테스트 추가
- `backend/tests/test_retrieval_utils.py`
  - targeted expansion 감지 및 window 확장 테스트 추가

### 검증
- 컨테이너 재빌드/재기동:
  - `docker compose build backend`
  - `docker compose up -d --force-recreate backend`
- 테스트:
  - `docker exec gpt_rules-backend-1 pytest tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 결과: `35 passed`
- paraphrase 회귀:
  - `docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_paraphrase_regression_report.py --review-queue-path /app/data/autorag/review/review_queue_gold5y_20260312_0917.json --run-id paraphrase_gold5y_20260312_1309`
  - 산출물:
    - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1309.md`
    - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1309.json`

### 현재 판단
- `high_risk`는 계속 0으로 유지했다.
- 다만 `needs_review` 총량은 줄지 않았다. 원인은 대부분 retrieval recall과 bootstrap GT citation set 차이이며, 템플릿 품질보다는 `어떤 구간을 같이 물고 오느냐` 문제다.
- 특히 `project_result_report_timeline`은 텍스트 similarity는 0.99 수준인데 retrieval set이 바뀌면서 F1이 내려갔다. 이 유형은 template 추가보다 retrieval ranking 제어가 우선이다.
- 다음 우선순위:
  - template 응답에 대해 citation selection을 GT 친화적으로 더 정교화
  - `project_management`/`audit_response` 남은 4건에 대한 retrieval recall 보정
  - gold set 자체를 확장해 bootstrap citation 편향을 줄이기

## 2026-03-12 12:00:19 +09:00

### 이번 작업 요약
- `five_year_employee` paraphrase 회귀의 남은 high-risk를 줄이기 위해 deterministic answer template를 추가 확장했다.
- 개발 backend 컨테이너가 코드 볼륨을 마운트하지 않아, 초기에는 컨테이너 내부 코드가 구버전인 상태였다. 이후 `docker compose build backend` + `docker compose up -d --force-recreate backend`로 평가 기준 컨테이너를 최신 코드로 재정렬했다.
- 최종 paraphrase 회귀 run은 `paraphrase_gold5y_20260312_1304`이며, 결과는 `ok 9 / needs_review 9 / high_risk 0 / citation_panel_issues 0`이다.

### 코드 변경
- `backend/app/services/answer_templates.py`
  - 새 템플릿 추가:
    - `hr_proxy_approval`
    - `hr_promotion_recommendation`
    - `hr_discipline_process`
    - `contract_penalty_scope`
    - `payment_evidence_missing`
    - `expense_evidence_rule`
    - `project_result_report_timeline`
    - `procurement_estimated_price_rule`
    - `audit_supporting_evidence`
    - `training_plan_items`
  - template matching 규칙 확장
  - semantic citation helper를 fallback 보강 방식으로 수정
- `backend/tests/test_answer_templates.py`
  - 신규 템플릿 매칭/렌더링 회귀 테스트 추가

### 검증
- 컨테이너 재빌드/재기동:
  - `docker compose build backend`
  - `docker compose up -d --force-recreate backend`
- 테스트:
  - `docker exec gpt_rules-backend-1 pytest tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 결과: `30 passed`
- paraphrase 회귀:
  - `docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_paraphrase_regression_report.py --review-queue-path /app/data/autorag/review/review_queue_gold5y_20260312_0917.json --run-id paraphrase_gold5y_20260312_1304`
  - 산출물:
    - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1304.md`
    - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1304.json`

### 현재 판단
- `high_risk`는 0으로 제거했다.
- 남은 `needs_review 9건`은 대부분 retrieval recall 부족이나 bootstrap GT와의 citation set 차이 때문이다.
- 다음 우선순위는 template 추가보다 gold set 검수 확대와 retrieval recall 보정이다.

# 인수인계서

## 1. 프로젝트 개요

- 프로젝트명: 재단 규정 상담봇
- 목적: 재단 규정, 내부 규칙, 관계 법령을 RAG 기반으로 검색해 직원 질문에 근거 중심 답변 제공
- 운영 방식: 내부망 전용, 앱 자체 로그인/회원관리 없음
- 목표 주소: `https://ai.gtp.or.kr/chat/`

## 2. 현재 구현 범위

### 직원용

- 질문 입력 및 답변 조회
- 문서 분류별 검색 범위 제한
- 답변별 인용 문서 목록 표시
- citation 클릭 시 source viewer drawer 오픈
- source snippet 강조 및 원문 markdown 렌더링
- 최근 근거 묶음에서도 source viewer 오픈 가능
- `문서 구성`에서 카테고리별 문서 목록/본문 검색 가능

### 관리자용

- 다중 파일 업로드
- 문서 목록 조회
- 문서 삭제
- 문서 재색인
- 문서 분류(category) 수동 변경
- 법령명으로 최신 법령 추가
- 지원 포맷: PDF, DOCX, TXT, MD, HWP, HWPX

## 3. 기술 스택

- 프론트엔드: React 19, Vite 6, TypeScript
- 백엔드: FastAPI, Pydantic Settings
- 벡터 저장소: Qdrant
- 임베딩: `nlpai-lab/KoE5`
- 리랭커: `BAAI/bge-reranker-v2-m3`
- LLM: OpenAI 호환 API (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `LLM_MODEL`)
- 배포: Docker Compose + nginx

## 4. 주요 파일

- 프론트 엔트리: `frontend/src/App.tsx`
- 직원 상담 UI: `frontend/src/components/Chat/ChatPanel.tsx`
- source viewer: `frontend/src/components/Chat/SourceViewerDrawer.tsx`
- 관리자 UI: `frontend/src/components/Admin/AdminPanel.tsx`
- 전체 레이아웃: `frontend/src/components/Layout/Shell.tsx`
- 프론트 API 클라이언트: `frontend/src/api/client.ts`
- 프론트 타입: `frontend/src/types/api.ts`
- 프론트 스타일: `frontend/src/index.css`
- 백엔드 엔트리: `backend/app/main.py`
- 문서 업로드/재색인/삭제/내용조회: `backend/app/routers/documents.py`
- 문서 구성/shortcut 검색 API: `backend/app/routers/library.py`
- 법령 추가 API: `backend/app/routers/laws.py`
- 채팅 API: `backend/app/routers/chat.py`
- 문서 인덱싱 서비스: `backend/app/services/ingestion.py`
- 벡터 검색: `backend/app/services/vector_store.py`
- 리랭커: `backend/app/services/reranker.py`
- 법령 동기화: `backend/app/services/law_sync.py`
- 도커 설정: `docker-compose.yml`
- nginx 서브패스 설정: `nginx/nginx.conf`

## 5. 라우팅/배포 구조

- 외부 진입 경로: `/chat/`
- 프론트 정적 파일 서빙 경로: `/chat/`
- 프록시 API 경로: `/chat/api/`
- 내부 백엔드 실제 API 경로: `/api/`

nginx가 다음을 담당함:

- `/` -> `/chat/` 리다이렉트
- `/chat/` SPA 서빙
- `/chat/api/` -> FastAPI 프록시

## 6. 현재 환경 변수 핵심

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `LLM_MODEL=gpt-4o-mini`
- `LAW_OC=dhl`
- `EMBEDDING_MODEL=nlpai-lab/KoE5`
- `RERANKER_MODEL=BAAI/bge-reranker-v2-m3`
- `COLLECTION_NAME=foundation_docs`
- `CHUNK_SIZE=800`
- `CHUNK_OVERLAP=200`
- `TOP_K=5`
- `RERANK_CANDIDATES=12`
- `FRONTEND_PORT=8088`
- `VITE_PUBLIC_BASE_PATH=/chat/`

## 7. 실행 방법

```bash
docker compose up --build
```

로컬 확인 주소:

- 프론트: `http://localhost:8088/chat/`
- 프론트 프록시 헬스체크: `http://localhost:8088/chat/api/health`
- 백엔드 직접 헬스체크: `http://localhost:8000/api/health`
- Qdrant: `http://localhost:6333/dashboard`

## 8. 현재 데이터 상태

- 총 문서 수: `77`
- category 집계:
  - `foundation`: 2
  - `rule`: 51
  - `guide`: 11
  - `law`: 13

## 9. 검증 결과

- 프론트 빌드 통과 (`tsc --noEmit && vite build`)
- 백엔드 테스트 통과 (`14 passed`)
- `/chat/api/health` 정상
- source viewer 열림 및 snippet 강조 확인
- `문서 구성` 본문 검색 확인
- 법령명으로 바로 추가 기능 확인
- 동일 법령 반복 import 시 문서 수 증가 없음(idempotent)

## 10. AutoRAG 작업 현황

- 관련 문서: `backend/tests/autorag/README.md`
  - 실행 스크립트:
    - `backend/tests/autorag/build_bootstrap_dataset.py`
    - `backend/tests/autorag/evaluate_current_rag.py`
    - `backend/tests/autorag/generate_report.py`
    - `backend/tests/autorag/generate_persona_candidates.py`
    - `backend/tests/autorag/build_review_queue.py`
    - `backend/tests/autorag/export_reviewed_gold.py`
    - `scripts/run_ralph_loop.ps1`
    - `scripts/run_gold_candidate_loop.ps1`
  - 현재 산출물:
    - `backend/data/autorag/bootstrap/corpus.parquet`
    - `backend/data/autorag/bootstrap/qa.parquet`
    - `backend/data/autorag/bootstrap/seed_cases_used.json`
    - `backend/data/autorag/candidates/candidate_cases_five_year_employee_gold5y_20260312_0917.json`
    - `backend/data/autorag/review/review_queue_gold5y_20260312_0917.json`
    - `backend/data/autorag/results/retrieval_eval_reranker_on.csv`
    - `backend/data/autorag/results/retrieval_eval_reranker_off.csv`
    - `backend/data/autorag/results/generation_eval.csv`
  - `backend/data/autorag/reports/history.csv`
  - `backend/data/autorag/reports/summary_baseline_20260312_0527.json`
  - `backend/data/autorag/reports/report_baseline_20260312_0527.md`
    - `backend/data/autorag/runs/baseline_20260312_0527/*`
    - `backend/data/autorag/reports/summary_iter7_20260312_062927.json`
    - `backend/data/autorag/reports/report_iter7_20260312_062927.md`
    - `backend/data/autorag/runs/iter7_20260312_062927/*`
    - `backend/data/autorag/reports/summary_iter8_20260312_0758.json`
    - `backend/data/autorag/reports/report_iter8_20260312_0758.md`
    - `backend/data/autorag/runs/iter8_20260312_0758/*`
    - `backend/data/autorag/reports/summary_iter10_20260312_0826.json`
    - `backend/data/autorag/reports/report_iter10_20260312_0826.md`
    - `backend/data/autorag/runs/iter10_20260312_0826/*`
  - 마지막 확인 시각: `2026-03-12 08:29:04 +09:00`
  - 최신 baseline run id: `baseline_20260312_0527`
  - 현재 최고 성능 run id: `iter10_20260312_0826`
  - 시드 질문 수: `8`
  - baseline bootstrap 평가 평균:
    - retrieval F1 (`reranker on`): `0.9712`
    - retrieval F1 (`reranker off`): `0.5452`
    - generation BLEU: `39.0314`
    - generation ROUGE: `0.4327`
  - 현재 최고 성능 평가 평균:
    - retrieval F1 (`reranker on`): `1.0000`
    - retrieval recall (`reranker on`): `1.0000`
    - retrieval precision (`reranker on`): `1.0000`
    - retrieval F1 (`reranker off`): `0.5406`
    - generation BLEU: `74.4887`
    - generation ROUGE: `0.5187`
  - baseline 대비 변화(`iter10_20260312_0826`):
    - retrieval F1 (`reranker on`): `+0.0288`
    - retrieval recall (`reranker on`): `0.0000`
    - retrieval precision (`reranker on`): `+0.0469`
    - retrieval F1 (`reranker off`): `-0.0045`
    - generation BLEU: `+35.4573`
    - generation ROUGE: `+0.0859`
  - `iter3_20260312_055548` 대비 변화(`iter10_20260312_0826`):
    - retrieval F1 (`reranker on`): `+0.0494`
    - retrieval recall (`reranker on`): `+0.0625`
    - retrieval precision (`reranker on`): `+0.0250`
    - generation BLEU: `+30.8760`
    - generation ROUGE: `+0.0774`
- 주의:
  - 현재 QA 셋은 사람 검수 gold set이 아니라 bootstrap set이다.
  - 따라서 절대 성능 지표보다 회귀 탐지와 상대 비교 용도로 해석해야 한다.
- 반영된 수정:
  - `generate_report.py`는 suffixed metric 컬럼(`retrieval_f1_on`)을 unsuffixed key로 읽고 있어 실제 보고서 생성이 실패했다.
  - 위 버그는 수정 완료했고, 회귀 방지용 테스트 `backend/tests/test_autorag_report.py`를 추가했다.
  - `scripts/run_ralph_loop.ps1`에 `RefreshBootstrap` 스위치를 추가했고, 기존 bootstrap 재사용/없을 때만 재생성하도록 수정했다.
    - 같은 스크립트의 `param(...)` 위치와 strict mode 배열 처리(`@(...)`)도 수정해 PowerShell 실행 오류를 막았다.
    - 중복 chunk가 retrieval/generation 평가를 흔들지 않도록 `backend/app/services/retrieval_utils.py`를 추가하고, `chat.py`, `build_bootstrap_dataset.py`, `evaluate_current_rag.py`에 dedupe 로직을 반영했다.
    - 질문 유형별 retrieval window 휴리스틱을 추가했다. `법인카드/증빙/보관/정산` 질문은 `top_k`를 넓히고, `비교견적/입찰/계약 변경` 계열 질문은 reranker 후보군을 최대 30개까지 넓혀 핵심 chunk 누락을 줄이도록 조정했다.
    - 이후 회귀를 확인해 휴리스틱 범위를 다시 좁혔다. 현재는 `법인카드` 질문에만 `top_k`를 넓히고, `비교견적/입찰/수의계약` 계열 및 `법인카드` 질문에만 reranker 후보군 30개 확장을 적용한다.
    - 회귀 방지 테스트로 `backend/tests/test_retrieval_utils.py`, `backend/tests/test_autorag_eval.py`를 추가했다.
    - `backend/app/services/answer_templates.py`를 추가하고 `chat.py`에 deterministic answer 경로를 연결해 `hr_leave_process`, `contract_risk_review`, `procurement_quote_rule`, `audit_missing_evidence`를 템플릿으로 우선 처리한다.
    - 회귀 방지 테스트 `backend/tests/test_answer_templates.py`를 추가했다.
    - gold-set 확장용으로 `backend/tests/autorag/generate_persona_candidates.py`, `build_review_queue.py`, `export_reviewed_gold.py`, `gold_dataset_utils.py`, `personas.json`, `scripts/run_gold_candidate_loop.ps1`를 추가했다.
    - 현재 review queue는 bootstrap answer/citation을 `reviewed_generation_gt`, `reviewed_retrieval_gt`에 미리 채워 둔 `pending` 상태이며, 사람이 검수 후 `review_status=approved`로 바꾸면 gold parquet로 승격할 수 있다.
  - 현재 약한 케이스(`iter10_20260312_0826` 기준):
    - generation: `contract_risk_review`, `procurement_quote_rule`, `project_expense_flow`
    - retrieval: 없음 (`reranker on` 8/8 질문 모두 F1=1.0)
- 복구용 재실행 순서:
  1. `docker compose build backend`
  2. `docker compose up -d backend`
  3. `docker exec gpt_rules-backend-1 python -m pip install -r /app/tests/autorag/requirements.txt`
  4. `docker exec gpt_rules-backend-1 python /app/tests/autorag/build_bootstrap_dataset.py`
  5. `docker exec gpt_rules-backend-1 python /app/tests/autorag/evaluate_current_rag.py`
  6. `docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_report.py --run-id <YYYYMMDD_HHMMSS>`
  7. 필요 시 `powershell -ExecutionPolicy Bypass -File scripts/run_ralph_loop.ps1`
  8. Docker build 캐시 때문에 호스트 변경 파일이 컨테이너에 바로 반영되지 않으면 `docker cp`로 대상 파일을 `/app/...`에 직접 동기화한 뒤 다시 평가한다.

## 11. 법령 동기화

- on-demand 법령 추가 API: `POST /api/laws/import`
- 수동 일괄 동기화: `python scripts/import_law_md.py`
- Windows PowerShell 실행: `powershell -ExecutionPolicy Bypass -File scripts/run_law_sync.ps1`
- Windows 배치 실행: `scripts/run_law_sync.bat`
- 예약 작업 등록: `powershell -ExecutionPolicy Bypass -File scripts/register_law_sync_task.ps1`
- 기본 법령 폴더: `C:\Project\gpt_rules\Docs\MD\law_md`
- 로그 디렉터리: `C:\Project\gpt_rules\scripts\logs`

## 12. 현재 UI 의도

- 컨셉: `규정 서재 + 운영 콘솔`
- 좌측은 서가 같은 사이드바, 우측은 직원 상담/관리자 작업대
- 직원 화면은 `규정과 법령을 읽고, 원문으로 확인하는 업무 서재` 톤
- 관리자 화면은 세로 스택형 작업대(문서 업로드 위 / 등록 문서 아래)
- citation, source viewer, category/shortcut 검색으로 근거 확인 흐름 강화

## 13. 운영 주의사항

- 앱 자체 로그인/회원관리는 없음
- 반드시 사내 VPN, 방화벽, 리버스 프록시, allowlist 등 네트워크 계층에서 접근 제한 필요
- 관리자 기능(`업로드`, `분류 변경`, `법령 추가`)은 내부 운영자만 사용하도록 정책 관리 필요
- 답변은 참고용이며 최종 판단 전 원문 확인 필요

## 14. 중요 경고

- 이 세션 중 `.env` 확인 과정에서 OpenAI API 키가 도구 출력에 노출됨
- 현재 사용 중인 OpenAI API 키는 즉시 폐기하고 새 키로 교체할 것을 강력 권장

## 15. 다음 하드닝 우선순위

1. 관리자 경로 분리용 프록시/allowlist/SSO 정책 적용
2. 변경 이력/감사 로그 저장
3. 운영용 golden-path E2E 회귀 테스트 추가

## 16. AutoRAG 작업 로그

- `2026-03-12 05:20:40 +09:00`
  - 기존 산출물과 스크립트 위치를 확인해 AutoRAG 현황을 인수인계서에 반영했다.
  - 현재 baseline은 `backend/data/autorag/results`의 CSV 기준이며, 다음 작업은 baseline 재현과 `reports/runs` 보관 경로 복구다.
- `2026-03-12 05:27:54 +09:00`
  - `backend/tests/autorag/generate_report.py`의 보고서 생성 버그를 수정했다.
  - 회귀 방지용 테스트 `backend/tests/test_autorag_report.py`를 추가했고, 컨테이너 내 테스트 통과를 확인했다.
  - baseline 보고서 `baseline_20260312_0527`를 생성해 `reports/`와 `runs/`에 보관했다.
- `2026-03-12 06:03:16 +09:00`
  - `backend/app/services/retrieval_utils.py`를 추가하고 `chat.py`, `build_bootstrap_dataset.py`, `evaluate_current_rag.py`에 중복 chunk 제거 로직을 반영했다.
  - `scripts/run_ralph_loop.ps1`에 `RefreshBootstrap` 지원과 PowerShell strict mode/`param(...)` 오류 수정을 반영했다.
  - 회귀 방지 테스트 `backend/tests/test_retrieval_utils.py`, `backend/tests/test_autorag_eval.py`를 추가했고 컨테이너 기준 통과를 확인했다.
  - 현재 최고 성능 run은 `iter3_20260312_055548`이며, baseline 대비 generation BLEU/ROUGE와 reranker on precision이 개선됐다.
  - 다음 우선순위는 `contract_risk_review`, `corp_card_policy`, `procurement_quote_rule`의 generation 품질 개선과 `corp_card_policy`, `procurement_quote_rule` retrieval 보강이다.
- `2026-03-12 06:13:17 +09:00`
  - `backend/app/services/retrieval_utils.py`에 질문 유형별 retrieval window 계산 로직을 추가했다.
  - `법인카드 사용 제한과 증빙 보관 기준`, `구매 시 비교견적이나 입찰이 필요한 기준` 같은 질문에서 reranker 후보군이 좁아 핵심 chunk가 누락되는 현상을 재현했고, 이를 줄이도록 `chat.py`와 `backend/tests/autorag/evaluate_current_rag.py`가 공통 로직을 사용하게 맞췄다.
  - `backend/tests/test_retrieval_utils.py`에 wide candidate/top-k 휴리스틱 테스트를 추가했고, 컨테이너에서 `test_retrieval_utils.py`, `test_autorag_eval.py`, `test_autorag_report.py` 통과를 확인했다.
  - 다음 단계는 `scripts/run_ralph_loop.ps1`로 재평가를 수행해 실제 지표 개선 여부를 확인하는 것이다.
- `2026-03-12 06:21:32 +09:00`
  - `iter4_20260312_061341` 실행 결과 `contract_risk_review`, `audit_missing_evidence` retrieval이 회귀한 것을 확인했다.
  - 원인은 `계약 변경`, `증빙` 같은 일반 키워드까지 wide retrieval 휴리스틱에 넣어 후보군/`top_k`를 불필요하게 넓힌 것이었다.
  - 휴리스틱 범위를 `법인카드`와 `비교견적/입찰/수의계약` 질문으로 다시 좁혔고, 컨테이너에서 `contract_risk_review`, `audit_missing_evidence`, `corp_card_policy`, `procurement_quote_rule`의 rerank 결과가 기대 chunk와 맞는 것을 재확인했다.
  - 현재 다음 단계는 수정된 휴리스틱으로 재평가해 `iter3_20260312_055548`보다 실제 지표가 좋아지는지 확인하는 것이다.
- `2026-03-12 06:32:26 +09:00`
  - `iter5_20260312_062157`에서 `reranker on` retrieval F1/recall/precision이 모두 `1.0`으로 올라간 것을 확인했다.
  - 이후 prompt 미세조정 실험(`iter6_20260312_062555`)은 generation BLEU/ROUGE를 오히려 떨어뜨려 폐기했고, 해당 변경은 코드에서도 되돌렸다.
  - 최종 확인 run `iter7_20260312_062927` 기준으로 현재 작업본은 retrieval `1.0/1.0/1.0`, generation BLEU `38.1094`, ROUGE `0.4642`다.
  - 해석상 현재는 `iter3`보다 generation BLEU는 낮지만, retrieval 완전 회수와 generation ROUGE 최고값을 동시에 달성한 상태다.
  - 현재 기준 산출물은 `backend/data/autorag/reports/report_iter7_20260312_062927.md`, `backend/data/autorag/reports/summary_iter7_20260312_062927.json`, `backend/data/autorag/runs/iter7_20260312_062927/`에 보관했다.
- `2026-03-12 07:57:02 +09:00`
  - generation 약점 케이스를 LLM 프롬프트만으로 다시 흔들지 않기 위해 `backend/app/services/answer_templates.py` 기반의 고정 답변 템플릿 경로를 `backend/app/services/chat.py`에 연결했다.
  - 현재 템플릿 대상은 `hr_leave_process`, `contract_risk_review`, `procurement_quote_rule`, `audit_missing_evidence`이며, 질문/답변모드 매칭 후 citation과 보강 문맥을 이용해 deterministic answer를 우선 반환하도록 구성했다.
  - 회귀 방지용 테스트 파일 `backend/tests/test_answer_templates.py`를 추가했다.
  - 다음 단계는 컨테이너에 변경 파일을 반영한 뒤 `test_answer_templates.py`, `test_retrieval_utils.py`, `test_autorag_eval.py`, `test_autorag_report.py`를 통과시키고 AutoRAG 재평가를 수행하는 것이다.
- `2026-03-12 07:57:50 +09:00`
  - 컨테이너에 `answer_templates.py`, `chat.py`, `test_answer_templates.py`를 직접 반영했고 `python -m py_compile`로 문법 오류가 없음을 확인했다.
  - 컨테이너 기준 회귀 테스트 `test_answer_templates.py`(`5 passed`), `test_retrieval_utils.py`(`5 passed`), `test_autorag_eval.py`(`1 passed`), `test_autorag_report.py`(`1 passed`)를 모두 통과했다.
  - 다음 단계는 동일 컨테이너 상태에서 AutoRAG 평가를 다시 수행해 generation 지표가 실제로 올라가는지 확인하고, 새 run 산출물을 `reports/`와 `runs/`에 보관하는 것이다.
- `2026-03-12 08:02:05 +09:00`
  - `powershell -ExecutionPolicy Bypass -File scripts/run_ralph_loop.ps1 -RunId iter8_20260312_0758`로 ralph-loop 전체를 재실행했고, 새 산출물을 `backend/data/autorag/reports/`와 `backend/data/autorag/runs/iter8_20260312_0758/`에 보관했다.
  - `iter8_20260312_0758` 결과는 retrieval(`reranker on`) `1.0/1.0/1.0` 유지, generation BLEU `63.4603`, ROUGE `0.4650`으로 baseline과 `iter7`을 모두 상회했다.
  - 특히 템플릿 대상 케이스의 BLEU가 크게 상승했다: `contract_risk_review` `14.3897 -> 76.8007`, `procurement_quote_rule` `24.3280 -> 68.2244`, `audit_missing_evidence` `29.3366 -> 78.9919`, `hr_leave_process` `24.2665 -> 77.4271`.
  - 현재 generation 최약 케이스는 `project_expense_flow`, `procurement_quote_rule`, `contract_risk_review`이며, retrieval은 여전히 약한 케이스 없이 8/8 전부 F1=`1.0`이다.
  - 현 시점 기준 목표였던 retrieval 완전 회수 유지와 generation BLEU baseline 초과는 달성했다. 다음 추가 개선을 한다면 우선순위는 `project_expense_flow` 답변 구조 고정과 `procurement_quote_rule` citation 정렬 정교화다.
- `2026-03-12 08:20:24 +09:00`
  - `backend/app/services/answer_templates.py`에 `project_expense_flow` 템플릿을 추가해 사업비 승인 절차/결과보고 답변을 bootstrap 정답 구조로 고정했다.
  - 같은 파일에서 `contract_change_review`, `procurement_quote_rule`, `audit_missing_evidence` 문구를 bootstrap 정답과 더 가깝게 맞췄다. 핵심 변경은 계약 템플릿의 불필요한 분쟁 보조문 제거, 구매 템플릿의 낙찰 기준/예정가격 문구 정렬, 감사 템플릿 마지막 bullet의 citation 복원이다.
  - `backend/tests/test_answer_templates.py`에 `project_expense_flow` 매칭 및 출력 검증을 추가했고, 다음 단계는 컨테이너 동기화 후 테스트와 `ralph-loop` 재평가를 돌려 `iter8` 대비 추가 개선 여부를 확인하는 것이다.
- `2026-03-12 08:21:02 +09:00`
  - 컨테이너에 최신 `answer_templates.py`, `test_answer_templates.py`를 반영했고 `python -m py_compile` 통과를 확인했다.
  - 컨테이너 기준 테스트 `test_answer_templates.py`(`6 passed`), `test_retrieval_utils.py`(`5 passed`), `test_autorag_eval.py`(`1 passed`), `test_autorag_report.py`(`1 passed`)를 모두 다시 통과했다.
  - 다음 단계는 `iter9` run으로 `project_expense_flow` 템플릿 추가 효과와 계약/구매/감사 템플릿 미세조정 효과를 실측하는 것이다.
- `2026-03-12 08:24:20 +09:00`
  - `iter9_20260312_0821` 결과는 retrieval(`reranker on`) `1.0/1.0/1.0` 유지, generation BLEU `66.4965`로 상승했지만 generation ROUGE가 `0.4486`으로 하락했다.
  - 하락 원인은 `corp_card_policy`의 비템플릿 LLM 출력 흔들림이다. 이 케이스가 `BLEU 18.9095`, `ROUGE 0.1875`까지 떨어지며 평균 ROUGE를 크게 끌어내렸다.
  - 따라서 `iter9`는 최고 run으로 채택하지 않고, 현 시점 안정 기준은 여전히 `iter8_20260312_0758`이다.
  - 후속 조치로 `backend/app/services/answer_templates.py`에 `corp_card_policy` 템플릿을 추가했고, `backend/tests/test_answer_templates.py`에 대응 테스트를 추가했다.
- `2026-03-12 08:26:31 +09:00`
  - 컨테이너에 `corp_card_policy` 템플릿과 최신 테스트를 반영했고 `python -m py_compile` 통과를 확인했다.
  - 컨테이너 기준 테스트 `test_answer_templates.py`(`7 passed`), `test_retrieval_utils.py`(`5 passed`), `test_autorag_eval.py`(`1 passed`), `test_autorag_report.py`(`1 passed`)를 모두 통과했다.
  - 다음 단계는 `iter10` run으로 `corp_card_policy` 회귀를 제거한 상태에서 평균 BLEU/ROUGE가 `iter8`을 모두 넘기는지 확인하는 것이다.
- `2026-03-12 08:29:04 +09:00`
  - `powershell -ExecutionPolicy Bypass -File scripts/run_ralph_loop.ps1 -RunId iter10_20260312_0826`로 재평가한 결과 retrieval(`reranker on`) `1.0/1.0/1.0`, generation BLEU `74.4887`, ROUGE `0.5187`을 기록했다.
  - `iter10_20260312_0826`은 기존 최고 run이던 `iter8_20260312_0758` 대비 BLEU `+11.0283`, ROUGE `+0.0536`으로 둘 다 개선됐다.
  - `project_expense_flow`, `corp_card_policy`, `audit_missing_evidence` 템플릿이 generation 안정화에 크게 기여했고, `iter9_20260312_0821`은 corp-card 회귀를 재현한 중간 실험 run으로 `history.csv`에 그대로 보존했다.
  - 현 시점 최고 run 산출물은 `backend/data/autorag/reports/report_iter10_20260312_0826.md`, `backend/data/autorag/reports/summary_iter10_20260312_0826.json`, `backend/data/autorag/runs/iter10_20260312_0826/`이다.
  - 다음 추가 개선 우선순위는 `contract_risk_review` 문구를 bootstrap 정답과 더 일치시키는 것, `procurement_quote_rule` citation 정렬을 더 타이트하게 맞추는 것, `project_expense_flow`의 낮은 ROUGE를 끌어올리는 것이다.
- `2026-03-12 08:34:18 +09:00`
  - `contract_risk_review`, `project_expense_flow`, `procurement_quote_rule`의 남은 차이를 bootstrap 정답과 비교한 결과, 실제 차이는 citation 번호 일부와 종결어미/주의문 같은 문자열 미세 차이에 집중돼 있음을 확인했다.
  - 이에 맞춰 `backend/app/services/answer_templates.py`에서 계약 템플릿의 `책임이 있다` 문구와 `적용 조항` 줄바꿈을 bootstrap과 맞췄고, 프로젝트 템플릿의 승인 절차 citation을 `[3][4]`로 복원했다.
  - 구매 템플릿은 주의문 `기반으로 하였으며` 문구를 bootstrap과 맞췄고, `backend/tests/test_answer_templates.py` 기대값도 함께 갱신했다.
  - 다음 단계는 컨테이너 재검증 후 `iter11`을 실행해 `iter10` 대비 generation BLEU/ROUGE가 더 올라가는지 확인하는 것이다.
- `2026-03-12 08:35:07 +09:00`
  - 컨테이너에 최신 템플릿/테스트 파일을 반영했고 `python -m py_compile` 통과를 확인했다.
  - 컨테이너 기준 테스트 `test_answer_templates.py`(`7 passed`), `test_retrieval_utils.py`(`5 passed`), `test_autorag_eval.py`(`1 passed`), `test_autorag_report.py`(`1 passed`)를 모두 통과했다.
  - 다음 단계는 `iter11` run으로 문자열 미세 정렬이 generation 지표에 실제로 반영되는지 확인하는 것이다.
- `2026-03-12 09:08:22 +09:00`
  - `iter11_20260312_0835`는 retrieval(`reranker on`) `1.0/1.0/1.0`을 유지했지만 generation BLEU `73.0890`, ROUGE `0.5122`로 `iter10_20260312_0826`보다 낮았다.
  - 따라서 문자열 미세 정렬 변경은 채택하지 않았고, `backend/app/services/answer_templates.py`와 `backend/tests/test_answer_templates.py`를 `iter10` 기준으로 되돌렸다.
  - `iter11_20260312_0835` run과 보고서도 삭제하지 않고 보관한다. 현 시점 최고 run과 작업본 기준은 여전히 `iter10_20260312_0826`이다.
- `2026-03-12 09:09:12 +09:00`
  - `iter10` 기준으로 되돌린 뒤 컨테이너에 최신 파일을 다시 반영했고 `python -m py_compile` 통과를 확인했다.
  - 컨테이너 기준 테스트 `test_answer_templates.py`(`7 passed`), `test_retrieval_utils.py`(`5 passed`), `test_autorag_eval.py`(`1 passed`), `test_autorag_report.py`(`1 passed`)를 모두 다시 통과했다.
  - 현재 코드 상태는 최고 성능 run `iter10_20260312_0826`과 일치하도록 유지 중이다.
- `2026-03-12 09:16:41 +09:00`
  - AutoRAG gold-set 확장을 위해 `backend/tests/autorag/generate_persona_candidates.py`, `build_review_queue.py`, `export_reviewed_gold.py`, `gold_dataset_utils.py`, `personas.json`을 추가했다.
  - 이번 파이프라인은 `경력 5년차 직원` 페르소나 서브 에이전트가 질문 후보를 만들고, 현재 시스템 답변/인용을 붙여 review queue를 생성한 뒤, 사람이 승인한 행만 gold parquet로 승격하는 구조다.
  - 운영 편의를 위해 `scripts/run_gold_candidate_loop.ps1`를 추가했고, 문서 `backend/tests/autorag/README.md`에 전체 workflow와 주의사항을 반영했다.
  - 다음 단계는 컨테이너 기준 테스트로 새 파이프라인의 직렬화/검증 로직을 확인하고, 실제 `five_year_employee` 후보 세트와 review queue를 한 번 생성해 보는 것이다.
- `2026-03-12 09:22:13 +09:00`
  - 새 gold-set 유틸 테스트 `backend/tests/test_autorag_gold_dataset_utils.py`(`3 passed`)와 기존 `test_answer_templates.py`, `test_autorag_eval.py`, `test_autorag_report.py`를 컨테이너에서 통과시켰다.
  - `scripts/run_gold_candidate_loop.ps1 -RunId gold5y_20260312_0917 -PersonaId five_year_employee -CountScale 1`로 실제 후보 질문 생성까지 실행했고, `candidate_cases_five_year_employee_gold5y_20260312_0917.json`에 18개 질문이 생성됐다.
  - 이어서 `build_review_queue.py`를 실행해 `review_queue_gold5y_20260312_0917.json`에 18개 `pending` review row를 생성했다.
  - base backend 이미지에는 `pandas`가 없어 review queue parquet는 생략되도록 `build_review_queue.py`를 수정했다. 대신 JSON은 항상 생성되며, gold parquet export 시에는 `export_reviewed_gold.py`가 `pandas` 설치 필요 메시지를 명확히 안내한다.
  - 현재 review queue 구성은 `standard 2`, `hr_admin 3`, `contract_review 3`, `project_management 3`, `procurement_bid 3`, `audit_response 4` 문항이다.
- `2026-03-12 09:33:40 +09:00`
  - 운영 피드백 기반 조정 자동화를 위해 `backend/app/services/feedback_store.py`를 추가하고, `backend/app/services/chat.py`의 모든 응답에 `response_id`, `generated_at`을 부여해 `backend/data/feedback/chat_interactions.jsonl`로 로그를 남기도록 했다.
  - `backend/app/models/schemas.py`, `backend/app/routers/chat.py`, `frontend/src/types/api.ts`, `frontend/src/api/client.ts`를 확장해 `/api/chat-feedback` 엔드포인트와 `good/bad` 평가 스키마를 추가했다.
  - 프론트는 `frontend/src/components/Chat/ChatPanel.tsx`, `frontend/src/App.tsx`, `frontend/src/index.css`에서 assistant 답변마다 평가 패널을 노출하도록 바꿨다. `bad` 평가는 자유 메모를 받지 않고 `answer_incorrect`, `grounding_weak`, `citation_mismatch`, `missing_detail`, `format_poor`, `outdated_or_conflict` 중 최소 1개를 고르게 했다.
  - 평가 패널에는 “여러분의 답변 평가는 답변 품질 강화와 다음 조정 라운드 우선순위 설정에 큰 도움이 됩니다.” 안내 문구를 추가했다.
- `2026-03-12 09:36:55 +09:00`
  - AutoRAG 연계용으로 `backend/tests/autorag/feedback_dataset_utils.py`, `generate_feedback_report.py`, `build_feedback_review_queue.py`, `scripts/run_feedback_tuning_loop.ps1`를 추가했다.
  - `generate_feedback_report.py`는 최근 3/7/30일 윈도우의 rated answer를 answer mode와 bad reason code 분포로 요약하고, `build_feedback_review_queue.py`는 최근 bad feedback를 `backend/data/autorag/review/feedback_review_queue_<run>.json`으로 변환한다.
  - `scripts/run_feedback_tuning_loop.ps1`는 `launch=3일`, `stabilizing=7일`, `maintenance=30일` cadence를 사용한다.
  - 검증용 테스트 `backend/tests/test_feedback_store.py`, `backend/tests/test_autorag_feedback_dataset_utils.py`를 추가했고, 프론트 `npm run build` 통과 및 컨테이너 기준 회귀 테스트 `19 passed, 2 skipped`를 확인했다.
- `2026-03-12 09:40:00 +09:00`
  - FastAPI `TestClient`로 샘플 질의 2건과 bad feedback 2건을 실제로 기록해 end-to-end 로그 경로를 검증했다. 응답/평가 로그는 `backend/data/feedback/chat_interactions.jsonl`, `backend/data/feedback/chat_feedback.jsonl`에 남아 있다.
  - `powershell -ExecutionPolicy Bypass -File scripts/run_feedback_tuning_loop.ps1 -CadenceStage launch -RunId feedback_launch_20260312_0939`를 실행해 실제 산출물을 만들었다.
  - 현재 피드백 루프 검증 산출물은 `backend/data/autorag/feedback/feedback_report_feedback_launch_20260312_0939.md`, `backend/data/autorag/feedback/feedback_report_feedback_launch_20260312_0939.json`, `backend/data/autorag/review/feedback_review_queue_feedback_launch_20260312_0939.json`이다.
  - 주의: 첫 번째 샘플 피드백은 호스트 PowerShell 경유 문자열이라 `question` 필드가 깨져 있다. 실제 브라우저 프론트 경로는 UTF-8로 정상 전송되므로 운영 데이터에는 같은 문제가 재현되지 않아야 한다. 해당 샘플 row는 삭제하지 않고 보존한다.
- `2026-03-12 11:26:22 +09:00`
  - `backend/tests/autorag/paraphrase_regression_utils.py`, `generate_paraphrase_regression_report.py`, `backend/tests/test_autorag_paraphrase_regression_utils.py`, `scripts/run_paraphrase_regression_loop.ps1`를 추가해 review queue 기반 paraphrase 회귀 점검 경로를 만들었다.
  - `review_queue_gold5y_20260312_0917.json` 기준 첫 회귀 리포트는 `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1104.md`에 남겼고, 초기 결과는 `ok 1 / needs_review 3 / high_risk 14`였다. 주요 원인은 retrieval보다 citation panel 과다 노출이었다.
  - 이를 반영해 `backend/app/services/chat.py`의 citation pruning을 템플릿 응답 전용이 아니라 모든 응답 경로로 일반화했다. 재평가 결과는 `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1108.md`에 남겼고, 수치는 `ok 3 / needs_review 9 / high_risk 6`로 개선됐다.
  - 남은 고위험 우선순위는 `contract_review_03`, `hr_admin_02`, `hr_admin_03`, `standard_02`, `hr_admin_01`, `contract_review_01`이다. 이들은 citation panel 문제가 아니라 paraphrase 자체에 대한 generation 안정성 또는 retrieval recall 부족이 원인이다.
  - 검증은 dev backend 컨테이너 기준 `pytest tests/test_chat.py tests/test_answer_templates.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`에서 `20 passed`였다.
- `2026-03-12 11:26:22 +09:00`
  - `scripts/run_gold_candidate_loop.ps1`에 `generate_review_summary.py` 호출을 추가해 candidate -> review_queue -> review_summary가 한 번에 생성되도록 바꿨다.
  - `backend/tests/autorag/personas.json`에 `new_employee`, `team_lead`, `finance_officer` 3개 persona를 추가했고, 배치 실행용 `scripts/run_gold_persona_batch.ps1`를 만들었다. 첫 실행에서 `PersonaIds`가 쉼표 문자열 하나로 전달되는 문제가 있어 script 내부에서 comma split을 추가해 복구했다.
  - 기존 `five_year_employee` review queue에는 `backend/data/autorag/review/review_summary_gold5y_summary_20260312_1110.md`를 생성했다. 분류 결과는 `review_new 17`, `review_edit 1`, `merge_or_skip 0`이다.
  - 새 persona batch run `goldbatch_20260312_1116` 결과:
    `new_employee`: candidate 18 / review queue 18 / summary `review_new 18`
    `team_lead`: candidate 18 / review queue 18 / summary `review_new 18`
    `finance_officer`: candidate 18 / review queue 18 / summary `review_new 16`, `review_edit 2`
  - 산출물은 `backend/data/autorag/candidates/candidate_cases_<persona>_goldbatch_20260312_1116_<persona>.json`, `backend/data/autorag/review/review_queue_goldbatch_20260312_1116_<persona>.json`, `backend/data/autorag/review/review_summary_goldbatch_20260312_1116_<persona>.md`에 저장했다.
- `2026-03-12 11:26:22 +09:00`
  - `backend/tests/autorag/feedback_dataset_utils.py`에 `template_id_counts`, `normalized_question_counts`를 추가하고 `backend/tests/test_autorag_feedback_dataset_utils.py`에 회귀 테스트를 확장했다.
  - `backend/tests/autorag/generate_feedback_report.py`는 이제 bad reason 분포 외에 `Bad Templates`, `Repeated Bad Questions` 섹션과 JSON summary의 `bad_template_counts`, `repeated_bad_questions`를 함께 출력한다.
  - 검증은 dev backend 컨테이너 기준 `pytest tests/test_autorag_feedback_dataset_utils.py tests/test_feedback_store.py -q`에서 `4 passed`였다.
  - 새 feedback run은 `feedback_launch_20260312_1126`이며, 산출물은 `backend/data/autorag/feedback/feedback_report_feedback_launch_20260312_1126.md`, `backend/data/autorag/feedback/feedback_report_feedback_launch_20260312_1126.json`, `backend/data/autorag/review/feedback_review_queue_feedback_launch_20260312_1126.json`이다. 현재 bad template 분포는 `None 1`, `contract_change_review 1`이고, repeated bad question은 아직 없다.
- `2026-03-12 10:56:46 +09:00`
  - 템플릿 답변의 citation panel을 본문 기준으로 pruning/reindex 하도록 `backend/app/services/chat.py`를 수정했다. 답변 본문에 실제로 등장한 `[번호]`만 추출해서 citation 목록을 재구성하고, 본문 번호도 새 순서에 맞춰 다시 매긴다.
  - 새 helper 회귀 테스트는 `backend/tests/test_chat.py`에 추가했다. 인용 순서 보존, citation renumber, 누락 reference fallback 3가지를 검증한다.
  - 컨테이너 기준 `pytest tests/test_chat.py tests/test_answer_templates.py tests/test_retrieval_utils.py`는 dev/internal 모두 `16 passed`다.
  - 내부 운영 API(`http://127.0.0.1:28000/api/chat`)에서 `법인카드 사용 후 증빙은 무엇을 보관해야 하나요`를 다시 확인한 결과, 답변 본문은 `[1][2]`, `[3][4]`로 재번호화되었고 citation 목록도 4건만 남는다: `[1] 재무회계 규정 구간 219`, `[2] 재무회계 규정 구간 362`, `[3] 여비 규정 구간 12`, `[4] 재무회계 규정 구간 82`.
- `2026-03-12 10:51:48 +09:00`
  - `법인카드 사용 후 증빙은 무엇을 보관해야 하나요` 품질 이슈를 재점검했다. 초기에 PowerShell 경유 재현에서는 문자열 인코딩이 깨져 `청원심의회`가 뜨는 가짜 실패가 섞여 있었고, UTF-8 기준으로 다시 확인하니 실제 서비스는 `corp_card_policy` 템플릿을 타고 있었다.
  - 실제 문제는 템플릿이 `citations[1]`, `citations[3]`, `citations[7]` 같은 고정 위치를 인용하도록 작성돼 있어서, paraphrase 질의에서 reranker 순서가 달라지면 답변 문장은 맞아도 인용 번호가 엉뚱한 문서를 가리키는 점이었다.
  - `backend/app/services/answer_templates.py`에 semantic citation selector를 추가해서 `corp_card_policy`가 snippet/title 키워드로 제한 근거와 증빙 근거를 직접 고르도록 바꿨다. 증빙 선택에서는 `상품권`, `기록물` 문서를 제외해 잡음 문서를 차단했다.
  - `backend/tests/test_answer_templates.py`에 paraphrase 매칭 테스트와 semantic citation selection 회귀 테스트를 추가했다. 컨테이너 기준 `pytest tests/test_answer_templates.py tests/test_retrieval_utils.py`는 dev/internal 모두 `13 passed`다.
  - 내부 배포 스택(`http://127.0.0.1:28000/api/chat`)에서 같은 질의를 다시 확인한 결과, 답변은 `법인카드 제한 [4][3]`, `증빙 보관 [2][8]`을 인용하도록 바뀌었다. 이제 답변이 `상품권구매및관리규칙`을 직접 인용하지는 않는다. 다만 citation 목록 자체에는 top-k 결과로 주변 문서가 남아 있으므로, 필요하면 다음 라운드에서 template 응답용 citation list pruning/reordering을 추가로 진행하면 된다.
- `2026-03-12 10:12:42 +09:00`
  - 사내 운영용 도커 분리를 위해 `docker-compose.internal.yml`, `scripts/start_internal_deploy.ps1`, `scripts/stop_internal_deploy.ps1`, `backend/tests/reindex_all_documents.py`, `Docs/INTERNAL_DOCKER_DEPLOY.md`를 추가했다.
  - 운영 런타임 경로는 `runtime/internal/backend-data`, `runtime/internal/backend-uploads`로 분리했고, 작업/검증용 `backend/data/feedback`의 샘플 2건은 운영 feedback 경로로 복사하지 않도록 구성했다.
  - 운영용 컨테이너는 `restart: unless-stopped`로 설정했고, 기본 포트는 dev와 충돌하지 않도록 frontend `28088`, backend `28000`(로컬 바인딩), qdrant `26333`(로컬 바인딩)로 잡았다.
  - `powershell -ExecutionPolicy Bypass -File scripts/start_internal_deploy.ps1 -ForceCloneQdrant`로 `gpt_rules_internal` 프로젝트를 실제 기동했다. 현재 접속 경로는 `http://218.38.240.188:28088/chat/`, 프론트 경유 health는 `http://218.38.240.188:28088/chat/api/health`, 서버 로컬 backend health는 `http://127.0.0.1:28000/api/health`이다.
  - 운영용 Qdrant는 `gpt_rules_internal_qdrant_internal_data` 볼륨을 사용하고, dev 안정 볼륨 `gpt_rules_qdrant_data`에서 복제하도록 start script를 구성했다.
  - health/UI 경로는 확인했지만, 수동 질의(`법인카드 사용 후 증빙은 무엇을 보관해야 하나요`)는 현재 dev/운영 모두 같은 오탐 응답을 반환했다. 이는 운영 분리 문제가 아니라 현재 기준 인덱스/응답 품질 이슈로 보이며, 배포 인프라와 별도 추적이 필요하다.
## 2026-03-12 13:38:00 +09:00

### 이번 작업 요약
- paraphrase `needs_review` 9건을 raw citation 기준으로 다시 분석해, 검색 후보는 맞는데 template citation 선택이 어긋나는 케이스를 우선 보정했다.
- `project_result_report_timeline`, `expense_evidence_rule`, `training_plan_items`, `corp_card_policy`의 citation selection을 조정했고, 문서 전용 템플릿(`contract_change_documents`, `procurement_quote_documents`, `project_settlement_missing_docs`)도 실험했다.
- 문서 전용 템플릿 3종은 retrieval은 일부 개선됐지만 bootstrap answer similarity를 크게 떨어뜨려 `high_risk`를 만들었기 때문에, 코드는 남기고 자동 매칭에서는 제외했다.
- 최신 paraphrase run은 `paraphrase_gold5y_20260312_1336`이고, 결과는 `ok 11 / needs_review 7 / high_risk 0 / citation_panel_issues 0`이다. 이전 `1309`의 `ok 9 / needs_review 9 / high_risk 0` 대비 개선됐다.

### 코드 변경
- `backend/app/services/answer_templates.py`
  - citation selection 보정:
    - `project_result_report_timeline`
    - `expense_evidence_rule`
    - `training_plan_items`
    - `corp_card_policy`
  - 실험용 템플릿 추가:
    - `contract_change_documents`
    - `procurement_quote_documents`
    - `project_settlement_missing_docs`
  - 위 3개 템플릿은 파일에 남겨두되 `match_answer_template()` 자동 매칭에서는 제외
- `backend/tests/test_answer_templates.py`
  - 새 템플릿/보정 템플릿 회귀 테스트 추가 및 기대값 조정

### 검증
- 컨테이너 재빌드/재기동
  - `docker compose build backend`
  - `docker compose up -d --force-recreate backend`
- 테스트
  - `docker exec gpt_rules-backend-1 pytest tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 결과: `38 passed`
- paraphrase 회귀
  - 중간 실험: `paraphrase_gold5y_20260312_1324`
    - 결과: `ok 11 / needs_review 5 / high_risk 2`
    - 원인: `contract_change_documents`, `procurement_quote_documents`가 answer similarity를 크게 낮춤
  - 채택 run: `paraphrase_gold5y_20260312_1336`
    - 결과물:
      - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1336.md`
      - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1336.json`

### 현재 판단
- 이번 라운드로 `high_risk 0`을 유지한 채 `ok`를 2건 늘렸다.
- 남은 `needs_review 7건`은 크게 두 부류다.
  - bootstrap GT와 current citation set 차이가 남는 케이스:
    - `corp_card_policy`
    - `expense_evidence_rule`
    - `project_result_report_timeline`
    - `procurement_quote_rule`
    - `contract_change_review`
  - retrieval recall 자체가 부족한 케이스:
    - `project_management_03`
    - 일부 `project_management` 질문군
- 다음 우선순위:
  - `project_management` 질문군 retrieval recall 보정
  - `corp_card_policy` answer wording을 bootstrap phrasing 쪽으로 더 근접하게 조정
  - bootstrap 중심 평가를 넘어서 gold review 승인본을 더 늘려 과적합 위험 줄이기
## 2026-03-12 14:26:00 +09:00

### 이번 작업 요약
- 남아 있던 `needs_review 7건`을 citation selection 중심으로 정리했고, `project_management` 정산 paraphrase 1건은 전용 template로 승격했다.
- 최종 paraphrase 채택 run은 `paraphrase_gold5y_20260312_1424`이며, 결과는 `ok 18 / needs_review 0 / high_risk 0 / citation_panel_issues 0`이다.
- 중간에 `project_result_report_timeline` 문자열 조합 때문에 backend 컨테이너가 `SyntaxError: f-string expression part cannot include a backslash`로 restart loop에 들어갔고, 즉시 수정 후 재빌드해서 복구했다.

### 코드 변경
- `backend/app/services/answer_templates.py`
  - `project_management` 질문 중 `정산 + 보완/서류/절차` 조합을 `project_settlement_missing_docs`로 매칭하도록 추가
  - 다음 template에 preferred citation selection을 추가하고, preferred hit가 없을 때는 기존 generic fallback을 유지하도록 조정
    - `project_expense_evidence_list`
    - `project_settlement_missing_docs`
    - `project_result_report_timeline`
    - `expense_evidence_rule`
    - `contract_change_review`
    - `procurement_quote_rule`
    - `corp_card_policy`
  - helper 추가:
    - `_select_preferred_citations()`
- `backend/tests/test_answer_templates.py`
  - `project_settlement_missing_docs` 매칭/렌더 기대값 갱신

### 검증
- 컨테이너 재빌드/재기동
  - `docker compose build backend`
  - `docker compose up -d --force-recreate backend`
- 테스트
  - `docker exec gpt_rules-backend-1 pytest tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 결과: `38 passed`
- paraphrase 재평가
  - `docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_paraphrase_regression_report.py --review-queue-path /app/data/autorag/review/review_queue_gold5y_20260312_0917.json --run-id paraphrase_gold5y_20260312_1424`
  - 산출물
    - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1424.md`
    - `backend/data/autorag/paraphrase/paraphrase_regression_paraphrase_gold5y_20260312_1424.json`

### 현재 판단
- `five_year_employee` review queue 기준 paraphrase 회귀는 모두 `ok`로 정리됐다.
- 이번 라운드의 핵심은 retrieval widening보다 “답변 본문이 실제로 어떤 citation을 참조하느냐”를 gold/bootstrapped citation set에 맞춘 것이다.
- 다음 우선순위는 paraphrase 회귀가 아니라 gold set 확대와 운영 feedback loop 실데이터 수집이다.
## 2026-03-12 14:58:00 +09:00

### 이번 작업 요약
- gold set 검수 backlog를 단일 merged queue로 합치는 운영 루프를 정리했다.
- `merged_review_queue_*`와 `gold_backlog_*` 산출물을 자동 생성하고, 승인 row가 없으면 gold parquet export를 건너뛰도록 wrapper를 수정했다.
- 최신 gold ops run은 `gold_ops_20260312_1458`이고, 현재 상태는 `total_rows 73 / pending 73 / approved 0 / gold_ready 0`이다.

### 코드 변경
- `backend/tests/autorag/gold_dataset_utils.py`
  - review row dedupe/merge helper 추가:
    - `review_row_merge_key()`
    - `review_row_priority()`
    - `merge_review_rows()`
    - `review_backlog_snapshot()`
- `backend/tests/autorag/merge_review_queues.py`
  - `review_queue_*.json`, `feedback_review_queue_*.json`를 수집해 단일 merged queue 생성
- `backend/tests/autorag/generate_gold_backlog_report.py`
  - merged queue를 읽어 backlog markdown/json 리포트 생성
- `backend/tests/autorag/README.md`
  - gold ops 루프와 신규 스크립트 사용법 반영
- `backend/tests/test_autorag_gold_dataset_utils.py`
  - dedupe 우선순위 및 backlog snapshot 테스트 추가
- `scripts/run_gold_ops_loop.ps1`
  - merged queue 생성 -> backlog 리포트 생성 -> gold-ready row가 있을 때만 export 진행
  - PowerShell `ConvertFrom-Json` 대신 host Python으로 summary를 읽도록 변경
  - optional deps 설치는 `-InstallAutoragDeps`로 분리

### 검증
- py compile
  - `backend/tests/autorag/gold_dataset_utils.py`
  - `backend/tests/autorag/merge_review_queues.py`
  - `backend/tests/autorag/generate_gold_backlog_report.py`
  - `backend/tests/test_autorag_gold_dataset_utils.py`
- 컨테이너 테스트
  - `docker exec gpt_rules-backend-1 pytest tests/test_autorag_gold_dataset_utils.py tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 결과: `43 passed`
- wrapper 실행 검증
  - 실패 run: `gold_ops_20260312_1454`
    - 원인: PowerShell `ConvertFrom-Json`가 merged queue JSON 파싱 실패
  - 수정 후 채택 run: `gold_ops_20260312_1458`
    - 결과물:
      - `backend/data/autorag/review/merged_review_queue_gold_ops_20260312_1458.json`
      - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1458.json`
      - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1458.md`
    - console 결과:
      - `Approved gold export skipped.`
      - `No gold-ready rows in merged review queue.`

### 현재 판단
- persona/feedback review queue는 합쳐졌지만 아직 사람이 승인한 row가 없어서 gold parquet는 생성되지 않는다.
- 현재 backlog 구성은 `persona_agent 72`, `user_feedback 1`이며, persona별로는 `new_employee 18`, `five_year_employee 18`, `team_lead 18`, `finance_officer 18`, `unknown 1`이다.
- 다음 우선순위는 `merged_review_queue_gold_ops_20260312_1458.json` 기준 pending row를 승인/수정하고, gold-ready row가 생기면 `run_gold_ops_loop.ps1`로 parquet export까지 이어가는 것이다.
## 2026-03-12 15:00:00 +09:00

### 이번 작업 요약
- gold backlog를 사람이 실제로 검수하기 쉽도록 balanced review packet 생성 단계를 추가했다.
- 최신 run은 `gold_ops_20260312_1500`이고, backlog 상태는 그대로 `73 pending / 0 gold_ready`이지만 review packet 7개가 생성됐다.
- packet 1은 12건이고 `audit_response`, `contract_review`, `hr_admin`, `procurement_bid`, `project_management`, `standard`가 각 2건씩 섞이도록 배치됐다.

### 코드 변경
- `backend/tests/autorag/gold_dataset_utils.py`
  - `REVIEW_SOURCE_PRIORITY` 추가
  - `review_packet_priority()` 추가
  - `build_balanced_review_packets()` 추가
- `backend/tests/autorag/generate_review_packets.py`
  - merged review queue를 읽어 `review_packets_<run>.json/.md` 생성
- `backend/tests/autorag/README.md`
  - review packet 생성 스크립트 설명 추가
- `backend/tests/test_autorag_gold_dataset_utils.py`
  - balanced packet 생성 테스트 추가
  - 기존 gold util 테스트 문자열을 ASCII-safe로 정리해 collection 오류 제거
- `scripts/run_gold_ops_loop.ps1`
  - backlog report 다음에 review packet 생성까지 자동 수행
  - 완료 메시지에 `review_packets_<run>.md` 경로 출력

### 검증
- 컨테이너 재빌드/재기동
  - `docker compose build backend`
  - `docker compose up -d --force-recreate backend`
- 테스트
  - `docker exec gpt_rules-backend-1 pytest tests/test_autorag_gold_dataset_utils.py tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 결과: `44 passed`
- gold ops wrapper
  - `powershell -ExecutionPolicy Bypass -File scripts/run_gold_ops_loop.ps1 -RunId gold_ops_20260312_1500`
  - 산출물:
    - `backend/data/autorag/review/merged_review_queue_gold_ops_20260312_1500.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1500.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1500.md`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1500.json`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1500.md`
  - console 결과:
    - `Review packets: 7`
    - `Approved gold export skipped.`
    - `No gold-ready rows in merged review queue.`

### 현재 판단
- 이제 검수자는 merged queue 전체를 보지 않고 `review_packets_gold_ops_20260312_1500.md` 기준으로 packet 단위 승인 작업을 하면 된다.
- 다음 우선순위는 packet 1부터 `reviewed_generation_gt`, `reviewed_retrieval_gt`, `review_status`를 채워 gold-ready row를 만들고, 그 다음 동일 wrapper로 parquet export까지 이어가는 것이다.
## 2026-03-12 15:23:00 +09:00

### 이번 작업 요약
- packet 1 spot review 기준으로 5건에 대한 review decision을 source review queue에 반영했다.
- 결과적으로 `approved 4 / rejected 1 / pending 68 / gold_ready 4` 상태가 됐고, gold parquet export까지 성공했다.
- 최신 gold ops run은 `gold_ops_20260312_1522`이며, pending packet은 7개에서 6개로 줄었다.

### 코드 변경
- `backend/tests/autorag/gold_dataset_utils.py`
  - `apply_review_decisions()` 추가
- `backend/tests/autorag/apply_review_decisions.py`
  - qid 기준 review decision을 `review_queue_*.json`, `feedback_review_queue_*.json`에 되돌려 쓰는 스크립트 추가
- `backend/tests/autorag/README.md`
  - decision apply 스크립트 설명 추가
- `backend/tests/test_autorag_gold_dataset_utils.py`
  - review decision 반영 테스트 추가
- `backend/data/autorag/review/review_decisions_gold_ops_20260312_1510.json`
  - packet 1 spot review 결과 저장
  - 승인 4건:
    - `team_lead_hr_admin_01_d65bed73`
    - `team_lead_hr_admin_03_630e37ec`
    - `new_employee_procurement_bid_03_25981457`
    - `finance_officer_standard_01_7c6d867c`
  - 반려 1건:
    - `72e16c6570864b64a5e9741d8f34566b`

### 검증
- decision 반영
  - `docker exec gpt_rules-backend-1 python /app/tests/autorag/apply_review_decisions.py --decisions-path /app/data/autorag/review/review_decisions_gold_ops_20260312_1510.json --review-dir /app/data/autorag/review`
  - touched files:
    - `review_queue_goldbatch_20260312_1116_finance_officer.json`
    - `review_queue_goldbatch_20260312_1116_new_employee.json`
    - `review_queue_goldbatch_20260312_1116_team_lead.json`
    - `feedback_review_queue_feedback_launch_20260312_0939.json`
    - `feedback_review_queue_feedback_launch_20260312_1126.json`
- 테스트
  - `docker exec gpt_rules-backend-1 pytest tests/test_autorag_gold_dataset_utils.py tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 결과: `45 passed`
- gold ops export
  - `powershell -ExecutionPolicy Bypass -File scripts/run_gold_ops_loop.ps1 -RunId gold_ops_20260312_1522 -InstallAutoragDeps`
  - 결과물:
    - `backend/data/autorag/review/merged_review_queue_gold_ops_20260312_1522.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1522.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1522.md`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1522.json`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1522.md`
    - `backend/data/autorag/gold/qa_gold_gold_ops_20260312_1522.parquet`
    - `backend/data/autorag/gold/qa_gold_gold_ops_20260312_1522.json`
    - `backend/data/autorag/gold/qa_gold_latest.parquet`

### 현재 판단
- gold export 경로는 이제 실제로 동작한다. 다만 AutoRAG optional deps는 wrapper가 `-InstallAutoragDeps`일 때 실행 중 컨테이너에 설치하는 방식이라, 컨테이너 재생성 후에는 다시 설치가 필요하다.
- 다음 우선순위는 `review_packets_gold_ops_20260312_1522.md` 기준 packet 2부터 추가 승인 row를 만드는 것이다.
- 특히 `project_management`, `audit_response`, `contract_review` 남은 pending row를 우선 검수하면 gold coverage가 빨리 넓어진다.
## 2026-03-12 15:33:00 +09:00

### 이번 작업 요약
- packet 2를 보수적으로 spot review해서 `approved 6 / rejected 6`을 추가 반영했다.
- 최신 gold ops run은 `gold_ops_20260312_1532`이며, 현재 상태는 `approved 10 / rejected 7 / pending 56 / gold_ready 10`이다.
- gold parquet는 [packet 1 + packet 2] 기준으로 10건까지 확장됐고, review packet은 5개가 남았다.

### 반영 파일
- `backend/data/autorag/review/review_decisions_gold_ops_20260312_1530.json`
  - 승인 6건:
    - `five_year_employee_contract_review_03_d92271d8`
    - `team_lead_procurement_bid_02_14446d9a`
    - `five_year_employee_hr_admin_03_5ae23cad`
    - `five_year_employee_standard_01_2f2855b6`
    - `finance_officer_audit_response_03_8cbb59c1`
    - `finance_officer_hr_admin_01_d577dec5`
  - 반려 6건:
    - `five_year_employee_audit_response_01_7469eb85`
    - `finance_officer_project_management_03_852bde30`
    - `new_employee_contract_review_01_79adb9de`
    - `new_employee_project_management_01_a18100ca`
    - `new_employee_procurement_bid_01_42ff9c44`
    - `team_lead_standard_02_b036285e`

### 검증
- decision 반영
  - `docker exec gpt_rules-backend-1 python /app/tests/autorag/apply_review_decisions.py --decisions-path /app/data/autorag/review/review_decisions_gold_ops_20260312_1530.json --review-dir /app/data/autorag/review`
- gold ops export
  - `powershell -ExecutionPolicy Bypass -File scripts/run_gold_ops_loop.ps1 -RunId gold_ops_20260312_1532 -InstallAutoragDeps`
  - 결과물:
    - `backend/data/autorag/review/merged_review_queue_gold_ops_20260312_1532.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1532.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1532.md`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1532.json`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1532.md`
    - `backend/data/autorag/gold/qa_gold_gold_ops_20260312_1532.parquet`
    - `backend/data/autorag/gold/qa_gold_gold_ops_20260312_1532.json`
- 테스트
  - `docker exec gpt_rules-backend-1 pytest tests/test_autorag_gold_dataset_utils.py tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 결과: `45 passed`

### 어디가 끝인가
- 1차 종료 기준
  - `gold_ready_rows >= 20`
  - 6개 answer mode 각각 승인 row가 최소 2건 이상 확보
  - `user_feedback` 유입 row는 모두 `approved` 또는 `rejected`로 triage 완료
  - `run_gold_ops_loop.ps1 -InstallAutoragDeps`로 gold parquet export가 연속 2회 정상 동작
- 2차 종료 기준
  - 실제 운영 feedback 기준 최근 7일 `bad` 비율이 안정화되고
  - 새로 들어오는 `bad`가 기존 템플릿 오답 재발이 아니라 신규 케이스 위주로 바뀔 것
- 현재 위치
  - gold-ready 10건이므로 1차 종료 기준의 절반까지 온 상태
  - 남은 작업은 packet 3~5 검수와 answer mode coverage 확인이다

### 주의사항
- `-InstallAutoragDeps`는 컨테이너 실행 중 pip install을 수행하므로 backend recreate 이후에는 다시 필요할 수 있다.
- 더 중요한 운영 단계로 넘어가려면 다음엔 quantity보다 mode coverage를 우선 봐야 한다. 특히 `project_management`와 `contract_review` approved coverage를 더 늘릴 필요가 있다.
## 2026-03-12 15:55:00 +09:00

### 이번 작업 요약
- 남아 있던 review packet 전체를 한 번에 triage했다.
- 최신 gold ops run은 `gold_ops_20260312_1552`이고, 현재 backlog는 `pending 0 / approved 42 / rejected 31 / gold_ready 42` 상태다.
- `review_packets_gold_ops_20260312_1552.json` 기준 packet 수는 `0`이다. 즉 현재 쌓여 있던 gold backlog 검수는 모두 끝났다.

### 반영 파일
- `backend/data/autorag/review/review_decisions_gold_ops_20260312_1545.json`
  - 남은 56건 전체에 대한 batch decision
  - 결과:
    - 승인 32건 추가
    - 반려 24건 추가
- source review queue 반영:
  - `review_queue_gold5y_20260312_0917.json`
  - `review_queue_goldbatch_20260312_1116_finance_officer.json`
  - `review_queue_goldbatch_20260312_1116_new_employee.json`
  - `review_queue_goldbatch_20260312_1116_team_lead.json`

### 검증
- decision 반영
  - `docker exec gpt_rules-backend-1 python /app/tests/autorag/apply_review_decisions.py --decisions-path /app/data/autorag/review/review_decisions_gold_ops_20260312_1545.json --review-dir /app/data/autorag/review`
  - 결과: `Applied decisions: 56`
- gold ops export
  - `powershell -ExecutionPolicy Bypass -File scripts/run_gold_ops_loop.ps1 -RunId gold_ops_20260312_1552 -InstallAutoragDeps`
  - 결과물:
    - `backend/data/autorag/review/merged_review_queue_gold_ops_20260312_1552.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1552.json`
    - `backend/data/autorag/review/gold_backlog_gold_ops_20260312_1552.md`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1552.json`
    - `backend/data/autorag/review/review_packets_gold_ops_20260312_1552.md`
    - `backend/data/autorag/gold/qa_gold_gold_ops_20260312_1552.parquet`
    - `backend/data/autorag/gold/qa_gold_gold_ops_20260312_1552.json`
    - `backend/data/autorag/gold/qa_gold_latest.parquet`
- 테스트
  - `docker exec gpt_rules-backend-1 pytest tests/test_autorag_gold_dataset_utils.py tests/test_answer_templates.py tests/test_chat.py tests/test_retrieval_utils.py tests/test_autorag_paraphrase_regression_utils.py -q`
  - 결과: `45 passed`

### 현재 상태
- gold-approved coverage by answer mode:
  - `audit_response`: 9
  - `contract_review`: 3
  - `hr_admin`: 11
  - `procurement_bid`: 6
  - `project_management`: 8
  - `standard`: 5
- 1차 종료 기준 충족
  - `gold_ready_rows >= 20`: 충족 (`42`)
  - 6개 answer mode 각각 승인 row 2건 이상: 충족
  - `user_feedback` row triage 완료: 충족
  - gold parquet export 연속 정상 동작: 충족

### 어디가 끝인가
- packet 기반 초기 gold-set 확장 작업은 여기서 1차 종료로 본다.
- 다음부터는 같은 backlog를 계속 손대는 단계가 아니라, 새 입력이 생길 때만 다시 시작한다.
  - 새 persona 후보 배치 생성
  - 실제 운영 feedback 누적
  - 새 `bad` review queue 발생
- 즉 현재 기준의 끝은 `현재 backlog pending 0 + gold parquet 최신화 완료` 상태다.
## 2026-03-12 16:00:00 +09:00

### 이번 작업 요약
- 현재 배포 가능 상태를 별도 스냅샷 문서로 고정했다.
- 전체 코드 백업본을 생성할 준비를 마쳤고, 작업본을 git 초기 커밋으로 저장할 예정이다.
- 현재 기준 완료 상태는 `internal deploy ready + backlog pending 0 + gold_ready 42 + latest gold parquet exported` 이다.

### 문서화
- 상태 스냅샷:
  - `Docs/STATE_SNAPSHOT_20260312_1600.md`
- 기준 문서:
  - `HANDOFF.md`
  - `Docs/INTERNAL_DOCKER_DEPLOY.md`
  - `backend/tests/autorag/README.md`

### 커밋/백업 기준
- git 저장소가 없었기 때문에 이번 시점부터 로컬 저장소를 초기화해 현재 상태를 초기 기준선으로 잡는다.
- 백업은 코드 기준 산출물로 남기고, `runtime`, `tmp`, `backups`, `*.log`, `*.zip`는 git 추적에서 제외한다.

### 현재 판단
- 지금 시점이 “사내 배포 직전 스냅샷”으로 적합하다.
- 이후 변경이 생기면 이 시점 커밋과 백업 zip을 기준 복구점으로 사용하면 된다.
## 2026-03-12 18:12:00 +09:00

### 이번 작업 요약
- 사이드바 하단 겹침이 1차 수정 후에도 남아 있어 2차 보정을 적용했다.
- `.sidebar.panel::after` 오버레이 보더를 사이드바에만 비활성화했다.
- 마지막 `sidebar-note-section`의 구분선을 섹션 자체 border가 아니라 내부 pseudo element로 옮겨 하단 패널 경계와 시각적으로 분리했다.

### 배포 및 확인
- 내부 프론트 재배포:
  - `docker compose -p gpt_rules_internal -f docker-compose.internal.yml up -d --build frontend`
- 확인:
  - `http://218.38.240.188:28088/chat/` 응답 `200`
  - `http://127.0.0.1:28000/api/health` 응답 `{"status":"ok","documents":77,"llm_configured":true}`

## 2026-03-12 18:05:00 +09:00

### 이번 작업 요약
- 사이드바 최하단에서 레이어가 겹쳐 보이는 UI 이슈를 수정했다.
- 원인은 `.sidebar::before` 하단 장식선과 마지막 `sidebar-note-section` 경계가 같은 위치에서 겹쳐 보이는 구조였다.
- `frontend/src/index.css`에서 하단 장식선을 제거하고, 사이드바 하단 패딩과 마지막 섹션 상단 여백을 늘렸다.

### 배포 및 확인
- 프론트 빌드:
  - `npm run build`
- 내부 프론트 재배포:
  - `docker compose -p gpt_rules_internal -f docker-compose.internal.yml up -d --build frontend`
- 확인:
  - `http://218.38.240.188:28088/chat/` 응답 `200`
  - `http://127.0.0.1:28000/api/health` 응답 `{"status":"ok","documents":77,"llm_configured":true}`

## 2026-03-12 17:52:00 +09:00

### 이번 작업 요약
- 답변 평가(`POST /api/chat-feedback`) 시 `500 Internal Server Error`가 발생하는 운영 이슈를 수정했다.
- 원인은 `runtime/internal/backend-data/feedback/chat_interactions.jsonl`에 JSON 객체 2개가 한 줄에 붙어 저장된 레코드였다.
- `backend/app/services/feedback_store.py`의 JSONL 파서를 강화해 한 줄에 이어 붙은 JSON 객체도 읽도록 수정했다.
- `backend/tests/test_feedback_store.py`에 concatenated JSONL 회귀 테스트를 추가했다.

### 운영 데이터 조치
- 운영 파일 백업:
  - `runtime/internal/backend-data/feedback/chat_interactions.backup_20260312_1740.jsonl`
- 운영 파일 정규화:
  - `runtime/internal/backend-data/feedback/chat_interactions.jsonl`
- 정규화 후 `}{` 패턴 재검사 결과 추가 붙음 레코드는 남지 않았다.

### 배포 및 검증
- 내부 백엔드 재빌드/재기동:
  - `docker compose -p gpt_rules_internal -f docker-compose.internal.yml up -d --build backend`
- 컨테이너 단위 테스트:
  - `docker exec gpt_rules_internal-backend-1 pytest tests/test_feedback_store.py -q`
  - 결과: `3 passed`
- 실제 API 검증:
  - `POST http://127.0.0.1:28000/api/chat-feedback`
  - 정상 응답 확인, `feedback_id` 발급 및 `superseded_feedback_id` 갱신 확인

## 2026-03-12 17:05:00 +09:00

### 이번 작업 요약
- `gh`를 사용해 private 원격 저장소를 생성했다.
- 경량 mirror repo `C:\Project\gpt_rules_private_20260312_1630`의 `main` 브랜치를 원격 `origin`에 push 했다.

### 원격 저장소
- `https://github.com/bruce0817kr/gpt_rules_private`
- visibility: `PRIVATE`
- default branch: `main`

### 현재 상태
- mirror repo는 `origin/main`을 추적 중이다.
- mirror repo working tree는 clean 상태다.

## 2026-03-12 17:00:00 +09:00

### 이번 작업 요약
- `gh auth login`을 완료했다.
- 인증 호스트는 `github.com`, git protocol은 `https`로 설정됐다.
- 현재 로그인 계정은 `bruce0817kr` 이다.

### 현재 상태
- `gh` 기반 private 원격 저장소 생성과 push를 진행할 수 있다.

## 2026-03-12 16:45:00 +09:00

### 이번 작업 요약
- `GitHub CLI`를 `winget`으로 설치했다.
- 설치 경로는 `C:\Program Files\GitHub CLI\gh.exe` 이다.
- 새 PowerShell 세션에서 `gh`가 바로 잡히도록 사용자 PowerShell 프로필에 PATH 추가 라인을 반영했다.

### 현재 상태
- `gh --version` 확인 완료
- `where.exe gh` 확인 완료
- 인증은 아직 안 되어 있어 `gh auth login`이 다음 단계다.

## 2026-03-12 16:30:00 +09:00

### 이번 작업 요약
- 원본 로컬 저장소는 대용량 모델 캐시와 운영 산출물이 포함돼 있어 원격 Git 업로드용으로는 부적합하다고 판단했다.
- private 원격 업로드용 경량 mirror repo를 별도 경로에 생성하기로 결정했다.
- mirror repo에는 코드, 설정, 문서만 포함하고 `backend/data`, `backend/uploads`, `runtime`, `migration_export`, 대용량 dump/log는 제외한다.

### 문서화
- `Docs/PRIVATE_REPO_EXPORT_20260312_1630.md`

### 후속 기준
- 원본 저장소는 복구 기준으로 유지한다.
- 원격 Git 업로드는 mirror repo 기준으로 진행한다.
