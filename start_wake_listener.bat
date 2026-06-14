@echo off
title Anushka — Wake Listener
echo.
echo  ============================================
echo   ANUSHKA - Wake Listener Background Mode
echo   Say "Hey Anushka" to wake her up!
echo  ============================================
echo.
cd /d "%~dp0"
call jarvis_env\Scripts\activate.bat
python anushka_wake_listener.py
pause
