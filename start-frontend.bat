@echo off
echo ============================================================
echo   DataAnalyzer - Demarrage Frontend
echo ============================================================
echo.

REM Verifier si node_modules existe
if not exist "node_modules" (
    echo [ERREUR] Dependances Node.js non installees
    echo.
    echo Veuillez executer d'abord: npm install
    echo.
    pause
    exit /b 1
)

echo Demarrage du serveur de developpement...
echo Interface disponible sur: http://localhost:5173
echo.
echo Appuyez sur CTRL+C pour arreter le serveur
echo ============================================================
echo.

npm run dev
