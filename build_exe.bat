@echo off
REM ========================================
REM  BUILD EXE - LBC AUTOMATION
REM ========================================
REM Script de compilation en .exe avec PyInstaller
REM
REM Prérequis :
REM   pip install pyinstaller
REM
REM Utilisation :
REM   Double-clic sur ce fichier
REM
REM ========================================

title LBC Automation - Build EXE
color 0A
cd /d "%~dp0"

echo.
echo ========================================
echo   LBC AUTOMATION - BUILD EXE
echo ========================================
echo.

REM Vérifier si PyInstaller est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python non trouve
    pause
    exit /b 1
)

echo [1/5] Verification de PyInstaller...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo [!] PyInstaller non installe
    echo [~] Installation de PyInstaller...
    python -m pip install pyinstaller
)
echo [OK] PyInstaller pret

REM Nettoyer les anciens builds
echo.
echo [2/5] Nettoyage des anciens builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"
echo [OK] Nettoyage termine

REM Compilation avec PyInstaller
echo.
echo [3/5] Compilation en cours...
echo.
echo Configuration :
echo   - Point d'entree : launcher.py
echo   - Mode : Fichier unique (onefile)
echo   - Console : Visible
echo   - Nom : LBC_Automation.exe
echo.

python -m PyInstaller ^
  --onefile ^
  --name "LBC_Automation" ^
  --add-data "static;static" ^
  --add-data "config.env.example;." ^
  --hidden-import=uvicorn.lifespan.on ^
  --hidden-import=uvicorn.lifespan.off ^
  --hidden-import=uvicorn.protocols.websockets.auto ^
  --hidden-import=uvicorn.protocols.http.auto ^
  --hidden-import=uvicorn.protocols.websockets.websockets_impl ^
  --hidden-import=playwright._impl._api_structures ^
  --collect-all fastapi ^
  --collect-all uvicorn ^
  --collect-all playwright ^
  launcher.py

if errorlevel 1 (
    echo.
    echo [ERREUR] La compilation a echoue
    pause
    exit /b 1
)

echo.
echo [4/5] Compilation terminee !

REM Créer le dossier de distribution
echo.
echo [5/5] Preparation du package de distribution...

if not exist "dist\LBC_Automation_Package" mkdir "dist\LBC_Automation_Package"

REM Copier l'exe
copy "dist\LBC_Automation.exe" "dist\LBC_Automation_Package\" >nul

REM Copier les fichiers nécessaires
copy "config.env.example" "dist\LBC_Automation_Package\" >nul
copy "README.md" "dist\LBC_Automation_Package\" >nul
copy "requirements.txt" "dist\LBC_Automation_Package\" >nul

REM Créer le dossier img vide
if not exist "dist\LBC_Automation_Package\img" mkdir "dist\LBC_Automation_Package\img"
echo Placez vos photos ici > "dist\LBC_Automation_Package\img\README.txt"

REM Créer un fichier d'instructions
echo # LBC AUTOMATION - GUIDE RAPIDE > "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo. >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo INSTALLATION : >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo 1. Double-clic sur LBC_Automation.exe >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo 2. Attendre l'installation de Chromium (premiere fois uniquement) >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo 3. Le navigateur s'ouvre automatiquement >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo. >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo CONFIGURATION : >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo 1. Cliquer sur "Configuration" >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo 2. Remplir vos identifiants LeBonCoin >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo 3. Configurer le Google Sheet >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo 4. Indiquer le dossier des photos >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo 5. Enregistrer >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo. >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo IMPORTANT : >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo - Placer service_account.json dans ce dossier >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"
echo - Ajouter vos photos dans le dossier img/ >> "dist\LBC_Automation_Package\GUIDE_RAPIDE.txt"

echo [OK] Package pret dans : dist\LBC_Automation_Package

REM Résumé
echo.
echo ========================================
echo   BUILD TERMINE !
echo ========================================
echo.
echo Fichiers generes :
echo   - dist\LBC_Automation.exe
echo   - dist\LBC_Automation_Package\ (package complet)
echo.
echo Taille approximative : ~50-100 MB
echo.
echo Prochaines etapes :
echo   1. Copier dist\LBC_Automation_Package
echo   2. Ajouter service_account.json
echo   3. Distribuer au client
echo.
echo ========================================
echo.

pause
