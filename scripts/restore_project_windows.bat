@echo off
setlocal

if "%~1"=="" (
  echo Usage: restore_project_windows.bat ^<bundle.zip^> ^<qdrant_data.tar.gz^> [TARGET_DIR]
  exit /b 1
)

if "%~2"=="" (
  echo Usage: restore_project_windows.bat ^<bundle.zip^> ^<qdrant_data.tar.gz^> [TARGET_DIR]
  exit /b 1
)

set BUNDLE=%~f1
set QDRANT_ARCHIVE=%~f2
set TARGET_DIR=%~3

:: Default target directory to one level up from this script (project root)
if "%TARGET_DIR%"=="" (
  set SCRIPTS_DIR=%~dp0
  for %%i in ("%SCRIPTS_DIR%..") do set TARGET_DIR=%%~fi
)

if not exist "%BUNDLE%" (
  echo Error: Bundle file not found: %BUNDLE%
  exit /b 1
)
if not exist "%QDRANT_ARCHIVE%" (
  echo Error: Qdrant archive not found: %QDRANT_ARCHIVE%
  exit /b 1
)

if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo [1/5] Preparing target directory...
powershell -NoProfile -Command ^
  "$target = [System.IO.Path]::GetFullPath('%TARGET_DIR%'); " ^
  "$paths = @('backend', 'frontend', 'nginx', 'scripts', 'Docs', 'tmp', 'docker-compose.yml', '.env.example', 'README.md', 'HANDOFF.md', 'MIGRATION_GUIDE.md', 'RELEASE_CHECKLIST.md'); " ^
  "foreach ($path in $paths) { " ^
  "  $candidate = Join-Path $target $path; " ^
  "  if (Test-Path $candidate) { Remove-Item -LiteralPath $candidate -Recurse -Force } " ^
  "}"

echo [2/5] Extracting project bundle to %TARGET_DIR% ...
powershell -NoProfile -Command "Expand-Archive -Path '%BUNDLE%' -DestinationPath '%TARGET_DIR%' -Force"

echo [2.5/5] Assigning free ports on target server...
powershell -NoProfile -ExecutionPolicy Bypass -File "%TARGET_DIR%\scripts\assign_free_ports.ps1" -TargetDir "%TARGET_DIR%"

echo [3/5] Creating Qdrant volume...
docker volume create gpt_rules_qdrant_data

echo [4/5] Restoring Qdrant data...
:: Get path to qdrant archive's directory for mounting
for %%i in ("%QDRANT_ARCHIVE%") do (
  set ARCHIVE_DIR=%%~dpi
  set ARCHIVE_NAME=%%~nxi
)
docker run --rm -v gpt_rules_qdrant_data:/target -v "%ARCHIVE_DIR%:/backup" alpine sh -c "cd /target && tar xzf /backup/%ARCHIVE_NAME%"

echo [5/5] Starting stack...
cd /d "%TARGET_DIR%"
docker compose up -d --build

echo [5.5/5] Running health checks...
set BPORT=8000
set FPORT=8088
if exist "%TARGET_DIR%\.env" (
  for /f "usebackq tokens=1,* delims==" %%a in ("%TARGET_DIR%\.env") do (
    if "%%a"=="BACKEND_PORT" set BPORT=%%b
    if "%%a"=="FRONTEND_PORT" set FPORT=%%b
  )
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%TARGET_DIR%\scripts\post_restore_healthcheck.ps1" -TargetDir "%TARGET_DIR%"

echo Done. Health endpoints:
echo   http://localhost:%BPORT%/api/health
echo   http://localhost:%FPORT%/chat/api/health

endlocal
