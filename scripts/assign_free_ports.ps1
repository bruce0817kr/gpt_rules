param(
  [string]$TargetDir = "C:\Deploy\gpt_rules"
)

function Get-FreePort {
  param(
    [int[]]$PreferredPorts,
    [int]$FallbackStart,
    [int]$FallbackEnd
  )

  foreach ($port in $PreferredPorts) {
    if (Test-PortAvailable -Port $port) {
      return $port
    }
  }

  for ($port = $FallbackStart; $port -le $FallbackEnd; $port++) {
    if (Test-PortAvailable -Port $port) {
      return $port
    }
  }

  throw "No free port found in range $FallbackStart-$FallbackEnd"
}

function Test-PortAvailable {
  param([int]$Port)

  $listener = $null
  try {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $Port)
    $listener.Start()
    return $true
  } catch {
    return $false
  } finally {
    if ($listener) {
      $listener.Stop()
    }
  }
}

function Set-EnvValue {
  param(
    [string]$FilePath,
    [string]$Key,
    [string]$Value
  )

  $content = Get-Content $FilePath -Raw -Encoding UTF8
  $pattern = "(?m)^$([regex]::Escape($Key))=.*$"
  if ($content -match $pattern) {
    $content = [regex]::Replace($content, $pattern, "$Key=$Value")
  } else {
    $content = $content.TrimEnd() + "`r`n$Key=$Value`r`n"
  }
  Set-Content -Path $FilePath -Value $content -Encoding UTF8
}

$envPath = Join-Path $TargetDir ".env"
if (!(Test-Path $envPath)) {
  throw ".env not found at $envPath"
}

$frontendPort = Get-FreePort -PreferredPorts @(8088, 8089, 8090) -FallbackStart 18080 -FallbackEnd 18120
$backendPort = Get-FreePort -PreferredPorts @(8000, 8001, 8002) -FallbackStart 18000 -FallbackEnd 18060
$qdrantPort = Get-FreePort -PreferredPorts @(6333, 6335, 6336) -FallbackStart 16333 -FallbackEnd 16380

Set-EnvValue -FilePath $envPath -Key "FRONTEND_PORT" -Value $frontendPort
Set-EnvValue -FilePath $envPath -Key "BACKEND_PORT" -Value $backendPort
Set-EnvValue -FilePath $envPath -Key "QDRANT_PORT" -Value $qdrantPort

Write-Host "Assigned ports:" -ForegroundColor Cyan
Write-Host "  FRONTEND_PORT=$frontendPort"
Write-Host "  BACKEND_PORT=$backendPort"
Write-Host "  QDRANT_PORT=$qdrantPort"
