# 백엔드 연동 가이드

## 백엔드 코드 위치

백엔드 코드는 `back-end` 브랜치에 있습니다. 현재 사용자 홈 디렉토리(`C:\Users\cse09`)에 백엔드 파일들이 체크아웃되어 있습니다.

## 백엔드 실행 방법

### 1. 백엔드 디렉토리로 이동

```bash
cd C:\Users\cse09
```

### 2. Python 가상환경 생성 및 활성화 (권장)

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

**주의**: `torch`와 `transformers`는 용량이 크므로 설치에 시간이 걸릴 수 있습니다.

### 4. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가:

```env
SECRET_KEY=your-secret-key-here
MODEL_DIRECTORY=./my_fake_news_model
```

### 5. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

### 6. 서버 실행

```bash
# 개발 서버 실행 (모든 네트워크 인터페이스에서 접근 가능)
python manage.py runserver 0.0.0.0:8000
```

또는

```bash
# localhost만 접근 가능
python manage.py runserver 8000
```

## 프론트엔드 연동

프론트엔드 API URL이 `http://localhost:8000/api/analyze`로 설정되어 있습니다.

### 프론트엔드 실행

```bash
# InfoMate 프로젝트 디렉토리로 이동
cd "OneDrive - 한밭대학교\바탕 화면\임성주\2학년\2학기\오픈소스\InfoMate"

# 개발 서버 실행
npm run dev
```

프론트엔드는 `http://localhost:3000`에서 실행됩니다.

## CORS 설정

백엔드의 `myproject/settings.py`에 이미 CORS 설정이 되어 있습니다:

- `CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]`
- `CORS_ALLOW_ALL_ORIGINS = True` (개발용)

## 백엔드 API 엔드포인트

- **POST** `/api/analyze/`
  - 요청: `{ "url": "뉴스 URL" }`
  - 응답: 
    ```json
    {
      "success": true,
      "data": {
        "requested_url": "...",
        "publisher_name": "...",
        "published_date": "...",
        "scraped_title": "...",
        "ai_prediction": {
          "prediction": "Fake" | "True",
          "fake_percentage": 0-100,
          "true_percentage": 0-100
        },
        "media_trust": {...}
      }
    }
    ```

## 문제 해결

### 1. 포트가 이미 사용 중인 경우

```bash
# 다른 포트 사용
python manage.py runserver 8001
```

그리고 프론트엔드 `api.js`에서 포트 번호 수정

### 2. CORS 오류

백엔드 `settings.py`에서 `CORS_ALLOW_ALL_ORIGINS = True` 확인

### 3. AI 모델 로딩 실패

`.env` 파일에서 `MODEL_DIRECTORY` 경로 확인

### 4. Playwright 오류

```bash
# Playwright 브라우저 설치
playwright install chromium
```

## 참고사항

- 백엔드 서버가 실행 중이어야 프론트엔드에서 API 호출이 가능합니다
- 백엔드와 프론트엔드를 동시에 실행해야 합니다
- 개발 중에는 두 터미널 창을 열어서 각각 실행하는 것이 편합니다


