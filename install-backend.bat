@echo off
echo ============================================================
echo   DataAnalyzer - Installation du Backend
echo ============================================================
echo.

REM Verifier si Python est installe
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans PATH
    echo.
    echo Telechargez Python depuis: https://www.python.org/downloads/
    echo Installez Python 3.10, 3.11 ou 3.12 (pas 3.14)
    pause
    exit /b 1
)

echo [1/4] Creation de l'environnement virtuel...
if not exist ".venv" (
    python -m venv .venv
    echo [OK] Environnement virtuel cree
) else (
    echo [OK] Environnement virtuel existe deja
)
echo.

echo [2/4] Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
echo.

echo [3/4] Installation des dependances de base...
echo Cela peut prendre quelques minutes...
echo.
python -m pip install --upgrade pip
python -m pip install flask flask-cors pandas numpy scipy scikit-learn statsmodels reportlab matplotlib seaborn openpyxl python-dateutil joblib
echo.

echo [4/4] Test de l'installation...
python backend\test_backend.py
echo.

echo ============================================================
echo Installation terminee!
echo.
echo Pour demarrer le backend, executez: start-backend.bat
echo ============================================================
pause
