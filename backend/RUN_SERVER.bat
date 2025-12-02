@echo off
echo ========================================
echo 백엔드 서버 시작 중...
echo ========================================
echo.

cd /d "%~dp0"
.\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000

pause

