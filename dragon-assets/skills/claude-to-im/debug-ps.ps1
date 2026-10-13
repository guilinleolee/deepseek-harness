$PROFILE | ForEach-Object { Write-Host "Profile: $_"; Test-Path $_ }
$PROFILE | ForEach-Object { if (Test-Path $_) { Get-Content $_ | Select-Object -First 10 } }
Write-Host "PSVersionTable:"
$PSVersionTable | Format-Table -AutoSize
Write-Host "Execution Policy (current): $(Get-ExecutionPolicy -Scope CurrentUser)"
Write-Host "args count: $($args.Count)"
$args | ForEach-Object { Write-Host "arg: $_" }
