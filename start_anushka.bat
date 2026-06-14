@echo off
echo.
echo  ============================================
echo   ANUSHKA - Your Personal AI Companion
echo   Starting up...
echo  ============================================
echo.

cd /d "%~dp0"
call jarvis_env\Scripts\activate.bat
python anushka_main.py text
