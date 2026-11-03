@echo off
cd /d "%~dp0"

echo ==========================================
echo Devine le nombre - backend setup
echo ==========================================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python launcher "py" was not found.
    echo Install Python 3.13 from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

echo Creating virtual environment...
py -3.13 -m venv .venv
if errorlevel 1 (
    echo.
    echo Could not create the environment with Python 3.13.
    echo Check that Python 3.13 is installed.
    pause
    exit /b 1
)

echo.
echo Updating pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip

echo.
echo Installing the required libraries...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo ==========================================
echo Setup finished.
echo Now put these files in the models folder:
echo   modele_chiffres.pkl
echo   scaler.pkl
echo Then double-click run_backend.bat
echo ==========================================
pause
