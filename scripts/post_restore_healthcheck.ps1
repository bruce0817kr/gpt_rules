param(
  [string]$TargetDir = "",
  [int]$MaxWaitSeconds = 180
)

if ([string]::IsNullOrEmpty($TargetDir)) {
  $TargetDir = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
}

$envPath = Join-Path $TargetDir ".env"
if (!(Test-Path $envPath)) {
  throw ".env not found at $envPath"
}

$envMap = @{}
Get-Content $envPath -Encoding UTF8 | ForEach-Object {
  if ($_ -match '^(?<k>[A-Z0-9_]+)=(?<v>.*)$') {
    $envMap[$Matches.k] = $Matches.v
  }
}

$backendPortValue = '8000'
if ($envMap.ContainsKey('BACKEND_PORT') -and $envMap['BACKEND_PORT']) {
  $backendPortValue = $envMap['BACKEND_PORT']
}

$frontendPortValue = '8088'
if ($envMap.ContainsKey('FRONTEND_PORT') -and $envMap['FRONTEND_PORT']) {
  $frontendPortValue = $envMap['FRONTEND_PORT']
}

$backendPort = [int]$backendPortValue
$frontendPort = [int]$frontendPortValue

$backendUrl = "http://localhost:$backendPort/api/health"
$frontendUrl = "http://localhost:$frontendPort/chat/api/health"

function Wait-Health {
  param(
    [string]$Url,
    [int]$MaxWaitSeconds
  )

  $deadline = (Get-Date).AddSeconds($MaxWaitSeconds)
  while ((Get-Date) -lt $deadline) {
    try {
      $resp = Invoke-RestMethod -Uri $Url -TimeoutSec 10
      return $resp
    } catch {
      Start-Sleep -Seconds 5
    }
  }
  throw "Health check timed out: $Url"
}

$backend = Wait-Health -Url $backendUrl -MaxWaitSeconds $MaxWaitSeconds
$frontend = Wait-Health -Url $frontendUrl -MaxWaitSeconds $MaxWaitSeconds

Write-Host "Backend health OK: $backendUrl"
Write-Host ($backend | ConvertTo-Json -Compress)
Write-Host "Frontend health OK: $frontendUrl"
Write-Host ($frontend | ConvertTo-Json -Compress)
