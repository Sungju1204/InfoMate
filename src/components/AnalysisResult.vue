<template>
  <div class="analysis-result">
    <!-- 헤더 -->
    <header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <div class="logo-icon">✓</div>
          <span class="logo-text">InfoMate</span>
        </div>
        <nav class="nav">
          <a href="#" class="nav-link">서비스 소개</a>
          <a href="#" class="nav-link">평가 기록</a>
          <a href="#" class="nav-link">문의/Q&A</a>
        </nav>
      </div>
    </header>

    <div class="content">
      <div class="main-content">
        <!-- 종합 신뢰도 -->
        <section class="reliability-section">
          <h2>종합 신뢰도</h2>
          <div class="reliability-score">
            <div class="score-circle">
              <span class="score-number">82</span>
              <span class="score-total">/100</span>
            </div>
            <div class="score-description">
              <div class="score-icon">✓</div>
              <p>이 뉴스는 신뢰될 수 있는 정보입니다. 검증된 플랫폼입니다.</p>
            </div>
          </div>
        </section>

        <!-- 상세 분석 내역 -->
        <section class="analysis-details">
          <h2>상세 분석 내역</h2>
          <div class="analysis-cards">
            <div class="analysis-card">
              <div class="card-icon">🏢</div>
              <div class="card-content">
                <h3>출처 신뢰도</h3>
                <p>공신력 있는 언론사를 통해 발표된 정보입니다</p>
              </div>
            </div>
            
            <div class="analysis-card">
              <div class="card-icon">⚖️</div>
              <div class="card-content">
                <h3>정보의 편향성</h3>
                <p>중립적인 관점에서 작성된 기사입니다</p>
              </div>
            </div>
            
            <div class="analysis-card">
              <div class="card-icon">📅</div>
              <div class="card-content">
                <h3>작성일/발행일</h3>
                <p>2024년 10월 7일 (최신)</p>
              </div>
            </div>
            
            <div class="analysis-card">
              <div class="card-icon">🔍</div>
              <div class="card-content">
                <h3>정보/신뢰성</h3>
                <p>크로스 체크를 통한 검증 완료</p>
              </div>
            </div>
            
            <div class="analysis-card warning">
              <div class="card-icon">⚠️</div>
              <div class="card-content">
                <h3>광고/상업성</h3>
                <p>일부 상업적 내용이 포함되어 있습니다</p>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- 사이드바 -->
      <aside class="sidebar">
        <!-- 관련 기사 -->
        <div class="sidebar-section">
          <h3>관련 기사</h3>
          <div class="article-list">
            <div class="article-item">
              <div class="article-thumbnail">📰</div>
              <div class="article-content">
                <h4>관련 뉴스 제목 1</h4>
                <p>관련 기사 설명...</p>
              </div>
            </div>
            <div class="article-item">
              <div class="article-thumbnail">📰</div>
              <div class="article-content">
                <h4>관련 뉴스 제목 2</h4>
                <p>관련 기사 설명...</p>
              </div>
            </div>
            <div class="article-item">
              <div class="article-thumbnail">📰</div>
              <div class="article-content">
                <h4>관련 뉴스 제목 3</h4>
                <p>관련 기사 설명...</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 함께 보면 좋은 글 -->
        <div class="sidebar-section">
          <h3>함께 보면 좋은 글</h3>
          <div class="article-list">
            <div class="article-item">
              <div class="article-thumbnail">📖</div>
              <div class="article-content">
                <h4>추천 기사 제목 1</h4>
                <p>추천 기사 설명...</p>
              </div>
            </div>
            <div class="article-item">
              <div class="article-thumbnail">📖</div>
              <div class="article-content">
                <h4>추천 기사 제목 2</h4>
                <p>추천 기사 설명...</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 정보 평가 기능 -->
        <div class="evaluation-section">
          <button class="eval-btn primary">평가하고 피드백</button>
          <button class="eval-btn secondary">제보하기</button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AnalysisResult'
}
</script>

<style scoped>
.analysis-result {
  min-height: 100vh;
  background: #f8fafc;
}

.header {
  background: white;
  padding: 1rem 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.logo-icon {
  background: #3b82f6;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.logo-text {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
}

.nav {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: #6b7280;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-link:hover {
  color: #3b82f6;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.reliability-section {
  background: white;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.reliability-section h2 {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.reliability-score {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.score-circle {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.score-number {
  font-size: 2.5rem;
  line-height: 1;
}

.score-total {
  font-size: 1rem;
  opacity: 0.8;
}

.score-description {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.score-icon {
  background: #10b981;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.score-description p {
  color: #374151;
  font-size: 1.1rem;
  line-height: 1.5;
}

.analysis-details h2 {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 1.5rem;
}

.analysis-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.analysis-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s;
}

.analysis-card:hover {
  transform: translateY(-2px);
}

.analysis-card.warning {
  border-left: 4px solid #f59e0b;
}

.card-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 12px;
}

.card-content h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.card-content p {
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.4;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.sidebar-section {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.sidebar-section h3 {
  font-size: 1.25rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 1rem;
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.article-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  transition: background 0.2s;
}

.article-item:hover {
  background: #f9fafb;
}

.article-thumbnail {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 8px;
}

.article-content h4 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
  line-height: 1.3;
}

.article-content p {
  font-size: 0.8rem;
  color: #6b7280;
  line-height: 1.3;
}

.evaluation-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.eval-btn {
  padding: 1rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.eval-btn.primary {
  background: #3b82f6;
  color: white;
}

.eval-btn.primary:hover {
  background: #2563eb;
}

.eval-btn.secondary {
  background: #f3f4f6;
  color: #374151;
}

.eval-btn.secondary:hover {
  background: #e5e7eb;
}

@media (max-width: 1024px) {
  .content {
    grid-template-columns: 1fr;
  }
  
  .reliability-score {
    flex-direction: column;
    text-align: center;
  }
  
  .analysis-cards {
    grid-template-columns: 1fr;
  }
}
</style>
