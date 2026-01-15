@echo off
REM ========================================
REM  LANCEUR - LBC AUTOMATION
REM ========================================

title LBC Automation
cd /d "%~dp0"

echo.
echo ========================================
echo   LBC AUTOMATION
echo ========================================
echo.
echo Demarrage du serveur...
echo Interface disponible sur : http://localhost:8000
echo.
echo Appuyez sur Ctrl+C pour arreter
echo.

REM Ouvrir le navigateur automatiquement apres 3 secondes
start /B timeout /t 3 /nobreak >nul && start http://localhost:8000

REM Lancer le serveur
python main.py

pause
