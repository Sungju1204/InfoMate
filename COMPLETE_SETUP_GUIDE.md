# InfoMate 완전 초기 설정 가이드

다른 컴퓨터에서 처음부터 시작하는 전체 가이드입니다. GitHub에서 클론하는 것부터 백엔드와 프론트엔드를 모두 설정하고 연결하는 방법을 단계별로 설명합니다.

## 📋 목차

1. [필수 사전 준비](#필수-사전-준비)
2. [프론트엔드 설정 (GitHub에서 클론)](#프론트엔드-설정-github에서-클론)
3. [백엔드 설정 (back-end 브랜치)](#백엔드-설정-back-end-브랜치)
4. [백엔드-프론트엔드 연결](#백엔드-프론트엔드-연결)
5. [실행 및 테스트](#실행-및-테스트)
6. [문제 해결](#문제-해결)

---

## 필수 사전 준비

### 1. 필요한 프로그램 설치 확인

다음 프로그램들이 설치되어 있어야 합니다:

#### Node.js 설치 (프론트엔드용)

1. **Node.js 다운로드**
   - https://nodejs.org/ 접속
   - LTS 버전 다운로드 (권장: v18 이상)
   - Windows Installer (.msi) 다운로드

2. **설치 확인**
   ```bash
   node --version
   npm --version
   ```
   - 두 명령어 모두 버전이 출력되면 정상 설치됨

#### Python 설치 (백엔드용)

1. **Python 다운로드**
   - https://www.python.org/downloads/ 접속
   - Python 3.9 이상 다운로드 (권장: 3.10 또는 3.11)

2. **설치 시 주의사항**
   - ✅ "Add Python to PATH" 체크박스 반드시 선택!
   - ✅ "Install pip" 옵션 선택

3. **설치 확인**
   ```bash
   python --version
   pip --version
   ```
   - 두 명령어 모두 버전이 출력되면 정상 설치됨

#### Git 설치 (GitHub 클론용)

1. **Git 다운로드**
   - https://git-scm.com/download/win 접속
   - Windows용 Git 다운로드 및 설치

2. **설치 확인**
   ```bash
   git --version
   ```

---

## 프론트엔드 설정 (GitHub에서 클론)

### 1단계: GitHub 저장소 클론

#### 1-1. 작업 디렉토리 생성

```bash
# 원하는 위치로 이동 (예: 바탕화면 또는 Documents)
cd Desktop
# 또는
cd Documents
```

#### 1-2. GitHub 저장소 클론

```bash
# GitHub 저장소 URL을 사용하여 클론
# [YOUR_GITHUB_URL]을 실제 저장소 URL로 변경하세요
git clone [YOUR_GITHUB_URL] InfoMate

# 예시:
# git clone https://github.com/username/InfoMate.git InfoMate
```

**참고**: 저장소 URL을 모르면 GitHub 저장소 페이지에서 초록색 "Code" 버튼을 클릭하면 URL을 복사할 수 있습니다.

#### 1-3. 프로젝트 디렉토리로 이동

```bash
cd InfoMate
```

### 2단계: 프론트엔드 의존성 설치

#### 2-1. npm 패키지 설치

```bash
npm install
```

**설치 시간**: 약 1-2분 소요 (인터넷 속도에 따라 다름)

**성공 확인**: `node_modules` 폴더가 생성되고, 터미널에 "added XXX packages" 메시지가 표시됩니다.

#### 2-2. 설치 확인

```bash
# package.json에 정의된 스크립트 확인
npm run dev --help
```

---

## 백엔드 설정 (back-end 브랜치)

### 1단계: 백엔드 브랜치 체크아웃

#### 1-1. 백엔드 브랜치 확인

```bash
# 현재 위치: InfoMate 디렉토리
# 모든 브랜치 확인
git branch -a
```

#### 1-2. back-end 브랜치로 전환

**방법 1: 기존 브랜치가 있는 경우**
```bash
git checkout back-end
```

**방법 2: 원격 브랜치를 로컬로 가져오기**
```bash
git fetch origin
git checkout -b back-end origin/back-end
```

**방법 3: 백엔드가 별도 저장소인 경우**
```bash
# 상위 디렉토리로 이동
cd ..

# 백엔드 저장소 클론 (별도 저장소인 경우)
git clone [BACKEND_GITHUB_URL] InfoMate-backend
cd InfoMate-backend
```

### 2단계: Python 가상환경 설정

#### 2-1. 가상환경 생성

```bash
# 현재 백엔드 디렉토리에서 실행
python -m venv venv
```

**참고**: `python` 명령어가 안 되면 `python3` 또는 `py`를 시도해보세요.

#### 2-2. 가상환경 활성화

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

**활성화 성공 확인**: 터미널 앞에 `(venv)`가 표시됩니다.

```
(venv) C:\Users\YourName\InfoMate>
```

### 3단계: 백엔드 의존성 설치

#### 3-1. requirements.txt 확인

백엔드 디렉토리에 `requirements.txt` 파일이 있는지 확인:

```bash
dir requirements.txt
# 또는
ls requirements.txt
```

#### 3-2. 패키지 설치

```bash
pip install -r requirements.txt
```

**설치 시간**: 
- 일반 패키지: 약 2-5분
- `torch`와 `transformers`: 약 10-30분 (용량이 큼, 인터넷 속도에 따라 다름)

**주의**: 
- 설치 중 오류가 발생하면 오류 메시지를 확인하세요
- `torch` 설치 시 CUDA 버전이 필요할 수 있습니다 (GPU 사용 시)

#### 3-3. 설치 확인

```bash
pip list
```

다음 패키지들이 설치되어 있어야 합니다:
- django
- django-cors-headers
- requests
- playwright
- transformers (선택사항, AI 모델 사용 시)

### 4단계: Django 환경 변수 설정

#### 4-1. .env 파일 생성

백엔드 디렉토리 루트에 `.env` 파일을 생성합니다.

**Windows (PowerShell):**
```powershell
New-Item -Path .env -ItemType File
```

**Windows (CMD):**
```cmd
type nul > .env
```

**Mac/Linux:**
```bash
touch .env
```

#### 4-2. .env 파일 내용 작성

`.env` 파일을 열고 다음 내용을 추가:

```env
SECRET_KEY=your-secret-key-here-change-this-to-random-string
MODEL_DIRECTORY=./my_fake_news_model
```

**SECRET_KEY 생성 방법:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

생성된 키를 복사하여 `.env` 파일의 `SECRET_KEY` 값으로 사용하세요.

### 5단계: Django 데이터베이스 설정

#### 5-1. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

**성공 확인**: "Applying XXX... OK" 메시지가 표시됩니다.

#### 5-2. 관리자 계정 생성 (선택사항)

```bash
python manage.py createsuperuser
```

사용자명, 이메일, 비밀번호를 입력하세요.

---

## 백엔드-프론트엔드 연결

### 1단계: 백엔드 CORS 설정 확인

#### 1-1. settings.py 파일 확인

백엔드 디렉토리에서 `myproject/settings.py` 또는 `settings.py` 파일을 찾습니다.

#### 1-2. CORS 설정 확인

다음 설정이 있는지 확인:

```python
INSTALLED_APPS = [
    # ... 기타 앱들 ...
    'corsheaders',  # 이 줄이 있어야 함
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 최상단에 있어야 함
    'django.middleware.common.CommonMiddleware',
    # ... 기타 미들웨어들 ...
]

# CORS 설정
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

# 개발용 (프로덕션에서는 False로 변경)
CORS_ALLOW_ALL_ORIGINS = True
```

**설정이 없으면 추가하세요.**

#### 1-3. django-cors-headers 설치 확인

```bash
pip install django-cors-headers
```

### 2단계: 프론트엔드 API 주소 설정

#### 2-1. API 설정 파일 확인

프론트엔드 디렉토리에서 `src/services/api.js` 파일을 확인합니다.

#### 2-2. 환경 변수 설정 (선택사항)

프론트엔드 루트 디렉토리에 `.env` 파일을 생성:

**Windows:**
```powershell
cd ..\InfoMate  # 프론트엔드 디렉토리로 이동
New-Item -Path .env -ItemType File
```

**Mac/Linux:**
```bash
cd ../InfoMate
touch .env
```

#### 2-3. .env 파일 내용

`.env` 파일에 다음 내용 추가:

```env
VITE_API_BASE_URL=http://localhost:8000/api/analyze
```

**참고**: 백엔드가 다른 포트를 사용하면 포트 번호를 변경하세요.

---

## 실행 및 테스트

### 실행 순서

**중요**: 반드시 다음 순서로 실행해야 합니다!

```
1. 백엔드 서버 실행
   ↓
2. 백엔드 정상 실행 확인
   ↓
3. 프론트엔드 서버 실행
   ↓
4. 브라우저에서 테스트
```

### 1단계: 백엔드 서버 실행

#### 1-1. 백엔드 디렉토리로 이동

```bash
# 백엔드 디렉토리로 이동
cd [백엔드 디렉토리 경로]

# 예시:
# cd C:\Users\YourName\InfoMate-backend
# 또는 back-end 브랜치를 사용한 경우:
# cd C:\Users\YourName\InfoMate
```

#### 1-2. 가상환경 활성화 (아직 안 했다면)

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

#### 1-3. Django 서버 실행

```bash
python manage.py runserver 0.0.0.0:8000
```

**성공 확인**: 터미널에 다음 메시지가 표시됩니다:
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CTRL-BREAK.
```

#### 1-4. 백엔드 접속 테스트

브라우저에서 `http://localhost:8000` 접속:
- Django 기본 페이지가 보이면 정상
- 오류가 나면 백엔드 설정을 다시 확인

**이 터미널 창은 그대로 두세요!** (백엔드 서버가 계속 실행되어야 함)

### 2단계: 프론트엔드 서버 실행

#### 2-1. 새 터미널 창 열기

백엔드 서버가 실행 중인 터미널은 그대로 두고, **새 터미널 창**을 엽니다.

#### 2-2. 프론트엔드 디렉토리로 이동

```bash
cd [프론트엔드 디렉토리 경로]

# 예시:
# cd C:\Users\YourName\Desktop\InfoMate
```

#### 2-3. 프론트엔드 서버 실행

```bash
npm run dev
```

**성공 확인**: 터미널에 다음 메시지가 표시됩니다:
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

브라우저가 자동으로 열립니다.

### 3단계: 연결 테스트

#### 3-1. 브라우저에서 테스트

1. 브라우저에서 `http://localhost:3000` 접속
2. 뉴스 URL 입력 (예: `https://news.naver.com/...`)
3. "분석하기" 버튼 클릭

#### 3-2. 개발자 도구로 확인

1. 브라우저에서 **F12** 키를 눌러 개발자 도구 열기
2. **Network** 탭 선택
3. 분석 버튼 클릭
4. `analyze` 요청이 보이고 상태가 `200 OK`면 성공!

#### 3-3. 콘솔 로그 확인

개발자 도구의 **Console** 탭에서 다음 로그 확인:

```
✅ 정상 연결:
- "API 호출 시작: [URL]"
- "API_BASE_URL: http://localhost:8000/api/analyze"
- "API 응답 성공: {...}"

❌ 연결 실패:
- "네트워크 오류: ..."
- "Failed to fetch"
```

---

## 문제 해결

### 문제 1: Git 클론 실패

**오류**: `git: command not found` 또는 `'git' is not recognized`

**해결**:
1. Git이 설치되어 있는지 확인: `git --version`
2. 설치되어 있지 않으면 https://git-scm.com/download/win 에서 설치
3. 설치 후 터미널을 재시작

---

### 문제 2: npm install 실패

**오류**: `npm ERR!` 메시지

**해결**:
1. Node.js가 설치되어 있는지 확인: `node --version`
2. npm 캐시 정리:
   ```bash
   npm cache clean --force
   ```
3. 다시 설치:
   ```bash
   npm install
   ```

---

### 문제 3: Python 가상환경 생성 실패

**오류**: `python: command not found` 또는 `'python' is not recognized`

**해결**:
1. Python이 설치되어 있는지 확인: `python --version`
2. 설치되어 있지 않으면 https://www.python.org/downloads/ 에서 설치
3. 설치 시 "Add Python to PATH" 옵션 체크 확인
4. 설치 후 터미널을 재시작

**대안**:
- `python3` 또는 `py` 명령어 시도:
  ```bash
  python3 -m venv venv
  # 또는
  py -m venv venv
  ```

---

### 문제 4: pip install 실패

**오류**: `pip: command not found` 또는 패키지 설치 실패

**해결**:
1. pip 업그레이드:
   ```bash
   python -m pip install --upgrade pip
   ```
2. 가상환경이 활성화되어 있는지 확인 (터미널 앞에 `(venv)` 표시)
3. 특정 패키지 설치 실패 시:
   ```bash
   pip install [패키지명] --no-cache-dir
   ```

---

### 문제 5: Django migrate 실패

**오류**: `django.core.exceptions.ImproperlyConfigured`

**해결**:
1. `.env` 파일이 올바른 위치에 있는지 확인
2. `SECRET_KEY`가 설정되어 있는지 확인
3. `settings.py`에서 환경 변수 로드 코드 확인:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   SECRET_KEY = os.getenv('SECRET_KEY')
   ```

---

### 문제 6: 백엔드 서버 실행 실패

**오류**: `Port 8000 is already in use`

**해결**:
1. 다른 포트 사용:
   ```bash
   python manage.py runserver 8001
   ```
2. 프론트엔드 `.env` 파일에서 포트 변경:
   ```env
   VITE_API_BASE_URL=http://localhost:8001/api/analyze
   ```
3. 프론트엔드 서버 재시작

---

### 문제 7: CORS 오류

**오류**: `Access to fetch ... has been blocked by CORS policy`

**해결**:
1. 백엔드 `settings.py`에서 CORS 설정 확인
2. `django-cors-headers` 설치 확인:
   ```bash
   pip install django-cors-headers
   ```
3. `INSTALLED_APPS`에 `'corsheaders'` 추가 확인
4. `MIDDLEWARE`에 `'corsheaders.middleware.CorsMiddleware'` 추가 확인
5. 백엔드 서버 재시작

---

### 문제 8: API 호출 실패

**오류**: `Failed to fetch` 또는 `네트워크 오류`

**해결**:
1. 백엔드 서버가 실행 중인지 확인
2. 브라우저에서 `http://localhost:8000` 직접 접속 테스트
3. 프론트엔드 `.env` 파일의 API 주소 확인
4. 프론트엔드 서버 재시작 (환경 변수 변경 후)

---

## 체크리스트

설정 완료 후 다음 항목을 확인하세요:

### 필수 프로그램
- [ ] Node.js 설치됨 (`node --version` 확인)
- [ ] Python 설치됨 (`python --version` 확인)
- [ ] Git 설치됨 (`git --version` 확인)

### 프론트엔드
- [ ] GitHub에서 클론 완료
- [ ] `npm install` 완료
- [ ] `node_modules` 폴더 존재
- [ ] `.env` 파일 생성 (선택사항)

### 백엔드
- [ ] back-end 브랜치 체크아웃 완료
- [ ] 가상환경 생성 및 활성화 완료
- [ ] `pip install -r requirements.txt` 완료
- [ ] `.env` 파일 생성 및 설정 완료
- [ ] `python manage.py migrate` 완료
- [ ] CORS 설정 확인 완료

### 실행
- [ ] 백엔드 서버 실행 중 (`http://localhost:8000` 접속 가능)
- [ ] 프론트엔드 서버 실행 중 (`http://localhost:3000` 접속 가능)
- [ ] API 호출 성공 (브라우저 개발자 도구에서 확인)

---

## 다음 단계

설정이 완료되면 다음 문서를 참고하세요:

- **프로젝트 구조 이해**: `QUICK_START.md`
- **상세 개발 가이드**: `PROJECT_GUIDE.md`
- **백엔드 상세 설정**: `BACKEND_SETUP.md`
- **연결 문제 해결**: `FRONTEND_BACKEND_CONNECTION.md`

---

## 추가 도움말

문제가 해결되지 않으면 다음 정보를 포함하여 문의하세요:

1. **오류 메시지 전체 내용**
2. **실행 환경**:
   - OS (Windows/Mac/Linux)
   - Node.js 버전 (`node --version`)
   - Python 버전 (`python --version`)
3. **어느 단계에서 문제가 발생했는지**
4. **스크린샷** (가능한 경우)

---

**축하합니다! 🎉** 이제 InfoMate 프로젝트를 개발할 준비가 되었습니다!

