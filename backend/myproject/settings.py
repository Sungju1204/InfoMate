"""
Django settings for myproject project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# .env 파일 로드
load_dotenv()

<<<<<<< HEAD
# SECRET_KEY 가져오기 (없으면 에러 방지용 임시 키 사용 - 배포 시 .env 확인 필수)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key-for-debug')
=======
load_dotenv() # .env 파일 로드

SECRET_KEY = os.environ.get('SECRET_KEY') or 'django-insecure-dev-key-change-in-production-12345'

# Quick-start development settings - unsuitable for production
>>>>>>> e19c1c2865a51bb953d7c7fa5dcc781e39f58d12

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ----------------------------------------------------------------------
# [수정됨] ALLOWED_HOSTS: http:// 빼고 도메인/IP만 입력해야 합니다.
# ----------------------------------------------------------------------
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',           # Docker 내부 통신용
    '.ngrok-free.app',   # ngrok v3
    '.ngrok.io',         # ngrok 구버전
    '134.185.99.4',      # ★ 오라클 클라우드 IP
]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 프로젝트 앱
    'api',
    # 외부 패키지
    'corsheaders',   # CORS
    'rest_framework', # DRF
]

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
    }
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ★ CORS 미들웨어 최상단
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ----------------------------------------------------------------------
# URL 설정: 슬래시 자동 추가 비활성화 (POST 요청 리다이렉트 오류 방지)
# ----------------------------------------------------------------------
APPEND_SLASH = False

# ----------------------------------------------------------------------
# [수정됨] CORS 설정
# ----------------------------------------------------------------------

# ★ 개발/배포 초기 단계에서는 접속 오류를 피하기 위해 True로 설정합니다.
# 보안이 걱정되면 나중에 이 줄을 주석 처리하고 아래 CORS_ALLOWED_ORIGINS를 푸세요.
CORS_ALLOW_ALL_ORIGINS = True

# 특정 도메인만 허용하려면 위 True를 지우고 아래 주석을 해제하세요.
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
#     "http://localhost:8080",
#     "http://134.185.99.4",
# ]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'ngrok-skip-browser-warning',
]

# CSRF 설정 (개발 편의를 위해 완화)
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'