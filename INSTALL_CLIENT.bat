@echo off
chcp 65001 >nul
title LBC Automation - Installation Client

echo.
echo ================================================================================
echo                     🤖 LBC AUTOMATION - INSTALLATION
echo ================================================================================
echo.

cd /d "%~dp0"

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERREUR : Python n'est pas installé
    echo.
    echo 📥 Téléchargez Python depuis : https://www.python.org/downloads/
    echo ⚠️  Cochez "Add Python to PATH" pendant l'installation
    echo.
    pause
    exit /b 1
)

echo ✅ Python détecté
python --version
echo.

REM Créer le fichier de configuration s'il n'existe pas
if not exist "config.env" (
    if exist "config.env.example" (
        echo 📝 Création du fichier de configuration...
        copy config.env.example config.env
        echo ✅ Fichier config.env créé
        echo.
        echo ⚠️  IMPORTANT : Éditez config.env pour ajouter vos identifiants
        echo    - Email LeBonCoin
        echo    - Mot de passe LeBonCoin
        echo    - Nom du Google Sheet
        echo.
    )
)

REM Créer le dossier img s'il n'existe pas
if not exist "img" (
    echo 📁 Création du dossier img...
    mkdir img
    echo ✅ Dossier img créé
    echo    Placez vos photos dans ce dossier
    echo.
)

REM Installer les dépendances
echo 📦 Installation des dépendances Python...
echo    (Cela peut prendre quelques minutes)
echo.
pip install --quiet fastapi uvicorn playwright gspread oauth2client playwright-stealth requests

if errorlevel 1 (
    echo.
    echo ❌ Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)

echo ✅ Dépendances Python installées
echo.

REM Installer Chromium
echo 🌐 Installation de Chromium...
python -m playwright install chromium

if errorlevel 1 (
    echo.
    echo ❌ Erreur lors de l'installation de Chromium
    pause
    exit /b 1
)

echo ✅ Chromium installé
echo.

REM Vérifier service_account.json
if not exist "service_account.json" (
    echo.
    echo ⚠️  ATTENTION : Fichier service_account.json manquant
    echo.
    echo 📋 Étapes à suivre :
    echo    1. Créez un Service Account sur Google Cloud Console
    echo    2. Téléchargez le fichier JSON
    echo    3. Renommez-le en service_account.json
    echo    4. Placez-le dans ce dossier
    echo.
    echo 📖 Consultez GUIDE_INSTALLATION_CLIENT.md pour plus de détails
    echo.
)

echo.
echo ================================================================================
echo                     ✅ INSTALLATION TERMINÉE
echo ================================================================================
echo.
echo 📋 PROCHAINES ÉTAPES :
echo.
echo 1. ✅ Python et dépendances installés
echo 2. 📝 Éditez config.env avec vos identifiants
echo 3. 📸 Ajoutez vos photos dans le dossier img\
echo 4. 🔑 Ajoutez service_account.json (Google Sheets)
echo 5. 🚀 Double-cliquez sur Lancer_Bot.bat
echo.
echo 💡 AIDE :
echo    - Pour configurer via interface web : http://localhost:8000/config
echo    - Guide complet : GUIDE_INSTALLATION_CLIENT.md
echo.
echo ================================================================================
echo.
pause

