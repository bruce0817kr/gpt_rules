# 경기테크노파크 규정 및 관계법령 가이드북

경기테크노파크의 규정과 관계 법령을 함께 검색해, 직원이 채팅으로 질문했을 때 근거 중심 답변을 빠르게 확인할 수 있도록 돕는 내부 업무용 가이드북입니다.

## 구성

- `frontend/`: React + Vite 기반의 질문 중심 UI
- `backend/`: FastAPI 기반의 문서 검색 및 답변 API
- `qdrant`: 벡터 저장소
- `KoE5`: 문서 검색용 로컬 임베딩 모델
- `bge-reranker-v2-m3`: 검색 결과 재정렬용 로컬 리랭커

## 주요 기능

- PDF, DOCX, TXT, MD 업로드 및 자동 색인
- HWP, HWPX 업로드 및 자동 색인
- 문서 목록, 상세, 검색
- 규정과 관계 법령을 함께 보여주는 근거 중심 응답
- 문서 분류별 검색 범위 제한
- 로그인 없는 내부 셀프서비스 운영

## 빠른 실행

1. `.env.example`을 복사해 `.env`를 만듭니다.
2. `OPENAI_API_KEY`와 필요 시 `OPENAI_BASE_URL`, `LLM_MODEL`을 설정합니다.
3. 배포 경로가 `https://ai.gtp.or.kr/chat`이면 기본 `VITE_PUBLIC_BASE_PATH`는 `/chat/`입니다.
4. 아래 명령으로 실행합니다.

```bash
docker compose up --build
```

기본 접속 주소:

- 프론트엔드: `http://localhost:8088/chat/`
- 백엔드 헬스체크: `http://localhost:8000/api/health`
- 프론트엔드 경유 API 헬스체크: `http://localhost:8088/chat/api/health`
- Qdrant: `http://localhost:6333/dashboard`

## 배포 참고

- 목표 주소: `https://ai.gtp.or.kr/chat/`
- 리버스 프록시는 `/chat/` 경로를 전달해야 합니다.
- 최소 하나의 API 경로(`/chat/api/` 또는 `/api/`)가 전달되어야 합니다.
- 프론트엔드는 브라우저에서 `/chat/api`와 `/api`를 자동 판별합니다.
- 두 경로 모두 전달되지 않으면 문서 목록과 채팅 응답이 모두 실패합니다.

## 법령 Markdown 동기화

- 수동 동기화: `python scripts/import_law_md.py`
- Windows 배치 실행: `scripts/run_law_sync.bat`
- 예약 작업 등록(관리자 권장): `powershell -ExecutionPolicy Bypass -File scripts/register_law_sync_task.ps1`
- 기본 법령 폴더: `C:\Project\gpt_rules\Docs\MD\law_md`