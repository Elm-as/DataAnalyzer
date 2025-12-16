@echo off
echo ============================================================
echo   DataAnalyzer - Lancement Complet
echo ============================================================
echo.
echo Ce script va lancer le backend ET le frontend
echo.
echo Deux fenetres vont s'ouvrir:
echo   1. Backend (Flask) - http://localhost:5000
echo   2. Frontend (Vite) - http://localhost:5173
echo.
echo Fermez cette fenetre pour arreter les deux serveurs
echo ============================================================
echo.
pause

REM Lancer le backend dans une nouvelle fenetre
start "DataAnalyzer Backend" cmd /k start-backend.bat

REM Attendre 3 secondes pour que le backend demarre
timeout /t 3 /nobreak

REM Lancer le frontend dans une nouvelle fenetre
start "DataAnalyzer Frontend" cmd /k start-frontend.bat

echo.
echo ============================================================
echo Les serveurs sont en cours de demarrage...
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Ouvrez votre navigateur sur http://localhost:5173
echo ============================================================
