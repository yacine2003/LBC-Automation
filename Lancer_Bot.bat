@echo off
chcp 65001 >nul
title LBC Automation - Serveur

echo.
echo ================================================================================
echo                     🤖 LBC AUTOMATION - DÉMARRAGE
echo ================================================================================
echo.

cd /d "%~dp0"

echo 📂 Répertoire de travail : %CD%
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR : Python n'est pas installé ou n'est pas dans le PATH
    echo.
    echo 📥 Téléchargez Python depuis : https://www.python.org/downloads/
    echo ⚠️  N'oubliez pas de cocher "Add Python to PATH" pendant l'installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python détecté : 
python --version
echo.

REM Vérifier que les dépendances sont installées
echo 🔍 Vérification des dépendances...
python -c "import fastapi, uvicorn, playwright, gspread" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  ATTENTION : Certaines dépendances sont manquantes
    echo.
    echo 📦 Installation des dépendances en cours...
    echo.
    pip install fastapi uvicorn playwright gspread oauth2client playwright-stealth requests
    echo.
    echo 🎭 Installation de Chromium...
    python -m playwright install chromium
    echo.
)

echo ✅ Dépendances OK
echo.

REM Vérifier la configuration
if not exist "config.py" (
    echo ❌ ERREUR : config.py introuvable
    echo    Vérifiez que vous êtes dans le bon dossier
    pause
    exit /b 1
)

if not exist "service_account.json" (
    echo ⚠️  ATTENTION : service_account.json introuvable
    echo    Le bot ne pourra pas accéder au Google Sheet
    echo.
)

echo 🚀 Lancement du serveur...
echo.
echo ================================================================================
echo                            📡 SERVEUR EN LIGNE
echo ================================================================================
echo.
echo 🌐 Interface web : http://localhost:8000
echo 🔗 Documentation : http://localhost:8000/docs
echo.
echo 💡 Pour arrêter le serveur : Appuyez sur Ctrl+C
echo.
echo ================================================================================
echo.

python main.py

echo.
echo ================================================================================
echo                           ⏹️  SERVEUR ARRÊTÉ
echo ================================================================================
echo.
pause

