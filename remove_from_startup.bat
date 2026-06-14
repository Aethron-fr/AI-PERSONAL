@echo off
echo.
echo  ============================================
echo   Removing ANUSHKA from Windows Startup
echo  ============================================
echo.

set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set VBS_FILE=%STARTUP_DIR%\anushka_wake.vbs

if exist "%VBS_FILE%" (
    del "%VBS_FILE%"
    echo ✅ ANUSHKA removed from startup.
) else (
    echo ℹ️  ANUSHKA was not in startup.
)
echo.
pause
