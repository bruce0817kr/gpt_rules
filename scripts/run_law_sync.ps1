$ProjectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$LogDir = Join-Path $PSScriptRoot "logs"
if (!(Test-Path $LogDir)) {
  New-Item -ItemType Directory -Path $LogDir | Out-Null
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir ("law_sync_{0}.log" -f $Timestamp)

$msg = "[$(Get-Date -Format s)] Starting law sync..."
$msg | Out-File -FilePath $LogFile -Encoding utf8
Write-Host $msg

python (Join-Path $PSScriptRoot "import_law_md.py") *>> $LogFile

$msg = "[$(Get-Date -Format s)] Law sync finished."
$msg | Out-File -FilePath $LogFile -Append -Encoding utf8
Write-Host $msg
