# 재단 규정 상담봇

재단 규정, 내부 규칙, 관계 법령을 RAG로 검색해 직원 질문에 근거 중심 답변을 제공하는 내부용 업무 상담 챗봇입니다.

## 구성

- `frontend/`: React + Vite 기반 직원 상담/문서관리 UI
- `backend/`: FastAPI 기반 문서 업로드, 인덱싱, 검색, 답변 API
- `qdrant`: 벡터 저장소
- `KoE5`: 한국어 문서 검색용 로컬 임베딩 모델
- `bge-reranker-v2-m3`: 검색 결과 재정렬용 로컬 리랭커

## 주요 기능

- PDF, DOCX, TXT, MD 업로드 및 자동 인덱싱
- HWP, HWPX 업로드 및 자동 인덱싱
- 문서 목록, 삭제, 재색인
- 질문별 근거 문서 인용 표시
- 문서 분류별 검색 범위 제한
- 로그인 없는 내부망 전용 운영 가정

## 빠른 실행

1. `.env.example`을 복사해 `.env`를 만듭니다.
2. `OPENAI_API_KEY`와 필요 시 `OPENAI_BASE_URL`, `LLM_MODEL`을 채웁니다.
3. 사내 배포 경로가 `https://ai.gtp.or.kr/chat` 이므로 기본 `VITE_PUBLIC_BASE_PATH`는 `/chat/` 입니다.
4. 아래 명령으로 실행합니다.

```bash
docker compose up --build
```

기본 접속 주소:

- 프론트엔드: `http://localhost:8088/chat/`
- 백엔드 헬스체크: `http://localhost:8000/api/health`
- 프론트 프록시 헬스체크: `http://localhost:8088/chat/api/health`
- Qdrant: `http://localhost:6333/dashboard`

## 사내 도메인 배포

- 목표 주소: `https://ai.gtp.or.kr/chat/`
- 외부 TLS 종료는 사내 리버스 프록시 또는 인그레스에서 처리합니다.
- 프록시는 `/chat/` 경로를 프론트엔드 컨테이너로 전달하면 됩니다.
- 프론트엔드 컨테이너는 `/chat/api/` 요청을 내부적으로 백엔드로 프록시합니다.

## 내부 배포 주의사항

- 앱 자체 로그인/회원관리는 없습니다.
- 반드시 사내 VPN, 방화벽, 리버스 프록시 등 네트워크 계층에서 접근을 제한하세요.
- 답변은 참고용이며 최종 판단 전 원문 확인이 필요합니다.

## 법령 Markdown 동기화

- 수동 동기화: `python scripts/import_law_md.py`
- Windows 배치 실행: `scripts/run_law_sync.bat`
- 예약 작업 등록(PowerShell 관리자 권장): `powershell -ExecutionPolicy Bypass -File scripts/register_law_sync_task.ps1`
- 기본 법령 폴더: `C:\Project\gpt_rules\Docs\MD\law_md`
## Company Domain Proxy

- `https://ai.gtp.or.kr/chat/` front proxy must pass `/chat/`
- It must also expose at least one API path: `/chat/api/` or `/api/`
- The frontend now auto-detects between `/chat/api` and `/api` in the browser
- If neither API path is forwarded, document list loading and chat answers will both fail
