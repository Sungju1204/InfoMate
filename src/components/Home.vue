<template>
  <div class="home">
    <!-- 헤더 -->
    <header class="header">
      <div class="header-content">
        <div class="logo">
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

    <!-- 메인 콘텐츠 -->
    <main class="main-content">
      <!-- 헤드라인 -->
      <div class="headline">
        <h1>가짜뉴스, AI로 10초 만에 판별해요</h1>
      </div>

      <!-- 링크 입력창 -->
      <div class="input-section">
        <div class="input-container">
          <input 
            type="text" 
            v-model="newsUrl"
            placeholder="분석하고 싶은 뉴스 링크를 여기에 붙여넣으세요"
            class="url-input"
          />
          <button @click="analyzeNews" class="analyze-btn">
            신뢰도 분석
          </button>
        </div>
      </div>

      <!-- 서비스 핵심 소개 -->
      <div class="features">
        <div class="feature-card">
          <div class="feature-icon">📄</div>
          <h3>AI 기반 신뢰성 검증</h3>
          <p>최신 AI 기술로 뉴스의 신뢰성을 종합적으로 분석합니다</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🔄</div>
          <h3>실시간 이슈 모니터링</h3>
          <p>핫한 이슈들을 실시간으로 모니터링하고 분석합니다</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🏢</div>
          <h3>강력한 콘텐츠 팀</h3>
          <p>전문가들이 검증한 신뢰할 수 있는 정보를 제공합니다</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      newsUrl: ''
    }
  },
  methods: {
    analyzeNews() {
      if (this.newsUrl.trim()) {
        // 분석 결과 페이지로 이동
        this.$router.push('/analysis')
      } else {
        alert('뉴스 링크를 입력해주세요.')
      }
    }
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
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

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 4rem 2rem;
  text-align: center;
}

.headline h1 {
  font-size: 3rem;
  font-weight: bold;
  color: white;
  margin-bottom: 2rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.input-section {
  margin-bottom: 4rem;
}

.input-container {
  display: flex;
  gap: 1rem;
  max-width: 800px;
  margin: 0 auto;
}

.url-input {
  flex: 1;
  padding: 1rem 1.5rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  outline: none;
}

.url-input:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

.analyze-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
  white-space: nowrap;
}

.analyze-btn:hover {
  background: #2563eb;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 4rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.95);
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 1rem;
}

.feature-card p {
  color: #6b7280;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .headline h1 {
    font-size: 2rem;
  }
  
  .input-container {
    flex-direction: column;
  }
  
  .features {
    grid-template-columns: 1fr;
  }
}
</style>
