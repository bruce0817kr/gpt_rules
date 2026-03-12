param(
    [string]$RunId = (Get-Date -Format "yyyyMMdd_HHmmss"),
    [switch]$RefreshBootstrap
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$AutoragRoot = Join-Path $ProjectRoot "backend\data\autorag"
$RunsRoot = Join-Path $AutoragRoot "runs"
$RunDir = Join-Path $RunsRoot $RunId

New-Item -ItemType Directory -Force $RunsRoot | Out-Null
New-Item -ItemType Directory -Force $RunDir | Out-Null

Push-Location $ProjectRoot
try {
    docker compose build backend
    docker compose up -d backend

    docker exec gpt_rules-backend-1 python -m pip install -r /app/tests/autorag/requirements.txt
    $BootstrapArtifacts = @(
        "backend\data\autorag\bootstrap\qa.parquet",
        "backend\data\autorag\bootstrap\corpus.parquet",
        "backend\data\autorag\bootstrap\seed_cases_used.json"
    )
    $BootstrapMissing = @($BootstrapArtifacts | Where-Object { -not (Test-Path (Join-Path $ProjectRoot $_)) })
    if ($RefreshBootstrap -or $BootstrapMissing.Count -gt 0) {
        docker exec gpt_rules-backend-1 python /app/tests/autorag/build_bootstrap_dataset.py
    }
    else {
        Write-Host "Reusing existing bootstrap dataset."
    }
    docker exec gpt_rules-backend-1 python /app/tests/autorag/evaluate_current_rag.py
    docker exec gpt_rules-backend-1 python /app/tests/autorag/generate_report.py --run-id $RunId

    $Artifacts = @(
        "backend\data\autorag\bootstrap\qa.parquet",
        "backend\data\autorag\bootstrap\corpus.parquet",
        "backend\data\autorag\bootstrap\seed_cases_used.json",
        "backend\data\autorag\results\retrieval_eval_reranker_on.csv",
        "backend\data\autorag\results\retrieval_eval_reranker_off.csv",
        "backend\data\autorag\results\generation_eval.csv",
        "backend\data\autorag\reports\summary_${RunId}.json",
        "backend\data\autorag\reports\report_${RunId}.md",
        "backend\data\autorag\reports\history.csv"
    )

    foreach ($RelativePath in $Artifacts) {
        $Source = Join-Path $ProjectRoot $RelativePath
        if (Test-Path $Source) {
            Copy-Item -Path $Source -Destination $RunDir -Force
        }
    }

    Write-Host "Ralph-loop run completed."
    Write-Host "Run ID: $RunId"
    Write-Host "Artifacts: $RunDir"
}
finally {
    Pop-Location
}
