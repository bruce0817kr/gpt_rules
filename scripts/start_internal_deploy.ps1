param(
    [switch]$ReindexAll,
    [switch]$ForceCloneQdrant,
    [string]$SeedQdrantVolume = "gpt_rules_qdrant_data"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ComposeFile = Join-Path $ProjectRoot "docker-compose.internal.yml"
$ComposeArgs = @("-f", $ComposeFile, "--project-name", "gpt_rules_internal")

$SourceUploadsDir = Join-Path $ProjectRoot "backend\uploads"
$SourceDataDir = Join-Path $ProjectRoot "backend\data"
$RuntimeRoot = Join-Path $ProjectRoot "runtime\internal"
$RuntimeUploadsDir = Join-Path $RuntimeRoot "backend-uploads"
$RuntimeDataDir = Join-Path $RuntimeRoot "backend-data"
$RuntimeLawDir = Join-Path $RuntimeDataDir "law_md"
$RuntimeFeedbackDir = Join-Path $RuntimeDataDir "feedback"
$InternalQdrantVolume = "gpt_rules_internal_qdrant_internal_data"

function Get-EnvValue([string]$Name, [string]$DefaultValue) {
    if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($Name))) {
        return $DefaultValue
    }
    return [Environment]::GetEnvironmentVariable($Name)
}

function Wait-ForBackendHealth([string[]]$ComposeArgs, [int]$MaxAttempts = 60) {
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        try {
            docker compose @ComposeArgs exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=5).read()" *> $null
            return
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }
    throw "Timed out waiting for backend container health."
}

function Copy-SeedTree([string]$SourceDir, [string]$TargetDir) {
    if (-not (Test-Path $SourceDir)) {
        return
    }
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
    Copy-Item -Path (Join-Path $SourceDir "*") -Destination $TargetDir -Recurse -Force -ErrorAction SilentlyContinue
}

function Docker-VolumeExists([string]$VolumeName) {
    docker volume inspect $VolumeName | Out-Null
    return ($LASTEXITCODE -eq 0)
}

function Copy-DockerVolume([string]$SourceVolume, [string]$TargetVolume) {
    docker run --rm -v "${SourceVolume}:/from:ro" -v "${TargetVolume}:/to" alpine sh -c "cp -a /from/. /to/"
}

function Get-DockerVolumeEntryCount([string]$VolumeName) {
    $Result = docker run --rm -v "${VolumeName}:/data" alpine sh -c "find /data -mindepth 1 -maxdepth 1 | wc -l"
    return [int]($Result | Select-Object -Last 1)
}

New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null
New-Item -ItemType Directory -Force -Path $RuntimeUploadsDir | Out-Null
New-Item -ItemType Directory -Force -Path $RuntimeDataDir | Out-Null
New-Item -ItemType Directory -Force -Path $RuntimeLawDir | Out-Null
New-Item -ItemType Directory -Force -Path $RuntimeFeedbackDir | Out-Null

$SeededNow = $false
$ClonedQdrantNow = $false
$RuntimeCatalogPath = Join-Path $RuntimeDataDir "documents.sqlite3"
if (-not (Test-Path $RuntimeCatalogPath)) {
    $SourceCatalogMatches = Get-ChildItem -Path $SourceDataDir -Filter "documents.sqlite3*" -File -ErrorAction SilentlyContinue
    foreach ($File in $SourceCatalogMatches) {
        Copy-Item -Path $File.FullName -Destination (Join-Path $RuntimeDataDir $File.Name) -Force
    }
    Copy-SeedTree -SourceDir $SourceUploadsDir -TargetDir $RuntimeUploadsDir
    Copy-SeedTree -SourceDir (Join-Path $SourceDataDir "law_md") -TargetDir $RuntimeLawDir
    $SeededNow = $true

}

if (
    (Docker-VolumeExists -VolumeName $SeedQdrantVolume) -and (
        $ForceCloneQdrant -or
        ((Get-DockerVolumeEntryCount -VolumeName $InternalQdrantVolume) -eq 0)
    )
) {
    Copy-DockerVolume -SourceVolume $SeedQdrantVolume -TargetVolume $InternalQdrantVolume
    $ClonedQdrantNow = $true
}

Push-Location $ProjectRoot
try {
    docker compose @ComposeArgs build
    docker compose @ComposeArgs up -d

    $BackendPort = Get-EnvValue -Name "INTERNAL_BACKEND_PORT" -DefaultValue "28000"
    $FrontendPort = Get-EnvValue -Name "INTERNAL_FRONTEND_PORT" -DefaultValue "28088"
    $QdrantPort = Get-EnvValue -Name "INTERNAL_QDRANT_PORT" -DefaultValue "26333"
    $PublicBasePath = Get-EnvValue -Name "VITE_PUBLIC_BASE_PATH" -DefaultValue "/chat/"
    if (-not $PublicBasePath.StartsWith("/")) {
        $PublicBasePath = "/$PublicBasePath"
    }
    if (-not $PublicBasePath.EndsWith("/")) {
        $PublicBasePath = "$PublicBasePath/"
    }

    Wait-ForBackendHealth -ComposeArgs $ComposeArgs

    if ((-not $ClonedQdrantNow) -and ($SeededNow -or $ReindexAll)) {
        docker compose @ComposeArgs exec -T backend python /app/tests/reindex_all_documents.py
    }

    $Ipv4Candidates = @(
        Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
            Where-Object {
                $_.IPAddress -notlike "127.*" -and
                $_.IPAddress -notlike "169.254.*" -and
                $_.PrefixOrigin -ne "WellKnown" -and
                $_.InterfaceAlias -notlike "vEthernet*"
            } |
            Select-Object -ExpandProperty IPAddress -Unique
    )
    $PrimaryIp = if ($Ipv4Candidates.Count -gt 0) { $Ipv4Candidates[0] } else { "localhost" }

    Write-Host "Internal deployment is running."
    Write-Host "Frontend: http://$PrimaryIp`:$FrontendPort$PublicBasePath"
    Write-Host "Frontend health: http://$PrimaryIp`:$FrontendPort$($PublicBasePath.TrimEnd('/'))/api/health"
    Write-Host "Backend health (server local only): http://127.0.0.1:$BackendPort/api/health"
    Write-Host "Qdrant dashboard (server local only): http://127.0.0.1:$QdrantPort/dashboard"
    Write-Host "Runtime uploads: $RuntimeUploadsDir"
    Write-Host "Runtime data: $RuntimeDataDir"
    if ($SeededNow -and $ClonedQdrantNow) {
        Write-Host "Runtime data was seeded from current backend catalog/uploads and the dedicated Qdrant volume was cloned from the stable development volume."
    }
    elseif ($SeededNow) {
        Write-Host "Runtime data was seeded from current backend catalog/uploads and reindexed into a dedicated Qdrant volume."
    }
    elseif ($ClonedQdrantNow) {
        Write-Host "Runtime catalog/uploads were reused and the dedicated Qdrant volume was refreshed from the stable development volume."
    }
    else {
        Write-Host "Runtime data already existed, so the existing internal dataset was reused."
    }
}
finally {
    Pop-Location
}
