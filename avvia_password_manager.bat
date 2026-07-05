@echo off
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
) else (
    python main.py
)

echo.
echo Se la finestra non si e aperta, leggi l'errore qui sopra.
pause
