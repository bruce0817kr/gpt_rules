param(
    [string]$RunId = (Get-Date -Format "yyyyMMdd_HHmmss"),
    [switch]$GenerateCandidates,
    [string[]]$PersonaIds = @("new_employee", "five_year_employee", "team_lead", "finance_officer"),
    [int]$CountScale = 1,
    [switch]$InstallAutoragDeps,
    [switch]$SkipGoldExport
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot

Push-Location $ProjectRoot
try {
    docker compose build backend
    docker compose up -d backend

    if ($GenerateCandidates) {
        foreach ($RawPersonaId in $PersonaIds) {
            foreach ($SplitPersonaId in ($RawPersonaId -split ",")) {
                $PersonaId = $SplitPersonaId.Trim()
                if ([string]::IsNullOrWhiteSpace($PersonaId)) {
                    continue
                }

                $PersonaRunId = "${RunId}_${PersonaId}"
                $CandidatePath = "/app/data/autorag/candidates/candidate_cases_${PersonaId}_${PersonaRunId}.json"
                $ReviewQueuePath = "/app/data/autorag/review/review_queue_${PersonaRunId}.json"

                docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_persona_candidates.py --persona-id $PersonaId --count-scale $CountScale --run-id $PersonaRunId
                docker exec gpt_rules-backend-1 python /app/tests/autorag/build_review_queue.py --cases-path $CandidatePath --run-id $PersonaRunId
                docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_review_summary.py --candidate-path $CandidatePath --review-queue-path $ReviewQueuePath --run-id $PersonaRunId
            }
        }
    }

    $MergedQueuePath = "/app/data/autorag/review/merged_review_queue_${RunId}.json"
    $MergedQueueHostPath = Join-Path $ProjectRoot "backend/data/autorag/review/merged_review_queue_${RunId}.json"

    docker exec gpt_rules-backend-1 python /app/tests/autorag/merge_review_queues.py --run-id $RunId
    docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_gold_backlog_report.py --review-queue-path $MergedQueuePath --run-id $RunId
    docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_review_packets.py --review-queue-path $MergedQueuePath --run-id $RunId

    $GoldReadyRowsOutput = @'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(payload["summary"]["gold_ready_rows"])
'@ | python - $MergedQueueHostPath
    $GoldReadyRows = [int]($GoldReadyRowsOutput | Select-Object -Last 1)
    $GoldExported = $false
    if (-not $SkipGoldExport -and $GoldReadyRows -gt 0) {
        if ($InstallAutoragDeps) {
            docker exec gpt_rules-backend-1 pip install -r /app/tests/autorag/requirements.txt
        }
        try {
            docker exec gpt_rules-backend-1 python /app/tests/autorag/export_reviewed_gold.py --review-queue-path $MergedQueuePath --run-id $RunId
            if ($LASTEXITCODE -ne 0) {
                throw "export_reviewed_gold.py failed with exit code $LASTEXITCODE"
            }
            $GoldExported = $true
        }
        catch {
            Write-Host "Approved gold export skipped."
            Write-Host $_.Exception.Message
        }
    }
    elseif (-not $SkipGoldExport) {
        Write-Host "Approved gold export skipped."
        Write-Host "No gold-ready rows in merged review queue."
    }

    Write-Host "Gold ops loop completed."
    Write-Host "Run ID: $RunId"
    Write-Host "Merged queue: backend/data/autorag/review/merged_review_queue_${RunId}.json"
    Write-Host "Backlog report: backend/data/autorag/review/gold_backlog_${RunId}.md"
    Write-Host "Review packets: backend/data/autorag/review/review_packets_${RunId}.md"
    if ($GoldExported) {
        Write-Host "Gold parquet: backend/data/autorag/gold/qa_gold_${RunId}.parquet"
    }
}
finally {
    Pop-Location
}
