@echo off
cd /d "%~dp0"
echo ========================================
echo   Challenge Raids Orientation
echo ========================================
echo.

REM Chercher Python dans différents emplacements
set PYTHON_CMD=

REM 1. Essayer py (Python Launcher)
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto :found
)

REM 2. Essayer python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :found
)

REM 3. Essayer python3
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    goto :found
)

REM 4. Chercher dans AppData (installation utilisateur)
if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    goto :found
)
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    goto :found
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :found
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :found
)
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    goto :found
)

REM 5. Chercher dans Program Files
if exist "C:\Python314\python.exe" (
    set PYTHON_CMD="C:\Python314\python.exe"
    goto :found
)
if exist "C:\Python313\python.exe" (
    set PYTHON_CMD="C:\Python313\python.exe"
    goto :found
)
if exist "C:\Python312\python.exe" (
    set PYTHON_CMD="C:\Python312\python.exe"
    goto :found
)

REM Python non trouve
echo ERREUR: Python non trouve.
echo.
echo Ou est installe votre Python ? Entrez le chemin complet vers python.exe
echo (ex: C:\Python314\python.exe)
echo Ou appuyez sur Entree pour quitter.
set /p PYTHON_CMD="Chemin: "
if "%PYTHON_CMD%"=="" (
    echo Installation annulee.
    pause
    exit /b 1
)
%PYTHON_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ce chemin ne fonctionne pas.
    pause
    exit /b 1
)

:found
echo Python trouve!
%PYTHON_CMD% --version
echo.

echo Installation des dependances...
%PYTHON_CMD% -m pip install -r requirements.txt --quiet
echo.

echo Lancement de l'application...
%PYTHON_CMD% -m streamlit run app.py
pause
