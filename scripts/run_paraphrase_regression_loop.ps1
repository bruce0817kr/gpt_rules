param(
    [string]$RunId = (Get-Date -Format "yyyyMMdd_HHmmss"),
    [string]$ReviewQueuePath = "/app/data/autorag/review/review_queue_gold5y_20260312_0917.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot

Push-Location $ProjectRoot
try {
    docker compose build backend
    docker compose up -d backend

    docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_paraphrase_regression_report.py --review-queue-path $ReviewQueuePath --run-id $RunId

    Write-Host "Paraphrase regression run completed."
    Write-Host "Run ID: $RunId"
    Write-Host "Review queue: $ReviewQueuePath"
    Write-Host "Regression report: backend/data/autorag/paraphrase/paraphrase_regression_${RunId}.md"
}
finally {
    Pop-Location
}
