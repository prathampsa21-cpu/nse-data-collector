# PowerShell Script to register Daily NSE 1-Min Data Collector Task
# Runs Monday to Friday at 4:00 PM IST (16:00)

$taskName = "NSE_1Min_Daily_Collector"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$batPath = Join-Path $scriptDir "run_daily.bat"

Write-Host "Registering Scheduled Task: $taskName" -ForegroundColor Cyan
Write-Host "Target script: $batPath"

$action = New-ScheduledTaskAction -Execute $batPath -WorkingDirectory $scriptDir

# Trigger at 4:00 PM (16:00) on weekdays (Mon-Fri)
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 4:00PM

# Settings: Allow wake to run, run as soon as possible if schedule missed
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -WakeToRun -StartWhenAvailable

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Daily automated NSE 1-minute OHLCV candle data collection for stocks > Rs 1,000 Cr" -Force

Write-Host ""
Write-Host "[OK] Successfully registered $taskName in Windows Task Scheduler!" -ForegroundColor Green
Write-Host "It will automatically run every weekday at 4:00 PM IST." -ForegroundColor Yellow
