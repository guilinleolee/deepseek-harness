$args | ForEach-Object { Write-Host "ARG: $_" }
& 'C:\Users\li\.claude\skills\claude-to-im\scripts\supervisor-windows.ps1' status
