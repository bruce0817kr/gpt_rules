# Private Repo Export

## 목적
- 원본 작업 저장소는 대용량 모델 캐시와 운영 산출물이 함께 들어 있어 원격 Git 업로드용으로는 부적합하다.
- private 원격 저장소에는 코드, 설정, 문서만 포함한 경량 mirror repo를 별도로 사용한다.

## 원본 저장소
- 경로: `C:\Project\gpt_rules`
- 기준 커밋: `73ba1c3d33ea7fced34bccaa7443d316fc98df80`

## 경량 mirror repo
- 경로: `C:\Project\gpt_rules_private_20260312_1630`
- 브랜치: `main`
- 목적: private 원격 업로드용

## mirror repo 제외 대상
- `backend/data/**`
- `backend/uploads/**`
- `runtime/**`
- `backups/**`
- `migration_export/**`
- `scripts/logs/**`
- `scripts/qdrant_data_*.tar.gz`
- `scripts/qdrant_logs.txt`
- `scripts/searcher_logs.txt`
- `scripts/volumes.txt`
- `scripts/qdrant_health.json`
- `frontend/node_modules/**`
- `frontend/dist/**`
- `.env`
- `*.zip`
- `*.log`

## 복구 기준
- 전체 작업 스냅샷과 운영 산출물은 원본 저장소와 백업 zip에서 보존한다.
- 원격 Git에는 재현 가능한 코드와 문서만 유지한다.
