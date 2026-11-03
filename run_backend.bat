@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo ERROR: The virtual environment does not exist.
    echo Run setup_backend.bat first.
    pause
    exit /b 1
)

if not exist "models\modele_chiffres.pkl" (
    echo ERROR: models\modele_chiffres.pkl is missing.
    echo Put the exported model file in the models folder.
    pause
    exit /b 1
)

if not exist "models\scaler.pkl" (
    echo ERROR: models\scaler.pkl is missing.
    echo Put the exported scaler file in the models folder.
    pause
    exit /b 1
)

echo Starting backend...
echo.
echo Open in your browser:
echo   http://127.0.0.1:8000
echo   http://127.0.0.1:8000/docs
echo.
echo Keep this window open while using the website.
echo Press CTRL+C to stop the backend.
echo.

".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000
pause
