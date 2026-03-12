$TaskName = "GTP-Law-Sync"
$ProjectRoot = "C:\Project\gpt_rules"
$BatchPath = Join-Path $ProjectRoot "scripts\run_law_sync.bat"

if (!(Test-Path $BatchPath)) {
  throw "Batch file not found: $BatchPath"
}

$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$BatchPath`""
$Trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force
Write-Host "Scheduled task '$TaskName' registered."
