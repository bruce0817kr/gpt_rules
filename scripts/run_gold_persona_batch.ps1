param(
    [string]$RunIdPrefix = (Get-Date -Format "yyyyMMdd_HHmmss"),
    [string[]]$PersonaIds = @("new_employee", "team_lead", "finance_officer"),
    [int]$CountScale = 1
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot

Push-Location $ProjectRoot
try {
    docker compose build backend
    docker compose up -d backend

    $NormalizedPersonaIds = @()
    foreach ($RawPersonaId in $PersonaIds) {
        foreach ($SplitPersonaId in ($RawPersonaId -split ",")) {
            $PersonaId = $SplitPersonaId.Trim()
            if (-not [string]::IsNullOrWhiteSpace($PersonaId)) {
                $NormalizedPersonaIds += $PersonaId
            }
        }
    }

    foreach ($PersonaId in $NormalizedPersonaIds) {
        $RunId = "${RunIdPrefix}_${PersonaId}"
        $CandidatePath = "/app/data/autorag/candidates/candidate_cases_${PersonaId}_${RunId}.json"
        $ReviewQueuePath = "/app/data/autorag/review/review_queue_${RunId}.json"

        docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_persona_candidates.py --persona-id $PersonaId --count-scale $CountScale --run-id $RunId
        docker exec gpt_rules-backend-1 python /app/tests/autorag/build_review_queue.py --cases-path $CandidatePath --run-id $RunId
        docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_review_summary.py --candidate-path $CandidatePath --review-queue-path $ReviewQueuePath --run-id $RunId

        Write-Host "Completed persona batch item."
        Write-Host "Persona: $PersonaId"
        Write-Host "Run ID: $RunId"
        Write-Host "Candidate file: backend/data/autorag/candidates/candidate_cases_${PersonaId}_${RunId}.json"
        Write-Host "Review queue: backend/data/autorag/review/review_queue_${RunId}.json"
        Write-Host "Review summary: backend/data/autorag/review/review_summary_${RunId}.md"
    }
}
finally {
    Pop-Location
}
