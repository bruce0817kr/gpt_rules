@echo off
setlocal

:: Resolve ROOT directory relative to the script location (scripts folder)
set SCRIPTS_DIR=%~dp0
for %%i in ("%SCRIPTS_DIR%..") do set ROOT=%%~fi
set EXPORT_DIR=%ROOT%\migration_export

if not exist "%EXPORT_DIR%" mkdir "%EXPORT_DIR%"

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set TS=%%i
set BUNDLE=%EXPORT_DIR%\gpt_rules_bundle_%TS%.zip
set QDRANT_ARCHIVE=%EXPORT_DIR%\qdrant_data_%TS%.tar.gz

echo [1/4] Stopping services...
cd /d "%ROOT%"
docker compose down

echo [2/4] Compressing project folder with generated artifacts excluded...
:: Build the zip from a recursive filtered file list so nested node_modules/dist/logs are excluded too.
powershell -NoProfile -Command ^
  "$root = [System.IO.Path]::GetFullPath('%ROOT%'); " ^
  "$dirExcludes = @('\migration_export\', '\.git\', '\.venv\', '\tmp\', '\frontend\node_modules\', '\frontend\dist\', '\scripts\logs\', '\__pycache__\'); " ^
  "$fileExcludes = @('\scripts\qdrant_data_', '\scripts\searcher_logs.txt', '\scripts\qdrant_logs.txt', '\scripts\qdrant_health.json', '\hwp_mcp_stdio_server.log'); " ^
  "$items = Get-ChildItem -Path $root -Recurse -File -Force | Where-Object { " ^
  "  $full = $_.FullName; " ^
  "  -not ($dirExcludes | Where-Object { $full.Contains($_) }) -and " ^
  "  -not ($fileExcludes | Where-Object { $full.Contains($_) }) " ^
  "}; " ^
  "Compress-Archive -LiteralPath $items.FullName -DestinationPath '%BUNDLE%' -Force"

echo [3/4] Exporting Qdrant volume...
docker run --rm -v gpt_rules_qdrant_data:/source -v "%EXPORT_DIR%:/backup" alpine sh -c "cd /source && tar czf /backup/qdrant_data_%TS%.tar.gz ."

echo [4/4] Backup complete.
echo Project bundle: %BUNDLE%
echo Qdrant archive: %QDRANT_ARCHIVE%

endlocal
