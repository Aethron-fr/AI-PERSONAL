@echo off
echo.
echo  ============================================
echo   Installing ANUSHKA to Windows Startup
echo   She will start automatically at boot!
echo  ============================================
echo.

set ANUSHKA_DIR=%~dp0
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set VBS_FILE=%STARTUP_DIR%\anushka_wake.vbs
set BAT_FILE=%ANUSHKA_DIR%start_wake_listener.bat

echo Creating hidden startup script...

rem Write a VBScript that runs the wake listener silently (no CMD window flashing)
(
echo Set WshShell = CreateObject("WScript.Shell"^)
echo WshShell.CurrentDirectory = "%ANUSHKA_DIR%"
echo WshShell.Run """%BAT_FILE%""", 1, False
) > "%VBS_FILE%"

echo.
echo ✅ SUCCESS! ANUSHKA wake listener added to Windows Startup.
echo.
echo She will now start AUTOMATICALLY every time you turn on your PC.
echo.
echo ➤ To activate her: Just say "Hey Anushka" or "Anushka wake up"
echo ➤ She will open a new window and start talking to you!
echo.
echo ➤ To REMOVE from startup, run: remove_from_startup.bat
echo.
pause
