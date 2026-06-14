@echo off
TITLE Anushka AI Companion
cd /d "%~dp0"
echo Starting ANUSHKA...
start "" ".\jarvis_env\Scripts\pythonw.exe" anushka_main.py
exit
