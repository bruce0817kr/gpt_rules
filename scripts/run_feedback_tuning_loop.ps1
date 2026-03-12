param(
    [string]$RunId = (Get-Date -Format "yyyyMMdd_HHmmss"),
    [ValidateSet("launch", "stabilizing", "maintenance")]
    [string]$CadenceStage = "launch"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LookbackDays = switch ($CadenceStage) {
    "launch" { 3 }
    "stabilizing" { 7 }
    "maintenance" { 30 }
}

Push-Location $ProjectRoot
try {
    docker compose build backend
    docker compose up -d backend

    docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_feedback_report.py --lookback-days $LookbackDays --run-id $RunId
    docker exec gpt_rules-backend-1 python /app/tests/autorag/build_feedback_review_queue.py --lookback-days $LookbackDays --run-id $RunId

    Write-Host "Feedback tuning loop completed."
    Write-Host "Run ID: $RunId"
    Write-Host "Cadence stage: $CadenceStage"
    Write-Host "Lookback days: $LookbackDays"
    Write-Host "Feedback report: backend/data/autorag/feedback/feedback_report_${RunId}.md"
    Write-Host "Feedback queue: backend/data/autorag/review/feedback_review_queue_${RunId}.json"
}
finally {
    Pop-Location
}
