Get-Process Outlook |   Foreach-Object { $_.CloseMainWindow() | Out-Null }

Get-Process Teams |   Foreach-Object { $_.CloseMainWindow() | Out-Null }

Stop-Process -Name Teams
