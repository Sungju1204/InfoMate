# InfoMate - 가짜뉴스 판독기

Vue.js로 구현된 가짜뉴스 판독기 프론트엔드 초안입니다.

## 주요 기능

### 메인 화면
- **헤더**: InfoMate 로고와 네비게이션 메뉴
- **헤드라인**: "가짜뉴스, AI로 10초 만에 판별해요"
- **링크 입력창**: 뉴스 URL 입력 및 분석 버튼
- **서비스 핵심 소개**: 3가지 주요 기능 소개

### 분석 결과 페이지
- **종합 신뢰도**: 0-100점 신뢰도 점수 표시
- **상세 분석 내역**: 출처, 편향성, 작성일, 신뢰성, 광고성 등 분석
- **사이드바**: 관련 기사 및 추천 기사 목록
- **정보 평가 기능**: 평가 및 피드백 버튼

## 기술 스택

- **Vue 3**: Composition API 사용
- **Vue Router**: 페이지 라우팅
- **Vite**: 빌드 도구
- **CSS3**: 반응형 디자인

## 설치 및 실행

```bash
# 프론트엔드 디렉토리로 이동
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 빌드
npm run build

# 프리뷰
npm run preview
```

## 프로젝트 구조

```
InfoMate/
├── backend/                      # Django 백엔드
│   ├── api/                      # API 앱
│   ├── manage.py
│   └── requirements.txt
├── frontend/                      # Vue.js 프론트엔드
│   ├── src/
│   │   ├── components/
│   │   │   ├── Home.vue              # 메인 화면
│   │   │   ├── AnalysisResult.vue   # 분석 결과 페이지
│   │   │   └── History.vue           # 평가 기록 페이지
│   │   ├── services/
│   │   │   ├── api.js                # API 통신
│   │   │   ├── evaluationService.js # 평가 서비스
│   │   │   └── historyService.js    # 히스토리 서비스
│   │   ├── utils/
│   │   │   ├── algorithms.js        # 알고리즘 유틸리티
│   │   │   ├── dataStructures.js    # 자료구조 유틸리티
│   │   │   └── urlParser.js         # URL 파서
│   │   ├── App.vue                  # 루트 컴포넌트
│   │   ├── main.js                  # 애플리케이션 진입점
│   │   └── style.css                # 전역 스타일
│   ├── index.html                  # HTML 템플릿
│   ├── package.json                # 프로젝트 설정
│   └── vite.config.js             # Vite 설정
└── README.md
```

## 디자인 특징

- **모던한 UI**: 그라데이션 배경과 글래스모피즘 효과
- **반응형 디자인**: 모바일과 데스크톱 모두 지원
- **직관적인 UX**: 사용자 친화적인 인터페이스
- **시각적 피드백**: 호버 효과와 애니메이션

## 개발 상태

- ✅ 백엔드 API 연동 완료
- ✅ 실제 뉴스 분석 기능 구현 완료
- ✅ 분석 히스토리 저장 기능 구현
- 🔄 사용자 인증 시스템 (진행 중)
- 📋 소셜 공유 기능 (계획 중)
