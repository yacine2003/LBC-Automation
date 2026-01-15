@echo off
REM ========================================
REM  CREATION PACKAGE PORTABLE - LBC AUTOMATION
REM ========================================
REM Ce script cree un package complet avec Python portable
REM pour livraison au client (aucune installation requise)
REM ========================================

title LBC Automation - Creation Package Portable
color 0A
cd /d "%~dp0"

echo.
echo ========================================
echo   CREATION PACKAGE PORTABLE
echo ========================================
echo.
echo Ce script va creer un package complet
echo avec Python portable pour le client.
echo.
echo Duree estimee : 10-15 minutes
echo Taille finale : ~500 MB
echo.
pause

REM ========================================
REM ETAPE 1 : Creer le dossier de distribution
REM ========================================
echo.
echo [1/8] Creation du dossier de distribution...
if exist "LBC_Portable" rmdir /s /q "LBC_Portable"
mkdir "LBC_Portable"
echo [OK] Dossier cree

REM ========================================
REM ETAPE 2 : Telecharger Python Portable
REM ========================================
echo.
echo [2/8] Telechargement de Python Portable (3.11.0)...
echo      Cela peut prendre 2-3 minutes...
powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-embed-amd64.zip' -OutFile 'python-portable.zip'}"
if errorlevel 1 (
    echo [ERREUR] Telechargement echoue
    pause
    exit /b 1
)
echo [OK] Python Portable telecharge

REM ========================================
REM ETAPE 3 : Extraire Python Portable
REM ========================================
echo.
echo [3/8] Extraction de Python Portable...
powershell -Command "& {Expand-Archive -Path 'python-portable.zip' -DestinationPath 'LBC_Portable\python' -Force}"
del python-portable.zip
echo [OK] Python Portable extrait

REM ========================================
REM ETAPE 4 : Configurer Python Portable pour pip
REM ========================================
echo.
echo [4/8] Configuration de Python Portable...

REM Activer les imports depuis site-packages
cd LBC_Portable\python
echo import site >> python311._pth
cd ..\..

REM Telecharger get-pip.py
echo      Telechargement de pip...
powershell -Command "& {Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'LBC_Portable\get-pip.py'}"

REM Installer pip
echo      Installation de pip...
LBC_Portable\python\python.exe LBC_Portable\get-pip.py --no-warn-script-location
del LBC_Portable\get-pip.py
echo [OK] Python Portable configure

REM ========================================
REM ETAPE 5 : Installer les dependances
REM ========================================
echo.
echo [5/8] Installation des dependances (5-7 minutes)...
LBC_Portable\python\python.exe -m pip install -r requirements.txt --no-warn-script-location
if errorlevel 1 (
    echo [ERREUR] Installation des dependances echouee
    pause
    exit /b 1
)
echo [OK] Dependances installees

REM ========================================
REM ETAPE 6 : Installer Chromium
REM ========================================
echo.
echo [6/8] Installation de Chromium (2-3 minutes)...
LBC_Portable\python\python.exe -m playwright install chromium
if errorlevel 1 (
    echo [ERREUR] Installation de Chromium echouee
    pause
    exit /b 1
)
echo [OK] Chromium installe

REM ========================================
REM ETAPE 7 : Copier les fichiers du projet
REM ========================================
echo.
echo [7/8] Copie des fichiers du projet...

REM Copier les fichiers Python
copy main.py LBC_Portable\ >nul
copy bot_engine.py LBC_Portable\ >nul
copy config.py LBC_Portable\ >nul
copy gsheet_manager.py LBC_Portable\ >nul
copy utils.py LBC_Portable\ >nul
copy captcha_handler.py LBC_Portable\ >nul
copy config.env.example LBC_Portable\ >nul

REM Copier le dossier static
xcopy /E /I /Y static LBC_Portable\static >nul

REM Copier les fichiers de documentation
copy LISEZMOI_CLIENT.txt LBC_Portable\ >nul
copy INSTRUCTIONS_CLIENT.md LBC_Portable\ >nul

echo [OK] Fichiers copies

REM ========================================
REM ETAPE 8 : Creer le lanceur
REM ========================================
echo.
echo [8/8] Creation du lanceur...

REM Creer DEMARRER.bat
(
echo @echo off
echo title LBC Automation
echo cd /d "%%~dp0"
echo.
echo echo.
echo echo ========================================
echo echo   LBC AUTOMATION
echo echo ========================================
echo echo.
echo echo Demarrage du serveur...
echo echo Interface disponible sur : http://localhost:8000
echo echo.
echo echo Appuyez sur Ctrl+C pour arreter
echo echo.
echo.
echo REM Ouvrir le navigateur apres 3 secondes
echo start /B timeout /t 3 /nobreak ^>nul ^&^& start http://localhost:8000
echo.
echo REM Lancer le serveur
echo python\python.exe main.py
echo.
echo pause
) > LBC_Portable\DEMARRER.bat

REM Creer README.txt
(
echo ========================================
echo   LBC AUTOMATION - GUIDE RAPIDE
echo ========================================
echo.
echo PREMIERE UTILISATION :
echo.
echo 1. Ajouter le fichier service_account.json dans ce dossier
echo 2. Double-cliquer sur DEMARRER.bat
echo 3. Une page web s'ouvre automatiquement
echo 4. Cliquer sur "Configuration"
echo 5. Remplir vos informations :
echo    - Identifiants Leboncoin
echo    - Nom du Google Sheet
echo    - Dossier des photos
echo 6. Enregistrer
echo.
echo UTILISATION QUOTIDIENNE :
echo.
echo 1. Double-cliquer sur DEMARRER.bat
echo 2. Cliquer sur "Demarrer"
echo 3. Suivre la progression
echo.
echo Pour arreter : Cliquer sur "Arreter" ou fermer la fenetre
echo.
echo ========================================
echo.
echo IMPORTANT :
echo - Partager votre Google Sheet avec :
echo   lbc-automation@lbc-automation-483321.iam.gserviceaccount.com
echo.
echo - Structure du Google Sheet :
echo   Titre ^| Description ^| Prix ^| Categorie ^| Photos ^| Statut ^| Type ^| Ville
echo.
echo - Mettre "A_FAIRE" dans la colonne Statut pour publier
echo.
echo ========================================
) > LBC_Portable\README.txt

echo [OK] Lanceur cree

REM ========================================
REM FINALISATION
REM ========================================
echo.
echo ========================================
echo   CREATION TERMINEE !
echo ========================================
echo.
echo Package cree dans : LBC_Portable\
echo.
echo PROCHAINES ETAPES :
echo.
echo 1. Copier service_account.json dans LBC_Portable\
echo 2. Tester : double-clic sur LBC_Portable\DEMARRER.bat
echo 3. Creer un ZIP du dossier LBC_Portable
echo 4. Envoyer le ZIP au client
echo.
echo TAILLE APPROXIMATIVE : ~500 MB
echo.
echo ========================================
echo.
pause
