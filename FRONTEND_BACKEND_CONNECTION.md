# 백엔드-프론트엔드 연결 가이드

이 문서는 InfoMate 프로젝트에서 백엔드(Django)와 프론트엔드(Vue.js)를 연결하는 방법을 설명합니다.

## 📋 목차

1. [전체 구조 개요](#전체-구조-개요)
2. [연결 방법 (단계별)](#연결-방법-단계별)
3. [API 연결 설정](#api-연결-설정)
4. [실행 순서](#실행-순서)
5. [연결 확인 방법](#연결-확인-방법)
6. [문제 해결](#문제-해결)

---

## 전체 구조 개요

```
┌─────────────────┐         HTTP POST 요청         ┌─────────────────┐
│   프론트엔드     │  ──────────────────────────>  │    백엔드        │
│  (Vue.js)       │                                │   (Django)       │
│  localhost:3000 │  <──────────────────────────  │  localhost:8000  │
└─────────────────┘         JSON 응답             └─────────────────┘
```

- **프론트엔드**: Vue.js + Vite, 포트 3000
- **백엔드**: Django REST API, 포트 8000
- **API 엔드포인트**: `POST http://localhost:8000/api/analyze/`

---

## 연결 방법 (단계별)

### 1단계: 백엔드 서버 실행

백엔드가 먼저 실행되어 있어야 프론트엔드에서 API 호출이 가능합니다.

#### 1-1. 백엔드 디렉토리로 이동

```bash
cd C:\Users\cse09
```

> **참고**: 백엔드 코드는 `back-end` 브랜치에 있으며, 사용자 홈 디렉토리에 체크아웃되어 있습니다.

#### 1-2. 가상환경 활성화 (선택사항, 권장)

```bash
# 가상환경 활성화 (Windows)
venv\Scripts\activate
```

#### 1-3. Django 서버 실행

```bash
# 모든 네트워크 인터페이스에서 접근 가능 (권장)
python manage.py runserver 0.0.0.0:8000

# 또는 localhost만 접근 가능
python manage.py runserver 8000
```

**✅ 백엔드가 정상 실행되면:**
- 터미널에 `Starting development server at http://0.0.0.0:8000/` 메시지가 표시됩니다
- 브라우저에서 `http://localhost:8000` 접속 시 Django 페이지가 보입니다

---

### 2단계: 프론트엔드 서버 실행

백엔드가 실행 중인 상태에서 프론트엔드를 실행합니다.

#### 2-1. 프론트엔드 디렉토리로 이동

```bash
cd "C:\Users\cse09\OneDrive - 한밭대학교\바탕 화면\임성주\2학년\2학기\오픈소스\InfoMate"
```

#### 2-2. 의존성 설치 (최초 1회만)

```bash
npm install
```

#### 2-3. 개발 서버 실행

```bash
npm run dev
```

**✅ 프론트엔드가 정상 실행되면:**
- 터미널에 `Local: http://localhost:3000/` 메시지가 표시됩니다
- 브라우저가 자동으로 열립니다

---

## API 연결 설정

### 기본 설정

프론트엔드의 API 주소는 `src/services/api.js` 파일에서 설정됩니다:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/analyze'
```

**기본값**: `http://localhost:8000/api/analyze`

### 환경 변수로 변경하기

백엔드 주소를 변경하려면 `.env` 파일을 생성하세요:

#### 1. 프로젝트 루트에 `.env` 파일 생성

```bash
# InfoMate 프로젝트 루트 디렉토리에 생성
```

#### 2. `.env` 파일 내용

```env
# 백엔드 API 주소 설정
VITE_API_BASE_URL=http://localhost:8000/api/analyze
```

**다른 포트를 사용하는 경우:**
```env
VITE_API_BASE_URL=http://localhost:8001/api/analyze
```

**ngrok 등 외부 주소를 사용하는 경우:**
```env
VITE_API_BASE_URL=https://your-ngrok-url.ngrok-free.app/api/analyze
```

#### 3. 프론트엔드 서버 재시작

환경 변수 변경 후에는 프론트엔드 서버를 재시작해야 합니다:

```bash
# Ctrl + C로 서버 중지 후
npm run dev
```

---

## 실행 순서

**중요**: 반드시 다음 순서로 실행해야 합니다!

```
1. 백엔드 서버 실행 (포트 8000)
   ↓
2. 백엔드가 정상 실행되었는지 확인
   ↓
3. 프론트엔드 서버 실행 (포트 3000)
   ↓
4. 브라우저에서 프론트엔드 접속
   ↓
5. 뉴스 URL 입력하여 테스트
```

### 💡 팁: 두 터미널 창 사용

개발 시에는 두 개의 터미널 창을 열어서 사용하는 것이 편합니다:

- **터미널 1**: 백엔드 서버 (`python manage.py runserver 0.0.0.0:8000`)
- **터미널 2**: 프론트엔드 서버 (`npm run dev`)

---

## 연결 확인 방법

### 방법 1: 브라우저 개발자 도구 확인

1. 프론트엔드 페이지에서 뉴스 URL을 입력하고 분석 버튼 클릭
2. 브라우저 개발자 도구 열기 (F12)
3. **Network** 탭 확인
   - `analyze` 요청이 보여야 합니다
   - 상태 코드가 `200 OK`면 성공
   - `CORS error` 또는 `Failed to fetch` 오류가 있으면 백엔드 CORS 설정 확인

### 방법 2: 콘솔 로그 확인

브라우저 개발자 도구의 **Console** 탭에서 다음 로그를 확인:

```
✅ 정상 연결 시:
- "API 호출 시작: [URL]"
- "API_BASE_URL: http://localhost:8000/api/analyze"
- "API 응답 성공: {...}"

❌ 연결 실패 시:
- "네트워크 오류: ..."
- "Fetch 오류 상세: ..."
```

### 방법 3: 백엔드 터미널 확인

백엔드 서버 터미널에서 다음 로그가 보이면 정상 연결:

```
[날짜 시간] "POST /api/analyze/ HTTP/1.1" 200 [응답 크기]
```

---

## 문제 해결

### 문제 1: "Failed to fetch" 또는 "네트워크 오류" 발생

**원인**: 백엔드 서버가 실행되지 않았거나 접근할 수 없음

**해결 방법**:
1. 백엔드 서버가 실행 중인지 확인
   ```bash
   # 백엔드 터미널에서 확인
   # "Starting development server at http://0.0.0.0:8000/" 메시지가 있어야 함
   ```
2. 브라우저에서 직접 접속 테스트
   ```
   http://localhost:8000
   ```
   - 접속이 안 되면 백엔드 서버를 다시 실행하세요

---

### 문제 2: CORS 오류 발생

**오류 메시지 예시**:
```
Access to fetch at 'http://localhost:8000/api/analyze/' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**원인**: 백엔드 CORS 설정 문제

**해결 방법**:
1. 백엔드 `settings.py` 파일 확인
2. 다음 설정이 있는지 확인:
   ```python
   CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
   # 또는 개발용으로
   CORS_ALLOW_ALL_ORIGINS = True
   ```
3. `django-cors-headers` 패키지가 설치되어 있는지 확인:
   ```bash
   pip list | grep django-cors-headers
   ```
4. `INSTALLED_APPS`에 `'corsheaders'`가 추가되어 있는지 확인
5. `MIDDLEWARE`에 `'corsheaders.middleware.CorsMiddleware'`가 추가되어 있는지 확인

---

### 문제 3: 포트가 이미 사용 중

**오류 메시지 예시**:
```
Error: That port is already in use
```

**해결 방법**:

**백엔드 포트 변경:**
```bash
python manage.py runserver 8001
```

**프론트엔드에서 포트 변경 반영:**
`.env` 파일 수정:
```env
VITE_API_BASE_URL=http://localhost:8001/api/analyze
```

프론트엔드 서버 재시작:
```bash
npm run dev
```

---

### 문제 4: API 응답 형식 오류

**오류 메시지 예시**:
```
알 수 없는 응답 형식입니다.
```

**원인**: 백엔드 응답 형식이 예상과 다름

**해결 방법**:
1. 브라우저 개발자 도구의 Network 탭에서 실제 응답 확인
2. 백엔드 응답 형식이 다음 중 하나인지 확인:
   ```json
   // 형식 1
   {
     "success": true,
     "data": { ... }
   }
   
   // 형식 2
   {
     "requested_url": "...",
     "publisher_name": "...",
     "ai_prediction": { ... }
   }
   ```
3. 백엔드 코드에서 응답 형식 확인

---

### 문제 5: 환경 변수가 적용되지 않음

**원인**: `.env` 파일 변경 후 서버를 재시작하지 않음

**해결 방법**:
1. 프론트엔드 서버 중지 (Ctrl + C)
2. `.env` 파일 확인
3. 프론트엔드 서버 재시작:
   ```bash
   npm run dev
   ```

---

## 요약 체크리스트

연결 전에 다음 사항을 확인하세요:

- [ ] 백엔드 서버가 실행 중인가요? (`http://localhost:8000` 접속 가능한지 확인)
- [ ] 프론트엔드 서버가 실행 중인가요? (`http://localhost:3000` 접속 가능한지 확인)
- [ ] 백엔드 CORS 설정이 되어 있나요? (`settings.py` 확인)
- [ ] API 주소가 올바른가요? (`src/services/api.js` 또는 `.env` 파일 확인)
- [ ] 두 서버를 모두 재시작했나요? (환경 변수 변경 시)

---

## 추가 참고 자료

- 백엔드 설정 상세: `BACKEND_SETUP.md`
- API 엔드포인트 상세: `BACKEND_SETUP.md`의 "백엔드 API 엔드포인트" 섹션
- 프론트엔드 API 코드: `src/services/api.js`

---

## 문의사항

문제가 해결되지 않으면 다음 정보를 포함하여 문의하세요:

1. 오류 메시지 전체 내용
2. 브라우저 개발자 도구의 Network 탭 스크린샷
3. 백엔드 터미널의 오류 로그
4. 실행 환경 (OS, Node.js 버전, Python 버전)

