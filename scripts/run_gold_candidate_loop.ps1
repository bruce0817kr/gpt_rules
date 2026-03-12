param(
    [string]$RunId = (Get-Date -Format "yyyyMMdd_HHmmss"),
    [string]$PersonaId = "five_year_employee",
    [int]$CountScale = 1
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot

Push-Location $ProjectRoot
try {
    docker compose build backend
    docker compose up -d backend

    docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_persona_candidates.py --persona-id $PersonaId --count-scale $CountScale --run-id $RunId
    $CandidatePath = "/app/data/autorag/candidates/candidate_cases_${PersonaId}_${RunId}.json"
    docker exec gpt_rules-backend-1 python /app/tests/autorag/build_review_queue.py --cases-path $CandidatePath --run-id $RunId
    $ReviewQueuePath = "/app/data/autorag/review/review_queue_${RunId}.json"
    docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_review_summary.py --candidate-path $CandidatePath --review-queue-path $ReviewQueuePath --run-id $RunId

    Write-Host "Gold candidate run completed."
    Write-Host "Run ID: $RunId"
    Write-Host "Candidate file: backend/data/autorag/candidates/candidate_cases_${PersonaId}_${RunId}.json"
    Write-Host "Review queue: backend/data/autorag/review/review_queue_${RunId}.json"
    Write-Host "Review summary: backend/data/autorag/review/review_summary_${RunId}.md"
}
finally {
    Pop-Location
}
