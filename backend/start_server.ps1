# 백엔드 서버 실행 스크립트
Write-Host "백엔드 서버 시작 중..." -ForegroundColor Green

# 가상환경의 Python으로 서버 실행
.\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000

Write-Host "서버가 종료되었습니다." -ForegroundColor Yellow

