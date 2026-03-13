# Internal Docker Deploy

This deployment path is for internal-only use on the same machine as the development workspace.

## What is separated

- Runtime uploads: `runtime/internal/backend-uploads`
- Runtime app data: `runtime/internal/backend-data`
- Runtime feedback logs: `runtime/internal/backend-data/feedback`
- Runtime vector store: dedicated Docker volume created under the `gpt_rules_internal` compose project

The internal runtime does not reuse `backend/data/feedback`, so the two verification feedback samples from local testing are not mixed into production feedback logs.

## Default internal ports

- Frontend: `28088`
- Backend: `28000`
- Qdrant HTTP: `26333`
- Qdrant gRPC: `26334`

These ports are separate from the default dev stack and can run in parallel.

## Start

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_internal_deploy.ps1
```

What the script does:

1. Creates `runtime/internal/...` directories if missing
2. Seeds the runtime catalog and uploads from the current workspace if the runtime catalog does not exist yet
3. Starts `docker-compose.internal.yml` as project `gpt_rules_internal`
4. Reindexes all seeded documents into the dedicated internal Qdrant volume on first start
5. Prints the access URLs

To force a full runtime reindex again:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_internal_deploy.ps1 -ReindexAll
```

To refresh the internal Qdrant volume from the current stable development Qdrant volume:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_internal_deploy.ps1 -ForceCloneQdrant
```

## Stop

```powershell
powershell -ExecutionPolicy Bypass -File scripts/stop_internal_deploy.ps1
```

## Access paths

- Employee UI: `http://<server-ip>:28088/chat/`
- Frontend health: `http://<server-ip>:28088/chat/api/health`
- Backend health from the server itself only: `http://127.0.0.1:28000/api/health`
- Qdrant dashboard from the server itself only: `http://127.0.0.1:26333/dashboard`

## Company domain proxy notes

For a company domain such as `https://ai.gtp.or.kr/chat/`, the upstream reverse proxy must forward:

- `/chat/` to the internal frontend nginx
- at least one of `/chat/api/` or `/api/` to the same frontend nginx or directly to the backend

The frontend now auto-detects a working API base between `/chat/api` and `/api`, so either path can be exposed by the company proxy. If neither path is forwarded, document list loading and question answering will both fail.

## Restart policy

All internal services use `restart: unless-stopped`.

If Docker Desktop or the Docker engine restarts, the internal containers are expected to come back automatically unless they were explicitly stopped.
