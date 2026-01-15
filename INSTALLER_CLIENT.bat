@echo off
REM ========================================
REM  INSTALLATEUR - LBC AUTOMATION
REM ========================================

title LBC Automation - Installation
color 0A
cd /d "%~dp0"

echo.
echo ========================================
echo   LBC AUTOMATION - INSTALLATION
echo ========================================
echo.

REM Verifier Python
echo [1/4] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERREUR] Python n'est pas installe
    echo.
    echo Telechargez Python depuis : https://www.python.org/downloads/
    echo Cochez "Add Python to PATH" lors de l'installation
    echo.
    pause
    exit /b 1
)
echo [OK] Python detecte
python --version

REM Installer les dependances
echo.
echo [2/4] Installation des dependances...
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERREUR] Installation des dependances echouee
    pause
    exit /b 1
)
echo [OK] Dependances installees

REM Installer Chromium
echo.
echo [3/4] Installation de Chromium (peut prendre 2-3 minutes)...
python -m playwright install chromium
if errorlevel 1 (
    echo [ERREUR] Installation de Chromium echouee
    pause
    exit /b 1
)
echo [OK] Chromium installe

REM Verification config
echo.
echo [4/4] Verification du fichier de configuration...
if not exist "service_account.json" (
    echo [ATTENTION] service_account.json manquant
    echo Ce fichier est necessaire pour acceder a Google Sheets
)
echo [OK] Verification terminee

REM Fin
echo.
echo ========================================
echo   INSTALLATION TERMINEE !
echo ========================================
echo.
echo Pour lancer LBC Automation :
echo   Double-cliquez sur LANCER.bat
echo.
pause
