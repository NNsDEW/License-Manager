@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==== Podgotovka Python ====
if not exist ".venv" (
    echo Sozdayu .venv ...
    python -m venv .venv
)

echo Ustanovka zavisimostey...
.venv\Scripts\python.exe -m pip install --upgrade pip -q
.venv\Scripts\pip.exe install -r requirements.txt -q

echo Migracii...
.venv\Scripts\python.exe manage.py migrate --noinput

echo ==== Zapusk Backend i Frontend ====
start "Django Backend" cmd /k "%~dp0run_backend.bat"
if exist "frontend\package.json" (
    start "Angular Frontend" cmd /k "%~dp0run_frontend.bat"
) else (
    echo Papka frontend ne naydena.
)

echo Gotovo. Backend: http://127.0.0.1:8000  Frontend: http://localhost:4200
pause
