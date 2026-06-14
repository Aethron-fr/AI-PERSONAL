$WshShell = New-Object -comObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath('Desktop')

# Shortcut 1: Talk to Anushka (Text Mode)
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\Talk to Anushka.lnk")
$Shortcut.TargetPath = "C:\Users\ghosh\.gemini\antigravity\scratch\JARVIS\start_anushka.bat"
$Shortcut.WorkingDirectory = "C:\Users\ghosh\.gemini\antigravity\scratch\JARVIS"
$Shortcut.Description = "Start Anushka - Your Personal AI Companion"
$Shortcut.IconLocation = "shell32.dll,13"
$Shortcut.Save()

Write-Host "Shortcut 1 created: Talk to Anushka"

# Shortcut 2: Anushka Voice Mode
$Shortcut2 = $WshShell.CreateShortcut("$DesktopPath\Anushka Voice Mode.lnk")
$Shortcut2.TargetPath = "C:\Users\ghosh\.gemini\antigravity\scratch\JARVIS\start_wake_listener.bat"
$Shortcut2.WorkingDirectory = "C:\Users\ghosh\.gemini\antigravity\scratch\JARVIS"
$Shortcut2.Description = "Start Anushka Wake Listener - Say Hey Anushka!"
$Shortcut2.IconLocation = "shell32.dll,168"
$Shortcut2.Save()

Write-Host "Shortcut 2 created: Anushka Voice Mode"
Write-Host "Both shortcuts are now on your Desktop!"
