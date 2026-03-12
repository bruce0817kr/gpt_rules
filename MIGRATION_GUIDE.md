# 서버 이전 가이드

이 문서는 `C:\Project\gpt_rules` 프로젝트와 현재 적재된 데이터 전체를 다른 서버로 옮기는 절차를 설명합니다.

## 1. 이전 대상

코드:

- `C:\Project\gpt_rules` 전체

로컬 바인드 데이터:

- `backend\uploads` - 원본 업로드 파일
- `backend\data` - sqlite, huggingface 캐시, 법령 markdown/json 저장분
- `scripts\logs` - 법령 동기화 로그

Docker volume 데이터:

- `gpt_rules_qdrant_data` - Qdrant 벡터 데이터

## 2. 이전 전 권장 작업

1. 서비스 중지 또는 읽기 전용 시간 확보
2. `.env`의 현재 OpenAI 키는 폐기 예정이면 새 키 준비
3. 대상 서버에 Docker / Docker Compose / Python 설치 확인

## 3. 가장 안전한 이전 방식

Windows 서버에서는 아래 배치 파일을 바로 사용할 수 있습니다.

- 원본 서버 백업: `scripts\backup_project_windows.bat`
- 대상 서버 복원: `scripts\restore_project_windows.bat`
- Docker 자동 시작 설정: `scripts\enable_docker_autostart.bat`
- 자동 포트 할당: `scripts\assign_free_ports.ps1`
- 복원 후 자동 헬스체크: `scripts\post_restore_healthcheck.ps1`

### 3-1. 원본 서버에서 서비스 중지

```bash
docker compose down
```

### 3-2. 프로젝트 폴더 압축

Windows PowerShell 예시:

```powershell
Compress-Archive -Path C:\Project\gpt_rules\* -DestinationPath C:\Project\gpt_rules_bundle.zip -Force
```

### 3-3. Qdrant volume 백업

```bash
docker run --rm -v gpt_rules_qdrant_data:/source -v C:\Project:/backup alpine sh -c "cd /source && tar czf /backup/qdrant_data.tar.gz ."
```

## 4. 대상 서버로 복사할 파일

- `gpt_rules_bundle.zip`
- `qdrant_data.tar.gz`

복사 방법 예시:

- `scp`
- `rsync`
- 사내 파일 전송 시스템

## 5. 대상 서버에서 복원

### 5-1. 프로젝트 압축 해제

```bash
mkdir -p /srv/gpt_rules
unzip gpt_rules_bundle.zip -d /srv/gpt_rules
```

### 5-2. 환경 파일 점검

- `/srv/gpt_rules/.env` 확인
- 새 서버용 `OPENAI_API_KEY` 교체
- 필요 시 포트/도메인 값 수정

### 5-3. Qdrant volume 생성 및 복원

```bash
docker volume create gpt_rules_qdrant_data
docker run --rm -v gpt_rules_qdrant_data:/target -v /srv:/backup alpine sh -c "cd /target && tar xzf /backup/qdrant_data.tar.gz"
```

### 5-4. 서비스 기동

```bash
cd /srv/gpt_rules
docker compose up -d --build
```

### 5-5. Windows 대상 서버용 빠른 실행

관리자 CMD 또는 PowerShell에서:

```bat
scripts\enable_docker_autostart.bat
scripts\restore_project_windows.bat C:\Transfer\gpt_rules_bundle.zip C:\Transfer\qdrant_data.tar.gz C:\Deploy\gpt_rules
```

복원 배치는 대상 서버에서 빈 포트를 자동 탐지해 `.env`의 아래 값을 갱신합니다.

- `FRONTEND_PORT`
- `BACKEND_PORT`
- `QDRANT_PORT`

기본 우선 포트:

- 프론트엔드: `8088`, `8089`, `8090`
- 백엔드: `8000`, `8001`, `8002`
- Qdrant: `6333`, `6335`, `6336`

우선 포트가 이미 사용 중이면 내부 fallback 범위에서 자동으로 빈 포트를 찾습니다.

복원 배치는 스택 기동 후 자동으로 아래 헬스체크를 수행합니다.

- `http://localhost:<BACKEND_PORT>/api/health`
- `http://localhost:<FRONTEND_PORT>/chat/api/health`

## 6. 복원 후 확인 체크

헬스체크:

```bash
curl http://localhost:8000/api/health
curl http://localhost:8088/chat/api/health
```

확인 항목:

- 문서 수가 원본과 같은지
- `law` 카테고리 문서 수가 같은지
- source viewer 정상 동작
- category/body 검색 정상 동작
- 관리자 문서 목록, 재색인, 법령 추가 정상 동작

## 7. 운영 데이터만 빠르게 이전하는 경우

이미 대상 서버에 같은 코드가 있다면 아래만 옮겨도 됩니다.

- `backend/uploads`
- `backend/data`
- `qdrant_data.tar.gz` 복원

단, 코드 버전이 다르면 schema/API 차이가 날 수 있으므로 전체 코드 동기화를 권장합니다.

## 8. 주의사항

- `backend/data/huggingface`는 모델 캐시라 용량이 큼
- 옮기지 않아도 새 서버에서 재다운로드 가능하지만, 초기 기동 시간이 늘어남
- Qdrant volume을 안 옮기면 벡터 인덱스를 다시 만들어야 하므로 시간이 많이 걸림
- `.env`는 절대 Git에 올리지 말 것
- 노출된 API 키는 반드시 폐기 후 새 키 사용
- `docker-compose.yml`의 각 서비스는 이미 `restart: unless-stopped`가 설정되어 있음
- 따라서 Windows 서버에서 Docker 서비스만 자동 시작되면 컨테이너도 재부팅 후 자동 복구됨

## 9. 추천 이전 순서 요약

1. 원본 서버 `docker compose down`
2. 프로젝트 폴더 압축
3. Qdrant volume tar 백업
4. 대상 서버로 전송
5. 프로젝트 해제 + `.env` 수정
6. Qdrant volume 복원
7. `docker compose up -d --build`
8. 헬스체크 + 문서 수 검증
