@echo off
echo ============================================================
echo   DataAnalyzer - Demarrage du Backend
echo ============================================================
echo.

REM Aller dans le dossier backend
cd /d "%~dp0backend"

REM Verifier si l'environnement virtuel existe
if exist "..\\.venv\Scripts\python.exe" (
    echo [OK] Environnement virtuel trouve
    echo.
    echo Demarrage du serveur Flask...
    echo Serveur disponible sur: http://localhost:5000
    echo.
    echo Appuyez sur CTRL+C pour arreter le serveur
    echo ============================================================
    echo.
    ..\.venv\Scripts\python.exe app.py
) else (
    echo [ERREUR] Environnement virtuel non trouve
    echo.
    echo Veuillez executer d'abord: install-backend.bat
    echo.
    pause
)
