@echo off
echo.
echo  ============================================
echo   ANUSHKA - Voice Mode (Wake Word)
echo   Say "Anushka" to wake me up!
echo  ============================================
echo.

cd /d "%~dp0"
call jarvis_env\Scripts\activate.bat
python anushka_main.py wake_word
