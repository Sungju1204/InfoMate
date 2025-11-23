# InfoMate 빠른 시작 가이드

## 🎯 프로젝트가 하는 일

1. 사용자가 뉴스 URL 입력
2. 백엔드로 전송하여 AI 분석
3. 신뢰도 점수 표시
4. 기록 저장

## 📁 파일별 역할 (한 줄 요약)

### 화면 (components/)
- `Home.vue` → 메인 페이지 (URL 입력)
- `AnalysisResult.vue` → 분석 결과 표시
- `History.vue` → 기록 보기

### 서비스 (services/)
- `api.js` → 백엔드와 통신
- `historyService.js` → 기록 저장/조회

### 유틸리티 (utils/)
- `dataStructures.js` → 해시테이블, 그래프
- `algorithms.js` → 정렬, 탐색 알고리즘
- `urlParser.js` → URL 검증

## 🔄 사용자 흐름

```
1. Home.vue에서 URL 입력
   ↓
2. api.js가 백엔드에 요청
   ↓
3. historyService.js가 기록 저장
   ↓
4. AnalysisResult.vue에 결과 표시
```

## 💡 핵심 개념

### 해시 테이블
- URL을 키로 사용
- 빠른 조회 (O(1))
- 캐싱에 사용

### 그래프
- 기사를 노드로 표현
- 관련 기사를 간선으로 연결
- DFS로 관련 기사 찾기

### 비동기 처리
```javascript
async function getData() {
  const result = await fetch(url)  // 대기
  return result
}
```

## 🚀 실행

```bash
npm install    # 처음 한 번만
npm run dev   # 개발 서버 실행
```

## 📚 더 자세히 알고 싶다면

`PROJECT_GUIDE.md` 파일을 읽어보세요!

