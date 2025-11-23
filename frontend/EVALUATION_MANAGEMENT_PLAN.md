# 평가/피드백/신고 데이터 관리 계획

## 📊 현재 상태

**현재 구현**: 로컬 스토리지에만 저장
- ✅ 빠른 구현
- ❌ 브라우저별로 데이터 분리
- ❌ 데이터 분석 불가
- ❌ 관리자 확인 불가

---

## 🎯 추천 관리 방안

### 1. Supabase 연동 (추천 ⭐⭐⭐⭐⭐)

**장점**:
- ✅ **교수님 평가에 유리**: 실제 백엔드 연동을 했다는 점이 큰 플러스
- ✅ **데이터베이스 설계 능력**: 테이블 설계, 관계 설정 등 보여줄 수 있음
- ✅ **실제 서비스 운영**: 프로덕션 환경과 유사
- ✅ **데이터 분석 가능**: SQL 쿼리로 통계 분석
- ✅ **무료 티어 제공**: 학생 프로젝트에 적합
- ✅ **실시간 동기화**: 여러 사용자 데이터 통합

**구현 내용**:
```sql
-- 평가 테이블
CREATE TABLE evaluations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  url TEXT NOT NULL,
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  feedback TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 신고 테이블
CREATE TABLE reports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  url TEXT NOT NULL,
  reason TEXT NOT NULL,
  description TEXT,
  count INTEGER DEFAULT 1,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**교수님 평가 포인트**:
- 백엔드 연동 능력
- 데이터베이스 설계 능력
- 실제 서비스 운영 경험
- 데이터 분석 및 활용 능력

---

### 2. 데이터 분석 및 시각화

**구현 가능한 기능**:
- 평균 평가 점수 계산
- 신고 빈도 분석
- 평가 트렌드 차트
- 가장 많이 신고된 뉴스 URL
- 사용자 만족도 통계

**예시 쿼리**:
```sql
-- 평균 평가 점수
SELECT AVG(rating) as avg_rating FROM evaluations;

-- 신고 사유별 통계
SELECT reason, COUNT(*) as count 
FROM reports 
GROUP BY reason 
ORDER BY count DESC;

-- URL별 평가 점수
SELECT url, AVG(rating) as avg_rating, COUNT(*) as count
FROM evaluations
GROUP BY url
ORDER BY avg_rating DESC;
```

---

### 3. 관리자 페이지

**기능**:
- 평가 목록 조회
- 신고 목록 조회
- 통계 대시보드
- 데이터 필터링 및 검색
- CSV 내보내기

---

### 4. 데이터 활용 방안

#### A. 서비스 개선
- 낮은 평가 점수 받은 분석 결과 개선
- 자주 신고되는 뉴스 패턴 분석
- 사용자 피드백 기반 기능 추가

#### B. 신뢰도 점수 보정
- 사용자 평가를 반영한 신뢰도 점수 조정
- 크라우드소싱 방식의 신뢰도 계산

#### C. 리포트 생성
- 주간/월간 평가 리포트
- 신고 현황 리포트
- 사용자 만족도 리포트

---

## 🚀 구현 우선순위

### Phase 1: Supabase 연동 (필수)
1. Supabase 프로젝트 생성
2. 테이블 설계 및 생성
3. API 키 설정
4. 프론트엔드 연동

### Phase 2: 데이터 분석 (권장)
1. 통계 쿼리 작성
2. 대시보드 UI 구현
3. 차트 라이브러리 연동 (Chart.js 등)

### Phase 3: 관리자 페이지 (선택)
1. 관리자 인증
2. 데이터 조회 페이지
3. 필터링 및 검색 기능

---

## 💡 교수님 평가 관점

### 높은 점수를 받을 수 있는 요소:

1. **기술적 완성도**
   - ✅ 백엔드 연동 (Supabase)
   - ✅ 데이터베이스 설계
   - ✅ API 통신 구현

2. **실제 서비스 운영**
   - ✅ 프로덕션 환경 구축
   - ✅ 데이터 영구 저장
   - ✅ 다중 사용자 지원

3. **데이터 활용**
   - ✅ 통계 분석
   - ✅ 시각화
   - ✅ 리포트 생성

4. **전체적인 시스템 설계**
   - ✅ 프론트엔드 + 백엔드 통합
   - ✅ 데이터 흐름 설계
   - ✅ 확장 가능한 구조

---

## 📝 구현 예시 코드

### Supabase 클라이언트 설정
```javascript
// src/services/supabaseClient.js
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseKey)
```

### 평가 저장
```javascript
// 평가 저장
const { data, error } = await supabase
  .from('evaluations')
  .insert([
    { url: url, rating: rating, feedback: feedback }
  ])
```

### 통계 조회
```javascript
// 평균 평가 점수
const { data } = await supabase
  .from('evaluations')
  .select('rating')
  
const avgRating = data.reduce((sum, e) => sum + e.rating, 0) / data.length
```

---

## 🎓 결론

**Supabase 연동을 강력히 추천합니다!**

**이유**:
1. 교수님 평가에 매우 유리 (백엔드 연동 경험)
2. 실제 서비스 운영 경험
3. 데이터베이스 설계 능력 증명
4. 데이터 분석 및 활용 능력 보여줄 수 있음
5. 무료로 사용 가능

**추가로 하면 더 좋은 것**:
- 통계 대시보드 구현
- 관리자 페이지 구현
- 데이터 시각화 (차트)

이렇게 하면 **프론트엔드 + 백엔드 + 데이터베이스 + 데이터 분석**까지 모두 보여줄 수 있어서 교수님 평가에 매우 유리할 것입니다!

