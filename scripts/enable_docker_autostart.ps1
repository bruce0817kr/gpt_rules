$ServiceName = "com.docker.service"

$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if (-not $service) {
  throw "Docker service '$ServiceName' not found. Make sure Docker Desktop or Docker Engine is installed on this Windows server."
}

Set-Service -Name $ServiceName -StartupType Automatic
Start-Service -Name $ServiceName

Write-Host "Docker service startup type set to Automatic and service started."
Write-Host "Note: docker-compose services already use 'restart: unless-stopped', so containers will auto-restart after Docker starts."
