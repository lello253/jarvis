@echo off
title J.A.R.V.I.S. AI System
cd /d "%~dp0"

:: Attiva l'ambiente virtuale Python (se usi venv)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

:: Avvia Jarvis
python main.py

pause