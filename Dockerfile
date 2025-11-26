# Dockerfile (Playwright 오류 최종 수정본)

# Dockerfile 맨 위

# 1. 베이스 이미지
FROM python:3.10-slim

# 2. 환경변수
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. 작업 디렉토리
WORKDIR /app

# 4. (!!!) 라이브러리 설치 (순서 변경)
# requirements.txt를 먼저 복사하고 pip를 먼저 실행합니다.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. (!!! 여기가 핵심 수정 !!!)
# Playwright가 필요로 하는 모든 '시스템 라이브러리'를 자동으로 설치
RUN playwright install-deps

# 6. (!!!) Playwright로 '크롬 브라우저' 다운로드
RUN playwright install chromium

# 7. 프로젝트 코드 전체 복사
COPY . .

# 8. 포트 개방
EXPOSE 8000


# 9. 서버 실행
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]