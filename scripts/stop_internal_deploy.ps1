Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ComposeFile = Join-Path $ProjectRoot "docker-compose.internal.yml"

Push-Location $ProjectRoot
try {
    docker compose -f $ComposeFile --project-name gpt_rules_internal down
}
finally {
    Pop-Location
}
